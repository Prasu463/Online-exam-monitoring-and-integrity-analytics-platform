import cv2
import os
from datetime import datetime

os.makedirs("static/uploads", exist_ok=True)

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Could not open webcam.")
    exit()

print("Press SPACE to capture photo")
print("Press ESC to exit")

while True:
    ret, frame = camera.read()

    if not ret:
        break

    cv2.imshow("Capture Photo", frame)

    key = cv2.waitKey(1)

    if key == 32:  # Space
        filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".jpg"
        filepath = os.path.join("static", "uploads", filename)

        cv2.imwrite(filepath, frame)

        print("Photo saved:", filepath)
        break

    elif key == 27:  # ESC
        break

camera.release()
cv2.destroyAllWindows()