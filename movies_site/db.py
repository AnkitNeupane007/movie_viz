import sqlite3
from flask import current_app

def get_db():
    conn = sqlite3.connect(current_app.config['DATABASE'])
    return conn


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
        
def get_user_username(email):
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT username FROM users WHERE email = ?', (email, ))
    
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
    conn.close()
    
def check_movie(movie):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id FROM movies WHERE LOWER(title) = LOWER(?)', (movie,))
    
    movie_id = cursor.fetchone()
    conn.close()
    
    return movie_id

def search_movies(movie):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT title FROM movies WHERE title LIKE ? ORDER BY title ASC LIMIT 8', (f'{movie}%', ))
    
    movies = cursor.fetchall()
    
    if not movies:
        cursor.execute('SELECT title FROM movies WHERE title LIKE ? LIMIT 8', (f'%{movie}%', ))
        movies = cursor.fetchall()
        
    conn.close()
    
    return movies

def search_actors(actor):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT name FROM actors WHERE name LIKE ? ORDER BY name ASC LIMIT 8', (f'{actor}%', ))
    
    actors = cursor.fetchall()
    
    if not actors:
        cursor.execute('SELECT name FROM actors WHERE name LIKE ? LIMIT 8', (f'%{actor}%', ))
        actors = cursor.fetchall()
        
    conn.close()
        
    return actors

def search_directors(director):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT name FROM directors WHERE name LIKE ? ORDER BY name ASC LIMIT 8', (f'{director}%', ))
    
    directors = cursor.fetchall()
    
    if not directors:
        cursor.execute('SELECT name FROM directors WHERE name LIKE ? LIMIT 8', (f'%{director}%', ))
        directors = cursor.fetchall()
        
    conn.close()
        
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
    
    conn.close()

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



def get_genres():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT name FROM genres ORDER BY name ASC')
    
    genres = cursor.fetchall()
    conn.close()
    
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
    
    conn.close()
    
    return result[1] if result else None

def check_actor(actor):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id FROM actors WHERE LOWER(name) = LOWER(?)', (actor,))
    
    actor_id = cursor.fetchone()
    conn.close()
    
    return actor_id

