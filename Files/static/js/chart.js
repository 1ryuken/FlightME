/**
 * Chart.js configuration and setup for flight price history
 * This file extends the functionality in main.js specific to charts
 */

function createPriceHistoryChart(dates, prices) {
    const ctx = document.getElementById('priceHistoryChart');
    if (!ctx) return;
    
    // Create gradient for area under the line
    const ctxContext = ctx.getContext('2d');
    const gradient = ctxContext.createLinearGradient(0, 0, 0, 300);
    gradient.addColorStop(0, 'rgba(255, 222, 0, 0.7)');  // Anime yellow with opacity
    gradient.addColorStop(1, 'rgba(255, 222, 0, 0.1)');
    
    // Format the data for better display
    const formattedDates = dates.map(date => {
        const d = new Date(date);
        return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });
    
    // Find min and max prices to set appropriate y-axis scale
    const minPrice = Math.min(...prices) * 0.9;  // 10% buffer below minimum
    const maxPrice = Math.max(...prices) * 1.1;  // 10% buffer above maximum
    
    // Create the chart
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: formattedDates,
            datasets: [{
                label: 'Price (USD)',
                data: prices,
                borderColor: '#FFDE00',  // Anime yellow
                backgroundColor: gradient,
                borderWidth: 3,
                pointBackgroundColor: '#FFDE00',
                pointBorderColor: '#FFFFFF',
                pointRadius: 5,
                pointHoverRadius: 7,
                tension: 0.3,  // Smooth curve
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false  // Hide legend as we only have one dataset
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(53, 59, 72, 0.9)',
                    titleFont: {
                        size: 14,
                        weight: 'bold'
                    },
                    bodyFont: {
                        size: 13
                    },
                    padding: 12,
                    cornerRadius: 8,
                    caretSize: 6,
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += new Intl.NumberFormat('en-US', {
                                    style: 'currency',
                                    currency: 'USD'
                                }).format(context.parsed.y);
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false,  // Hide vertical grid lines
                        drawBorder: false
                    },
                    ticks: {
                        font: {
                            size: 12
                        },
                        maxRotation: 45,
                        minRotation: 45
                    }
                },
                y: {
                    beginAtZero: false,
                    suggestedMin: minPrice,
                    suggestedMax: maxPrice,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'  // Lighter grid lines
                    },
                    ticks: {
                        font: {
                            size: 12
                        },
                        callback: function(value) {
                            return '$' + value.toFixed(0);
                        }
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            },
            elements: {
                line: {
                    tension: 0.4  // Smooth curve
                }
            },
            animation: {
                duration: 1500,
                easing: 'easeOutQuart'
            }
        }
    });
    
    return chart;
}

// Add trend markers to the chart
function addTrendMarkersToChart(chart, trend) {
    if (!chart || !trend) return;
    
    // Add annotation plugin if needed
    if (!Chart.annotationPlugin) {
        console.warn('Chart.js Annotation plugin not available');
        return;
    }
    
    const trendColor = getTrendColor(trend);
    
    chart.options.plugins.annotation = {
        annotations: {
            trendLine: {
                type: 'line',
                scaleID: 'y',
                value: chart.data.datasets[0].data[chart.data.datasets[0].data.length - 1],
                borderColor: trendColor,
                borderWidth: 2,
                borderDash: [5, 5],
                label: {
                    content: `${trend.toUpperCase()} TREND`,
                    display: true,
                    position: 'end',
                    backgroundColor: trendColor,
                    color: '#FFFFFF',
                    font: {
                        weight: 'bold'
                    }
                }
            }
        }
    };
    
    chart.update();
}

// Get appropriate color for trend
function getTrendColor(trend) {
    switch(trend.toLowerCase()) {
        case 'rising':
            return '#FF6B6B';  // Red
        case 'falling':
            return '#1DD1A1';  // Green
        case 'stable':
            return '#54A0FF';  // Blue
        default:
            return '#FFDE00';  // Default yellow
    }
}

// Helper function to format price with currency
function formatPrice(price) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(price);
}
