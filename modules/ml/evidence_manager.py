import sqlite3
import os
from datetime import datetime


DATABASE = "database/examguard.db"


def create_evidence_table():

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS violation_evidence (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            session_id TEXT,

            candidate_name TEXT,

            violation_type TEXT,

            warning_number INTEGER,

            screenshot_path TEXT,

            event_time TEXT

        )
    """)

    connection.commit()

    connection.close()


def save_evidence(
    session_id,
    candidate_name,
    violation_type,
    warning_number,
    screenshot_path
):

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    event_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute("""
        INSERT INTO violation_evidence
        (
            session_id,
            candidate_name,
            violation_type,
            warning_number,
            screenshot_path,
            event_time
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        session_id,
        candidate_name,
        violation_type,
        warning_number,
        screenshot_path,
        event_time
    ))

    connection.commit()

    connection.close()


def get_evidence(session_id=None):

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    if session_id:

        cursor.execute("""
            SELECT
                id,
                session_id,
                candidate_name,
                violation_type,
                warning_number,
                screenshot_path,
                event_time
            FROM violation_evidence
            WHERE session_id = ?
            ORDER BY event_time DESC
        """, (session_id,))

    else:

        cursor.execute("""
            SELECT
                id,
                session_id,
                candidate_name,
                violation_type,
                warning_number,
                screenshot_path,
                event_time
            FROM violation_evidence
            ORDER BY event_time DESC
        """)

    rows = cursor.fetchall()

    connection.close()

    return rows


if __name__ == "__main__":

    create_evidence_table()

    print()
    print(
        "=========================================="
    )

    print(
        "ExamGuard Evidence Management"
    )

    print(
        "=========================================="
    )

    print(
        "Violation evidence table is ready."
    )