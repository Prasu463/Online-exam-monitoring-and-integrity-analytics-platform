from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import os
import secrets
from functools import wraps

app = Flask(__name__)

app.secret_key = "examguard-secret-key-2026"

DATABASE = "database/examguard.db"
MAX_WARNINGS = 3


# ============================================================
# FOLDERS
# ============================================================

os.makedirs("database", exist_ok=True)
os.makedirs("static/uploads/id_cards", exist_ok=True)
os.makedirs("static/uploads/selfies", exist_ok=True)
os.makedirs("static/uploads/room_scan", exist_ok=True)
os.makedirs("static/uploads/violations", exist_ok=True)


# ============================================================
# EXAM STATUS
# ============================================================

exam_status = {
    "warnings": 0,
    "terminated": False,
    "message": ""
}


violation_counts = {
    "left": 0,
    "right": 0,
    "up": 0,
    "down": 0,
    "no_face": 0,
    "mobile": 0,
    "multiple_persons": 0,
    "tab_switch": 0
}


# ============================================================
# RISK CALCULATION
# ============================================================

def calculate_risk(data):
    def count(name):
        try:
            return int(data.get(name, 0) or 0)
        except (TypeError, ValueError):
            return 0

    risk_points = 0
    suspicious_events = []

    if count("no_face") > 0:
        risk_points += 1
        suspicious_events.append("Face Absence Detected")
    if count("multiple_persons") > 0:
        risk_points += 2
        suspicious_events.append("Multiple Person Detected")
    if count("looking_left") >= 10:
        risk_points += 1
        suspicious_events.append("Excessive Left Head Movement")
    if count("looking_right") >= 10:
        risk_points += 1
        suspicious_events.append("Excessive Right Head Movement")
    if count("looking_up") >= 10:
        risk_points += 1
        suspicious_events.append("Excessive Upward Head Movement")
    if count("looking_down") >= 10:
        risk_points += 1
        suspicious_events.append("Excessive Downward Head Movement")
    if count("mobile") > 0:
        risk_points += 3
        suspicious_events.append("Mobile Phone Detected")
    if count("tab_switch") > 0:
        risk_points += 1
        suspicious_events.append("Tab Switching Detected")

    if risk_points >= 6:
        risk_level = "HIGH RISK"
    elif risk_points >= 3:
        risk_level = "SUSPICIOUS"
    else:
        risk_level = "NORMAL"

    return risk_points, risk_level, suspicious_events


# ============================================================
# CREATE DATABASE TABLES
# ============================================================

def create_tables():

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # Candidates
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidates (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            fullname TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL,

            phone TEXT,

            photo TEXT

        )
    """)

    # Questions
    #
    # IMPORTANT:
    # Your existing database already uses:
    #
    # option1
    # option2
    # option3
    # option4
    # correct_answer
    #
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            question TEXT NOT NULL,

            option1 TEXT NOT NULL,

            option2 TEXT NOT NULL,

            option3 TEXT NOT NULL,

            option4 TEXT NOT NULL,

            correct_answer TEXT NOT NULL

        )
    """)

    # Browser/session logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS session_logs (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            session_id TEXT,

            candidate_name TEXT,

            candidate_email TEXT,

            event_type TEXT,

            event_time TEXT,

            event_value TEXT

        )
    """)

    # Exam results
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exam_results (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            candidate_name TEXT,

            candidate_email TEXT,

            score INTEGER,

            total_questions INTEGER,

            percentage REAL,

            total_warnings INTEGER DEFAULT 0,

            looking_left INTEGER DEFAULT 0,

            looking_right INTEGER DEFAULT 0,

            looking_up INTEGER DEFAULT 0,

            looking_down INTEGER DEFAULT 0,

            no_face INTEGER DEFAULT 0,

            mobile INTEGER DEFAULT 0,

            multiple_persons INTEGER DEFAULT 0,

            tab_switch INTEGER DEFAULT 0,

            exam_status TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    # Violation evidence
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS violation_evidence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            candidate_name TEXT,
            violation_type TEXT,
            warning_number INTEGER DEFAULT 0,
            screenshot_path TEXT,
            event_time TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Face absence logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS face_presence_logs (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            session_id TEXT,

            candidate_email TEXT,

            event_type TEXT,

            start_time TEXT,

            end_time TEXT,

            duration_seconds REAL

        )
    """)

    connection.commit()
    connection.close()


