// Global variables
let statisticsData = null;
let currentYearFilter = 'all';

// Fetch the JSON data
async function fetchData() {
    try {
        const response = await fetch('data/statistics.json');
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        statisticsData = await response.json();
        initializeWebsite();
    } catch (error) {
        console.error('Error fetching data:', error);
        document.body.innerHTML = `<div class="error">Failed to load data. Please try again later.</div>`;
    }
}

// Initialize all website components
function initializeWebsite() {
    populateYearSelector();
    updateLastUpdateDate();
    renderSummaryStats();
    renderMonthlyData();
    renderTopArtistsData();
    renderTopSongsData();
    populateDataBrowser();
    setupEventListeners();
}

// Populate the year selector dropdown
function populateYearSelector() {
    const yearSelect = document.getElementById('year-select');
    // Extract all years from the years_data array
    const years = Object.keys(statisticsData.top_artists_by_year);

    years.forEach(year => {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year;
        yearSelect.appendChild(option);
    });
}

// Update the last update date
function updateLastUpdateDate() {
    const lastUpdateElement = document.getElementById('last-update');
    const currentDate = new Date();
    lastUpdateElement.textContent = currentDate.toLocaleDateString('pl-PL');
}

// Render summary statistics
function renderSummaryStats() {
    const summaryElement = document.getElementById('summary-stats');
    const metadata = statisticsData.metadata;

    // Format dates
    const minDate = new Date(metadata.min_date);
    const maxDate = new Date(metadata.max_date);

    const filteredSongCount = currentYearFilter === 'all'
        ? metadata.total_songs
        : statisticsData.years_data.find(y => y.year === currentYearFilter)?.song_count || 0;

    summaryElement.innerHTML = `
        <div class="summary-item">
            <span class="summary-label">Całkowita liczba odtworzeń:</span>
            <span class="summary-value">${filteredSongCount.toLocaleString('pl-PL')}</span>
        </div>
        <div class="summary-item">
            <span class="summary-label">Pierwsze odtworzenie:</span>
            <span class="summary-value">${minDate.toLocaleDateString('pl-PL')}</span>
        </div>
        <div class="summary-item">
            <span class="summary-label">Ostatnie odtworzenie:</span>
            <span class="summary-value">${maxDate.toLocaleDateString('pl-PL')}</span>
        </div>
    `;
}

// Render monthly data (both chart and table)
function renderMonthlyData() {
    renderMonthlyChart();
    renderMonthlyTable();
}

// Render monthly chart
function renderMonthlyChart() {
    const chartElement = document.getElementById('monthly-chart');

    // Filter data by selected year
    let monthlyData;
    if (currentYearFilter === 'all') {
        // Aggregate all years
        const allMonthlyData = {};
        Object.entries(statisticsData.monthly_data_by_year).forEach(([year, monthsData]) => {
            monthsData.forEach(monthData => {
                const month = monthData.month;
                if (!allMonthlyData[month]) {
                    allMonthlyData[month] = 0;
                }
                allMonthlyData[month] += monthData.song_count;
            });
        });

        monthlyData = Object.entries(allMonthlyData).map(([month, song_count]) => ({
            month,
            song_count
        })).sort((a, b) => Number(a.month) - Number(b.month));
    } else {
        monthlyData = statisticsData.monthly_data_by_year[currentYearFilter] || [];
    }

    // Prepare data for Plotly
    const months = ['Styczeń', 'Luty', 'Marzec', 'Kwiecień', 'Maj', 'Czerwiec',
        'Lipiec', 'Sierpień', 'Wrzesień', 'Październik', 'Listopad', 'Grudzień'];

    const monthNumbers = monthlyData.map(d => Number(d.month));
    const monthNames = monthNumbers.map(num => months[num - 1]);
    const songCounts = monthlyData.map(d => d.song_count);

    const data = [{
        x: monthNames,
        y: songCounts,
        type: 'bar',
        marker: {
            color: '#e60000'
        }
    }];

    const layout = {
        title: currentYearFilter === 'all' ? 'Miesięczne odtworzenia (wszystkie lata)' : `Miesięczne odtworzenia (${currentYearFilter})`,
        xaxis: { title: 'Miesiąc' },
        yaxis: { title: 'Liczba odtworzeń' },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: { color: '#000000' },
        margin: { l: 60, r: 30, t: 50, b: 80 }
    };

    Plotly.newPlot(chartElement, data, layout);
}

