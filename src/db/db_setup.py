import sqlite3
import uuid

DB_PATH = "../data/games.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON")


def new_session_id() -> str:
    return str(uuid.uuid4())


cursor.execute("""
    CREATE TABLE IF NOT EXISTS players (
        player_id      TEXT    PRIMARY KEY,
        player_name    TEXT    NOT NULL,
        member         INTEGER NOT NULL DEFAULT 0 CHECK(member IN (0, 1)),
        gender         TEXT    NOT NULL DEFAULT 'unspecified'
                           CHECK(gender IN ('male', 'female', 'unspecified')),
        singles_rank   REAL    CHECK(singles_rank > 0),
        doubles_rank   REAL    CHECK(doubles_rank > 0),
        mixed_rank     REAL    CHECK(mixed_rank > 0)
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        session_id    TEXT     PRIMARY KEY,
        session_date  DATE     NOT NULL,
        start_time    DATETIME,
        end_time      DATETIME,
        location      TEXT,
        courts        INTEGER  NOT NULL,
        shuttles_used INTEGER,
        status        TEXT     NOT NULL DEFAULT 'scheduled'
                          CHECK(status IN ('scheduled', 'in_progress', 'finished', 'cancelled')),
        created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS games (
        game_id       INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id    TEXT    NOT NULL,
        team1_player1 TEXT    NOT NULL,
        team1_player2 TEXT    NOT NULL,
        team1_score   INTEGER,
        team2_player1 TEXT    NOT NULL,
        team2_player2 TEXT    NOT NULL,
        team2_score   INTEGER,
        start_time    DATETIME,
        end_time      DATETIME,
        status        TEXT    NOT NULL DEFAULT 'in_progress'
                          CHECK(status IN ('finished', 'abandoned', 'in_progress')),
        FOREIGN KEY (session_id)    REFERENCES sessions(session_id),
        FOREIGN KEY (team1_player1) REFERENCES players(player_id),
        FOREIGN KEY (team1_player2) REFERENCES players(player_id),
        FOREIGN KEY (team2_player1) REFERENCES players(player_id),
        FOREIGN KEY (team2_player2) REFERENCES players(player_id)
    )
""")

conn.commit()