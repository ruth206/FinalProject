import cv2
import pickle
import face_recognition
import time
import numpy as np
from picamera2 import Picamera2

MODEL_PATH = "models/face_knn.pkl"

with open(MODEL_PATH, "rb") as f:
    knn = pickle.load(f)

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"size": (640, 480)}))
picam2.start()

print("Camera starting...")
time.sleep(3)   # gives you time to get into position

print("Press Q to quit.")

while True:

    frame = picam2.capture_array()

    # remove alpha channel if present
    if frame.shape[2] == 4:
        frame = frame[:, :, :3]

    # ensure OpenCV-compatible array
    frame = np.ascontiguousarray(frame)

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for (top, right, bottom, left), encoding in zip(face_locations, face_encodings):

        distances, _ = knn.kneighbors([encoding], n_neighbors=1)
        distance = distances[0][0]

        if distance < 0.50:
            prediction = knn.predict([encoding])[0]
        else:
            prediction = "unknown"

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

        cv2.putText(
            frame,
            prediction,
            (left, top - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

    cv2.imshow("Face Recognition Test", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

picam2.stop()
cv2.destroyAllWindows()