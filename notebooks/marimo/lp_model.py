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
        "sandy" : {
            "pair_up_preference" : [
                ("rahul", 1), 
                ("habby", 2), 
                ("sumit", 3),
                ("annie_george", 4),
                ("thenes", 5),
                ("barrie", 6),
                ("kelvin", 7),
                ("aviral", 8)
            ],
            "avoid" : ["pritto", "akhil_srikanth", "yaw", "shahar", "faisal"]
        },
        "thenes" : {
            "pair_up_preference" : [
                ("barrie", 1),
                ("sumit", 2),
                ("kelvin", 3),
                ("sandy", 4),
                ("rahul", 5),
                ("aviral", 6)
            ],
            "avoid" : ["pritto", "akhil_srikanth", "yaw"]
        }
    }
    return (player_preferences,)


@app.cell
def _():
    player_data = [
        {"user_id": "thenes", "name": "Thenes", "member": True},
        {"user_id": "sandy", "name": "Sandy", "member": True},
        {"user_id": "habby", "name": "Habby", "member": True},
        {"user_id": "pritto", "name": "Pritto", "member": True},
        {"user_id": "aviral", "name": "Aviral", "member": True},
        {"user_id": "chan", "name": "Chan", "member": True},
        {"user_id": "akhil_srikanth", "name": "Akhil Srikanth", "member": True},
        {"user_id": "naresh", "name": "Naresh", "member": True},
        {"user_id": "jack", "name": "Jack", "member": True},
        {"user_id": "yaw", "name": "Yaw", "member": True},
        {"user_id": "sumit", "name": "Sumit", "member": True},
        {"user_id": "anoop", "name": "Anoop", "member": True},
        {"user_id": "andy", "name": "Andy S", "member": True},
        {"user_id": "suandi", "name": "Suandi Halim", "member": True},
        {"user_id": "ragesh", "name": "Ragesh", "member": True},
        {"user_id": "harry", "name": "Harry P", "member": True},
        {"user_id": "annie_george", "name": "Annie George", "member": True},
        {"user_id": "sachi", "name": "Sachi", "member": True},
        {"user_id": "rahul", "name": "Rahul", "member": True},
        {"user_id": "shahar", "name": "Shahar", "member": False},
        {"user_id": "faisal", "name": "Faisal", "member": False},
        {"user_id": "kelvin", "name": "Kelvin", "member": True},
        {"user_id": "barrie", "name": "Barrie", "member": True}
    ]

    ROUNDS = 9
    COURTS = 4
    TEAM_SIZE = 2
    N_PLAYERS = len(player_data)
    return COURTS, N_PLAYERS, ROUNDS, player_data


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Model & Variables
    """)
    return


@app.cell
def _(pywraplp):
    solver = pywraplp.Solver.CreateSolver("SCIP")
    return (solver,)


@app.cell
def _(COURTS, N_PLAYERS, ROUNDS, player_data, solver):
    # x[p1, p2, r, c] = 1 if players p1 and p2 are teammates on court c in round r
    # Only defined for p1 < p2 to avoid redundancy
    x = {}
    for _p1 in range(N_PLAYERS):
        for _p2 in range(_p1 + 1, N_PLAYERS):
            for _r in range(ROUNDS):
                for _c in range(COURTS):
                    x[_p1, _p2, _r, _c] = solver.IntVar(
                        0, 1,
                        f"x_{player_data[_p1]['name']}_{player_data[_p2]['name']}_r{_r}_c{_c}"
                    )

    # plays[p, r, c] = 1 if player p is on court c in round r (regardless of team)
    # Auxiliary variable — will be linked to x via constraints
    plays = {}
    for _p in range(N_PLAYERS):
        for _r in range(ROUNDS):
            for _c in range(COURTS):
                plays[_p, _r, _c] = solver.IntVar(
                    0, 1,
                    f"plays_{player_data[_p]['name']}_r{_r}_c{_c}"
                )
    return plays, x


@app.cell
def _(COURTS, N_PLAYERS, ROUNDS, mo, plays, x):
    n_x = len(x)
    n_plays = len(plays)
    mo.md(f"""
    ### Variables created

    | Variable | Shape | Count |
    |---|---|---|
    | `x[p1, p2, r, c]` | C({N_PLAYERS},2) × {ROUNDS} × {COURTS} | {n_x} |
    | `plays[p, r, c]` | {N_PLAYERS} × {ROUNDS} × {COURTS} | {n_plays} |
    | **Total** | | **{n_x + n_plays}** |
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Constraints
    """)
    return


@app.cell
def _(COURTS, N_PLAYERS, ROUNDS, player_data, player_preferences, plays, solver, x):
    # Build user_id -> player index lookup
    uid_to_idx = {p["user_id"]: i for i, p in enumerate(player_data)}

    # 1. Avoid constraints: zero out x for any avoided pairing
    for _uid, _prefs in player_preferences.items():
        if _uid not in uid_to_idx:
            continue
        _p = uid_to_idx[_uid]
        for _avoided in _prefs.get("avoid", []):
            if _avoided not in uid_to_idx:
                continue
            _q = uid_to_idx[_avoided]
            _p1, _p2 = (_p, _q) if _p < _q else (_q, _p)
            for _r in range(ROUNDS):
                for _c in range(COURTS):
                    solver.Add(x[_p1, _p2, _r, _c] == 0)

    # 2. Exactly 2 teammate pairs per court per round (2 teams of 2 = 4 players)
    for _r in range(ROUNDS):
        for _c in range(COURTS):
            solver.Add(
                solver.Sum([
                    x[_p1, _p2, _r, _c]
                    for _p1 in range(N_PLAYERS)
                    for _p2 in range(_p1 + 1, N_PLAYERS)
                ]) == 2
            )

    # 3. Link plays[p, r, c] to x: player p is on court c in round r iff they have a teammate there
    for _p in range(N_PLAYERS):
        for _r in range(ROUNDS):
            for _c in range(COURTS):
                _teammates = (
                    [x[_p, _p2, _r, _c] for _p2 in range(_p + 1, N_PLAYERS)] +
                    [x[_p1, _p, _r, _c] for _p1 in range(_p)]
                )
                solver.Add(plays[_p, _r, _c] == solver.Sum(_teammates))

    # 4. Each player is on at most one court per round
    for _p in range(N_PLAYERS):
        for _r in range(ROUNDS):
            solver.Add(
                solver.Sum([plays[_p, _r, _c] for _c in range(COURTS)]) <= 1
            )

    return


if __name__ == "__main__":
    app.run()