// Render monthly table
function renderMonthlyTable() {
    const tableElement = document.getElementById('monthly-table');

    // Filter data by selected year (same as in renderMonthlyChart)
    let monthlyData;
    if (currentYearFilter === 'all') {
        // Aggregate all years
        const allMonthlyData = {};
        Object.entries(statisticsData.monthly_data_by_year).forEach(([year, monthsData]) => {
            monthsData.forEach(monthData => {
                const month = monthData.month;
                if (!allMonthlyData[month]) {
                    allMonthlyData[month] = 0;
                }
                allMonthlyData[month] += monthData.song_count;
            });
        });

        monthlyData = Object.entries(allMonthlyData).map(([month, song_count]) => ({
            month,
            song_count
        })).sort((a, b) => Number(a.month) - Number(b.month));
    } else {
        monthlyData = statisticsData.monthly_data_by_year[currentYearFilter] || [];
    }

    const months = ['Styczeń', 'Luty', 'Marzec', 'Kwiecień', 'Maj', 'Czerwiec',
        'Lipiec', 'Sierpień', 'Wrzesień', 'Październik', 'Listopad', 'Grudzień'];

    // Create HTML table
    let tableHTML = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>Miesiąc</th>
                    <th>Liczba odtworzeń</th>
                </tr>
            </thead>
            <tbody>
    `;

    monthlyData.forEach(data => {
        const monthName = months[Number(data.month) - 1];
        tableHTML += `
            <tr>
                <td>${monthName}</td>
                <td>${data.song_count.toLocaleString('pl-PL')}</td>
            </tr>
        `;
    });

    tableHTML += `
            </tbody>
        </table>
    `;

    tableElement.innerHTML = tableHTML;
}

// Render top artists data (both chart and table)
function renderTopArtistsData() {
    renderTopArtistsChart();
    renderTopArtistsTable();
}

// Render top artists chart
function renderTopArtistsChart() {
    const chartElement = document.getElementById('top-artists-chart');

    // Filter data by selected year
    let artistsData;
    if (currentYearFilter === 'all') {
        artistsData = statisticsData.top_artists.slice(0, 20);
    } else {
        artistsData = statisticsData.top_artists_by_year[currentYearFilter] || [];
    }

    // Prepare data for Plotly
    const artists = artistsData.map(d => d.artist);
    const playCounts = artistsData.map(d => d.play_count);

    // Sort data by play count (already sorted, but ensure order)
    const sortedIndices = playCounts.map((_, i) => i)
        .sort((a, b) => playCounts[b] - playCounts[a]);

    // Truncate artist names if too long
    const sortedArtists = sortedIndices.map(i => {
        const name = artists[i];
        return name.length > 30 ? name.substring(0, 27) + '...' : name;
    });
    const sortedPlayCounts = sortedIndices.map(i => playCounts[i]);

    const data = [{
        y: sortedArtists,
        x: sortedPlayCounts,
        type: 'bar',
        orientation: 'h',
        marker: {
            color: '#e60000'
        }
    }];

    const layout = {
        title: currentYearFilter === 'all' ? 'Top 20 artystów (wszystkie lata)' : `Top 20 artystów (${currentYearFilter})`,
        xaxis: { title: 'Liczba odtworzeń' },
        yaxis: { title: 'Artysta', automargin: true },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: { color: '#000000' },
        yaxis: { autorange: 'reversed' },
        margin: { l: 180, r: 30, t: 50, b: 50 }
    };

    Plotly.newPlot(chartElement, data, layout);
}

// Render top artists table
function renderTopArtistsTable() {
    const tableElement = document.getElementById('top-artists-table');

    // Filter data by selected year (same as in renderTopArtistsChart)
    let artistsData;
    if (currentYearFilter === 'all') {
        artistsData = statisticsData.top_artists.slice(0, 20);
    } else {
        artistsData = statisticsData.top_artists_by_year[currentYearFilter] || [];
    }

    // Sort data by play count descending
    artistsData.sort((a, b) => b.play_count - a.play_count);

    // Create HTML table
    let tableHTML = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>Pozycja</th>
                    <th>Artysta</th>
                    <th>Liczba odtworzeń</th>
                </tr>
            </thead>
            <tbody>
    `;

    artistsData.forEach((artist, index) => {
        tableHTML += `
            <tr>
                <td>${index + 1}</td>
                <td>${artist.artist}</td>
                <td>${artist.play_count.toLocaleString('pl-PL')}</td>
            </tr>
        `;
    });

    tableHTML += `
            </tbody>
        </table>
    `;

    tableElement.innerHTML = tableHTML;
}

