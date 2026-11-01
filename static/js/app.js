/**
 * API SENTINEL - Enterprise Cybersecurity SOC Frontend Application
 * Handles Real-time Dashboards, Chart.js Visualizations, Threat Alerts,
 * Interactive Attack Simulation Lab, and Model Diagnostics.
 */

// Global State
const Sentinel = {
    trafficChart: null,
    categoryChart: null,
    featureChart: null,
    autoRefreshTimer: null,
    currentPage: 1,
    perPage: 15
};

// Initialize common components on DOM loaded
document.addEventListener('DOMContentLoaded', () => {
    initClock();
    checkSystemHealth();
    setupMobileSidebar();
});

/**
 * Live SOC Clock (UTC & Local)
 */
function initClock() {
    const clockEl = document.getElementById('socClock');
    if (!clockEl) return;
    
    function update() {
        const now = new Date();
        const timeStr = now.toTimeString().split(' ')[0];
        const utcStr = now.toISOString().slice(11, 19) + ' UTC';
        clockEl.innerHTML = `<i class="bi bi-clock me-1 text-cyan"></i>${timeStr} <span class="text-muted ms-1">(${utcStr})</span>`;
    }
    update();
    setInterval(update, 1000);
}

/**
 * Check System Engine Health
 */
async function checkSystemHealth() {
    try {
        const res = await fetch('/api/health');
        if (!res.ok) return;
        const data = await res.json();
        
        const badge = document.getElementById('engineHealthBadge');
        if (badge) {
            if (data.status === 'HEALTHY') {
                badge.className = 'status-beacon active';
                badge.title = 'AI Engines & Database Online';
            } else {
                badge.className = 'status-beacon danger';
                badge.title = 'Engine Degraded';
            }
        }
    } catch (err) {
        console.warn('Health check unreachable:', err);
    }
}

/**
 * Mobile Sidebar Toggle
 */
function setupMobileSidebar() {
    const toggleBtn = document.getElementById('sidebarToggleBtn');
    const sidebar = document.querySelector('.app-sidebar');
    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('show');
        });
    }
}

/**
 * Global Toast Notification Dispatcher
 */
