"""
API SENTINEL - AI-Powered API Security and Intelligent Threat Detection Platform
Main Flask Application Server
"""

import os
import functools
from datetime import datetime, timedelta, timezone
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, jsonify, abort
)
from config import Config
from models import db, User, APIRequest, SecurityAlert, SimulationEvent, SecurityLog
from detection import detector, calculate_payload_risk, calculate_endpoint_weight
from simulator import run_simulation, seed_database


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    # Context processor to make current user and system status available to all templates
    @app.context_processor
    def inject_global_template_vars():
        current_user = None
        if 'user_id' in session:
            current_user = db.session.get(User, session['user_id'])
        return {
            'current_user': current_user,
            'now': datetime.now(timezone.utc),
            'app_name': 'API SENTINEL',
            'app_tagline': 'Intelligent API Protection. Real-Time Threat Detection.'
        }

    return app


app = create_app()


# ---------------------------------------------------------
# AUTHENTICATION DECORATOR & UTILITIES
# ---------------------------------------------------------
def login_required(view):
    """Ensure user is logged in before accessing protected routes."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Unauthorized. Please log in.'}), 401
            return redirect(url_for('login', next=request.path))
        return view(**kwargs)
    return wrapped_view


# ---------------------------------------------------------
# PAGE ROUTES (HTML TEMPLATES)
# ---------------------------------------------------------
@app.route('/')
def index():
    """Root redirect: To dashboard if authenticated, else login."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page with secure credential validation."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Please enter both username and password.', 'warning')
            return render_template('login.html', demo_users=Config.DEMO_USERS)

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session.clear()
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            session.permanent = True
            
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()

            # Audit log
            log = SecurityLog(
                event_type='AUTH',
                source_ip=request.remote_addr or '127.0.0.1',
                endpoint='/login',
                risk_score=0,
                detection_result='Successful Authentication',
                action_taken='Session Granted',
                details=f"User '{user.username}' authenticated successfully."
            )
            db.session.add(log)
            db.session.commit()

            flash(f'Welcome back, {user.name}!', 'success')
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('dashboard')
            return redirect(next_page)
        else:
            # Audit log failed login
            log = SecurityLog(
                event_type='AUTH',
                source_ip=request.remote_addr or '127.0.0.1',
                endpoint='/login',
                risk_score=35,
                detection_result='Failed Login Attempt',
                action_taken='Rejected',
                details=f"Failed login attempt for username '{username}'."
            )
            db.session.add(log)
            db.session.commit()

            flash('Invalid username or password. Check demo credentials below.', 'danger')

    return render_template('login.html', demo_users=Config.DEMO_USERS)


