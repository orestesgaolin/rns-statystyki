from datetime import datetime, date, timedelta
import json
import sqlite3
from pathlib import Path
import requests
import argparse
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DB_NAME = "playlist.db"
DATA_DIR = Path("data")
API_URL = "https://nowyswiat.online/api/Mobile/get_playlist_from_date"
DEFAULT_API_KEY = os.environ.get("RNS_API_KEY", "")
START_DATE = date(2020, 7, 10)  # Fixed: using date directly instead of datetime.date
DOCS_DIR = Path("docs")


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


def fetch_data(api_key):
    """Fetch and process playlist data from the latest processed date (or START_DATE) to today."""
    DOCS_DIR.mkdir(exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Find the latest date we have processed
    latest_date = get_latest_processed_date()
    
    # If we have processed data before, start from the latest date
    if latest_date:
        current_date = latest_date
        print(f"Resuming from {current_date.isoformat()} (latest processed date)")
    else:
        current_date = START_DATE
        print(f"Starting from the beginning: {START_DATE.isoformat()}")
    
    end_date = date.today()
    api_headers = {"x-rns-api-key": api_key}

    # If we're already up to date
    if current_date > end_date:
        print("Already up to date! No new data to fetch.")
        return

    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        print(f"Fetching data for {date_str}...")

        params = {"date": date_str, "page": 1, "perpage": 300}
        try:
            response = requests.get(API_URL, headers=api_headers, params=params)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {date_str}: {e}")
            current_date += timedelta(days=1)  # Fixed: using timedelta directly
            continue

        # Save JSON to file
        year_dir = DATA_DIR / str(current_date.year)
        year_dir.mkdir(parents=True, exist_ok=True)
        json_path = year_dir / f"{date_str}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        current_date += timedelta(days=1)  # Fixed: using timedelta directly

    print("Data fetching completed!")


def get_latest_processed_date():
    """Get the latest date for which we have data."""
    if not DATA_DIR.exists():
        return None
    
    json_files = list(DATA_DIR.rglob("*.json"))
    if not json_files:
        return None
    
    # Extract dates from filenames (format: YYYY-MM-DD.json)
    latest_date = None
    for file_path in json_files:
        try:
            date_str = file_path.stem  # Get filename without extension
            file_date = date.fromisoformat(date_str)
            if latest_date is None or file_date > latest_date:
                latest_date = file_date
        except ValueError:
            # Skip files with invalid date format
            continue
    
    return latest_date


def save_to_database():
    """Process JSON files and save data to the database."""
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

    print("Database update completed!")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Radio Nowy Świat playlist fetcher and processor")

    parser.add_argument("--fetch", action="store_true", help="Fetch data from API and save as JSON files")
    parser.add_argument("--create-db", action="store_true", help="Create or recreate the database")
    parser.add_argument("--save-to-db", action="store_true", help="Process JSON files and save to database")
    parser.add_argument("--api-key", help="API key for Radio Nowy Świat API",
                        default=DEFAULT_API_KEY)

    # If no arguments provided, default to running all steps
    args = parser.parse_args()
    if not (args.fetch or args.create_db or args.save_to_db):
        args.fetch = args.create_db = args.save_to_db = True
        
    # Validate API key if fetching data
    if args.fetch and not args.api_key:
        parser.error("API key is required for fetching data. Provide it with --api-key or set RNS_API_KEY in .env file.")

    return args


def main():
    """Main function to run the script based on command line arguments."""
    args = parse_arguments()

    if args.create_db:
        print("Setting up database...")
        setup_database()

    if args.fetch:
        print("Fetching data from API...")
        fetch_data(args.api_key)

    if args.save_to_db:
        print("Saving data to database...")
        save_to_database()

    print("Done!")


if __name__ == "__main__":
    main()