function showNotification(title, message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toastId = 'toast-' + Math.random().toString(36).substring(2, 9);
    const bgMap = {
        success: 'border-emerald text-emerald',
        danger: 'border-crimson text-crimson',
        warning: 'border-amber text-amber',
        info: 'border-cyan text-cyan'
    };
    
    const iconMap = {
        success: 'bi-check-circle-fill text-emerald',
        danger: 'bi-exclamation-triangle-fill text-crimson',
        warning: 'bi-shield-exclamation text-amber',
        info: 'bi-info-circle-fill text-cyan'
    };

    const toastHtml = `
        <div id="${toastId}" class="toast align-items-center text-white bg-dark border ${bgMap[type] || 'border-cyan'}" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body d-flex align-items-center gap-2">
                    <i class="bi ${iconMap[type] || iconMap.info} fs-5"></i>
                    <div>
                        <strong>${title}</strong>
                        <div class="small text-light opacity-75">${message}</div>
                    </div>
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', toastHtml);
    const toastElem = document.getElementById(toastId);
    const bsToast = new bootstrap.Toast(toastElem, { delay: 4500 });
    bsToast.show();

    toastElem.addEventListener('hidden.bs.toast', () => {
        toastElem.remove();
    });
}

/* ==========================================================================
   DASHBOARD CONTROLLER
   ========================================================================== */
function initDashboard() {
    loadDashboardStats();
    
    // Auto-refresh stats every 12 seconds
    Sentinel.autoRefreshTimer = setInterval(loadDashboardStats, 12000);

    const refreshBtn = document.getElementById('refreshDashboardBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            loadDashboardStats();
            showNotification('Refreshed', 'SOC metrics and charts updated from backend.', 'info');
        });
    }
}

async function loadDashboardStats() {
    try {
        const res = await fetch('/api/stats');
        if (!res.ok) throw new Error('Failed to fetch statistics');
        const data = await res.json();

        // Update KPI values
        document.getElementById('kpiTotalRequests').innerText = data.kpis.total_requests.toLocaleString();
        document.getElementById('kpiSafeRequests').innerText = data.kpis.safe_requests.toLocaleString();
        document.getElementById('kpiSuspiciousRequests').innerText = data.kpis.suspicious_requests.toLocaleString();
        document.getElementById('kpiBlockedRequests').innerText = data.kpis.blocked_requests.toLocaleString();
        document.getElementById('kpiActiveAlerts').innerText = data.kpis.active_alerts.toLocaleString();
        document.getElementById('kpiAvgLatency').innerText = data.kpis.avg_latency_ms + ' ms';

        // Update Threat Banner
        const threatLevelEl = document.getElementById('threatLevelText');
        const threatBadgeEl = document.getElementById('threatLevelBadge');
        if (threatLevelEl && threatBadgeEl) {
            threatLevelEl.innerText = data.kpis.threat_level;
            threatBadgeEl.style.borderColor = data.kpis.threat_color;
            threatBadgeEl.style.color = data.kpis.threat_color;
        }

        // Render / Update Charts
        renderTrafficChart(data.charts.timeline);
        renderCategoryChart(data.charts.categories);

        // Render Recent Alerts
        renderRecentAlertsTable(data.recent_alerts);

        // Render Recent Requests
        renderRecentRequestsTable(data.recent_requests);

    } catch (err) {
        console.error('Error loading dashboard stats:', err);
    }
}

function renderTrafficChart(timelineData) {
    const ctx = document.getElementById('trafficTimelineChart');
    if (!ctx) return;

    if (Sentinel.trafficChart) {
        Sentinel.trafficChart.data.labels = timelineData.labels;
        Sentinel.trafficChart.data.datasets[0].data = timelineData.risk_scores;
        Sentinel.trafficChart.data.datasets[1].data = timelineData.latencies;
        Sentinel.trafficChart.update();
        return;
    }

    const context = ctx.getContext('2d');
    const gradientRisk = context.createLinearGradient(0, 0, 0, 240);
    gradientRisk.addColorStop(0, 'rgba(0, 240, 255, 0.35)');
    gradientRisk.addColorStop(0.6, 'rgba(0, 240, 255, 0.08)');
    gradientRisk.addColorStop(1, 'rgba(0, 240, 255, 0.0)');

    const gradientLatency = context.createLinearGradient(0, 0, 0, 240);
    gradientLatency.addColorStop(0, 'rgba(255, 183, 3, 0.25)');
    gradientLatency.addColorStop(1, 'rgba(255, 183, 3, 0.0)');

    Sentinel.trafficChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: timelineData.labels,
            datasets: [
                {
                    label: 'Risk Score (0-100)',
                    data: timelineData.risk_scores,
                    borderColor: '#00f0ff',
                    backgroundColor: gradientRisk,
                    borderWidth: 2.5,
                    tension: 0.4,
                    fill: true,
                    pointRadius: 4,
                    pointHoverRadius: 8,
                    pointBackgroundColor: '#00f0ff',
                    pointBorderColor: '#050811',
                    pointBorderWidth: 2,
                    yAxisID: 'y'
                },
                {
                    label: 'Latency (ms)',
                    data: timelineData.latencies,
                    borderColor: '#ffb703',
                    backgroundColor: gradientLatency,
                    borderWidth: 1.8,
                    borderDash: [5, 4],
                    tension: 0.3,
                    fill: true,
                    pointRadius: 3,
                    pointHoverRadius: 6,
                    pointBackgroundColor: '#ffb703',
                    pointBorderColor: '#050811',
                    pointBorderWidth: 2,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#94a3b8', font: { family: 'Inter', size: 11, weight: '600' } }
                },
                tooltip: {
                    backgroundColor: 'rgba(8, 12, 24, 0.95)',
                    titleColor: '#00f0ff',
                    bodyColor: '#f8fafc',
                    borderColor: 'rgba(0, 240, 255, 0.4)',
                    borderWidth: 1.5,
                    padding: 10,
                    boxPadding: 4,
                    usePointStyle: true
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.04)' },
                    ticks: { color: '#64748b', font: { family: 'Fira Code', size: 10 } }
                },
                y: {
                    min: 0,
                    max: 100,
                    position: 'left',
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#00f0ff', font: { size: 10, weight: '600' } },
                    title: { display: true, text: 'Risk Score (0-100)', color: '#00f0ff', font: { size: 11, weight: '700' } }
                },
                y1: {
                    min: 0,
                    position: 'right',
                    grid: { drawOnChartArea: false },
                    ticks: { color: '#ffb703', font: { size: 10, weight: '600' } },
                    title: { display: true, text: 'Latency (ms)', color: '#ffb703', font: { size: 11, weight: '700' } }
                }
            }
        }
    });
}

function renderCategoryChart(categoryData) {
    const ctx = document.getElementById('threatCategoryChart');
    if (!ctx) return;

    const colors = ['#ff2e63', '#ffb703', '#3b82f6', '#00f59b', '#a855f7', '#00f0ff'];

    if (Sentinel.categoryChart) {
        Sentinel.categoryChart.data.labels = categoryData.labels;
        Sentinel.categoryChart.data.datasets[0].data = categoryData.counts;
        Sentinel.categoryChart.update();
        return;
    }

    Sentinel.categoryChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: categoryData.labels,
            datasets: [{
                data: categoryData.counts,
                backgroundColor: colors.slice(0, categoryData.labels.length),
                borderColor: '#0a0f1d',
                borderWidth: 3,
                hoverOffset: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#94a3b8', font: { family: 'Inter', size: 10, weight: '500' }, padding: 8 }
                },
                tooltip: {
                    backgroundColor: 'rgba(8, 12, 24, 0.95)',
                    titleColor: '#00f0ff',
                    bodyColor: '#ffffff',
                    borderColor: 'rgba(0, 240, 255, 0.4)',
                    borderWidth: 1.5
                }
            },
            cutout: '70%'
        }
    });
}

function renderRecentAlertsTable(alerts) {
    const tbody = document.getElementById('recentAlertsTbody');
    if (!tbody) return;

    if (!alerts || alerts.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center text-muted py-4">No active security alerts recorded.</td></tr>`;
        return;
    }

    tbody.innerHTML = alerts.map(a => `
        <tr>
            <td>
                <span class="badge-soc ${getSeverityClass(a.severity)}">
                    ${a.severity}
                </span>
            </td>
            <td>
                <div class="fw-bold text-white">${escapeHtml(a.alert_title)}</div>
                <div class="small text-muted font-mono">${escapeHtml(a.endpoint)}</div>
            </td>
            <td class="font-mono text-cyan">${escapeHtml(a.source_ip)}</td>
            <td>
                <div class="fw-bold font-mono ${getRiskColorClass(a.risk_score)}">${a.risk_score} / 100</div>
                <div class="risk-meter">
                    <div class="risk-meter-fill ${getRiskFillClass(a.risk_score)}" style="width: ${a.risk_score}%"></div>
                </div>
            </td>
            <td class="text-end">
                <a href="/alerts" class="btn btn-sm btn-cyber-outline py-1 px-2">
                    <i class="bi bi-shield-shaded"></i> Triage
                </a>
            </td>
        </tr>
    `).join('');
}

