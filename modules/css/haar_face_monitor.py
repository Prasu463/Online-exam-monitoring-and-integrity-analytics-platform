import cv2
import sqlite3
import time
from datetime import datetime


# ============================================================
# SETTINGS
# ============================================================

DATABASE = "database/examguard.db"

ABSENT_THRESHOLD = 2


# ============================================================
# HAAR CASCADE
# ============================================================

CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"

face_cascade = cv2.CascadeClassifier(
    CASCADE_PATH
)


# ============================================================
# CREATE FACE MONITORING TABLE
# ============================================================

def create_face_log_table():

    connection = sqlite3.connect(
        DATABASE
    )

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS face_presence_logs (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            session_id TEXT,

            candidate_email TEXT,

            event_type TEXT,

            start_time TEXT,

            end_time TEXT,

            duration_seconds REAL

        )
        """
    )

    connection.commit()

    connection.close()


# ============================================================
# SAVE FACE-ABSENT INTERVAL
# ============================================================

def save_absent_interval(
    session_id,
    candidate_email,
    start_time,
    end_time
):

    duration = (
        end_time - start_time
    ).total_seconds()


    connection = sqlite3.connect(
        DATABASE
    )

    cursor = connection.cursor()


    cursor.execute(
        """
        INSERT INTO face_presence_logs (

            session_id,

            candidate_email,

            event_type,

            start_time,

            end_time,

            duration_seconds

        )

        VALUES (?, ?, ?, ?, ?, ?)
        """,

        (

            session_id,

            candidate_email,

            "FACE_ABSENT",

            start_time.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

            end_time.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

            duration

        )
    )


    connection.commit()

    connection.close()


    print()
    print("================================")
    print("FACE ABSENT INTERVAL")
    print("================================")
    print(
        "Start:",
        start_time
    )
    print(
        "End:",
        end_time
    )
    print(
        "Duration:",
        round(
            duration,
            2
        ),
        "seconds"
    )
    print("================================")


# ============================================================
# MAIN FACE MONITOR
# ============================================================

def start_face_monitor():

    create_face_log_table()


    session_id = (
        "HAAR-"
        + datetime.now().strftime(
            "%Y%m%d%H%M%S"
        )
    )


    candidate_email = "test@example.com"


    cap = cv2.VideoCapture(0)


    if not cap.isOpened():

        print(
            "ERROR: Camera could not be opened."
        )

        return


    face_absent = False

    absent_start_time = None

    last_state = None


    print()
    print("================================")
    print("HAAR CASCADE FACE MONITOR")
    print("================================")
    print("Press Q to stop.")
    print("================================")


    while True:

        success, frame = cap.read()


        if not success:

            print(
                "Camera frame could not be read."
            )

            break


        frame = cv2.flip(
            frame,
            1
        )


        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )


        faces = face_cascade.detectMultiScale(

            gray,

            scaleFactor=1.1,

            minNeighbors=5,

            minSize=(80, 80)

        )


        current_time = datetime.now()


        # ====================================================
        # FACE PRESENT
        # ====================================================

        if len(faces) > 0:

            state = "FACE PRESENT"


            if face_absent:

                save_absent_interval(

                    session_id,

                    candidate_email,

                    absent_start_time,

                    current_time

                )


                face_absent = False

                absent_start_time = None


        # ====================================================
        # FACE ABSENT
        # ====================================================

        else:

            state = "FACE ABSENT"


            if not face_absent:

                face_absent = True

                absent_start_time = current_time


        # ====================================================
        # DRAW FACE BOX
        # ====================================================

        for (
            x,
            y,
            w,
            h
        ) in faces:

            cv2.rectangle(

                frame,

                (x, y),

                (x + w, y + h),

                (0, 255, 0),

                2

            )


        # ====================================================
        # DISPLAY STATUS
        # ====================================================

        if state == "FACE PRESENT":

            color = (
                0,
                255,
                0
            )

        else:

            color = (
                0,
                0,
                255
            )


        cv2.putText(

            frame,

            state,

            (20, 40),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.9,

            color,

            2

        )


        cv2.putText(

            frame,

            "Faces: "
            + str(
                len(faces)
            ),

            (20, 80),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.7,

            (255, 255, 0),

            2

        )


        cv2.imshow(

            "ExamGuard - Haar Face Monitor",

            frame

        )


        # ====================================================
        # EXIT
        # ====================================================

        if (
            cv2.waitKey(1)
            & 0xFF
            == ord("q")
        ):

            break


    # ========================================================
    # IF CAMERA CLOSED WHILE FACE ABSENT
    # ========================================================

    if face_absent:

        end_time = datetime.now()


        save_absent_interval(

            session_id,

            candidate_email,

            absent_start_time,

            end_time

        )


    cap.release()

    cv2.destroyAllWindows()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    start_face_monitor()