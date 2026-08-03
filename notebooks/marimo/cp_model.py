import marimo

__generated_with = "0.23.14"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    from ortools.sat.python import cp_model

    return (cp_model,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Configuration
    """)
    return


@app.cell
def _():
    # player partner preference
    player_preferences = {
        "sandy" : {
            "pair_up_preference" : [
                ("sumit", 1),
                ("harry", 2),
                ("thenes", 3),
                ("jack", 4),
            ],
            "avoid" : ["akhil_srikanth", "lesley", "yaw", "anoop", "naresh"]
        },
        "thenes" : {
            "pair_up_preference" : [
                ("sumit", 1),
                ("harry", 2),
                ("suandi", 3)
            ],
            "avoid" : ["andy", "lesley", "ulf"]
        },
        # "habby" : {
        #     "pair_up_preference" : [
        #         ("sumit", 1),
        #         ("thenes", 2),
        #         ("harry", 3),
        #     ],
        #     "avoid" : ["shahar", "raheel", "ulf", "wilson"]
        # },
        "naresh" : {
            "pair_up_preference" : [
                ("sumit", 1),
                ("suandi", 2),
                ("harry", 3),
                ("andy", 4),
            ],
            "avoid" : []
        },
        "jack" : {
            "pair_up_preference" : [],
            "avoid" : ["andy", "sachi"]
        },

    }
    return (player_preferences,)


@app.cell
def _():
    player_data = [
        {"user_id": "thenes", "name": "Thenes", "member": True, "level" : 5},
        {"user_id": "jack", "name": "Jack", "member": True, "level" : 5},
        {"user_id": "andy", "name": "Andy", "member": True, "level" : 5},
        {"user_id": "suandi", "name": "Suandi", "member": True, "level" : 5},
        {"user_id": "harry", "name": "Harry", "member": True, "level" : 4},
        {"user_id": "lesley", "name": "Lesley", "member": True, "level" : 1},
        {"user_id": "sumit", "name": "Sumit", "member": True, "level" : 5},
        {"user_id": "naresh", "name": "Naresh", "member": True, "level" : 3},
        {"user_id": "aviral", "name": "Aviral", "member": True, "level" : 3},
        {"user_id": "yaw", "name": "Yaw", "member": True, "level" : 4},
        {"user_id": "pritto", "name": "Pritto", "member": True, "level" : 2},
        {"user_id": "sachi", "name": "Sachi", "member": True, "level" : 2},
        {"user_id": "kelvin", "name": "Kelvin", "member": True, "level" : 5},
        {"user_id": "barrie", "name": "Barrie", "member": True, "level" : 5},
        {"user_id": "annie", "name": "Annie", "member": True, "level" : 4},

        # casuals
        {"user_id": "nithin", "name": "Nithin", "member": False, "level" : 3},
        {"user_id": "shahar", "name": "Shahar", "member": False, "level" : 4},
        {"user_id": "danish", "name": "Danish", "member": False, "level" : 3},
        {"user_id": "hridaan", "name": "Hridaan", "member": False, "level" : 5},
        {"user_id": "chinu", "name": "Chinu", "member": False, "level" : 5},
        {"user_id": "karthik", "name": "Karthik", "member": False, "level" : 4},
        {"user_id": "hamza", "name": "Hamza", "member": False, "level" : 2},
    ]

    ROUNDS = 10
    COURTS = 4
    N_PLAYERS = len(player_data)
    print(N_PLAYERS)
    return COURTS, ROUNDS, player_data


@app.cell
def _(player_data, player_preferences):
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
            return (10 / (l_p + 1)) * (l_p + 2 - pair_up[p_prime])
        else:
            return 10 / (l_p + 1)

    _players = [p["user_id"] for p in player_data]
    preference_score = {
        (p, p_prime): int(round(_compute_score(p, p_prime) * SCALE))
        for p in _players
        for p_prime in _players
        if p != p_prime
    }
    return SCALE, preference_score


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Variables
    """)
    return