function renderRecentRequestsTable(requests) {
    const tbody = document.getElementById('recentRequestsTbody');
    if (!tbody) return;

    if (!requests || requests.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center text-muted py-4">No traffic recorded yet.</td></tr>`;
        return;
    }

    tbody.innerHTML = requests.map(r => `
        <tr>
            <td>
                <span class="badge-method badge-${r.method.toLowerCase()}">${r.method}</span>
            </td>
            <td class="font-mono text-truncate" style="max-width: 180px;" title="${escapeHtml(r.endpoint)}">
                ${escapeHtml(r.endpoint)}
            </td>
            <td class="font-mono text-muted">${escapeHtml(r.ip_address)}</td>
            <td>
                <span class="badge ${r.status_code >= 400 ? 'bg-danger' : 'bg-success'} text-white font-mono">
                    ${r.status_code}
                </span>
            </td>
            <td>
                <span class="badge-soc ${getClassificationClass(r.classification)}">
                    ${r.classification}
                </span>
            </td>
            <td class="font-mono text-end ${getRiskColorClass(r.risk_score)} fw-bold">
                ${r.risk_score}
            </td>
        </tr>
    `).join('');
}

/* ==========================================================================
   TRAFFIC MONITORING CONTROLLER
   ========================================================================== */
function initTrafficPage() {
    loadTrafficData();

    // Event listeners for filters
    const searchInput = document.getElementById('trafficSearch');
    const methodFilter = document.getElementById('methodFilter');
    const classFilter = document.getElementById('classFilter');
    const statusFilter = document.getElementById('statusFilter');

    if (searchInput) {
        searchInput.addEventListener('input', debounce(() => {
            Sentinel.currentPage = 1;
            loadTrafficData();
        }, 300));
    }

    [methodFilter, classFilter, statusFilter].forEach(filter => {
        if (filter) {
            filter.addEventListener('change', () => {
                Sentinel.currentPage = 1;
                loadTrafficData();
            });
        }
    });

    const refreshBtn = document.getElementById('refreshTrafficBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => loadTrafficData());
    }
}

