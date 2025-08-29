import musicbrainzngs
from langdetect import detect, LangDetectException
import time
import json
import re
from database import update_song_metadata, record_not_found_song
from logger_config import setup_logger

# Configure logging
logger = setup_logger(__name__, 'metadata_processing.log')

# Set up MusicBrainz API client
musicbrainzngs.set_useragent(
    "rns-stat", 
    "0.2", 
    "https://github.com/orestesgaolin/rns-statystyki"
)

# Artist cache to avoid redundant API calls
_artist_cache = {}
_artist_details_cache = {}
_CACHE_FILE = "artist_cache.json"

def _load_cache():
    """Load artist cache from disk.
    
    The artist cache contains found artists (with their data) and not-found artists (with None value).
    This helps avoid redundant API calls for artists that were previously not found.
    """
    global _artist_cache, _artist_details_cache
    try:
        with open(_CACHE_FILE, 'r') as f:
            cache_data = json.load(f)
            _artist_cache = cache_data.get('artists', {})
            _artist_details_cache = cache_data.get('details', {})
        logger.info(f"Loaded artist cache with {len(_artist_cache)} artists and {len(_artist_details_cache)} artist details")
    except FileNotFoundError:
        logger.info("No cache file found, starting with empty cache")
    except Exception as e:
        logger.warning(f"Error loading artist cache: {str(e)}")

def _save_cache():
    """Save artist cache to disk."""
    try:
        # Convert non-serializable keys (like artist IDs) to strings
        artists_serializable = {}
        details_serializable = {}
        
        for artist, data in _artist_cache.items():
            artists_serializable[artist] = data
            
        for artist_id, data in _artist_details_cache.items():
            details_serializable[str(artist_id)] = data
            
        with open(_CACHE_FILE, 'w') as f:
            cache_data = {
                'artists': artists_serializable,
                'details': details_serializable
            }
            json.dump(cache_data, f)
        logger.info(f"Saved artist cache with {len(_artist_cache)} artists and {len(_artist_details_cache)} artist details")
    except Exception as e:
        logger.warning(f"Error saving artist cache: {str(e)}")

def clear_cache():
    """Clear the artist cache and delete the cache file."""
    global _artist_cache, _artist_details_cache
    _artist_cache = {}
    _artist_details_cache = {}
    
    try:
        import os
        if os.path.exists(_CACHE_FILE):
            os.remove(_CACHE_FILE)
            logger.info(f"Cache file {_CACHE_FILE} deleted")
    except Exception as e:
        logger.warning(f"Error deleting cache file: {str(e)}")
    
    logger.info("Artist cache cleared")

# Load cache at module initialization
_load_cache()