@app.cell
def _(COURTS, ROUNDS, cp_model, player_data, player_preferences):
    from itertools import combinations

    players = [p["user_id"] for p in player_data]
    player_pairs = list(combinations(players, 2))
    rounds = range(ROUNDS)
    courts = range(COURTS)

    model = cp_model.CpModel()

    # x[p1, p2, r, c, t]: p1 and p2 are paired as team t (0 or 1) on court c in round r
    x = {
        (p1, p2, r, c, t): model.new_bool_var(f'x_{p1}_{p2}_{r}_{c}_{t}')
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
        (r, c): model.new_int_var(0, _max_possible_diff, f'diff_{r}_{c}')
        for r in rounds
        for c in courts
    }

    # M: maximum number of games played by any player
    M = model.new_int_var(0, ROUNDS, 'M')

    # m: minimum number of games played by any player
    m = model.new_int_var(0, ROUNDS, 'm')

    # z[p, r]: whether player p played in round r
    z = {
        (p, r): model.new_bool_var(f'z_{p}_{r}')
        for p in players
        for r in rounds
    }

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
        (p1, p2): model.new_bool_var(f'w_{p1}_{p2}')
        for (p1, p2) in player_pairs
        if (p1, p2) not in _avoided
    }

    # consec3[p, r]: 1 if player p plays in rounds r, r+1, and r+2
    consec3 = {
        (p, r): model.new_bool_var(f'consec3_{p}_{r}')
        for p in players
        for r in range(ROUNDS - 2)
    }
    return (
        M,
        consec3,
        courts,
        diff,
        m,
        model,
        player_pairs,
        players,
        rounds,
        w,
        x,
        z,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Constraints
    """)
    return


@app.cell
def _(
    COURTS,
    M,
    ROUNDS,
    consec3,
    courts,
    diff,
    m,
    model,
    player_data,
    player_pairs,
    player_preferences,
    players,
    rounds,
    w,
    x,
    z,
):
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
                ) <= 1
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
                <=
                sum(i * x[(p1, p2, r, c, 1)] for i, (p1, p2) in enumerate(player_pairs))
            )

    # Symmetry breaking: enforce a total ordering of courts within each round by their
    # team-0 pair index, eliminating COURTS!^ROUNDS symmetric solutions from court swaps.
    for r in rounds:
        for c in range(COURTS - 1):
            model.add(
                sum(i * x[(p1, p2, r, c, 0)]     for i, (p1, p2) in enumerate(player_pairs))
                <=
                sum(i * x[(p1, p2, r, c + 1, 0)] for i, (p1, p2) in enumerate(player_pairs))
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
                z[(p, r)] == sum(
                    x[(p1, p2, r, c, t)]
                    for (p1, p2) in player_pairs
                    for c in courts
                    for t in range(2)
                    if p1 == p or p2 == p
                )
            )

    # # Constraint 5: a player can play at most 2 games in 3 consecutive rounds
    # for p in players:
    #     for r in range(ROUNDS - 2):
    #         model.add(z[(p, r)] + z[(p, r + 1)] + z[(p, r + 2)] <= 2)

    # consec3 definition: consec3[p,r] = 1 if player p plays in all 3 of rounds r, r+1, r+2
    for p in players:
        for r in range(ROUNDS - 2):
            model.add(consec3[(p, r)] >= z[(p, r)] + z[(p, r + 1)] + z[(p, r + 2)] - 2)

    # Constraint 6: a player can be on break for at most 1 consecutive round
    for p in players:
        for r in range(ROUNDS - 1):
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
        model.add(w_var <= sum(x[(p1, p2, r, c, t)] for r in rounds for c in courts for t in range(2)))

    # Skill balance: diff[r,c] = |avg_skill_team0 - avg_skill_team1| on court c in round r
    # Using level sums (integers); diff is linearised absolute value via two constraints
    _level = {p["user_id"]: p["level"] for p in player_data}
    _pair_skill = {(p1, p2): _level[p1] + _level[p2] for (p1, p2) in player_pairs}
    for r in rounds:
        for c in courts:
            _s0 = sum(_pair_skill[(p1, p2)] * x[(p1, p2, r, c, 0)] for (p1, p2) in player_pairs)
            _s1 = sum(_pair_skill[(p1, p2)] * x[(p1, p2, r, c, 1)] for (p1, p2) in player_pairs)
            model.add(diff[(r, c)] >= _s0 - _s1)
            model.add(diff[(r, c)] >= _s1 - _s0)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Objective
    """)
    return


@app.cell
def _(courts, player_pairs, preference_score, rounds, x):
    # Objective 1: maximise partner preference scores (already scaled by SCALE)
    obj_preference = (
        [x[(p1, p2, r, c, t)] for (p1, p2) in player_pairs for r in rounds for c in courts for t in range(2)],
        [preference_score.get((p1, p2), 0) + preference_score.get((p2, p1), 0)
         for (p1, p2) in player_pairs for r in rounds for c in courts for t in range(2)],
    )
    return (obj_preference,)


@app.cell
def _(SCALE, w):
    # Objective 2: maximise partnership variety as a proxy for opponent variety
    obj_variety = (list(w.values()), [10 * SCALE] * len(w))
    return (obj_variety,)


@app.cell
def _(SCALE, consec3):
    # Objective 4: minimise occurrences of 3 consecutive games for any player
    obj_consecutive = (list(consec3.values()), [-10 * SCALE] * len(consec3))
    return (obj_consecutive,)


