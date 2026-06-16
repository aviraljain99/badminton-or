import marimo

__generated_with = "0.23.6"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    from ortools.linear_solver import pywraplp

    return (pywraplp,)


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
        # "sandy" : {
        #     "pair_up_preference" : [
        #         ("sumit", 1),
        #         ("annie_george", 2),
        #         ("harry", 3),
        #         ("thenes", 4)
        #     ],
        #     "avoid" : ["akhil_srikanth", "yaw", "shahar", "faisal", "anoop", "naresh", "sachee", "faisal"]
        # },
        "thenes" : {
            "pair_up_preference" : [
                ("sumit", 1),
                ("harry", 2),
                ("suandi", 3)
            ],
            "avoid" : ["andy", "raheel", "ulf"]
        },
        "habby" : {
            "pair_up_preference" : [
                ("sumit", 1),
                ("thenes", 2),
                ("harry", 3),
            ],
            "avoid" : ["shahar", "raheel", "ulf", "wilson"]
        }
        # "naresh" : {
        #     "pair_up_preference" : [
        #         ("sumit", 1),
        #         ("suandi", 2),
        #         ("harry", 3),
        #         ("andy", 4),
        #         ("yaw", 5)
        #     ],
        #     "avoid" : []
        # },
    }
    return (player_preferences,)


@app.cell
def _():
    player_data = [
        {"user_id": "thenes", "name": "Thenes", "member": True},
        {"user_id": "jack", "name": "Jack", "member": True},
        {"user_id": "andy", "name": "Andy", "member": True},
        {"user_id": "suandi", "name": "Suandi", "member": True},
        {"user_id": "harry", "name": "Harry", "member": True},
        {"user_id": "raheel", "name": "Raheel", "member": False},
        {"user_id": "sumit", "name": "Sumit", "member": True},
        {"user_id": "habby", "name": "Habby", "member": True},
        {"user_id": "shahar", "name": "Shahar", "member": False},
        {"user_id": "wilson", "name": "Wilson", "member": False},
        {"user_id": "kelvin", "name": "Kelvin", "member": True},
        {"user_id": "ulf", "name": "Ulf", "member": True},
    ]

    ROUNDS = 10
    COURTS = 2
    N_PLAYERS = len(player_data)
    print(N_PLAYERS)
    return COURTS, ROUNDS, player_data


