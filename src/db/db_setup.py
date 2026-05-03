import sqlite3

DB_PATH = "../data/games.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS players (
        player_id TEXT PRIMARY KEY,
        player_name TEXT NOT NULL,
        member INTEGER NOT NULL DEFAULT 0 CHECK(member IN (0, 1))
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS games (
        game_id INTEGER PRIMARY KEY AUTOINCREMENT,
        team1_player1 TEXT NOT NULL,
        team1_player2 TEXT NOT NULL,
        team1_score INTEGER,
        team2_player1 TEXT NOT NULL,
        team2_player2 TEXT NOT NULL,
        team2_score INTEGER,
        start_time DATETIME,
        end_time DATETIME,
        status TEXT NOT NULL DEFAULT 'in_progress'
            CHECK(status IN ('finished', 'abandoned', 'in_progress')),
        FOREIGN KEY (team1_player1) REFERENCES players(player_id),
        FOREIGN KEY (team1_player2) REFERENCES players(player_id),
        FOREIGN KEY (team2_player1) REFERENCES players(player_id),
        FOREIGN KEY (team2_player2) REFERENCES players(player_id)
    )
""")

conn.commit()