# ============================================================
# LOGIN REQUIRED
# ============================================================

def login_required(function):

    @wraps(function)
    def decorated_function(*args, **kwargs):

        if "email" not in session:
            return redirect(url_for("login"))

        return function(*args, **kwargs)

    return decorated_function


# ============================================================
# PROCTOR SESSION INFORMATION
# ============================================================

@app.route("/proctor_session")
@login_required
def proctor_session():

    return jsonify({
        "success": True,
        "session_id": session.get("exam_session_id", ""),
        "candidate_name": session.get("name", ""),
        "candidate_email": session.get("email", "")
    })


# ============================================================
# RESET EXAM
# ============================================================

def reset_exam():

    global exam_status
    global violation_counts

    exam_status = {
        "warnings": 0,
        "terminated": False,
        "message": ""
    }

    violation_counts = {
        "left": 0,
        "right": 0,
        "up": 0,
        "down": 0,
        "no_face": 0,
        "mobile": 0,
        "multiple_persons": 0,
        "tab_switch": 0
    }

    session["exam_session_id"] = (
        "EXAM-" + secrets.token_hex(4).upper()
    )


# ============================================================
# SAVE SESSION EVENT
# ============================================================

def save_session_event(event_type, event_value):

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO session_logs (

            session_id,

            candidate_name,

            candidate_email,

            event_type,

            event_time,

            event_value

        )

        VALUES (

            ?,
            ?,
            ?,
            ?,
            datetime('now'),
            ?

        )
    """, (

        session.get("exam_session_id", ""),

        session.get("name", ""),

        session.get("email", ""),

        event_type,

        event_value

    ))

    connection.commit()
    connection.close()

    print(
        "EVENT:",
        event_type,
        "|",
        event_value
    )


# ============================================================
# RECORD VIOLATION
# ============================================================

def record_violation(message):

    global violation_counts

    text = str(message).lower()

    if "looking left" in text:
        violation_counts["left"] += 1

    elif "looking right" in text:
        violation_counts["right"] += 1

    elif "looking up" in text:
        violation_counts["up"] += 1

    elif "looking down" in text:
        violation_counts["down"] += 1

    elif "no face" in text:
        violation_counts["no_face"] += 1

    elif "mobile" in text or "phone" in text:
        violation_counts["mobile"] += 1

    elif "multiple persons" in text:
        violation_counts["multiple_persons"] += 1

    elif "tab switch" in text:
        violation_counts["tab_switch"] += 1


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return render_template("index.html")


# ============================================================
# REGISTER
# ============================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        fullname = request.form.get(
            "fullname",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        if not fullname or not email or not password:

            flash(
                "Please fill all required fields.",
                "danger"
            )

            return render_template(
                "register.html"
            )

        connection = sqlite3.connect(DATABASE)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id
            FROM candidates
            WHERE email = ?
        """, (email,))

        existing = cursor.fetchone()

        if existing:

            connection.close()

            flash(
                "Email already exists!",
                "danger"
            )

            return render_template(
                "register.html"
            )

        cursor.execute("""
            INSERT INTO candidates (

                fullname,
                email,
                password,
                phone,
                photo

            )

            VALUES (?, ?, ?, ?, ?)

        """, (
            fullname,
            email,
            password,
            phone,
            ""
        ))

        connection.commit()
        connection.close()

        flash(
            "Registration successful!",
            "success"
        )

        return redirect(
            url_for("login")
        )

    return render_template(
        "register.html"
    )