def get_actor_info(actor):
    conn = get_db()
    cursor = conn.cursor()

    try:
        # Get the actor's ID based on their name
        cursor.execute("SELECT id FROM actors WHERE LOWER(name) = LOWER(?)", (actor,))
        actor_id = cursor.fetchone()

        if not actor_id:
            return {"error": "Actor not found"}

        actor_id = actor_id[0]

        # Total number of movies the actor appeared in
        cursor.execute('''
            SELECT COUNT(*) FROM movie_cast
            JOIN movies ON movie_cast.movie_id = movies.id
            WHERE movie_cast.actor_id = ?
        ''', (actor_id,))
        total_movies = cursor.fetchone()[0]

        # Number of "hits" (rating > 7)
        cursor.execute('''
            SELECT COUNT(*) FROM movie_cast
            JOIN movies ON movie_cast.movie_id = movies.id
            JOIN reviews ON movies.id = reviews.movie_id
            WHERE movie_cast.actor_id = ? AND reviews.rating > 7
        ''', (actor_id,))
        hits = cursor.fetchone()[0]

        # Number of "super hits" (rating > 9)
        cursor.execute('''
            SELECT COUNT(*) FROM movie_cast
            JOIN movies ON movie_cast.movie_id = movies.id
            JOIN reviews ON movies.id = reviews.movie_id
            WHERE movie_cast.actor_id = ? AND reviews.rating > 9
        ''', (actor_id,))
        super_hits = cursor.fetchone()[0]

        # Number of "flops" (rating < 5)
        cursor.execute('''
            SELECT COUNT(*) FROM movie_cast
            JOIN movies ON movie_cast.movie_id = movies.id
            JOIN reviews ON movies.id = reviews.movie_id
            WHERE movie_cast.actor_id = ? AND reviews.rating < 5
        ''', (actor_id,))
        flops = cursor.fetchone()[0]

        # Most frequent genre the actor has appeared in
        cursor.execute('''
            SELECT genres.name, COUNT(*) AS genre_count
            FROM movie_cast
            JOIN movie_genres ON movie_cast.movie_id = movie_genres.movie_id
            JOIN genres ON movie_genres.genre_id = genres.id
            WHERE movie_cast.actor_id = ?
            GROUP BY genres.name
            ORDER BY genre_count DESC
            LIMIT 1
        ''', (actor_id,))
        most_frequent_genre = cursor.fetchone()

        if most_frequent_genre:
            genre_name = most_frequent_genre[0]
            genre_count = most_frequent_genre[1]
        else:
            genre_name = "Unknown"
            genre_count = 0

        # Average rating of the actor's movies
        cursor.execute('''
            SELECT AVG(reviews.rating) FROM movie_cast
            JOIN movies ON movie_cast.movie_id = movies.id
            JOIN reviews ON movies.id = reviews.movie_id
            WHERE movie_cast.actor_id = ?
        ''', (actor_id,))
        avg_rating = cursor.fetchone()[0]

        # Most frequent cast member the actor has appeared with
        cursor.execute('''
            SELECT actors.name, COUNT(*) AS coactor_count
            FROM movie_cast
            JOIN movie_cast AS coactor_cast ON movie_cast.movie_id = coactor_cast.movie_id
            JOIN actors ON coactor_cast.actor_id = actors.id
            WHERE movie_cast.actor_id = ? AND actors.id != movie_cast.actor_id
            GROUP BY actors.name
            ORDER BY coactor_count DESC
            LIMIT 1
        ''', (actor_id,))
        most_frequent_coactor = cursor.fetchone()

        if most_frequent_coactor:
            coactor_name = most_frequent_coactor[0]
            coactor_count = most_frequent_coactor[1]
        else:
            coactor_name = "No co-actors found"
            coactor_count = 0

        # Most frequent production company the actor has worked with
        cursor.execute('''
            SELECT production_companies.name, COUNT(*) AS company_count
            FROM movie_cast
            JOIN movies ON movie_cast.movie_id = movies.id
            JOIN production_companies ON movies.production_company_id = production_companies.id
            WHERE movie_cast.actor_id = ?
            GROUP BY production_companies.name
            ORDER BY company_count DESC
            LIMIT 1
        ''', (actor_id,))
        most_frequent_company = cursor.fetchone()

        if most_frequent_company:
            company_name = most_frequent_company[0]
            company_count = most_frequent_company[1]
        else:
            company_name = "No production company found"
            company_count = 0

        # Most frequent director the actor has worked with
        cursor.execute('''
            SELECT directors.name, COUNT(*) AS director_count
            FROM movie_cast
            JOIN movies ON movie_cast.movie_id = movies.id
            JOIN directors ON movies.director_id = directors.id
            WHERE movie_cast.actor_id = ?
            GROUP BY directors.name
            ORDER BY director_count DESC
            LIMIT 1
        ''', (actor_id,))
        most_frequent_director = cursor.fetchone()

        if most_frequent_director:
            director_name = most_frequent_director[0]
            director_count = most_frequent_director[1]
        else:
            director_name = "No director found"
            director_count = 0

        # Best rated movie (highest rating)
        cursor.execute('''
            SELECT movies.title, MAX(reviews.rating) 
            FROM movie_cast
            JOIN movies ON movie_cast.movie_id = movies.id
            JOIN reviews ON movies.id = reviews.movie_id
            WHERE movie_cast.actor_id = ?
        ''', (actor_id,))
        best_movie = cursor.fetchone()
        best_movie_title = best_movie[0] if best_movie else "No best movie"
        best_movie_rating = best_movie[1] if best_movie else "N/A"

        # Worst rated movie (lowest rating)
        cursor.execute('''
            SELECT movies.title, MIN(reviews.rating) 
            FROM movie_cast
            JOIN movies ON movie_cast.movie_id = movies.id
            JOIN reviews ON movies.id = reviews.movie_id
            WHERE movie_cast.actor_id = ?
        ''', (actor_id,))
        worst_movie = cursor.fetchone()
        worst_movie_title = worst_movie[0] if worst_movie else "No worst movie"
        worst_movie_rating = worst_movie[1] if worst_movie else "N/A"

        # Return actor statistics
        return {
            "actor": actor,
            "total_movies": total_movies,
            "hits": hits,
            "super_hits": super_hits,
            "flops": flops,
            "most_frequent_genre": {
                "genre": genre_name,
                "count": genre_count
            },
            "avg_rating": avg_rating if avg_rating else "No ratings available",
            "most_frequent_coactor": {
                "actor": coactor_name,
                "count": coactor_count
            },
            "most_frequent_production_company": {
                "company": company_name,
                "count": company_count
            },
            "most_frequent_director": {
                "director": director_name,
                "count": director_count
            },
            "best_movie": {
                "title": best_movie_title,
                "rating": best_movie_rating
            },
            "worst_movie": {
                "title": worst_movie_title,
                "rating": worst_movie_rating
            }
        }

    except sqlite3.Error as e:
        return {"error": f"An error occurred: {e}"}

    finally:
        conn.close()
        
