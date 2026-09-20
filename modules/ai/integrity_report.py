import pandas as pd
import os

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate


# ============================================================
# SETTINGS
# ============================================================

INPUT_FILE = "modules/ml/output/integrity_scores.csv"
OUTPUT_FOLDER = "modules/ai/output"

os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)


# ============================================================
# LOCAL AI MODEL
# ============================================================

# Qwen runs locally through Ollama.
# No OpenAI API key is required.

llm = ChatOllama(
    model="qwen2.5:0.5b",
    temperature=0.1,
    num_predict=120,
    num_ctx=1024,
    keep_alive="5m"
)


# ============================================================
# AI PROMPT
# ============================================================

# Python provides the verified facts.
# Qwen only explains them.

prompt = ChatPromptTemplate.from_template(
"""
You are an AI assistant for ExamGuard, an online exam
monitoring system.

Explain the verified findings below in 2 or 3 simple sentences.

Candidate: {candidate_name}
Risk Level: {risk_level}
Integrity Score: {integrity_score}

Verified suspicious activity:
{suspicious_events}

Important rules:
- Do not change the risk level.
- Do not call normal events suspicious.
- Do not invent any events.
- Do not mention events with zero occurrences.
- Focus only on the suspicious activities.
- Be concise and professional.
"""
)


chain = prompt | llm


# ============================================================
# LOAD DATA
# ============================================================

print()
print("Loading integrity scores...")
print()

try:

    df = pd.read_csv(INPUT_FILE)

except FileNotFoundError:

    print("ERROR: Integrity score file not found:")
    print(INPUT_FILE)
    exit()


print("Sessions found:", len(df))

print()
print("=" * 46)
print("       EXAMGUARD AI INTEGRITY REPORT")
print("=" * 46)
print()


# ============================================================
# EVENT CLASSIFICATION
# ============================================================

# These events are considered suspicious.

SUSPICIOUS_EVENTS = [
    "FACE_ABSENT",
    "LOOKING_DOWN",
    "LOOKING_LEFT",
    "LOOKING_RIGHT",
    "LOOKING_UP",
    "MOBILE_DETECTED",
    "MULTIPLE_PERSONS",
    "TAB_SWITCH",
    "MOBILE_PHONE",
    "WINDOW_BLUR"
]


# These are normal monitoring events.

NORMAL_EVENTS = [
    "EXAM_START",
    "EXAM_SUBMIT",
    "FACE_PRESENT",
    "KEYBOARD_ACTIVITY",
    "MOUSE_ACTIVITY",
    "WINDOW_FOCUS"
]


# ============================================================
# PROCESS EACH SESSION
# ============================================================

successful_reports = 0
failed_reports = 0


