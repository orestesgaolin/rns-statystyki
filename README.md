# Radio Nowy Świat Statistics

This project collects and visualizes statistics from Radio Nowy Świat playlist data.

## Features

- Collects play history from JSON files
- Stores data in SQLite database
- Retrieves metadata for songs (language, genre, etc.) using MusicBrainz API
- Generates statistics including:
  - Top artists
  - Top songs
  - Monthly play counts
  - Yearly trends
  - Language and genre distribution
- Interactive web visualization with filtering by year
- Smart data fetching (resumes from the last fetched date)
- Flexible command-line interface to run specific tasks
- Artist caching system to reduce API calls

## Structure

- `data/` - Contains raw JSON files with playlist data by date
- `website/` - Static website for visualizing the statistics
- `main.py` - Script to process JSON files and create the database
- `metadata.py` - Script to retrieve and process song metadata
- `database.py` - Database utilities and queries
- `export_stats.py` - Script to generate statistics JSON for the website
- `logger_config.py` - Centralized logging configuration
- `logs/` - Directory containing log files
- `playlist.db` - SQLite database with processed data
- `.env` - Configuration file for API key (not tracked in version control)

## Usage

### Configuration

Create a `.env` file in the project root with your API key:

```
RNS_API_KEY=your_api_key_here
```

### Command Line Arguments

The script supports the following command-line arguments:

```
python main.py [options]
```

Options:
- `--fetch` - Fetch data from API and save as JSON files
- `--create-db` - Create or recreate the database
- `--save-to-db` - Process JSON files and save to database
- `--process-metadata` - Process metadata for songs without it
- `--metadata-stats` - Show detailed metadata statistics
- `--api-key KEY` - Override the API key from the .env file
- `--limit N` - Limit metadata processing to N songs
- `--artist TEXT` - Filter songs by artist name substring
- `--exact-artist TEXT` - Filter songs by exact artist name
- `--title TEXT` - Filter songs by title substring
- `--clear-cache` - Clear the artist cache before processing

If no arguments are provided, the fetch, create-db, and save-to-db steps will be executed in sequence.

### Examples

Fetch new data only:
```
python main.py --fetch
```

Recreate the database from existing JSON files:
```
python main.py --create-db --save-to-db
```

Process metadata for songs without it (limited to 100 songs):
```
python main.py --process-metadata --limit 100
```

Show metadata statistics:
```
python main.py --metadata-stats
```

Process metadata for songs by a specific artist:
```
python main.py --process-metadata --artist "The Beatles"
```

Clear the artist cache and process metadata for a specific artist:
```
python main.py --clear-cache --process-metadata --exact-artist "David Bowie"
```

## Metadata Processing

The project uses the MusicBrainz API to retrieve metadata for songs, including:

- **Language**: Determined from the artist's country or area
- **Genre**: Extracted from artist tags
- **Publication Date**: (Where available)

### Artist Caching System

To improve performance and reduce API calls, the system maintains two caches:

1. **Artist Cache**: Stores basic artist information from initial searches
2. **Artist Details Cache**: Stores detailed artist information including tags

The caching system:
- Saves data to disk between runs in `artist_cache.json`
- Caches "not found" artists to avoid redundant searches
- Can be cleared using the `--clear-cache` option

### Logging

All operations are logged to files in the `logs/` directory:
- `rns_main.log` - Main script operations
- `metadata_processing.log` - Metadata retrieval operations
- `db_migration.log` - Database operations
- `export_stats.log` - Statistics export operations

## Updating the Website

After collecting data and processing metadata:

1. Run the export script:
```
python export_stats.py
```

2. This will generate updated JSON files in the `website/data/` directory
3. Open `website/index.html` in a browser to view the statistics

If no arguments are provided, all steps will be executed in sequence.

### Examples

Fetch new data only:
```
python main.py --fetch
```

Recreate the database from existing JSON files:
```
python main.py --create-db --save-to-db
```

Use a custom API key for a single run:
```
python main.py --fetch --api-key your_custom_key
```





## Statistics (as of 2025-08-29)

- First play: 2020-07-10 00:02:00
- Latest play: 2025-08-29 20:19:16
- Total plays: 411105
- Unique songs: 139354
- Songs with metadata: 138341 (99.27%)

### Language Distribution

