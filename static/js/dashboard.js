// Dashboard JavaScript - Data Fetching and Visualization

const API_BASE = '/api';

// Morandi color palette
const COLORS = {
    primary: '#7d9d9c',      // Morandi teal
    secondary: '#b08b7a',    // Morandi terracotta
    accent1: '#a8b5a0',      // Morandi sage
    accent2: '#c9b6a8',      // Morandi taupe
    accent3: '#9d9791',      // Morandi gray
    text: '#5a5654'
};

// Counter animation
function animateCounter(element, target, duration = 1500) {
    const start = 0;
    const increment = target / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = Math.round(target).toLocaleString();
            clearInterval(timer);
        } else {
            element.textContent = Math.round(current).toLocaleString();
        }
    }, 16);
}

// Fetch and display overview stats
async function loadOverview() {
    try {
        const response = await fetch(`${API_BASE}/stats`);
        const data = await response.json();
        
        const totalEl = document.getElementById('total-events');
        const usersEl = document.getElementById('unique-users');
        const tracksEl = document.getElementById('unique-tracks');
        const completionEl = document.getElementById('avg-completion');
        
        animateCounter(totalEl, data.total_events);
        animateCounter(usersEl, data.unique_users);
        animateCounter(tracksEl, data.unique_tracks);
        
        // Completion rate with decimal
        const completionValue = data.avg_completion_rate;
        let current = 0;
        const increment = completionValue / 100;
        const timer = setInterval(() => {
            current += increment;
            if (current >= completionValue) {
                completionEl.textContent = completionValue.toFixed(1) + '%';
                clearInterval(timer);
            } else {
                completionEl.textContent = current.toFixed(1) + '%';
            }
        }, 15);
        
    } catch (error) {
        console.error('Error loading overview:', error);
    }
}

// Event distribution chart
async function loadEventDistribution() {
    try {
        const response = await fetch(`${API_BASE}/event-distribution`);
        const data = await response.json();
        
        const chart = echarts.init(document.getElementById('event-chart'));
        
        const option = {
            tooltip: {
                trigger: 'item',
                formatter: '{b}: {c} ({d}%)'
            },
            series: [{
                type: 'pie',
                radius: ['40%', '70%'],
                avoidLabelOverlap: true,
                label: {
                    show: true,
                    formatter: '{b}\n{d}%'
                },
                data: data.labels.map((label, i) => ({
                    name: label,
                    value: data.values[i]
                })),
                color: [COLORS.primary, COLORS.secondary, COLORS.accent1, COLORS.accent2, COLORS.accent3]
            }]
        };
        
        chart.setOption(option);
        
    } catch (error) {
        console.error('Error loading event distribution:', error);
    }
}

// Completion rate distribution chart
async function loadCompletionDistribution() {
    try {
        const response = await fetch(`${API_BASE}/completion-distribution`);
        const data = await response.json();
        
        const chart = echarts.init(document.getElementById('completion-chart'));
        
        const option = {
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'shadow'
                }
            },
            xAxis: {
                type: 'category',
                data: data.labels,
                axisLabel: {
                    color: COLORS.text
                }
            },
            yAxis: {
                type: 'value',
                axisLabel: {
                    color: COLORS.text
                }
            },
            series: [{
                type: 'bar',
                data: data.values,
                itemStyle: {
                    color: COLORS.primary
                },
                barWidth: '60%'
            }]
        };
        
        chart.setOption(option);
        
    } catch (error) {
        console.error('Error loading completion distribution:', error);
    }
}

// Cluster analysis chart
async function loadClusterAnalysis() {
    try {
        const response = await fetch(`${API_BASE}/clustering/results`);
        const data = await response.json();
        
        const chart = echarts.init(document.getElementById('cluster-chart'));
        
        const option = {
            tooltip: {
                trigger: 'axis'
            },
            legend: {
                data: ['Avg Completion Rate', 'Like Ratio'],
                textStyle: {
                    color: COLORS.text
                }
            },
            xAxis: {
                type: 'category',
                data: data.clusters.map(c => `Cluster ${c}`),
                axisLabel: {
                    color: COLORS.text,
                    rotate: 0
                }
            },
            yAxis: {
                type: 'value',
                axisLabel: {
                    color: COLORS.text
                }
            },
            series: [
                {
                    name: 'Avg Completion Rate',
                    type: 'bar',
                    data: data.avg_completion_rate,
                    itemStyle: {
                        color: COLORS.primary
                    }
                },
                {
                    name: 'Like Ratio',
                    type: 'line',
                    yAxisIndex: 0,
                    data: data.like_ratio.map(v => v * 100),
                    itemStyle: {
                        color: COLORS.secondary
                    }
                }
            ]
        };
        
        chart.setOption(option);
        
    } catch (error) {
        console.error('Error loading cluster analysis:', error);
    }
}

