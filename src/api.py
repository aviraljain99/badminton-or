import os
import sqlite3

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

DB_PATH = os.path.join(os.path.dirname(__file__), "../data/games.db")


@app.get("/api/players")
def get_players():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT player_id, player_name FROM players ORDER BY player_name")
        return [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]


@app.get("/api/games")
def get_games():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT team1_player1, team1_player2, team1_score, "
            "       team2_player1, team2_player2, team2_score "
            "FROM games WHERE status = 'finished'"
        )
        cols = [
            "team1_player1",
            "team1_player2",
            "team1_score",
            "team2_player1",
            "team2_player2",
            "team2_score",
        ]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]


@app.get("/api/court-time")
def get_court_time():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT p.player_id, p.player_name, COALESCE(SUM(pt.duration_min), 0) AS court_time_min
            FROM players p
            LEFT JOIN (
                SELECT team1_player1 AS player_id,
                       (julianday(end_time) - julianday(start_time)) * 1440 AS duration_min
                FROM games WHERE status IN ('finished', 'abandoned')
                  AND start_time IS NOT NULL AND end_time IS NOT NULL
                UNION ALL
                SELECT team1_player2,
                       (julianday(end_time) - julianday(start_time)) * 1440
                FROM games WHERE status IN ('finished', 'abandoned')
                  AND start_time IS NOT NULL AND end_time IS NOT NULL
                UNION ALL
                SELECT team2_player1,
                       (julianday(end_time) - julianday(start_time)) * 1440
                FROM games WHERE status IN ('finished', 'abandoned')
                  AND start_time IS NOT NULL AND end_time IS NOT NULL
                UNION ALL
                SELECT team2_player2,
                       (julianday(end_time) - julianday(start_time)) * 1440
                FROM games WHERE status IN ('finished', 'abandoned')
                  AND start_time IS NOT NULL AND end_time IS NOT NULL
            ) AS pt USING (player_id)
            GROUP BY p.player_id
            ORDER BY court_time_min DESC
            """
        )
        return [
            {"id": row[0], "name": row[1], "courtTimeMin": row[2]}
            for row in cursor.fetchall()
        ]