@app.route('/logout')
def logout():
    """Terminate current user session."""
    username = session.get('username', 'Unknown')
    session.clear()
    flash(f'You have been logged out securely.', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    """SOC Executive & Operational Dashboard."""
    return render_template('dashboard.html')


@app.route('/traffic')
@login_required
def traffic():
    """API Traffic Monitoring and Packet Analysis."""
    return render_template('traffic.html')


@app.route('/alerts')
@login_required
def alerts():
    """Threat Detection and Security Alerts Management."""
    return render_template('alerts.html')


@app.route('/simulation')
@login_required
def simulation():
    """Interactive Attack Simulation Lab."""
    return render_template('simulation.html')


@app.route('/models')
@login_required
def models():
    """AI/ML Model Intelligence and Performance Evaluation."""
    return render_template('models.html')


@app.route('/logs')
@login_required
def logs():
    """Security Audit and Activity Event Logs."""
    return render_template('logs.html')


# ---------------------------------------------------------
# REST API ENDPOINTS (JSON BACKEND)
# ---------------------------------------------------------
@app.route('/api/stats', methods=['GET'])
@login_required
def get_stats():
    """
    Returns live database-backed SOC statistics, KPI metrics,
    traffic timeline data, and threat category distribution.
    """
    total_requests = APIRequest.query.count()
    safe_requests = APIRequest.query.filter_by(classification='Normal').count()
    suspicious_requests = APIRequest.query.filter_by(classification='Suspicious').count()
    blocked_requests = APIRequest.query.filter(
        (APIRequest.is_blocked == True) | (APIRequest.classification == 'Potential Attack')
    ).count()

    active_alerts = SecurityAlert.query.filter(SecurityAlert.status.in_(['Active', 'Investigating'])).count()
    critical_alerts = SecurityAlert.query.filter_by(severity='Critical', status='Active').count()
    high_alerts = SecurityAlert.query.filter_by(severity='High', status='Active').count()

    # Determine overall system threat level
    if critical_alerts > 0:
        threat_level = 'CRITICAL'
        threat_color = '#ef4444'
        threat_badge = 'danger'
    elif high_alerts > 0 or suspicious_requests > (total_requests * 0.25):
        threat_level = 'ELEVATED'
        threat_color = '#f59e0b'
        threat_badge = 'warning'
    elif suspicious_requests > 0:
        threat_level = 'GUARDED'
        threat_color = '#3b82f6'
        threat_badge = 'info'
    else:
        threat_level = 'LOW / NORMAL'
        threat_color = '#10b981'
        threat_badge = 'success'

    # Average latency
    avg_latency = db.session.query(db.func.avg(APIRequest.response_time_ms)).scalar() or 42.5

    # Traffic timeline for line chart (latest 15 requests in chronological sequence)
    timeline_requests = APIRequest.query.order_by(APIRequest.timestamp.desc()).limit(15).all()
    timeline_requests.reverse()

    chart_labels = []
    chart_risk_scores = []
    chart_latencies = []
    for r in timeline_requests:
        chart_labels.append(r.timestamp.strftime('%H:%M:%S') if r.timestamp else 'N/A')
        chart_risk_scores.append(r.risk_score)
        chart_latencies.append(round(r.response_time_ms, 1))

    # Threat category distribution for doughnut chart
    category_counts = db.session.query(
        SecurityAlert.category, db.func.count(SecurityAlert.id)
    ).group_by(SecurityAlert.category).all()

    threat_distribution = {cat: count for cat, count in category_counts}
    if not threat_distribution:
        threat_distribution = {
            'Authentication': 2,
            'Volumetric': 1,
            'Access Control': 1,
            'Injection': 1
        }

    # Recent 6 alerts
    recent_alerts = SecurityAlert.query.order_by(SecurityAlert.timestamp.desc()).limit(6).all()

    # Recent 8 requests
    recent_requests = APIRequest.query.order_by(APIRequest.timestamp.desc()).limit(8).all()

    return jsonify({
        'kpis': {
            'total_requests': total_requests,
            'safe_requests': safe_requests,
            'suspicious_requests': suspicious_requests,
            'blocked_requests': blocked_requests,
            'active_alerts': active_alerts,
            'critical_alerts': critical_alerts,
            'avg_latency_ms': round(avg_latency, 1),
            'threat_level': threat_level,
            'threat_color': threat_color,
            'threat_badge': threat_badge
        },
        'charts': {
            'timeline': {
                'labels': chart_labels,
                'risk_scores': chart_risk_scores,
                'latencies': chart_latencies
            },
            'categories': {
                'labels': list(threat_distribution.keys()),
                'counts': list(threat_distribution.values())
            }
        },
        'recent_alerts': [a.to_dict() for a in recent_alerts],
        'recent_requests': [r.to_dict() for r in recent_requests]
    })


@app.route('/api/traffic', methods=['GET', 'POST'])
@login_required
def handle_traffic():
    """
    GET: Search, filter, sort and paginate monitored API traffic.
    POST: Ingest and analyze a custom API request via ML detection engine.
    """
    if request.method == 'POST':
        data = request.get_json() or {}
        method = (data.get('method') or 'GET').upper()
        endpoint = (data.get('endpoint') or '/api/v1/test').strip()
        ip = (data.get('ip_address') or request.remote_addr or '127.0.0.1').strip()
        payload = data.get('payload', '')
        
        # Calculate feature variables
        p_risk = calculate_payload_risk(payload)
        ep_weight = calculate_endpoint_weight(endpoint)
        freq = float(data.get('request_frequency', 5.0))
        failed_logins = int(data.get('failed_login_count', 0))
        resp_status = int(data.get('status_code', 200))
        payload_size = len(str(payload).encode('utf-8')) if payload else int(data.get('payload_size', 120))
        resp_time = float(data.get('response_time_ms', 45.0))
        auth_status = int(data.get('auth_status', 0))

        req_feature_dict = {
            'request_frequency': freq,
            'failed_login_count': failed_logins,
            'response_status': resp_status,
            'payload_size': payload_size,
            'response_time_ms': resp_time,
            'auth_status': auth_status,
            'payload_risk_indicator': p_risk,
            'endpoint_risk_weight': ep_weight
        }

        # Predict with ML Engine
        eval_result = detector.predict_request(req_feature_dict)

        now = datetime.now(timezone.utc)
        req_obj = APIRequest(
            request_id=f"REQ-{uuid.uuid4().hex[:8].upper()}",
            timestamp=now,
            method=method,
            endpoint=endpoint,
            ip_address=ip,
            user_agent=data.get('user_agent', 'API-Client/2.0'),
            status_code=resp_status,
            response_time_ms=resp_time,
            payload_size=payload_size,
            classification=eval_result['classification'],
            anomaly_score=eval_result['anomaly_score'],
            risk_score=eval_result['risk_score'],
            threat_type=eval_result['action'] if eval_result['risk_score'] > 30 else 'None',
            is_blocked=eval_result['is_blocked'],
            reasons='; '.join(eval_result['reasons'])
        )
        db.session.add(req_obj)

        if eval_result['risk_score'] >= 60:
            alert = SecurityAlert(
                alert_id=f"ALT-{uuid.uuid4().hex[:6].upper()}",
                request_id=req_obj.id,
                alert_title=f"Custom Threat Detected: {eval_result['classification']}",
                category="Injection" if p_risk > 3 else "Anomaly",
                severity=eval_result['severity'],
                source_ip=ip,
                endpoint=endpoint,
                risk_score=eval_result['risk_score'],
                timestamp=now,
                description=f"Inbound request triggered security heuristics: {'; '.join(eval_result['reasons'])}",
                recommended_action=eval_result['recommended_action'],
                status="Active"
            )
            db.session.add(alert)

        db.session.commit()

        return jsonify({
            'status': 'success',
            'request': req_obj.to_dict(),
            'evaluation': eval_result
        }), 201

    # GET Request: Filter & Search
    query = APIRequest.query

    # Search query
    search = request.args.get('search', '').strip()
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (APIRequest.request_id.ilike(search_filter)) |
            (APIRequest.endpoint.ilike(search_filter)) |
            (APIRequest.ip_address.ilike(search_filter)) |
            (APIRequest.threat_type.ilike(search_filter))
        )

    # HTTP Method filter
    method_filter = request.args.get('method', '').strip().upper()
    if method_filter and method_filter != 'ALL':
        query = query.filter_by(method=method_filter)

    # Classification filter
    class_filter = request.args.get('classification', '').strip()
    if class_filter and class_filter != 'ALL':
        query = query.filter_by(classification=class_filter)

    # Status Code filter
    status_filter = request.args.get('status_code', '').strip()
    if status_filter and status_filter != 'ALL':
        try:
            query = query.filter_by(status_code=int(status_filter))
        except ValueError:
            pass

    # Sort
    sort_by = request.args.get('sort_by', 'timestamp')
    sort_dir = request.args.get('sort_dir', 'desc')
    
    sort_column = getattr(APIRequest, sort_by, APIRequest.timestamp)
    if sort_dir == 'asc':
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 15, type=int)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'items': [r.to_dict() for r in pagination.items],
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages,
        'has_prev': pagination.has_prev,
        'has_next': pagination.has_next
    })


