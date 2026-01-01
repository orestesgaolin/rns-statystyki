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







## Statistics (as of 2026-01-01)

- First play: 2020-07-10 00:02:00
- Latest play: 2026-01-01 16:04:03
- Total plays: 444051
- Unique songs: 148489
- Songs with metadata: 138341 (93.17%)

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

## Top 100 Artists (as of 2026-01-01)

| Rank | Artist | Play Count |
|------|--------|------------|
| 1 | The Rolling Stones | 1559 |
| 2 | The Beatles | 1275 |
| 3 | David Bowie | 1238 |
| 4 | The Black Keys | 1052 |
| 5 | Fisz Emade Tworzywo | 1037 |
| 6 | U2 | 1023 |
| 7 | The Cure | 970 |
| 8 | Sting | 924 |
| 9 | Depeche Mode | 913 |
| 10 | Lenny Kravitz | 884 |
| 11 | John Mayer | 868 |
| 12 | Natalia Przybysz | 842 |
| 13 | Bruce Springsteen | 829 |
| 14 | Red Hot Chili Peppers | 804 |
| 15 | Maanam | 799 |
| 16 | Jungle | 790 |
| 17 | Foo Fighters | 778 |
| 18 | Nick Cave & The Bad Seeds | 778 |
| 19 | Arctic Monkeys | 762 |
| 20 | Queen | 752 |
| 21 | Michael Kiwanuka | 737 |
| 22 | Moby | 716 |
| 23 | Iggy Pop | 711 |
| 24 | Pearl Jam | 708 |
| 25 | Prince | 700 |
| 26 | Black Pumas | 699 |
| 27 | Florence + the Machine | 683 |
| 28 | Amy Winehouse | 673 |
| 29 | Coldplay | 670 |
| 30 | Voo Voo | 659 |
| 31 | Kings of Leon | 649 |
| 32 | Billie Eilish | 643 |
| 33 | Metallica | 638 |
| 34 | Royal Blood | 627 |
| 35 | Aretha Franklin | 623 |
| 36 | Arlo Parks | 612 |
| 37 | Chumbawamba | 611 |
| 38 | Peter Gabriel | 606 |
| 39 | Krzysztof Zalewski | 603 |
| 40 | Brodka | 602 |
| 41 | Elvis Presley | 598 |
| 42 | Miles Kane | 594 |
| 43 | Foals | 592 |
| 44 | Greta Van Fleet | 588 |
| 45 | Paolo Nutini | 588 |
| 46 | Nirvana | 575 |
| 47 | Stevie Wonder | 570 |
| 48 | Little Simz | 568 |
| 49 | Eric Clapton | 561 |
| 50 | Kaleo | 559 |
| 51 | Marvin Gaye | 546 |
| 52 | PJ Harvey | 544 |
| 53 | Norah Jones | 541 |
| 54 | Tame Impala | 536 |
| 55 | Johnny Cash | 530 |
| 56 | Morcheeba | 527 |
| 57 | Kate Bush | 526 |
| 58 | Joy Crookes | 524 |
| 59 | R.E.M. | 523 |
| 60 | Björk | 522 |
| 61 | Broken Bells | 522 |
| 62 | Jack White | 522 |
| 63 | Led Zeppelin | 521 |
| 64 | Jamiroquai | 517 |
| 65 | Massive Attack | 516 |
| 66 | Bob Dylan | 513 |
| 67 | Kaśka Sochacka | 513 |
| 68 | Stereophonics | 513 |
| 69 | Curtis Harding | 509 |
| 70 | Organek | 505 |
| 71 | Muse | 500 |
| 72 | Alicia Keys | 498 |
| 73 | Jessie Ware | 488 |
| 74 | Fleetwood Mac | 487 |
| 75 | Chris Stapleton | 482 |
| 76 | Cold War Kids | 478 |
| 77 | Hozier | 478 |
| 78 | Dave Matthews Band | 475 |
| 79 | Jorja Smith | 474 |
| 80 | John Lennon | 463 |
| 81 | The White Stripes | 463 |
| 82 | Lana Del Rey | 452 |
| 83 | The Record Company | 452 |
| 84 | Elton John | 451 |
| 85 | Rival Sons | 447 |
| 86 | Sault | 446 |
| 87 | Queens of the Stone Age | 445 |
| 88 | Radiohead | 444 |
| 89 | Gregory Porter | 442 |
| 90 | Alabama Shakes | 441 |
| 91 | The National | 439 |
| 92 | Pink Floyd | 438 |
| 93 | Faith No More | 437 |
| 94 | The Heavy | 435 |
| 95 | Adele | 434 |
| 96 | Black Pistol Fire | 433 |
| 97 | Manic Street Preachers | 431 |
| 98 | Nina Simone | 431 |
| 99 | Dezerter | 426 |
| 100 | Guns N' Roses | 426 |

