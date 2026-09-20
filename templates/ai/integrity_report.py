"""
ExamGuard - AI Integrity Report Agent

Uses:
    Pandas
    LangChain
    Ollama
    Qwen2.5 0.5B

No OpenAI API key is required.
"""

import os
import pandas as pd

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        ".."
    )
)

CSV_PATH = os.path.join(
    BASE_DIR,
    "modules",
    "ml",
    "output",
    "integrity_scores.csv"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "modules",
    "ai",
    "output"
)

# Create output directory if it doesn't exist
os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# ============================================================
# CHECK CSV
# ============================================================

if not os.path.exists(CSV_PATH):

    print("ERROR: Integrity CSV file not found.")
    print()
    print("Expected:")
    print(CSV_PATH)

    raise SystemExit


# ============================================================
# LOAD CSV
# ============================================================

df = pd.read_csv(CSV_PATH)

print()
print(f"Sessions found: {len(df)}")

print()
print("==============================================")
print("       EXAMGUARD AI INTEGRITY REPORT")
print("==============================================")


# ============================================================
# INITIALIZE LOCAL QWEN MODEL
# ============================================================

llm = ChatOllama(
    model="qwen2.5:0.5b",
    temperature=0.2
)


# ============================================================
# LANGCHAIN PROMPT
# ============================================================

prompt = ChatPromptTemplate.from_template(
    """
You are an AI integrity analyst for ExamGuard,
an online examination monitoring system.

Analyze the examination session information below.

Candidate: {candidate_name}
Session ID: {session_id}

Integrity Score: {integrity_score} / 100
Risk Level: {risk_label}

Face Presence Ratio: {face_presence_ratio}
Total Events: {total_events}
Total Penalty: {total_penalty}

Suspicious Events:

Looking Left: {looking_left}
Looking Right: {looking_right}
Looking Up: {looking_up}
Looking Down: {looking_down}
Face Absent: {no_face}
Mobile Detected: {mobile}
Multiple Persons: {multiple_persons}
Tab Switch: {tab_switch}

Generate a short professional integrity assessment.

Mention:
1. Overall integrity condition
2. Important suspicious activities
3. Whether the session requires review

Do not invent information.
Do not accuse the candidate of cheating.
Use cautious professional language.

Keep the response short.
"""
)


# ============================================================
# CREATE LANGCHAIN CHAIN
# ============================================================

chain = prompt | llm


# ============================================================
# SAFE VALUE FUNCTION
# ============================================================

def get_value(row, column, default=0):

    if column not in row.index:
        return default

    value = row[column]

    if pd.isna(value):
        return default

    return value


# ============================================================
# GENERATE ONE AI REPORT
# ============================================================

