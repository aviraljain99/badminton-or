"""CP-SAT badminton scheduler.

Script conversion of cp_model.py (marimo notebook). Run from this directory so
that `session_config` and the `solution/` checkpoint dir resolve correctly:

    python cp_model_script.py
"""

import os
import time
from itertools import combinations

from ortools.sat.python import cp_model

from session_config import (
    COURTS,
    PLAYER_ALLOCATIONS,
    PLAYER_DATA,
    PLAYER_PREFERENCES,
    ROUNDS,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
player_data = PLAYER_DATA
player_preferences = PLAYER_PREFERENCES
player_allocations = PLAYER_ALLOCATIONS
print(len(player_data))

# CP-SAT requires integer coefficients — scale float scores by SCALE
SCALE = 1000


def _compute_score(p, p_prime):
    if p not in player_preferences:
        return 0
    pair_up = {player: rank for player, rank in player_preferences[p]["pair_up_preference"]}
    l_p = len(pair_up)
    if l_p == 0:
        return 0
    if p_prime in pair_up:
        return (12 / (l_p + 1)) * (l_p + 2 - pair_up[p_prime])
    else:
        return 12 / (l_p + 1)


_players = [p["user_id"] for p in player_data]
preference_score = {
    (p, p_prime): int(round(_compute_score(p, p_prime) * SCALE))
    for p in _players
    for p_prime in _players
    if p != p_prime
}

# ---------------------------------------------------------------------------
# Variables
# ---------------------------------------------------------------------------
players = [p["user_id"] for p in player_data]
player_pairs = list(combinations(players, 2))
rounds = range(ROUNDS)
courts = range(COURTS)

model = cp_model.CpModel()

# x[p1, p2, r, c, t]: p1 and p2 are paired as team t (0 or 1) on court c in round r
x = {
    (p1, p2, r, c, t): model.new_bool_var(f"x_{p1}_{p2}_{r}_{c}_{t}")
    for (p1, p2) in player_pairs
    for r in rounds
    for c in courts
    for t in range(2)
}

# diff[r, c]: absolute skill difference between the two teams on court c in round r
_level = {p["user_id"]: p["level"] for p in player_data}
_pair_skill = {(p1, p2): _level[p1] + _level[p2] for (p1, p2) in player_pairs}
_max_possible_diff = max(_pair_skill.values()) - min(_pair_skill.values())
diff = {
    (r, c): model.new_int_var(0, _max_possible_diff, f"diff_{r}_{c}")
    for r in rounds
    for c in courts
}

# M: maximum number of games played by any player
M = model.new_int_var(0, ROUNDS, "M")

# m: minimum number of games played by any player
m = model.new_int_var(0, ROUNDS, "m")

# z[p, r]: whether player p played in round r
z = {(p, r): model.new_bool_var(f"z_{p}_{r}") for p in players for r in rounds}

_pairs_set = set(player_pairs)
_players_set = set(players)
_avoided = set()
for _p, _prefs in player_preferences.items():
    if _p not in _players_set:
        continue
    for _pa in _prefs["avoid"]:
        if _pa not in _players_set:
            continue
        _avoided.add((_p, _pa) if (_p, _pa) in _pairs_set else (_pa, _p))

# w[p1, p2]: 1 if p1 and p2 ever partner during the session (skips avoided pairs)
w = {
    (p1, p2): model.new_bool_var(f"w_{p1}_{p2}")
    for (p1, p2) in player_pairs
    if (p1, p2) not in _avoided
}

# Players who flagged that they don't mind long streaks are exempted from the
# 3-consecutive-games penalty (no consec3 var is created for them).
consec_exempt = {
    p
    for p in players
    if player_preferences.get(p, {}).get("ok_with_consecutive_games", False)
}

# consec3[p, r]: 1 if player p plays in rounds r, r+1, and r+2
consec3 = {
    (p, r): model.new_bool_var(f"consec3_{p}_{r}")
    for p in players
    if p not in consec_exempt
    for r in range(ROUNDS - 2)
}

# ---------------------------------------------------------------------------
# Constraints
# ---------------------------------------------------------------------------
# Constraint 1: a player can't be on more than 1 court in a given round
for p in players:
    for r in rounds:
        model.add(
            sum(
                x[(p1, p2, r, c, t)]
                for (p1, p2) in player_pairs
                for c in courts
                for t in range(2)
                if p1 == p or p2 == p
            )
            <= 1
        )

# Constraint 2: each team slot must have exactly 1 pair per court per round
for r in rounds:
    for c in courts:
        for t in range(2):
            model.add(sum(x[(p1, p2, r, c, t)] for (p1, p2) in player_pairs) == 1)

# Symmetry breaking: team 0 always holds the lower-indexed pair in player_pairs,
# eliminating the 2^(ROUNDS*COURTS) symmetric solutions from swapping team labels.
for r in rounds:
    for c in courts:
        model.add(
            sum(i * x[(p1, p2, r, c, 0)] for i, (p1, p2) in enumerate(player_pairs))
            <= sum(i * x[(p1, p2, r, c, 1)] for i, (p1, p2) in enumerate(player_pairs))
        )

# Symmetry breaking: enforce a total ordering of courts within each round by their
# team-0 pair index, eliminating COURTS!^ROUNDS symmetric solutions from court swaps.
for r in rounds:
    for c in range(COURTS - 1):
        model.add(
            sum(i * x[(p1, p2, r, c, 0)] for i, (p1, p2) in enumerate(player_pairs))
            <= sum(i * x[(p1, p2, r, c + 1, 0)] for i, (p1, p2) in enumerate(player_pairs))
        )

_player_pairs_set = set(player_pairs)

# Constraint 3: player avoidance preferences — never pair avoided players together
for p, prefs in player_preferences.items():
    if p not in players:
        continue
    for p_avoid in prefs["avoid"]:
        if p_avoid not in players:
            continue
        pair = (p, p_avoid) if (p, p_avoid) in _player_pairs_set else (p_avoid, p)
        for r in rounds:
            for c in courts:
                for t in range(2):
                    model.add(x[(pair[0], pair[1], r, c, t)] == 0)

# z definition: z[p,r] = 1 iff player p plays in round r
for p in players:
    for r in rounds:
        model.add(
            z[(p, r)]
            == sum(
                x[(p1, p2, r, c, t)]
                for (p1, p2) in player_pairs
                for c in courts
                for t in range(2)
                if p1 == p or p2 == p
            )
        )

# Player allocations: round-level availability rules from PLAYER_ALLOCATIONS.
# Round numbers in the config are 1-indexed; internally rounds are 0-indexed.
available_rounds = {p: set(rounds) for p in players}
for p, _alloc in player_allocations.items():
    if p not in _players_set:
        continue
    for _rnd in _alloc.get("must_not_play", []):
        available_rounds[p].discard(_rnd - 1)
    _from = _alloc.get("unavailable_from")
    if _from is not None:
        available_rounds[p] -= {r for r in rounds if r >= _from - 1}
    _arrive = _alloc.get("available_from")
    if _arrive is not None:
        available_rounds[p] -= {r for r in rounds if r < _arrive - 1}

# Constraint 4a: a player never plays a round they are unavailable for
for p in players:
    for r in rounds:
        if r not in available_rounds[p]:
            model.add(z[(p, r)] == 0)

# Constraint 4b: a player must play the rounds they are required to play
required_rounds = {p: set() for p in players}
for p, _alloc in player_allocations.items():
    if p not in _players_set:
        continue
    for _rnd in _alloc.get("must_play", []):
        assert (_rnd - 1) in available_rounds[p], (
            f"{p}: must_play round {_rnd} conflicts with an unavailability rule"
        )
        required_rounds[p].add(_rnd - 1)
        model.add(z[(p, _rnd - 1)] == 1)

# consec3 definition: consec3[p,r] = 1 if player p plays in all 3 of rounds r, r+1, r+2
# (only defined for players not exempt from the consecutive-games penalty)
for (p, r), _c3 in consec3.items():
    model.add(_c3 >= z[(p, r)] + z[(p, r + 1)] + z[(p, r + 2)] - 2)

# Constraint 6: a player can be on break for at most 1 consecutive round
# (only enforced across rounds the player is actually available for — an
# unavailable round is an absence, not a break, and breaks the chain)
for p in players:
    for r in range(ROUNDS - 1):
        if r in available_rounds[p] and (r + 1) in available_rounds[p]:
            model.add(z[(p, r)] + z[(p, r + 1)] >= 1)

members = [p["user_id"] for p in player_data if p["member"]]
casuals = [p["user_id"] for p in player_data if not p["member"]]


def _total_games(p):
    return sum(
        x[(p1, p2, r, c, t)]
        for (p1, p2) in player_pairs
        for r in rounds
        for c in courts
        for t in range(2)
        if p1 == p or p2 == p
    )


# Constraint 7: every member plays at least as many games as every casual
for member in members:
    for casual in casuals:
        model.add(_total_games(member) >= _total_games(casual))

# M and m definitions: M >= games played by any player, m <= games played by any player
for p in players:
    _games = _total_games(p)
    model.add(M >= _games)
    model.add(m <= _games)

# w definition: w[p1,p2] can only be 1 if p1 and p2 partnered at least once
for (p1, p2), w_var in w.items():
    model.add(
        w_var <= sum(x[(p1, p2, r, c, t)] for r in rounds for c in courts for t in range(2))
    )

# Skill balance: diff[r,c] = |skill_team0 - skill_team1| on court c in round r
# Using level sums (integers); diff is linearised absolute value via two constraints
for r in rounds:
    for c in courts:
        _s0 = sum(_pair_skill[(p1, p2)] * x[(p1, p2, r, c, 0)] for (p1, p2) in player_pairs)
        _s1 = sum(_pair_skill[(p1, p2)] * x[(p1, p2, r, c, 1)] for (p1, p2) in player_pairs)
        model.add(diff[(r, c)] >= _s0 - _s1)
        model.add(diff[(r, c)] >= _s1 - _s0)

# ---------------------------------------------------------------------------
# Objective
# ---------------------------------------------------------------------------
# Objective 1: maximise partner preference scores (already scaled by SCALE).
# A pair is scored by the AVERAGE of the two players' preferences for each other,
# not the sum, so a mutually-preferred pair is not counted twice.
obj_preference = (
    [
        x[(p1, p2, r, c, t)]
        for (p1, p2) in player_pairs
        for r in rounds
        for c in courts
        for t in range(2)
    ],
    [
        round((preference_score.get((p1, p2), 0) + preference_score.get((p2, p1), 0)) / 2)
        for (p1, p2) in player_pairs
        for r in rounds
        for c in courts
        for t in range(2)
    ],
)

# Objective 2: maximise partnership variety as a proxy for opponent variety
obj_variety = (list(w.values()), [10 * SCALE] * len(w))

# Objective 4: minimise occurrences of 3 consecutive games for any player
obj_consecutive = (list(consec3.values()), [-10 * SCALE] * len(consec3))

# Objective 5: minimise sum of skill differences across all games
obj_skill_balance = (list(diff.values()), [-10 * SCALE] * len(diff))

# Objective 3: maximise equality — assemble all objectives and set on model
_all_vars = []
_all_coefs = []
for _vl, _cl in [obj_preference, obj_variety, obj_consecutive, obj_skill_balance]:
    _all_vars.extend(_vl)
    _all_coefs.extend(_cl)
# equality: -10 * SCALE * (M - m) = -10*SCALE*M + 10*SCALE*m
_all_vars.extend([M, m])
_all_coefs.extend([-10 * SCALE, 10 * SCALE])

model.maximize(cp_model.LinearExpr.weighted_sum(_all_vars, _all_coefs))

print("Number of variables =", len(model.proto.variables))
print("Number of constraints =", len(model.proto.constraints))


# ---------------------------------------------------------------------------
# Schedule rendering
# ---------------------------------------------------------------------------
def render_schedule_html(is_playing, header_comment):
    """Build the schedule table HTML. `is_playing` maps (p1, p2, r, c, t) -> bool."""
    name = {p["user_id"]: p["name"] for p in player_data}
    rows = []
    for r in rounds:
        court_teams = {}
        for c in courts:
            court_teams[c] = [
                next(
                    (
                        (p1, p2)
                        for (p1, p2) in player_pairs
                        if is_playing(x[(p1, p2, r, c, t)])
                    ),
                    None,
                )
                for t in range(2)
            ]
        playing = {
            p
            for c in courts
            for pair in court_teams[c]
            if pair is not None
            for p in pair
        }
        on_break = ", ".join(name[p] for p in players if p not in playing)
        for i, c in enumerate(courts):
            teams = court_teams[c]
            if teams[0] and teams[1]:
                t1 = f"{name[teams[0][0]]} / {name[teams[0][1]]}"
                t2 = f"{name[teams[1][0]]} / {name[teams[1][1]]}"
            else:
                t1 = "—"
                t2 = "—"
            if i == 0:
                rows.append(
                    "<tr>"
                    f"<td rowspan='{len(courts)}' style='text-align:center;padding:4px 8px'>{r + 1}</td>"
                    f"<td style='text-align:center;padding:4px 8px'>{c + 1}</td>"
                    f"<td style='padding:4px 8px'>{t1}</td>"
                    f"<td style='padding:4px 8px'>{t2}</td>"
                    f"<td rowspan='{len(courts)}' style='padding:4px 8px'>{on_break}</td>"
                    "</tr>"
                )
            else:
                rows.append(
                    "<tr>"
                    f"<td style='text-align:center;padding:4px 8px'>{c + 1}</td>"
                    f"<td style='padding:4px 8px'>{t1}</td>"
                    f"<td style='padding:4px 8px'>{t2}</td>"
                    "</tr>"
                )
    return (
        f"<!-- {header_comment} -->"
        "<table border='1' style='border-collapse:collapse;width:100%'>"
        "<thead><tr>"
        "<th style='padding:4px 8px'>Round</th>"
        "<th style='padding:4px 8px'>Court</th>"
        "<th style='padding:4px 8px'>Team 1</th>"
        "<th style='padding:4px 8px'>Team 2</th>"
        "<th style='padding:4px 8px'>Break</th>"
        "</tr></thead>"
        "<tbody>" + "".join(rows) + "</tbody>"
        "</table>"
    )


# ---------------------------------------------------------------------------
# Checkpointer: periodically write the current best solution to disk
# ---------------------------------------------------------------------------
class ScheduleCheckpointer(cp_model.CpSolverSolutionCallback):
    def __init__(self):
        super().__init__()
        self._last_saved = 0
        os.makedirs("solution", exist_ok=True)

    def on_solution_callback(self):
        print(f"  obj={self.objective_value:.0f}  t={self.wall_time:.1f}s")
        if time.time() - self._last_saved < 180:  # 3 minutes
            return
        self._last_saved = time.time()
        html = render_schedule_html(
            self.boolean_value,
            f"obj={self.objective_value:.0f} t={self.wall_time:.1f}s",
        )
        stamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        path = f"solution/schedule_best_{stamp}.html"
        with open(path, "w") as f:
            f.write(html)
        print(f"  -> checkpoint saved to {path}")


checkpointer = ScheduleCheckpointer()

# ---------------------------------------------------------------------------
# Warm start
# ---------------------------------------------------------------------------
_breaks = {p: 0 for p in players}
_break_count = len(players) - len(courts) * 4

for _r in rounds:
    # players who cannot play this round must sit; players required to play cannot
    _cant_play = {p for p in players if _r not in available_rounds[p]}
    _must_play = {p for p in players if _r in required_rounds[p]}
    _candidates = sorted(
        [p for p in players if p not in _cant_play and p not in _must_play],
        key=lambda p: (_breaks[p], players.index(p)),
    )
    _n_extra = max(0, _break_count - len(_cant_play))
    _break_players = _cant_play | set(_candidates[:_n_extra])
    for _p in _break_players:
        if _p not in _cant_play:
            _breaks[_p] += 1

    _active = sorted(
        [p for p in players if p not in _break_players],
        key=lambda p: _level[p],
        reverse=True,
    )
    for _c in courts:
        _cp = _active[_c * 4 : (_c + 1) * 4]
        for _team, (_a, _b) in enumerate([(_cp[0], _cp[3]), (_cp[1], _cp[2])]):
            _pair = (_a, _b) if (_a, _b) in _pairs_set else (_b, _a)
            model.add_hint(x[(_pair[0], _pair[1], _r, _c, _team)], 1)

print(f"Warm start: hints set for {len(rounds)} rounds × {len(courts)} courts")

# ---------------------------------------------------------------------------
# Solve
# ---------------------------------------------------------------------------
_status_map = {
    cp_model.OPTIMAL: "OPTIMAL",
    cp_model.FEASIBLE: "FEASIBLE",
    cp_model.INFEASIBLE: "INFEASIBLE",
    cp_model.UNKNOWN: "UNKNOWN",
    cp_model.MODEL_INVALID: "MODEL_INVALID",
}
cp_solver = cp_model.CpSolver()
cp_solver.parameters.max_time_in_seconds = 1800
solve_status = cp_solver.solve(model, checkpointer)
print("Solver status:", _status_map.get(solve_status, f"UNKNOWN ({solve_status})"))

# ---------------------------------------------------------------------------
# Write final schedule
# ---------------------------------------------------------------------------
if solve_status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    schedule_html = render_schedule_html(
        cp_solver.boolean_value, f"solve_status={solve_status}"
    )
    with open("schedule.html", "w") as f:
        f.write(schedule_html)
    print("Wrote schedule.html")
else:
    print("No feasible solution found; schedule.html not written.")