async function loadTrafficData() {
    const search = document.getElementById('trafficSearch')?.value || '';
    const method = document.getElementById('methodFilter')?.value || '';
    const classification = document.getElementById('classFilter')?.value || '';
    const status_code = document.getElementById('statusFilter')?.value || '';

    const params = new URLSearchParams({
        page: Sentinel.currentPage,
        per_page: Sentinel.perPage,
        search,
        method,
        classification,
        status_code
    });

    try {
        const res = await fetch(`/api/traffic?${params.toString()}`);
        if (!res.ok) throw new Error('Failed to load traffic');
        const data = await res.json();

        renderTrafficTable(data.items);
        renderPagination(data);

        // Update count badge
        const countBadge = document.getElementById('trafficCountBadge');
        if (countBadge) {
            countBadge.innerText = `${data.total} requests logged`;
        }

    } catch (err) {
        console.error('Error fetching traffic:', err);
    }
}

function renderTrafficTable(items) {
    const tbody = document.getElementById('trafficTableBody');
    if (!tbody) return;

    if (!items || items.length === 0) {
        tbody.innerHTML = `<tr><td colspan="9" class="text-center text-muted py-5">No API traffic matching search criteria.</td></tr>`;
        return;
    }

    tbody.innerHTML = items.map(r => `
        <tr>
            <td class="font-mono small text-cyan">${escapeHtml(r.request_id)}</td>
            <td class="small text-muted font-mono">${r.timestamp}</td>
            <td>
                <span class="badge-method badge-${r.method.toLowerCase()}">${r.method}</span>
            </td>
            <td class="font-mono text-truncate" style="max-width: 220px;" title="${escapeHtml(r.endpoint)}">
                ${escapeHtml(r.endpoint)}
            </td>
            <td class="font-mono text-muted small">${escapeHtml(r.ip_address)}</td>
            <td>
                <span class="badge ${r.status_code >= 400 ? 'bg-danger' : 'bg-success'} text-white font-mono">
                    ${r.status_code}
                </span>
            </td>
            <td class="font-mono small text-muted">${r.response_time_ms} ms</td>
            <td>
                <span class="badge-soc ${getClassificationClass(r.classification)}">
                    ${r.classification}
                </span>
            </td>
            <td>
                <div class="d-flex align-items-center gap-2">
                    <span class="font-mono fw-bold ${getRiskColorClass(r.risk_score)}">${r.risk_score}</span>
                    <button class="btn btn-sm btn-cyber-outline py-0 px-2 ms-auto" onclick="inspectRequest(${r.id})">
                        <i class="bi bi-search"></i> Inspect
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

function renderPagination(data) {
    const container = document.getElementById('trafficPagination');
    if (!container) return;

    if (data.pages <= 1) {
        container.innerHTML = '';
        return;
    }

    let html = `
        <li class="page-item ${!data.has_prev ? 'disabled' : ''}">
            <button class="page-link bg-dark text-cyan border-secondary" onclick="changePage(${data.page - 1})">Previous</button>
        </li>
    `;

    for (let p = 1; p <= data.pages; p++) {
        if (p === 1 || p === data.pages || (p >= data.page - 1 && p <= data.page + 1)) {
            html += `
                <li class="page-item ${p === data.page ? 'active' : ''}">
                    <button class="page-link ${p === data.page ? 'bg-primary border-primary text-white' : 'bg-dark text-cyan border-secondary'}" onclick="changePage(${p})">${p}</button>
                </li>
            `;
        } else if (p === data.page - 2 || p === data.page + 2) {
            html += `<li class="page-item disabled"><span class="page-link bg-dark text-muted border-secondary">...</span></li>`;
        }
    }

    html += `
        <li class="page-item ${!data.has_next ? 'disabled' : ''}">
            <button class="page-link bg-dark text-cyan border-secondary" onclick="changePage(${data.page + 1})">Next</button>
        </li>
    `;

    container.innerHTML = html;
}

function changePage(page) {
    Sentinel.currentPage = page;
    loadTrafficData();
}

async function inspectRequest(reqId) {
    try {
        const res = await fetch(`/api/traffic/${reqId}`);
        if (!res.ok) throw new Error('Inspection failed');
        const data = await res.json();
        const r = data.request;

        document.getElementById('inspectReqId').innerText = r.request_id;
        document.getElementById('inspectMethod').innerText = r.method;
        document.getElementById('inspectEndpoint').innerText = r.endpoint;
        document.getElementById('inspectIp').innerText = r.ip_address;
        document.getElementById('inspectTimestamp').innerText = r.timestamp;
        document.getElementById('inspectStatus').innerText = r.status_code;
        document.getElementById('inspectLatency').innerText = `${r.response_time_ms} ms`;
        document.getElementById('inspectPayloadSize').innerText = `${r.payload_size} bytes`;
        document.getElementById('inspectUserAgent').innerText = r.user_agent;
        
        // ML Assessment
        document.getElementById('inspectClassification').innerHTML = `<span class="badge-soc ${getClassificationClass(r.classification)}">${r.classification}</span>`;
        document.getElementById('inspectRiskScore').innerHTML = `<span class="font-mono fw-bold fs-5 ${getRiskColorClass(r.risk_score)}">${r.risk_score} / 100</span>`;
        document.getElementById('inspectAnomalyScore').innerText = r.anomaly_score + ' / 100';
        document.getElementById('inspectThreatType').innerText = r.threat_type;
        document.getElementById('inspectBlocked').innerHTML = r.is_blocked 
            ? `<span class="badge bg-danger">BLOCKED AT WAF</span>` 
            : `<span class="badge bg-success">PASSED</span>`;

        // Explainability Reasons
        const reasonsList = document.getElementById('inspectReasonsList');
        if (reasonsList) {
            const reasonsArr = r.reasons.split('; ');
            reasonsList.innerHTML = reasonsArr.map(reason => `
                <li class="list-group-item bg-dark text-light border-secondary small d-flex align-items-center gap-2">
                    <i class="bi bi-arrow-right-circle text-cyan"></i> ${escapeHtml(reason)}
                </li>
            `).join('');
        }

        const modal = new bootstrap.Modal(document.getElementById('requestInspectModal'));
        modal.show();

    } catch (err) {
        showNotification('Error', 'Unable to inspect request details.', 'danger');
    }
}

/* ==========================================================================
   THREAT ALERTS CONTROLLER
   ========================================================================== */
function initAlertsPage() {
    loadAlertsData();

    const sevFilter = document.getElementById('alertSeverityFilter');
    const statusFilter = document.getElementById('alertStatusFilter');
    const searchInput = document.getElementById('alertSearch');

    if (sevFilter) sevFilter.addEventListener('change', () => loadAlertsData());
    if (statusFilter) statusFilter.addEventListener('change', () => loadAlertsData());
    if (searchInput) searchInput.addEventListener('input', debounce(() => loadAlertsData(), 300));
}

async function loadAlertsData() {
    const severity = document.getElementById('alertSeverityFilter')?.value || '';
    const status = document.getElementById('alertStatusFilter')?.value || '';
    const search = document.getElementById('alertSearch')?.value || '';

    const params = new URLSearchParams({ severity, status, search });

    try {
        const res = await fetch(`/api/alerts?${params.toString()}`);
        if (!res.ok) throw new Error('Failed to load alerts');
        const alerts = await res.json();

        renderAlertsCards(alerts);

        const countEl = document.getElementById('totalAlertsCount');
        if (countEl) countEl.innerText = `${alerts.length} Incidents`;

    } catch (err) {
        console.error('Error fetching alerts:', err);
    }
}

function renderAlertsCards(alerts) {
    const container = document.getElementById('alertsCardsContainer');
    if (!container) return;

    if (!alerts || alerts.length === 0) {
        container.innerHTML = `
            <div class="col-12 text-center py-5">
                <i class="bi bi-shield-check display-4 text-emerald"></i>
                <h5 class="mt-3 text-light">No Threats or Security Incidents Active</h5>
                <p class="text-muted">Use the Attack Simulation Lab to simulate live threat detection scenarios.</p>
            </div>
        `;
        return;
    }

    container.innerHTML = alerts.map(a => `
        <div class="col-md-6 col-xl-4 mb-4">
            <div class="soc-card h-100 d-flex flex-column justify-content-between border-${getBorderColorName(a.severity)}">
                <div>
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span class="badge-soc ${getSeverityClass(a.severity)}">
                            <i class="bi bi-shield-exclamation"></i> ${a.severity}
                        </span>
                        <span class="badge bg-secondary text-light font-mono small">${a.category}</span>
                    </div>

                    <h5 class="text-white fw-bold mb-1">${escapeHtml(a.alert_title)}</h5>
                    <div class="font-mono text-cyan small mb-2">${escapeHtml(a.endpoint)}</div>
                    
                    <div class="d-flex align-items-center justify-content-between my-2 p-2 rounded bg-black">
                        <span class="text-muted small">Source IP: <strong class="text-light font-mono">${escapeHtml(a.source_ip)}</strong></span>
                        <span class="font-mono fw-bold ${getRiskColorClass(a.risk_score)}">Risk: ${a.risk_score}/100</span>
                    </div>

                    <p class="small text-light opacity-80 mb-3">${escapeHtml(a.description)}</p>

                    <div class="p-2 rounded border border-secondary bg-dark mb-3">
                        <div class="small fw-bold text-cyan mb-1"><i class="bi bi-play-circle me-1"></i>SOC Recommended Playbook:</div>
                        <div class="small text-light">${escapeHtml(a.recommended_action)}</div>
                    </div>
                </div>

                <div class="d-flex align-items-center justify-content-between pt-2 border-top border-secondary">
                    <span class="badge ${getStatusBadgeClass(a.status)}">${a.status}</span>
                    <div class="btn-group btn-group-sm">
                        ${a.status !== 'Mitigated' ? `
                            <button class="btn btn-soc-danger" onclick="updateAlertStatus(${a.id}, 'Mitigated')">
                                <i class="bi bi-ban"></i> Mitigate IP
                            </button>
                        ` : ''}
                        ${a.status !== 'Resolved' ? `
                            <button class="btn btn-cyber-outline" onclick="updateAlertStatus(${a.id}, 'Resolved')">
                                <i class="bi bi-check2-circle"></i> Resolve
                            </button>
                        ` : ''}
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

async function updateAlertStatus(alertId, newStatus) {
    try {
        const res = await fetch(`/api/alerts/${alertId}/status`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus })
        });
        const data = await res.json();
        if (res.ok) {
            showNotification('Status Updated', data.message, 'success');
            loadAlertsData();
        } else {
            showNotification('Error', data.error || 'Failed to update alert.', 'danger');
        }
    } catch (err) {
        showNotification('Error', 'Communication failure.', 'danger');
    }
}