@app.cell
def _(player_data, player_preferences):
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
        (p, p_prime): _compute_score(p, p_prime)
        for p in _players
        for p_prime in _players
        if p != p_prime
    }
    return (preference_score,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Variables
    """)
    return


@app.cell
def _(COURTS, ROUNDS, player_data, player_preferences, pywraplp):
    from itertools import combinations

    players = [p["user_id"] for p in player_data]
    player_pairs = list(combinations(players, 2))
    rounds = range(ROUNDS)
    courts = range(COURTS)

    solver = pywraplp.Solver.CreateSolver('SCIP')

    # x[p1, p2, r, c]: p1 and p2 are paired as a team on court c in round r
    x = {
        (p1, p2, r, c): solver.BoolVar(f'x_{p1}_{p2}_{r}_{c}')
        for (p1, p2) in player_pairs
        for r in rounds
        for c in courts
    }

    # # y_rc[p1, p2, r, c]: p1 and p2 opposed each other on court c in round r
    # y_rc = {
    #     (p1, p2, r, c): solver.BoolVar(f'y_rc_{p1}_{p2}_{r}_{c}')
    #     for (p1, p2) in player_pairs
    #     for r in rounds
    #     for c in courts
    # }

    # # y_r[p1, p2, r]: p1 and p2 opposed each other in round r
    # y_r = {
    #     (p1, p2, r): solver.BoolVar(f'y_r_{p1}_{p2}_{r}')
    #     for (p1, p2) in player_pairs
    #     for r in rounds
    # }

    # # y[p1, p2]: p1 and p2 opposed each other at any point in the session
    # y = {
    #     (p1, p2): solver.BoolVar(f'y_{p1}_{p2}')
    #     for (p1, p2) in player_pairs
    # }

    # M: maximum number of games played by any player
    M = solver.IntVar(0, ROUNDS, 'M')

    # m: minimum number of games played by any player
    m = solver.IntVar(0, ROUNDS, 'm')

    # z[p, r]: whether player p played in round r
    z = {
        (p, r): solver.BoolVar(f'z_{p}_{r}')
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
        (p1, p2): solver.BoolVar(f'w_{p1}_{p2}')
        for (p1, p2) in player_pairs
        if (p1, p2) not in _avoided
    }

    # consec3[p, r]: 1 if player p plays in rounds r, r+1, and r+2
    consec3 = {
        (p, r): solver.BoolVar(f'consec3_{p}_{r}')
        for p in players
        for r in range(ROUNDS - 2)
    }
    return (
        M,
        consec3,
        courts,
        m,
        player_pairs,
        players,
        rounds,
        solver,
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
    M,
    ROUNDS,
    consec3,
    courts,
    m,
    player_data,
    player_pairs,
    player_preferences,
    players,
    rounds,
    solver,
    w,
    x,
    z,
):
    # Constraint 1: a player can't be on more than 1 court in a given round
    for p in players:
        for r in rounds:
            solver.Add(solver.Sum([
                x[(p1, p2, r, c)]
                for (p1, p2) in player_pairs
                for c in courts
                if p1 == p or p2 == p
            ]) <= 1)

    # Constraint 2: each court must have exactly 2 pairs (4 players) per round
    for r in rounds:
        for c in courts:
            solver.Add(solver.Sum([
                x[(p1, p2, r, c)]
                for (p1, p2) in player_pairs
            ]) == 2)

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
                    solver.Add(x[(pair[0], pair[1], r, c)] == 0)

    # z definition: z[p,r] = 1 iff player p plays in round r
    for p in players:
        for r in rounds:
            solver.Add(z[(p, r)] == solver.Sum([
                x[(p1, p2, r, c)]
                for (p1, p2) in player_pairs
                for c in courts
                if p1 == p or p2 == p
            ]))

    # # Constraint 5: a player can play at most 2 games in 3 consecutive rounds
    # for p in players:
    #     for r in range(ROUNDS - 2):
    #         solver.Add(z[(p, r)] + z[(p, r + 1)] + z[(p, r + 2)] <= 2)

    # consec3 definition: consec3[p,r] = 1 if player p plays in all 3 of rounds r, r+1, r+2
    for p in players:
        for r in range(ROUNDS - 2):
            solver.Add(consec3[(p, r)] >= z[(p, r)] + z[(p, r + 1)] + z[(p, r + 2)] - 2)

    # Constraint 6: a player can be on break for at most 1 consecutive round
    for p in players:
        for r in range(ROUNDS - 1):
            solver.Add(z[(p, r)] + z[(p, r + 1)] >= 1)


    members = [p["user_id"] for p in player_data if p["member"]]
    casuals = [p["user_id"] for p in player_data if not p["member"]]

    def _total_games(p):
        return solver.Sum([
            x[(p1, p2, r, c)]
            for (p1, p2) in player_pairs
            for r in rounds
            for c in courts
            if p1 == p or p2 == p
        ])

    # Constraint 7: every member plays at least as many games as every casual
    for member in members:
        for casual in casuals:
            solver.Add(_total_games(member) >= _total_games(casual))

    # # y definition: y[p,p'] can only be 1 if p and p' are both on opposing teams at least once in the entire session.
    # # For a given r/c combination, the sum counts x variables involving p (excl. p') plus those
    # # involving p' (excl. p) and equals 2 only when both are present on opposing sides.
    # # And then it sums it over all possible r/c combinations.
    # for (p, p_prime) in player_pairs:
    #     _terms = []
    #     for r in rounds:
    #         for c in courts:
    #             _terms.extend(
    #                     [
    #                         x[(p1, p2, r, c)]
    #                         for (p1, p2) in player_pairs
    #                         if (p1 == p or p2 == p) and p1 != p_prime and p2 != p_prime
    #                     ] + [
    #                         x[(p1, p2, r, c)]
    #                         for (p1, p2) in player_pairs
    #                         if (p1 == p_prime or p2 == p_prime) and p1 != p and p2 != p
    #                     ]
    #                 )
    #     solver.Add(2 * y[(p, p_prime)] <= solver.Sum(_terms))

    # # y_r definition: y_r[p,p',r] can only be 1 if p and p' opposed on some court in round r.
    # # The note divides by C, but since a player can only be on one court per round the sum
    # # is at most 1, so the division is dropped to avoid incorrectly forcing y_r to zero.
    # for (p, p_prime) in player_pairs:
    #     for r in rounds:
    #         solver.Add(
    #             y_r[(p, p_prime, r)] <= solver.Sum([y_rc[(p, p_prime, r, c)] for c in courts])
    #         )

    # # y definition: y[p,p'] can only be 1 if p and p' opposed in at least one round
    # for (p, p_prime) in player_pairs:
    #     solver.Add(y[(p, p_prime)] <= solver.Sum([y_r[(p, p_prime, r)] for r in rounds]))

    # M and m definitions: M >= games played by any player, m <= games played by any player
    for p in players:
        _games = solver.Sum([
            x[(p1, p2, r, c)]
            for (p1, p2) in player_pairs
            for r in rounds
            for c in courts
            if p1 == p or p2 == p
        ])
        solver.Add(M >= _games)
        solver.Add(m <= _games)

    # w definition: w[p1,p2] can only be 1 if p1 and p2 partnered at least once
    for (p1, p2), w_var in w.items():
        solver.Add(w_var <= solver.Sum([
            x[(p1, p2, r, c)]
            for r in rounds
            for c in courts
        ]))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Objective
    """)
    return


