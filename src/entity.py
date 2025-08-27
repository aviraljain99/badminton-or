"""Represents entities in a session"""

class Player:
    def __init__(self, name: str, member: bool):
        self.name = name
        self.member = member

class Session:
    def __init__(self, players: Player, courts: int):
        pass