@app.route('/api/traffic/<int:req_id>', methods=['GET'])
@login_required
def get_traffic_detail(req_id):
    """Retrieve detailed metadata and AI explainability for an API request."""
    req_obj = db.session.get(APIRequest, req_id)
    if not req_obj:
        return jsonify({'error': 'Request not found'}), 404
        
    return jsonify({
        'request': req_obj.to_dict(),
        'alerts': [a.to_dict() for a in req_obj.alerts]
    })


@app.route('/api/alerts', methods=['GET'])
@login_required
def get_alerts():
    """Returns security alerts filtered by severity and status."""
    query = SecurityAlert.query

    severity = request.args.get('severity', '').strip()
    if severity and severity != 'ALL':
        query = query.filter_by(severity=severity.capitalize())

    status = request.args.get('status', '').strip()
    if status and status != 'ALL':
        query = query.filter_by(status=status.capitalize())

    search = request.args.get('search', '').strip()
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (SecurityAlert.alert_title.ilike(search_filter)) |
            (SecurityAlert.source_ip.ilike(search_filter)) |
            (SecurityAlert.endpoint.ilike(search_filter)) |
            (SecurityAlert.category.ilike(search_filter))
        )

    alerts_list = query.order_by(SecurityAlert.timestamp.desc()).all()
    return jsonify([a.to_dict() for a in alerts_list])


