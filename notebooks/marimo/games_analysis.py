import marimo

__generated_with = "0.23.2"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    mo.Html(
        """
        <style>
        .cm-content, .cm-line {
            white-space: pre !important;
            word-wrap: normal !important;
        }
        .cm-scroller {
            overflow-x: auto !important;
        }
        </style>
        """
    )
    return (mo,)


@app.cell
def _():
    import pandas as pd

    return (pd,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Loading wins and losses
    """)
    return


@app.cell
def _(pd):
    player_names = set()
    players_data = pd.DataFrame(columns=['player_id', 'Player Name', 'Member'])
    return


@app.cell
def _():
    games_dicts = []
    with open('../data/superbadder/20260421/games.txt', 'r') as _f:
        for _line in _f:
            if '-' in _line:
                team1, team2 = _line.strip().split('-')
                team1_players_and_score = team1.strip().split(' and ')
                team1_score = team1_players_and_score[-1].split()[-1].strip()
                team1_player1 = team1_players_and_score[0]
                team1_player2 = ' '.join(team1_players_and_score[-1].split()[0:-1])


                team2_players_and_score = team2.strip().split(' and ')
                team2_score = team2_players_and_score[0].split()[0].strip()
                team2_player1 = team2_players_and_score[0].split(maxsplit=1)[1].strip()
                team2_player2 = team2_players_and_score[-1].strip()

                games_dicts.append(
                    {
                        'team1_player1': team1_player1,
                        'team1_player2': team1_player2,
                        'team1_score': team1_score,
                        'team2_player1': team2_player1, 
                        'team2_player2': team2_player2, 
                        'team2_score': team2_score
                    }
                )
    return (games_dicts,)


@app.cell
def _(games_dicts, pd):
    games_df = pd.DataFrame(columns=['team1_player1', 'team1_player2', 'team1_score', 'team2_player1', 'team2_player2'])
    games_df = pd.DataFrame(games_dicts)
    return (games_df,)


@app.cell
def _(games_df):
    games_df
    return


@app.cell
def _(games_df):
    # Returns all rows where 'your_string' is found in any column
    games_df_filtered = games_df[games_df.apply(lambda row: row.astype(str).str.contains('Pritto').any(), axis=1)]
    return


@app.cell
def _():
    import numpy as np
    import seaborn as sns
    import matplotlib.pyplot as plt

    return np, plt, sns


@app.cell
def _(games_df_1, np, pd, plt, sns):
    # 1. Prepare unique list of all players
    players = sorted(list(set(games_df_1['team1_player1']) | set(games_df_1['team1_player2']) | set(games_df_1['team2_player1']) | set(games_df_1['team2_player2'])))
    n = len(players)
    counts = pd.DataFrame(np.zeros((n, n)), index=players, columns=players)
    # 2. Initialize empty matrices for games played and wins
    wins = pd.DataFrame(np.zeros((n, n)), index=players, columns=players)
    for _, row in games_df_1.iterrows():
        p1, p2 = sorted([row['team1_player1'], row['team1_player2']])
        counts.loc[p1, p2] = counts.loc[p1, p2] + 1
    # 3. Populate the matrices
        counts.loc[p2, p1] = counts.loc[p2, p1] + 1
        if row['team1_score'] > row['team2_score']:  # Process Team 1
            wins.loc[p1, p2] = wins.loc[p1, p2] + 1
            wins.loc[p2, p1] = wins.loc[p2, p1] + 1
        p3, p4 = sorted([row['team2_player1'], row['team2_player2']])
        counts.loc[p3, p4] = counts.loc[p3, p4] + 1
        counts.loc[p4, p3] = counts.loc[p4, p3] + 1
        if row['team2_score'] > row['team1_score']:
            wins.loc[p3, p4] = wins.loc[p3, p4] + 1
            wins.loc[p4, p3] = wins.loc[p4, p3] + 1  # Process Team 2
    win_rate = (wins / counts).fillna(0)
    plt.figure(figsize=(12, 10))
    sns.heatmap(win_rate, annot=True, cmap='RdYlGn', fmt='.2f', mask=np.eye(n))
    plt.title('Pairing Effectiveness (Win Rate Together)')
    # Calculate Win Rate (Win Matrix / Count Matrix)
    # 4. Visualization: Partnership Win Rate
    plt.show()  # Show win rate numbers  # Green for high win rate, Red for low  # Format to 2 decimal places  # Hide the diagonal (player playing with themselves)
    return


@app.cell
def _(pd):
    # Function to build a pairing matrix based on a metric
    def build_pairing_matrix(df, metric='count'):
        unique_players = sorted(list(set(df['team1_player1']) | set(df['team1_player2']) | set(df['team2_player1']) | set(df['team2_player2'])))
        count_matrix = pd.DataFrame(0.0, index=unique_players, columns=unique_players)
        win_matrix = pd.DataFrame(0.0, index=unique_players, columns=unique_players)
        for _, row in df.iterrows():  # Initialize matrices
            p1, p2 = sorted([row['team1_player1'], row['team1_player2']])
            count_matrix.loc[p1, p2] = count_matrix.loc[p1, p2] + 1
            count_matrix.loc[p2, p1] = count_matrix.loc[p2, p1] + 1
            if row['team1_score'] > row['team2_score']:
                win_matrix.loc[p1, p2] = win_matrix.loc[p1, p2] + 1  # Team 1 pairing
                win_matrix.loc[p2, p1] = win_matrix.loc[p2, p1] + 1
            p3, p4 = sorted([row['team2_player1'], row['team2_player2']])
            count_matrix.loc[p3, p4] = count_matrix.loc[p3, p4] + 1
            count_matrix.loc[p4, p3] = count_matrix.loc[p4, p3] + 1
            if row['team2_score'] > row['team1_score']:
                win_matrix.loc[p3, p4] = win_matrix.loc[p3, p4] + 1
                win_matrix.loc[p4, p3] = win_matrix.loc[p4, p3] + 1
        if metric == 'win_rate':  # Team 2 pairing
            return (win_matrix / count_matrix).fillna(0)
        return count_matrix  # Calculate win rate, handling division by zero

    return (build_pairing_matrix,)


@app.cell
def _(build_pairing_matrix, games_df_1):
    # Generate the matrices
    count_mtx = build_pairing_matrix(games_df_1, 'count')
    win_rate_mtx = build_pairing_matrix(games_df_1, 'win_rate')
    return (count_mtx,)


@app.cell
def _(count_mtx, plt, sns):
    # Plot 1: Partnership Frequency
    plt.figure(figsize=(10, 8))
    sns.heatmap(count_mtx, annot=True, cmap='Blues', fmt='.0f')
    plt.title('Partnership Frequency (Games Played Together)')
    plt.savefig('partnership_frequency.png')
    plt.close()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Loading time spent
    """)
    return


@app.cell
def _():
    game_time_dicts = []
    with open('../data/superbadder/20260421/audit.txt', 'r') as _f:
        for _line in _f:
            if 'Start Game' in _line:
                print(_line)  
                # team1, team2 = line.strip().split('-')  # team1_players_and_score = team1.strip().split(' and ')  # team1_score = team1_players_and_score[-1].split()[-1].strip()  # team1_player1 = team1_players_and_score[0]  # team1_player2 = ' '.join(team1_players_and_score[-1].split()[0:-1])  # team2_players_and_score = team2.strip().split(' and ')  # team2_score = team2_players_and_score[0].split()[0].strip()  # team2_player1 = team2_players_and_score[0].split(maxsplit=1)[1].strip()  # team2_player2 = team2_players_and_score[-1].strip()  # game_time_dicts.append(  #     {  #         'team1_player1': team1_player1,  #         'team1_player2': team1_player2,  #         'team1_score': team1_score,  #         'team2_player1': team2_player1,  #         'team2_player2': team2_player2,  #         'team2_score': team2_score  #     }  # )
    return


if __name__ == "__main__":
    app.run()
