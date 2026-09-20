import cv2
from ai.face_detection import detect_faces

camera = cv2.VideoCapture(0)

while True:
    success, frame = camera.read()

    if not success:
        break

    result = detect_faces(frame)

    cv2.putText(
        frame,
        result["status"],
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2,
    )

    cv2.imshow("ExamGuard AI", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()