def check_director(director):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id FROM directors WHERE LOWER(name) = LOWER(?)', (director,))
    
    director_id = cursor.fetchone()
    conn.close()
    
    return director_id

def get_director_info(director):
    conn = get_db()
    cursor = conn.cursor()

    try:
        # Get the director's ID based on their name
        cursor.execute("SELECT id FROM directors WHERE LOWER(name) = LOWER(?)", (director,))
        director_id = cursor.fetchone()

        if not director_id:
            return {"error": "Director not found"}

        director_id = director_id[0]

        # Total number of movies the director has directed
        cursor.execute(''' 
            SELECT COUNT(*) FROM movies 
            WHERE director_id = ?
        ''', (director_id,))
        total_movies = cursor.fetchone()[0]

        # Number of "hits" (rating > 7)
        cursor.execute(''' 
            SELECT COUNT(*) FROM movies 
            JOIN reviews ON movies.id = reviews.movie_id
            WHERE movies.director_id = ? AND reviews.rating > 7
        ''', (director_id,))
        hits = cursor.fetchone()[0]

        # Number of "super hits" (rating > 9)
        cursor.execute(''' 
            SELECT COUNT(*) FROM movies 
            JOIN reviews ON movies.id = reviews.movie_id
            WHERE movies.director_id = ? AND reviews.rating > 9
        ''', (director_id,))
        super_hits = cursor.fetchone()[0]

        # Number of "flops" (rating < 5)
        cursor.execute(''' 
            SELECT COUNT(*) FROM movies 
            JOIN reviews ON movies.id = reviews.movie_id
            WHERE movies.director_id = ? AND reviews.rating < 5
        ''', (director_id,))
        flops = cursor.fetchone()[0]

        # Most frequent genre the director has worked in
        cursor.execute(''' 
            SELECT genres.name, COUNT(*) AS genre_count
            FROM movies
            JOIN movie_genres ON movies.id = movie_genres.movie_id
            JOIN genres ON movie_genres.genre_id = genres.id
            WHERE movies.director_id = ?
            GROUP BY genres.name
            ORDER BY genre_count DESC
            LIMIT 1
        ''', (director_id,))
        most_frequent_genre = cursor.fetchone()

        if most_frequent_genre:
            genre_name = most_frequent_genre[0]
            genre_count = most_frequent_genre[1]
        else:
            genre_name = "Unknown"
            genre_count = 0

        # Average rating of the director's movies
        cursor.execute(''' 
            SELECT AVG(reviews.rating) FROM movies
            JOIN reviews ON movies.id = reviews.movie_id
            WHERE movies.director_id = ?
        ''', (director_id,))
        avg_rating = cursor.fetchone()[0]

        # Most frequent actor the director has worked with
        cursor.execute(''' 
            SELECT actors.name, COUNT(*) AS actor_count
            FROM movie_cast
            JOIN movies ON movie_cast.movie_id = movies.id
            JOIN actors ON movie_cast.actor_id = actors.id
            WHERE movies.director_id = ?
            GROUP BY actors.name
            ORDER BY actor_count DESC
            LIMIT 1
        ''', (director_id,))
        most_frequent_actor = cursor.fetchone()

        if most_frequent_actor:
            actor_name = most_frequent_actor[0]
            actor_count = most_frequent_actor[1]
        else:
            actor_name = "No actor found"
            actor_count = 0

        # Best rated movie (highest rating)
        cursor.execute(''' 
            SELECT movies.title, MAX(reviews.rating) 
            FROM movies
            JOIN reviews ON movies.id = reviews.movie_id
            WHERE movies.director_id = ?
        ''', (director_id,))
        best_movie = cursor.fetchone()
        best_movie_title = best_movie[0] if best_movie else "No best movie"
        best_movie_rating = best_movie[1] if best_movie else "N/A"

        # Worst rated movie (lowest rating)
        cursor.execute(''' 
            SELECT movies.title, MIN(reviews.rating) 
            FROM movies
            JOIN reviews ON movies.id = reviews.movie_id
            WHERE movies.director_id = ?
        ''', (director_id,))
        worst_movie = cursor.fetchone()
        worst_movie_title = worst_movie[0] if worst_movie else "No worst movie"
        worst_movie_rating = worst_movie[1] if worst_movie else "N/A"

        # Return director statistics
        return {
            "director": director,
            "total_movies": total_movies,
            "hits": hits,
            "super_hits": super_hits,
            "flops": flops,
            "most_frequent_genre": {
                "genre": genre_name,
                "count": genre_count
            },
            "avg_rating": avg_rating if avg_rating else "No ratings available",
            "most_frequent_actor": {
                "actor": actor_name,
                "count": actor_count
            },
            "best_movie": {
                "title": best_movie_title,
                "rating": best_movie_rating
            },
            "worst_movie": {
                "title": worst_movie_title,
                "rating": worst_movie_rating
            }
        }

    except sqlite3.Error as e:
        return {"error": f"An error occurred: {e}"}

    finally:
        conn.close()  


