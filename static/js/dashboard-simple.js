// Minimal Dashboard without External Dependencies
// Simple visualization using DOM and CSS only

const API_BASE = '/api';

// Morandi color palette
const COLORS = {
    primary: '#7d9d9c',
    secondary: '#b08b7a',
    accent1: '#a8b5a0',
    accent2: '#c9b6a8',
    accent3: '#9d9791'
};

// Counter animation
function animateCounter(element, target, duration = 1500, decimals = 0) {
    const start = 0;
    const increment = target / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = decimals > 0 ? 
                target.toFixed(decimals) + (decimals > 0 && target < 100 ? '%' : '') : 
                Math.round(target).toLocaleString();
            clearInterval(timer);
        } else {
            element.textContent = decimals > 0 ? 
                current.toFixed(decimals) + (decimals > 0 && current < 100 ? '%' : '') : 
                Math.round(current).toLocaleString();
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
        animateCounter(completionEl, data.avg_completion_rate, 1500, 1);
        
    } catch (error) {
        console.error('Error loading overview:', error);
    }
}

// Create simple bar chart
function createBarChart(container, data) {
    const html = `
        <div style="display: flex; flex-direction: column; height: 100%; justify-content: space-around; padding: 10px;">
            ${data.labels.map((label, i) => {
                const maxValue = Math.max(...data.values);
                const width = (data.values[i] / maxValue * 100).toFixed(1);
                return `
                    <div style="margin-bottom: 8px;">
                        <div style="font-size: 12px; color: #5a5654; margin-bottom: 3px;">${label}</div>
                        <div style="display: flex; align-items: center;">
                            <div style="flex: 0 0 70%; background: #d4cfc9; height: 20px; position: relative;">
                                <div style="background: ${COLORS.primary}; height: 100%; width: ${width}%; transition: width 1s ease;"></div>
                            </div>
                            <div style="flex: 0 0 30%; padding-left: 10px; font-size: 11px; color: #8a8380;">
                                ${data.values[i].toLocaleString()}
                            </div>
                        </div>
                    </div>
                `;
            }).join('')}
        </div>
    `;
    container.innerHTML = html;
}

// Create simple pie chart representation
function createPieChartList(container, data) {
    const total = data.values.reduce((a, b) => a + b, 0);
    const colors = [COLORS.primary, COLORS.secondary, COLORS.accent1, COLORS.accent2, COLORS.accent3];
    
    const html = `
        <div style="display: flex; flex-direction: column; height: 100%; justify-content: space-around; padding: 10px;">
            ${data.labels.map((label, i) => {
                const percentage = (data.values[i] / total * 100).toFixed(1);
                return `
                    <div style="display: flex; align-items: center; margin-bottom: 5px;">
                        <div style="width: 15px; height: 15px; background: ${colors[i % colors.length]}; margin-right: 8px;"></div>
                        <div style="flex: 1; font-size: 12px; color: #5a5654;">${label}</div>
                        <div style="font-size: 11px; color: #8a8380; font-weight: bold;">${percentage}%</div>
                    </div>
                `;
            }).join('')}
        </div>
    `;
    container.innerHTML = html;
}

// Event distribution
async function loadEventDistribution() {
    try {
        const response = await fetch(`${API_BASE}/event-distribution`);
        const data = await response.json();
        const container = document.getElementById('event-chart');
        createPieChartList(container, data);
    } catch (error) {
        console.error('Error loading event distribution:', error);
    }
}

// Completion rate distribution
async function loadCompletionDistribution() {
    try {
        const response = await fetch(`${API_BASE}/completion-distribution`);
        const data = await response.json();
        const container = document.getElementById('completion-chart');
        createBarChart(container, data);
    } catch (error) {
        console.error('Error loading completion distribution:', error);
    }
}

// Cluster analysis
async function loadClusterAnalysis() {
    try {
        const response = await fetch(`${API_BASE}/clustering/results`);
        const data = await response.json();
        const container = document.getElementById('cluster-chart');
        
        const chartData = {
            labels: data.clusters.map(c => `Cluster ${c}`),
            values: data.avg_completion_rate
        };
        createBarChart(container, chartData);
    } catch (error) {
        console.error('Error loading cluster analysis:', error);
    }
}

// Cluster distribution
async function loadClusterDistribution() {
    try {
        const response = await fetch(`${API_BASE}/clustering/distribution`);
        const data = await response.json();
        const container = document.getElementById('cluster-dist-chart');
        createPieChartList(container, data);
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

// Feature importance
async function loadFeatureImportance() {
    try {
        const response = await fetch(`${API_BASE}/prediction/feature-importance`);
        const data = await response.json();
        const container = document.getElementById('feature-chart');
        
        // Reverse to show top features first
        const chartData = {
            labels: data.features.slice(0, 8).reverse(),
            values: data.importance.slice(0, 8).reverse().map(v => (v * 100).toFixed(2))
        };
        
        const html = `
            <div style="display: flex; flex-direction: column; height: 100%; justify-content: space-around; padding: 10px;">
                ${chartData.labels.map((label, i) => {
                    const maxValue = Math.max(...chartData.values);
                    const width = (chartData.values[i] / maxValue * 100).toFixed(1);
                    return `
                        <div style="margin-bottom: 6px;">
                            <div style="font-size: 11px; color: #5a5654; margin-bottom: 2px;">${label}</div>
                            <div style="display: flex; align-items: center;">
                                <div style="flex: 0 0 75%; background: #d4cfc9; height: 18px; position: relative;">
                                    <div style="background: ${COLORS.accent1}; height: 100%; width: ${width}%; transition: width 1s ease;"></div>
                                </div>
                                <div style="flex: 0 0 25%; padding-left: 8px; font-size: 10px; color: #8a8380;">
                                    ${chartData.values[i]}%
                                </div>
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
        container.innerHTML = html;
        
    } catch (error) {
        console.error('Error loading feature importance:', error);
    }
}

// Anomaly detection
async function loadAnomalyDetection() {
    try {
        const response = await fetch(`${API_BASE}/anomaly/summary`);
        const data = await response.json();
        const container = document.getElementById('anomaly-chart');
        
        const chartData = {
            labels: ['Normal Users', 'Anomalous Users'],
            values: [data.normal_count, data.anomaly_count]
        };
        
        createPieChartList(container, chartData);
        
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
}

// Start when DOM is ready
document.addEventListener('DOMContentLoaded', initDashboard);
