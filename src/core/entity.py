"""Represents entities in a session"""
from typing import TypedDict

class Player(TypedDict):
    name: str
    member: bool


class Team(TypedDict):
    player_1: Player
    player_2: Player


class SessionAllocation:
    def __init__(self):
        pass
        # { 
        #   round_id : 
        #       { 
        #           court_id : { team_1 : [player_id, player_id], team_2 : [player_id, player_id] } 
        #       } 
        # }


    def add_teams_to_court_in_round(self, court_id: int, round_int: int) -> None:
        pass