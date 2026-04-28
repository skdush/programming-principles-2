import psycopg2
from config import DB_CONFIG


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def setup_db():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    id       SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS game_sessions (
                    id            SERIAL PRIMARY KEY,
                    player_id     INTEGER REFERENCES players(id),
                    score         INTEGER NOT NULL,
                    level_reached INTEGER NOT NULL,
                    played_at     TIMESTAMP DEFAULT NOW()
                )
            """)


def save_result(username, score, level):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO players (username) VALUES (%s)
                ON CONFLICT (username) DO NOTHING
            """, (username,))
            cur.execute("SELECT id FROM players WHERE username = %s", (username,))
            player_id = cur.fetchone()[0]
            cur.execute("""
                INSERT INTO game_sessions (player_id, score, level_reached)
                VALUES (%s, %s, %s)
            """, (player_id, score, level))


def get_top10():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT p.username, gs.score, gs.level_reached,
                       TO_CHAR(gs.played_at, 'YYYY-MM-DD')
                FROM game_sessions gs
                JOIN players p ON p.id = gs.player_id
                ORDER BY gs.score DESC
                LIMIT 10
            """)
            return cur.fetchall()


def get_personal_best(username):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT MAX(gs.score)
                FROM game_sessions gs
                JOIN players p ON p.id = gs.player_id
                WHERE p.username = %s
            """, (username,))
            row = cur.fetchone()
            return row[0] if row and row[0] else 0
