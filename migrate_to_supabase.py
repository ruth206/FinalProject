import psycopg2

CONNECTION = "postgresql://postgres.jwcpdrchnrkjqvwnybrg:Air*)cULT&&ur£!!4@aws-1-eu-west-2.pooler.supabase.com:5432/postgres"

def migrate():
    print("Connecting to Supabase...")
    conn = psycopg2.connect(CONNECTION)
    cur = conn.cursor()
    print("Creating tables...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id    SERIAL PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name  TEXT NOT NULL,
            email      TEXT NOT NULL UNIQUE,
            role       TEXT NOT NULL DEFAULT 'user',
            created    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS face (
            face_id     SERIAL PRIMARY KEY,
            user_id     INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
            binary_face BYTEA NOT NULL,
            ai_model    TEXT,
            created     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active   INTEGER DEFAULT 1
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cards (
            card_id     SERIAL PRIMARY KEY,
            user_id     INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
            nfc_uid     TEXT NOT NULL UNIQUE,
            is_active   INTEGER DEFAULT 1,
            issue_date  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            finished_at TIMESTAMP
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reader_door (
            reader_id   SERIAL PRIMARY KEY,
            reader_name TEXT NOT NULL,
            location    TEXT,
            created     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS access_logs (
            log_id  SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(user_id),
            nfc_uid TEXT,
            method  TEXT NOT NULL,
            result  TEXT NOT NULL,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("All tables created successfully in Supabase!")

if __name__ == "__main__":
    migrate()
    
