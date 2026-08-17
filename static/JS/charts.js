/**
 * Dashboard Charts
 * Initializes Chart.js for monthly projects, revisions, and revenue
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts when page loads
    initCharts();
});

export function renderAll() {
    initCharts();
}

function initCharts() {
    initMonthlyChart();
    initRevisionsChart();
    initRevenueChart();
}

/**
 * Monthly Projects Chart
 */
function initMonthlyChart() {
    const ctx = document.getElementById('chartMonthly');
    if (!ctx) return;
    
    // Get data from template context or fetch via AJAX
    const chartData = window.chartMonthlyData || {
        labels: [],
        data: []
    };
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: 'Projects',
                data: chartData.data,
                borderColor: '#0d6efd',
                backgroundColor: 'rgba(13, 110, 253, 0.05)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#0d6efd',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 7
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                filler: {
                    propagate: true
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 2
                    },
                    grid: {
                        drawBorder: false,
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false,
                        drawBorder: false
                    }
                }
            }
        }
    });
}

/**
 * Revision Usage Chart (Doughnut)
 */
function initRevisionsChart() {
    const ctx = document.getElementById('chartRevisions');
    if (!ctx) return;
    
    const chartData = window.chartRevisionsData || {
        labels: ['Included', 'Used', 'Billable'],
        data: [0, 0, 0]
    };
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: chartData.labels,
            datasets: [{
                data: chartData.data,
                backgroundColor: [
                    '#0d6efd',  // Included - Primary Blue
                    '#198754',  // Used - Success Green
                    '#fd7e14'   // Billable - Warning Orange
                ],
                borderColor: '#fff',
                borderWidth: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true,
                        font: {
                            size: 13,
                            weight: '500'
                        }
                    }
                }
            }
        }
    });
}

/**
 * Revenue Analytics Chart (Bar)
 */
function initRevenueChart() {
    const ctx = document.getElementById('chartRevenue');
    if (!ctx) return;
    
    const chartData = window.chartRevenueData || {
        labels: [],
        data: []
    };
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: 'Revenue (₦M)',
                data: chartData.data,
                backgroundColor: '#0d6efd',
                borderColor: '#0d6efd',
                borderWidth: 0,
                borderRadius: 4,
                hoverBackgroundColor: '#0b5ed7'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '₦' + value.toLocaleString();
                        }
                    },
                    grid: {
                        drawBorder: false,
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false,
                        drawBorder: false
                    }
                }
            }
        }
    });
}

/**
 * Load chart data via AJAX
 * Called if you want to refresh charts dynamically
 */
function loadChartData() {
    // Load monthly chart data
    fetch('/dashboard/api/chart/monthly/')
        .then(response => response.json())
        .then(data => {
            window.chartMonthlyData = data;
        });
    
    // Load revisions chart data
    fetch('/dashboard/api/chart/revisions/')
        .then(response => response.json())
        .then(data => {
            window.chartRevisionsData = data;
        });
    
    // Load revenue chart data
    fetch('/dashboard/api/chart/revenue/')
        .then(response => response.json())
        .then(data => {
            window.chartRevenueData = data;
        });
}