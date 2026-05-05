import cv2
import face_recognition
import pickle
import time
from picamera2 import Picamera2


def face_capture():
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"size": (640, 480)}))
    picam2.start()
    time.sleep(2)

    print("Camera opened.")
    print("Look at the camera and press SPACE to capture.")
    print("Press Q to quit.")

    face_bytes = None

    while True:
        frame = picam2.capture_array()

        # Picamera2 often returns 4 channels (XBGR/RGBA-like), so trim to 3
        if frame.shape[2] == 4:
            frame = frame[:, :, :3]

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_frame)

        display_frame = frame.copy()
        for (top, right, bottom, left) in face_locations:
            cv2.rectangle(display_frame, (left, top), (right, bottom), (0, 255, 0), 2)

        cv2.imshow("Face Capture", display_frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord(" "):
            if len(face_locations) == 0:
                print("No face detected. Try again.")
                continue

            if len(face_locations) > 1:
                print("More than one face detected. Make sure only one person is in frame.")
                continue

            encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            if len(encodings) != 1:
                print("Could not extract exactly one face encoding.")
                continue

            face_bytes = pickle.dumps(encodings[0])
            print("Face captured successfully.")
            break

        elif key == ord("q"):
            print("Face capture cancelled.")
            break

    picam2.stop()
    cv2.destroyAllWindows()
    return face_bytes