document.addEventListener('DOMContentLoaded', function() {
    fetchTransactions();
    setInterval(fetchTransactions, 30000);
});

function fetchTransactions() {
    fetch('/api/transactions')
        .then(response => response.json())
        .then(transactions => {
            displayTransactions(transactions);
        })
        .catch(error => {
            console.error('Error fetching transaction data:', error);
            document.getElementById('transactionsTableBody').innerHTML =
                '<tr><td colspan="7" class="error">Error loading transaction data. Please try again later.</td></tr>';
        });
}

function displayTransactions(transactions) {
    const tableBody = document.getElementById('transactionsTableBody');

    tableBody.innerHTML = '';

    if (transactions.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="7" class="no-data">No transactions available at the moment.</td></tr>';
        return;
    }

    transactions.forEach(transaction => {
        const row = document.createElement('tr');

        row.innerHTML = `
            <td>${transaction.id}</td>
            <td>${transaction.username}</td>
            <td>${transaction.team_name}</td>
            <td>${transaction.stock_name} (${transaction.stock_code})</td>
            <td class="${transaction.amount > 0 ? 'positive' : 'negative'}">${transaction.amount}</td>
            <td>${transaction.purchase_price} coins</td>
            <td>${transaction.total_price} coins</td>
        `;

        tableBody.appendChild(row);
    });
}
