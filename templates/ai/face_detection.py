import cv2

# Load OpenCV's built-in face detector
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

def detect_faces(frame):
    """
    Detect faces in a webcam frame.

    Returns:
        {
            "status": "No Face" | "Face Detected" | "Multiple Faces",
            "count": int
        }
    """

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(60, 60)
    )

    count = len(faces)

    if count == 0:
        status = "No Face"
    elif count == 1:
        status = "Face Detected"
    else:
        status = "Multiple Faces"

    return {
        "status": status,
        "count": count
    }