import sqlite3

conn = sqlite3.connect('movies.db')

# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS users (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     username TEXT NOT NULL,
#     email TEXT UNIQUE NOT NULL,
#     password TEXT NOT NULL,
#     role TEXT CHECK(role IN ('admin', 'reviewer')) NOT NULL
#     )
# '''
# )

def get_director_info(director):
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






print(get_director_info("Christopher Nolan"))