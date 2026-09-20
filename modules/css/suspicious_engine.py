import sqlite3


# ============================================================
# CONFIGURATION
# ============================================================

DATABASE = "database/examguard.db"

# Configurable thresholds
TAB_SWITCH_THRESHOLD = 3

FOCUS_LOSS_THRESHOLD = 5

FACE_ABSENCE_THRESHOLD = 120  # seconds

MULTIPLE_PERSON_THRESHOLD = 3

HEAD_POSE_THRESHOLD = 5


# ============================================================
# GET LATEST EXAM SESSION
# ============================================================

def get_latest_session_id():

    try:

        connection = sqlite3.connect(DATABASE)

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT session_id
            FROM session_logs
            WHERE event_type = 'EXAM_START'
            ORDER BY id DESC
            LIMIT 1
            """
        )

        result = cursor.fetchone()

        connection.close()

        if result:
            return result[0]

        return None

    except Exception as e:

        print(
            "Latest session error:",
            e
        )

        return None


# ============================================================
# GET AI VIOLATION COUNT
# ============================================================

def get_violation_count(session_id, keyword):

    try:

        connection = sqlite3.connect(DATABASE)

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM violation_evidence
            WHERE session_id = ?
            AND violation_type LIKE ?
            """,
            (
                session_id,
                "%" + keyword + "%"
            )
        )

        result = cursor.fetchone()

        connection.close()

        if result:
            return result[0]

        return 0

    except Exception as e:

        print(
            "Violation count error:",
            e
        )

        return 0


# ============================================================
# GET BROWSER EVENT COUNT
# ============================================================

def get_browser_event_count(session_id, event_type):

    try:

        connection = sqlite3.connect(DATABASE)

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM session_logs
            WHERE session_id = ?
            AND event_type = ?
            """,
            (
                session_id,
                event_type
            )
        )

        result = cursor.fetchone()

        connection.close()

        if result:
            return result[0]

        return 0

    except Exception as e:

        print(
            "Browser event count error:",
            e
        )

        return 0


# ============================================================
# GET TOTAL FACE ABSENCE
# ============================================================

def get_face_absence_duration(session_id):

    try:

        connection = sqlite3.connect(DATABASE)

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT COALESCE(
                SUM(duration_seconds),
                0
            )
            FROM face_absence_intervals
            WHERE session_id = ?
            """,
            (session_id,)
        )

        result = cursor.fetchone()

        connection.close()

        if result:
            return float(result[0])

        return 0.0

    except Exception as e:

        print(
            "Face absence error:",
            e
        )

        return 0.0


# ============================================================
# SAVE RISK RESULT
# ============================================================

def save_risk_result(
    session_id,
    risk_level,
    risk_points,
    suspicious_events
):

    try:

        connection = sqlite3.connect(DATABASE)

        cursor = connection.cursor()

        # ----------------------------------------------------
        # Create table if it does not exist
        # ----------------------------------------------------

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS suspicious_events
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                risk_level TEXT,
                risk_points INTEGER,
                suspicious_events TEXT
            )
            """
        )

        # ----------------------------------------------------
        # Convert events to text
        # ----------------------------------------------------

        events_text = ", ".join(
            suspicious_events
        )

        # ----------------------------------------------------
        # Save result
        # ----------------------------------------------------

        cursor.execute(
            """
            INSERT INTO suspicious_events
            (
                session_id,
                risk_level,
                risk_points,
                suspicious_events
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                session_id,
                risk_level,
                risk_points,
                events_text
            )
        )

        connection.commit()

        connection.close()

        print()
        print(
            "Risk result saved to database."
        )

    except Exception as e:

        print(
            "Risk result database error:",
            e
        )


# ============================================================
# SUSPICIOUS EVENT ANALYSIS
# ============================================================

