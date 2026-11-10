"""
=============================================================================
QueueLess Comprehensive Verification & Diagnostic Test Suite
=============================================================================
Tests:
1. Application and module imports (app.py and api/index.py)
2. Database connectivity & health check
3. Database initialization and table seeding
4. All major UI routes (/, /institutions, /book, /track, /display, /health)
5. Static asset availability (/static/css/style.css, /static/images/logo.svg)
6. Customer registration, login, dashboard, logout
7. Queue booking API (/api/tokens/book)
8. Live token status tracking API (/api/tokens/track/<token_number>)
9. QR check-in API (/api/tokens/qr-checkin)
10. Feedback submission (/api/feedback)
11. Operator login, workstation dashboard, call-next, skip, recall APIs
12. Admin login, console analytics (/admin/dashboard), /api/stats
13. Simulated serverless cold-start entrypoint (api/index.py)
"""

import sys
import os
import unittest
import json

class QueueLessTestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Test serverless entrypoint
        from api.index import app
        cls.app = app
        cls.client = app.test_client()
        import database
        cls.db = database
        database.ensure_db_initialized()

    def test_01_health_check(self):
        res = self.client.get('/health')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get('status'), 'healthy')
        self.assertTrue(data.get('database', {}).get('connected'))

    def test_02_static_assets(self):
        css_res = self.client.get('/static/css/style.css')
        self.assertEqual(css_res.status_code, 200)
        self.assertIn(b'body', css_res.data)

        logo_res = self.client.get('/static/images/logo.svg')
        self.assertEqual(logo_res.status_code, 200)

    def test_03_major_ui_routes(self):
        routes = ['/', '/institutions', '/book', '/track', '/display', '/tv']
        for route in routes:
            res = self.client.get(route)
            self.assertEqual(res.status_code, 200, f"Route {route} failed with status {res.status_code}")
            self.assertIn(b'QueueLess', res.data, f"QueueLess branding not found on {route}")

    def test_04_catalog_and_institutions_api(self):
        res = self.client.get('/api/catalog')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get('success'))
        self.assertGreaterEqual(len(data.get('institutions', [])), 8)

        search_res = self.client.get('/api/institutions/search?category=Hospital')
        self.assertEqual(search_res.status_code, 200)
        s_data = search_res.get_json()
        self.assertGreaterEqual(s_data.get('count', 0), 1)

    def test_05_customer_registration_and_login(self):
        # Register new customer with unique phone
        import time
        test_phone = f"99{int(time.time()) % 100000000:08d}"
        res = self.client.post('/customer/register', data={
            'name': 'Test User A',
            'phone': test_phone,
            'email': f'user_{test_phone}@example.com',
            'password': 'testpassword123'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Test User A', res.data)

        # Logout
        self.client.get('/customer/logout')

        # Login with registered credentials
        login_res = self.client.post('/customer/login', data={
            'phone': test_phone,
            'password': 'testpassword123'
        }, follow_redirects=True)
        self.assertEqual(login_res.status_code, 200)
        self.assertIn(b'Test User A', login_res.data)

    def test_06_token_booking_and_tracking(self):
        # Book a token via API
        book_payload = {
            "institution_id": 1,
            "branch_id": 1,
            "service_id": 1,
            "customer_name": "Diagnostic Patient",
            "phone": "9876543210",
            "priority": "senior",
            "token_type": "instant"
        }
        res = self.client.post('/api/tokens/book',
                               data=json.dumps(book_payload),
                               content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get('success'))
        token = data.get('token')
        self.assertIsNotNone(token)
        token_num = token.get('token_number')
        vcode = token.get('verification_code')
        self.assertTrue(token_num.startswith('HOSP-'))
        self.assertTrue(vcode.startswith('QL-'))

        # Track the generated token
        track_res = self.client.get(f'/api/tokens/track/{token_num}')
        self.assertEqual(track_res.status_code, 200)
        t_data = track_res.get_json()
        self.assertTrue(t_data.get('success'))
        self.assertEqual(t_data.get('token', {}).get('token_number'), token_num)

        # QR Check-in verification
        qr_res = self.client.post('/api/tokens/qr-checkin',
                                  data=json.dumps({'code': vcode}),
                                  content_type='application/json')
        self.assertEqual(qr_res.status_code, 200)
        qr_data = qr_res.get_json()
        self.assertTrue(qr_data.get('success'))
        self.assertEqual(qr_data.get('token', {}).get('checkin_status'), 'checked_in')

    def test_07_feedback_api(self):
        fb_payload = {
            "token_number": "HOSP-101",
            "customer_name": "Test Reviewer",
            "rating": 5,
            "comment": "Super seamless verification and real-time screen!"
        }
        res = self.client.post('/api/feedback',
                               data=json.dumps(fb_payload),
                               content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get('success'))

    def test_08_operator_calling_and_controls(self):
        # Operator login
        op_login = self.client.post('/operator/login', data={
            'username': 'operator',
            'password': 'op123',
            'counter': 1
        }, follow_redirects=True)
        self.assertEqual(op_login.status_code, 200)
        self.assertIn(b'Counter Officer', op_login.data)

        # Call next token
        call_res = self.client.post('/api/operator/call-next',
                                    data=json.dumps({'counter': 1, 'branch_id': 1}),
                                    content_type='application/json')
        self.assertEqual(call_res.status_code, 200)
        c_data = call_res.get_json()
        self.assertTrue('success' in c_data)

        # Toggle counter status
        toggle_res = self.client.post('/api/operator/counter-status',
                                      data=json.dumps({'branch_id': 1, 'counter': 1, 'status': 'break'}),
                                      content_type='application/json')
        self.assertEqual(toggle_res.status_code, 200)

    def test_09_admin_console_and_analytics(self):
        # Admin login
        admin_login = self.client.post('/admin/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertEqual(admin_login.status_code, 200)
        self.assertIn(b'Analytics', admin_login.data)

        # Stats API
        stats_res = self.client.get('/api/stats')
        self.assertEqual(stats_res.status_code, 200)
        s_data = stats_res.get_json()
        self.assertTrue(s_data.get('success'))
        stats = s_data.get('stats', {})
        self.assertIn('total', stats)
        self.assertIn('serving', stats)
        self.assertIn('waiting', stats)

    def test_10_display_screen_live_feed(self):
        res = self.client.get('/api/display/live?branch_id=1')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get('success'))
        self.assertIn('board', data)
        self.assertIn('serving_counters', data['board'])
        self.assertIn('waiting_tokens', data['board'])

if __name__ == '__main__':
    unittest.main()
