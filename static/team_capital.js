document.addEventListener('DOMContentLoaded', function() {
    fetchTeamCapital();
    setInterval(fetchTeamCapital, 30000);
});

let teamCapitalChart = null;

function fetchTeamCapital() {
    fetch('/api/team-capital')
        .then(response => response.json())
        .then(teams => {
            displayTeamCapital(teams);
            updateTeamCapitalChart(teams);
        })
        .catch(error => {
            console.error('Error fetching team capital data:', error);
            document.getElementById('teamTableBody').innerHTML =
                '<tr><td colspan="5" class="error">Error loading team data. Please try again later.</td></tr>';
        });
}

function displayTeamCapital(teams) {
    const tableBody = document.getElementById('teamTableBody');

    tableBody.innerHTML = '';

    if (teams.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="5" class="no-data">No team data available at the moment.</td></tr>';
        return;
    }

    teams.forEach((team, index) => {
        const row = document.createElement('tr');

        row.innerHTML = `
            <td class="team-rank">#${index + 1}</td>
            <td class="team-name">${team.name}</td>
            <td class="balance">${team.balance} coins</td>
            <td class="stock-value">${Math.round(team.stock_value)} coins</td>
            <td class="total-capital">${Math.round(team.total_capital)} coins</td>
        `;

        tableBody.appendChild(row);
    });
}

function updateTeamCapitalChart(teams) {
    const sortedTeams = [...teams].sort((a, b) => b.total_capital - a.total_capital);
    const ctx = document.getElementById('teamCapitalChart').getContext('2d');

    const labels = sortedTeams.map(team => team.name);
    const cashData = sortedTeams.map(team => team.balance);
    const stockData = sortedTeams.map(team => Math.round(team.stock_value));

    if (teamCapitalChart) {
        teamCapitalChart.destroy();
    }

    teamCapitalChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Баланс монет',
                    data: cashData,
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Баланс акций',
                    data: stockData,
                    backgroundColor: 'rgba(75, 192, 192, 0.6)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
             animation: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Капиталы команд',
                    font: {
                        size: 18
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Капитал (ТюмКоины)'
                    },
                    stacked: true
                },
                x: {
                    title: {
                        display: true,
                        text: 'Команды'
                    },
                    stacked: true
                }
            }
        }
    });
}