/* ==========================================================================
   ATTACK SIMULATION LAB CONTROLLER
   ========================================================================== */
function initSimulationPage() {
    const consoleEl = document.getElementById('simConsole');

    window.triggerSim = async function(type, subtype = '') {
        appendConsole(`[DISPATCH] Initiating ${type.toUpperCase()} simulation against API Sentinel...`, 'cmd');

        try {
            const bodyPayload = { type, params: {} };
            if (subtype) bodyPayload.params.subtype = subtype;

            const res = await fetch('/api/simulate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(bodyPayload)
            });

            const data = await res.json();

            if (res.ok) {
                appendConsole(`[ENGINE] Simulation ID: ${data.sim_id}`, 'info');
                appendConsole(`[INGEST] Generated ${data.requests_count} simulated request packets into SQLite`, 'info');
                appendConsole(`[AI/ML] Processed through Random Forest & Isolation Forest`, 'info');
                appendConsole(`[RISK] Calculated Average Risk Score: ${data.avg_risk_score}/100`, data.avg_risk_score > 60 ? 'danger' : 'success');
                
                if (data.threats_detected > 0) {
                    appendConsole(`[ALERT] Generated ${data.threats_detected} High/Critical Security Alerts!`, 'danger');
                    data.alerts.forEach(a => {
                        appendConsole(` -> ${a.alert_title} on ${a.endpoint} from IP ${a.source_ip}`, 'danger');
                    });
                } else {
                    appendConsole(`[STATUS] All requests classified as Safe/Normal. Zero alerts generated.`, 'success');
                }

                showNotification('Simulation Completed', data.message, data.threats_detected > 0 ? 'warning' : 'success');
                loadSimulationHistory();

            } else {
                appendConsole(`[ERROR] Simulation failed: ${data.error}`, 'danger');
            }

        } catch (err) {
            appendConsole(`[NETWORK ERROR] Could not contact simulation backend: ${err.message}`, 'danger');
        }
    };

    const clearConsoleBtn = document.getElementById('clearConsoleBtn');
    if (clearConsoleBtn) {
        clearConsoleBtn.addEventListener('click', () => {
            if (consoleEl) consoleEl.innerHTML = '<div class="console-line info"><i class="bi bi-terminal me-1"></i>[SYSTEM] Console buffer cleared. Ready for attack execution.</div>';
        });
    }

    loadSimulationHistory();
}

