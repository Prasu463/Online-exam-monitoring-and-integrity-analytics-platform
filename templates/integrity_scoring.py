"""
===========================================================
EXAMGUARD - MILESTONE 3
INTEGRITY SCORING MODULE
===========================================================

Purpose:
    Calculate the integrity/risk score of an exam session
    using the monitoring events generated in Milestone 2.

Input:
    Number of monitoring events

Output:
    - Weighted risk score
    - Normalized score
    - Face-presence ratio
    - Risk level: LOW / MEDIUM / HIGH
===========================================================
"""


# ---------------------------------------------------------
# 1. EVENT WEIGHTS
# ---------------------------------------------------------
# Each suspicious event has a different importance.
#
# Higher weight = more serious event.
#
# These weights are based on the rule-based scoring
# already used in your project.
# ---------------------------------------------------------

EVENT_WEIGHTS = {

    "NO_FACE": 1,

    "LOOKING_LEFT": 1,

    "LOOKING_RIGHT": 1,

    "LOOKING_UP": 1,

    "LOOKING_DOWN": 1,

    "MULTIPLE_PERSONS": 2,

    "MOBILE_DETECTED": 3,

    "TAB_SWITCH": 1
}


# ---------------------------------------------------------
# 2. CALCULATE WEIGHTED RISK SCORE
# ---------------------------------------------------------

def calculate_weighted_score(events):
    """
    Calculate the total weighted score.

    events should be a dictionary like:

    {
        "NO_FACE": 2,
        "LOOKING_LEFT": 3,
        "TAB_SWITCH": 1
    }

    Returns:
        Total weighted score
    """

    total_score = 0

    # Go through every event in the session
    for event_name, event_count in events.items():

        # Get the weight of the event.
        # If the event is not defined, use 0.
        weight = EVENT_WEIGHTS.get(
            event_name,
            0
        )

        # Multiply:
        # number of events × event weight
        total_score += (
            event_count * weight
        )

    return total_score


# ---------------------------------------------------------
# 3. CALCULATE FACE-PRESENCE RATIO
# ---------------------------------------------------------

def calculate_face_presence_ratio(
    total_monitoring_checks,
    no_face_count
):
    """
    Calculate how often the candidate's face
    was visible during monitoring.

    Formula:

        Face Presence Ratio =
        (Total Checks - No Face Checks)
        / Total Checks

    Example:

        Total checks = 100
        No face = 10

        Ratio = (100 - 10) / 100
              = 0.90

        Therefore:
        Face presence = 90%
    """

    # Avoid division by zero
    if total_monitoring_checks <= 0:
        return 0.0

    face_present_checks = (
        total_monitoring_checks
        - no_face_count
    )

    # Make sure the value doesn't become negative
    face_present_checks = max(
        face_present_checks,
        0
    )

    ratio = (
        face_present_checks
        / total_monitoring_checks
    )

    return round(
        ratio,
        2
    )


# ---------------------------------------------------------
# 4. NORMALIZE THE RISK SCORE
# ---------------------------------------------------------

def normalize_score(
    score,
    maximum_score
):
    """
    Convert the raw risk score into a percentage.

    Example:

        score = 5
        maximum_score = 10

        normalized score = 50
    """

    if maximum_score <= 0:
        return 0

    normalized = (
        score / maximum_score
    ) * 100

    # Keep score between 0 and 100
    normalized = max(
        0,
        min(normalized, 100)
    )

    return round(
        normalized,
        2
    )


# ---------------------------------------------------------
# 5. ASSIGN RISK LEVEL
# ---------------------------------------------------------

def get_risk_level(normalized_score):
    """
    Convert the normalized score into a risk level.

    0 - 33     → LOW
    34 - 66    → MEDIUM
    67 - 100   → HIGH
    """

    if normalized_score <= 33:

        return "LOW"

    elif normalized_score <= 66:

        return "MEDIUM"

    else:

        return "HIGH"


# ---------------------------------------------------------
# 6. COMPLETE SESSION ANALYSIS
# ---------------------------------------------------------

def analyze_session(
    events,
    total_monitoring_checks
):
    """
    Perform complete integrity analysis
    for one examination session.

    Returns a dictionary containing:

        weighted score
        normalized score
        face presence ratio
        risk level
    """

    # Get NO_FACE count
    no_face_count = events.get(
        "NO_FACE",
        0
    )

    # ---------------------------------------------
    # Calculate weighted score
    # ---------------------------------------------

    weighted_score = calculate_weighted_score(
        events
    )

    # ---------------------------------------------
    # Calculate maximum possible score
    #
    # We use the total number of monitoring checks
    # as the base for normalization.
    # ---------------------------------------------

    maximum_score = (
        total_monitoring_checks
        * max(EVENT_WEIGHTS.values())
    )

    # ---------------------------------------------
    # Calculate normalized score
    # ---------------------------------------------

    normalized_score = normalize_score(
        weighted_score,
        maximum_score
    )

    # ---------------------------------------------
    # Calculate face-presence ratio
    # ---------------------------------------------

    face_presence_ratio = (
        calculate_face_presence_ratio(
            total_monitoring_checks,
            no_face_count
        )
    )

    # ---------------------------------------------
    # Determine risk level
    # ---------------------------------------------

    risk_level = get_risk_level(
        normalized_score
    )

    # ---------------------------------------------
    # Return all results
    # ---------------------------------------------

    return {

        "weighted_score":
            weighted_score,

        "normalized_score":
            normalized_score,

        "face_presence_ratio":
            face_presence_ratio,

        "risk_level":
            risk_level
    }


# ---------------------------------------------------------
# 7. TEST THE MODULE
# ---------------------------------------------------------
# This section runs only when this file itself is executed.
#
# It will NOT run automatically when app.py imports this
# module.
# ---------------------------------------------------------

if __name__ == "__main__":

    # Example session data
    test_events = {

        "NO_FACE": 3,

        "LOOKING_LEFT": 2,

        "LOOKING_RIGHT": 1,

        "LOOKING_UP": 0,

        "LOOKING_DOWN": 1,

        "MULTIPLE_PERSONS": 1,

        "MOBILE_DETECTED": 0,

        "TAB_SWITCH": 2
    }

    # Number of face-monitoring checks
    total_checks = 100

    # Analyse the session
    result = analyze_session(
        test_events,
        total_checks
    )

    # Display the result
    print("\n===== INTEGRITY ANALYSIS =====")

    print(
        "Weighted Score:",
        result["weighted_score"]
    )

    print(
        "Normalized Score:",
        result["normalized_score"],
        "%"
    )

    print(
        "Face Presence Ratio:",
        result["face_presence_ratio"] * 100,
        "%"
    )

    print(
        "Risk Level:",
        result["risk_level"]
    )