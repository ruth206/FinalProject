import os
import pickle
import face_recognition
from sklearn.neighbors import KNeighborsClassifier

DATASET_DIR = "dataset"
MODEL_PATH = "models/face_knn.pkl"

X = []
y = []

print("Scanning dataset...")

for person_name in os.listdir(DATASET_DIR):
    person_dir = os.path.join(DATASET_DIR, person_name)

    if not os.path.isdir(person_dir):
        continue

    for image_name in os.listdir(person_dir):
        image_path = os.path.join(person_dir, image_name)

        try:
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)

            if len(encodings) == 1:
                X.append(encodings[0])
                y.append(person_name)
                print(f"Added: {image_path}")
            else:
                print(f"Skipped {image_path} (found {len(encodings)} faces)")
        except Exception as e:
            print(f"Error processing {image_path}: {e}")

if not X:
    print("No training data found.")
    exit()

print("Training KNN model...")

knn = KNeighborsClassifier(n_neighbors=3)
knn.fit(X, y)

os.makedirs("models", exist_ok=True)

with open(MODEL_PATH, "wb") as f:
    pickle.dump(knn, f)

print(f"Model saved to {MODEL_PATH}")