function appendConsole(msg, lineClass = 'info') {
    const consoleEl = document.getElementById('simConsole');
    if (!consoleEl) return;

    const time = new Date().toLocaleTimeString();
    const line = document.createElement('div');
    line.className = `console-line ${lineClass}`;
    line.innerHTML = `<span class="text-muted">[${time}]</span> ${escapeHtml(msg)}`;
    consoleEl.appendChild(line);
    consoleEl.scrollTop = consoleEl.scrollHeight;
}

async function loadSimulationHistory() {
    try {
        const res = await fetch('/api/logs?event_type=SIMULATION');
        if (!res.ok) return;
        const logs = await res.json();

        const tbody = document.getElementById('simHistoryTbody');
        if (!tbody) return;

        if (logs.length === 0) {
            tbody.innerHTML = `<tr><td colspan="4" class="text-center text-muted py-3">No simulations executed in this session.</td></tr>`;
            return;
        }

        tbody.innerHTML = logs.slice(0, 5).map(l => `
            <tr>
                <td class="font-mono text-cyan small">${l.timestamp}</td>
                <td><span class="badge bg-secondary font-mono">${escapeHtml(l.detection_result)}</span></td>
                <td class="font-mono ${getRiskColorClass(l.risk_score)} fw-bold">${l.risk_score}</td>
                <td class="small text-light">${escapeHtml(l.details)}</td>
            </tr>
        `).join('');
    } catch (e) {
        console.warn('Error loading sim history:', e);
    }
}

