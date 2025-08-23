# Radio Nowy Świat Statistics

This project collects and visualizes statistics from Radio Nowy Świat playlist data.

## Features

- Collects play history from JSON files
- Stores data in SQLite database
- Generates statistics including:
  - Top artists
  - Top songs
  - Monthly play counts
  - Yearly trends
- Interactive web visualization with filtering by year
- Smart data fetching (resumes from the last fetched date)
- Flexible command-line interface to run specific tasks

## Structure

- `data/` - Contains raw JSON files with playlist data by date
- `website/` - Static website for visualizing the statistics
- `main.py` - Script to process JSON files and create the database
- `export_stats.py` - Script to generate statistics JSON for the website
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
- `--api-key KEY` - Override the API key from the .env file

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


## Top 100 Artists (as of 2025-08-23)

| Rank | Artist | Play Count |
|------|--------|------------|
| 1 | The Rolling Stones | 1477 |
| 2 | The Beatles | 1229 |
| 3 | David Bowie | 1184 |
| 4 | The Black Keys | 1028 |
| 5 | U2 | 1008 |
| 6 | Fisz Emade Tworzywo | 996 |
| 7 | The Cure | 932 |
| 8 | Sting | 898 |
| 9 | Depeche Mode | 868 |
| 10 | John Mayer | 841 |
| 11 | Lenny Kravitz | 840 |
| 12 | Natalia Przybysz | 772 |
| 13 | Red Hot Chili Peppers | 771 |
| 14 | Bruce Springsteen | 762 |
| 15 | Maanam | 758 |
| 16 | Arctic Monkeys | 744 |
| 17 | Michael Kiwanuka | 731 |
| 18 | Jungle | 725 |
| 19 | Nick Cave & The Bad Seeds | 722 |
| 20 | Foo Fighters | 712 |
| 21 | Queen | 692 |
| 22 | Pearl Jam | 692 |
| 23 | Prince | 669 |
| 24 | Iggy Pop | 665 |
| 25 | Amy Winehouse | 664 |
| 26 | Moby | 661 |
| 27 | Black Pumas | 645 |
| 28 | Coldplay | 641 |
| 29 | Billie Eilish | 629 |
| 30 | Florence + the Machine | 606 |
| 31 | Voo Voo | 605 |
| 32 | Chumbawamba | 604 |
| 33 | Aretha Franklin | 604 |
| 34 | Royal Blood | 592 |
| 35 | Krzysztof Zalewski | 589 |
| 36 | Metallica | 588 |
| 37 | Kings of Leon | 588 |
| 38 | Paolo Nutini | 585 |
| 39 | Arlo Parks | 575 |
| 40 | Brodka | 572 |
| 41 | Elvis Presley | 565 |
| 42 | Greta Van Fleet | 564 |
| 43 | Peter Gabriel | 557 |
| 44 | Foals | 549 |
| 45 | Nirvana | 547 |
| 46 | Stevie Wonder | 534 |
| 47 | Eric Clapton | 532 |
| 48 | Little Simz | 528 |
| 49 | Marvin Gaye | 524 |
| 50 | Kaleo | 524 |
| 51 | Miles Kane | 523 |
| 52 | Morcheeba | 517 |
| 53 | Jack White | 507 |
| 54 | Norah Jones | 504 |
| 55 | PJ Harvey | 501 |
| 56 | Massive Attack | 495 |
| 57 | Jamiroquai | 493 |
| 58 | R.E.M. | 491 |
| 59 | Kate Bush | 491 |
| 60 | Curtis Harding | 490 |
| 61 | Broken Bells | 489 |
| 62 | Björk | 489 |
| 63 | Tame Impala | 486 |
| 64 | Stereophonics | 486 |
| 65 | Organek | 482 |
| 66 | Led Zeppelin | 482 |
| 67 | Kaśka Sochacka | 481 |
| 68 | Johnny Cash | 480 |
| 69 | Alicia Keys | 479 |
| 70 | Joy Crookes | 477 |
| 71 | Bob Dylan | 475 |
| 72 | Chris Stapleton | 469 |
| 73 | Muse | 467 |
| 74 | Fleetwood Mac | 459 |
| 75 | Jessie Ware | 453 |
| 76 | Hozier | 438 |
| 77 | Sault | 436 |
| 78 | The White Stripes | 434 |
| 79 | John Lennon | 434 |
| 80 | Cold War Kids | 434 |
| 81 | The Record Company | 431 |
| 82 | Gregory Porter | 431 |
| 83 | Dave Matthews Band | 431 |
| 84 | Adele | 430 |
| 85 | Jorja Smith | 428 |
| 86 | Lana Del Rey | 425 |
| 87 | Faith No More | 424 |
| 88 | Elton John | 423 |
| 89 | Manic Street Preachers | 418 |
| 90 | Rival Sons | 415 |
| 91 | Radiohead | 414 |
| 92 | Nina Simone | 413 |
| 93 | Pink Floyd | 411 |
| 94 | Black Pistol Fire | 410 |
| 95 | Wojciech Młynarski | 404 |
| 96 | The Heavy | 401 |
| 97 | Blur | 401 |
| 98 | INXS | 400 |
| 99 | Beth Hart | 399 |
| 100 | The National | 398 |

