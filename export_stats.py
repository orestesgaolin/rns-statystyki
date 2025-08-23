import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path

def export_data():
    conn = sqlite3.connect('playlist.db')
    conn.row_factory = sqlite3.Row  # This enables column access by name
    cursor = conn.cursor()

    # Create export directory if it doesn't exist
    os.makedirs('website/data', exist_ok=True)

    # Export metadata
    cursor.execute("SELECT MIN(date_play) as min_date, MAX(date_play) as max_date, COUNT(*) as total_songs FROM songs")
    metadata = dict(cursor.fetchone())
    
    # Ensure dates are formatted consistently
    print(f"Original min_date: {metadata['min_date']}")
    print(f"Original max_date: {metadata['max_date']}")
    
    # No need to modify the dates here, we'll handle the formatting in JavaScript
    
    # Export top artists overall
    cursor.execute("""
        SELECT artist, COUNT(*) as play_count 
        FROM songs 
        GROUP BY artist 
        ORDER BY play_count DESC 
        LIMIT 100
    """)
    top_artists = [dict(row) for row in cursor.fetchall()]
    
    # Export top songs overall
    cursor.execute("""
        SELECT artist, title, COUNT(*) as play_count 
        FROM songs 
        GROUP BY artist, title 
        ORDER BY play_count DESC 
        LIMIT 100
    """)
    top_songs = [dict(row) for row in cursor.fetchall()]
    
    # Export data by year
    cursor.execute("""
        SELECT strftime('%Y', date_play) as year, COUNT(*) as song_count
        FROM songs
        GROUP BY year
        ORDER BY year
    """)
    years_data = []
    for row in cursor.fetchall():
        year_data = dict(row)
        # Make sure year is included properly
        years_data.append(year_data)
    
    # Export top artists by year (last 6 years)
    years = [row['year'] for row in years_data][-6:]
    top_artists_by_year = {}
    
    for year in years:
        cursor.execute("""
            SELECT artist, COUNT(*) as play_count 
            FROM songs 
            WHERE strftime('%Y', date_play) = ?
            GROUP BY artist 
            ORDER BY play_count DESC 
            LIMIT 20
        """, (year,))
        top_artists_by_year[year] = [dict(row) for row in cursor.fetchall()]
    
    # Export top songs by year (last 6 years)
    top_songs_by_year = {}
    
    for year in years:
        cursor.execute("""
            SELECT artist, title, COUNT(*) as play_count 
            FROM songs 
            WHERE strftime('%Y', date_play) = ?
            GROUP BY artist, title 
            ORDER BY play_count DESC 
            LIMIT 20
        """, (year,))
        top_songs_by_year[year] = [dict(row) for row in cursor.fetchall()]
    
    # Export monthly data for each year
    cursor.execute("""
        SELECT strftime('%Y', date_play) as year, 
               strftime('%m', date_play) as month, 
               COUNT(*) as song_count
        FROM songs
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
    
    # Combine all data
    export_data = {
        'metadata': metadata,
        'top_artists': top_artists,
        'top_songs': top_songs,
        'years_data': years_data,
        'top_artists_by_year': top_artists_by_year,
        'top_songs_by_year': top_songs_by_year,
        'monthly_data_by_year': monthly_data_by_year,
    }
    
    # Write to JSON file
    with open('website/data/statistics.json', 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    print(f"Data exported to website/data/statistics.json")
    conn.close()
    
    # Update README with top artists and songs
    update_readme_with_stats(top_artists[:100], top_songs[:100])

def update_readme_with_stats(top_artists, top_songs):
    """Update README.md with tables of top 100 artists and songs."""
    readme_path = Path("README.md")
    
    if not readme_path.exists():
        print("README.md not found. Creating a new one.")
        readme_content = "# Radio Nowy Świat Statistics\n\n"
    else:
        with open(readme_path, "r", encoding="utf-8") as f:
            readme_content = f.read()
    
    # Create tables for top artists and songs
    current_date = datetime.now().strftime("%Y-%m-%d")
    
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
    
    # Replace existing tables or append new ones
    if "## Top 100 Artists" in readme_content:
        # Replace existing tables by finding sections and replacing them
        start_artists = readme_content.find("## Top 100 Artists")
        end_artists = readme_content.find("##", start_artists + 1)
        if end_artists == -1:  # If no section follows
            end_artists = len(readme_content)
        
        start_songs = readme_content.find("## Top 100 Songs")
        if start_songs != -1:
            end_songs = readme_content.find("##", start_songs + 1)
            if end_songs == -1:  # If no section follows
                end_songs = len(readme_content)
            
            # If both sections exist
            if start_artists < start_songs:
                # Replace songs section first (from the end)
                readme_content = readme_content[:start_songs] + songs_table + readme_content[end_songs:]
                # Then replace artists section
                readme_content = readme_content[:start_artists] + artists_table + readme_content[start_songs:]
            else:
                # Replace artists section first (from the end)
                readme_content = readme_content[:start_artists] + artists_table + readme_content[end_artists:]
                # Then replace songs section
                readme_content = readme_content[:start_songs] + songs_table + readme_content[end_songs:]
        else:
            # Only artists section exists
            readme_content = readme_content[:start_artists] + artists_table + readme_content[end_artists:] + songs_table
    else:
        # Append both tables to the end
        readme_content += artists_table + songs_table
    
    # Write updated content back to README
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print(f"README.md updated with top 100 artists and songs tables.")

if __name__ == "__main__":
    export_data()
