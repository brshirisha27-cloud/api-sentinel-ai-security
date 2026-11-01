"""
AI SENTINEL - Detection Engine
Implements Scikit-learn Random Forest Classifier and Isolation Forest
for real-time API threat detection and transparent risk scoring.
"""

import os
import re
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)

# Feature Names used in ML models
FEATURE_NAMES = [
    'request_frequency',       # Req/min from this IP
    'failed_login_count',      # Recent consecutive failed auth attempts
    'response_status',         # HTTP status code
    'payload_size',            # Payload size in bytes
    'response_time_ms',        # Latency in milliseconds
    'auth_status',             # 0=Valid Auth, 1=Anonymous, 2=Tampered/Invalid Token
    'payload_risk_indicator',  # Regex heuristic score (0-10) for injection patterns
    'endpoint_risk_weight'     # 1=Public, 2=Standard Data, 3=Sensitive Auth/Admin
]

CLASS_LABELS = {
    0: 'Normal',
    1: 'Suspicious',
    2: 'Potential Attack'
}

# Regex heuristics for signature/pattern pre-filtering
SQLI_PATTERNS = re.compile(r"(\b(UNION(\s+ALL)?|SELECT|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|EXEC)\b|--|;|\bOR\b\s+['\d]=['\d]|\bAND\b\s+['\d]=['\d])", re.IGNORECASE)
XSS_PATTERNS = re.compile(r"(<script.*?>|javascript:|onload=|onerror=|<img.*?onerror=|<svg.*?onload=)", re.IGNORECASE)
TRAVERSAL_PATTERNS = re.compile(r"(\.\./|\.\.\\|/etc/passwd|/windows/win\.ini)", re.IGNORECASE)
COMMAND_INJECTION_PATTERNS = re.compile(r"(;|\||&&|`|\$\(.*?\))\s*(cat|ls|whoami|sh|bash|powershell|cmd)", re.IGNORECASE)


def calculate_payload_risk(payload_str: str) -> float:
    """Calculate a 0.0 to 10.0 heuristic risk indicator based on dangerous patterns."""
    if not payload_str:
        return 0.0
    
    score = 0.0
    text = str(payload_str)
    
    if SQLI_PATTERNS.search(text):
        score += 6.5
    if XSS_PATTERNS.search(text):
        score += 5.5
    if TRAVERSAL_PATTERNS.search(text):
        score += 6.0
    if COMMAND_INJECTION_PATTERNS.search(text):
        score += 7.0
        
    # Check for excessive special characters
    special_char_count = len(re.findall(r"['\"<>{};#]", text))
    if special_char_count > 5:
        score += min(special_char_count * 0.4, 3.0)
        
    return min(round(score, 1), 10.0)


def calculate_endpoint_weight(endpoint: str) -> int:
    """Classify endpoint sensitivity weight (1: Public, 2: Standard, 3: Sensitive)."""
    ep = (endpoint or '').lower()
    if any(k in ep for k in ['/auth', '/login', '/admin', '/tokens', '/keys', '/payment', '/credentials', '/internal']):
        return 3
    elif any(k in ep for k in ['/users', '/orders', '/profile', '/settings', '/v1/data']):
        return 2
    return 1


