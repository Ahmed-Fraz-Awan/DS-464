// Simple Dashboard Script
let data = [];

async function loadData() {
    try {
        // Load the CSV data
        const response = await fetch('../data/cleaned_data.csv');
        const csvText = await response.text();
        
        // Parse CSV
        const rows = csvText.split('\n');
        const headers = rows[0].split(',');
        
        data = rows.slice(1).map(row => {
            const values = row.split(',');
            const obj = {};
            headers.forEach((header, index) => {
                obj[header.trim()] = values[index] ? values[index].trim() : '';
            });
            return obj;
        }).filter(row => row.date); // Remove empty rows
        
        // Update dashboard
        updateDashboard();
        
        // Hide loading, show dashboard
        document.getElementById('loading').style.display = 'none';
        document.getElementById('dashboard').style.display = 'block';
        
    } catch (error) {
        console.error('Error loading data:', error);
        document.getElementById('loading').innerHTML = `
            <div class="alert alert-danger">
                Error loading data. Please make sure cleaned_data.csv exists in the data folder.
            </div>
        `;
    }
}

function updateDashboard() {
    if (data.length === 0) return;
    
    // Calculate KPIs
    const totalRevenue = data.reduce((sum, row) => sum + parseFloat(row.revenue || 0), 0);
    const totalProfit = data.reduce((sum, row) => sum + parseFloat(row.profit || 0), 0);
    const avgOrderValue = totalRevenue / data.length;
    
    // Update KPI cards
    document.getElementById('total-revenue').textContent = `$${totalRevenue.toFixed(2)}`;
    document.getElementById('total-profit').textContent = `$${totalProfit.toFixed(2)}`;
    document.getElementById('total-transactions').textContent = data.length;
    document.getElementById('avg-order').textContent = `$${avgOrderValue.toFixed(2)}`;
    
    // Create charts
    createCharts();
    
    // Update table (show first 10 rows)
    updateTable();
}

function createCharts() {
    // Category Chart
    const categories = {};
    data.forEach(row => {
        if (row.category) {
            categories[row.category] = (categories[row.category] || 0) + parseFloat(row.revenue || 0);
        }
    });
    
    const categoryTrace = {
        values: Object.values(categories),
        labels: Object.keys(categories),
        type: 'pie',
        hole: 0.4
    };
    
    Plotly.newPlot('category-chart', [categoryTrace], {
        title: 'Revenue by Category',
        height: 400
    });
    
    // Region Chart
    const regions = {};
    data.forEach(row => {
        if (row.region) {
            regions[row.region] = (regions[row.region] || 0) + parseFloat(row.revenue || 0);
        }
    });
    
    const regionTrace = {
        x: Object.keys(regions),
        y: Object.values(regions),
        type: 'bar',
        marker: {
            color: ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        }
    };
    
    Plotly.newPlot('region-chart', [regionTrace], {
        title: 'Revenue by Region',
        xaxis: { title: 'Region' },
        yaxis: { title: 'Revenue ($)' },
        height: 400
    });
}

function updateTable() {
    const tableBody = document.getElementById('data-table');
    tableBody.innerHTML = '';
    
    // Show first 10 rows
    data.slice(0, 10).forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${row.date}</td>
            <td><span class="badge bg-primary">${row.category}</span></td>
            <td>${row.region}</td>
            <td>$${parseFloat(row.revenue).toFixed(2)}</td>
            <td class="${parseFloat(row.profit) >= 0 ? 'text-success' : 'text-danger'}">
                $${parseFloat(row.profit).toFixed(2)}
            </td>
        `;
        tableBody.appendChild(tr);
    });
}

// Load data when page loads
document.addEventListener('DOMContentLoaded', loadData);