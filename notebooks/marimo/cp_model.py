import marimo

__generated_with = "0.23.9"
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
    }
    return (player_preferences,)


@app.cell
def _():
    player_data = [
        {"user_id": "thenes", "name": "Thenes", "member": True, "level" : 5},
        {"user_id": "jack", "name": "Jack", "member": True, "level" : 5},
        {"user_id": "andy", "name": "Andy", "member": True, "level" : 5},
        {"user_id": "suandi", "name": "Suandi", "member": True, "level" : 5},
        {"user_id": "harry", "name": "Harry", "member": True, "level" : 5},
        {"user_id": "lesley", "name": "Lesley", "member": True, "level" : 2},
        {"user_id": "sumit", "name": "Sumit", "member": True, "level" : 5},
        {"user_id": "naresh", "name": "Naresh", "member": True, "level" : 3},
        {"user_id": "shahar", "name": "Shahar", "member": False, "level" : 4},
        {"user_id": "ulf", "name": "Ulf", "member": True, "level" : 3},
        {"user_id": "sandy", "name": "Sandy", "member": True, "level" : 5},
        {"user_id": "nithin", "name": "Nithin", "member": False, "level" : 4},
    ]

    ROUNDS = 10
    COURTS = 2
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

    # x[p1, p2, r, c]: p1 and p2 are paired as a team on court c in round r
    x = {
        (p1, p2, r, c): model.new_bool_var(f'x_{p1}_{p2}_{r}_{c}')
        for (p1, p2) in player_pairs
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
    return M, consec3, courts, m, model, player_pairs, players, rounds, w, x, z


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Constraints
    """)
    return


@app.cell
def _(
    M,
    ROUNDS,
    consec3,
    courts,
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
                    x[(p1, p2, r, c)]
                    for (p1, p2) in player_pairs
                    for c in courts
                    if p1 == p or p2 == p
                ) <= 1
            )

    # Constraint 2: each court must have exactly 2 pairs (4 players) per round
    for r in rounds:
        for c in courts:
            model.add(sum(x[(p1, p2, r, c)] for (p1, p2) in player_pairs) == 2)

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
                    model.add(x[(pair[0], pair[1], r, c)] == 0)

    # z definition: z[p,r] = 1 iff player p plays in round r
    for p in players:
        for r in rounds:
            model.add(
                z[(p, r)] == sum(
                    x[(p1, p2, r, c)]
                    for (p1, p2) in player_pairs
                    for c in courts
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
            x[(p1, p2, r, c)]
            for (p1, p2) in player_pairs
            for r in rounds
            for c in courts
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
        model.add(w_var <= sum(x[(p1, p2, r, c)] for r in rounds for c in courts))

    # Skill balance: use sum-based pair skill (CP-SAT requires integers; avg = sum/2)
    _level = {p["user_id"]: p["level"] for p in player_data}
    _pair_skill = {(p1, p2): _level[p1] + _level[p2] for (p1, p2) in player_pairs}
    _skill_vals = list(_pair_skill.values())
    _max_diff = max(_skill_vals) - min(_skill_vals)

    D_max = model.new_int_var(0, _max_diff, 'D_max')
    D_min = model.new_int_var(0, _max_diff, 'D_min')

    for _i, _A in enumerate(player_pairs):
        for _B in player_pairs[_i + 1:]:
            if _A[0] in _B or _A[1] in _B:
                continue
            _diff = abs(_pair_skill[_A] - _pair_skill[_B])
            for _r in rounds:
                for _c in courts:
                    _assigned = x[_A + (_r, _c)] + x[_B + (_r, _c)]
                    model.add(D_max >= _diff * (_assigned - 1))
                    model.add(D_min <= _diff + _max_diff * (2 - _assigned))
    return D_max, D_min


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
        [x[(p1, p2, r, c)] for (p1, p2) in player_pairs for r in rounds for c in courts],
        [preference_score.get((p1, p2), 0) + preference_score.get((p2, p1), 0)
         for (p1, p2) in player_pairs for r in rounds for c in courts],
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
def _(D_max, D_min, SCALE):
    # Objective 5: minimise spread of skill differences across games
    # Pair skill uses sum (not avg) so coef is -5*SCALE to keep the same per-avg-unit weight
    obj_skill_balance = ([D_max, D_min], [-5 * SCALE, 5 * SCALE])
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
def _(cp_model, mo, model):
    _status_map = {
        cp_model.OPTIMAL: ("OPTIMAL", "green"),
        cp_model.FEASIBLE: ("FEASIBLE", "orange"),
        cp_model.INFEASIBLE: ("INFEASIBLE", "red"),
        cp_model.UNKNOWN: ("UNKNOWN", "gray"),
        cp_model.MODEL_INVALID: ("MODEL_INVALID", "red"),
    }
    cp_solver = cp_model.CpSolver()
    cp_solver.parameters.max_time_in_seconds = 900
    solve_status = cp_solver.solve(model)
    _label, _color = _status_map.get(solve_status, (f"UNKNOWN ({solve_status})", "red"))
    mo.callout(
        mo.md(f"Solver status: **{_label}**"),
        kind="success" if _color == "green" else "warn" if _color == "orange" else "danger" if _color == "red" else "info"
    )
    return cp_solver, solve_status


@app.cell
def _(
    courts,
    cp_solver,
    player_data,
    player_pairs,
    players,
    rounds,
    solve_status,
    x,
):
    _name = {p["user_id"]: p["name"] for p in player_data}
    _rows = []

    for _r in rounds:
        _court_teams = {}
        for _c in courts:
            _court_teams[_c] = [
                (_p1, _p2) for (_p1, _p2) in player_pairs
                if cp_solver.boolean_value(x[(_p1, _p2, _r, _c)])
            ]

        _playing = {
            _p
            for _c in courts
            for (_p1, _p2) in _court_teams[_c]
            for _p in (_p1, _p2)
        }
        _on_break = ", ".join(_name[_p] for _p in players if _p not in _playing)

        for _i, _c in enumerate(courts):
            _teams = _court_teams[_c]
            if len(_teams) == 2:
                _t1 = f"{_name[_teams[0][0]]} / {_name[_teams[0][1]]}"
                _t2 = f"{_name[_teams[1][0]]} / {_name[_teams[1][1]]}"
            else:
                _t1 = "—"
                _t2 = "—"

            if _i == 0:
                _rows.append(
                    f"<tr>"
                    f"<td rowspan='2' style='text-align:center;padding:4px 8px'>{_r + 1}</td>"
                    f"<td style='text-align:center;padding:4px 8px'>{_c + 1}</td>"
                    f"<td style='padding:4px 8px'>{_t1}</td>"
                    f"<td style='padding:4px 8px'>{_t2}</td>"
                    f"<td rowspan='2' style='padding:4px 8px'>{_on_break}</td>"
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

    schedule_html = (
        f"<!-- solve_status={solve_status} -->"
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
    return (schedule_html,)


@app.cell
def _(schedule_html):
    with open("schedule.html", "w") as _f:
        _f.write(schedule_html)
    return


if __name__ == "__main__":
    app.run()