def get_top_grossing_movies():
    # Connect to the database
    conn = get_db()
    cursor = conn.cursor()

    try:
        # Query for the top 10 grossing movies
        cursor.execute("""
            SELECT title, revenue
            FROM movies
            ORDER BY revenue DESC
            LIMIT 10
        """)
        movies = cursor.fetchall()

        return movies  # List of tuples (title, revenue)
    
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None
    
    finally:
        conn.close()
        
def get_top_rated_movies():
    # Connect to the database
    conn = get_db()
    cursor = conn.cursor()

    try:
        # Query for the top 10 rated movies (average rating)
        cursor.execute("""
            SELECT m.title, AVG(r.rating) AS avg_rating
            FROM movies m
            JOIN reviews r ON m.id = r.movie_id
            GROUP BY m.id
            ORDER BY avg_rating DESC
            LIMIT 10
        """)
        movies = cursor.fetchall()

        return movies  # List of tuples (title, avg_rating)
    
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None
    
    finally:
        conn.close()
        
def get_top_actors_most_movies():
    # Connect to the database
    conn = get_db()
    cursor = conn.cursor()

    try:
        # Query for the top 10 actors who appeared in the most movies
        cursor.execute("""
            SELECT a.name, COUNT(m.id) AS movie_count
            FROM actors a
            JOIN movie_cast mc ON a.id = mc.actor_id
            JOIN movies m ON mc.movie_id = m.id
            GROUP BY a.id
            ORDER BY movie_count DESC
            LIMIT 10
        """)
        actors = cursor.fetchall()

        return actors  # List of tuples (actor_name, movie_count)
    
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None
    
    finally:
        conn.close()
        
def get_top_directors_most_movies():
    # Connect to the database
    conn = get_db()
    cursor = conn.cursor()

    try:
        # Query for the top 10 directors with the most movies
        cursor.execute("""
            SELECT d.name, COUNT(m.id) AS movie_count
            FROM directors d
            JOIN movies m ON d.id = m.director_id
            GROUP BY d.id
            ORDER BY movie_count DESC
            LIMIT 10
        """)
        directors = cursor.fetchall()

        return directors  # List of tuples (director_name, movie_count)
    
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None
    
    finally:
        conn.close()
        