@app.route('/api/alerts/<int:alert_id>/status', methods=['POST'])
@login_required
def update_alert_status(alert_id):
    """Update status of a security alert (Active, Investigating, Mitigated, Resolved)."""
    alert = db.session.get(SecurityAlert, alert_id)
    if not alert:
        return jsonify({'error': 'Alert not found'}), 404

    data = request.get_json() or {}
    new_status = data.get('status', 'Resolved').capitalize()
    
    if new_status not in ['Active', 'Investigating', 'Mitigated', 'Resolved']:
        return jsonify({'error': 'Invalid status'}), 400

    old_status = alert.status
    alert.status = new_status

    log = SecurityLog(
        event_type='DETECTION',
        source_ip=alert.source_ip,
        endpoint=alert.endpoint,
        risk_score=alert.risk_score,
        detection_result=f"Alert Status Updated: {new_status}",
        action_taken=f"Status changed from {old_status} to {new_status}",
        details=f"User '{session.get('username')}' updated alert {alert.alert_id}."
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({
        'status': 'success',
        'alert': alert.to_dict(),
        'message': f"Alert {alert.alert_id} marked as {new_status}."
    })


@app.route('/api/simulate', methods=['POST'])
@login_required
def simulate():
    """
    Triggers an educational attack simulation:
    - Normal API Request
    - Brute Force Attack
    - Traffic Spike / DoS Simulation
    - Unauthorized Access Attempt
    - Suspicious Payload Simulation (SQLi/XSS)
    """
    data = request.get_json() or {}
    sim_type = data.get('type', 'normal')
    custom_params = data.get('params', {})

    result = run_simulation(sim_type, custom_params)
    return jsonify(result)


@app.route('/api/model-metrics', methods=['GET'])
@login_required
def get_model_metrics():
    """Returns actual evaluation metrics, confusion matrix and feature importances."""
    diagnostics = detector.get_model_diagnostics()
    return jsonify(diagnostics)


@app.route('/api/logs', methods=['GET'])
@login_required
def get_logs():
    """Returns searchable security audit logs."""
    query = SecurityLog.query

    event_type = request.args.get('event_type', '').strip().upper()
    if event_type and event_type != 'ALL':
        query = query.filter_by(event_type=event_type)

    search = request.args.get('search', '').strip()
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (SecurityLog.source_ip.ilike(search_filter)) |
            (SecurityLog.endpoint.ilike(search_filter)) |
            (SecurityLog.detection_result.ilike(search_filter)) |
            (SecurityLog.details.ilike(search_filter))
        )

    logs_list = query.order_by(SecurityLog.timestamp.desc()).limit(100).all()
    return jsonify([l.to_dict() for l in logs_list])


@app.route('/api/health', methods=['GET'])
def get_health():
    """Returns real-time health indicator of detection engine and database."""
    db_connected = True
    try:
        db.session.execute(db.text('SELECT 1'))
    except Exception:
        db_connected = False

    return jsonify({
        'status': 'HEALTHY' if db_connected and detector.is_trained else 'DEGRADED',
        'database': 'ONLINE' if db_connected else 'OFFLINE',
        'ml_engine': {
            'random_forest': 'ONLINE' if detector.rf_model else 'OFFLINE',
            'isolation_forest': 'ONLINE' if detector.if_model else 'OFFLINE',
            'is_trained': detector.is_trained
        },
        'system_time': datetime.now(timezone.utc).isoformat(),
        'version': '2.4.0-Enterprise-SOC'
    })


@app.route('/api/reset-data', methods=['POST'])
@login_required
def reset_data():
    """Resets and re-seeds sample demonstration data."""
    APIRequest.query.delete()
    SecurityAlert.query.delete()
    SimulationEvent.query.delete()
    SecurityLog.query.delete()
    db.session.commit()

    seed_database(app)
    return jsonify({'status': 'success', 'message': 'Database re-seeded successfully with baseline data.'})


# ---------------------------------------------------------
# APPLICATION ENTRYPOINT
# ---------------------------------------------------------
if __name__ == '__main__':
    # Initialize DB & Seed Demo Data on first boot
    seed_database(app)

    port = int(os.getenv('PORT', 5000))
    print(f"\n=======================================================")
    print(f"  API SENTINEL - AI-Powered API Security Platform")
    print(f"  SOC Dashboard Running at: http://127.0.0.1:{port}")
    print(f"  Demo Credentials: admin / Sentinel@2025")
    print(f"=======================================================\n")
    app.run(host='127.0.0.1', port=port, debug=True)

