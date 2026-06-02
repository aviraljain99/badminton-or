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
        {"user_id": "aviral", "name": "Aviral", "member": True},
        {"user_id": "jack", "name": "Jack", "member": True},
        {"user_id": "rahul", "name": "Rahul", "member": True},
        {"user_id": "ragesh", "name": "Ragesh", "member": True},
        {"user_id": "ulf", "name": "Ulf", "member": True},
        {"user_id": "andy", "name": "Andy", "member": True},
        {"user_id": "suandi", "name": "Suandi", "member": True},
        {"user_id": "harry", "name": "Harry", "member": True},
        {"user_id": "anoop", "name": "Anoop", "member": True},
        {"user_id": "sumit", "name": "Sumit", "member": True},
        {"user_id": "yaw", "name": "Yaw", "member": True},
        {"user_id": "sachi", "name": "Sachi", "member": True},
        {"user_id": "annie_george", "name": "Annie George", "member": True},
        {"user_id": "shahar", "name": "Shahar", "member": False},
        {"user_id": "nithin", "name": "Nithin", "member": False},
        {"user_id": "james", "name": "James Pawathu", "member": False}
    ]

    ROUNDS = 9
    COURTS = 3
    N_PLAYERS = len(player_data)
    return COURTS, ROUNDS, player_data


@app.cell
def _(player_data, player_preferences):
    def _compute_score(p, p_prime):
        if p not in player_preferences:
            return 0
        pair_up = {player: rank for player, rank in player_preferences[p]["pair_up_preference"]}
        l_p = len(pair_up)
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
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Variables
    """)
    return


@app.cell
def _(COURTS, ROUNDS, player_data, pywraplp):
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

    # y_rc[p1, p2, r, c]: p1 and p2 opposed each other on court c in round r
    y_rc = {
        (p1, p2, r, c): solver.BoolVar(f'y_rc_{p1}_{p2}_{r}_{c}')
        for (p1, p2) in player_pairs
        for r in rounds
        for c in courts
    }

    # y_r[p1, p2, r]: p1 and p2 opposed each other in round r
    y_r = {
        (p1, p2, r): solver.BoolVar(f'y_r_{p1}_{p2}_{r}')
        for (p1, p2) in player_pairs
        for r in rounds
    }

    # y[p1, p2]: p1 and p2 opposed each other at any point in the session
    y = {
        (p1, p2): solver.BoolVar(f'y_{p1}_{p2}')
        for (p1, p2) in player_pairs
    }

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
    return


if __name__ == "__main__":
    app.run()