def find_song_metadata(conn, song_id, artist, title):
    """Try to find song metadata using MusicBrainz API."""
    try:
        # Extract metadata
        language = None
        genres = []
        publish_date = None
        
        # Define mapping of countries to languages
        country_to_lang = {
            # English speaking countries
            'GB': 'en-GB', 'US': 'en-US', 'CA': 'en-CA', 'AU': 'en-AU', 'NZ': 'en-NZ', 'IE': 'en-IE',
            # European languages
            'FR': 'fr', 'DE': 'de', 'IT': 'it', 'ES': 'es', 'PL': 'pl', 
            'RU': 'ru', 'PT': 'pt', 'NL': 'nl', 'BE': 'nl', 'SE': 'sv',
            'NO': 'no', 'DK': 'da', 'FI': 'fi', 'GR': 'el', 'CZ': 'cs',
            # Asian languages
            'JP': 'ja', 'CN': 'zh', 'KR': 'ko', 'TH': 'th', 'IN': 'hi',
            # Latin American countries (mostly Spanish)
            'MX': 'es', 'AR': 'es', 'CO': 'es', 'CL': 'es', 'PE': 'es', 
            'VE': 'es', 'EC': 'es', 'GT': 'es', 'CU': 'es', 'BO': 'es',
            'DO': 'es', 'HN': 'es', 'PY': 'es', 'SV': 'es', 'NI': 'es', 
            'CR': 'es', 'PA': 'es', 'UY': 'es',
            # Brazil (Portuguese)
            'BR': 'pt'
        }
        
        # Search directly for the artist
        logger.info(f"Searching MusicBrainz for artist: '{artist}'")
        
        # Check if we have the artist in our cache
        if artist in _artist_cache:
            # Check if the artist was previously not found
            if _artist_cache[artist] is None:
                logger.info(f"Artist '{artist}' was previously not found in MusicBrainz")
                return False
                
            logger.info(f"Using cached artist data for: '{artist}'")
            artist_data = _artist_cache[artist]
        else:
            # Search the MusicBrainz API
            artist_result = musicbrainzngs.search_artists(query=artist, limit=5)
            
            # Add a small delay to avoid rate limiting
            time.sleep(0.25)
            
            if "artist-list" not in artist_result or not artist_result["artist-list"]:
                logger.info(f"No artists found for query: {artist}")
                # Cache the fact that this artist wasn't found (using None)
                _artist_cache[artist] = None
                _save_cache()  # Save the cache immediately for not-found artists
                return False
                
            # Log found artists for debugging
            logger.info(f"Found {len(artist_result['artist-list'])} artists matching '{artist}'")
            for idx, artist_item in enumerate(artist_result["artist-list"]):
                logger.info(f"Artist {idx+1}: {artist_item.get('name', 'Unknown')} [{artist_item.get('id', 'No ID')}]")
                
            # Take the first artist match
            artist_data = artist_result["artist-list"][0]
            
            # Cache the artist data for future use
            _artist_cache[artist] = artist_data
            
        logger.info(f"Selected artist: {artist_data.get('name', 'Unknown')} [{artist_data.get('id', 'No ID')}]")
        
        # Log the full artist data for debugging
        # logger.info(f"Artist data: {json.dumps(artist_data, indent=2)}")
        
        # First try to determine language from country code (direct and most reliable)
        if 'country' in artist_data:
            country = artist_data['country']
            language = country_to_lang.get(country)
            logger.info(f"Using artist country code '{country}' to determine language: {language}")
            
        # If no language found from country code, try the area name
        if not language and 'area' in artist_data:
            area_name = artist_data['area']['name']
            logger.info(f"Found artist area: {area_name}")
            
            # Map common countries/areas to language codes
            area_to_lang = {
                # English-speaking areas
                'United States': 'en-US', 'United Kingdom': 'en-GB', 'Australia': 'en-AU', 
                'Canada': 'en-CA', 'New Zealand': 'en-NZ', 'Ireland': 'en-IE', 'England': 'en-GB',
                'Scotland': 'en-GB', 'Wales': 'en-GB', 
                
                # European areas with distinct languages
                'Germany': 'de', 'Austria': 'de', 'Switzerland': 'de',
                'France': 'fr', 'Belgium': 'fr',  # Note: Belgium could be fr or nl
                'Italy': 'it', 'Spain': 'es', 'Poland': 'pl', 'Russia': 'ru',
                'Sweden': 'sv', 'Norway': 'no', 'Denmark': 'da', 'Finland': 'fi',
                'Netherlands': 'nl', 'Greece': 'el', 'Czech Republic': 'cs',
                'Hungary': 'hu', 'Portugal': 'pt', 'Romania': 'ro', 'Bulgaria': 'bg',
                'Ukraine': 'uk', 'Croatia': 'hr', 'Serbia': 'sr', 'Slovakia': 'sk',
                
                # Asian areas
                'Japan': 'ja', 'China': 'zh', 'Korea': 'ko', 'South Korea': 'ko',
                'Thailand': 'th', 'India': 'hi', 'Turkey': 'tr', 'Indonesia': 'id',
                'Malaysia': 'ms', 'Philippines': 'tl',
                
                # Latin American areas
                'Mexico': 'es', 'Argentina': 'es', 'Colombia': 'es', 'Chile': 'es',
                'Peru': 'es', 'Venezuela': 'es', 'Ecuador': 'es', 'Guatemala': 'es',
                'Cuba': 'es', 'Bolivia': 'es', 'Dominican Republic': 'es',
                'Honduras': 'es', 'Paraguay': 'es', 'El Salvador': 'es',
                'Nicaragua': 'es', 'Costa Rica': 'es', 'Panama': 'es',
                'Uruguay': 'es', 'Puerto Rico': 'es',
                
                # Brazil (Portuguese)
                'Brazil': 'pt'
            }
            language = area_to_lang.get(area_name)
            if language:
                logger.info(f"Using artist area '{area_name}' to determine language: {language}")
        
                # No need for the fallback to country code since we now check it first
        
        # Try to get genre tags for the artist
        artist_id = artist_data.get('id')
        if artist_id:
            try:
                # Check if we have the artist details in our cache
                if artist_id in _artist_details_cache:
                    logger.info(f"Using cached artist details for ID: {artist_id}")
                    artist_details = _artist_details_cache[artist_id]
                else:
                    # Look up detailed artist info to get tags for potential genres
                    logger.info(f"Fetching extended artist details for ID: {artist_id}")
                    artist_details = musicbrainzngs.get_artist_by_id(artist_id, includes=['tags'])
                    # Add a small delay to avoid rate limiting
                    time.sleep(0.25)

                    # Cache the artist details for future use
                    _artist_details_cache[artist_id] = artist_details
                
                if 'artist' in artist_details and 'tag-list' in artist_details['artist']:
                    # Extract genres from tags
                    for tag in artist_details['artist']['tag-list']:
                        if 'name' in tag:
                            genres.append(tag['name'])
                    logger.info(f"Found genres from artist tags: {genres}")
            except Exception as e:
                logger.warning(f"Error getting extended artist details: {str(e)}")
        
        # Convert genres to JSON string
        genres_json = json.dumps(genres) if genres else None
        
        # Store the metadata
        update_song_metadata(
            conn=conn,
            song_id=song_id,
            language=language,
            genre=genres_json,  # Use JSON string instead of list
            publish_date=publish_date,
            source='musicbrainz',
            raw_data=json.dumps(artist_data)  # Convert dict to JSON string
        )
        
        logger.info(f"Updated metadata for {artist} - {title}: lang={language}, genres={genres}")
        return True
            
    except Exception as e:
        logger.error(f"Error searching MusicBrainz for {artist} - {title}: {str(e)}")
        return False
        
        # If we get here, none of the search strategies worked
        logger.warning(f"No MusicBrainz results for: {artist} - {title}")
        return False

def detect_language_from_text(text):
    """Try to detect language from song title and artist."""
    try:
        # Try to detect language from combined artist and title
        language = detect(text)
        return language
    except LangDetectException as e:
        logger.warning(f"Could not detect language from '{text}': {str(e)}")
        return None

def process_song_without_metadata(conn, song_id, artist, title):
    """Process a song that doesn't have metadata yet."""
    # Try MusicBrainz
    success = find_song_metadata(conn, song_id, artist, title)
    
    # If MusicBrainz failed, record the song as not found
    if not success:
        logger.info(f"Could not find metadata for: {artist} - {title}")
        record_not_found_song(artist, title)
        # No need to save cache here as we now save it within find_song_metadata for not-found artists
    else:
        # Save the artist cache after successful lookups
        _save_cache()
    
