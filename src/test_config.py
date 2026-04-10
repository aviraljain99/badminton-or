from core.entity import Player

ROUNDS = 9
COURTS = 4
TEAM_SIZE = 2

MIN_GAMES = 6
MAX_GAMES = MIN_GAMES + 1

player_data: list[Player] = [
    {"name": "Thenes", "member": True},
    {"name": "Sandy", "member": True},
    {"name": "Hridaan", "member": True},
    {"name": "Habby", "member": True},
    {"name": "Pritto", "member": True},
    {"name": "Aviral", "member": True},
    {"name": "Chan", "member": True},
    {"name": "Akhil Srikanth", "member": True},
    {"name": "Akhil Appukutam", "member": True},
    {"name": "Naresh", "member": True},
    {"name": "Anto", "member": True},
    {"name": "Jack", "member": True},
    {"name": "Yaw", "member": True},
    {"name": "Sumit", "member": True},
    {"name": "Anoop", "member": True},
    {"name": "Andy S", "member": True},
    {"name": "Andi H", "member": True},
    {"name": "Ragesh", "member": True},
    {"name": "Harry P", "member": False},
    {"name": "Annie George", "member": False},
    {"name": "Ravi", "member": False},
    {"name": "Sachi", "member": False}
]

PLAYERS = len(player_data)