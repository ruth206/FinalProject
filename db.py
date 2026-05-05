import psycopg2 #handles connections and quieries
import psycopg2.extras #retuns rows as dictionaries 
import os #to read enviorement vaiables
from dotenv import load_dotenv #loads .env file
load_dotenv() #read .env file making variables availible 
CONNECTION = os.getenv("DB_CONNECTION") #keeps credentials out of the code 

def get_conn():
    #opens and returns new connection to supabase postsql database
    conn = psycopg2.connect(CONNECTION)
    return conn

def create_user(first_name, last_name, email, role="user"):
    #insert a new user into users table and returnjs generated id
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO users (first_name, last_name, email, role)
            VALUES (%s, %s, %s, %s)
            RETURNING user_id
        """, (first_name, last_name, email, role))
        user_id = cur.fetchone()[0] #get users id
        conn.commit() #save changes
        return user_id

def get_user_by_email(email):
    #looks up new user from email address and returns full record as a dictionary
    with get_conn() as conn:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        return cur.fetchone()

def get_user_by_id(user_id):
    #looks up user by user_id and returns record
    with get_conn() as conn:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        return cur.fetchone()

def get_all_users():
    #return all users
    with get_conn() as conn:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM users ORDER BY created DESC")
        return cur.fetchall()

def deactivate_cards(user_id):
    #marking active cards for a user as inactive
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE cards
            SET is_active = 0, finished_at = CURRENT_TIMESTAMP
            WHERE user_id = %s AND is_active = 1
        """, (user_id,))
        conn.commit()

def assign_card(user_id, nfc_uid):
    #assigning a new card to a user 
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO cards (user_id, nfc_uid, is_active)
            VALUES (%s, %s, 1)
            RETURNING card_id
        """, (user_id, nfc_uid.upper()))
        card_id = cur.fetchone()[0]
        conn.commit()
        return card_id

def get_active_card_owner(nfc_uid):
    #returning users record from the nfc card uid
    with get_conn() as conn:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT users.*
            FROM cards
            JOIN users ON cards.user_id = users.user_id
            WHERE cards.nfc_uid = %s AND cards.is_active = 1
        """, (nfc_uid.upper(),))
        return cur.fetchone()

def deactivate_faces(user_id):
    #marking active face encoding as inactive
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE face
            SET is_active = 0
            WHERE user_id = %s AND is_active = 1
        """, (user_id,))
        conn.commit()

def save_face(user_id, binary_face, ai_model):
    #saves a new face to the database for a user
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO face (user_id, binary_face, ai_model, is_active)
            VALUES (%s, %s, %s, 1)
            RETURNING face_id
        """, (user_id, psycopg2.Binary(binary_face), ai_model))
        face_id = cur.fetchone()[0]
        conn.commit()
        return face_id

def get_active_face(user_id):
    #gets most recent enrolled face for a user
    with get_conn() as conn:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT * FROM face
            WHERE user_id = %s AND is_active = 1
            ORDER BY face_id DESC
            LIMIT 1
        """, (user_id,))
        return cur.fetchone()

def log_access(user_id, nfc_uid, method, result, reader_id=1):
    #records access attempts
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO access_logs (user_id, nfc_uid, method, result, reader_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, nfc_uid, method, result, reader_id))
        conn.commit()

def get_access_logs(limit=50):
    #returns most recent log entries for dashboard display
    with get_conn() as conn:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT access_logs.*, users.first_name, users.last_name
            FROM access_logs
            LEFT JOIN users ON access_logs.user_id = users.user_id
            ORDER BY access_logs.created DESC
            LIMIT %s
        """, (limit,))
        return cur.fetchall()

def get_stats():
    #returns all 4 statistics for the dashboard 
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users")
        user_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM cards WHERE is_active = 1")
        card_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM access_logs WHERE result = 'granted' AND created::date = CURRENT_DATE")
        access_today = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM access_logs WHERE result = 'denied' AND created::date = CURRENT_DATE")
        denied_today = cur.fetchone()[0]
        return {
            "user_count":   user_count,
            "card_count":   card_count,
            "access_today": access_today,
            "denied_today": denied_today
        }