/* ==========================================================================
   AI / ML MODEL METRICS CONTROLLER
   ========================================================================== */
async function initModelsPage() {
    try {
        const res = await fetch('/api/model-metrics');
        if (!res.ok) throw new Error('Failed to load metrics');
        const data = await res.json();

        const m = data.metrics;

        // Populate KPIs
        document.getElementById('metricAccuracy').innerText = (m.accuracy * 100).toFixed(1) + '%';
        document.getElementById('metricPrecision').innerText = (m.precision * 100).toFixed(1) + '%';
        document.getElementById('metricRecall').innerText = (m.recall * 100).toFixed(1) + '%';
        document.getElementById('metricF1').innerText = (m.f1_score * 100).toFixed(1) + '%';
        document.getElementById('metricTrainSamples').innerText = m.train_sample_size.toLocaleString();
        document.getElementById('metricTestSamples').innerText = m.test_sample_size.toLocaleString();

        // Populate Confusion Matrix Visual Heatmap
        renderConfusionMatrix(data.confusion_matrix);

        // Populate Feature Importance Chart
        renderFeatureImportanceChart(data.feature_importances);

        // Populate Per-Class Breakdown Table
        renderClassMetricsTable(m.class_metrics);

    } catch (err) {
        console.error('Error initializing models page:', err);
    }
}

function renderConfusionMatrix(matrix) {
    const container = document.getElementById('confusionMatrixContainer');
    if (!container || !matrix) return;

    const labels = ['True Normal', 'True Suspicious', 'True Attack'];
    const predLabels = ['Pred Normal', 'Pred Suspicious', 'Pred Attack'];

    let html = `
        <table class="cm-table">
            <thead>
                <tr>
                    <th class="text-light-silver small fw-bold">Actual \\ Pred</th>
                    ${predLabels.map(p => `<th class="text-cyan small fw-bold">${p}</th>`).join('')}
                </tr>
            </thead>
            <tbody>
    `;

    for (let i = 0; i < matrix.length; i++) {
        html += `<tr><td class="text-light-silver small fw-bold text-start">${labels[i]}</td>`;
        for (let j = 0; j < matrix[i].length; j++) {
            const count = matrix[i][j];
            const isDiagonal = (i === j);
            html += `
                <td>
                    <div class="cm-cell ${isDiagonal ? 'cm-diagonal' : (count > 0 ? 'cm-off-diagonal' : 'cm-zero')}">
                        ${count}
                    </div>
                </td>
            `;
        }
        html += `</tr>`;
    }

    html += `</tbody></table>`;
    container.innerHTML = html;
}

function renderFeatureImportanceChart(features) {
    const ctx = document.getElementById('featureImportanceChart');
    if (!ctx || !features) return;

    const labels = features.map(f => f.feature);
    const values = features.map(f => f.importance);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Relative Importance Weight',
                data: values,
                backgroundColor: 'rgba(0, 240, 255, 0.45)',
                borderColor: '#00f0ff',
                borderWidth: 1.5,
                borderRadius: 4
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#111827',
                    titleColor: '#00f0ff',
                    bodyColor: '#ffffff',
                    callbacks: {
                        label: (ctx) => `Importance: ${(ctx.raw * 100).toFixed(2)}%`
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#64748b' }
                },
                y: {
                    grid: { display: false },
                    ticks: { color: '#f8fafc', font: { family: 'Inter', size: 11 } }
                }
            }
        }
    });
}

