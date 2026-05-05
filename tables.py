# import sqlite3

# conn = sqlite3.connect('database.db') #creating a new database if one doesnmt exist
# N = conn.cursor() # coNn connection to database and cursor pointer to send sql commands
# N.execute("PRAGMA foreign_keys = ON;") #Enforcing foreign keys


# N.execute("DROP TABLE IF EXISTS users")

# N.execute("""
#     CREATE TABLE users(
#     user_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     first_Name TEXT NOT NULL,
#     last_Name TEXT NOT NULL,
#     email TEXT NOT NULL,
#     role TEXT NOT NULL 'user',
#     created TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
#     );
# """)
# #USER_ID USER IDENTIFIYER LINKS TO FACE ID NFC CARD AND ACCESS LO9GS


# N.execute("DROP TABLE IF EXISTS face")

# N.execute("""
#     CREATE TABLE face(
#     face_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     user_id INTEGER NOT NULL,
#     binary_face BLOB NOT NULL,
#     ai_model TEXT,
#     created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     is_active INTEGER DEFAULT 1,
#     FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE


#     );
# """)
# #cascade means delete from everywear

# #access logs for security and reporting

# N.execute("DROP TABLE IF EXISTS access_logs")

# N.execute("""
#     CREATE TABLE access_logs (
#     log_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     user_id INTEGER,
#     nfc_uid TEXT,
#     method TEXT NOT NULL,
#     result TEXT NOT NULL,
#     created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     FOREIGN KEY (user_id) REFERENCES users(user_id)

#     );

# """)

# N.execute("DROP TABLE IF EXISTS cards")

# N.execute("""
#     CREATE TABLE cards (
#     card_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     user_id INTEGER NOT NULL,
#     nfc_user_id TEXT NOT NULL UNIQUE,
#     is_active INTEGER DEFAULT 1,
#     issue_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     finished_at TIMESTAMP,
#     FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE

#     );
# """)

# N.execute("DROP TABLE IF EXISTS reader_door")

# N.execute("""
#     CREATE TABLE reader_door (
#     reader_id INTEGER PRIMARY KEY AUTOINCREMENT,
#     reader_name TEXT NOT NULL,
#     location TEXT,
#     created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#     );
# """)




# conn.commit()
# conn.close()
# print("tables done")

import sqlite3
#from contetxlib import closing
from datetime import datetime #timestamps for debugging

conn = sqlite3.connect("database.db")
N = conn.cursor()

N.execute("PRAGMA foreign_keys = ON;")

# Drop child tables first
N.execute("DROP TABLE IF EXISTS face;")
N.execute("DROP TABLE IF EXISTS access_logs;")
N.execute("DROP TABLE IF EXISTS cards;")
N.execute("DROP TABLE IF EXISTS reader_door;")
N.execute("DROP TABLE IF EXISTS users;")

N.execute("""
CREATE TABLE users(
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL DEFAULT 'user',
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

N.execute("""
CREATE TABLE face(
    face_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    binary_face BLOB NOT NULL,
    ai_model TEXT,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active INTEGER DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
""")

N.execute("""
CREATE TABLE cards(
    card_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    nfc_uid TEXT NOT NULL UNIQUE,
    is_active INTEGER DEFAULT 1,
    issue_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
""")

N.execute("""
CREATE TABLE reader_door(
    reader_id INTEGER PRIMARY KEY AUTOINCREMENT,
    reader_name TEXT NOT NULL,
    location TEXT,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

N.execute("""
CREATE TABLE access_logs(
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    nfc_uid TEXT,
    method TEXT NOT NULL,
    result TEXT NOT NULL,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
""")

conn.commit()
conn.close()
print(" tables done")