# ============================================================
# LOGIN
# ============================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        connection = sqlite3.connect(DATABASE)
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                fullname,
                email,
                phone,
                photo

            FROM candidates

            WHERE email = ?

            AND password = ?

        """, (
            email,
            password
        ))

        user = cursor.fetchone()

        connection.close()

        if user:

            session["candidate_id"] = user[0]
            session["name"] = user[1]
            session["email"] = user[2]
            session["phone"] = user[3]
            session["photo"] = user[4]

            return redirect(
                url_for("dashboard")
            )

        flash(
            "Invalid Email or Password!",
            "danger"
        )

    return render_template(
        "login.html"
    )


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
@login_required
def dashboard():

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            fullname,
            email,
            phone,
            photo

        FROM candidates

        WHERE email = ?

    """, (
        session["email"],
    ))

    user = cursor.fetchone()

    connection.close()

    return render_template(
        "dashboard.html",
        user=user
    )


# ============================================================
# START EXAM
# ============================================================

@app.route("/start_exam")
@login_required
def start_exam():

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            fullname,
            email,
            phone,
            photo

        FROM candidates

        WHERE email = ?

    """, (
        session["email"],
    ))

    user = cursor.fetchone()

    connection.close()

    return render_template(
        "start_exam.html",
        user=user
    )


# ============================================================
# EXAM
# ============================================================

@app.route("/exam")
@login_required
def exam():

    reset_exam()

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # IMPORTANT:
    # Use the actual column names from your database.
    cursor.execute("""
        SELECT
            id,
            question,
            option1,
            option2,
            option3,
            option4,
            correct_answer

        FROM questions

        ORDER BY id
    """)

    questions = cursor.fetchall()

    connection.close()

    return render_template(
        "exam.html",
        questions=questions
    )


# ============================================================
# BROWSER EVENT LOGGING
# ============================================================

@app.route("/log_event", methods=["POST"])
@login_required
def log_event():

    data = request.get_json(
        silent=True
    )

    if not data:

        return jsonify({
            "success": False,
            "message": "No event data"
        }), 400

    event_type = data.get(
        "event_type",
        "UNKNOWN"
    )

    event_value = data.get(
        "event_value",
        ""
    )

    save_session_event(
        event_type,
        event_value
    )

    return jsonify({
        "success": True
    })


# ============================================================
# AI WARNING
# ============================================================

@app.route("/update_warning", methods=["POST"])
@login_required
def update_warning():

    global exam_status

    data = request.get_json(
        silent=True
    )

    if not data:

        return jsonify({
            "success": False,
            "message": "No warning data"
        }), 400

    message = data.get(
        "message",
        "WARNING"
    )

    # Don't add warnings after termination
    if exam_status["terminated"]:

        return jsonify({

            "success": True,

            "warnings":
                exam_status["warnings"],

            "terminated": True,

            "message":
                "EXAM TERMINATED",

            "violations":
                violation_counts

        })

    exam_status["warnings"] += 1

    exam_status["message"] = message

    record_violation(message)

    save_session_event(
        "AI_WARNING",
        message
    )

    if exam_status["warnings"] >= MAX_WARNINGS:

        exam_status["terminated"] = True

        exam_status["message"] = "EXAM TERMINATED"

    print()
    print(
        "WARNING:",
        message
    )

    print(
        "WARNING COUNT:",
        exam_status["warnings"]
    )

    print(
        "================================"
    )

    return jsonify({

        "success": True,

        "warnings":
            exam_status["warnings"],

        "terminated":
            exam_status["terminated"],

        "message":
            exam_status["message"],

        "violations":
            violation_counts

    })


# ============================================================
# TAB SWITCH WARNING
# ============================================================

@app.route("/tab_warning", methods=["POST"])
@login_required
def tab_warning():

    global exam_status

    if exam_status["terminated"]:

        return jsonify({

            "success": True,

            "warnings":
                exam_status["warnings"],

            "terminated": True,

            "message":
                "EXAM TERMINATED",

            "violations":
                violation_counts

        })

    exam_status["warnings"] += 1

    exam_status["message"] = (
        "WARNING : TAB SWITCH DETECTED"
    )

    violation_counts["tab_switch"] += 1

    save_session_event(
        "TAB_SWITCH",
        "Candidate switched browser tab"
    )

    if exam_status["warnings"] >= MAX_WARNINGS:

        exam_status["terminated"] = True

        exam_status["message"] = "EXAM TERMINATED"

    print()
    print(
        "WARNING:",
        exam_status["message"]
    )

    print(
        "WARNING COUNT:",
        exam_status["warnings"]
    )

    print(
        "================================"
    )

    return jsonify({

        "success": True,

        "warnings":
            exam_status["warnings"],

        "terminated":
            exam_status["terminated"],

        "message":
            exam_status["message"],

        "violations":
            violation_counts

    })


# ============================================================
# EXAM STATUS
# ============================================================

@app.route("/exam_status")
@login_required
def exam_status_api():

    return jsonify({

        "warnings":
            exam_status["warnings"],

        "terminated":
            exam_status["terminated"],

        "message":
            exam_status["message"],

        "violations":
            violation_counts

    })


# ============================================================
# SUBMIT EXAM
# ============================================================

@app.route("/submit_exam", methods=["POST"])
@login_required
def submit_exam():

    save_session_event(
        "EXAM_SUBMIT",
        "Candidate submitted examination"
    )

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # ========================================================
    # GET QUESTIONS
    # ========================================================

    cursor.execute("""
        SELECT
            id,
            question,
            option1,
            option2,
            option3,
            option4,
            correct_answer

        FROM questions

        ORDER BY id
    """)

    questions = cursor.fetchall()

    # ========================================================
    # CALCULATE SCORE
    # ========================================================

    score = 0

    for question in questions:

        question_id = str(
            question[0]
        )

        option1 = str(
            question[2]
        ).strip()

        option2 = str(
            question[3]
        ).strip()

        option3 = str(
            question[4]
        ).strip()

        option4 = str(
            question[5]
        ).strip()

        correct_answer = str(
            question[6]
        ).strip()

        selected_answer = request.form.get(
            "q" + question_id
        )

        if selected_answer:

            selected_answer = (
                selected_answer
                .strip()
                .upper()
            )

        # ----------------------------------------------------
        # Convert A/B/C/D into actual answer text
        # ----------------------------------------------------

        if selected_answer == "A":

            selected_text = option1

        elif selected_answer == "B":

            selected_text = option2

        elif selected_answer == "C":

            selected_text = option3

        elif selected_answer == "D":

            selected_text = option4

        else:

            selected_text = ""

        # ----------------------------------------------------
        # Compare answer text
        # ----------------------------------------------------

        if (
            selected_text.strip().lower()
            ==
            correct_answer.strip().lower()
        ):

            score += 1

    # ========================================================
    # SCORE / PERCENTAGE
    # ========================================================

    total = len(questions)

    if total > 0:

        percentage = round(
            (score / total) * 100,
            2
        )

    else:

        percentage = 0

    # ========================================================
    # PASS / FAIL
    # ========================================================

    if percentage >= 40:

        result_status = "PASSED"

    else:

        result_status = "FAILED"

    # ========================================================
    # TERMINATION
    # ========================================================

    if exam_status["terminated"]:

        final_status = "TERMINATED"

    else:

        final_status = result_status

    # ========================================================
    # SAVE RESULT
    # ========================================================

    cursor.execute("""
        INSERT INTO exam_results (

            candidate_name,

            candidate_email,

            score,

            total_questions,

            percentage,

            total_warnings,

            looking_left,

            looking_right,

            looking_up,

            looking_down,

            no_face,

            mobile,

            multiple_persons,

            tab_switch,

            exam_status

        )

        VALUES (

            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?

        )
    """, (

        session.get(
            "name",
            ""
        ),

        session.get(
            "email",
            ""
        ),

        score,

        total,

        percentage,

        exam_status["warnings"],

        violation_counts["left"],

        violation_counts["right"],

        violation_counts["up"],

        violation_counts["down"],

        violation_counts["no_face"],

        violation_counts["mobile"],

        violation_counts["multiple_persons"],

        violation_counts["tab_switch"],

        final_status

    ))

    connection.commit()
    connection.close()

    # ========================================================
    # TERMINAL OUTPUT
    # ========================================================

    print()
    print(
        "================================"
    )

    print(
        "EXAM RESULT"
    )

    print(
        "================================"
    )

    print(
        "Score:",
        score,
        "/",
        total
    )

    print(
        "Percentage:",
        percentage,
        "%"
    )

    print(
        "Warnings:",
        exam_status["warnings"]
    )

    print(
        "Status:",
        final_status
    )

    print(
        "================================"
    )

    # ========================================================
    # ========================================================
    # FINAL RISK CALCULATION
    # ========================================================

    risk_data = {
        "looking_left": violation_counts.get("left", 0),
        "looking_right": violation_counts.get("right", 0),
        "looking_up": violation_counts.get("up", 0),
        "looking_down": violation_counts.get("down", 0),
        "no_face": violation_counts.get("no_face", 0),
        "mobile": violation_counts.get("mobile", 0),
        "multiple_persons": violation_counts.get("multiple_persons", 0),
        "tab_switch": violation_counts.get("tab_switch", 0)
    }

    risk_points, risk_level, suspicious_events = calculate_risk(
        risk_data
    )

    # ========================================================
    # RESULT PAGE
    # ========================================================

    return render_template(
        "result.html",
        score=score,
        total=total,
        percentage=percentage,
        result_status=result_status,
        warnings=exam_status["warnings"],
        violations=violation_counts.copy(),
        terminated=exam_status["terminated"],
        message=exam_status["message"],
        risk_points=risk_points,
        risk_level=risk_level,
        suspicious_events=suspicious_events
    )

# ============================================================
# ADMIN RESULTS
# ============================================================

@app.route("/admin/results")
@login_required
def admin_results():

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT

            id,

            candidate_name,

            candidate_email,

            score,

            total_questions,

            percentage,

            total_warnings,

            looking_left,

            looking_right,

            looking_up,

            looking_down,

            no_face,

            mobile,

            multiple_persons,

            tab_switch,

            exam_status,

            created_at

        FROM exam_results

        ORDER BY id DESC
    """)

    results = cursor.fetchall()

    connection.close()

    return render_template(
        "admin_results.html",
        results=results
    )