| Language | Count | Percentage |
|----------|-------|------------|
| en-US | 41593 | 38.87% |
| en-GB | 20996 | 19.62% |
| pl | 14471 | 13.52% |
| fr | 7167 | 6.7% |
| de | 3869 | 3.62% |
| en-CA | 2559 | 2.39% |
| nl | 2012 | 1.88% |
| it | 2007 | 1.88% |
| en-AU | 1754 | 1.64% |
| es | 1641 | 1.53% |
| sv | 1524 | 1.42% |
| pt | 1213 | 1.13% |
| no | 967 | 0.9% |
| en-IE | 898 | 0.84% |
| ja | 786 | 0.73% |
| da | 541 | 0.51% |
| cs | 432 | 0.4% |
| ru | 357 | 0.33% |
| fi | 347 | 0.32% |
| uk | 340 | 0.32% |
| en-NZ | 336 | 0.31% |
| el | 240 | 0.22% |
| hu | 183 | 0.17% |
| ko | 132 | 0.12% |
| hi | 106 | 0.1% |
| ro | 95 | 0.09% |
| hr | 85 | 0.08% |
| sk | 81 | 0.08% |
| zh | 65 | 0.06% |
| sr | 56 | 0.05% |
| id | 56 | 0.05% |
| bg | 41 | 0.04% |
| tl | 34 | 0.03% |
| th | 18 | 0.02% |
| ms | 11 | 0.01% |
| en | 3 | 0.0% |

## Top 100 Artists (as of 2025-08-29)

| Rank | Artist | Play Count |
|------|--------|------------|
| 1 | The Rolling Stones | 1482 |
| 2 | The Beatles | 1229 |
| 3 | David Bowie | 1187 |
| 4 | The Black Keys | 1031 |
| 5 | U2 | 1008 |
| 6 | Fisz Emade Tworzywo | 998 |
| 7 | The Cure | 935 |
| 8 | Sting | 900 |
| 9 | Depeche Mode | 869 |
| 10 | John Mayer | 842 |
| 11 | Lenny Kravitz | 842 |
| 12 | Natalia Przybysz | 774 |
| 13 | Red Hot Chili Peppers | 773 |
| 14 | Maanam | 772 |
| 15 | Bruce Springsteen | 765 |
| 16 | Arctic Monkeys | 745 |
| 17 | Michael Kiwanuka | 732 |
| 18 | Jungle | 730 |
| 19 | Nick Cave & The Bad Seeds | 724 |
| 20 | Foo Fighters | 716 |
| 21 | Pearl Jam | 693 |
| 22 | Queen | 692 |
| 23 | Prince | 673 |
| 24 | Iggy Pop | 668 |
| 25 | Moby | 666 |
| 26 | Amy Winehouse | 664 |
| 27 | Black Pumas | 648 |
| 28 | Coldplay | 642 |
| 29 | Billie Eilish | 630 |
| 30 | Florence + the Machine | 615 |
| 31 | Aretha Franklin | 606 |
| 32 | Voo Voo | 606 |
| 33 | Chumbawamba | 604 |
| 34 | Royal Blood | 594 |
| 35 | Metallica | 593 |
| 36 | Kings of Leon | 591 |
| 37 | Krzysztof Zalewski | 589 |
| 38 | Paolo Nutini | 585 |
| 39 | Arlo Parks | 576 |
| 40 | Brodka | 573 |
| 41 | Elvis Presley | 566 |
| 42 | Greta Van Fleet | 566 |
| 43 | Peter Gabriel | 559 |
| 44 | Foals | 550 |
| 45 | Nirvana | 548 |
| 46 | Stevie Wonder | 534 |
| 47 | Eric Clapton | 533 |
| 48 | Little Simz | 529 |
| 49 | Miles Kane | 526 |
| 50 | Kaleo | 525 |
| 51 | Marvin Gaye | 525 |
| 52 | Morcheeba | 517 |
| 53 | Jack White | 508 |
| 54 | Norah Jones | 505 |
| 55 | PJ Harvey | 502 |
| 56 | Massive Attack | 495 |
| 57 | Jamiroquai | 494 |
| 58 | R.E.M. | 493 |
| 59 | Kate Bush | 492 |
| 60 | Curtis Harding | 491 |
| 61 | Björk | 490 |
| 62 | Broken Bells | 489 |
| 63 | Stereophonics | 487 |
| 64 | Tame Impala | 487 |
| 65 | Led Zeppelin | 484 |
| 66 | Organek | 483 |
| 67 | Kaśka Sochacka | 482 |
| 68 | Johnny Cash | 481 |
| 69 | Alicia Keys | 480 |
| 70 | Joy Crookes | 480 |
| 71 | Bob Dylan | 477 |
| 72 | Chris Stapleton | 469 |
| 73 | Muse | 469 |
| 74 | Fleetwood Mac | 460 |
| 75 | Jessie Ware | 454 |
| 76 | Hozier | 439 |
| 77 | Sault | 438 |
| 78 | Cold War Kids | 436 |
| 79 | John Lennon | 435 |
| 80 | The White Stripes | 435 |
| 81 | Dave Matthews Band | 433 |
| 82 | The Record Company | 432 |
| 83 | Gregory Porter | 431 |
| 84 | Adele | 430 |
| 85 | Jorja Smith | 429 |
| 86 | Lana Del Rey | 426 |
| 87 | Elton John | 425 |
| 88 | Faith No More | 425 |
| 89 | Manic Street Preachers | 418 |
| 90 | Rival Sons | 416 |
| 91 | Radiohead | 415 |
| 92 | Nina Simone | 413 |
| 93 | Black Pistol Fire | 411 |
| 94 | Pink Floyd | 411 |
| 95 | The Heavy | 404 |
| 96 | Wojciech Młynarski | 404 |
| 97 | Blur | 401 |
| 98 | INXS | 401 |
| 99 | The National | 400 |
| 100 | Beth Hart | 399 |