class ThreatDetectionEngine:
    """
    Dual-Model ML Threat Detection Engine combining:
    1. Supervised Random Forest Classifier (Multi-class traffic categorizer)
    2. Unsupervised Isolation Forest (Multivariate anomaly detector)
    """

    def __init__(self):
        self.rf_model = None
        self.if_model = None
        self.is_trained = False
        self.model_metrics = {}
        self.dataset_stats = {}
        self.feature_importances = {}
        self.confusion_matrix_data = []
        
        # Initialize and train models on startup
        self.train_and_evaluate()

    def generate_synthetic_dataset(self, n_samples: int = 2500) -> pd.DataFrame:
        """
        Generates a realistic synthetic training dataset representing diverse
        API traffic patterns (Normal, Suspicious, Potential Attack).
        """
        np.random.seed(42)
        
        # Class 0: Normal Traffic (~65%)
        n_normal = int(n_samples * 0.65)
        normal_freq = np.random.exponential(scale=5.0, size=n_normal) + 1.0  # 1 to 20 req/min
        normal_failed_logins = np.zeros(n_normal, dtype=int)
        normal_status = np.random.choice([200, 201, 204, 304], size=n_normal, p=[0.85, 0.08, 0.04, 0.03])
        normal_payload_size = np.random.normal(loc=350, scale=120, size=n_normal).clip(20, 1500)
        normal_response_time = np.random.normal(loc=45, scale=18, size=n_normal).clip(10, 140)
        normal_auth = np.random.choice([0, 1], size=n_normal, p=[0.75, 0.25])
        normal_payload_risk = np.random.exponential(scale=0.1, size=n_normal).clip(0, 0.8)
        normal_endpoint_weight = np.random.choice([1, 2, 3], size=n_normal, p=[0.40, 0.45, 0.15])
        normal_labels = np.zeros(n_normal, dtype=int)

        # Class 1: Suspicious Traffic (~20%)
        n_suspicious = int(n_samples * 0.20)
        suspicious_freq = np.random.normal(loc=35, scale=12, size=n_suspicious).clip(15, 70)
        suspicious_failed_logins = np.random.choice([0, 1, 2, 3], size=n_suspicious, p=[0.45, 0.30, 0.15, 0.10])
        suspicious_status = np.random.choice([200, 400, 401, 403, 404, 429], size=n_suspicious, p=[0.30, 0.25, 0.15, 0.15, 0.10, 0.05])
        suspicious_payload_size = np.random.normal(loc=1800, scale=800, size=n_suspicious).clip(50, 6000)
        suspicious_response_time = np.random.normal(loc=220, scale=90, size=n_suspicious).clip(80, 650)
        suspicious_auth = np.random.choice([0, 1, 2], size=n_suspicious, p=[0.20, 0.50, 0.30])
        suspicious_payload_risk = np.random.uniform(1.0, 4.5, size=n_suspicious)
        suspicious_endpoint_weight = np.random.choice([1, 2, 3], size=n_suspicious, p=[0.15, 0.40, 0.45])
        suspicious_labels = np.ones(n_suspicious, dtype=int)

        # Class 2: Potential Attack (~15%)
        n_attack = n_samples - n_normal - n_suspicious
        # Sub-vectors: Brute force (30%), DoS (30%), Injection (25%), BOLA/Admin probe (15%)
        n_bf = int(n_attack * 0.30)
        n_dos = int(n_attack * 0.30)
        n_inj = int(n_attack * 0.25)
        n_bola = n_attack - n_bf - n_dos - n_inj

        # 1. Brute Force
        bf_freq = np.random.normal(loc=65, scale=15, size=n_bf).clip(30, 120)
        bf_failed = np.random.randint(4, 18, size=n_bf)
        bf_status = np.random.choice([401, 403], size=n_bf, p=[0.75, 0.25])
        bf_payload = np.random.normal(loc=240, scale=40, size=n_bf).clip(100, 400)
        bf_time = np.random.normal(loc=90, scale=25, size=n_bf).clip(30, 200)
        bf_auth = np.full(n_bf, 2)
        bf_risk = np.random.uniform(0.5, 3.0, size=n_bf)
        bf_endpoint = np.full(n_bf, 3)

        # 2. DoS / Spike
        dos_freq = np.random.normal(loc=180, scale=45, size=n_dos).clip(100, 320)
        dos_failed = np.random.choice([0, 1], size=n_dos, p=[0.8, 0.2])
        dos_status = np.random.choice([429, 500, 503, 200], size=n_dos, p=[0.55, 0.25, 0.15, 0.05])
        dos_payload = np.random.normal(loc=600, scale=200, size=n_dos).clip(200, 2500)
        dos_time = np.random.normal(loc=950, scale=350, size=n_dos).clip(400, 2800)
        dos_auth = np.random.choice([0, 1], size=n_dos, p=[0.4, 0.6])
        dos_risk = np.random.uniform(0.0, 2.5, size=n_dos)
        dos_endpoint = np.random.choice([1, 2, 3], size=n_dos, p=[0.2, 0.5, 0.3])

        # 3. Injection (SQLi/XSS/Command)
        inj_freq = np.random.normal(loc=18, scale=8, size=n_inj).clip(2, 40)
        inj_failed = np.random.choice([0, 1, 2], size=n_inj, p=[0.5, 0.3, 0.2])
        inj_status = np.random.choice([400, 500, 403, 200], size=n_inj, p=[0.45, 0.30, 0.15, 0.10])
        inj_payload = np.random.normal(loc=4200, scale=1800, size=n_inj).clip(800, 12000)
        inj_time = np.random.normal(loc=180, scale=80, size=n_inj).clip(40, 700)
        inj_auth = np.random.choice([1, 2], size=n_inj, p=[0.6, 0.4])
        inj_risk = np.random.uniform(6.5, 10.0, size=n_inj)
        inj_endpoint = np.random.choice([2, 3], size=n_inj, p=[0.4, 0.6])

        # 4. BOLA / Admin breach
        bola_freq = np.random.normal(loc=25, scale=10, size=n_bola).clip(5, 55)
        bola_failed = np.random.randint(1, 5, size=n_bola)
        bola_status = np.random.choice([403, 401], size=n_bola, p=[0.7, 0.3])
        bola_payload = np.random.normal(loc=400, scale=150, size=n_bola).clip(100, 1200)
        bola_time = np.random.normal(loc=110, scale=40, size=n_bola).clip(40, 300)
        bola_auth = np.full(n_bola, 1)  # Unauthorized
        bola_risk = np.random.uniform(2.0, 5.0, size=n_bola)
        bola_endpoint = np.full(n_bola, 3)

        # Assemble Attack arrays
        attack_freq = np.concatenate([bf_freq, dos_freq, inj_freq, bola_freq])
        attack_failed = np.concatenate([bf_failed, dos_failed, inj_failed, bola_failed])
        attack_status = np.concatenate([bf_status, dos_status, inj_status, bola_status])
        attack_payload = np.concatenate([bf_payload, dos_payload, inj_payload, bola_payload])
        attack_time = np.concatenate([bf_time, dos_time, inj_time, bola_time])
        attack_auth = np.concatenate([bf_auth, dos_auth, inj_auth, bola_auth])
        attack_risk = np.concatenate([bf_risk, dos_risk, inj_risk, bola_risk])
        attack_endpoint = np.concatenate([bf_endpoint, dos_endpoint, inj_endpoint, bola_endpoint])
        attack_labels = np.full(n_attack, 2, dtype=int)

        # Merge all into dataframe
        df = pd.DataFrame({
            'request_frequency': np.concatenate([normal_freq, suspicious_freq, attack_freq]),
            'failed_login_count': np.concatenate([normal_failed_logins, suspicious_failed_logins, attack_failed]),
            'response_status': np.concatenate([normal_status, suspicious_status, attack_status]),
            'payload_size': np.concatenate([normal_payload_size, suspicious_payload_size, attack_payload]),
            'response_time_ms': np.concatenate([normal_response_time, suspicious_response_time, attack_time]),
            'auth_status': np.concatenate([normal_auth, suspicious_auth, attack_auth]),
            'payload_risk_indicator': np.concatenate([normal_payload_risk, suspicious_payload_risk, attack_risk]),
            'endpoint_risk_weight': np.concatenate([normal_endpoint_weight, suspicious_endpoint_weight, attack_endpoint]),
            'target_label': np.concatenate([normal_labels, suspicious_labels, attack_labels])
        })

        # Add slight realistic noise/overlap between boundary cases (4% realistic variance)
        noise_idx = np.random.choice(n_samples, size=int(n_samples * 0.04), replace=False)
        for idx in noise_idx:
            if df.loc[idx, 'target_label'] == 1 and np.random.rand() > 0.5:
                df.loc[idx, 'request_frequency'] = np.random.uniform(14, 20)
                df.loc[idx, 'payload_risk_indicator'] = np.random.uniform(0.3, 0.8)
            elif df.loc[idx, 'target_label'] == 2 and np.random.rand() > 0.5:
                df.loc[idx, 'request_frequency'] = np.random.uniform(25, 38)
                df.loc[idx, 'failed_login_count'] = 2

        return df


    def train_and_evaluate(self):
        """Train Random Forest and Isolation Forest, evaluating on held-out test set."""
        df = self.generate_synthetic_dataset(n_samples=2500)
        
        X = df[FEATURE_NAMES]
        y = df['target_label']

        # 80/20 train/test split stratified by class
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.20, random_state=42, stratify=y
        )

        # 1. Random Forest Classifier
        self.rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=4,
            random_state=42,
            n_jobs=1
        )
        self.rf_model.fit(X_train, y_train)

        # 2. Isolation Forest (Anomaly Detection on normal/suspicious training subset)
        self.if_model = IsolationForest(
            n_estimators=100,
            contamination=0.15,
            random_state=42,
            n_jobs=1
        )
        self.if_model.fit(X_train)

        # Genuine Evaluation on held-out test split
        y_pred = self.rf_model.predict(X_test)
        
        acc = float(accuracy_score(y_test, y_pred))
        prec = float(precision_score(y_test, y_pred, average='weighted', zero_division=0))
        rec = float(recall_score(y_test, y_pred, average='weighted', zero_division=0))
        f1 = float(f1_score(y_test, y_pred, average='weighted', zero_division=0))
        cm = confusion_matrix(y_test, y_pred).tolist()

        # Detailed per-class metrics
        report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
        
        # Feature importances from Random Forest
        importances = self.rf_model.feature_importances_
        feature_imp_list = [
            {'feature': name.replace('_', ' ').title(), 'importance': round(float(imp), 4), 'key': name}
            for name, imp in sorted(zip(FEATURE_NAMES, importances), key=lambda x: x[1], reverse=True)
        ]

        self.model_metrics = {
            'accuracy': round(acc, 4),
            'precision': round(prec, 4),
            'recall': round(rec, 4),
            'f1_score': round(f1, 4),
            'test_sample_size': len(y_test),
            'train_sample_size': len(y_train),
            'class_metrics': {
                'Normal': {
                    'precision': round(report['0']['precision'], 4),
                    'recall': round(report['0']['recall'], 4),
                    'f1_score': round(report['0']['f1-score'], 4),
                    'support': report['0']['support']
                },
                'Suspicious': {
                    'precision': round(report['1']['precision'], 4),
                    'recall': round(report['1']['recall'], 4),
                    'f1_score': round(report['1']['f1-score'], 4),
                    'support': report['1']['support']
                },
                'Potential Attack': {
                    'precision': round(report['2']['precision'], 4),
                    'recall': round(report['2']['recall'], 4),
                    'f1_score': round(report['2']['f1-score'], 4),
                    'support': report['2']['support']
                }
            }
        }
        
        self.confusion_matrix_data = cm
        self.feature_importances = feature_imp_list
        self.dataset_stats = {
            'total_samples': len(df),
            'normal_count': int((df['target_label'] == 0).sum()),
            'suspicious_count': int((df['target_label'] == 1).sum()),
            'attack_count': int((df['target_label'] == 2).sum()),
        }
        self.is_trained = True

    def predict_request(self, req_data: dict) -> dict:
        """
        Analyze an incoming or simulated API request using the trained dual-model pipeline.
        
        Calculates:
        - Random Forest prediction and probability distribution
        - Isolation Forest anomaly score (-1 to 1 converted to 0 to 100 anomaly scale)
        - Explainable reasons behind risk score
        - Composite Risk Score (0 - 100)
        - Severity Level (Low, Medium, High, Critical)
        - Action (Allowed, Flagged, Blocked)
        - SOC Recommended Action
        """
        if not self.is_trained:
            self.train_and_evaluate()

        # Extract or default features
        freq = float(req_data.get('request_frequency', 1.0))
        failed_logins = int(req_data.get('failed_login_count', 0))
        status = int(req_data.get('response_status', 200))
        payload_size = float(req_data.get('payload_size', 128))
        resp_time = float(req_data.get('response_time_ms', 45.0))
        auth_status = int(req_data.get('auth_status', 0))
        payload_risk = float(req_data.get('payload_risk_indicator', 0.0))
        endpoint_weight = int(req_data.get('endpoint_risk_weight', 1))

        # Vector for model prediction formatted as DataFrame with feature names
        feature_df = pd.DataFrame([{
            'request_frequency': freq,
            'failed_login_count': failed_logins,
            'response_status': status,
            'payload_size': payload_size,
            'response_time_ms': resp_time,
            'auth_status': auth_status,
            'payload_risk_indicator': payload_risk,
            'endpoint_risk_weight': endpoint_weight
        }])[FEATURE_NAMES]

        # 1. Random Forest Predictions
        rf_pred_class = int(self.rf_model.predict(feature_df)[0])
        rf_probs = self.rf_model.predict_proba(feature_df)[0]
        prob_normal = float(rf_probs[0])
        prob_suspicious = float(rf_probs[1]) if len(rf_probs) > 1 else 0.0
        prob_attack = float(rf_probs[2]) if len(rf_probs) > 2 else 0.0

        # 2. Isolation Forest Anomaly Detection
        raw_anomaly = float(self.if_model.decision_function(feature_df)[0])
        # Scale to 0-100 anomaly score (higher = more anomalous)
        # Decision function is typically in range [-0.3, 0.3]
        anomaly_index = max(0.0, min(100.0, (0.25 - raw_anomaly) * 160.0))

        # 3. Explainability Reasons & Heuristics
        reasons = []
        heuristic_penalty = 0.0

        if payload_risk >= 5.0:
            reasons.append(f"Dangerous payload signatures detected (Score: {payload_risk}/10)")
            heuristic_penalty += payload_risk * 6.5
        elif payload_risk > 1.0:
            reasons.append(f"Unusual character sequence in request payload (Score: {payload_risk}/10)")
            heuristic_penalty += payload_risk * 3.0

        if failed_logins >= 4:
            reasons.append(f"High consecutive failed logins ({failed_logins} attempts) indicates credential stuffing")
            heuristic_penalty += min(failed_logins * 7.0, 35.0)
        elif failed_logins >= 1:
            reasons.append(f"Failed login event recorded ({failed_logins} attempt)")
            heuristic_penalty += 8.0

        if freq >= 90:
            reasons.append(f"Severe request rate spike ({int(freq)} req/min) exceeds typical threshold")
            heuristic_penalty += min((freq - 80) * 0.45, 25.0)
        elif freq >= 35:
            reasons.append(f"Elevated request rate ({int(freq)} req/min) above baseline")
            heuristic_penalty += 10.0

        if endpoint_weight == 3 and auth_status != 0:
            reasons.append("Unauthenticated or invalid token access attempt on high-value sensitive endpoint")
            heuristic_penalty += 20.0

        if status in [401, 403]:
            reasons.append(f"Access denied with HTTP {status}")
            heuristic_penalty += 8.0
        elif status == 429:
            reasons.append("HTTP 429 Too Many Requests: Rate limiter triggered")
            heuristic_penalty += 18.0
        elif status >= 500:
            reasons.append(f"Internal server error HTTP {status} following request processing")
            heuristic_penalty += 12.0

        if resp_time > 800:
            reasons.append(f"Abnormal backend latency ({int(resp_time)}ms)")
            heuristic_penalty += 10.0

        if not reasons:
            reasons.append("Conforms to expected normal operational API baseline")

        # 4. Composite Risk Score Calculation (0 to 100)
        # Weighted formula combining RF probability, IF anomaly score, and heuristic indicators
        rf_risk_component = (prob_suspicious * 50.0) + (prob_attack * 92.0)
        if_risk_component = anomaly_index
        
        composite_score = (
            0.45 * rf_risk_component +
            0.25 * if_risk_component +
            0.30 * min(heuristic_penalty, 100.0)
        )
        
        # Override to critical if definite dangerous injection or massive brute force
        if payload_risk >= 6.0 or failed_logins >= 6:
            composite_score = max(composite_score, 82.0)
        elif freq > 150:
            composite_score = max(composite_score, 80.0)

        risk_score = int(round(max(5.0, min(99.0, composite_score))))

        # 5. Severity Categorization
        if risk_score >= 80:
            severity = 'Critical'
            classification = 'Potential Attack'
            action = 'Blocked'
            is_blocked = True
            rec_action = "Instantly terminate session, issue IP block rule at API gateway/WAF, and notify incident response."
        elif risk_score >= 60:
            severity = 'High'
            classification = 'Potential Attack'
            action = 'Blocked' if (payload_risk >= 5.0 or freq > 100) else 'Flagged'
            is_blocked = action == 'Blocked'
            rec_action = "Enforce adaptive challenge (MFA/CAPTCHA), throttle IP to 5 req/min, and flag user token for audit."
        elif risk_score >= 30:
            severity = 'Medium'
            classification = 'Suspicious'
            action = 'Flagged'
            is_blocked = False
            rec_action = "Monitor source IP session activity, increment risk telemetry, and log request parameters."
        else:
            severity = 'Low'
            classification = 'Normal'
            action = 'Allowed'
            is_blocked = False
            rec_action = "Standard telemetry logging; no immediate mitigation required."

        return {
            'classification': classification,
            'rf_class_id': rf_pred_class,
            'probabilities': {
                'normal': round(prob_normal, 4),
                'suspicious': round(prob_suspicious, 4),
                'attack': round(prob_attack, 4)
            },
            'anomaly_score': round(anomaly_index, 2),
            'raw_anomaly': round(raw_anomaly, 4),
            'risk_score': risk_score,
            'severity': severity,
            'action': action,
            'is_blocked': is_blocked,
            'reasons': reasons,
            'recommended_action': rec_action
        }

    def get_model_diagnostics(self) -> dict:
        """Return diagnostic metrics, confusion matrix, and feature importances."""
        if not self.is_trained:
            self.train_and_evaluate()
            
        return {
            'metrics': self.model_metrics,
            'confusion_matrix': self.confusion_matrix_data,
            'feature_importances': self.feature_importances,
            'dataset_stats': self.dataset_stats,
            'class_labels': ['Normal', 'Suspicious', 'Potential Attack'],
            'model_info': {
                'rf_algorithm': 'Random Forest Classifier (100 Estimators, Gini, max_depth=10)',
                'if_algorithm': 'Isolation Forest Anomaly Detector (100 Trees, contamination=0.15)',
                'framework': 'Scikit-learn',
                'training_type': 'Synthetic SOC API Traffic Benchmark Dataset',
                'disclaimer': 'Note: Metrics reflect performance on a held-out synthetic test dataset designed for educational demonstrations.'
            }
        }


# Global engine instance
detector = ThreatDetectionEngine()
