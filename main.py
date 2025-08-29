from datetime import datetime, date, timedelta
import json
import sqlite3
from pathlib import Path
import requests
import argparse
import os
from dotenv import load_dotenv
from database import (
    setup_database, get_or_create_song, add_song_play, 
    get_songs_without_metadata, get_song_stats
)
from metadata import process_song_without_metadata
from logger_config import setup_logger

# Load environment variables from .env file
load_dotenv()

# Configure logging
logger = setup_logger(__name__, 'rns_main.log')

DB_NAME = "playlist.db"
DATA_DIR = Path("data")
API_URL = "https://nowyswiat.online/api/Mobile/get_playlist_from_date"
DEFAULT_API_KEY = os.environ.get("RNS_API_KEY", "")
START_DATE = date(2020, 7, 10)  # Fixed: using date directly instead of datetime.date
DOCS_DIR = Path("docs")


def setup_database():
    """Create the database and tables."""
    from database import setup_database as db_setup
    db_setup()


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
        total_files = len(json_files)
        
        logger.info(f"Processing {total_files} JSON files...")
        for i, json_path in enumerate(json_files, 1):
            logger.info(f"Processing file {i}/{total_files}: {json_path}")
            
            with open(json_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    logger.error(f"Error decoding JSON from {json_path}")
                    continue

            if "playlist" in data and data["playlist"]:
                for song in data["playlist"]:
                    if not song.get("artist") or not song.get("title"):
                        continue
                    
                    # Get or create song
                    song_id = get_or_create_song(
                        conn, 
                        song["artist"], 
                        song["title"], 
                        song.get("id")
                    )
                    
                    # Add to playlist
                    add_song_play(
                        conn,
                        song_id,
                        song["date_play"],
                        song.get("img")
                    )

    logger.info("Database update completed!")


def process_metadata(limit=None, artist_substring=None, title_substring=None, exact_artist=None):
    """Process metadata for songs that don't have it yet."""
    if artist_substring or title_substring or exact_artist:
        from database import get_songs_by_criteria
        songs_without_metadata = get_songs_by_criteria(
            artist_substring=artist_substring, 
            title_substring=title_substring,
            exact_artist=exact_artist,
            limit=limit
        )
        filter_desc = f"artist: {artist_substring}" if artist_substring else ""
        filter_desc += f", exact artist: {exact_artist}" if exact_artist else ""
        filter_desc += f", title: {title_substring}" if title_substring else ""
        logger.info(f"Processing metadata for filtered songs ({filter_desc})")
    else:
        from database import get_songs_without_metadata
        songs_without_metadata = get_songs_without_metadata(limit)
        logger.info(f"Processing metadata for songs without existing metadata")
    
    total_songs = len(songs_without_metadata)
    
    if total_songs == 0:
        logger.info("No matching songs found.")
        return
    
    logger.info(f"Processing metadata for {total_songs} songs...")
    
    with sqlite3.connect(DB_NAME) as conn:
        for i, song in enumerate(songs_without_metadata, 1):
            logger.info(f"Processing metadata ({i}/{total_songs}): {song['artist']} - {song['title']}")
            process_song_without_metadata(conn, song['id'], song['artist'], song['title'])
            
            # Print progress every 10 songs
            if i % 10 == 0 or i == total_songs:
                stats = get_song_stats()
                logger.info(f"Progress: {i}/{total_songs} songs processed")
                logger.info(f"Metadata coverage: {stats['metadata_coverage_percent']}%")
    
    # Print final statistics
    stats = get_song_stats()
    logger.info("Metadata processing completed!")
    logger.info(f"Total songs: {stats['total_songs']}")
    logger.info(f"Songs with metadata: {stats['songs_with_metadata']}")
    logger.info(f"Metadata coverage: {stats['metadata_coverage_percent']}%")
    logger.info(f"Sources: {stats['sources']}")
    if 'languages' in stats:
        logger.info(f"Languages: {stats['languages']}")

def show_metadata_stats():
    """Display detailed statistics about metadata."""
    stats = get_song_stats()
    logger.info("Metadata Statistics:")
    logger.info("=" * 40)
    logger.info(f"Total songs: {stats['total_songs']}")
    logger.info(f"Songs with metadata: {stats['songs_with_metadata']}")
    logger.info(f"Metadata coverage: {stats['metadata_coverage_percent']}%")
    logger.info("-" * 40)
    logger.info(f"Sources: {stats['sources']}")
    
    if 'languages' in stats:
        logger.info(f"Languages: {stats['languages']}")
        
    if 'top_genres' in stats:
        logger.info("-" * 40)
        logger.info("Top Genres:")
        for genre, count in stats['top_genres'].items():
            logger.info(f"  {genre}: {count}")
            
    if 'publish_dates' in stats:
        by_decade = {}
        for year, count in stats['publish_dates'].items():
            if year:
                decade = int(year) // 10 * 10
                by_decade[decade] = by_decade.get(decade, 0) + count
                
        if by_decade:
            logger.info("-" * 40)
            logger.info("Publication by Decade:")
            for decade, count in sorted(by_decade.items()):
                logger.info(f"  {decade}s: {count}")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Radio Nowy Świat playlist fetcher and processor")

    parser.add_argument("--fetch", action="store_true", help="Fetch data from API and save as JSON files")
    parser.add_argument("--create-db", action="store_true", help="Create or recreate the database")
    parser.add_argument("--save-to-db", action="store_true", help="Process JSON files and save to database")
    parser.add_argument("--process-metadata", action="store_true", help="Process metadata for songs")
    parser.add_argument("--metadata-stats", action="store_true", help="Show metadata statistics")
    parser.add_argument("--limit", type=int, help="Limit the number of songs to process for metadata", default=None)
    parser.add_argument("--artist", type=str, help="Filter songs by artist name substring", default=None)
    parser.add_argument("--exact-artist", type=str, help="Filter songs by exact artist name", default=None)
    parser.add_argument("--title", type=str, help="Filter songs by title substring", default=None)
    parser.add_argument("--api-key", help="API key for Radio Nowy Świat API", default=DEFAULT_API_KEY)
    parser.add_argument("--clear-cache", action="store_true", help="Clear the artist cache before processing")

    # If no arguments provided, default to running all steps
    args = parser.parse_args()
    if not (args.fetch or args.create_db or args.save_to_db or args.process_metadata or args.metadata_stats or args.clear_cache):
        args.fetch = args.create_db = args.save_to_db = True
        
    # Validate API key if fetching data
    if args.fetch and not args.api_key:
        parser.error("API key is required for fetching data. Provide it with --api-key or set RNS_API_KEY in .env file.")

    return args


def main():
    """Main function to run the script based on command line arguments."""
    args = parse_arguments()
    try:
        if args.clear_cache:
            from metadata import clear_cache
            logger.info("Clearing artist cache...")
            clear_cache()

        if args.create_db:
            logger.info("Setting up database...")
            setup_database()

        if args.fetch:
            logger.info("Fetching data from API...")
            fetch_data(args.api_key)

        if args.save_to_db:
            logger.info("Saving data to database...")
            save_to_database()
            
        if args.process_metadata:
            logger.info("Processing metadata for songs...")
            process_metadata(
                limit=args.limit,
                artist_substring=args.artist,
                title_substring=args.title,
                exact_artist=args.exact_artist
            )
            
        if args.metadata_stats:
            show_metadata_stats()
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
    finally:
        logger.info("Done")


if __name__ == "__main__":
    main()