## Top 100 Songs (as of 2025-08-29)

| Rank | Artist | Title | Play Count |
|------|--------|-------|------------|
| 1 | Chumbawamba | Enough Is Enough | 521 |
| 2 | The White Stripes | Fell in Love with a Girl | 237 |
| 3 | Earth | Je mi fajn | 194 |
| 4 | The Alan Parsons Project | Sirius | 189 |
| 5 | Voo Voo | Łajba | 176 |
| 6 | Fisz Emade Tworzywo | Spektrum barw | 169 |
| 7 | Monika Borzym, Kuba Badach, Wojciech Waglewski, Zbigniew Zamachowski | Tango Nowy Świat | 168 |
| 8 | John Mayer | Last Train Home | 164 |
| 9 | Kaśka Sochacka | Niebo było różowe | 153 |
| 10 | Bruce Cockburn | The Blues Got the World... | 152 |
| 11 | Arlo Parks | Hope | 140 |
| 12 | Fisz Emade Tworzywo | Za Mało Czasu | 139 |
| 13 | Tame Impala | The Less I Know the Better | 139 |
| 14 | The Redaktors | Chodź tu | 126 |
| 15 | Florence + the Machine | King | 120 |
| 16 | Black Pumas | Colors | 118 |
| 17 | Iggy Pop | Morning Show | 116 |
| 18 | Iggy Pop | Strung Out Johnny | 113 |
| 19 | The Pretenders | I Didn't Know When to Stop | 112 |
| 20 | Rammstein | Zeit | 106 |
| 21 | The Redaktors | By nie zapeszyć | 106 |
| 22 | Dezerter | Żółć | 104 |
| 23 | Fleetwood Mac | Dreams | 99 |
| 24 | Primal Scream | Movin' on Up | 99 |
| 25 | Sting | Rushing Water | 99 |
| 26 | Maria Peszek | Lovesong | 98 |
| 27 | Natalia Przybysz | Zew | 98 |
| 28 | Brodka | Sadza | 97 |
| 29 | Broken Bells | The Ghost Inside | 97 |
| 30 | Rival Sons | Shooting Stars | 96 |
| 31 | Lianne La Havas | Can't Fight | 95 |
| 32 | Creedence Clearwater Revival | Green River | 94 |
| 33 | The Black Keys | Wild Child | 93 |
| 34 | The Avalanches | Since I Left You | 91 |
| 35 | Mazzy Star | Fade Into You | 90 |
| 36 | Gregory Porter | Revival | 89 |
| 37 | Johnny Cash | Hurt | 89 |
| 38 | Fatboy Slim | Praise You | 88 |
| 39 | The Black Keys | Go | 88 |
| 40 | Cage The Elephant | Ain't No Rest for the Wicked | 87 |
| 41 | Harry Styles | Watermelon Sugar | 87 |
| 42 | Alabama Shakes | Don't Wanna Fight | 86 |
| 43 | Depeche Mode | Policy of Truth | 86 |
| 44 | Stone Temple Pilots | Interstate Love Song | 86 |
| 45 | The Beatles | Something | 86 |
| 46 | Benjamin Booker | Believe | 85 |
| 47 | Michael Kiwanuka | Cold Little Heart | 85 |
| 48 | Otis Redding | Hard to Handle | 85 |
| 49 | Audioslave | Gasoline | 84 |
| 50 | Maanam | Lipstick on the Glass | 84 |
| 51 | Mick Jagger | Strange Game | 84 |
| 52 | The Redaktors | Policzę do trzech | 84 |
| 53 | Travis | Sing | 84 |
| 54 | The Beatles | Here Comes The Sun | 83 |
| 55 | Massive Attack | Unfinished Sympathy | 82 |
| 56 | Black Pistol Fire | Pick Your Poison | 81 |
| 57 | Peter Bjorn And John | Young Folks | 81 |
| 58 | The Buena Vista Social Club | Chan Chan | 81 |
| 59 | Twenty One Pilots | Stressed Out | 81 |
| 60 | Joy Crookes | When You Were Mine | 80 |
| 61 | Krzysztof Zalewski | Ptaki | 80 |
| 62 | Tame Impala | Lost In Yesterday | 80 |
| 63 | The Record Company | Never Leave You | 80 |
| 64 | Asaf Avidan | Love It Or Leave It | 79 |
| 65 | Black Sabbath | Paranoid | 79 |
| 66 | Eddie Vedder | Brother the Cloud | 79 |
| 67 | Lou Reed | Walk On The Wild Side | 79 |
| 68 | Robert Cichy | Piach i wiatr | 79 |
| 69 | Spin Doctors | Two Princes | 79 |
| 70 | TOTO | Hold the Line | 79 |
| 71 | Temple Of The Dog | Hunger Strike | 78 |
| 72 | John Lennon | Imagine | 77 |
| 73 | Kaleo | Break My Baby | 77 |
| 74 | Kate Bush | Running Up That Hill (A Deal with God) | 77 |
| 75 | Polskie Znaki & Mark Lanegan | Oh Angel | 76 |
| 76 | Sault | Why Why Why Why Why | 76 |
| 77 | Grażyna Łobaszewska | Czas nas uczy pogody | 75 |
| 78 | Jessie Ware | Remember Where You Are | 75 |
| 79 | Stone Temple Pilots | Fare Thee Well | 75 |
| 80 | Counting Crows | Mr. Jones | 74 |
| 81 | Eva Cassidy | Wade In The Water | 74 |
| 82 | Fisz Emade Tworzywo | Dwa ognie | 74 |
| 83 | Jeff Buckley | Everybody Here Wants You | 74 |
| 84 | Jungle | All Of The Time | 74 |
| 85 | Morcheeba | Rome Wasn't Built in a Day | 74 |
| 86 | The Strokes | Brooklyn Bridge to Chorus | 74 |
| 87 | Hooverphonic | Summer Sun | 73 |
| 88 | Natalia Przybysz | Oko cyklonu | 73 |
| 89 | The Clash | Rock the Casbah | 73 |
| 90 | The Rolling Stones | Miss You | 73 |
| 91 | Angus & Julia Stone | Grizzly Bear | 72 |
| 92 | Edwyn Collins | A Girl Like You | 72 |
| 93 | Faith No More | Midlife Crisis | 72 |
| 94 | Feist | How Come You Never Go There | 72 |
| 95 | George Michael | Faith | 72 |
| 96 | Guns N' Roses | Welcome To The Jungle | 72 |
| 97 | Pearl Jam | Jeremy | 72 |
| 98 | Charlotte Gainsbourg | The Songs That We Sing | 71 |
| 99 | DJ Shadow | This Time (I'm Gonna Try It My Way) | 71 |
| 100 | Elton John | Rocket Man (I Think It's Going To Be A Long, Long Time) | 71 |
