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

    return


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
    return


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
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
