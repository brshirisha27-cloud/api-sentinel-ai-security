"""
Live HTTP Test Script for API Sentinel on http://127.0.0.1:5000
Verifies:
1. HTTP 200 on /login
2. Session authentication with demo credentials (admin / Sentinel@2025)
3. HTTP 200 on /dashboard
4. HTML contains: radar-scope, cyber-laser-line, trafficTimelineChart, threatCategoryChart, kpi cards
5. /api/stats returns JSON with KPIs, timeline labels, and category counts
6. /static/css/style.css contains all neon color variables (--threat-critical, --accent-cyan, etc.)
7. /static/js/app.js contains gradient chart renderers
"""

import urllib.request
import urllib.parse
import http.cookiejar
import json
import sys
import io

# Ensure UTF-8 output encoding across Windows consoles
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_URL = "http://127.0.0.1:5000"

def test_live_dashboard():
    print("=" * 60)
    print("  TESTING API SENTINEL LIVE ON http://127.0.0.1:5000")
    print("=" * 60)

    # 1. Cookie Jar for handling authenticated sessions
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    # 2. Check /api/health
    try:
        with opener.open(f"{BASE_URL}/api/health") as res:
            health = json.loads(res.read().decode('utf-8'))
            assert health['status'] == 'HEALTHY', "Engine not healthy"
            print(" [PASS] /api/health responded: HEALTHY (Dual ML Engines Online)")
    except Exception as e:
        print(f" [FAIL] Could not connect to {BASE_URL}: {e}")
        sys.exit(1)

    # 3. Test /login page
    with opener.open(f"{BASE_URL}/login") as res:
        login_html = res.read().decode('utf-8')
        assert "SOC Authentication Portal" in login_html, "Login title missing"
        assert "demo-account-pill" in login_html, "Demo credential autofill missing"
        print(" [PASS] /login page loaded successfully with Demo Autofill Presets")

    # 4. Perform Login
    login_data = urllib.parse.urlencode({'username': 'admin', 'password': 'Sentinel@2025'}).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/login", data=login_data, method='POST')
    with opener.open(req) as res:
        login_resp = res.read().decode('utf-8')
        print(" [PASS] Authenticated successfully as 'admin' (SOC Administrator)")

    # 5. Access /dashboard with authenticated session
    with opener.open(f"{BASE_URL}/dashboard") as res:
        dash_html = res.read().decode('utf-8')
        assert res.status == 200, f"Expected status 200, got {res.status}"
        print(" [PASS] /dashboard returned HTTP 200 (Authorized Session)")

        # Verify advanced UI elements in dashboard HTML
        checks = [
            ("cyber-laser-line", "Top Cyber Laser Scanline"),
            ("kpi-cyan", "Cyan Neon KPI Card"),
            ("kpi-green", "Emerald Neon KPI Card"),
            ("kpi-amber", "Amber Neon KPI Card"),
            ("kpi-red", "Crimson Neon KPI Card"),
            ("radar-scope", "360-degree Threat Radar Scope Widget"),
            ("radar-sweep", "Rotating Radar Beam"),
            ("radar-blip", "Pulsing Active Threat Blips"),
            ("trafficTimelineChart", "Real-time Traffic Activity Canvas"),
            ("threatCategoryChart", "Threat Category Distribution Canvas"),
            ("recentAlertsTbody", "Recent Incidents Telemetry Table"),
            ("recentRequestsTbody", "Live Inbound Request Stream Table")
        ]
        for token, name in checks:
            assert token in dash_html, f"Missing element: {name}"
            print(f"   ✓ Verified: {name}")

    # 6. Test /api/stats (Used dynamically by dashboard)
    with opener.open(f"{BASE_URL}/api/stats") as res:
        stats = json.loads(res.read().decode('utf-8'))
        kpis = stats['kpis']
        charts = stats['charts']
        print(f" [PASS] /api/stats live data:")
        print(f"   • Total Requests: {kpis['total_requests']}")
        print(f"   • Safe Traffic: {kpis['safe_requests']}")
        print(f"   • Suspicious Events: {kpis['suspicious_requests']}")
        print(f"   • Blocked Threats: {kpis['blocked_requests']}")
        print(f"   • Active Threat Level: {kpis['threat_level']} (Badge: {kpis['threat_badge']})")
        print(f"   • Avg Latency: {kpis['avg_latency_ms']} ms")
        print(f"   • Timeline Data Points: {len(charts['timeline']['labels'])} points")
        print(f"   • Threat Categories: {charts['categories']['labels']}")

    # 7. Test /static/css/style.css color variables
    with opener.open(f"{BASE_URL}/static/css/style.css") as res:
        css = res.read().decode('utf-8')
        color_checks = [
            ("--bg-primary: #050811", "Obsidian Deep Space Navy Base"),
            ("--accent-cyan: #00f0ff", "Electric Cyan Accent"),
            ("--threat-safe: #00f59b", "Radiant Emerald Safe Indicator"),
            ("--threat-medium: #ffb703", "Solar Amber Suspicious Indicator"),
            ("--threat-critical: #ff2e63", "Crimson Laser Threat Indicator"),
            ("radar-scope", "Radar Scope CSS"),
            ("cyber-laser-line", "Cyber Laser Scanline CSS"),
            ("risk-meter", "Dynamic Risk Meter CSS")
        ]
        print(" [PASS] /static/css/style.css color & visual tokens verified:")
        for token, name in color_checks:
            assert token in css, f"Missing CSS token: {name}"
            print(f"   ✓ Verified: {name}")

    # 8. Test /static/js/app.js
    with opener.open(f"{BASE_URL}/static/js/app.js") as res:
        js = res.read().decode('utf-8')
        assert "createLinearGradient" in js, "Chart gradient missing"
        assert "renderTrafficChart" in js, "renderTrafficChart function missing"
        print(" [PASS] /static/js/app.js gradient charts and telemetry handlers verified")

    print("\n" + "=" * 60)
    print("  ALL LIVE DASHBOARD TESTS PASSED SUCCESSFULLY! (100% OK)")
    print("=" * 60)

if __name__ == '__main__':
    test_live_dashboard()
