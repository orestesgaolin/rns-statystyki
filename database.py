import sqlite3
from pathlib import Path
import json
import os
from logger_config import setup_logger

# Configure logging
logger = setup_logger(__name__, 'db_migration.log')

DB_NAME = "playlist.db"
NOT_FOUND_SONGS_FILE = "not_found_songs.txt"

def setup_database():
    """Create the database with the new schema."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        
        # Drop existing tables if they exist
        # cursor.execute("DROP TABLE IF EXISTS songs")
        # cursor.execute("DROP TABLE IF EXISTS playlists")
        # cursor.execute("DROP TABLE IF EXISTS song_metadata")
        
        # Create songs table - stores unique songs
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_id INTEGER,
            artist TEXT NOT NULL,
            title TEXT NOT NULL,
            UNIQUE(artist, title)
        )
        """)
        
        # Create playlists table - stores when songs were played
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS playlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            song_id INTEGER NOT NULL,
            date_play TEXT NOT NULL,
            img TEXT,
            FOREIGN KEY (song_id) REFERENCES songs(id)
        )
        """)
        
        # Create song_metadata table - stores additional song information
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS song_metadata (
            song_id INTEGER PRIMARY KEY,
            language TEXT,
            genre TEXT,  -- Stored as JSON array
            publish_date TEXT,
            source TEXT,  -- Where the metadata came from (e.g., 'musicbrainz', 'langdetect')
            raw_data TEXT,  -- Raw response data in JSON format for future processing
            FOREIGN KEY (song_id) REFERENCES songs(id)
        )
        """)
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_playlists_song_id ON playlists(song_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_playlists_date_play ON playlists(date_play)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_songs_artist_title ON songs(artist, title)")
        
        conn.commit()
        logger.info("Database schema created successfully")

def get_or_create_song(conn, artist, title, original_id=None):
    """Get a song ID or create a new entry if it doesn't exist."""
    cursor = conn.cursor()
    
    # Try to find the song first
    cursor.execute(
        "SELECT id FROM songs WHERE artist = ? AND title = ?",
        (artist, title)
    )
    result = cursor.fetchone()
    
    if result:
        return result[0]
    
    # If not found, create a new song entry
    cursor.execute(
        "INSERT INTO songs (artist, title, original_id) VALUES (?, ?, ?)",
        (artist, title, original_id)
    )
    conn.commit()
    return cursor.lastrowid

def add_song_play(conn, song_id, date_play, img=None):
    """Add a song play to the playlists table."""
    cursor = conn.cursor()
    
    # Check if the combination of song_id and date_play already exists
    cursor.execute(
        "SELECT id FROM playlists WHERE song_id = ? AND date_play = ?",
        (song_id, date_play)
    )
    existing_record = cursor.fetchone()
    
    if existing_record:
        # Return existing record ID if found
        return existing_record[0]
    
    # If not found, insert the new record
    cursor.execute(
        "INSERT INTO playlists (song_id, date_play, img) VALUES (?, ?, ?)",
        (song_id, date_play, img)
    )
    conn.commit()
    return cursor.lastrowid

def update_song_metadata(conn, song_id, language=None, genre=None, publish_date=None, source=None, raw_data=None):
    """Update or create metadata for a song."""
    cursor = conn.cursor()
    
    # Convert genre list to JSON if it's a list
    if genre and isinstance(genre, list):
        genre = json.dumps(genre)
    
    # Convert raw_data to JSON if it's a dict
    if raw_data and isinstance(raw_data, dict):
        raw_data = json.dumps(raw_data)
    
    # Check if metadata already exists for this song
    cursor.execute("SELECT 1 FROM song_metadata WHERE song_id = ?", (song_id,))
    exists = cursor.fetchone() is not None
    
    if exists:
        # Update existing metadata, preserving existing values for fields not provided
        updates = []
        params = []
        
        if language is not None:
            updates.append("language = ?")
            params.append(language)
        if genre is not None:
            updates.append("genre = ?")
            params.append(genre)
        if publish_date is not None:
            updates.append("publish_date = ?")
            params.append(publish_date)
        if source is not None:
            updates.append("source = ?")
            params.append(source)
        if raw_data is not None:
            updates.append("raw_data = ?")
            params.append(raw_data)
        
        if updates:
            query = f"UPDATE song_metadata SET {', '.join(updates)} WHERE song_id = ?"
            params.append(song_id)
            cursor.execute(query, params)
    else:
        # Insert new metadata
        cursor.execute(
            """
            INSERT INTO song_metadata (song_id, language, genre, publish_date, source, raw_data)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (song_id, language, genre, publish_date, source, raw_data)
        )
    
    conn.commit()

def record_not_found_song(artist, title):
    """Record songs that were not found in MusicBrainz to a text file."""
    with open(NOT_FOUND_SONGS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{artist} - {title}\n")

def get_songs_by_criteria(language=None, artist_substring=None, title_substring=None, exact_artist=None, limit=100):
    """Get songs matching specific criteria for focused metadata processing."""
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query_parts = ["SELECT s.id, s.artist, s.title FROM songs s"]
        where_clauses = []
        params = []
        
        # Check if we want to join with metadata
        if language is not None:
            query_parts.append("JOIN song_metadata sm ON s.id = sm.song_id")
            where_clauses.append("sm.language = ?")
            params.append(language)
        
        # Add exact artist filter
        if exact_artist is not None:
            where_clauses.append("s.artist = ?")
            params.append(exact_artist)
        # Add artist substring filter
        elif artist_substring is not None:
            where_clauses.append("s.artist LIKE ?")
            params.append(f"%{artist_substring}%")
        
        # Add title filter
        if title_substring is not None:
            where_clauses.append("s.title LIKE ?")
            params.append(f"%{title_substring}%")
        
        # Add WHERE clause if we have conditions
        if where_clauses:
            query_parts.append("WHERE " + " AND ".join(where_clauses))
        
        # Add limit
        query_parts.append(f"LIMIT {limit}")
        
        # Build and execute the query
        query = " ".join(query_parts)
        cursor.execute(query, params)
        
        return [dict(row) for row in cursor.fetchall()]

def get_songs_without_metadata(limit=None):
    """Get a list of songs that don't have metadata yet."""
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = """
            SELECT s.id, s.artist, s.title 
            FROM songs s
            LEFT JOIN song_metadata sm ON s.id = sm.song_id
            WHERE sm.song_id IS NULL
        """
        
        if limit:
            query += f" LIMIT {limit}"
            
        cursor.execute(query)
        
        return [dict(row) for row in cursor.fetchall()]

def get_song_stats():
    """Get statistics about songs and metadata coverage."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        
        # Total songs
        cursor.execute("SELECT COUNT(*) FROM songs")
        total_songs = cursor.fetchone()[0]
        
        # Songs with metadata
        cursor.execute("SELECT COUNT(*) FROM song_metadata")
        songs_with_metadata = cursor.fetchone()[0]
        
        # Songs by metadata source
        cursor.execute("SELECT source, COUNT(*) FROM song_metadata GROUP BY source")
        sources = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Languages detected
        cursor.execute("SELECT language, COUNT(*) FROM song_metadata WHERE language IS NOT NULL GROUP BY language")
        languages = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Extract genres (stored as JSON arrays)
        cursor.execute("SELECT genre FROM song_metadata WHERE genre IS NOT NULL")
        genre_counts = {}
        for row in cursor.fetchall():
            if row[0]:
                try:
                    genres = json.loads(row[0])
                    for genre in genres:
                        genre_counts[genre] = genre_counts.get(genre, 0) + 1
                except json.JSONDecodeError:
                    pass
        
        # Sort genres by popularity and take top 20
        top_genres = dict(sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:20])
        
        # Publication years
        cursor.execute("SELECT publish_date, COUNT(*) FROM song_metadata WHERE publish_date IS NOT NULL GROUP BY publish_date")
        publish_dates = {}
        for row in cursor.fetchall():
            if row[0]:
                # Extract just the year from the date (could be in format YYYY-MM-DD or just YYYY)
                try:
                    year = row[0].split('-')[0] if '-' in row[0] else row[0]
                    publish_dates[year] = row[1]
                except (IndexError, AttributeError):
                    pass
        
        return {
            "total_songs": total_songs,
            "songs_with_metadata": songs_with_metadata,
            "metadata_coverage_percent": round((songs_with_metadata / total_songs * 100) if total_songs > 0 else 0, 2),
            "sources": sources,
            "languages": languages,
            "top_genres": top_genres,
            "publish_dates": publish_dates
        }
