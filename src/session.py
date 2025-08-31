"""Holds classes for session and session solving."""

from ortools.sat.python import cp_model
from player import Player

class Session:
    """Holds session configuration."""
    def __init__(self, players: list[Player], rounds: int, courts: int, teams: int, min_games: int, max_games: int):
        self.players = players
        self.rounds = rounds
        self.courts = courts
        self.teams = teams

        self.min_games = min_games
        self.max_games = max_games

class Schedule:
    """Holds the schedule for a session."""
    def __init__(self, session: Session, solver: cp_model.CpSolver, variables: dict[tuple, cp_model.IntVar]):
        self.session = session
        self.solver = solver
        self.variables = variables
    

class Scheduler:
    """ Schedules a badminton session using CP-SAT."""

    @staticmethod
    def generate_schedule_for_session(session: Session) -> Schedule:
        """Creates the CP-SAT model for the session."""
        model = cp_model.CpModel()
        variables: dict[tuple, cp_model.IntVar] = {}

        Scheduler.__create_player_variables(session, model, variables)
        Scheduler.__add_consecutive_break_constraints(session, model, variables)
        Scheduler.__add_max_consecutive_games_constraints(session, model, variables)
        Scheduler.__add_basic_constraints(session, model, variables)
        Scheduler.__add_game_count_constraints(session, model, variables)
        Scheduler.__add_casual_permanent_constraints(session, model, variables)

    @staticmethod
    def __create_player_variables(session: Session, model: cp_model.CpModel, variables: dict[tuple, cp_model.IntVar]) -> None:
        """Creates variables for each player, round, court, and team."""
        for player_id, _ in enumerate(session.players):
            for round_id in range(session.rounds):
                for court_id in range(session.courts):
                    for team_id in range(session.teams):
                        variables[
                            (player_id, round_id, court_id, team_id)
                        ] = model.new_int_var(
                            0, 1, f"x_{player_id}_{round_id}_{court_id}_{team_id}"
                        )

    @staticmethod
    def __add_consecutive_break_constraints(session: Session, model: cp_model.CpModel, variables: dict[tuple, cp_model.IntVar]):
        """Adds constraints to ensure no player has more than 2 consecutive breaks."""
        for player_id, _ in enumerate(session.players):
            for window_start in range(session.rounds - 2):
                model.add(
                    sum(
                        variables[(player_id, round_id, court_id, team_id)]
                        for court_id in range(session.courts)
                        for team_id in range(session.teams)
                        for round_id in range(window_start, window_start + 3)
                    ) >= 1
                )

    @staticmethod
    def __add_max_consecutive_games_constraints(session: Session, model: cp_model.CpModel, variables: dict[tuple, cp_model.IntVar]):
        """Adds constraints to ensure no player has more than 3 consecutive games."""
        for player_id, _ in enumerate(session.players):
            for window_start in range(session.rounds - 3):
                model.add(
                    sum(
                        variables[(player_id, round_id, court_id, team_id)]
                        for court_id in range(session.courts)
                        for team_id in range(session.teams)
                        for round_id in range(window_start, window_start + 4)
                    ) <= 3
                )

    @staticmethod
    def __add_basic_constraints(session: Session, model: cp_model.CpModel, variables: dict[tuple, cp_model.IntVar]):
        """Adds basic constraints to the model."""
        # Adds constraint such that every team will only have TWO players on a given court and a given round
        for round_id in range(session.rounds):
            for court_id in range(session.courts):
                for team_id in range(session.teams):
                    model.add(
                        sum(
                            variables[(player_id, round_id, court_id, team_id)]
                            for player_id in range(len(session.players))) == 2
                        )

        
        # Adds a constraint that, given a round and given a player, the player will have at most 1 allocation
        for player_id in range(len(session.players)):
            for round_id in range(session.rounds):
                model.add(
                    sum(
                        variables[(player_id, round_id, court_id, team_id)]
                        for court_id in range(session.courts)
                        for team_id in range(session.teams)
                    ) <= 1
                )

    @staticmethod
    def __add_game_count_constraints(session: Session, model: cp_model.CpModel, variables: dict[tuple, cp_model.IntVar]):
        """Adds constraints to ensure each player plays within the min and max game limits."""
        for player_id in range(len(session.players)):
            model.add(
                sum(
                    variables[(player_id, round_id, court_id, team_id)]
                    for round_id in range(session.rounds)
                    for court_id in range(session.courts)
                    for team_id in range(session.teams)
                ) >= session.min_games
            )
            model.add(
                sum(
                    variables[(player_id, round_id, court_id, team_id)]
                    for round_id in range(session.rounds)
                    for court_id in range(session.courts)
                    for team_id in range(session.teams)
                ) <= session.max_games
            )

    @staticmethod        
    def __add_casual_permanent_constraints(session: Session, model: cp_model.CpModel, variables: dict[tuple, cp_model.IntVar]):
        """Adds constraints to ensure permanent players get more games than casual players."""
        for player_id, player in enumerate(session.players):
            if player.is_permanent:
                for other_player_id, other_player in enumerate(session.players):
                    if not other_player.is_permanent and player_id != other_player_id:
                        for round_id in range(session.rounds):
                            model.add(
                                sum(
                                    variables[(player_id, r, c, t)]
                                    for r in range(round_id + 1)
                                    for c in range(session.courts)
                                    for t in range(session.teams)
                                ) >=
                                sum(
                                    variables[(other_player_id, r, c, t)]
                                    for r in range(round_id + 1)
                                    for c in range(session.courts)
                                    for t in range(session.teams)
                                )
                            )


    @staticmethod
    def __add_maximum_pair_ups_constraints(session: Session, model: cp_model.CpModel, variables: dict[tuple, cp_model.IntVar]):
        """Adds constraints to ensure no two players are paired up more than twice."""
        pass
    


    