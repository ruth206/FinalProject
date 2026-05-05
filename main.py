import cv2 #used for drawing the rectangle and label on camera priview
import pickle #convert face encoding brom bytes to what python can understand
import face_recognition #detects face and compares them
import time #tracking how long camera has been running
import numpy as np #fixes camera frame format so face rec can read it
from picamera2 import Picamera2 #contolls pi camera
from db import get_active_card_owner, get_active_face #function from db to see who owns nfc and fetch there stored face
from gpiozero import LED # to control the lights 
# for pi to no what gpio led is connected to 
green_led = LED(27)
red_led =LED(17) 

THRESHOLD = 0.50
TIMEOUT   = 15 #camera timewaiting for face

def recognise_face(stored_encoding, threshold=THRESHOLD, timeout=TIMEOUT):
    """
    Opens the Pi camera, tries to match the live face against
    the stored encoding from the database.
    Returns True if matched, False if not.
    """
    picam2 = Picamera2() #creating camera object
    picam2.configure(picam2.create_preview_configuration(main={"size": (640, 480)})) #setting resolution
    picam2.start()
    print("Camera starting...")
    time.sleep(2) #starting camera and waiting 
    print("Look at the camera...")

    start_time = time.time()
    result = False #no match

    while time.time() - start_time < timeout: #keep trying untill timeout is reached
        frame = picam2.capture_array()
        if frame.shape[2] == 4:
            frame = frame[:, :, :3]
        frame = np.ascontiguousarray(frame)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_frame) #finding co-ordinets of face
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations) #converting detected face into numerical encoding

        #loop through each face founf in frame

        for (top, right, bottom, left), live_encoding in zip(face_locations, face_encodings):
            #KNN distance comparison against the stored encoding
            distance = face_recognition.face_distance([stored_encoding], live_encoding)[0]
            matched  = distance < threshold #if distance below threshold then match
            label    = "Access Granted" if matched else "Unknown"
            colour   = (0, 255, 0) if matched else (0, 0, 255) #green for match red for unknown

            cv2.rectangle(frame, (left, top), (right, bottom), colour, 2)
            cv2.putText(frame, f"{label} ({distance:.2f})", (left, top - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, colour, 2)

            if matched:
                green_led.on() #green light on for access granted
                time.sleep(3)
                green_led.off()
                picam2.stop()
                cv2.destroyAllWindows()
                return True

        cv2.imshow("Face Verification", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    #if here then no match was found

    picam2.stop()
    cv2.destroyAllWindows()
    red_led.on()
    time.sleep(3)
    red_led.off() #red light on for access denied 
    return result


def main():
    print("Please tap card...")

    #waiting for nfc card and get its id
    from nfc_reader import read_uid
    uid = read_uid()

    #if no card detected deny and stop
    if not uid:
        print("Access denied: no card detected.")
        return

    print(f"Card UID: {uid}")

    #look up who owns this card
    user = get_active_card_owner(uid)
    if not user:
        print("Access denied: unknown or inactive card.")
        return

    print(f"Card belongs to: {user['first_name']} {user['last_name']}")

    #load their face encoding from the database
    face_row = get_active_face(user["user_id"])
    if not face_row:
        print("Access denied: no face enrolled for this user.")
        return

    stored_encoding = pickle.loads(face_row["binary_face"])

    #run face recognition using KNN distance
    matched = recognise_face(stored_encoding)

    if matched:
        print(f"Access granted — welcome {user['first_name']} {user['last_name']}!")
        from db import log_access
        log_access(user["user_id"], uid, "NFC+Face", "granted")
    else:
        print("Access denied: face does not match card holder.")
        from db import log_access
        log_access(user["user_id"], uid, "NFC+Face", "denied")


if __name__ == "__main__":
    main()
