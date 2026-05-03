from dataclasses import dataclass
import datetime

from core.entity import Team

@dataclass
class Game:
    number: int
    team1: Team
    team2: Team
    start_time: datetime.datetime
    end_time: datetime.datetime | None = None
    team1_score: int | None = None
    team2_score: int | None = None
    outcome: str = "in_progress"  # "finished", "abandoned", "in_progress"