# ============================================================
# FACULTY / PROCTOR DASHBOARD
# ============================================================

@app.route("/faculty/dashboard")
@login_required
def faculty_dashboard():

    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            candidate_name,
            candidate_email,
            score,
            total_questions,
            percentage,
            total_warnings,
            looking_left,
            looking_right,
            looking_up,
            looking_down,
            no_face,
            mobile,
            multiple_persons,
            tab_switch,
            exam_status,
            created_at
        FROM exam_results
        ORDER BY id DESC
    """)

    results = cursor.fetchall()

    sessions = []

    normal_count = 0
    suspicious_count = 0
    high_risk_count = 0

    for result in results:

        session_data = dict(result)

        risk_points, risk_level, suspicious_events = calculate_risk(
            session_data
        )

        if risk_level == "HIGH RISK":
            high_risk_count += 1
        elif risk_level == "SUSPICIOUS":
            suspicious_count += 1
        else:
            normal_count += 1

        session_data["risk_points"] = risk_points
        session_data["risk_level"] = risk_level
        session_data["suspicious_events"] = suspicious_events
        session_data["session_id"] = str(session_data["id"])

        sessions.append(session_data)

    connection.close()

    return render_template(
        "faculty_dashboard.html",
        sessions=sessions,
        total_exams=len(sessions),
        normal_count=normal_count,
        suspicious_count=suspicious_count,
        high_risk_count=high_risk_count
    )


# ============================================================
# FACULTY SESSION DETAILS
# ============================================================

@app.route("/faculty/session/<session_id>")
@login_required
def faculty_session_details(session_id):

    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM exam_results
        WHERE id = ?
        LIMIT 1
    """, (session_id,))

    result = cursor.fetchone()

    if result is None:
        connection.close()
        flash("Examination session not found.", "danger")
        return redirect(url_for("faculty_dashboard"))

    result = dict(result)

    risk_points, risk_level, suspicious_events = calculate_risk(result)

    # Existing database stores numeric exam_results.id separately
    # from the EXAM-XXXXXXXX session_id in session_logs.
    cursor.execute("""
        SELECT session_id
        FROM session_logs
        WHERE candidate_email = ?
          AND event_type = 'EXAM_SUBMIT'
        ORDER BY id DESC
        LIMIT 1
    """, (result["candidate_email"],))

    session_row = cursor.fetchone()
    actual_session_id = session_row["session_id"] if session_row else ""

    if actual_session_id:
        cursor.execute("""
            SELECT session_id, event_type, event_time, event_value
            FROM session_logs
            WHERE session_id = ?
            ORDER BY id DESC
        """, (actual_session_id,))
        logs = cursor.fetchall()

        cursor.execute("""
            SELECT session_id, event_type, start_time, end_time, duration_seconds
            FROM face_presence_logs
            WHERE session_id = ?
            ORDER BY id DESC
        """, (actual_session_id,))
        face_logs = cursor.fetchall()
    else:
        logs = []
        face_logs = []

    connection.close()

    return render_template(
        "faculty_session_details.html",
        result=result,
        logs=logs,
        face_logs=face_logs,
        session_id=actual_session_id or session_id,
        risk_level=risk_level,
        risk_points=risk_points,
        suspicious_events=suspicious_events
    )