// Render top songs data (both chart and table)
function renderTopSongsData() {
    renderTopSongsChart();
    renderTopSongsTable();
}

// Render top songs chart
function renderTopSongsChart() {
    const chartElement = document.getElementById('top-songs-chart');

    // Filter data by selected year
    let songsData;
    if (currentYearFilter === 'all') {
        songsData = statisticsData.top_songs.slice(0, 20);
    } else {
        songsData = statisticsData.top_songs_by_year[currentYearFilter] || [];
    }

    // Prepare data for Plotly
    const songLabels = songsData.map(d => `${d.artist} - ${d.title}`);
    const playCounts = songsData.map(d => d.play_count);

    // Sort data by play count (already sorted, but ensure order)
    const sortedIndices = playCounts.map((_, i) => i)
        .sort((a, b) => playCounts[b] - playCounts[a]);

    // Truncate song labels if too long
    const sortedSongs = sortedIndices.map(i => {
        const label = songLabels[i];
        return label.length > 30 ? label.substring(0, 27) + '...' : label;
    });
    const sortedPlayCounts = sortedIndices.map(i => playCounts[i]);

    const data = [{
        y: sortedSongs,
        x: sortedPlayCounts,
        type: 'bar',
        orientation: 'h',
        marker: {
            color: '#e60000'
        }
    }];

    const layout = {
        title: currentYearFilter === 'all' ? 'Top 20 utworów (wszystkie lata)' : `Top 20 utworów (${currentYearFilter})`,
        xaxis: { title: 'Liczba odtworzeń' },
        yaxis: { title: 'Utwór', automargin: true },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: { color: '#000000' },
        yaxis: { autorange: 'reversed' },
        margin: { l: 220, r: 30, t: 50, b: 50 }
    };

    Plotly.newPlot(chartElement, data, layout);
}

// Render top songs table
function renderTopSongsTable() {
    const tableElement = document.getElementById('top-songs-table');

    // Filter data by selected year (same as in renderTopSongsChart)
    let songsData;
    if (currentYearFilter === 'all') {
        songsData = statisticsData.top_songs.slice(0, 20);
    } else {
        songsData = statisticsData.top_songs_by_year[currentYearFilter] || [];
    }

    // Sort data by play count descending
    songsData.sort((a, b) => b.play_count - a.play_count);

    // Create HTML table
    let tableHTML = `
        <table class="data-table">
            <thead>
                <tr>
                    <th>Pozycja</th>
                    <th>Artysta</th>
                    <th>Tytuł</th>
                    <th>Liczba odtworzeń</th>
                </tr>
            </thead>
            <tbody>
    `;

    songsData.forEach((song, index) => {
        tableHTML += `
            <tr>
                <td>${index + 1}</td>
                <td>${song.artist}</td>
                <td>${song.title}</td>
                <td>${song.play_count.toLocaleString('pl-PL')}</td>
            </tr>
        `;
    });

    tableHTML += `
            </tbody>
        </table>
    `;

    tableElement.innerHTML = tableHTML;
}

// Populate data browser with lists of artists and songs
function populateDataBrowser() {
    populateArtistsList();
    populateSongsList();
}

