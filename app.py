from flask import Flask, request, url_for, redirect, render_template, jsonify, Response, session
from flask_bcrypt import Bcrypt #passworfd hashing 
from flask_limiter import Limiter #rate limiting
from flask_limiter.util import get_remote_address #gets ip address of person making request
from dotenv import load_dotenv
import threading
import time
import functools
import pickle
import os

load_dotenv()
print("PASSWORD_HASH loaded:", os.getenv("ADMIN_PASSWORD_HASH", "NOT FOUND"))

#creating flask app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback-secret-key")

#seeting up brcypt for password hashing
bcrypt  = Bcrypt(app)
limiter = Limiter(get_remote_address, app=app, default_limits=[])

#loading admin credentials not hardcoded
USERNAME      = os.getenv("ADMIN_USERNAME", "admin")
PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH", "")

enroll_sessions = {}
camera_busy     = False
shared_picam    = None

def login_required(f):
    #redirects to login page if user isint logged in
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return decorated

@app.route("/")
def login_page():
    return render_template("ht.html")

@app.route("/login", methods=["POST"])
@limiter.limit("5 per minute") #rate limiting 5 attempts per min for one ip to limit brute force attacks
def login():
    #login form submission 
    username = request.form["username"]
    password = request.form["password"]
    if username == USERNAME and bcrypt.check_password_hash(PASSWORD_HASH, password):
        session["logged_in"] = True
        return redirect(url_for("dashboard"))
    return render_template("ht.html", error="Invalid credentials")

@app.route("/logout")
#clears session sends user back to login
def logout():
    session.clear()
    return redirect(url_for("login_page"))

@app.route("/dashboard")

@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/users")
@login_required
def users():
    return render_template("users.html")

@app.route("/enroll")
@login_required
def enroll_page():
    return render_template("enroll.html")

@app.route("/logs")
@login_required
def logs():
    return render_template("logs.html")

@app.route("/settings")
@login_required
def settings():
    return render_template("settings.html")

@app.route("/reports")
@login_required
def reports():
    return render_template("reports.html")

@app.route("/api/stats")
@login_required
def api_stats():
    from db import get_stats
    stats = get_stats()
    return jsonify(stats)
@app.route("/api/logs")
@login_required
def api_logs():
    from db import get_access_logs
    logs = get_access_logs()
    return jsonify(logs)

@app.route("/api/users")
@login_required
def api_users():
    from db import get_all_users
    users = get_all_users()
    return jsonify(users)

def generate_frames():
    #continulessly captures frames and streams them to the browser as MJPEG
    global camera_busy, shared_picam
    #try to use the pi camera first 
    try:
        import cv2
        try:
            from picamera2 import Picamera2
            shared_picam = Picamera2()
            shared_picam.configure(shared_picam.create_preview_configuration(main={"size": (640, 480)}))
            shared_picam.start()
            time.sleep(1)
            use_picamera = True
        except Exception:
            #if pi camera not working fall back to usb webcam
            use_picamera = False
            cap = cv2.VideoCapture(0)

        while True:
            if camera_busy:
                #ifwhilst face capture is in progress pause streaming to avoid conflict 
                time.sleep(0.1)
                continue
            if use_picamera:
                frame = shared_picam.capture_array()
                if frame.shape[2] == 4:
                    frame = frame[:, :, :3]
            else:
                ret, frame = cap.read()
                if not ret:
                    break
            ret, buffer = cv2.imencode(".jpg", frame)
            if not ret:
                continue
            #yeild frame in MJPEG so browser can display it as live stream
            yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n")
            time.sleep(0.05)
    except Exception as e:
        print(f"Camera stream error: {e}")

@app.route("/camera_feed")
@login_required
def camera_feed():
    #streams live camera feed to browser
    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/enroll/scan_nfc", methods=["POST"])
@login_required
def enroll_scan_nfc():
    data = request.get_json()
    session_id = data.get("session_id")
    if session_id not in enroll_sessions:
        enroll_sessions[session_id] = {}
    enroll_sessions[session_id]["nfc_status"] = "scanning"
    enroll_sessions[session_id]["uid"] = None

    def scan():
        #runs in a seperate thread waits for a card tap and stores the uid when found
        try:
            from nfc_reader import read_uid
            uid = read_uid()
            if uid:
                enroll_sessions[session_id]["uid"] = uid
                enroll_sessions[session_id]["nfc_status"] = "done"
            else:
                enroll_sessions[session_id]["nfc_status"] = "error"
        except Exception as e:
            enroll_sessions[session_id]["nfc_status"] = "error"
            print(f"NFC error: {e}")

    t = threading.Thread(target=scan)
    t.daemon = True
    t.start()
    return jsonify({"ok": True})

@app.route("/enroll/nfc_status/<session_id>")
@login_required
def nfc_status(session_id):
    s = enroll_sessions.get(session_id, {})
    return jsonify({"status": s.get("nfc_status", "waiting"), "uid": s.get("uid")})

@app.route("/enroll/capture_face", methods=["POST"])
@login_required
def capture_face():
    #pauses live stream and captures face from camera
    global camera_busy, shared_picam
    data = request.get_json()
    session_id = data.get("session_id")
    if session_id not in enroll_sessions:
        return jsonify({"ok": False, "message": "Session not found."})
    if shared_picam is None:
        return jsonify({"ok": False, "message": "Camera not ready yet."})
    try:
        import cv2
        import face_recognition
        camera_busy = True
        time.sleep(0.3)
        encoding = None
        #try up to 15 times 
        for _ in range(15):
            frame = shared_picam.capture_array()
            if frame.shape[2] == 4:
                frame = frame[:, :, :3]
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            locations = face_recognition.face_locations(rgb)
            encodings = face_recognition.face_encodings(rgb, locations)
            #only except frame if exactly one face is detectecd
            if len(encodings) == 1:
                encoding = encodings[0]
                break
            time.sleep(0.3)
    except Exception as e:
        camera_busy = False
        return jsonify({"ok": False, "message": f"Capture error: {str(e)}"})
    finally:
        camera_busy = False
    if encoding is None:
        return jsonify({"ok": False, "message": "No face detected. Make sure your face is clearly visible and try again."})
    enroll_sessions[session_id]["face_bytes"] = pickle.dumps(encoding)
    return jsonify({"ok": True, "message": "Face captured successfully."})

@app.route("/enroll/save", methods=["POST"])
@login_required
def enroll_save():
    #saves the enrollment 
    data       = request.get_json()
    session_id = data.get("session_id")
    first_name = data.get("first_name", "").strip()
    last_name  = data.get("last_name", "").strip()
    email      = data.get("email", "").strip().lower()
    role       = data.get("role", "user").strip().lower()
    s          = enroll_sessions.get(session_id, {})
    uid        = s.get("uid")
    face_bytes = s.get("face_bytes")
    if not uid:
        return jsonify({"ok": False, "message": "No NFC card scanned."})
    if not face_bytes:
        return jsonify({"ok": False, "message": "No face captured."})
    try:
        from db import (create_user, get_user_by_email, deactivate_cards,
                        assign_card, deactivate_faces, save_face)
        user = get_user_by_email(email)
        user_id = user["user_id"] if user else create_user(first_name, last_name, email, role)
        deactivate_cards(user_id)
        assign_card(user_id, uid)
        deactivate_faces(user_id)
        save_face(user_id, face_bytes, "face_ai_recognition_v1")
        del enroll_sessions[session_id]
        return jsonify({"ok": True, "message": "Enrollment complete!"})
    except Exception as e:
        return jsonify({"ok": False, "message": f"Save error: {str(e)}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
