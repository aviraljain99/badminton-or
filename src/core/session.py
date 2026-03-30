from session_config import player_data, TEAM_SIZE, MIN_GAMES, MAX_GAMES
from ortools.sat.python import cp_model

from core.entity import Player, SessionAllocation

class Session:
    def __init__(self, players: list[Player], courts: int, rounds: int):
        self.players = players
        self.total_players = len(self.players)
        self.courts = courts
        self.rounds = rounds
        self.model = cp_model.CpModel()
        self.variables = {}

    def __initialize_player_variables(self):
        """Initializes variables in the model recording players per round per court per team."""

        for p in range(self.total_players):
            for r in range(self.rounds):
                for c in range(self.courts):
                    for t in range(TEAM_SIZE):
                        self.variables[(p, r, c, t)] = self.model.new_int_var(0, 1, f"x_{p}_{r}_{c}_{t}")

    def __initialize_team_pair_variables(self):
        """Initializes variables in the model that holds when two players are together"""
        # Adds variables to represent when two PLAYERS play together
        for p1 in range(PLAYERS):
            for p2 in range(p1 + 1, PLAYERS):
                for r in range(ROUNDS):
                    for c in range(COURTS):
                        for t in range(TEAMS):
                            # Creates a variable to represent when two PLAYERS are in the same team
                            self.variables[(p1, p2, r, c, t)] = self.model.new_int_var(0, 1, f"x_{p1}x{p2}_{r}_{c}_{t}")

                            # These constraints ensure that the variable for two PLAYERS being on the same team is true 
                            # when they are on the same team and false when they are not
                            self.model.add((2 * self.variables[(p1, p2, r, c, t)]) < (self.variables[(p1, r, c, t)] + self.variables[(p2, r, c, t)] + 1))
                            self.model.add((2 * self.variables[(p1, p2, r, c, t)]) + 2 > (self.variables[(p1, r, c, t)] + self.variables[(p2, r, c, t)]))


    def __initialize_model(self):
        pass

    def generate_session_allocation(self) -> SessionAllocation:
        pass