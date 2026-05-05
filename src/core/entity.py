"""Represents entities in a session"""

import datetime
from typing import Optional, TypedDict
from dataclasses import dataclass

@dataclass
class Player:
    player_id: str
    name: str
    member: Optional[bool] = None

@dataclass
class Team:
    player_1: Player
    player_2: Player


@dataclass
class Session:
    session_id: str
    session_date: str
    status: str = "finished"
    start_time: Optional[datetime.datetime] = None
    end_time: Optional[datetime.datetime] = None
    location: Optional[str] = None
    courts: Optional[int] = None
    shuttles_used: Optional[int] = None


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
