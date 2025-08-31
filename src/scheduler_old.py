"""Simple solve."""
from ortools.sat.python import cp_model
import logging

from session_config import player_data, ROUNDS, COURTS, TEAMS, PLAYERS, MIN_GAMES, MAX_GAMES
from md_writer import get_table_headers, get_games_in_round, get_round_as_md, get_players_on_break, get_empty_row

logger = logging.getLogger(__name__)


model = cp_model.CpModel()

variables = {}
for p in range(PLAYERS):
    for r in range(ROUNDS):
        for c in range(COURTS):
            for t in range(TEAMS):
                variables[(p, r, c, t)] = model.new_int_var(0, 1, f"x_{p}_{r}_{c}_{t}")

###### Ensures that two players only play together at most once! ######

# Adds variables to represent when two PLAYERS play together
for p1 in range(PLAYERS):
    for p2 in range(p1 + 1, PLAYERS):
        for r in range(ROUNDS):
            for c in range(COURTS):
                for t in range(TEAMS):
                    # Creates a variable to represent when two PLAYERS are in the same team
                    variables[(p1, p2, r, c, t)] = model.new_int_var(0, 1, f"x_{p1}x{p2}_{r}_{c}_{t}")

                    # These constraints ensure that the variable for two PLAYERS being on the same team is true 
                    # when they are on the same team and false when they are not
                    model.add((2 * variables[(p1, p2, r, c, t)]) < (variables[(p1, r, c, t)] + variables[(p2, r, c, t)] + 1))
                    model.add((2 * variables[(p1, p2, r, c, t)]) + 2 > (variables[(p1, r, c, t)] + variables[(p2, r, c, t)]))

# Uses the team variables to enforce that two players only play at most once together
for p1 in range(PLAYERS):
    for p2 in range(p1 + 1, PLAYERS):
        model.add(sum(variables[(p1, p2, r, c, t)] for r in range(ROUNDS) for c in range(COURTS) for t in range(TEAMS)) <= 1)

# Add a constraint to enforce that an individual only gets at most 2 consecutive breaks
for p in range(PLAYERS):
    for r1 in range(ROUNDS - 2):
        model.add(sum(variables[(p, r2, c, t)] for c in range(COURTS) for t in range(TEAMS) for r2 in range(r1, r1 + 3)) >= 1)

# Add a constraint that an individual only gets at most 3 games in a row
for p in range(PLAYERS):
    for r1 in range(ROUNDS - 3):
        model.add(sum(variables[(p, r2, c, t)] for c in range(COURTS) for t in range(TEAMS) for r2 in range(r1, r1 + 4)) <= 3)

# Adds constraint such that every team will only have TWO players on a given court and a given round
for r in range(ROUNDS):
    for c in range(COURTS):
        for t in range(TEAMS):
            model.add(sum(variables[(p, r, c, t)] for p in range(PLAYERS)) == 2)

# Adds a constraint that, given a round and given a player, the player will have at most 1 allocation
for p in range(PLAYERS):
    for r in range(ROUNDS):
        model.add(sum(variables[(p, r, c, t)] for c in range(COURTS) for t in range(TEAMS)) <= 1)


# Adds a constraint that all PLAYERS get to play 7 times across all the rounds
for p in range(PLAYERS):

    model.add(sum(variables[(p, r, c, t)] for r in range(ROUNDS) for c in range(COURTS) for t in range(TEAMS)) >= MIN_GAMES)
    model.add(sum(variables[(p, r, c, t)] for r in range(ROUNDS) for c in range(COURTS) for t in range(TEAMS)) <= MAX_GAMES)

    for r in range(ROUNDS):
        # Adds a constraint that if this player is permanent, they will have had more games than players who are casual
        if player_data[p][1]:
            for p1 in range(PLAYERS):
                if not player_data[p1][1] and p != p1:
                    model.add(
                        sum(
                            variables[(p, r1, c, t)] for r1 in range(r + 1) for c in range(COURTS) for t in range(TEAMS)
                        ) >= 
                        sum(
                            variables[(p1, r1, c, t)] for r1 in range(r + 1) for c in range(COURTS) for t in range(TEAMS)
                        )
                    )


# Creates the solver and solves the model.
solver = cp_model.CpSolver()
status = solver.solve(model)

# Statistics.
print("\nStatistics")
print(f"  status   : {solver.status_name(status)}")
print(f"  conflicts: {solver.num_conflicts}")
print(f"  branches : {solver.num_branches}")
print(f"  wall time: {solver.wall_time} s")

if status == cp_model.OPTIMAL:
    print("Optimal solution found.")
elif status == cp_model.FEASIBLE:
    print("Feasible solution found, but not optimal.")

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print("Solved")

    # Prints the number of games played by each player across all rounds
    player_games = [0] * PLAYERS
    for p in range(PLAYERS):
        for r in range(ROUNDS):
            for c in range(COURTS):
                for t in range(TEAMS):
                    if solver.value(variables[(p, r, c, t)]) == 1:
                        player_games[p] += 1
    print("Games played by each player:", player_games)

    # Checks that in a given round, there are only 16 PLAYERS
    round_players = [0] * ROUNDS
    for r in range(ROUNDS):
        round_players[r] = sum(solver.value(variables[(p, r, c, t)]) for p in range(PLAYERS) for c in range(COURTS) for t in range(TEAMS))
    print(round_players)

    # Check that in a given round, a player only plays at most once
    for p in range(PLAYERS):
        for r in range(ROUNDS):
            if sum(solver.value(variables[(p, r, c, t)]) for c in range(COURTS) for t in range(TEAMS)) > 1:
                print(f"Player {p} plays more than once in round {r}")
    
    # Checks how many times two PLAYERS play together
    player_pairs = [[0] * PLAYERS for _ in range(PLAYERS)]
    for p1 in range(PLAYERS):
        for p2 in range(p1 + 1, PLAYERS):
            for r in range(ROUNDS):
                for c in range(COURTS):
                    for t in range(TEAMS):
                        if solver.value(variables[(p1, r, c, t)]) == 1 and solver.value(variables[(p2, r, c, t)]) == 1:
                            player_pairs[p1][p2] += 1
                            player_pairs[p2][p1] += 1
                            if player_pairs[p1][p2] > 2:
                                print(f"Players {p1} and {p2} play together more than twice")

    import pprint
    pprint.pprint(player_pairs)

    rounds_in_session = []
    for r in range(ROUNDS):
        games_in_round: list[list[list[str]]] = get_games_in_round(r, solver, variables)
        rounds_in_session.append(games_in_round)
    
    with open("test_schedule.md", "w") as f:
        f.write("# Badminton Schedule\n\n")
        f.write("## Schedule\n\n")
        f.write(get_table_headers() + "\n")
        for round_id, games_in_round in enumerate(rounds_in_session):
            f.write(get_round_as_md(games_in_round, round_id, get_players_on_break(round_id, variables, solver)))
            f.write(get_empty_row())
        f.write("\n")
    