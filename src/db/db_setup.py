import sqlite3
from core import game


def create_all_dbs(db_path: str):
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    player_id      TEXT    PRIMARY KEY,
                    player_name    TEXT    NOT NULL,
                    member         INTEGER DEFAULT 0 CHECK(member IN (0, 1)),
                    gender         TEXT    DEFAULT 'unspecified'
                                    CHECK(gender IN ('male', 'female', 'unspecified')),
                    singles_rank   REAL    CHECK(singles_rank > 0),
                    doubles_rank   REAL    CHECK(doubles_rank > 0),
                    mixed_rank     REAL    CHECK(mixed_rank > 0)
                )
            """)

            # cursor.execute("""
            #     CREATE TABLE IF NOT EXISTS sessions (
            #         session_id    TEXT     PRIMARY KEY,
            #         session_date  DATE     NOT NULL,
            #         start_time    DATETIME,
            #         end_time      DATETIME,
            #         location      TEXT,
            #         courts        INTEGER  NOT NULL,
            #         shuttles_used INTEGER,
            #         status        TEXT     NOT NULL DEFAULT 'scheduled'
            #                         CHECK(status IN ('scheduled', 'in_progress', 'finished', 'cancelled')),
            #         created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
            #     )
            # """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS games (
                    game_id       INTEGER PRIMARY KEY AUTOINCREMENT,
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
                    FOREIGN KEY (team1_player1) REFERENCES players(player_id),
                    FOREIGN KEY (team1_player2) REFERENCES players(player_id),
                    FOREIGN KEY (team2_player1) REFERENCES players(player_id),
                    FOREIGN KEY (team2_player2) REFERENCES players(player_id)
                )
            """)

            # cursor.execute("""
            #     CREATE TABLE IF NOT EXISTS shuttle_inventory (
            #         shuttle_id     TEXT    PRIMARY KEY,
            #         brand          TEXT    NOT NULL,
            #         model          TEXT,
            #         type           TEXT    NOT NULL DEFAULT 'feather'
            #                         CHECK(type IN ('feather', 'synthetic')),
            #         speed          INTEGER,
            #         cost_per_tube  REAL,
            #         tubes_in_stock INTEGER NOT NULL DEFAULT 0 CHECK(tubes_in_stock >= 0)
            #     )
            # """)

    except sqlite3.OperationalError as e:
        raise RuntimeError(f"Failed to create tables at '{db_path}': {e}") from e


def player_id(name: str) -> str:
    return name.lower().replace(" ", "_")


def write_data_to_db(db_path: str, games: list[game.Game]):
    all_players = {
        p.player_id: p
        for g in games
        for p in (g.team1.player_1, g.team1.player_2, g.team2.player_1, g.team2.player_2)
    }.values()

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")

            cursor.executemany(
                "INSERT OR IGNORE INTO players (player_id, player_name) VALUES (?, ?)",
                [(p.player_id, p.name) for p in all_players],
            )

            cursor.executemany(
                """
                INSERT INTO games
                    (team1_player1, team1_player2, team1_score,
                     team2_player1, team2_player2, team2_score,
                     start_time, end_time, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        g.team1.player_1.player_id, g.team1.player_2.player_id, g.team1_score,
                        g.team2.player_1.player_id, g.team2.player_2.player_id, g.team2_score,
                        g.start_time.isoformat(), g.end_time.isoformat() if g.end_time else None,
                        g.outcome,
                    )
                    for g in games
                ],
            )

    except sqlite3.IntegrityError as e:
        raise RuntimeError(f"Integrity violation writing to '{db_path}': {e}") from e
    except sqlite3.OperationalError as e:
        raise RuntimeError(f"Failed to write to '{db_path}': {e}") from e

    print(f"Inserted {len(list(all_players))} players, {len(games)} games")
