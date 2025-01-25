import sqlite3
import csv

# Create and connect to the SQLite database
conn = sqlite3.connect('movies.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    release_date TEXT,
    runtime INTEGER,
    tagline TEXT,
    overview TEXT,
    budget INTEGER,
    revenue INTEGER,
    original_language TEXT,
    director_id INTEGER,
    production_company_id INTEGER,
    FOREIGN KEY(director_id) REFERENCES directors(id),
    FOREIGN KEY(production_company_id) REFERENCES production_companies(id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS actors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS genres (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS directors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS production_companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS movie_genres (
    movie_id INTEGER,
    genre_id INTEGER,
    FOREIGN KEY(movie_id) REFERENCES movies(id),
    FOREIGN KEY(genre_id) REFERENCES genres(id),
    PRIMARY KEY (movie_id, genre_id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS movie_cast (
    movie_id INTEGER,
    actor_id INTEGER,
    FOREIGN KEY(movie_id) REFERENCES movies(id),
    FOREIGN KEY(actor_id) REFERENCES actors(id),
    PRIMARY KEY (movie_id, actor_id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS reviews (
    movie_id INTEGER PRIMARY KEY,
    rating REAL,
    vote_count INTEGER,
    FOREIGN KEY(movie_id) REFERENCES movies(id)
)
''')

# Function to insert actors and get actor ID
def get_actor_id(actor_name):
    cursor.execute('SELECT id FROM actors WHERE name = ?', (actor_name,))
    actor = cursor.fetchone()
    if actor:
        return actor[0]
    else:
        cursor.execute('INSERT INTO actors (name) VALUES (?)', (actor_name,))
        conn.commit()
        return cursor.lastrowid

# Function to insert genres and get genre ID
def get_genre_id(genre_name):
    cursor.execute('SELECT id FROM genres WHERE name = ?', (genre_name,))
    genre = cursor.fetchone()
    if genre:
        return genre[0]
    else:
        cursor.execute('INSERT INTO genres (name) VALUES (?)', (genre_name,))
        conn.commit()
        return cursor.lastrowid

# Function to insert directors and get director ID
def get_director_id(director_name):
    cursor.execute('SELECT id FROM directors WHERE name = ?', (director_name,))
    director = cursor.fetchone()
    if director:
        return director[0]
    else:
        cursor.execute('INSERT INTO directors (name) VALUES (?)', (director_name,))
        conn.commit()
        return cursor.lastrowid

# Function to insert production companies and get production company ID
def get_production_company_id(company_name):
    cursor.execute('SELECT id FROM production_companies WHERE name = ?', (company_name,))
    company = cursor.fetchone()
    if company:
        return company[0]
    else:
        cursor.execute('INSERT INTO production_companies (name) VALUES (?)', (company_name,))
        conn.commit()
        return cursor.lastrowid

# Function to insert votes (vote_average and vote_count)
def insert_votes(movie_id, vote_average, vote_count):
    cursor.execute('''
    INSERT INTO reviews (movie_id, rating, vote_count)
    VALUES (?, ?, ?)
    ''', (movie_id, vote_average, vote_count))
    conn.commit()

# Read the CSV file
with open('draft.csv', 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    
    for row in reader:
        movie_title = row['title']
        release_date = row['release_date']
        runtime = int(row['runtime']) if row['runtime'] else None
        tagline = row['tagline']
        overview = row['overview']
        budget = int(row['budget']) if row['budget'] else None
        revenue = int(row['revenue']) if row['revenue'] else None
        original_language = row['original_language']

        director_name = row['director']
        production_company_name = row['production_companies']
        
        # Insert movie into the 'movies' table, including director and production company
        director_id = get_director_id(director_name)
        production_company_id = get_production_company_id(production_company_name)
        
        cursor.execute('''
        INSERT INTO movies (title, release_date, runtime, tagline, overview, budget, revenue, original_language, director_id, production_company_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (movie_title, release_date, runtime, tagline, overview, budget, revenue, original_language, director_id, production_company_id))
        movie_id = cursor.lastrowid

        # Insert cast and create associations in 'movie_cast'
        cast_members = row['cast'].split(',')  # Assuming 'cast' column contains comma-separated names
        for cast_member in cast_members:
            actor_id = get_actor_id(cast_member.strip())
            cursor.execute('INSERT INTO movie_cast (movie_id, actor_id) VALUES (?, ?)', (movie_id, actor_id))
        
        # Insert genres and create associations in 'movie_genres'
        genres = row['genres'].split()  # Assuming 'genres' column contains space-separated genres
        for genre in genres:
            genre_id = get_genre_id(genre)
            cursor.execute('INSERT INTO movie_genres (movie_id, genre_id) VALUES (?, ?)', (movie_id, genre_id))
        
        # Insert vote_average and vote_count into the 'votes' table
        vote_average = float(row['vote_average']) if row['vote_average'] else None
        vote_count = int(row['vote_count']) if row['vote_count'] else None
        insert_votes(movie_id, vote_average, vote_count)
        
        conn.commit()

# Close the connection
conn.close()