def analyze_session(session_id):

    print()
    print(
        "=============================================="
    )
    print(
        "       SUSPICIOUS EVENT ANALYSIS"
    )
    print(
        "=============================================="
    )

    print()

    print(
        "Session:",
        session_id
    )

    # ========================================================
    # AI VIOLATIONS
    # ========================================================

    no_face = get_violation_count(
        session_id,
        "No Face"
    )

    multiple_persons = get_violation_count(
        session_id,
        "Multiple Persons"
    )

    looking_left = get_violation_count(
        session_id,
        "Looking Left"
    )

    looking_right = get_violation_count(
        session_id,
        "Looking Right"
    )

    # ========================================================
    # BROWSER EVENTS
    # ========================================================

    tab_switches = get_browser_event_count(
        session_id,
        "TAB_SWITCH"
    )

    focus_losses = get_browser_event_count(
        session_id,
        "WINDOW_BLUR"
    )

    # ========================================================
    # FACE ABSENCE
    # ========================================================

    face_absence_duration = (
        get_face_absence_duration(
            session_id
        )
    )

    # ========================================================
    # HEAD POSE
    # ========================================================

    head_pose_count = (
        looking_left
        +
        looking_right
    )

    # ========================================================
    # DISPLAY COUNTS
    # ========================================================

    print(
        "No Face:",
        no_face
    )

    print(
        "Multiple Persons:",
        multiple_persons
    )

    print(
        "Looking Left:",
        looking_left
    )

    print(
        "Looking Right:",
        looking_right
    )

    print(
        "Tab Switches:",
        tab_switches
    )

    print(
        "Focus Losses:",
        focus_losses
    )

    print(
        "Face Absence:",
        round(
            face_absence_duration,
            2
        ),
        "seconds"
    )

    # ========================================================
    # RISK CALCULATION
    # ========================================================

    suspicious_events = []

    risk_points = 0

    # ========================================================
    # TAB SWITCHING
    # ========================================================

    if tab_switches >= TAB_SWITCH_THRESHOLD:

        suspicious_events.append(
            "Excessive Tab Switching"
        )

        risk_points += 3

    elif tab_switches > 0:

        suspicious_events.append(
            "Tab Switching Detected"
        )

        risk_points += 1

    # ========================================================
    # WINDOW FOCUS LOSS
    # ========================================================

    if focus_losses >= FOCUS_LOSS_THRESHOLD:

        suspicious_events.append(
            "Excessive Window Focus Loss"
        )

        risk_points += 2

    elif focus_losses > 0:

        suspicious_events.append(
            "Window Focus Loss Detected"
        )

        risk_points += 1

    # ========================================================
    # FACE ABSENCE
    # ========================================================

    if (
        face_absence_duration
        >=
        FACE_ABSENCE_THRESHOLD
    ):

        suspicious_events.append(
            "Excessive Face Absence"
        )

        risk_points += 3

    elif no_face > 0:

        suspicious_events.append(
            "Face Absence Detected"
        )

        risk_points += 1

    # ========================================================
    # MULTIPLE PERSONS
    # ========================================================

    if (
        multiple_persons
        >=
        MULTIPLE_PERSON_THRESHOLD
    ):

        suspicious_events.append(
            "Repeated Multiple Persons"
        )

        risk_points += 3

    elif multiple_persons > 0:

        suspicious_events.append(
            "Multiple Person Detected"
        )

        risk_points += 2

    # ========================================================
    # HEAD MOVEMENT
    # ========================================================

    if (
        head_pose_count
        >=
        HEAD_POSE_THRESHOLD
    ):

        suspicious_events.append(
            "Excessive Head Movement"
        )

        risk_points += 2

    elif head_pose_count > 0:

        suspicious_events.append(
            "Head Direction Violation"
        )

        risk_points += 1

    # ========================================================
    # FINAL RISK LEVEL
    # ========================================================

    if risk_points >= 6:

        risk_level = "HIGH RISK"

    elif risk_points >= 3:

        risk_level = "SUSPICIOUS"

    else:

        risk_level = "NORMAL"

    # ========================================================
    # DISPLAY RESULT
    # ========================================================

    print()

    print(
        "Risk Points:",
        risk_points
    )

    print(
        "Risk Level:",
        risk_level
    )

    print()

    print(
        "Suspicious Events:"
    )

    if suspicious_events:

        for event in suspicious_events:

            print(
                " -",
                event
            )

    else:

        print(
            " - None"
        )

    # ========================================================
    # SAVE RESULT
    # ========================================================

    save_risk_result(
        session_id,
        risk_level,
        risk_points,
        suspicious_events
    )

    print()

    print(
        "=============================================="
    )

    return {
        "session_id": session_id,

        "risk_level": risk_level,

        "risk_points": risk_points,

        "suspicious_events":
            suspicious_events,

        "no_face":
            no_face,

        "multiple_persons":
            multiple_persons,

        "looking_left":
            looking_left,

        "looking_right":
            looking_right,

        "tab_switches":
            tab_switches,

        "focus_losses":
            focus_losses,

        "face_absence_seconds":
            face_absence_duration
    }


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    # --------------------------------------------------------
    # Automatically find latest exam
    # --------------------------------------------------------

    session_id = get_latest_session_id()

    if session_id is None:

        print()
        print(
            "No exam session found."
        )

        print(
            "Please start an exam first."
        )

    else:

        print()

        print(
            "Analyzing latest session:",
            session_id
        )

        print()

        result = analyze_session(
            session_id
        )