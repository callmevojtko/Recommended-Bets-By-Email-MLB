// Define a mapping from team names to logo filenames
const teamLogos = {
    'Arizona Diamondbacks': '/assets/img/ari_d.svg',
    'Atlanta Braves': '/assets/img/atl_d.svg',
    'Baltimore Orioles': '/assets/img/bal_d.svg',
    'Boston Red Sox': '/assets/img/bos_d.svg',
    'Chicago Cubs': '/assets/img/chc_d.svg',
    'Chicago White Sox': '/assets/img/cws_d.svg',
    'Cincinnati Reds': '/assets/img/cin_d.svg',
    'Cleveland Guardians': '/assets/img/cle_d.svg',
    'Colorado Rockies': '/assets/img/col_d.svg',
    'Detroit Tigers': '/assets/img/det_d.svg',
    'Houston Astros': '/assets/img/hou_d.svg',
    'Kansas City Royals': '/assets/img/kc_d.svg',
    'Los Angeles Angels': '/assets/img/laa_d.svg',
    'Los Angeles Dodgers': '/assets/img/lad_d.svg',
    'Miami Marlins': '/assets/img/mia_d.svg',
    'Milwaukee Brewers': '/assets/img/mil_d.svg',
    'Minnesota Twins': '/assets/img/min_d.svg',
    'New York Mets': '/assets/img/nym_d.svg',
    'New York Yankees': '/assets/img/nyy_d.svg',
    'Oakland Athletics': '/assets/img/oak_d.svg',
    'Philadelphia Phillies': '/assets/img/phi_d.svg',
    'Pittsburgh Pirates': '/assets/img/pit_d.svg',
    'San Diego Padres': '/assets/img/sd_d.svg',
    'San Francisco Giants': '/assets/img/sf_d.svg',
    'Seattle Mariners': '/assets/img/sea_d.svg',
    'St. Louis Cardinals': '/assets/img/stl_d.svg',
    'Tampa Bay Rays': '/assets/img/tb_d.svg',
    'Texas Rangers': '/assets/img/tex_d.svg',
    'Toronto Blue Jays': '/assets/img/tor_d.svg',
    'Washington Nationals': '/assets/img/wsh_d.svg',
}

// Bookmaker names to logo filenames
const bookmakerLogos = {
    'Barstool Sportsbook': '/assets/img/barstool.png',
    'FanDuel': '/assets/img/fanduel.png',
    'DraftKings': '/assets/img/DKNG.svg',
}

// Fetch game JSON
fetch('data.json')
    .then(response => response.json())
    .then(data => createHtml(data));

function createHtml(games) {
    // Create a container for the games
    var container = document.createElement('div');

    games.forEach(game => {
        // Create a div for each game
        var gameDiv = document.createElement('div');
        gameDiv.className = 'game';

        // Create and append the home team, away team
        var teams = document.createElement('h2');

        var homeLogo = document.createElement('img');
        homeLogo.src = "/assets/img/" + teamLogos[game.home_team];
        homeLogo.alt = game.home_team + " logo";
        homeLogo.classList.add('team-logo');

        var awayLogo = document.createElement('img');
        awayLogo.src = "/assets/img/" + teamLogos[game.away_team];
        awayLogo.alt = game.away_team + " logo";
        awayLogo.classList.add('team-logo');

        teams.appendChild(homeLogo);
        teams.appendChild(document.createTextNode(`${game.home_team} vs ${game.away_team}`));
        teams.appendChild(awayLogo);

        gameDiv.appendChild(teams);

        // Create and append each recommendation
        game.recommendation.forEach(rec => {
            var recommendationDiv = document.createElement('div');
            recommendationDiv.className = 'recommendation';

            var bookmakerLogo = document.createElement('img');
            bookmakerLogo.src = "/assets/img/" + bookmakerLogos[rec.bookmaker];
            bookmakerLogo.alt = rec.bookmaker + " logo";
            bookmakerLogo.classList.add('bookmaker-logo');

            recommendationDiv.appendChild(document.createTextNode(`Recommendation: ${rec.team} (${rec.point}/${rec.price}) at `));
            recommendationDiv.appendChild(bookmakerLogo);

            gameDiv.appendChild(recommendationDiv);
        });

        // Append the game div to the container
        container.appendChild(gameDiv);
    });

    // Append the container to the body of the page
    document.body.appendChild(container);
}
