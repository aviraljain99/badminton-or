"""Represents a player in a badminton session."""

class Player:
    """Represents a player in a badminton session."""
    def __init__(self, name: str, is_permanent: bool):
        self.name = name
        self.is_permanent = is_permanent
    
    def __repr__(self) -> str:
        return f"Player(name={self.name}, is_permanent={self.is_permanent})"