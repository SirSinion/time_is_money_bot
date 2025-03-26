document.addEventListener('DOMContentLoaded', function() {
    fetchStocks();
    setInterval(fetchStocks, 30000);
});

let stockChart = null;

function fetchStocks() {
    fetch('/api/stocks')
        .then(response => response.json())
        .then(stocks => {
            displayStocks(stocks);
            updateStockChart(stocks);
        })
        .catch(error => {
            console.error('Error fetching stock data:', error);
            document.getElementById('stockContainer').innerHTML = 
                '<div class="error">Error loading stock data. Please try again later.</div>';
        });
}

function displayStocks(stocks) {
    const container = document.getElementById('stockContainer');

    container.innerHTML = '';

    if (stocks.length === 0) {
        container.innerHTML = '<div class="no-data">No stocks available at the moment.</div>';
        return;
    }

    stocks.sort((a, b) => b.price - a.price);
    stocks.forEach(stock => {
        const stockCard = document.createElement('div');
        stockCard.className = 'stock-card';

        stockCard.innerHTML = `
            <div class="stock-header">
               <span class="stock-code">${stock.code}</span>    </div>
            <div class="stock-price">${stock.price} coins</div>
        `;

        container.appendChild(stockCard);
    });
}
function updateStockChart(stocks) {
    const sortedStocks = [...stocks].sort((a, b) => a.price - b.price);

    const ctx = document.getElementById('stockChart').getContext('2d');

    // Prepare data
    const labels = sortedStocks.map(stock => stock.code);
    const prices = sortedStocks.map(stock => stock.price);

    if (stockChart) {
        stockChart.destroy();
    }

    stockChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Stock Prices',
                data: prices,
                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Акции',
                    font: {
                        size: 18
                    }
                },
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Цена (ТюмКоины)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Станции '
                    }
                }
            }
        }
    });
}
