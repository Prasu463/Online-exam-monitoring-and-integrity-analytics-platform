import sqlite3
import random
import uuid

from datetime import datetime, timedelta

from faker import Faker


# ============================================================
# SETTINGS
# ============================================================

DATABASE = "database/examguard.db"

NUMBER_OF_SESSIONS = 20


fake = Faker()


# ============================================================
# EVENT TYPES
# ============================================================

EVENT_TYPES = [

    "FACE_PRESENT",

    "FACE_ABSENT",

    "TAB_SWITCH",

    "WINDOW_BLUR",

    "WINDOW_FOCUS",

    "LOOKING_LEFT",

    "LOOKING_RIGHT",

    "LOOKING_UP",

    "LOOKING_DOWN",

    "MOBILE_DETECTED",

    "MULTIPLE_PERSONS",

    "MOUSE_ACTIVITY",

    "KEYBOARD_ACTIVITY"

]


# ============================================================
# CREATE SESSION LOG TABLE
# ============================================================

def create_session_log_table():

    connection = sqlite3.connect(
        DATABASE
    )

    cursor = connection.cursor()


    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS session_logs (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            session_id TEXT,

            candidate_name TEXT,

            candidate_email TEXT,

            event_type TEXT,

            event_time TEXT,

            event_value TEXT

        )
        """
    )


    connection.commit()

    connection.close()


# ============================================================
# GENERATE SESSION LOGS
# ============================================================

def generate_session_logs():

    connection = sqlite3.connect(
        DATABASE
    )

    cursor = connection.cursor()


    for session_number in range(
        1,
        NUMBER_OF_SESSIONS + 1
    ):

        # ----------------------------------------------------
        # Generate candidate information
        # ----------------------------------------------------

        candidate_name = fake.name()

        candidate_email = fake.email()


        # ----------------------------------------------------
        # Generate session ID
        # ----------------------------------------------------

        session_id = (
            "SESSION-"
            + str(
                uuid.uuid4()
            )[:8].upper()
        )


        # ----------------------------------------------------
        # Generate starting time
        # ----------------------------------------------------

        start_time = datetime.now()


        # ----------------------------------------------------
        # Number of events
        # ----------------------------------------------------

        number_of_events = random.randint(
            5,
            15
        )


        for event_number in range(
            number_of_events
        ):

            event_type = random.choice(
                EVENT_TYPES
            )


            # ------------------------------------------------
            # Event timestamp
            # ------------------------------------------------

            event_time = (
                start_time
                + timedelta(
                    seconds=random.randint(
                        1,
                        3600
                    )
                )
            )


            # ------------------------------------------------
            # Event value
            # ------------------------------------------------

            if event_type == "FACE_PRESENT":

                event_value = "Face detected"


            elif event_type == "FACE_ABSENT":

                event_value = "Face not detected"


            elif event_type == "TAB_SWITCH":

                event_value = "Browser tab changed"


            elif event_type == "WINDOW_BLUR":

                event_value = "Exam window lost focus"


            elif event_type == "WINDOW_FOCUS":

                event_value = "Exam window regained focus"


            elif event_type == "LOOKING_LEFT":

                event_value = "Candidate looking left"


            elif event_type == "LOOKING_RIGHT":

                event_value = "Candidate looking right"


            elif event_type == "LOOKING_UP":

                event_value = "Candidate looking up"


            elif event_type == "LOOKING_DOWN":

                event_value = "Candidate looking down"


            elif event_type == "MOBILE_DETECTED":

                event_value = "Mobile phone detected"


            elif event_type == "MULTIPLE_PERSONS":

                event_value = "Multiple persons detected"


            elif event_type == "MOUSE_ACTIVITY":

                event_value = "Mouse interaction"


            elif event_type == "KEYBOARD_ACTIVITY":

                event_value = "Keyboard interaction"


            else:

                event_value = "Unknown event"


            # ------------------------------------------------
            # Save event
            # ------------------------------------------------

            cursor.execute(
                """
                INSERT INTO session_logs (

                    session_id,

                    candidate_name,

                    candidate_email,

                    event_type,

                    event_time,

                    event_value

                )

                VALUES (?, ?, ?, ?, ?, ?)

                """,

                (

                    session_id,

                    candidate_name,

                    candidate_email,

                    event_type,

                    event_time.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),

                    event_value

                )
            )


    connection.commit()

    connection.close()


# ============================================================
# DISPLAY GENERATED DATA
# ============================================================

def show_session_logs():

    connection = sqlite3.connect(
        DATABASE
    )

    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT
            id,
            session_id,
            candidate_name,
            event_type,
            event_time,
            event_value
        FROM session_logs
        ORDER BY id DESC
        LIMIT 20
        """
    )


    rows = cursor.fetchall()


    connection.close()


    print()

    print(
        "=============================================="
    )

    print(
        "       SYNTHETIC SESSION LOG DATA"
    )

    print(
        "=============================================="
    )


    for row in rows:

        print()

        print(
            "ID:",
            row[0]
        )

        print(
            "Session:",
            row[1]
        )

        print(
            "Candidate:",
            row[2]
        )

        print(
            "Event:",
            row[3]
        )

        print(
            "Time:",
            row[4]
        )

        print(
            "Value:",
            row[5]
        )

        print(
            "----------------------------------------------"
        )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    create_session_log_table()

    generate_session_logs()

    show_session_logs()

    print()

    print(
        "Synthetic session logs generated successfully."
    )