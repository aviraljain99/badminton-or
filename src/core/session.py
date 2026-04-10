from test_config import TEAM_SIZE
from ortools.sat.python import cp_model
from ortools.sat.cp_model_pb2 import CpSolverStatus

from core.entity import Player

class Session:
    def __init__(self, players: list[Player], courts: int, rounds: int, min_games: int, max_games: int):
        self.players = players
        self.TOTAL_PLAYERS = len(self.players)
        self.COURTS = courts
        self.ROUNDS = rounds

        self.min_games = min_games
        self.max_games = max_games

        # Model variables
        self.model = cp_model.CpModel()
        self.variables = {}

    def initialize_model(self):
        # Initialize all variables
        self.__initialize_player_variables()
        self.__initialize_team_pair_variables()

        # base constraints (could go into a super class)
        self.__game_rule_constraints()

        # mixing constraints
        self.__players_play_together_once_constraint()
        
        # Constraints about how often a person will get breaks
        self.__player_gets_max_two_consecutive_breaks()
        self.__player_gets_max_three_consecutive_games()

        # custom constraints
        self.__min_max_games_constraint()
        self.__permanents_play_more_than_casuals()

    def solve_session(self) -> tuple[CpSolverStatus, cp_model.CpSolver]:
        # Creates the solver and solves the model.
        solver = cp_model.CpSolver()
        status = solver.solve(self.model)

        return status, solver


    def __initialize_player_variables(self):
        """Initializes variables in the model recording players per round per court per team."""
        for p in range(self.TOTAL_PLAYERS):
            for r in range(self.ROUNDS):
                for c in range(self.COURTS):
                    for t in range(TEAM_SIZE):
                        self.variables[(p, r, c, t)] = self.model.new_int_var(0, 1, f"x_{p}_{r}_{c}_{t}")

    def __initialize_team_pair_variables(self):
        """Initializes variables in the model that holds when two players are together"""
        # Adds variables to represent when two PLAYERS play together
        for p1 in range(self.TOTAL_PLAYERS):
            for p2 in range(p1 + 1, self.TOTAL_PLAYERS):
                for r in range(self.ROUNDS):
                    for c in range(self.COURTS):
                        for t in range(TEAM_SIZE):
                            # Creates a variable to represent when two PLAYERS are in the same team
                            self.variables[(p1, p2, r, c, t)] = self.model.new_int_var(0, 1, f"x_{p1}x{p2}_{r}_{c}_{t}")

                            # These constraints ensure that the variable for two PLAYERS being on the same team is true 
                            # when they are on the same team and false when they are not
                            self.model.add((2 * self.variables[(p1, p2, r, c, t)]) < (self.variables[(p1, r, c, t)] + self.variables[(p2, r, c, t)] + 1))
                            self.model.add((2 * self.variables[(p1, p2, r, c, t)]) + 2 > (self.variables[(p1, r, c, t)] + self.variables[(p2, r, c, t)]))

    def __players_play_together_once_constraint(self):
        # Uses the team variables to enforce that two players only play at most once together
        for p1 in range(self.TOTAL_PLAYERS):
            for p2 in range(p1 + 1, self.TOTAL_PLAYERS):
                self.model.add(sum(self.variables[(p1, p2, r, c, t)] for r in range(self.ROUNDS) for c in range(self.COURTS) for t in range(TEAM_SIZE)) <= 1)

    def __player_gets_max_two_consecutive_breaks(self):
        # Add a constraint to enforce that an individual only gets at most 2 consecutive breaks
        for p in range(self.TOTAL_PLAYERS):
            for r1 in range(self.ROUNDS - 2):
                self.model.add(sum(self.variables[(p, r2, c, t)] for c in range(self.COURTS) for t in range(TEAM_SIZE) for r2 in range(r1, r1 + 3)) >= 1)

    def __player_gets_max_three_consecutive_games(self):
        # Add a constraint that an individual only gets at most 3 games in a row
        for p in range(self.TOTAL_PLAYERS):
            for r1 in range(self.ROUNDS - 3):
                self.model.add(sum(self.variables[(p, r2, c, t)] for c in range(self.COURTS) for t in range(TEAM_SIZE) for r2 in range(r1, r1 + 4)) <= 3)

    def __game_rule_constraints(self):
        # Adds constraint such that every team will only have TWO players on a given court and a given round
        for r in range(self.ROUNDS):
            for c in range(self.COURTS):
                for t in range(TEAM_SIZE):
                    self.model.add(sum(self.variables[(p, r, c, t)] for p in range(self.TOTAL_PLAYERS)) == TEAM_SIZE)

        # Adds a constraint that, given a round and given a player, the player will have at most 1 allocation
        for p in range(self.TOTAL_PLAYERS):
            for r in range(self.ROUNDS):
                self.model.add(sum(self.variables[(p, r, c, t)] for c in range(self.COURTS) for t in range(TEAM_SIZE)) <= 1)

    def __min_max_games_constraint(self):
        # Adds a constraint that all PLAYERS get to play 7 times across all the rounds
        for p in range(self.TOTAL_PLAYERS):
            self.model.add(sum(self.variables[(p, r, c, t)] for r in range(self.ROUNDS) for c in range(self.COURTS) for t in range(TEAM_SIZE)) >= self.min_games)
            self.model.add(sum(self.variables[(p, r, c, t)] for r in range(self.ROUNDS) for c in range(self.COURTS) for t in range(TEAM_SIZE)) <= self.max_games)

    def __permanents_play_more_than_casuals(self):
        for p in range(self.TOTAL_PLAYERS):
            for r in range(self.ROUNDS):
                # Adds a constraint that if this player is permanent, they will have had more games than players who are casual
                if player_data[p]["member"]:
                    for p1 in range(self.TOTAL_PLAYERS):
                        if not player_data[p1]["member"] and p != p1:
                            self.model.add(
                                sum(
                                    self.variables[(p, r1, c, t)] for r1 in range(r + 1) for c in range(self.COURTS) for t in range(TEAM_SIZE)
                                ) >= 
                                sum(
                                    self.variables[(p1, r1, c, t)] for r1 in range(r + 1) for c in range(self.COURTS) for t in range(TEAM_SIZE)
                                )
                            )


    # def generate_session_allocation(self) -> SessionAllocation:
    #     pass