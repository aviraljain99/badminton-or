"""Represents entities in a session"""
from typing import TypedDict
from ortools.sat.python import cp_model
from session_config import player_data, ROUNDS, COURTS, TEAMS, PLAYERS, MIN_GAMES, MAX_GAMES

class Player(TypedDict):
    name: str
    member: bool


class Team(TypedDict):
    player_1: Player
    player_2: Player


class SessionAllocation:
    def __init__(self):
        pass

    def add_teams_to_courts(self, round: int) -> None:
        pass