function renderClassMetricsTable(classMetrics) {
    const tbody = document.getElementById('classMetricsTbody');
    if (!tbody || !classMetrics) return;

    tbody.innerHTML = Object.entries(classMetrics).map(([className, m]) => `
        <tr>
            <td class="fw-bold text-white">${className}</td>
            <td class="font-mono text-cyan">${(m.precision * 100).toFixed(1)}%</td>
            <td class="font-mono text-emerald">${(m.recall * 100).toFixed(1)}%</td>
            <td class="font-mono text-amber">${(m.f1_score * 100).toFixed(1)}%</td>
            <td class="font-mono text-muted">${m.support}</td>
        </tr>
    `).join('');
}

/* ==========================================================================
   SECURITY LOGS CONTROLLER
   ========================================================================== */
function initLogsPage() {
    loadLogsData();

    const typeFilter = document.getElementById('logTypeFilter');
    const searchInput = document.getElementById('logSearch');

    if (typeFilter) typeFilter.addEventListener('change', () => loadLogsData());
    if (searchInput) searchInput.addEventListener('input', debounce(() => loadLogsData(), 300));
}

async function loadLogsData() {
    const event_type = document.getElementById('logTypeFilter')?.value || '';
    const search = document.getElementById('logSearch')?.value || '';

    const params = new URLSearchParams({ event_type, search });

    try {
        const res = await fetch(`/api/logs?${params.toString()}`);
        if (!res.ok) throw new Error('Failed to load logs');
        const logs = await res.json();

        const tbody = document.getElementById('logsTableBody');
        if (!tbody) return;

        if (logs.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" class="text-center text-muted py-5">No security audit logs recorded.</td></tr>`;
            return;
        }

        tbody.innerHTML = logs.map(l => `
            <tr>
                <td class="font-mono small text-muted">${l.timestamp}</td>
                <td><span class="badge ${getLogTypeBadge(l.event_type)} font-mono">${l.event_type}</span></td>
                <td class="font-mono text-cyan small">${escapeHtml(l.source_ip)}</td>
                <td class="font-mono small text-light">${escapeHtml(l.endpoint)}</td>
                <td class="font-mono ${getRiskColorClass(l.risk_score)} fw-bold">${l.risk_score}</td>
                <td class="small text-light">${escapeHtml(l.detection_result)}</td>
                <td class="small text-muted font-mono">${escapeHtml(l.action_taken)}</td>
            </tr>
        `).join('');

    } catch (err) {
        console.error('Error fetching logs:', err);
    }
}

/* ==========================================================================
   UTILITY & STYLING HELPERS
   ========================================================================== */
function getSeverityClass(sev) {
    switch ((sev || '').toLowerCase()) {
        case 'critical': return 'badge-critical';
        case 'high': return 'badge-high';
        case 'medium': return 'badge-medium';
        default: return 'badge-low';
    }
}

function getClassificationClass(cls) {
    switch ((cls || '').toLowerCase()) {
        case 'potential attack': return 'badge-attack';
        case 'suspicious': return 'badge-suspicious';
        default: return 'badge-safe';
    }
}

function getRiskColorClass(score) {
    if (score >= 80) return 'text-crimson';
    if (score >= 60) return 'text-amber';
    if (score >= 30) return 'text-warning';
    return 'text-emerald';
}

function getRiskFillClass(score) {
    if (score >= 80) return 'risk-fill-critical';
    if (score >= 60) return 'risk-fill-high';
    if (score >= 30) return 'risk-fill-medium';
    return 'risk-fill-low';
}

function getBorderColorName(sev) {
    switch ((sev || '').toLowerCase()) {
        case 'critical': return 'danger';
        case 'high': return 'warning';
        case 'medium': return 'info';
        default: return 'secondary';
    }
}

function getStatusBadgeClass(st) {
    switch ((st || '').toLowerCase()) {
        case 'active': return 'bg-danger';
        case 'investigating': return 'bg-warning text-dark';
        case 'mitigated': return 'bg-info text-dark';
        case 'resolved': return 'bg-success';
        default: return 'bg-secondary';
    }
}

function getLogTypeBadge(type) {
    switch ((type || '').toUpperCase()) {
        case 'DETECTION': return 'bg-danger';
        case 'BLOCK': return 'bg-danger';
        case 'AUTH': return 'bg-primary';
        case 'SIMULATION': return 'bg-info text-dark';
        case 'SYSTEM': return 'bg-secondary';
        default: return 'bg-dark';
    }
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

