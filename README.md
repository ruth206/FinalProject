BioAccess - Biometric Door Access Control System 

A low-cost two-factor biometric access control system built on a Raspberry Pi 5,
combining NFC smart card authentication with face recognition to provide multi-factor physical security.

Overview

BioAccess requires users to present both a registered NFC card and a matching face 
before access is granted. Neither factor alone is sufficient. All access attempts are logged 
to a cloud database and viewable through a secure web administration dashboard accessible from anywhere 
in the world.


Features

- Two-factor authentication — NFC card + face recognition
- KNN face recognition using 128-dimensional face encodings
- Real-time access logging to Supabase PostgreSQL
- Secure web admin dashboard built with Flask
- Live camera stream on the enrollment page
- User enrollment, management, and card deactivation
- Remote access via ngrok tunnel (bioaccess.ngrok.app)
- bcrypt password hashing, rate limiting, and Row-Level Security
- Green/red LED indicators for access granted/denied

Hardware 

- Raspberry Pi 5
- ACR122U USB NFC Reader
- Raspberry Pi Camera Module
- NFC Smart Cards (AES/3DES encrypted)
- Green and Red LEDs wired to GPIO pins 27 and 17

Setup 

1. Clone the repository

git clone https://github.com/ruth206/FinalProject.git
cd FinalProject

2. Create Virtual enviorement

python3 -m venv --system-site-packages pn532-env
source pn532-env/bin/activate

The --system-site-packages flag is required so that libcamera and picamera,
which must be installed at OS level, are accessible inside the virtual enviorement.

3. pip install flask flask-bcrypt flask-limiter psycopg2-binary python-dotenv face-recognition opencv-python pyscard gpiozero

4. create a .env file
Create .env file in the project root with the following

DB_CONNECTION=your_supabase_connection_string
SECRET_KEY=your_flask_secret_key
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=your_bcrypt_hash

5. Run the flask dashboard

python app.py

6. Run the door access system

Security 

- All dashboard traffic encrypted via HTTPS through ngrok tunnel
- Passwords stored as bcrypt hashes — never in plaintext
- Login endpoint rate limited to 5 attempts per minute
- Row-Level Security enabled on all Supabase tables
- All credentials stored in .env file — excluded from version control
- Parameterised SQL queries throughout to prevent injection attacks
- Face data stored as mathematical encodings, not images

Technologies Used  

| Technologies | Purpose |
|--------------|---------|
| Python 3.13 | Main programming language |
| Flask | Web administration dashboard |
| face_recogntion | KNN face encoding and comparison |
| Picamera2 | Raspberry Pi camera control |
| psycopg2 | PostgreSQL database connection |
| Supabase | Cloud PostgreSQL database |
| pyscard | NFC card reading via ACR122U |
| ngrok | Secure remote access tunnel |
| bcrypt | Password hashing |
| gpiozero | GPIO LED control |

Author 

Ruth Robinson - COMP3000 Final Year Project 2025/26


   
