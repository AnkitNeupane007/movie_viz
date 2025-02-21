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

def search_actors(actor):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT name FROM actors WHERE name LIKE ? ORDER BY name ASC LIMIT 8', (f'{actor}%', ))
    
    actors = cursor.fetchall()
    
    if not actors:
        cursor.execute('SELECT name FROM actors WHERE name LIKE ? LIMIT 8', (f'%{actor}%', ))
        actors = cursor.fetchall()
        
    return actors

def search_directors(director):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT name FROM directors WHERE name LIKE ? ORDER BY name ASC LIMIT 8', (f'{director}%', ))
    
    directors = cursor.fetchall()
    
    if not directors:
        cursor.execute('SELECT name FROM directors WHERE name LIKE ? LIMIT 8', (f'%{director}%', ))
        directors = cursor.fetchall()
        
    return directors

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
    
    # Fetch results
    movie_information = cursor.fetchone()

    # Convert to dictionary
    if movie_information:
        columns = [desc[0] for desc in cursor.description]
        movie_information = dict(zip(columns, movie_information))
    
    return movie_information

def insert_movie_data(
    title,
    release_date,
    runtime,
    tagline,
    overview,
    budget,
    revenue,
    original_language,
    director_name,
    production_company_name,
    production_company_country,
    cast_list,
    genre_list
):
    # Connect to the database
    conn = get_db()
    cursor = conn.cursor()

    try:
        # Insert or get director ID
        cursor.execute("INSERT OR IGNORE INTO directors (name) VALUES (?)", (director_name,))
        cursor.execute("SELECT id FROM directors WHERE name = ?", (director_name,))
        director_id = cursor.fetchone()[0]

        # Insert or get production company ID
        cursor.execute("INSERT OR IGNORE INTO production_companies (name, country) VALUES (?, ?)", (production_company_name, production_company_country),)
        cursor.execute("SELECT id FROM production_companies WHERE name = ?", (production_company_name,))
        production_company_id = cursor.fetchone()[0]

        # Insert movie data
        cursor.execute(
            """
            INSERT INTO movies 
            (
                title, release_date, runtime, tagline, overview, budget, revenue, original_language, director_id, production_company_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                title,
                release_date,
                runtime,
                tagline,
                overview,
                budget,
                revenue,
                original_language,
                director_id,
                production_company_id,
            ),
        )
        movie_id = cursor.lastrowid

        # Insert cast data
        for actor_name in cast_list.split(","):
            actor_name = actor_name.strip()
            cursor.execute("INSERT OR IGNORE INTO actors (name) VALUES (?)", (actor_name,))
            cursor.execute("SELECT id FROM actors WHERE name = ?", (actor_name,))
            actor_id = cursor.fetchone()[0]
            cursor.execute("INSERT INTO movie_cast (movie_id, actor_id) VALUES (?, ?)", (movie_id, actor_id))

        # Insert genre data
        for genre_name in genre_list.split(","):
            genre_name = genre_name.strip()
            cursor.execute("INSERT OR IGNORE INTO genres (name) VALUES (?)", (genre_name,))
            cursor.execute("SELECT id FROM genres WHERE name = ?", (genre_name,))
            genre_id = cursor.fetchone()[0]
            cursor.execute("INSERT INTO movie_genres (movie_id, genre_id) VALUES (?, ?)", (movie_id, genre_id))

        # Insert review data with default values
        cursor.execute("INSERT INTO reviews (movie_id, rating, vote_count) VALUES (?, 0, 0)", (movie_id,),)

        # Commit changes
        conn.commit()
        # print("Movie data inserted successfully.")

    except sqlite3.Error as e:
        conn.rollback()
        print(f"An error occurred: {e}")

    conn.close()

# # Example usage
# insert_movie_data(
#     db_path="movies.db",
#     title="Knives Out",
#     release_date="2019-11-27",
#     runtime=130,
#     tagline="Hell, any of them could have done it.",
#     overview="When renowned crime novelist Harlan Thrombey is found dead at his estate just after his 85th birthday, the inquisitive and debonair Detective Benoit Blanc is mysteriously enlisted to investigate. From Harlan's dysfunctional family to his devoted staff, Blanc sifts through a web of red herrings and self-serving lies to uncover the truth behind Harlan's untimely death.",
#     budget=40000000,
#     revenue=311400000,
#     original_language="en",
#     director_name="Rian Johnson",
#     production_company_name="Lionsgate",
#     production_company_country="USA",
#     cast_list="Daniel Craig, Chris Evans, Ana de Armas, Jamie Lee Curtis, Michael Shannon",
#     genre_list="Comedy, Crime, Drama"
# )

def get_genres():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT name FROM genres ORDER BY name ASC')
    
    genres = cursor.fetchall()
    
    return genres

def get_rating_per_genre(genre):
    
    conn = sqlite3.connect("instance/movies.db")
    cursor = conn.cursor()
    
    cursor.execute(''' 
                SELECT g.name AS genre, AVG(r.rating) AS avg_rating
                FROM movies m
                JOIN movie_genres mg ON m.id = mg.movie_id
                JOIN genres g ON mg.genre_id = g.id
                JOIN reviews r ON m.id = r.movie_id
                WHERE LOWER(g.name) = LOWER(?)
                GROUP BY g.name;
                   ''', (genre,))
    
    result = cursor.fetchone()
    
    return result[1] if result else None

