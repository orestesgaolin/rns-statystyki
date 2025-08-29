import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path
from logger_config import setup_logger

# Configure logging
logger = setup_logger(__name__, 'export_stats.log')

def export_data():
    conn = sqlite3.connect('playlist.db')
    conn.row_factory = sqlite3.Row  # This enables column access by name
    cursor = conn.cursor()

    # Create export directory if it doesn't exist
    os.makedirs('website/data', exist_ok=True)

    # Export metadata
    cursor.execute("""
        SELECT MIN(date_play) as min_date, MAX(date_play) as max_date, COUNT(*) as total_plays 
        FROM playlists
    """)
    metadata = dict(cursor.fetchone())
    
    # Get total unique songs
    cursor.execute("SELECT COUNT(*) as total_songs FROM songs")
    metadata['total_songs'] = cursor.fetchone()['total_songs']
    
    # Get metadata coverage
    cursor.execute("SELECT COUNT(*) as songs_with_metadata FROM song_metadata")
    metadata['songs_with_metadata'] = cursor.fetchone()['songs_with_metadata']
    metadata['metadata_coverage_percent'] = round(
        (metadata['songs_with_metadata'] / metadata['total_songs'] * 100) 
        if metadata['total_songs'] > 0 else 0, 
        2
    )
    
    # Get language statistics
    cursor.execute("""
        SELECT language, COUNT(*) as count 
        FROM song_metadata 
        WHERE language IS NOT NULL 
        GROUP BY language 
        ORDER BY count DESC
    """)
    metadata['languages'] = {row['language']: row['count'] for row in cursor.fetchall()}
    
    # Export top artists overall
    cursor.execute("""
        SELECT s.artist, COUNT(*) as play_count 
        FROM playlists p
        JOIN songs s ON p.song_id = s.id
        GROUP BY s.artist 
        ORDER BY play_count DESC 
        LIMIT 100
    """)
    top_artists = [dict(row) for row in cursor.fetchall()]
    
    # Export top songs overall
    cursor.execute("""
        SELECT s.artist, s.title, COUNT(*) as play_count 
        FROM playlists p
        JOIN songs s ON p.song_id = s.id
        GROUP BY s.artist, s.title 
        ORDER BY play_count DESC 
        LIMIT 100
    """)
    top_songs = [dict(row) for row in cursor.fetchall()]
    
    # Export data by year
    cursor.execute("""
        SELECT strftime('%Y', date_play) as year, COUNT(*) as song_count
        FROM playlists
        GROUP BY year
        ORDER BY year
    """)
    years_data = []
    for row in cursor.fetchall():
        year_data = dict(row)
        # Make sure year is included properly
        years_data.append(year_data)
    
    # Export top artists by year starting from 2020
    years = [row['year'] for row in years_data if row['year'] >= '2020']
    top_artists_by_year = {}
    
    for year in years:
        cursor.execute("""
            SELECT s.artist, COUNT(*) as play_count 
            FROM playlists p
            JOIN songs s ON p.song_id = s.id
            WHERE strftime('%Y', p.date_play) = ?
            GROUP BY s.artist 
            ORDER BY play_count DESC 
            LIMIT 20
        """, (year,))
        top_artists_by_year[year] = [dict(row) for row in cursor.fetchall()]
    
    # Export top songs by year
    top_songs_by_year = {}
    
    for year in years:
        cursor.execute("""
            SELECT s.artist, s.title, COUNT(*) as play_count 
            FROM playlists p
            JOIN songs s ON p.song_id = s.id
            WHERE strftime('%Y', p.date_play) = ?
            GROUP BY s.artist, s.title 
            ORDER BY play_count DESC 
            LIMIT 20
        """, (year,))
        top_songs_by_year[year] = [dict(row) for row in cursor.fetchall()]
    
    # Export monthly data for each year
    cursor.execute("""
        SELECT strftime('%Y', date_play) as year, 
               strftime('%m', date_play) as month, 
               COUNT(*) as song_count
        FROM playlists
        GROUP BY year, month
        ORDER BY year, month
    """)
    monthly_data_rows = [dict(row) for row in cursor.fetchall()]
    
    # Reorganize monthly data by year
    monthly_data_by_year = {}
    for row in monthly_data_rows:
        year = row['year']
        if year not in monthly_data_by_year:
            monthly_data_by_year[year] = []
        monthly_data_by_year[year].append({
            'month': row['month'],
            'song_count': row['song_count']
        })
    
    # Export top artists movement over years - focused on ranking changes
    cursor.execute("""
        SELECT DISTINCT strftime('%Y', date_play) as year
        FROM playlists
        ORDER BY year
    """)
    all_years = [row['year'] for row in cursor.fetchall()]
    
    # Track the overall top artists across all years
    cursor.execute("""
        SELECT s.artist, COUNT(*) as total_play_count 
        FROM playlists p
        JOIN songs s ON p.song_id = s.id
        GROUP BY s.artist 
        ORDER BY total_play_count DESC 
        LIMIT 40
    """)
    top_overall_artists = [row['artist'] for row in cursor.fetchall()]
    
    # Also track artists who have been in the top 10 in any year
    cursor.execute("""
        WITH yearly_top_artists AS (
            SELECT 
                strftime('%Y', p.date_play) as year, 
                s.artist, 
                COUNT(*) as play_count,
                RANK() OVER (PARTITION BY strftime('%Y', p.date_play) ORDER BY COUNT(*) DESC) as yearly_rank
            FROM playlists p
            JOIN songs s ON p.song_id = s.id
            GROUP BY year, s.artist
        )
        SELECT DISTINCT artist
        FROM yearly_top_artists
        WHERE yearly_rank <= 10
        ORDER BY artist
    """)
    top10_any_year_artists = [row['artist'] for row in cursor.fetchall()]
    
    # Combine the lists to ensure we track both overall popular artists and those who were top 10 in any year
    artists_to_track = list(set(top_overall_artists + top10_any_year_artists))
    
    # Create a dictionary to track which years each artist appears in
    artist_years = {artist: [] for artist in artists_to_track}
    
    # Get top 100 artists for each year
    artist_rankings = {}
    for year in all_years:
        cursor.execute("""
            SELECT s.artist, COUNT(*) as play_count 
            FROM playlists p
            JOIN songs s ON p.song_id = s.id
            WHERE strftime('%Y', p.date_play) = ?
            GROUP BY s.artist 
            ORDER BY play_count DESC 
            LIMIT 100
        """, (year,))
        results = [dict(row) for row in cursor.fetchall()]
        
        # Add rank information
        for i, artist_data in enumerate(results, 1):
            artist_data['rank'] = i
            # Record which years each tracked artist appears in
            if artist_data['artist'] in artists_to_track:
                artist_years[artist_data['artist']].append(year)
        
        artist_rankings[year] = results
    
    # Prepare a timeline dataset optimized for rank visualization
    artist_rank_timeline = {}
    
    # First pass: add data for artists in their ranked years
    for artist in artists_to_track:
        artist_rank_timeline[artist] = []
        
        for year in all_years:
            year_data = artist_rankings.get(year, [])
            artist_data = next((data for data in year_data if data['artist'] == artist), None)
            
            if artist_data:
                artist_rank_timeline[artist].append({
                    'year': year,
                    'rank': artist_data['rank'],
                    'play_count': artist_data['play_count']
                })
    
    # Second pass: fill in missing years for artists that appear in multiple years
    for artist in artists_to_track:
        # Only process artists that appear in at least 2 years
        years_appeared = artist_years[artist]
        if len(years_appeared) >= 2:
            # Find years where the artist is missing but should be tracked
            years_to_add = []
            
            for i in range(len(all_years) - 1):
                current_year = all_years[i]
                next_year = all_years[i+1]
                
                # If artist appears in current year but not in next year, add next year
                if current_year in years_appeared and next_year not in years_appeared:
                    years_to_add.append(next_year)
                
                # If artist appears in next year but not in current year (gap filling)
                elif current_year not in years_appeared and next_year in years_appeared:
                    # Check if there's a previous year they appeared in
                    if i > 0 and all_years[i-1] in years_appeared:
                        years_to_add.append(current_year)
            
            # Get exact rank and play count for missing years
            for year in years_to_add:
                # Skip if this year was already added in the first pass
                if any(entry['year'] == year for entry in artist_rank_timeline[artist]):
                    continue
                    
                cursor.execute("""
                    WITH ranked_artists AS (
                        SELECT 
                            s.artist, 
                            COUNT(*) as play_count,
                            RANK() OVER (ORDER BY COUNT(*) DESC) as rank
                        FROM playlists p
                        JOIN songs s ON p.song_id = s.id
                        WHERE strftime('%Y', p.date_play) = ?
                        GROUP BY s.artist
                    )
                    SELECT artist, play_count, rank FROM ranked_artists
                    WHERE artist = ?
                """, (year, artist))
                
                extended_data = cursor.fetchone()
                if extended_data:
                    artist_rank_timeline[artist].append({
                        'year': year,
                        'rank': extended_data['rank'],
                        'play_count': extended_data['play_count']
                    })
                else:
                    # If artist has no plays in this year, add with rank 999 and play_count 0
                    # This ensures the artist stays in the timeline but indicates absence
                    artist_rank_timeline[artist].append({
                        'year': year,
                        'rank': 999,  # Special value to indicate absence
                        'play_count': 0
                    })
    
    # Sort each artist's timeline by year
    for artist in artist_rank_timeline:
        artist_rank_timeline[artist].sort(key=lambda x: x['year'])
    
    # Add language metadata
    cursor.execute("""
        SELECT s.artist, s.title, sm.language, json_extract(sm.genre, '$') as genres, sm.publish_date 
        FROM songs s
        JOIN song_metadata sm ON s.id = sm.song_id
        WHERE sm.language IS NOT NULL
    """)
    song_metadata = {}
    for row in cursor.fetchall():
        key = f"{row['artist']} - {row['title']}"
        song_metadata[key] = {
            'language': row['language'],
            'genres': json.loads(row['genres']) if row['genres'] else [],
            'publish_date': row['publish_date']
        }
    
    # Get language statistics by year
    language_by_year = {}
    for year in all_years:
        cursor.execute("""
            SELECT sm.language, COUNT(*) as count
            FROM playlists p
            JOIN songs s ON p.song_id = s.id
            JOIN song_metadata sm ON s.id = sm.song_id
            WHERE strftime('%Y', p.date_play) = ? AND sm.language IS NOT NULL
            GROUP BY sm.language
            ORDER BY count DESC
        """, (year,))
        language_by_year[year] = {row['language']: row['count'] for row in cursor.fetchall()}
    
    # Combine all data
    export_data = {
        'metadata': metadata,
        'top_artists': top_artists,
        'top_songs': top_songs,
        'years_data': years_data,
        'top_artists_by_year': top_artists_by_year,
        'top_songs_by_year': top_songs_by_year,
        'monthly_data_by_year': monthly_data_by_year,
        'artist_rank_timeline': artist_rank_timeline,
        'years_timeline': all_years,
        'song_metadata': song_metadata,
        'language_by_year': language_by_year
    }
    
    # Write to JSON file
    with open('website/data/statistics.json', 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Data exported to website/data/statistics.json")
    conn.close()
    
    # Update README with top artists and songs
    update_readme_with_stats(top_artists[:100], top_songs[:100], metadata)

def update_readme_with_stats(top_artists, top_songs, metadata):
    """Update README.md with tables of top 100 artists and songs and metadata."""
    readme_path = Path("README.md")
    
    if not readme_path.exists():
        logger.info("README.md not found. Creating a new one.")
        readme_content = "# Radio Nowy Świat Statistics\n\n"
    else:
        with open(readme_path, "r", encoding="utf-8") as f:
            readme_content = f.read()
    
    # Create tables for top artists and songs
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Create metadata section
    metadata_section = f"\n## Statistics (as of {current_date})\n\n"
    metadata_section += f"- First play: {metadata['min_date']}\n"
    metadata_section += f"- Latest play: {metadata['max_date']}\n"
    metadata_section += f"- Total plays: {metadata['total_plays']}\n"
    metadata_section += f"- Unique songs: {metadata['total_songs']}\n"
    metadata_section += f"- Songs with metadata: {metadata['songs_with_metadata']} ({metadata['metadata_coverage_percent']}%)\n\n"
    
    # Add language statistics if available
    if 'languages' in metadata and metadata['languages']:
        metadata_section += "### Language Distribution\n\n"
        metadata_section += "| Language | Count | Percentage |\n"
        metadata_section += "|----------|-------|------------|\n"
        
        total_with_language = sum(metadata['languages'].values())
        for lang, count in sorted(metadata['languages'].items(), key=lambda x: x[1], reverse=True):
            percentage = round((count / total_with_language * 100), 2) if total_with_language > 0 else 0
            metadata_section += f"| {lang} | {count} | {percentage}% |\n"
    
    # Create top artists table
    artists_table = f"\n## Top 100 Artists (as of {current_date})\n\n"
    artists_table += "| Rank | Artist | Play Count |\n"
    artists_table += "|------|--------|------------|\n"
    for i, artist in enumerate(top_artists, 1):
        artists_table += f"| {i} | {artist['artist']} | {artist['play_count']} |\n"
    
    # Create top songs table
    songs_table = f"\n## Top 100 Songs (as of {current_date})\n\n"
    songs_table += "| Rank | Artist | Title | Play Count |\n"
    songs_table += "|------|--------|-------|------------|\n"
    for i, song in enumerate(top_songs, 1):
        songs_table += f"| {i} | {song['artist']} | {song['title']} | {song['play_count']} |\n"
    
    # Replace existing sections or append new ones
    sections = {
        "## Statistics": metadata_section,
        "## Top 100 Artists": artists_table,
        "## Top 100 Songs": songs_table
    }
    
    for marker, content in sections.items():
        if marker in readme_content:
            # Find section start
            start = readme_content.find(marker)
            # Find next section or end of content
            next_section = float('inf')
            for m in sections.keys():
                pos = readme_content.find(m, start + len(marker))
                if pos > start and pos < next_section:
                    next_section = pos
            
            if next_section == float('inf'):
                next_section = len(readme_content)
                
            # Replace content
            readme_content = readme_content[:start] + content + readme_content[next_section:]
        else:
            # Append content
            readme_content += content
    
    # Write updated content back to README
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    logger.info(f"README.md updated with statistics and top 100 artists and songs tables.")

if __name__ == "__main__":
    export_data()