@app.cell
def _(SCALE, diff):
    # Objective 5: minimise sum of skill differences across all games
    obj_skill_balance = (list(diff.values()), [-10 * SCALE] * len(diff))
    return (obj_skill_balance,)


@app.cell
def _(
    M,
    SCALE,
    cp_model,
    m,
    model,
    obj_consecutive,
    obj_preference,
    obj_skill_balance,
    obj_variety,
):
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
    return


@app.cell
def _(model):
    print("Number of variables =", len(model.proto.variables))
    print("Number of constraints =", len(model.proto.constraints))
    return


@app.cell
def _(courts, cp_model, player_data, player_pairs, players, rounds, x):
    import os
    import time

    class ScheduleCheckpointer(cp_model.CpSolverSolutionCallback):
        def __init__(self):
            super().__init__()
            self._name = {p["user_id"]: p["name"] for p in player_data}
            self._last_saved = 0
            os.makedirs("solution", exist_ok=True)

        def on_solution_callback(self):
            print(f"  obj={self.objective_value:.0f}  t={self.wall_time:.1f}s")
            if time.time() - self._last_saved < 180:  # 2.5 minutes
                return
            self._last_saved = time.time()
            _rows = []
            for _r in rounds:
                _court_teams = {}
                for _c in courts:
                    _court_teams[_c] = [
                        next(
                            ((_p1, _p2) for (_p1, _p2) in player_pairs
                             if self.boolean_value(x[(_p1, _p2, _r, _c, _t)])),
                            None
                        )
                        for _t in range(2)
                    ]
                _playing = {
                    _p
                    for _c in courts
                    for _pair in _court_teams[_c]
                    if _pair is not None
                    for _p in _pair
                }
                _on_break = ", ".join(self._name[_p] for _p in players if _p not in _playing)
                for _i, _c in enumerate(courts):
                    _teams = _court_teams[_c]
                    if _teams[0] and _teams[1]:
                        _t1 = f"{self._name[_teams[0][0]]} / {self._name[_teams[0][1]]}"
                        _t2 = f"{self._name[_teams[1][0]]} / {self._name[_teams[1][1]]}"
                    else:
                        _t1 = "—"
                        _t2 = "—"
                    if _i == 0:
                        _rows.append(
                            f"<tr>"
                            f"<td rowspan='{len(courts)}' style='text-align:center;padding:4px 8px'>{_r + 1}</td>"
                            f"<td style='text-align:center;padding:4px 8px'>{_c + 1}</td>"
                            f"<td style='padding:4px 8px'>{_t1}</td>"
                            f"<td style='padding:4px 8px'>{_t2}</td>"
                            f"<td rowspan='{len(courts)}' style='padding:4px 8px'>{_on_break}</td>"
                            f"</tr>"
                        )
                    else:
                        _rows.append(
                            f"<tr>"
                            f"<td style='text-align:center;padding:4px 8px'>{_c + 1}</td>"
                            f"<td style='padding:4px 8px'>{_t1}</td>"
                            f"<td style='padding:4px 8px'>{_t2}</td>"
                            f"</tr>"
                        )
            _html = (
                f"<!-- obj={self.objective_value:.0f} t={self.wall_time:.1f}s -->"
                "<table border='1' style='border-collapse:collapse;width:100%'>"
                "<thead><tr>"
                "<th style='padding:4px 8px'>Round</th>"
                "<th style='padding:4px 8px'>Court</th>"
                "<th style='padding:4px 8px'>Team 1</th>"
                "<th style='padding:4px 8px'>Team 2</th>"
                "<th style='padding:4px 8px'>Break</th>"
                "</tr></thead>"
                "<tbody>" + "".join(_rows) + "</tbody>"
                "</table>"
            )
            with open(f"solution/schedule_best_{time.strftime('%Y-%m-%d_%H-%M-%S')}.html", "w") as _f:
                _f.write(_html)
            print(f"  -> checkpoint saved to solution/schedule_best_{time.strftime('%Y-%m-%d_%H-%M-%S')}.html")

    checkpointer = ScheduleCheckpointer()
    return (checkpointer,)