## Top 100 Songs (as of 2026-01-01)

| Rank | Artist | Title | Play Count |
|------|--------|-------|------------|
| 1 | Chumbawamba | Enough Is Enough | 521 |
| 2 | The White Stripes | Fell in Love with a Girl | 254 |
| 3 | The Alan Parsons Project | Sirius | 204 |
| 4 | Earth | Je mi fajn | 196 |
| 5 | Voo Voo | Łajba | 180 |
| 6 | Monika Borzym, Kuba Badach, Wojciech Waglewski, Zbigniew Zamachowski | Tango Nowy Świat | 172 |
| 7 | Bruce Cockburn | The Blues Got the World... | 170 |
| 8 | Fisz Emade Tworzywo | Spektrum barw | 170 |
| 9 | John Mayer | Last Train Home | 164 |
| 10 | Kaśka Sochacka | Niebo było różowe | 153 |
| 11 | Arlo Parks | Hope | 144 |
| 12 | Fisz Emade Tworzywo | Za Mało Czasu | 140 |
| 13 | Tame Impala | The Less I Know the Better | 140 |
| 14 | The Redaktors | Chodź tu | 130 |
| 15 | Florence + the Machine | King | 125 |
| 16 | Dezerter | Żółć | 122 |
| 17 | Iggy Pop | Strung Out Johnny | 120 |
| 18 | Black Pumas | Colors | 119 |
| 19 | Iggy Pop | Morning Show | 116 |
| 20 | The Pretenders | I Didn't Know When to Stop | 112 |
| 21 | The Redaktors | By nie zapeszyć | 110 |
| 22 | Rammstein | Zeit | 106 |
| 23 | Sting | Rushing Water | 104 |
| 24 | Broken Bells | The Ghost Inside | 101 |
| 25 | Creedence Clearwater Revival | Green River | 101 |
| 26 | Fleetwood Mac | Dreams | 101 |
| 27 | Natalia Przybysz | Zew | 100 |
| 28 | Maria Peszek | Lovesong | 99 |
| 29 | Primal Scream | Movin' on Up | 99 |
| 30 | Brodka | Sadza | 97 |
| 31 | Mazzy Star | Fade Into You | 97 |
| 32 | Rival Sons | Shooting Stars | 97 |
| 33 | Johnny Cash | Hurt | 95 |
| 34 | Lianne La Havas | Can't Fight | 95 |
| 35 | The Black Keys | Wild Child | 94 |
| 36 | Fatboy Slim | Praise You | 93 |
| 37 | The Avalanches | Since I Left You | 92 |
| 38 | Alabama Shakes | Don't Wanna Fight | 91 |
| 39 | Gregory Porter | Revival | 91 |
| 40 | Harry Styles | Watermelon Sugar | 91 |
| 41 | Benjamin Booker | Believe | 90 |
| 42 | The Black Keys | Go | 88 |
| 43 | Cage The Elephant | Ain't No Rest for the Wicked | 87 |
| 44 | Depeche Mode | Policy of Truth | 87 |
| 45 | Otis Redding | Hard to Handle | 87 |
| 46 | Peter Bjorn And John | Young Folks | 87 |
| 47 | Stone Temple Pilots | Interstate Love Song | 86 |
| 48 | The Beatles | Something | 86 |
| 49 | The Buena Vista Social Club | Chan Chan | 86 |
| 50 | Audioslave | Gasoline | 85 |
| 51 | Black Sabbath | Paranoid | 85 |
| 52 | Maanam | Lipstick on the Glass | 85 |
| 53 | Michael Kiwanuka | Cold Little Heart | 85 |
| 54 | Massive Attack | Unfinished Sympathy | 84 |
| 55 | Mick Jagger | Strange Game | 84 |
| 56 | The Redaktors | Policzę do trzech | 84 |
| 57 | Travis | Sing | 84 |
| 58 | Asaf Avidan | Love It Or Leave It | 83 |
| 59 | Spin Doctors | Two Princes | 83 |
| 60 | TOTO | Hold the Line | 83 |
| 61 | The Beatles | Here Comes The Sun | 83 |
| 62 | Kate Bush | Running Up That Hill (A Deal with God) | 82 |
| 63 | Black Pistol Fire | Pick Your Poison | 81 |
| 64 | John Lennon | Imagine | 81 |
| 65 | Tame Impala | Lost In Yesterday | 81 |
| 66 | Twenty One Pilots | Stressed Out | 81 |
| 67 | Joy Crookes | When You Were Mine | 80 |
| 68 | Krzysztof Zalewski | Ptaki | 80 |
| 69 | Lou Reed | Walk On The Wild Side | 80 |
| 70 | Stone Temple Pilots | Fare Thee Well | 80 |
| 71 | The Record Company | Never Leave You | 80 |
| 72 | Eddie Vedder | Brother the Cloud | 79 |
| 73 | Robert Cichy | Piach i wiatr | 79 |
| 74 | The Strokes | Brooklyn Bridge to Chorus | 79 |
| 75 | Counting Crows | Mr. Jones | 78 |
| 76 | Eva Cassidy | Wade In The Water | 78 |
| 77 | Grażyna Łobaszewska | Czas nas uczy pogody | 78 |
| 78 | Jungle | All Of The Time | 78 |
| 79 | Temple Of The Dog | Hunger Strike | 78 |
| 80 | America | A Horse with No Name | 77 |
| 81 | Faith No More | Midlife Crisis | 77 |
| 82 | Guns N' Roses | Welcome To The Jungle | 77 |
| 83 | Hooverphonic | Summer Sun | 77 |
| 84 | Kaleo | Break My Baby | 77 |
| 85 | Natalia Przybysz | Oko cyklonu | 77 |
| 86 | Polskie Znaki & Mark Lanegan | Oh Angel | 77 |
| 87 | Jessie Ware | Remember Where You Are | 76 |
| 88 | Sault | Why Why Why Why Why | 76 |
| 89 | Balthazar | Halfway | 75 |
| 90 | DJ Shadow | This Time (I'm Gonna Try It My Way) | 75 |
| 91 | Edwyn Collins | A Girl Like You | 75 |
| 92 | Elton John | Rocket Man (I Think It's Going To Be A Long, Long Time) | 75 |
| 93 | Fisz Emade Tworzywo | Dwa ognie | 75 |
| 94 | Morcheeba | Rome Wasn't Built in a Day | 75 |
| 95 | Nirvana | The Man Who Sold The World | 75 |
| 96 | The Rolling Stones | Miss You | 75 |
| 97 | The Stranglers | Golden Brown | 75 |
| 98 | Iggy Pop | James Bond | 74 |
| 99 | Jeff Buckley | Everybody Here Wants You | 74 |
| 100 | Kaleo | Hey Gringo | 74 |
