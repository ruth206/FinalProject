import os
import cv2
import time
import numpy as np
from picamera2 import Picamera2

first_name = input("First name: ").strip().lower()
last_name = input("Last name: ").strip().lower()

person_name = f"{first_name}_{last_name}"
save_dir = os.path.join("dataset", person_name)
os.makedirs(save_dir, exist_ok=True)

# Find next file number so we don't overwrite old images
existing_files = [f for f in os.listdir(save_dir) if f.endswith(".jpg")]
if existing_files:
    numbers = []
    for f in existing_files:
        try:
            numbers.append(int(os.path.splitext(f)[0]))
        except ValueError:
            pass
    count = max(numbers) + 1 if numbers else 0
else:
    count = 0

max_new_images = 25

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"size": (640, 480)}))
picam2.start()

print("Camera starting...")
time.sleep(3)

print(f"Saving images to: {save_dir}")
print(f"Starting from image number: {count:03d}")
print("Press SPACE to save an image.")
print("Press Q to quit.")

saved_this_session = 0

while True:
    frame = picam2.capture_array()

    if frame.shape[2] == 4:
        frame = frame[:, :, :3]

    frame = np.ascontiguousarray(frame)

    display = frame.copy()

    text = f"Saved this session: {saved_this_session}/{max_new_images}"
    cv2.putText(display, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    cv2.imshow("Dataset Capture", display)
    key = cv2.waitKey(1) & 0xFF

    if key == ord(" "):
        filename = os.path.join(save_dir, f"{count:03d}.jpg")
        cv2.imwrite(filename, frame)
        print(f"Saved {filename}")
        count += 1
        saved_this_session += 1

        if saved_this_session >= max_new_images:
            print("Finished capturing images.")
            break

    elif key == ord("q"):
        print("Capture stopped.")
        break

picam2.stop()
cv2.destroyAllWindows()