@app.cell
def _(courts, model, player_data, player_pairs, players, rounds, x):
    _level = {p["user_id"]: p["level"] for p in player_data}
    _pairs_set = set(player_pairs)
    _breaks = {p: 0 for p in players}
    _break_count = len(players) - len(courts) * 4

    for _r in rounds:
        _by_breaks = sorted(players, key=lambda p: (_breaks[p], players.index(p)))
        _break_players = set(_by_breaks[:_break_count])
        for _p in _break_players:
            _breaks[_p] += 1

        _active = sorted(
            [p for p in players if p not in _break_players],
            key=lambda p: _level[p], reverse=True
        )
        for _c in courts:
            _cp = _active[_c * 4:(_c + 1) * 4]
            for _team, (_a, _b) in enumerate([(_cp[0], _cp[3]), (_cp[1], _cp[2])]):
                _pair = (_a, _b) if (_a, _b) in _pairs_set else (_b, _a)
                model.add_hint(x[(_pair[0], _pair[1], _r, _c, _team)], 1)

    print(f"Warm start: hints set for {len(rounds)} rounds × {len(courts)} courts")
    warm_start_done = True
    return (warm_start_done,)


@app.cell
def _(checkpointer, cp_model, mo, model, warm_start_done):
    _status_map = {
        cp_model.OPTIMAL: ("OPTIMAL", "green"),
        cp_model.FEASIBLE: ("FEASIBLE", "orange"),
        cp_model.INFEASIBLE: ("INFEASIBLE", "red"),
        cp_model.UNKNOWN: ("UNKNOWN", "gray"),
        cp_model.MODEL_INVALID: ("MODEL_INVALID", "red"),
    }
    cp_solver = cp_model.CpSolver()
    cp_solver.parameters.max_time_in_seconds = 1800
    solve_status = cp_solver.solve(model, checkpointer)
    _label, _color = _status_map.get(solve_status, (f"UNKNOWN ({solve_status})", "red"))
    mo.callout(
        mo.md(f"Solver status: **{_label}**"),
        kind="success" if _color == "green" else "warn" if _color == "orange" else "danger" if _color == "red" else "info"
    )
    return


@app.cell
def _():
    # _name = {p["user_id"]: p["name"] for p in player_data}
    # _rows = []

    # for _r in rounds:
    #     _court_teams = {}
    #     for _c in courts:
    #         _court_teams[_c] = [
    #             next(
    #                 ((_p1, _p2) for (_p1, _p2) in player_pairs
    #                  if cp_solver.boolean_value(x[(_p1, _p2, _r, _c, _t)])),
    #                 None
    #             )
    #             for _t in range(2)
    #         ]

    #     _playing = {
    #         _p
    #         for _c in courts
    #         for _pair in _court_teams[_c]
    #         if _pair is not None
    #         for _p in _pair
    #     }
    #     _on_break = ", ".join(_name[_p] for _p in players if _p not in _playing)

    #     for _i, _c in enumerate(courts):
    #         _teams = _court_teams[_c]
    #         if _teams[0] and _teams[1]:
    #             _t1 = f"{_name[_teams[0][0]]} / {_name[_teams[0][1]]}"
    #             _t2 = f"{_name[_teams[1][0]]} / {_name[_teams[1][1]]}"
    #         else:
    #             _t1 = "—"
    #             _t2 = "—"

    #         if _i == 0:
    #             _rows.append(
    #                 f"<tr>"
    #                 f"<td rowspan='{len(courts)}' style='text-align:center;padding:4px 8px'>{_r + 1}</td>"
    #                 f"<td style='text-align:center;padding:4px 8px'>{_c + 1}</td>"
    #                 f"<td style='padding:4px 8px'>{_t1}</td>"
    #                 f"<td style='padding:4px 8px'>{_t2}</td>"
    #                 f"<td rowspan='{len(courts)}' style='padding:4px 8px'>{_on_break}</td>"
    #                 f"</tr>"
    #             )
    #         else:
    #             _rows.append(
    #                 f"<tr>"
    #                 f"<td style='text-align:center;padding:4px 8px'>{_c + 1}</td>"
    #                 f"<td style='padding:4px 8px'>{_t1}</td>"
    #                 f"<td style='padding:4px 8px'>{_t2}</td>"
    #                 f"</tr>"
    #             )

    # schedule_html = (
    #     f"<!-- solve_status={solve_status} -->"
    #     "<table border='1' style='border-collapse:collapse;width:100%'>"
    #     "<thead><tr>"
    #     "<th style='padding:4px 8px'>Round</th>"
    #     "<th style='padding:4px 8px'>Court</th>"
    #     "<th style='padding:4px 8px'>Team 1</th>"
    #     "<th style='padding:4px 8px'>Team 2</th>"
    #     "<th style='padding:4px 8px'>Break</th>"
    #     "</tr></thead>"
    #     "<tbody>" + "".join(_rows) + "</tbody>"
    #     "</table>"
    # )
    return


@app.cell
def _():
    # with open("schedule.html", "w") as _f:
    #     _f.write(schedule_html)
    return


if __name__ == "__main__":
    app.run()
