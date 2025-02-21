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

def top_directors_most_movies():
    # Connect to the database
    # conn = get_db()
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

print(top_directors_most_movies())
