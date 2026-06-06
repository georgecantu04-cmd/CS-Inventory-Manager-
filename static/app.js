// Global state
let inventoryData = [];
let currentItemId = null;
let inventoryChart = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    refreshData();
});

// API Functions
async function syncInventory() {
    const syncBtn = document.getElementById('sync-text');
    const spinner = document.getElementById('sync-spinner');

    syncBtn.classList.add('hidden');
    spinner.classList.remove('hidden');

    try {
        const response = await fetch('/api/sync', { method: 'POST' });
        const data = await response.json();

        if (data.success) {
            showAlert(`Inventory synced! ${data.added} added, ${data.updated} updated.`, 'success');
            await refreshData();
        } else {
            showAlert(data.message || 'Failed to sync inventory', 'error');
        }
    } catch (error) {
        showAlert('Error syncing inventory: ' + error.message, 'error');
    } finally {
        syncBtn.classList.remove('hidden');
        spinner.classList.add('hidden');
    }
}

async function updatePrices() {
    const updateBtn = document.getElementById('update-text');
    const spinner = document.getElementById('update-spinner');

    updateBtn.classList.add('hidden');
    spinner.classList.remove('hidden');

    try {
        const response = await fetch('/api/update-prices', { method: 'POST' });
        const data = await response.json();

        if (data.success) {
            showAlert(`Prices updated! ${data.updated} items updated, ${data.alerts} new alerts.`, 'success');
            await refreshData();
        } else {
            showAlert(data.message || 'Failed to update prices', 'error');
        }
    } catch (error) {
        showAlert('Error updating prices: ' + error.message, 'error');
    } finally {
        updateBtn.classList.remove('hidden');
        spinner.classList.add('hidden');
    }
}

async function refreshData() {
    await Promise.all([
        loadSummary(),
        loadItems(),
        loadAlerts(),
        loadInventoryHistory()
    ]);
}

async function loadSummary() {
    try {
        const response = await fetch('/api/summary');
        const data = await response.json();

        document.getElementById('total-items').textContent = data.total_items;
        document.getElementById('total-value').textContent = `$${data.total_value.toFixed(2)}`;
        document.getElementById('total-invested').textContent = `$${data.total_purchase_price.toFixed(2)}`;

        const profitLossEl = document.getElementById('profit-loss');
        const profitLossPercentageEl = document.getElementById('profit-loss-percentage');

        profitLossEl.textContent = `$${data.total_profit_loss.toFixed(2)}`;
        profitLossPercentageEl.textContent = `(${data.profit_loss_percentage >= 0 ? '+' : ''}${data.profit_loss_percentage.toFixed(2)}%)`;

        if (data.total_profit_loss >= 0) {
            profitLossEl.classList.add('positive');
            profitLossEl.classList.remove('negative');
            profitLossPercentageEl.classList.add('positive');
            profitLossPercentageEl.classList.remove('negative');
        } else {
            profitLossEl.classList.add('negative');
            profitLossEl.classList.remove('positive');
            profitLossPercentageEl.classList.add('negative');
            profitLossPercentageEl.classList.remove('positive');
        }
    } catch (error) {
        console.error('Error loading summary:', error);
    }
}

async function loadItems() {
    try {
        const response = await fetch('/api/items');
        inventoryData = await response.json();

        renderItems(inventoryData);
    } catch (error) {
        console.error('Error loading items:', error);
    }
}

