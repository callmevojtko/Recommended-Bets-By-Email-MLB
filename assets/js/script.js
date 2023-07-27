// Define a mapping from team names to logo filenames
const teamLogos = {
    'Arizona Diamondbacks': 'ari_d.svg',
    'Atlanta Braves': 'atl_d.svg',
    'Baltimore Orioles': 'bal_d.svg',
    'Boston Red Sox': 'bos_d.svg',
    'Chicago Cubs': 'chc_d.svg',
    'Chicago White Sox': 'cws_d.svg',
    'Cincinnati Reds': 'cin_d.svg',
    'Cleveland Guardians': 'cle_d.svg',
    'Colorado Rockies': 'col_d.svg',
    'Detroit Tigers': 'det_d.svg',
    'Houston Astros': 'hou_d.svg',
    'Kansas City Royals': 'kc_d.svg',
    'Los Angeles Angels': 'laa_d.svg',
    'Los Angeles Dodgers': 'lad_d.svg',
    'Miami Marlins': 'mia_d.svg',
    'Milwaukee Brewers': 'mil_d.svg',
    'Minnesota Twins': 'min_d.svg',
    'New York Mets': 'nym_d.svg',
    'New York Yankees': 'nyy_d.svg',
    'Oakland Athletics': 'oak_d.svg',
    'Philadelphia Phillies': 'phi_d.svg',
    'Pittsburgh Pirates': 'pit_d.svg',
    'San Diego Padres': 'sd_d.svg',
    'San Francisco Giants': 'sf_d.svg',
    'Seattle Mariners': 'sea_d.svg',
    'St. Louis Cardinals': 'stl_d.svg',
    'Tampa Bay Rays': 'tb_d.svg',
    'Texas Rangers': 'tex_d.svg',
    'Toronto Blue Jays': 'tor_d.svg',
    'Washington Nationals': 'wsh_d.svg',
}

// Bookmaker names to logo filenames
const bookmakerLogos = {
    'Barstool Sportsbook': 'barstool.png',
    'FanDuel': 'fanduel.png',
    'DraftKings': 'DKNG.svg',
}

// Fetch game JSON
fetch('data/data.json')
    .then((response) => response.json())
    .then((data) => createHtml(data))

function createHtml(games) {
    // Get the existing container for the games
    var container = document.querySelector('.games-container');

    games.forEach((game) => {
        // Create a div for each game
        var gameDiv = document.createElement('div')
        gameDiv.className = 'game'

        // Create and append the home team, away team
        var teams = document.createElement('h2')

        var homeLogo = document.createElement('img')
        homeLogo.src = '/assets/images/' + teamLogos[game.home_team]
        homeLogo.alt = game.home_team + ' logo'
        homeLogo.classList.add('team-logo')

        var awayLogo = document.createElement('img')
        awayLogo.src = '/assets/images/' + teamLogos[game.away_team]
        awayLogo.alt = game.away_team + ' logo'
        awayLogo.classList.add('team-logo')

        teams.appendChild(homeLogo)
        teams.appendChild(
            document.createTextNode(`${game.home_team} vs ${game.away_team}`)
        )
        teams.appendChild(awayLogo)

        gameDiv.appendChild(teams)

        var startTime = document.createElement('div')
        startTime.className = 'start-time'
        startTime.textContent = `Start time: ${new Date(
            game.commence_time
        ).toLocaleTimeString()} EST`
        gameDiv.appendChild(startTime)

        // Create and append each recommendation
        game.recommendation.forEach((rec) => {
            var recommendationDiv = document.createElement('div')
            recommendationDiv.className = 'recommendation'

            var bookmakerLogo = document.createElement('img')
            bookmakerLogo.src = '/assets/images/' + bookmakerLogos[rec.bookmaker]
            bookmakerLogo.alt = rec.bookmaker + ' logo'
            bookmakerLogo.classList.add('bookmaker-logo')

            recommendationDiv.appendChild(
                document.createTextNode(
                    `Recommendation: ${rec.team} (${rec.price}) at `
                )
            )
            recommendationDiv.appendChild(bookmakerLogo)

            gameDiv.appendChild(recommendationDiv)
        })

        // Append the game div to the container
        container.appendChild(gameDiv)
    })
}
