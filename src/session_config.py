ROUNDS = 9
COURTS = 4
TEAMS = 2

MIN_GAMES = 6
MAX_GAMES = MIN_GAMES + 1

player_data: list[tuple[str, bool]] = [
    ("Thenes", True),
    ("Sandy", True),
    ("Hridaan", True),
    ("Habby", True),
    ("Pritto", True),
    ("Aviral", True),
    ("Chan", True),
    ("Akhil Srikanth", True),
    ("Akhil Appukutam", True),
    ("Naresh", True),
    ("Anto", True),
    ("Jack", True),
    ("Yaw", True),
    ("Sumit", True),
    ("Anoop", True),
    ("Andy S", True),
    ("Andi H", True),
    ("Ragesh", True),
    ("Harry P", False),
    ("Annie George", False),
    ("Ravi", False),
    ("Sachi", False)
]

PLAYERS = len(player_data)