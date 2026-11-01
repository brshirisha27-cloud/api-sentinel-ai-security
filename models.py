import json
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    """User account model with secure password hashing."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), default='Security Analyst')
    name = db.Column(db.String(120), default='SOC Operator')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }


class APIRequest(db.Model):
    """Monitored API Request model representing incoming API traffic."""
    __tablename__ = 'api_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.String(32), unique=True, nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    method = db.Column(db.String(10), nullable=False, default='GET')
    endpoint = db.Column(db.String(256), nullable=False, index=True)
    ip_address = db.Column(db.String(45), nullable=False, index=True)
    user_agent = db.Column(db.String(256), default='Mozilla/5.0')
    status_code = db.Column(db.Integer, nullable=False, default=200)
    response_time_ms = db.Column(db.Float, nullable=False, default=45.0)
    payload_size = db.Column(db.Integer, nullable=False, default=128)
    
    # AI/ML & Threat evaluation fields
    classification = db.Column(db.String(30), nullable=False, default='Normal', index=True)
    anomaly_score = db.Column(db.Float, default=0.0)
    risk_score = db.Column(db.Integer, nullable=False, default=10, index=True)
    threat_type = db.Column(db.String(80), default='None')
    is_blocked = db.Column(db.Boolean, default=False, index=True)
    reasons = db.Column(db.Text, default='Standard API request profile')
    
    # Relationship to alerts
    alerts = db.relationship('SecurityAlert', backref='api_request', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'request_id': self.request_id,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else None,
            'method': self.method,
            'endpoint': self.endpoint,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'status_code': self.status_code,
            'response_time_ms': round(self.response_time_ms, 2),
            'payload_size': self.payload_size,
            'classification': self.classification,
            'anomaly_score': round(self.anomaly_score, 2),
            'risk_score': self.risk_score,
            'threat_type': self.threat_type,
            'is_blocked': self.is_blocked,
            'reasons': self.reasons,
            'alerts_count': len(self.alerts)
        }


class SecurityAlert(db.Model):
    """Security alert generated when high-risk or anomalous traffic is detected."""
    __tablename__ = 'security_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    alert_id = db.Column(db.String(32), unique=True, nullable=False, index=True)
    request_id = db.Column(db.Integer, db.ForeignKey('api_requests.id', ondelete='SET NULL'), nullable=True)
    alert_title = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # Authentication, Volumetric, Injection, BOLA, Anomaly
    severity = db.Column(db.String(20), nullable=False, index=True)  # Low, Medium, High, Critical
    source_ip = db.Column(db.String(45), nullable=False, index=True)
    endpoint = db.Column(db.String(256), nullable=False)
    risk_score = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    description = db.Column(db.Text, nullable=False)
    recommended_action = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), default='Active', index=True)  # Active, Investigating, Mitigated, Resolved

    def to_dict(self):
        return {
            'id': self.id,
            'alert_id': self.alert_id,
            'request_id': self.request_id,
            'alert_title': self.alert_title,
            'category': self.category,
            'severity': self.severity,
            'source_ip': self.source_ip,
            'endpoint': self.endpoint,
            'risk_score': self.risk_score,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else None,
            'description': self.description,
            'recommended_action': self.recommended_action,
            'status': self.status
        }


class SimulationEvent(db.Model):
    """Record of an attack simulation experiment conducted in the lab."""
    __tablename__ = 'simulation_events'
    
    id = db.Column(db.Integer, primary_key=True)
    sim_id = db.Column(db.String(32), unique=True, nullable=False)
    simulation_type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    requests_generated = db.Column(db.Integer, nullable=False)
    threats_detected = db.Column(db.Integer, nullable=False)
    avg_risk_score = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'sim_id': self.sim_id,
            'simulation_type': self.simulation_type,
            'title': self.title,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else None,
            'requests_generated': self.requests_generated,
            'threats_detected': self.threats_detected,
            'avg_risk_score': round(self.avg_risk_score, 1),
            'description': self.description
        }


class SecurityLog(db.Model):
    """Detailed audit log of system events, detections, actions, and administrative ops."""
    __tablename__ = 'security_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    event_type = db.Column(db.String(40), nullable=False, index=True)  # AUTH, TRAFFIC, DETECTION, BLOCK, SIMULATION, SYSTEM
    source_ip = db.Column(db.String(45), default='N/A')
    endpoint = db.Column(db.String(256), default='N/A')
    risk_score = db.Column(db.Integer, default=0)
    detection_result = db.Column(db.String(100), default='Informational')
    action_taken = db.Column(db.String(100), default='Logged')  # Allowed, Flagged, Blocked, Alert Created, Mitigated
    details = db.Column(db.Text, default='')

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else None,
            'event_type': self.event_type,
            'source_ip': self.source_ip,
            'endpoint': self.endpoint,
            'risk_score': self.risk_score,
            'detection_result': self.detection_result,
            'action_taken': self.action_taken,
            'details': self.details
        }