// Populate artists list
function populateArtistsList() {
    const artistsListElement = document.getElementById('artists-list');

    // Filter data by selected year
    let artistsData;
    if (currentYearFilter === 'all') {
        artistsData = statisticsData.top_artists;
    } else {
        // If we have specific year data, use it, otherwise show empty
        artistsData = statisticsData.top_artists_by_year[currentYearFilter] || [];
    }

    artistsListElement.innerHTML = '';

    artistsData.forEach(artist => {
        const artistElement = document.createElement('div');
        artistElement.className = 'data-item';
        artistElement.innerHTML = `
            <span class="item-name">${artist.artist}</span>
            <span class="item-count">${artist.play_count} odtworzeń</span>
        `;
        artistsListElement.appendChild(artistElement);
    });

    if (artistsData.length === 0) {
        artistsListElement.innerHTML = '<div class="no-data">Brak danych dla wybranego roku</div>';
    }
}

// Populate songs list
function populateSongsList() {
    const songsListElement = document.getElementById('songs-list');

    // Filter data by selected year
    let songsData;
    if (currentYearFilter === 'all') {
        songsData = statisticsData.top_songs;
    } else {
        // If we have specific year data, use it, otherwise show empty
        songsData = statisticsData.top_songs_by_year[currentYearFilter] || [];
    }

    songsListElement.innerHTML = '';

    songsData.forEach(song => {
        const songElement = document.createElement('div');
        songElement.className = 'data-item';
        songElement.innerHTML = `
            <span class="item-name">${song.artist} - ${song.title}</span>
            <span class="item-count">${song.play_count} odtworzeń</span>
        `;
        songsListElement.appendChild(songElement);
    });

    if (songsData.length === 0) {
        songsListElement.innerHTML = '<div class="no-data">Brak danych dla wybranego roku</div>';
    }
}

// Set up event listeners
function setupEventListeners() {
    // Year filter change
    document.getElementById('year-select').addEventListener('change', function (e) {
        currentYearFilter = e.target.value;
        updateAllVisualizations();
    });

    // View toggle buttons
    document.querySelectorAll('.toggle-btn').forEach(button => {
        button.addEventListener('click', function () {
            const target = this.getAttribute('data-target');
            const view = this.getAttribute('data-view');

            // Remove active class from all buttons in this toggle group
            document.querySelectorAll(`.toggle-btn[data-target="${target}"]`).forEach(btn => {
                btn.classList.remove('active');
            });

            // Add active class to clicked button
            this.classList.add('active');

            // Hide all views for this target
            document.querySelectorAll(`#${target}-chart, #${target}-table`).forEach(element => {
                element.classList.remove('active-view');
            });

            // Show the selected view
            document.getElementById(`${target}-${view}`).classList.add('active-view');
        });
    });

    // Tab switching
    document.querySelectorAll('.tab-btn').forEach(button => {
        button.addEventListener('click', function () {
            // Remove active class from all buttons and panes
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));

            // Add active class to clicked button and corresponding pane
            this.classList.add('active');
            const tabName = this.getAttribute('data-tab');
            document.getElementById(`${tabName}-tab`).classList.add('active');
        });
    });

    // Search functionality
    document.getElementById('artist-search').addEventListener('input', function (e) {
        filterList('artists-list', e.target.value);
    });

    document.getElementById('song-search').addEventListener('input', function (e) {
        filterList('songs-list', e.target.value);
    });
}

// Filter list items based on search input
function filterList(listId, searchTerm) {
    const items = document.querySelectorAll(`#${listId} .data-item`);
    const lowerSearchTerm = searchTerm.toLowerCase();

    items.forEach(item => {
        const text = item.querySelector('.item-name').textContent.toLowerCase();
        if (text.includes(lowerSearchTerm)) {
            item.style.display = '';
        } else {
            item.style.display = 'none';
        }
    });
}

// Update all visualizations based on year filter
function updateAllVisualizations() {
    renderSummaryStats();
    renderMonthlyData();
    renderTopArtistsData();
    renderTopSongsData();
    populateDataBrowser();
}

// Start the application
document.addEventListener('DOMContentLoaded', fetchData);
