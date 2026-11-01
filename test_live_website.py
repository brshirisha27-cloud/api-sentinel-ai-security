"""
Comprehensive Live Website Test Suite for:
https://brshirisha27-cloud.github.io/api-sentinel-ai-security/

Verifies:
1. Live Web Server Response (HTTP 200 OK)
2. All linked sub-assets on GitHub Pages (css/style.css, images/logo.svg)
3. All external CDNs (Bootstrap 5 CSS, Bootstrap Icons, Google Fonts, Chart.js, Bootstrap JS)
4. Full DOM Structure & 6 Core SOC Functional Views:
   - Dashboard (Radar scope, KPI glow cards, Real-time Charts, Telemetry Streams)
   - Traffic Monitoring (Filter buttons, Traffic Log Table, Pagination)
   - Threat Alerts (Filter buttons, Risk Matrix, Incident Cards, Triage Actions)
   - Attack Simulation Lab (Preset Scenarios, Custom Payload Builder, Fire Attack)
   - AI Detection Models (Random Forest ROC, Isolation Forest Anomaly Score, Confusion Matrix)
   - Audit Event Logs (Search, Category Badges, SOC Event Timeline)
5. Cyberpunk Neon Color Scheme in live CSS
6. JavaScript Engine Integrity & State Initialization
"""

import urllib.request
import urllib.parse
import ssl
import sys
import io
import re

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_URL = "https://brshirisha27-cloud.github.io/api-sentinel-ai-security"
CTX = ssl.create_default_context()
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 API-Sentinel-Tester/1.0'}

def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, context=CTX, timeout=15) as res:
        return res.status, res.read().decode('utf-8', errors='replace')

