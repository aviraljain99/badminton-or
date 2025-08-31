"""Holds classes for session and session solving."""

from ortools.sat.python import cp_model

class Session:
    """Holds session configuration."""
    def __init__(self, players: list[str], rounds: int, courts: int, teams: int, min_games: int, max_games: int):
        self.players = players
        self.rounds = rounds
        self.courts = courts
        self.teams = teams

        self.min_games = min_games
        self.max_games = max_games


class SessionSolver:
    """Creates and solves a session scheduling model."""
    def __init__(self, session: Session):
        self.session = session

        self.variables = {}
        self.model = None

    def __create_player_variables(self):
        """Creates variables for each player, round, court, and team."""
        for player_id, _ in enumerate(self.session.players):
            for round_id in range(self.session.rounds):
                for court_id in range(self.session.courts):
                    for team_id in range(self.session.teams):
                        self.variables[
                            (player_id, round_id, court_id, team_id)
                        ] = self.model.new_int_var(
                            0, 1, f"x_{player_id}_{round_id}_{court_id}_{team_id}"
                        )


    def __add_consecutive_break_constraints(self):
        """Adds constraints to ensure no player has more than 2 consecutive breaks."""
        for player_id, _ in enumerate(self.session.players):
            for window_start in range(self.session.rounds - 2):
                self.model.add(
                    sum(
                        self.variables[(player_id, round_id, court_id, team_id)]
                        for court_id in range(self.session.courts)
                        for team_id in range(self.session.teams)
                        for round_id in range(window_start, window_start + 3)
                    ) >= 1
                )

    def __add_max_consecutive_games_constraints(self):
        """Adds constraints to ensure no player has more than 3 consecutive games."""
        for player_id, _ in enumerate(self.session.players):
            for window_start in range(self.session.rounds - 3):
                self.model.add(
                    sum(
                        self.variables[(player_id, round_id, court_id, team_id)]
                        for court_id in range(self.session.courts)
                        for team_id in range(self.session.teams)
                        for round_id in range(window_start, window_start + 4)
                    ) <= 3
                )

    def __add_basic_constraints(self):
        """Adds basic constraints to the model."""
        # Adds constraint such that every team will only have TWO players on a given court and a given round
        for round_id in range(self.session.rounds):
            for court_id in range(self.session.courts):
                for team_id in range(self.session.teams):
                    self.model.add(
                        sum(
                            self.variables[(player_id, round_id, court_id, team_id)]
                            for player_id in range(len(self.session.players))) == 2
                        )

        
        # Adds a constraint that, given a round and given a player, the player will have at most 1 allocation
        for player_id in range(len(self.session.players)):
            for round_id in range(self.session.rounds):
                self.model.add(
                    sum(
                        self.variables[(player_id, round_id, court_id, team_id)]
                        for court_id in range(self.session.courts)
                        for team_id in range(self.session.teams)
                    ) <= 1
                )
        
    def __add_game_count_constraints(self):
        """Adds constraints to ensure each player plays within the min and max game limits."""
        for player_id in range(len(self.session.players)):
            self.model.add(
                sum(
                    self.variables[(player_id, round_id, court_id, team_id)]
                    for round_id in range(self.session.rounds)
                    for court_id in range(self.session.courts)
                    for team_id in range(self.session.teams)
                ) >= self.session.min_games
            )
            self.model.add(
                sum(
                    self.variables[(player_id, round_id, court_id, team_id)]
                    for round_id in range(self.session.rounds)
                    for court_id in range(self.session.courts)
                    for team_id in range(self.session.teams)
                ) <= self.session.max_games
            )
        
    def __add_casual_permanent_constraints(self):
        """Adds constraints to ensure permanent players get more games than casual players."""
        for player_id, is_permanent in enumerate(self.session.players):
            if is_permanent:
                for other_player_id, is_other_permanent in enumerate(self.session.players):
                    if not is_other_permanent and player_id != other_player_id:
                        for round_id in range(self.session.rounds):
                            self.model.add(
                                sum(
                                    self.variables[(player_id, r, c, t)]
                                    for r in range(round_id + 1)
                                    for c in range(self.session.courts)
                                    for t in range(self.session.teams)
                                ) >=
                                sum(
                                    self.variables[(other_player_id, r, c, t)]
                                    for r in range(round_id + 1)
                                    for c in range(self.session.courts)
                                    for t in range(self.session.teams)
                                )
                            )


    def create_model(self):
        """Creates the CP-SAT model for the session."""
        self.model = cp_model.CpModel()

        self.__create_player_variables()
        self.__add_consecutive_break_constraints()
        self.__add_max_consecutive_games_constraints()
        self.__add_basic_constraints()
        self.__add_game_count_constraints()
        # self.__add_casual_permanent_constraints()


    