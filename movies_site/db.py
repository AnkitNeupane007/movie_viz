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
    
def create_user(role, email, username, hashed_password):
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO users (role, email, username, password)
        VALUES (?, ?, ?, ?)
    """, (role, email, username, hashed_password))
    
    conn.commit()
    conn.close()
    
def check_admin():
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM users WHERE role = "admin"')
    
    result = cursor.fetchone()
    conn.close()
    
    return result[0]

def get_all_users():
    
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT username, email, role FROM users WHERE role != "admin"')
        
    users = cursor.fetchall()

    # get all the users in a dictionary format
    users = [dict(user) for user in users]
    
    conn.close()
    
    return users

def delete_user_from_database(email):
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM users WHERE email = ?', (email, ))
    
    conn.commit()
    conn.close()
    
def update_user_in_database(email, new_username):
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('UPDATE users SET  username = ? WHERE email = ?', (new_username, email))
    
    conn.commit()
    conn.close()
            
def update_review(reviewer_rating, movie):
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
    UPDATE reviews
    SET 
        rating = rating + (? / CASE WHEN vote_count = 0 THEN 1 ELSE vote_count END),
        vote_count = vote_count + 1
    WHERE 
        movie_id = (SELECT id FROM movies WHERE LOWER(title) = LOWER(?))
    ''', (reviewer_rating, movie))
    
    conn.commit()
    
def check_movie(movie):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id FROM movies WHERE LOWER(title) = LOWER(?)', (movie,))
    
    movie_id = cursor.fetchone()
    
    return movie_id

def search_movies(movie):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT title FROM movies WHERE title LIKE ? ORDER BY title ASC LIMIT 8', (f'{movie}%', ))
    
    movies = cursor.fetchall()
    
    if not movies:
        cursor.execute('SELECT title FROM movies WHERE title LIKE ? LIMIT 8', (f'%{movie}%', ))
        movies = cursor.fetchall()
    
    return movies

def display_movie(movie_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
    SELECT 
    m.title, 
    m.release_date, 
    m.runtime, 
    m.tagline, 
    m.overview, 
    m.budget, 
    m.revenue, 
    m.original_language, 
    d.name AS director, 
    p.name AS production_company, 
    r.rating AS rating,
    -- Subquery to ensure distinct genres
    (SELECT GROUP_CONCAT(g.name, ', ')
     FROM movie_genres mg
     JOIN genres g ON mg.genre_id = g.id
     WHERE mg.movie_id = m.id) AS genres,
    -- Subquery to ensure distinct actors
    (SELECT GROUP_CONCAT(a.name, ', ')
     FROM movie_cast ma
     JOIN actors a ON ma.actor_id = a.id
     WHERE ma.movie_id = m.id) AS actors
    FROM 
        movies m
    JOIN 
        directors d ON m.director_id = d.id
    JOIN 
        production_companies p ON m.production_company_id = p.id
    LEFT JOIN 
        reviews r ON r.movie_id = m.id
    WHERE 
        m.id = ? 
    GROUP BY 
        m.id, m.title, m.release_date, m.runtime, m.tagline, m.overview, m.budget, m.revenue, m.original_language, d.name, p.name, r.rating;
    ''', (movie_id, ))
    
    movie_information = cursor.fetchall()
    
    return movie_information