import sqlite3
import requests

# conn = sqlite3.connect('movies.db')

# # cursor.execute('''
# #     CREATE TABLE IF NOT EXISTS users (
# #     id INTEGER PRIMARY KEY AUTOINCREMENT,
# #     username TEXT NOT NULL,
# #     email TEXT UNIQUE NOT NULL,
# #     password TEXT NOT NULL,
# #     role TEXT CHECK(role IN ('admin', 'reviewer')) NOT NULL
# #     )
# # '''
# # )

# def top_directors_most_movies():
#     # Connect to the database
#     # conn = get_db()
#     cursor = conn.cursor()

#     try:
#         # Query for the top 10 directors with the most movies
#         cursor.execute("""
#             SELECT d.name, COUNT(m.id) AS movie_count
#             FROM directors d
#             JOIN movies m ON d.id = m.director_id
#             GROUP BY d.id
#             ORDER BY movie_count DESC
#             LIMIT 10
#         """)
#         directors = cursor.fetchall()

#         return directors  # List of tuples (director_name, movie_count)
    
#     except sqlite3.Error as e:
#         print(f"An error occurred: {e}")
#         return None
    
#     finally:
#         conn.close()

# print(top_directors_most_movies())

def get_person_image(person_name):
    """Fetch an image of an actor or director using TMDb API."""
    
    if not person_name:
        return None

    # Construct the TMDb API URL with the query
    tmdb_url = f"https://api.themoviedb.org/3/search/person?query={person_name}&api_key=a8fdfb98352cb76469729ffe375525d5"

    try:
        # Request data from the API
        response = requests.get(tmdb_url, timeout=5).json()
        # print(response['results'])

        # Check if 'results' key exists and is non-empty
        if 'results' in response and response["results"]:
            # Get the profile image path from the first result
            profile_path = response["results"][0].get("profile_path")
            
            if profile_path:  # Ensure profile_path is not None or empty
                TMDB_IMAGE_URL = "https://image.tmdb.org/t/p/w185"
                return f"{TMDB_IMAGE_URL}{profile_path}"
            else:
                current_app.logger.warning(f"No profile image found for {person_name}.")
                return None
        else:
            current_app.logger.warning(f"No results found for {person_name}.")
            return None

    except requests.RequestException as e:
        current_app.logger.error(f"TMDb API request failed: {e}")
        return None

print(get_person_image("Tom Cruise"))