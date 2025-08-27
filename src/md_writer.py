"""Writes the schedule to a markdown file"""
from ortools.sat.python.cp_model import CpSolver, IntVar

from session_config import player_data, COURTS, TEAMS

def get_table_headers() -> str:
    return "\n".join(["| Round | Court | Team-A | Team-B |", "|-|-|-|-|"])

def get_players_in_team(round: int, court: int, team_id: int, variables: dict[tuple, IntVar], solver: CpSolver) -> list[str, str]:
    team = []
    for player_id, player_name in enumerate(player_data):
        if solver.value(variables[(player_id, round, court, team_id)]) == 1:
            team.append(player_name[0])
    return team

def get_games_in_round(round: int, solver: CpSolver, variables: dict[tuple, IntVar]) -> list[list[list[str]]]:
    games_in_round: list[list[list[str]]] = []
    for court in range(COURTS):
        teams_on_court = []
        for team in range(TEAMS):
            team_players = get_players_in_team(round, court, team, variables, solver)
            teams_on_court.append(team_players)
        games_in_round.append(teams_on_court)
    return games_in_round

def get_round_as_md(games_in_round: list[list[list[str]]], round: int) -> str:
    md = ""
    for court_id, teams in enumerate(games_in_round):
        team_a, team_b = teams
        md += f"| {str(round + 1) if court_id == 0 else ""} | {court_id + 1} | {team_a[0]} & {team_a[1]} | {team_b[0]} & {team_b[1]} |\n"
    return md


