import mysql.connector
import os
from dotenv import load_dotenv
import bcrypt

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME", "tipchatbotdb")

def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME
    )

def create_user(username, password):
    con = get_connection()
    cur = con.cursor()

    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    try:
        cur.execute(
            "INSERT INTO users (username, password_hash, credits, name) VALUES (%s, %s, %s, %s)",
            (username, pw_hash.decode(), 0, username)
        )
        con.commit()
        return True
    except mysql.connector.Error:
        return False
    finally:
        con.close()


def authenticate_user(username, password):
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT password_hash FROM users WHERE username = %s", (username,))
    row = cur.fetchone()
    con.close()

    if not row:
        return False

    saved_hash = row[0].encode()
    return bcrypt.checkpw(password.encode(), saved_hash)

def get_credits(username):
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT credits FROM users WHERE username = %s", (username,))
    row = cur.fetchone()
    con.close()
    return row[0] if row else 0

def set_credits(username, new_credits):
    con = get_connection()
    cur = con.cursor()
    cur.execute("UPDATE users SET credits = %s WHERE username = %s", (new_credits, username))
    con.commit()
    con.close()

def add_credits(username, amount):
    con = get_connection()
    cur = con.cursor()
    cur.execute("UPDATE users SET credits = credits + %s WHERE username = %s", (amount, username))
    con.commit()
    con.close()

def create_transaction(username, stripe_session_id, credits, amount_cents, currency, status="pending"):
    con = get_connection()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO transactions (username, stripe_session_id, credits, amount_cents, currency, status) VALUES (%s,%s,%s,%s,%s,%s)",
        (username, stripe_session_id, credits, amount_cents, currency, status)
    )
    con.commit()
    con.close()

def update_transaction_status(stripe_session_id, status):
    con = get_connection()
    cur = con.cursor()
    cur.execute("UPDATE transactions SET status = %s WHERE stripe_session_id = %s", (status, stripe_session_id))
    con.commit()
    con.close()