def generate_ai_report(row):

    candidate_name = get_value(
        row,
        "candidate_name",
        "Unknown Candidate"
    )

    session_id = get_value(
        row,
        "session_id",
        "Unknown Session"
    )

    integrity_score = float(
        get_value(
            row,
            "integrity_score",
            0
        )
    )

    risk_label = str(
        get_value(
            row,
            "risk_label",
            "UNKNOWN"
        )
    ).upper()

    face_presence_ratio = float(
        get_value(
            row,
            "face_presence_ratio",
            0
        )
    )

    total_events = int(
        get_value(
            row,
            "total_events",
            0
        )
    )

    total_penalty = float(
        get_value(
            row,
            "total_penalty",
            0
        )
    )

    # --------------------------------------------------------
    # EVENT COUNTS
    # --------------------------------------------------------

    looking_left = int(
        get_value(
            row,
            "LOOKING_LEFT",
            0
        )
    )

    looking_right = int(
        get_value(
            row,
            "LOOKING_RIGHT",
            0
        )
    )

    looking_up = int(
        get_value(
            row,
            "LOOKING_UP",
            0
        )
    )

    looking_down = int(
        get_value(
            row,
            "LOOKING_DOWN",
            0
        )
    )

    no_face = int(
        get_value(
            row,
            "FACE_ABSENT",
            0
        )
    )

    mobile = int(
        get_value(
            row,
            "MOBILE_DETECTED",
            0
        )
    )

    multiple_persons = int(
        get_value(
            row,
            "MULTIPLE_PERSONS",
            0
        )
    )

    tab_switch = int(
        get_value(
            row,
            "TAB_SWITCH",
            0
        )
    )


    # --------------------------------------------------------
    # CALL LOCAL QWEN THROUGH LANGCHAIN
    # --------------------------------------------------------

    response = chain.invoke({

        "candidate_name": candidate_name,

        "session_id": session_id,

        "integrity_score":
            f"{integrity_score:.2f}",

        "risk_label":
            risk_label,

        "face_presence_ratio":
            f"{face_presence_ratio:.3f}",

        "total_events":
            total_events,

        "total_penalty":
            f"{total_penalty:.2f}",

        "looking_left":
            looking_left,

        "looking_right":
            looking_right,

        "looking_up":
            looking_up,

        "looking_down":
            looking_down,

        "no_face":
            no_face,

        "mobile":
            mobile,

        "multiple_persons":
            multiple_persons,

        "tab_switch":
            tab_switch
    })


    ai_assessment = response.content


    # --------------------------------------------------------
    # RECOMMENDATION
    # --------------------------------------------------------

    if risk_label == "HIGH":

        recommendation = (
            "Perform a detailed review of the session "
            "logs and available evidence before accepting "
            "the examination."
        )

    elif risk_label == "MEDIUM":

        recommendation = (
            "Review the recorded session events and "
            "available evidence before finalizing the "
            "examination result."
        )

    else:

        recommendation = (
            "No immediate action is required. The session "
            "can be considered low risk."
        )


    # --------------------------------------------------------
    # FINAL REPORT
    # --------------------------------------------------------

    report = f"""
========================================
       EXAMGUARD INTEGRITY REPORT
========================================

Candidate:
{candidate_name}

Session ID:
{session_id}

----------------------------------------
INTEGRITY SUMMARY
----------------------------------------

Integrity Score:
{integrity_score:.2f} / 100

Risk Level:
{risk_label}

Face Presence Ratio:
{face_presence_ratio:.3f}

Total Events:
{total_events}

Total Penalty:
{total_penalty:.2f}

----------------------------------------
EVENT SUMMARY
----------------------------------------

Looking Left:
{looking_left}

Looking Right:
{looking_right}

Looking Up:
{looking_up}

Looking Down:
{looking_down}

Face Absent:
{no_face}

Mobile Detected:
{mobile}

Multiple Persons:
{multiple_persons}

Tab Switch:
{tab_switch}

----------------------------------------
AI-STYLE ASSESSMENT
----------------------------------------

{ai_assessment}

----------------------------------------
RECOMMENDATION
----------------------------------------

{recommendation}

========================================
          END OF REPORT
========================================
"""

    return report


# ============================================================
# PROCESS ALL SESSIONS
# ============================================================

successful = 0
failed = 0

for index, row in df.iterrows():

    print()
    print(
        f"Generating AI report "
        f"{index + 1}/{len(df)}..."
    )

    try:

        report = generate_ai_report(row)

        session_id = str(
            get_value(
                row,
                "session_id",
                f"SESSION_{index + 1}"
            )
        )

        # Keep only safe filename characters
        safe_session_id = "".join(
            character
            for character in session_id
            if character.isalnum()
            or character in "-_"
        )

        if not safe_session_id:

            safe_session_id = (
                f"SESSION_{index + 1}"
            )


        report_path = os.path.join(
            OUTPUT_DIR,
            f"{safe_session_id}_report.txt"
        )


        # Save report
        with open(
            report_path,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(report)


        print("AI report generated successfully.")
        print(
            f"Saved: {report_path}"
        )

        successful += 1


    except Exception as error:

        print()
        print("ERROR generating AI report:")
        print(error)

        failed += 1


# ============================================================
# FINAL STATUS
# ============================================================

print()
print("==============================================")
print("              PROCESS COMPLETED")
print("==============================================")

print(
    f"Successful reports: {successful}"
)

print(
    f"Failed reports: {failed}"
)

print(
    f"Total sessions: {len(df)}"
)

print()
print("Reports folder:")
print(OUTPUT_DIR)

print("==============================================")