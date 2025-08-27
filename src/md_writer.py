"""Writes the schedule to a markdown file"""
from ortools.sat.python.cp_model import CpSolver, IntVar

from session_config import player_data, COURTS, TEAMS

def get_table_headers() -> str:
    return "\n".join(["| Round | Court | Team-A | | Team-B | | Break |", "|-|-|-|-|-|-|-|"])

def get_empty_row() -> str:
    return "||||||||\n"

def get_players_in_team(round: int, court: int, team_id: int, variables: dict[tuple, IntVar], solver: CpSolver) -> list[str, str]:
    team = []
    for player_id, player_name in enumerate(player_data):
        if solver.value(variables[(player_id, round, court, team_id)]) == 1:
            team.append(player_name[0])
    return team

def get_players_on_break(round: int, variables: dict[tuple, IntVar], solver: CpSolver) -> list[str]:
    players_on_break = []
    for player_id, player_name in enumerate(player_data):
        if all(solver.value(variables[(player_id, round, court, team)]) == 0 for court in range(COURTS) for team in range(TEAMS)):
            players_on_break.append(player_name[0])
    return players_on_break

def get_games_in_round(round: int, solver: CpSolver, variables: dict[tuple, IntVar]) -> list[list[list[str]]]:
    games_in_round: list[list[list[str]]] = []
    for court in range(COURTS):
        teams_on_court = []
        for team in range(TEAMS):
            team_players = get_players_in_team(round, court, team, variables, solver)
            teams_on_court.append(team_players)
        games_in_round.append(teams_on_court)
    return games_in_round

def get_round_as_md(games_in_round: list[list[list[str]]], round: int, players_on_break: list[str]) -> str:
    md = ""
    players_on_break_chunks: list[str] = []
    chunk_size = len(players_on_break) // len(games_in_round)
    for i in range(0, len(games_in_round), max(chunk_size, 1)):
        players_on_break_chunks.append(", ".join(players_on_break[i:i + chunk_size]))

    for court_id, (teams, players_on_break) in enumerate(zip(games_in_round, players_on_break_chunks)):
        team_a, team_b = teams
        md += f"| {str(round + 1) if court_id == 0 else ""} | {court_id + 1} | {team_a[0]} | {team_a[1]} | {team_b[0]} | {team_b[1]} | {players_on_break} |\n"
    return md