# ============================================================
# FACULTY EVIDENCE
# ============================================================

@app.route("/faculty/session/<session_id>/evidence")
@login_required
def faculty_session_evidence(session_id):

    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM exam_results
        WHERE id = ?
        LIMIT 1
    """, (session_id,))

    result = cursor.fetchone()

    if result is None:
        connection.close()
        flash("Examination session not found.", "danger")
        return redirect(url_for("faculty_dashboard"))

    result = dict(result)

    # Find the real EXAM-XXXXXXXX session ID stored in session_logs.
    cursor.execute("""
        SELECT session_id
        FROM session_logs
        WHERE candidate_email = ?
          AND event_type = 'EXAM_SUBMIT'
        ORDER BY id DESC
        LIMIT 1
    """, (result["candidate_email"],))

    row = cursor.fetchone()
    actual_session_id = row["session_id"] if row else ""

    # Retrieve evidence using the real session ID when available.
    evidence = []

    if actual_session_id:
        cursor.execute("""
            SELECT
                id, session_id, candidate_name, violation_type,
                warning_number, screenshot_path, event_time
            FROM violation_evidence
            WHERE session_id = ?
            ORDER BY id DESC
        """, (actual_session_id,))
        rows = cursor.fetchall()
    else:
        rows = []

    for row in rows:
        item = dict(row)
        raw_path = str(item.get("screenshot_path") or "").replace("\\", "/")

        if raw_path.startswith("/static/"):
            static_filename = raw_path[len("/static/"):]
        elif raw_path.startswith("static/"):
            static_filename = raw_path[len("static/"):]
        else:
            static_filename = "uploads/violations/" + os.path.basename(raw_path) if raw_path else ""

        item["image_url"] = (
            url_for("static", filename=static_filename)
            if static_filename else None
        )
        evidence.append(item)

    connection.close()

    return render_template(
        "faculty_evidence.html",
        result=result,
        session_id=actual_session_id or session_id,
        evidence=evidence
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "Logged out successfully.",
        "success"
    )

    return redirect(
        url_for("login")
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    create_tables()

    print()
    print(
        "========================================"
    )

    print(
        "          EXAMGUARD SERVER"
    )

    print(
        "========================================"
    )

    print(
        "Database:",
        DATABASE
    )

    print(
        "Maximum warnings:",
        MAX_WARNINGS
    )

    print(
        "Server: http://127.0.0.1:5000"
    )

    print(
        "========================================"
    )

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )