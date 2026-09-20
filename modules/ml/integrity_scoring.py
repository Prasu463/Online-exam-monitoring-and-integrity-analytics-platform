import sqlite3
import pandas as pd
import os


# ============================================================
# SETTINGS
# ============================================================

DATABASE = "database/examguard.db"

OUTPUT_FOLDER = "modules/ml/output"

os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)


# ============================================================
# EVENT WEIGHTS
# ============================================================
#
# Higher weight = more suspicious
#
# Positive events have 0 penalty.
#
# ============================================================

EVENT_WEIGHTS = {

    "FACE_PRESENT": 0,

    "KEYBOARD_ACTIVITY": 0,

    "MOUSE_ACTIVITY": 0,

    "WINDOW_FOCUS": 0,

    "WINDOW_BLUR": 5,

    "FACE_ABSENT": 15,

    "LOOKING_LEFT": 10,

    "LOOKING_RIGHT": 10,

    "LOOKING_UP": 10,

    "LOOKING_DOWN": 10,

    "MULTIPLE_PERSONS": 25,

    "MOBILE_PHONE": 30,

    "TAB_SWITCH": 20,

    "AI_WARNING": 15

}


# ============================================================
# LOAD SESSION LOGS
# ============================================================

def load_logs():

    connection = sqlite3.connect(
        DATABASE
    )

    query = """
        SELECT
            session_id,
            candidate_name,
            candidate_email,
            event_type,
            event_time,
            event_value
        FROM session_logs
        WHERE session_id IS NOT NULL
        AND session_id != ''
    """

    df = pd.read_sql_query(
        query,
        connection
    )

    connection.close()

    return df


# ============================================================
# CALCULATE SESSION SCORE
# ============================================================

def calculate_scores(df):

    if df.empty:

        print(
            "No session logs found."
        )

        return pd.DataFrame()


    # --------------------------------------------------------
    # Add event weight
    # --------------------------------------------------------

    df["weight"] = (

        df["event_type"]

        .map(EVENT_WEIGHTS)

        .fillna(5)

    )


    # --------------------------------------------------------
    # Count events by session
    # --------------------------------------------------------

    grouped = df.groupby(
        [
            "session_id",
            "candidate_name",
            "candidate_email"
        ]
    )


    result = grouped.agg(

        total_events=(
            "event_type",
            "count"
        ),

        total_penalty=(
            "weight",
            "sum"
        )

    ).reset_index()


    # ========================================================
    # EVENT COUNTS
    # ========================================================

    event_counts = pd.crosstab(

        df["session_id"],

        df["event_type"]

    )


    event_counts = event_counts.reset_index()


    result = result.merge(

        event_counts,

        on="session_id",

        how="left"

    )


    # ========================================================
    # ENSURE REQUIRED COLUMNS EXIST
    # ========================================================

    required_events = [

        "FACE_PRESENT",

        "FACE_ABSENT",

        "LOOKING_LEFT",

        "LOOKING_RIGHT",

        "LOOKING_UP",

        "LOOKING_DOWN",

        "MULTIPLE_PERSONS",

        "MOBILE_PHONE",

        "TAB_SWITCH",

        "WINDOW_BLUR",

        "KEYBOARD_ACTIVITY",

        "MOUSE_ACTIVITY"

    ]


    for event in required_events:

        if event not in result.columns:

            result[event] = 0


    # ========================================================
    # FACE PRESENCE RATIO
    # ========================================================

    face_present = result[
        "FACE_PRESENT"
    ]

    face_absent = result[
        "FACE_ABSENT"
    ]


    total_face_events = (

        face_present
        +
        face_absent

    )


    result[
        "face_presence_ratio"
    ] = (

        face_present

        /

        total_face_events.replace(
            0,
            1
        )

    )


    # ========================================================
    # NORMALIZED PENALTY
    # ========================================================

    result[
        "penalty_per_event"
    ] = (

        result["total_penalty"]

        /

        result["total_events"].replace(
            0,
            1
        )

    )


    # ========================================================
    # INTEGRITY SCORE
    # ========================================================
    #
    # Start with 100.
    #
    # More suspicious activity
    # reduces the score.
    #
    # ========================================================

    result[
        "integrity_score"
    ] = (

        100

        -

        result["penalty_per_event"] * 5

    )


    # Keep score between 0 and 100

    result[
        "integrity_score"
    ] = result[
        "integrity_score"
    ].clip(
        0,
        100
    )


    # ========================================================
    # RISK LABEL
    # ========================================================

    def risk_label(score):

        if score >= 75:

            return "LOW"

        elif score >= 50:

            return "MEDIUM"

        else:

            return "HIGH"


    result[
        "risk_label"
    ] = result[
        "integrity_score"
    ].apply(
        risk_label
    )


    # ========================================================
    # ROUND VALUES
    # ========================================================

    result[
        "face_presence_ratio"
    ] = result[
        "face_presence_ratio"
    ].round(3)


    result[
        "penalty_per_event"
    ] = result[
        "penalty_per_event"
    ].round(2)


    result[
        "integrity_score"
    ] = result[
        "integrity_score"
    ].round(2)


    return result


# ============================================================
# SAVE RESULTS
# ============================================================

def save_results(result):

    output_file = os.path.join(

        OUTPUT_FOLDER,

        "integrity_scores.csv"

    )


    result.to_csv(

        output_file,

        index=False

    )


    print()
    print(
        "Results saved to:"
    )

    print(
        output_file
    )


# ============================================================
# DISPLAY RESULTS
# ============================================================

def display_results(result):

    print()
    print(
        "======================================================"
    )

    print(
        "             EXAMGUARD INTEGRITY ANALYSIS"
    )

    print(
        "======================================================"
    )


    for _, row in result.iterrows():

        print()

        print(
            "Session:",
            row["session_id"]
        )

        print(
            "Candidate:",
            row["candidate_name"]
        )

        print(
            "Total Events:",
            row["total_events"]
        )

        print(
            "Face Presence Ratio:",
            row["face_presence_ratio"]
        )

        print(
            "Total Penalty:",
            row["total_penalty"]
        )

        print(
            "Integrity Score:",
            row["integrity_score"]
        )

        print(
            "Risk:",
            row["risk_label"]
        )

        print(
            "------------------------------------------------------"
        )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print()
    print(
        "Loading session logs..."
    )


    logs = load_logs()


    print(
        "Total log records:",
        len(logs)
    )


    scores = calculate_scores(
        logs
    )


    if not scores.empty:

        display_results(
            scores
        )

        save_results(
            scores

        )

    else:

        print(
            "No data available for analysis."
        )