function renderItems(items) {
    const tbody = document.getElementById('inventory-tbody');

    if (items.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="no-data">No items yet. Click "Sync Inventory" to load your items.</td></tr>';
        return;
    }

    tbody.innerHTML = items.map(item => {
        const profitLoss = item.profit_loss || 0;
        const profitLossClass = profitLoss >= 0 ? 'positive' : 'negative';
        const profitLossSign = profitLoss >= 0 ? '+' : '';

        return `
            <tr>
                <td><strong>${item.name}</strong></td>
                <td>${item.type || '-'}</td>
                <td>${item.rarity || '-'}</td>
                <td>${item.exterior || '-'}</td>
                <td>$${(item.current_price || 0).toFixed(2)}</td>
                <td>$${(item.purchase_price || 0).toFixed(2)}</td>
                <td class="${profitLossClass}">${profitLossSign}$${profitLoss.toFixed(2)}</td>
                <td>
                    <button onclick="openPriceModal(${item.id}, '${item.name.replace(/'/g, "\\'")}', ${item.purchase_price || 0})" class="btn btn-small btn-secondary">
                        Set Purchase Price
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

async function loadAlerts() {
    try {
        const response = await fetch('/api/alerts');
        const alerts = await response.json();

        const container = document.getElementById('alerts-container');

        if (alerts.length === 0) {
            container.innerHTML = '<p class="no-data">No alerts yet. Prices will be monitored automatically.</p>';
            return;
        }

        container.innerHTML = alerts.slice(0, 10).map(alert => {
            const typeClass = alert.alert_type;
            const sign = alert.percentage_change >= 0 ? '+' : '';
            const arrow = alert.alert_type === 'gain' ? '📈' : '📉';

            return `
                <div class="alert-item ${typeClass}">
                    <div class="alert-content">
                        <div class="alert-title">${arrow} ${alert.item_name}</div>
                        <div class="alert-details">
                            ${sign}${alert.percentage_change.toFixed(2)}% -
                            $${alert.old_price.toFixed(2)} → $${alert.new_price.toFixed(2)}
                            (${new Date(alert.created_at).toLocaleString()})
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    } catch (error) {
        console.error('Error loading alerts:', error);
    }
}

async function loadInventoryHistory() {
    try {
        const response = await fetch('/api/inventory-history?days=30');
        const history = await response.json();

        if (history.length === 0) {
            return;
        }

        const labels = history.map(h => new Date(h.timestamp).toLocaleDateString());
        const values = history.map(h => h.total_value);

        const ctx = document.getElementById('inventory-chart');

        if (inventoryChart) {
            inventoryChart.destroy();
        }

        inventoryChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Total Value ($)',
                    data: values,
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: true,
                        labels: {
                            color: '#f1f5f9'
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            color: '#94a3b8',
                            callback: function(value) {
                                return '$' + value.toFixed(2);
                            }
                        },
                        grid: {
                            color: '#475569'
                        }
                    },
                    x: {
                        ticks: {
                            color: '#94a3b8'
                        },
                        grid: {
                            color: '#475569'
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading inventory history:', error);
    }
}

// Modal functions
function openPriceModal(itemId, itemName, currentPrice) {
    currentItemId = itemId;
    document.getElementById('modal-item-name').textContent = itemName;
    document.getElementById('purchase-price-input').value = currentPrice || '';
    document.getElementById('price-modal').classList.remove('hidden');
}

function closeModal() {
    document.getElementById('price-modal').classList.add('hidden');
    currentItemId = null;
}

async function savePurchasePrice() {
    const price = parseFloat(document.getElementById('purchase-price-input').value);

    if (isNaN(price) || price < 0) {
        showAlert('Please enter a valid price', 'error');
        return;
    }

    try {
        const response = await fetch(`/api/items/${currentItemId}/purchase-price`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ purchase_price: price })
        });

        if (response.ok) {
            showAlert('Purchase price updated successfully', 'success');
            closeModal();
            await refreshData();
        } else {
            showAlert('Failed to update purchase price', 'error');
        }
    } catch (error) {
        showAlert('Error updating purchase price: ' + error.message, 'error');
    }
}

// Filter and sort functions
function filterItems() {
    const searchTerm = document.getElementById('search-input').value.toLowerCase();
    const filteredItems = inventoryData.filter(item =>
        item.name.toLowerCase().includes(searchTerm) ||
        (item.type && item.type.toLowerCase().includes(searchTerm)) ||
        (item.rarity && item.rarity.toLowerCase().includes(searchTerm))
    );
    renderItems(filteredItems);
}

function sortItems() {
    const sortBy = document.getElementById('sort-select').value;
    let sortedItems = [...inventoryData];

    switch (sortBy) {
        case 'name':
            sortedItems.sort((a, b) => a.name.localeCompare(b.name));
            break;
        case 'value-desc':
            sortedItems.sort((a, b) => (b.current_price || 0) - (a.current_price || 0));
            break;
        case 'value-asc':
            sortedItems.sort((a, b) => (a.current_price || 0) - (b.current_price || 0));
            break;
        case 'profit-desc':
            sortedItems.sort((a, b) => (b.profit_loss || 0) - (a.profit_loss || 0));
            break;
        case 'profit-asc':
            sortedItems.sort((a, b) => (a.profit_loss || 0) - (b.profit_loss || 0));
            break;
    }

    renderItems(sortedItems);
}

// Alert functions
function showAlert(message, type = 'info') {
    const banner = document.getElementById('alert-banner');
    const messageEl = document.getElementById('alert-message');

    banner.className = 'alert-banner ' + type;
    messageEl.textContent = message;
    banner.classList.remove('hidden');

    setTimeout(() => {
        closeAlert();
    }, 5000);
}

function closeAlert() {
    document.getElementById('alert-banner').classList.add('hidden');
}