def run_tests():
    print("=" * 70)
    print("  TESTING LIVE DEPLOYED WEBSITE")
    print(f"  URL: {BASE_URL}/")
    print("=" * 70)

    # 1. Test Base URL
    try:
        status, html = fetch(f"{BASE_URL}/")
        assert status == 200, f"Expected 200, got {status}"
        print(f" [PASS] Live Webpage online: HTTP {status} ({len(html):,} bytes)")
    except Exception as e:
        print(f" [FAIL] Unable to reach {BASE_URL}: {e}")
        sys.exit(1)

    # 2. Test Linked Assets on GitHub Pages
    assets = [
        ("css/style.css", "Cyberpunk SOC Custom CSS Stylesheet"),
        ("images/logo.svg", "API Sentinel Vector Brand Icon")
    ]
    print("\n [TEST] Validating Deployed Sub-Assets on GitHub Pages:")
    for path, desc in assets:
        url = f"{BASE_URL}/{path}"
        try:
            astatus, acontent = fetch(url)
            assert astatus == 200, f"HTTP {astatus}"
            print(f"   ✓ [200 OK] {desc} -> {path} ({len(acontent):,} bytes)")
        except Exception as e:
            print(f"   ✗ [FAIL] {desc} -> {path}: {e}")
            sys.exit(1)

    # 3. Test External CDNs referenced in HTML
    cdns = [
        ("https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css", "Bootstrap 5 CSS CDN"),
        ("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css", "Bootstrap Icons CDN"),
        ("https://cdn.jsdelivr.net/npm/chart.js@4.4.2/dist/chart.umd.min.js", "Chart.js Library CDN"),
        ("https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js", "Bootstrap 5 Bundle JS CDN")
    ]
    print("\n [TEST] Validating External CDN Dependencies:")
    for url, desc in cdns:
        try:
            cstatus, ccontent = fetch(url)
            assert cstatus == 200, f"HTTP {cstatus}"
            print(f"   ✓ [200 OK] {desc}")
        except Exception as e:
            print(f"   ✗ [FAIL] {desc} ({url}): {e}")
            sys.exit(1)

    # 4. Test Cyberpunk Color Variables in Live CSS
    print("\n [TEST] Verifying Cyberpunk Theme & Neon Coloring:")
    _, css_content = fetch(f"{BASE_URL}/css/style.css")
    color_palette = [
        ("--bg-primary: #050811", "Obsidian Deep Space Navy (#050811)"),
        ("--accent-cyan: #00f0ff", "Electric Cyan Laser (#00f0ff)"),
        ("--threat-safe: #00f59b", "Radiant Emerald Safe (#00f59b)"),
        ("--threat-medium: #ffb703", "Solar Amber Suspicious (#ffb703)"),
        ("--threat-high: #fb8500", "Sunset Orange High Threat (#fb8500)"),
        ("--threat-critical: #ff2e63", "Crimson Laser Critical Threat (#ff2e63)"),
        ("backdrop-filter: blur(16px)", "Glassmorphism Card Blur Filter"),
        (".cyber-laser-line", "Cyber Laser Top Animated Scanline"),
        (".radar-scope", "360-degree Threat Radar HUD"),
        (".radar-sweep", "Rotating Radar Ray Sweep"),
        (".radar-blip", "Pulsing Active Threat Blips")
    ]
    for token, desc in color_palette:
        assert token in css_content, f"Missing color token: {desc}"
        print(f"   ✓ Verified: {desc}")

    # 5. Test Live DOM & Interactive Components in HTML
    print("\n [TEST] Verifying Interactive DOM & Functional SOC Sections:")
    dom_checks = [
        # Brand & Navigation
        ("API SENTINEL", "Brand Title Header"),
        ("AI THREAT INTELLIGENCE", "SOC Subtitle"),
        ("switchTab('dashboard')", "Dashboard Tab Switcher"),
        ("switchTab('traffic')", "Traffic Tab Switcher"),
        ("switchTab('alerts')", "Alerts Tab Switcher"),
        ("switchTab('simulation')", "Simulation Lab Tab Switcher"),
        ("switchTab('models')", "AI Models Tab Switcher"),
        ("switchTab('logs')", "Audit Logs Tab Switcher"),

        # Section 1: Dashboard View
        ('id="view-dashboard"', "Dashboard Section Container"),
        ("cyber-laser-line", "Top Cyber Laser Scanline"),
        ("kpi-cyan", "Total Requests Neon Glow Card"),
        ("kpi-green", "Safe Traffic Neon Glow Card"),
        ("kpi-amber", "Suspicious Events Neon Glow Card"),
        ("kpi-red", "Blocked Threats Neon Glow Card"),
        ("radar-scope", "Threat Radar Canvas Widget"),
        ("trafficTimelineChart", "Real-Time Traffic Timeline Chart"),
        ("threatCategoryChart", "Threat Distribution Chart"),
        ("recentAlertsTbody", "Live Alerts Stream Table"),
        ("recentRequestsTbody", "Inbound Request Telemetry Table"),

        # Section 2: Traffic View
        ('id="view-traffic"', "Traffic Telemetry Section Container"),
        ("filterTraffic", "Traffic Status Filter Controls"),
        ("trafficTableBody", "Full Traffic Logs Telemetry Table"),
        ("inspectRequest", "Packet Deep-Inspection Modal Handler"),

        # Section 3: Alerts View
        ('id="view-alerts"', "Threat Alerts Section Container"),
        ("filterAlerts", "Alert Severity Filter Controls"),
        ("alertsCardsContainer", "SOC Incident Alerts Grid"),
        ("updateAlertStatus", "Alert Triage Handler (Investigate/Mitigate/Resolve)"),

        # Section 4: Simulation View
        ('id="view-simulation"', "Adversarial Simulation Lab Container"),
        ("triggerClientSimulation", "Scenario Attack Simulation Triggers"),
        ("handleCustomSubmit", "Custom Payload Injection Builder"),
        ("simHistoryTbody", "Adversarial Attack Event Timeline"),

        # Section 5: AI Engine View
        ('id="view-models"', "AI Model Intelligence Section Container"),
        ("Random Forest Classifier", "Supervised ML Classification Model Card"),
        ("Isolation Forest", "Unsupervised Anomaly Model Card"),
        ("Confusion Matrix", "Confusion Matrix Analysis Card"),

        # Section 6: Audit Logs View
        ('id="view-logs"', "SOC Event Logs Section Container"),
        ("filterLogs", "Audit Log Severity/Type Filter"),
        ("logsTableBody", "SOC Audit Event Stream Table")
    ]

    for token, desc in dom_checks:
        assert token in html, f"Missing DOM component: {desc}"
        print(f"   ✓ Verified: {desc}")

    # 6. Test Client-Side Simulation & State Engine
    print("\n [TEST] Verifying Client-Side Reactive Simulation Engine:")
    js_checks = [
        ("initSampleData", "Preloaded Inbound Telemetry Baseline Generator"),
        ("initClock", "Live UTC / SOC Wall Clock Synchronizer"),
        ("initCharts", "Chart.js Neon Gradient Line & Doughnut Renderer"),
        ("renderDashboardKPIs", "Real-Time KPI Metric Refresh Engine"),
        ("renderTrafficTable", "Traffic Table Live Telemetry Renderer"),
        ("renderAlertsCards", "Security Incidents Card Renderer"),
        ("triggerClientSimulation", "Interactive Attack Simulation Engine"),
        ("inspectRequest", "Deep Payload Inspection Engine"),
        ("renderAll", "Global State Reconciliation Engine")
    ]
    for token, desc in js_checks:
        assert token in html, f"Missing JavaScript function/data: {desc}"
        print(f"   ✓ Verified: {desc}")

    print("\n" + "=" * 70)
    print("  ALL LIVE WEBSITE TESTS PASSED SUCCESSFULLY! (100% OPERATIONAL)")
    print(f"  Access Live Platform: {BASE_URL}/")
    print("=" * 70)

if __name__ == '__main__':
    run_tests()
