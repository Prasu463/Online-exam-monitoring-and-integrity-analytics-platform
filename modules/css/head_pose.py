import cv2
import mediapipe as mp
import sqlite3
import os
import time
import requests


# ============================================================
# CONFIGURATION
# ============================================================

SESSION_ID = "TEST-SESSION"
CANDIDATE_NAME = "Prasanna Puttaparthi"

MAX_WARNINGS = 3

DATABASE = "database/examguard.db"

VIOLATION_FOLDER = "static/uploads/violations"

FLASK_URL = "http://127.0.0.1:5000"


# ============================================================
# FOLDERS
# ============================================================

os.makedirs(VIOLATION_FOLDER, exist_ok=True)
os.makedirs("database", exist_ok=True)


# ============================================================
# FACE ABSENCE TABLE
# ============================================================

def create_face_absence_table():

    try:

        connection = sqlite3.connect(DATABASE)

        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS face_absence_intervals
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                candidate_name TEXT,
                start_time TEXT,
                end_time TEXT,
                duration_seconds REAL
            )
            """
        )

        connection.commit()
        connection.close()

        print("Face absence table ready.")

    except Exception as e:

        print(
            "Face absence table error:",
            e
        )


create_face_absence_table()


# ============================================================
# SAVE FACE ABSENCE INTERVAL
# ============================================================

def save_face_absence_interval(
    session_id,
    candidate_name,
    start_time,
    end_time,
    duration_seconds
):

    try:

        connection = sqlite3.connect(DATABASE)

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO face_absence_intervals
            (
                session_id,
                candidate_name,
                start_time,
                end_time,
                duration_seconds
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                session_id,
                candidate_name,
                start_time,
                end_time,
                duration_seconds
            )
        )

        connection.commit()
        connection.close()

        print()
        print("--------------------------------")
        print("FACE ABSENCE INTERVAL SAVED")
        print("--------------------------------")
        print("Start:", start_time)
        print("End:", end_time)
        print(
            "Duration:",
            round(duration_seconds, 2),
            "seconds"
        )
        print("--------------------------------")

    except Exception as e:

        print(
            "Face absence database error:",
            e
        )


# ============================================================
# SAVE VIOLATION
# ============================================================

def save_violation(
    session_id,
    candidate_name,
    violation_type,
    warning_number,
    screenshot_path
):

    try:

        connection = sqlite3.connect(DATABASE)

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO violation_evidence
            (
                session_id,
                candidate_name,
                violation_type,
                warning_number,
                screenshot_path
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                session_id,
                candidate_name,
                violation_type,
                warning_number,
                screenshot_path
            )
        )

        connection.commit()
        connection.close()

        print(
            "Violation saved to database."
        )

    except Exception as e:

        print(
            "Database error:",
            e
        )


# ============================================================
# SEND WARNING TO FLASK
# ============================================================

def send_event(event_type):

    try:

        if event_type == "left":

            message = "WARNING : Looking Left"

        elif event_type == "right":

            message = "WARNING : Looking Right"

        elif event_type == "no_face":

            message = "WARNING : No Face"

        elif event_type == "multiple_persons":

            message = "WARNING : Multiple Persons"

        else:

            message = str(event_type)

        response = requests.post(
            FLASK_URL + "/update_warning",
            json={
                "message": message
            },
            timeout=2
        )

        print(
            "Flask warning update:",
            response.status_code
        )

        try:

            data = response.json()

            print(
                "Flask warnings:",
                data.get("warnings")
            )

            print(
                "Flask terminated:",
                data.get("terminated")
            )

        except Exception:

            pass

        return True

    except Exception as e:

        print(
            "Flask connection error:",
            e
        )

        return False


# ============================================================
# WARNING SYSTEM
# ============================================================

warning_count = 0


def create_warning(frame, message):

    global warning_count

    warning_count += 1

    print()
    print("================================")
    print(
        "WARNING:",
        message
    )
    print(
        "WARNING COUNT:",
        warning_count
    )
    print("================================")

    # ========================================================
    # SAVE SCREENSHOT
    # ========================================================

    timestamp = int(time.time())

    filename = (
        f"warning_{warning_count}_{timestamp}.jpg"
    )

    filepath = os.path.join(
        VIOLATION_FOLDER,
        filename
    )

    cv2.imwrite(
        filepath,
        frame
    )

    print(
        "Screenshot saved:",
        filepath
    )

    # ========================================================
    # SAVE DATABASE
    # ========================================================

    save_violation(
        SESSION_ID,
        CANDIDATE_NAME,
        message,
        warning_count,
        filepath
    )

    # ========================================================
    # SEND TO FLASK
    # ========================================================

    if "Looking Left" in message:

        send_event("left")

    elif "Looking Right" in message:

        send_event("right")

    elif "No Face" in message:

        send_event("no_face")

    elif "Multiple Persons" in message:

        send_event("multiple_persons")

    # ========================================================
    # TERMINATION
    # ========================================================

    if warning_count >= MAX_WARNINGS:

        print()
        print("================================")
        print(
            "EXAM TERMINATED"
        )
        print("================================")

        return True

    return False


# ============================================================
# MEDIAPIPE
# ============================================================

mp_face_mesh = mp.solutions.face_mesh

face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=5,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)


# ============================================================
# CAMERA
# ============================================================

cap = cv2.VideoCapture(
    0,
    cv2.CAP_DSHOW
)

if not cap.isOpened():

    print(
        "ERROR: Cannot open camera."
    )

    exit()


cap.set(
    cv2.CAP_PROP_FRAME_WIDTH,
    640
)

cap.set(
    cv2.CAP_PROP_FRAME_HEIGHT,
    480
)


# ============================================================
# HEADER
# ============================================================

print()
print(
    "=============================================="
)
print(
    "       EXAMGUARD FACE MONITOR"
)
print(
    "=============================================="
)

print()

print(
    "Session:",
    SESSION_ID
)

print(
    "Candidate:",
    CANDIDATE_NAME
)

print()

print(
    "Q = Quit"
)

print()

print(
    "Please look STRAIGHT at the camera."
)

print(
    "Calibrating for 3 seconds..."
)

print()


# ============================================================
# CALIBRATION
# ============================================================

CALIBRATION_TIME = 3

calibration_start = time.time()

calibration_values = []

calibration_complete = False

baseline_offset = 0.0


# ============================================================
# DETECTION SETTINGS
# ============================================================

TURN_THRESHOLD = 0.035

DIRECTION_CONFIRM_TIME = 0.7

WARNING_COOLDOWN = 2


# ============================================================
# STATE
# ============================================================

last_warning_time = 0

last_direction = "Looking Straight"

current_direction = "Looking Straight"

direction_start_time = time.time()


# ============================================================
# FACE ABSENCE STATE
# ============================================================

face_absent = False

face_absence_start_time = None

face_absence_start_text = None


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    success, frame = cap.read()

    if not success:

        print(
            "Unable to read camera."
        )

        break

    # --------------------------------------------------------
    # Mirror camera
    # --------------------------------------------------------

    frame = cv2.flip(
        frame,
        1
    )

    # --------------------------------------------------------
    # Convert BGR → RGB
    # --------------------------------------------------------

    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    # --------------------------------------------------------
    # MediaPipe
    # --------------------------------------------------------

    results = face_mesh.process(
        rgb_frame
    )

    face_count = 0

    if results.multi_face_landmarks:

        face_count = len(
            results.multi_face_landmarks
        )


    # ========================================================
    # NO FACE
    # ========================================================

    if face_count == 0:

        cv2.putText(
            frame,
            "NO FACE",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2
        )

        # ====================================================
        # START FACE ABSENCE INTERVAL
        # ====================================================

        if not face_absent:

            face_absent = True

            face_absence_start_time = time.time()

            face_absence_start_text = time.strftime(
                "%Y-%m-%d %H:%M:%S",
                time.localtime(
                    face_absence_start_time
                )
            )

            print()
            print(
                "================================"
            )
            print(
                "FACE ABSENCE STARTED"
            )
            print(
                "Start:",
                face_absence_start_text
            )
            print(
                "================================"
            )

        # ====================================================
        # SHOW ABSENCE DURATION
        # ====================================================

        if face_absence_start_time is not None:

            absence_duration = (
                time.time()
                -
                face_absence_start_time
            )

            cv2.putText(
                frame,
                f"Absent: {absence_duration:.1f}s",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2
            )

        # ====================================================
        # EXISTING WARNING SYSTEM
        # ====================================================

        if calibration_complete:

            current_time = time.time()

            if (
                current_time
                -
                last_warning_time
                >
                WARNING_COOLDOWN
            ):

                terminated = create_warning(
                    frame,
                    "WARNING : No Face"
                )

                last_warning_time = (
                    current_time
                )

                if terminated:

                    break


    # ========================================================
    # MULTIPLE FACES
    # ========================================================

    elif face_count > 1:

        # ----------------------------------------------------
        # If face returns after absence, save interval first
        # ----------------------------------------------------

        if face_absent:

            face_absent = False

            face_absence_end_time = time.time()

            face_absence_end_text = time.strftime(
                "%Y-%m-%d %H:%M:%S",
                time.localtime(
                    face_absence_end_time
                )
            )

            duration = (
                face_absence_end_time
                -
                face_absence_start_time
            )

            save_face_absence_interval(
                SESSION_ID,
                CANDIDATE_NAME,
                face_absence_start_text,
                face_absence_end_text,
                duration
            )

            face_absence_start_time = None

            face_absence_start_text = None

        # ----------------------------------------------------

        cv2.putText(
            frame,
            f"MULTIPLE FACES: {face_count}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2
        )

        if calibration_complete:

            current_time = time.time()

            if (
                current_time
                -
                last_warning_time
                >
                WARNING_COOLDOWN
            ):

                terminated = create_warning(
                    frame,
                    "WARNING : Multiple Persons"
                )

                last_warning_time = (
                    current_time
                )

                if terminated:

                    break


    # ========================================================
    # ONE FACE
    # ========================================================

    else:

        # ----------------------------------------------------
        # FACE RETURNED
        # ----------------------------------------------------

        if face_absent:

            face_absent = False

            face_absence_end_time = time.time()

            face_absence_end_text = time.strftime(
                "%Y-%m-%d %H:%M:%S",
                time.localtime(
                    face_absence_end_time
                )
            )

            duration = (
                face_absence_end_time
                -
                face_absence_start_time
            )

            print()
            print(
                "================================"
            )
            print(
                "FACE RETURNED"
            )
            print(
                "End:",
                face_absence_end_text
            )
            print(
                "Duration:",
                round(duration, 2),
                "seconds"
            )
            print(
                "================================"
            )

            save_face_absence_interval(
                SESSION_ID,
                CANDIDATE_NAME,
                face_absence_start_text,
                face_absence_end_text,
                duration
            )

            face_absence_start_time = None

            face_absence_start_text = None

        # ----------------------------------------------------

        face_landmarks = (
            results.multi_face_landmarks[0]
        )

        landmarks = (
            face_landmarks.landmark
        )

        # ----------------------------------------------------
        # Face landmarks
        # ----------------------------------------------------

        nose = landmarks[1]

        left_face = landmarks[234]

        right_face = landmarks[454]

        # ----------------------------------------------------
        # Face width
        # ----------------------------------------------------

        face_width = abs(
            right_face.x
            -
            left_face.x
        )

        if face_width > 0:

            # ------------------------------------------------
            # Face center
            # ------------------------------------------------

            face_center = (
                left_face.x
                +
                right_face.x
            ) / 2

            # ------------------------------------------------
            # Nose offset
            # ------------------------------------------------

            head_offset = (
                nose.x
                -
                face_center
            )

            # =================================================
            # CALIBRATION
            # =================================================

            if not calibration_complete:

                elapsed = (
                    time.time()
                    -
                    calibration_start
                )

                calibration_values.append(
                    head_offset
                )

                remaining = max(
                    0,
                    CALIBRATION_TIME
                    -
                    elapsed
                )

                cv2.putText(
                    frame,
                    "CALIBRATING - LOOK STRAIGHT",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 255),
                    2
                )

                cv2.putText(
                    frame,
                    f"Time: {remaining:.1f}s",
                    (20, 75),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 255),
                    2
                )

                # --------------------------------------------
                # Calibration complete
                # --------------------------------------------

                if elapsed >= CALIBRATION_TIME:

                    if len(calibration_values) > 0:

                        baseline_offset = (
                            sum(
                                calibration_values
                            )
                            /
                            len(
                                calibration_values
                            )
                        )

                    else:

                        baseline_offset = (
                            head_offset
                        )

                    calibration_complete = True

                    current_direction = (
                        "Looking Straight"
                    )

                    last_direction = (
                        "Looking Straight"
                    )

                    direction_start_time = (
                        time.time()
                    )

                    print()
                    print(
                        "=============================================="
                    )

                    print(
                        "CALIBRATION COMPLETE"
                    )

                    print(
                        "Baseline:",
                        round(
                            baseline_offset,
                            4
                        )
                    )

                    print(
                        "=============================================="
                    )

                    print()


            # =================================================
            # HEAD DIRECTION
            # =================================================

            else:

                relative_offset = (
                    head_offset
                    -
                    baseline_offset
                )

                # ------------------------------------------------
                # Debug information
                # ------------------------------------------------

                cv2.putText(
                    frame,
                    f"Baseline: {baseline_offset:.3f}",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (255, 255, 0),
                    2
                )

                cv2.putText(
                    frame,
                    f"Offset: {relative_offset:.3f}",
                    (20, 70),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (255, 255, 0),
                    2
                )

                # =================================================
                # DETERMINE DIRECTION
                # =================================================

                detected_direction = (
                    "Looking Straight"
                )

                if (
                    relative_offset
                    <
                    -TURN_THRESHOLD
                ):

                    detected_direction = (
                        "Looking Left"
                    )

                elif (
                    relative_offset
                    >
                    TURN_THRESHOLD
                ):

                    detected_direction = (
                        "Looking Right"
                    )

                # ------------------------------------------------
                # Display direction
                # ------------------------------------------------

                cv2.putText(
                    frame,
                    detected_direction,
                    (20, 105),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (0, 255, 0),
                    2
                )

                # =================================================
                # DIRECTION CHANGED
                # =================================================

                if (
                    detected_direction
                    !=
                    last_direction
                ):

                    last_direction = (
                        detected_direction
                    )

                    direction_start_time = (
                        time.time()
                    )

                direction_duration = (
                    time.time()
                    -
                    direction_start_time
                )

                # =================================================
                # CONFIRM LEFT / RIGHT
                # =================================================

                if (
                    detected_direction
                    in
                    [
                        "Looking Left",
                        "Looking Right"
                    ]
                    and
                    direction_duration
                    >=
                    DIRECTION_CONFIRM_TIME
                ):

                    current_time = (
                        time.time()
                    )

                    if (
                        current_time
                        -
                        last_warning_time
                        >
                        WARNING_COOLDOWN
                    ):

                        if (
                            detected_direction
                            !=
                            current_direction
                        ):

                            current_direction = (
                                detected_direction
                            )

                            # ------------------------------------
                            # LEFT
                            # ------------------------------------

                            if (
                                detected_direction
                                ==
                                "Looking Left"
                            ):

                                terminated = (
                                    create_warning(
                                        frame,
                                        "WARNING : Looking Left"
                                    )
                                )

                            # ------------------------------------
                            # RIGHT
                            # ------------------------------------

                            else:

                                terminated = (
                                    create_warning(
                                        frame,
                                        "WARNING : Looking Right"
                                    )
                                )

                            last_warning_time = (
                                current_time
                            )

                            if terminated:

                                break

                # =================================================
                # RETURN STRAIGHT
                # =================================================

                if (
                    detected_direction
                    ==
                    "Looking Straight"
                ):

                    current_direction = (
                        "Looking Straight"
                    )


    # ========================================================
    # WARNING DISPLAY
    # ========================================================

    cv2.putText(
        frame,
        f"Warnings: {warning_count}/{MAX_WARNINGS}",
        (20, 450),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 255),
        2
    )


    # ========================================================
    # SHOW CAMERA
    # ========================================================

    cv2.imshow(
        "ExamGuard Face Monitor",
        frame
    )


    # ========================================================
    # QUIT
    # ========================================================

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):

        print(
            "User stopped monitoring."
        )

        break


# ============================================================
# SAVE OPEN FACE-ABSENCE INTERVAL BEFORE EXIT
# ============================================================

if face_absent and face_absence_start_time is not None:

    face_absence_end_time = time.time()

    face_absence_end_text = time.strftime(
        "%Y-%m-%d %H:%M:%S",
        time.localtime(
            face_absence_end_time
        )
    )

    duration = (
        face_absence_end_time
        -
        face_absence_start_time
    )

    save_face_absence_interval(
        SESSION_ID,
        CANDIDATE_NAME,
        face_absence_start_text,
        face_absence_end_text,
        duration
    )


# ============================================================
# CLEANUP
# ============================================================

cap.release()

cv2.destroyAllWindows()

face_mesh.close()

print()

print(
    "Camera closed."
)