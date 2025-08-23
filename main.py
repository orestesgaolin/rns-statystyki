import json
import sqlite3
from pathlib import Path

DB_NAME = "playlist.db"
DATA_DIR = Path("data")


def setup_database():
    """Create the database and songs table if they don't exist."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS songs")
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            song_id INTEGER,
            date_play TEXT NOT NULL,
            artist TEXT NOT NULL,
            title TEXT NOT NULL,
            img TEXT
        )
        """
        )
        conn.commit()


def main():
    """Recreate the database from JSON files."""
    setup_database()

    with sqlite3.connect(DB_NAME) as conn:
        json_files = sorted(DATA_DIR.rglob("*.json"))

        for json_path in json_files:
            print(f"Processing {json_path}...")
            with open(json_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    print(f"Error decoding JSON from {json_path}")
                    continue

            if "playlist" in data and data["playlist"]:
                cursor = conn.cursor()
                songs_to_insert = [
                    (
                        song["id"],
                        song["date_play"],
                        song["artist"],
                        song["title"],
                        song["img"],
                    )
                    for song in data["playlist"]
                    if song.get("artist") and song.get("title")
                ]
                cursor.executemany(
                    """
                    INSERT INTO songs (song_id, date_play, artist, title, img)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    songs_to_insert,
                )
                conn.commit()

    print("Done!")


if __name__ == "__main__":
    main()