// Cluster distribution chart
async function loadClusterDistribution() {
    try {
        const response = await fetch(`${API_BASE}/clustering/distribution`);
        const data = await response.json();
        
        const chart = echarts.init(document.getElementById('cluster-dist-chart'));
        
        const option = {
            tooltip: {
                trigger: 'item'
            },
            series: [{
                type: 'pie',
                radius: '60%',
                data: data.labels.map((label, i) => ({
                    name: label,
                    value: data.values[i]
                })),
                label: {
                    formatter: '{b}\n{c} songs'
                },
                color: [COLORS.primary, COLORS.secondary, COLORS.accent1, COLORS.accent2, COLORS.accent3]
            }]
        };
        
        chart.setOption(option);
        
    } catch (error) {
        console.error('Error loading cluster distribution:', error);
    }
}

// Prediction metrics
async function loadPredictionMetrics() {
    try {
        const response = await fetch(`${API_BASE}/prediction/metrics`);
        const data = await response.json();
        
        const container = document.querySelector('.prediction-metrics .card-content');
        
        container.innerHTML = `
            <div class="metrics-grid">
                <div class="metric-item">
                    <div class="value">${data.mae_test.toFixed(2)}</div>
                    <div class="label">MAE (Test)</div>
                </div>
                <div class="metric-item">
                    <div class="value">${data.rmse_test.toFixed(2)}</div>
                    <div class="label">RMSE (Test)</div>
                </div>
                <div class="metric-item">
                    <div class="value">${data.mae_train.toFixed(2)}</div>
                    <div class="label">MAE (Train)</div>
                </div>
                <div class="metric-item">
                    <div class="value">${data.rmse_train.toFixed(2)}</div>
                    <div class="label">RMSE (Train)</div>
                </div>
            </div>
        `;
        
    } catch (error) {
        console.error('Error loading prediction metrics:', error);
    }
}

// Feature importance chart
async function loadFeatureImportance() {
    try {
        const response = await fetch(`${API_BASE}/prediction/feature-importance`);
        const data = await response.json();
        
        const chart = echarts.init(document.getElementById('feature-chart'));
        
        const option = {
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'shadow'
                }
            },
            xAxis: {
                type: 'value',
                axisLabel: {
                    color: COLORS.text
                }
            },
            yAxis: {
                type: 'category',
                data: data.features.reverse(),
                axisLabel: {
                    color: COLORS.text,
                    fontSize: 11
                }
            },
            series: [{
                type: 'bar',
                data: data.importance.reverse(),
                itemStyle: {
                    color: COLORS.accent1
                }
            }]
        };
        
        chart.setOption(option);
        
    } catch (error) {
        console.error('Error loading feature importance:', error);
    }
}

// Anomaly detection chart
async function loadAnomalyDetection() {
    try {
        const response = await fetch(`${API_BASE}/anomaly/summary`);
        const data = await response.json();
        
        const chart = echarts.init(document.getElementById('anomaly-chart'));
        
        const option = {
            tooltip: {
                trigger: 'item',
                formatter: '{b}: {c} ({d}%)'
            },
            series: [{
                type: 'pie',
                radius: ['40%', '70%'],
                data: [
                    {
                        name: 'Normal Users',
                        value: data.normal_count,
                        itemStyle: { color: COLORS.accent1 }
                    },
                    {
                        name: 'Anomalous Users',
                        value: data.anomaly_count,
                        itemStyle: { color: COLORS.secondary }
                    }
                ],
                label: {
                    formatter: '{b}\n{c} ({d}%)'
                }
            }]
        };
        
        chart.setOption(option);
        
    } catch (error) {
        console.error('Error loading anomaly detection:', error);
    }
}

// Update timestamp
function updateTimestamp() {
    const timestampEl = document.getElementById('timestamp');
    const now = new Date();
    const formatted = now.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    timestampEl.textContent = formatted;
}

// Initialize dashboard
async function initDashboard() {
    updateTimestamp();
    setInterval(updateTimestamp, 1000);
    
    // Load all data
    await Promise.all([
        loadOverview(),
        loadEventDistribution(),
        loadCompletionDistribution(),
        loadClusterAnalysis(),
        loadClusterDistribution(),
        loadPredictionMetrics(),
        loadFeatureImportance(),
        loadAnomalyDetection()
    ]);
    
    // Handle window resize for charts
    window.addEventListener('resize', () => {
        echarts.init(document.getElementById('event-chart')).resize();
        echarts.init(document.getElementById('completion-chart')).resize();
        echarts.init(document.getElementById('cluster-chart')).resize();
        echarts.init(document.getElementById('cluster-dist-chart')).resize();
        echarts.init(document.getElementById('feature-chart')).resize();
        echarts.init(document.getElementById('anomaly-chart')).resize();
    });
}

// Start when DOM is ready
document.addEventListener('DOMContentLoaded', initDashboard);