## Top 100 Songs (as of 2025-08-23)

| Rank | Artist | Title | Play Count |
|------|--------|-------|------------|
| 1 | Chumbawamba | Enough Is Enough | 521 |
| 2 | The White Stripes | Fell in Love with a Girl | 237 |
| 3 | Earth | Je mi fajn | 193 |
| 4 | The Alan Parsons Project | Sirius | 188 |
| 5 | Voo Voo | Łajba | 175 |
| 6 | Fisz Emade Tworzywo | Spektrum barw | 169 |
| 7 | Monika Borzym, Kuba Badach, Wojciech Waglewski, Zbigniew Zamachowski | Tango Nowy Świat | 168 |
| 8 | John Mayer | Last Train Home | 164 |
| 9 | Kaśka Sochacka | Niebo było różowe | 153 |
| 10 | Bruce Cockburn | The Blues Got the World... | 151 |
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
| 21 | The Redaktors | By nie zapeszyć | 105 |
| 22 | Dezerter | Żółć | 103 |
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
| 33 | The Black Keys | Wild Child | 92 |
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
| 70 | TOTO | Hold the Line | 78 |
| 71 | Temple Of The Dog | Hunger Strike | 78 |
| 72 | John Lennon | Imagine | 77 |
| 73 | Kaleo | Break My Baby | 77 |
| 74 | Kate Bush | Running Up That Hill (A Deal with God) | 77 |
| 75 | Polskie Znaki & Mark Lanegan | Oh Angel | 76 |
| 76 | Sault | Why Why Why Why Why | 76 |
| 77 | Grażyna Łobaszewska | Czas nas uczy pogody | 75 |
| 78 | Jessie Ware | Remember Where You Are | 75 |
| 79 | Counting Crows | Mr. Jones | 74 |
| 80 | Fisz Emade Tworzywo | Dwa ognie | 74 |
| 81 | Jeff Buckley | Everybody Here Wants You | 74 |
| 82 | Morcheeba | Rome Wasn't Built in a Day | 74 |
| 83 | Stone Temple Pilots | Fare Thee Well | 74 |
| 84 | The Strokes | Brooklyn Bridge to Chorus | 74 |
| 85 | Eva Cassidy | Wade In The Water | 73 |
| 86 | Jungle | All Of The Time | 73 |
| 87 | The Clash | Rock the Casbah | 73 |
| 88 | The Rolling Stones | Miss You | 73 |
| 89 | Angus & Julia Stone | Grizzly Bear | 72 |
| 90 | Feist | How Come You Never Go There | 72 |
| 91 | George Michael | Faith | 72 |
| 92 | Guns N' Roses | Welcome To The Jungle | 72 |
| 93 | Hooverphonic | Summer Sun | 72 |
| 94 | Natalia Przybysz | Oko cyklonu | 72 |
| 95 | Pearl Jam | Jeremy | 72 |
| 96 | Charlotte Gainsbourg | The Songs That We Sing | 71 |
| 97 | Edwyn Collins | A Girl Like You | 71 |
| 98 | Faith No More | Midlife Crisis | 71 |
| 99 | Fisz Emade Tworzywo | Wolne Dni | 71 |
| 100 | Iggy Pop | James Bond | 71 |