for index, row in df.iterrows():

    print(
        f"Generating AI report {index + 1}/{len(df)}..."
    )

    try:

        # ----------------------------------------------------
        # BASIC DATA
        # ----------------------------------------------------

        candidate_name = row.get(
            "candidate_name",
            "Unknown"
        )

        session_id = row.get(
            "session_id",
            "Unknown"
        )

        integrity_score = row.get(
            "integrity_score",
            0
        )

        risk_level = row.get(
            "risk_label",
            "UNKNOWN"
        )

        total_events = row.get(
            "total_events",
            0
        )

        total_penalty = row.get(
            "total_penalty",
            0
        )

        face_presence_ratio = row.get(
            "face_presence_ratio",
            0
        )


        # ----------------------------------------------------
        # FIND SUSPICIOUS EVENTS
        # ----------------------------------------------------

        suspicious_list = []

        for event in SUSPICIOUS_EVENTS:

            if event not in df.columns:
                continue

            value = row[event]

            if pd.isna(value):
                value = 0

            value = int(value)

            if value > 0:

                suspicious_list.append(
                    f"- {event}: {value} occurrence(s)"
                )


        # ----------------------------------------------------
        # SUSPICIOUS EVENT TEXT
        # ----------------------------------------------------

        if suspicious_list:

            suspicious_text = "\n".join(
                suspicious_list
            )

        else:

            suspicious_text = (
                "- No suspicious monitoring events detected."
            )


        # ----------------------------------------------------
        # NORMAL EVENTS
        # ----------------------------------------------------

        normal_list = []

        for event in NORMAL_EVENTS:

            if event not in df.columns:
                continue

            value = row[event]

            if pd.isna(value):
                value = 0

            value = int(value)

            if value > 0:

                normal_list.append(
                    f"- {event}: {value} occurrence(s)"
                )


        if normal_list:

            normal_text = "\n".join(
                normal_list
            )

        else:

            normal_text = (
                "- No normal monitoring events recorded."
            )


        # ----------------------------------------------------
        # PYTHON-CONTROLLED ASSESSMENT
        # ----------------------------------------------------

        if risk_level.upper() == "HIGH":

            overall_assessment = (
                f"The session has a HIGH risk level with "
                f"an integrity score of {integrity_score}."
            )

            recommendation = (
                "The session should be reviewed carefully "
                "before accepting the examination result."
            )


        elif risk_level.upper() == "MEDIUM":

            overall_assessment = (
                f"The session has a MEDIUM risk level with "
                f"an integrity score of {integrity_score}."
            )

            recommendation = (
                "The suspicious activities should be reviewed "
                "before making a final decision."
            )


        elif risk_level.upper() == "LOW":

            overall_assessment = (
                f"The session has a LOW risk level with "
                f"an integrity score of {integrity_score}."
            )

            recommendation = (
                "No major integrity concerns were identified, "
                "but the session can be retained for normal review."
            )


        else:

            overall_assessment = (
                f"The session has a {risk_level} risk level "
                f"with an integrity score of {integrity_score}."
            )

            recommendation = (
                "Review the available monitoring information "
                "before making a final decision."
            )


        # ----------------------------------------------------
        # AI EXPLANATION
        # ----------------------------------------------------

        try:

            response = chain.invoke(
                {
                    "candidate_name": candidate_name,
                    "risk_level": risk_level,
                    "integrity_score": integrity_score,
                    "suspicious_events": suspicious_text
                }
            )

            ai_explanation = response.content.strip()

        except Exception as ai_error:

            print(
                "AI explanation failed."
            )

            print(ai_error)

            # Fallback explanation.
            # The report will still be generated even if
            # the local AI model fails.

            if suspicious_list:

                ai_explanation = (
                    "The session contains the verified "
                    "suspicious activities listed above. "
                    "These activities should be reviewed "
                    "according to the session risk level."
                )

            else:

                ai_explanation = (
                    "No suspicious monitoring events were "
                    "detected in the verified session data."
                )


        # ----------------------------------------------------
        # OUTPUT FILE
        # ----------------------------------------------------

        safe_session_id = str(
            session_id
        ).replace("/", "_").replace("\\", "_")


        output_file = os.path.join(
            OUTPUT_FOLDER,
            f"{safe_session_id}_report.txt"
        )


        # ----------------------------------------------------
        # WRITE REPORT
        # ----------------------------------------------------

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                "========================================\n"
            )

            file.write(
                "       EXAMGUARD AI INTEGRITY REPORT\n"
            )

            file.write(
                "========================================\n\n"
            )


            # BASIC INFORMATION

            file.write(
                "SESSION INFORMATION\n"
            )

            file.write(
                "----------------------------------------\n"
            )

            file.write(
                f"Candidate: {candidate_name}\n"
            )

            file.write(
                f"Session ID: {session_id}\n"
            )

            file.write(
                f"Integrity Score: {integrity_score}\n"
            )

            file.write(
                f"Risk Level: {risk_level}\n"
            )

            file.write(
                f"Face Presence Ratio: {face_presence_ratio}\n"
            )

            file.write(
                f"Total Events: {total_events}\n"
            )

            file.write(
                f"Total Penalty: {total_penalty}\n\n"
            )


            # OVERALL ASSESSMENT

            file.write(
                "OVERALL ASSESSMENT\n"
            )

            file.write(
                "----------------------------------------\n"
            )

            file.write(
                overall_assessment
            )

            file.write("\n\n")


            # SUSPICIOUS EVENTS

            file.write(
                "VERIFIED SUSPICIOUS ACTIVITIES\n"
            )

            file.write(
                "----------------------------------------\n"
            )

            file.write(
                suspicious_text
            )

            file.write("\n\n")


            # NORMAL EVENTS

            file.write(
                "VERIFIED NORMAL MONITORING EVENTS\n"
            )

            file.write(
                "----------------------------------------\n"
            )

            file.write(
                normal_text
            )

            file.write("\n\n")


            # AI EXPLANATION

            file.write(
                "AI EXPLANATION\n"
            )

            file.write(
                "----------------------------------------\n"
            )

            file.write(
                ai_explanation
            )

            file.write("\n\n")


            # RISK EXPLANATION

            file.write(
                "RISK EXPLANATION\n"
            )

            file.write(
                "----------------------------------------\n"
            )

            if suspicious_list:

                file.write(
                    f"The session is classified as "
                    f"{risk_level} risk. "
                    f"The main suspicious activities are "
                    f"listed above and should be reviewed."
                )

            else:

                file.write(
                    f"The session is classified as "
                    f"{risk_level} risk and no suspicious "
                    f"monitoring events were detected."
                )

            file.write("\n\n")


            # RECOMMENDATION

            file.write(
                "RECOMMENDATION\n"
            )

            file.write(
                "----------------------------------------\n"
            )

            file.write(
                recommendation
            )

            file.write("\n")


        successful_reports += 1

        print(
            f"Report saved: {output_file}"
        )

        print()


    except Exception as error:

        failed_reports += 1

        print(
            "ERROR generating report:"
        )

        print(error)

        print()


# ============================================================
# FINAL SUMMARY
# ============================================================

print("=" * 46)

print(
    f"Reports generated successfully: "
    f"{successful_reports}"
)

print(
    f"Reports failed: {failed_reports}"
)

print("=" * 46)