@app.cell
def _(courts, player_pairs, preference_score, rounds, solver, x):
    # Objective 1: maximise partner preference scores.
    # Preferences are directional so both directions are summed for each unordered pair.
    obj_preference = solver.Sum([
        (preference_score.get((p1, p2), 0) + preference_score.get((p2, p1), 0))
        * x[(p1, p2, r, c)]
        for (p1, p2) in player_pairs
        for r in rounds
        for c in courts
    ])
    return (obj_preference,)


@app.cell
def _(solver, w):
    # # Objective 2: maximise variety of opponents across the session
    # obj_variety = 10 * solver.Sum([y[(p1, p2)] for (p1, p2) in player_pairs])

    # Objective 2: maximise partnership variety as a proxy for opponent variety
    obj_variety = 10 * solver.Sum(list(w.values()))
    return (obj_variety,)


@app.cell
def _(consec3, solver):
    # Objective 4: minimise occurrences of 3 consecutive games for any player
    obj_consecutive = -10 * solver.Sum(list(consec3.values()))
    return (obj_consecutive,)


@app.cell
def _(M, m, obj_consecutive, obj_preference, obj_variety, solver):
    # Objective 3: maximise equality of games played across permanent members
    obj_equality = -10 * (M - m)

    solver.Maximize(obj_preference + obj_variety + obj_equality + obj_consecutive)
    solver.SetTimeLimit(600_000)  # 2 minutes in milliseconds
    return


@app.cell
def _(solver):
    print("Number of variables =", solver.NumVariables())
    print("Number of constraints =", solver.NumConstraints())
    return


@app.cell
def _(mo, solver):
    _status_map = {
        0: ("OPTIMAL", "green"),
        1: ("FEASIBLE", "orange"),
        2: ("INFEASIBLE", "red"),
        3: ("UNBOUNDED", "red"),
        4: ("ABNORMAL", "red"),
        6: ("NOT_SOLVED", "gray"),
    }
    solve_status = solver.Solve()
    _label, _color = _status_map.get(solve_status, (f"UNKNOWN ({solve_status})", "red"))
    mo.callout(mo.md(f"Solver status: **{_label}**"), kind="success" if _color == "green" else "warn" if _color == "orange" else "danger" if _color == "red" else "info")
    return (solve_status,)


@app.cell
def _(courts, player_data, player_pairs, players, rounds, solve_status, x):
    _name = {p["user_id"]: p["name"] for p in player_data}
    _rows = []

    for _r in rounds:
        _court_teams = {}
        for _c in courts:
            _court_teams[_c] = [
                (_p1, _p2) for (_p1, _p2) in player_pairs
                if x[(_p1, _p2, _r, _c)].solution_value() > 0.5
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
