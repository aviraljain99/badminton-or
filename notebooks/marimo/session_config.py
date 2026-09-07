ROUNDS = 10
COURTS = 3

PLAYER_DATA = [
    {"user_id": "thenes",  "name": "Thenes",  "member": True, "level": 5},
    {"user_id": "jack",    "name": "Jack",    "member": True, "level": 5},
    {"user_id": "andy",    "name": "Andy",    "member": True, "level": 5},
    {"user_id": "sandy",   "name": "Sandy",   "member": True, "level": 5},
    {"user_id": "suandi",  "name": "Suandi",  "member": True, "level": 5},
    {"user_id": "anoop",   "name": "Anoop",   "member": True, "level": 3},
    {"user_id": "lesley",  "name": "Lesley",  "member": True, "level": 2},
    {"user_id": "naresh",  "name": "Naresh",  "member": True, "level": 4},
    {"user_id": "yaw",     "name": "Yaw",     "member": True, "level": 4},
    {"user_id": "pritto",  "name": "Pritto",  "member": True, "level": 3},
    {"user_id": "sachee",  "name": "Sachee",  "member": True, "level": 3},
    {"user_id": "annie",   "name": "Annie",   "member": True, "level": 4},
    # casuals
    {"user_id": "hridaan", "name": "Hridaan", "member": True, "level": 5},
    {"user_id": "shebin",  "name": "Shebin",  "member": True, "level": 3},
    {"user_id": "nithin",  "name": "Nithin",  "member": True, "level": 4},
    {"user_id": "shahar",  "name": "Shahar",  "member": True, "level": 4},
]

PLAYER_PREFERENCES = {
    "sandy": {
        "pair_up_preference": [
            ("annie", 1),
            ("jack", 2),
            ("thenes", 3),
            ("nithin", 4),
        ],
        "avoid": ["akhil_srikanth", "lesley", "yaw", "anoop", "naresh", "andy"],
    },
    "thenes": {
        "pair_up_preference": [
            ("sumit", 1),
            ("naresh", 2),
            ("lesley", 3),
            ("nithin", 4),
        ],
        "avoid": ["andy"],
    },
    "suandi": {
        "pair_up_preference": [
            ("andy", 1),
            ("lesley", 2),
            ("rahul", 3),
        ],
        "avoid": [],
        "ok_with_consecutive_games": True,
    },
    "andy": {
        "pair_up_preference": [],
        "avoid": [],
        "ok_with_consecutive_games": True,
    },
    # "habby": {
    #     "pair_up_preference": [
    #         ("sumit", 1),
    #         ("thenes", 2),
    #         ("harry", 3),
    #     ],
    #     "avoid": ["shahar", "raheel", "ulf", "wilson"],
    # },
    "naresh": {
        "pair_up_preference": [
            ("saket", 1),
            ("sumit", 2),
            ("sachee", 3),
            ("andy", 4),
        ],
        "avoid": ["sandy"],
    },
    "jack": {
        "pair_up_preference": [
            ("hridaan", 1),
            ("sandy", 2),
            ("annie", 3),
        ],
        "avoid": ["andy", "sachee", "logesh"],
    },
    "barrie": {
        "pair_up_preference": [
            ("kelvin", 1),
            ("john", 2),
            ("thenes", 3),
        ],
        "avoid": ["anoop", "pritto", "logesh"],
    },
    "kelvin": {
        "pair_up_preference": [
            ("barrie", 1),
            ("suandi", 2),
            ("hridaan", 3),
        ],
        "avoid": ["anoop", "pritto", "logesh"],
    },
    "pritto": {
        "pair_up_preference": [
            ("nithin", 1),
        ],
        "avoid": ["thenes", "sandy"],
    },
    "hridaan": {
        "pair_up_preference": [
            ("jack", 1),
            ("annie", 2),
            ("sandy", 3),
            ("suandi", 4),
        ],
        "avoid": [],
    },
}

# Per-round availability rules. Round numbers are 1-indexed (Round 1 == first round).
# Supported keys per player:
#   must_play         list[int]  rounds the player must be scheduled to play
#   must_not_play     list[int]  rounds the player must sit out
#   unavailable_from  int        player is absent from this round onward (inclusive)
#   available_from    int        player is absent before this round (arrives late)
PLAYER_ALLOCATIONS = {
    "andy": {"must_play": [1]},
    "suandi": {"must_play": [1]},
    "pritto": {"unavailable_from": 7},
    "lesley": {"must_not_play": [1]},
}
