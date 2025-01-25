import sqlite3
from flask import current_app

def get_db():
    db = sqlite3.connect(current_app.config['DATABASE'])
    return db


def get_password(email):

    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT password FROM users WHERE email = ?', (email, ))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return result[0]
    else:
        return None
        

def get_role(email):
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT role FROM users WHERE email = ?', (email, ))
    
    result = cursor.fetchone()
    conn.close()

    if result:
        return result[0]
    else:
        return None
            