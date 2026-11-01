"""
API SENTINEL - Comprehensive Verification & Test Suite
Validates backend routes, authentication, database persistence,
ML inference, and attack simulations.
"""

import unittest
from app import app
from models import db, User, APIRequest, SecurityAlert, SimulationEvent, SecurityLog
from simulator import seed_database

class APISentinelTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        seed_database(app)

    def login(self, username='admin', password='Sentinel@2025'):
        return self.client.post('/login', data={
            'username': username,
            'password': password
        }, follow_redirects=True)

    def test_health_endpoint(self):
        """Test health check endpoint without authentication."""
        res = self.client.get('/api/health')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'HEALTHY')
        self.assertEqual(data['database'], 'ONLINE')
        self.assertEqual(data['ml_engine']['random_forest'], 'ONLINE')
        self.assertEqual(data['ml_engine']['isolation_forest'], 'ONLINE')
        print(" [PASS] /api/health returns HEALTHY and dual engines online")

    def test_unauthenticated_redirect(self):
        """Unauthenticated user accessing /dashboard should redirect to /login."""
        res = self.client.get('/dashboard')
        self.assertEqual(res.status_code, 302)
        self.assertIn('/login', res.headers['Location'])
        print(" [PASS] Protected /dashboard redirects unauthenticated users to /login")

    def test_authentication_workflow(self):
        """Test login with demo credentials and logout."""
        # Invalid password
        bad_res = self.client.post('/login', data={'username': 'admin', 'password': 'WrongPassword'}, follow_redirects=True)
        self.assertIn(b'Invalid username or password', bad_res.data)

        # Valid password
        good_res = self.login()
        self.assertEqual(good_res.status_code, 200)
        self.assertIn(b'Security Operations Center', good_res.data)

        # Logout
        logout_res = self.client.get('/logout', follow_redirects=True)
        self.assertIn(b'You have been logged out securely', logout_res.data)
        print(" [PASS] Authentication workflow (bad credentials, successful login, logout)")

    def test_pages_render_when_logged_in(self):
        """Verify all major pages render HTTP 200 with appropriate titles."""
        self.login()
        pages = [
            ('/dashboard', b'Security Operations Center'),
            ('/traffic', b'API Traffic Telemetry'),
            ('/alerts', b'Security Incidents'),
            ('/simulation', b'Adversarial Attack Simulation Lab'),
            ('/models', b'AI / Machine Learning Threat Intelligence'),
            ('/logs', b'SOC Security Audit')
        ]
        for url, expected_text in pages:
            res = self.client.get(url)
            self.assertEqual(res.status_code, 200)
            self.assertIn(expected_text, res.data)
            print(f" [PASS] Page {url} rendered successfully")

    def test_api_stats(self):
        """Verify /api/stats returns valid metrics, KPIs, and chart data."""
        self.login()
        res = self.client.get('/api/stats')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('kpis', data)
        self.assertIn('charts', data)
        self.assertIn('total_requests', data['kpis'])
        self.assertGreater(data['kpis']['total_requests'], 0)
        print(" [PASS] /api/stats returned dynamic KPIs and chart timelines")

    def test_api_traffic_search_and_filter(self):
        """Verify /api/traffic supports filtering by method and pagination."""
        self.login()
        res = self.client.get('/api/traffic?per_page=10&method=ALL')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('items', data)
        self.assertIn('total', data)
        self.assertGreaterEqual(len(data['items']), 1)
        print(f" [PASS] /api/traffic retrieved {len(data['items'])} paginated items")

    def test_attack_simulation(self):
        """Test running attack simulations and verifying alert creation."""
        self.login()
        # 1. Normal simulation
        res_norm = self.client.post('/api/simulate', json={'type': 'normal'})
        self.assertEqual(res_norm.status_code, 200)
        norm_data = res_norm.get_json()
        self.assertEqual(norm_data['threats_detected'], 0)

        # 2. Brute force attack simulation
        res_bf = self.client.post('/api/simulate', json={'type': 'brute_force'})
        self.assertEqual(res_bf.status_code, 200)
        bf_data = res_bf.get_json()
        self.assertGreater(bf_data['threats_detected'], 0)
        self.assertGreaterEqual(bf_data['avg_risk_score'], 70)

        # 3. Malicious SQLi payload simulation
        res_sqli = self.client.post('/api/simulate', json={'type': 'payload', 'params': {'subtype': 'sqli'}})
        self.assertEqual(res_sqli.status_code, 200)
        sqli_data = res_sqli.get_json()
        self.assertGreater(sqli_data['threats_detected'], 0)
        self.assertGreaterEqual(sqli_data['avg_risk_score'], 80)
        print(" [PASS] Attack Simulation Lab executed normal, brute force, and SQLi attacks with genuine ML alerts")

    def test_model_metrics(self):
        """Verify /api/model-metrics returns genuine ML diagnostics."""
        self.login()
        res = self.client.get('/api/model-metrics')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('metrics', data)
        self.assertIn('confusion_matrix', data)
        self.assertIn('feature_importances', data)
        self.assertGreater(data['metrics']['accuracy'], 0.90)
        print(f" [PASS] ML Model Metrics: Accuracy={data['metrics']['accuracy']*100:.1f}%, F1={data['metrics']['f1_score']*100:.1f}%")

if __name__ == '__main__':
    print("\n--- RUNNING API SENTINEL TEST SUITE ---")
    unittest.main()
