import sqlite3
import json
import os
from contextlib import contextmanager

from app.config import DATABASE_PATH


def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_db():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS loads (
                load_id TEXT PRIMARY KEY,
                origin TEXT NOT NULL,
                destination TEXT NOT NULL,
                pickup_datetime TEXT NOT NULL,
                delivery_datetime TEXT NOT NULL,
                equipment_type TEXT NOT NULL,
                loadboard_rate REAL NOT NULL,
                notes TEXT,
                weight REAL,
                commodity_type TEXT,
                num_of_pieces INTEGER,
                miles REAL,
                dimensions TEXT
            );

            CREATE TABLE IF NOT EXISTS calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                call_id TEXT UNIQUE,
                session_id TEXT,
                carrier_name TEXT,
                mc_number TEXT,
                equipment_type TEXT,
                load_id TEXT,
                offered_rate REAL,
                agreed_rate REAL,
                outcome TEXT,
                sentiment TEXT,
                negotiation_rounds INTEGER DEFAULT 0,
                call_duration REAL,
                timestamp TEXT NOT NULL,
                transcript TEXT,
                FOREIGN KEY (load_id) REFERENCES loads(load_id)
            );

            CREATE TABLE IF NOT EXISTS negotiations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                call_id TEXT NOT NULL,
                round_number INTEGER NOT NULL,
                carrier_offer REAL,
                agent_offer REAL,
                accepted INTEGER DEFAULT 0,
                timestamp TEXT NOT NULL
            );
        """)

        cursor = conn.execute("SELECT COUNT(*) FROM loads")
        if cursor.fetchone()[0] == 0:
            seed_path = os.path.join(os.path.dirname(__file__), "..", "data", "seed_loads.json")
            with open(seed_path) as f:
                loads = json.load(f)
            conn.executemany(
                """INSERT INTO loads (load_id, origin, destination, pickup_datetime,
                   delivery_datetime, equipment_type, loadboard_rate, notes, weight,
                   commodity_type, num_of_pieces, miles, dimensions)
                   VALUES (:load_id, :origin, :destination, :pickup_datetime,
                   :delivery_datetime, :equipment_type, :loadboard_rate, :notes,
                   :weight, :commodity_type, :num_of_pieces, :miles, :dimensions)""",
                loads,
            )
            conn.commit()
