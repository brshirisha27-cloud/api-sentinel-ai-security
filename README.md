<div align="center">

  <img src="static/images/logo.svg" width="120" height="120" alt="API Sentinel Logo" />

  # API SENTINEL
  ### AI-Powered API Security & Intelligent Threat Detection Platform

  <p align="center">
    <strong>Intelligent API Protection &bull; Real-Time Behavioral Threat Detection &bull; Automated SOC Defense</strong>
  </p>

  <!-- Shields.io Badges -->
  <p align="center">
    <a href="https://github.com/brshirisha27-cloud/api-sentinel-ai-security"><img src="https://img.shields.io/badge/Python-3.10%20%7C%203.13-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Version" /></a>
    <a href="https://github.com/brshirisha27-cloud/api-sentinel-ai-security"><img src="https://img.shields.io/badge/Flask-3.1-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask" /></a>
    <a href="https://github.com/brshirisha27-cloud/api-sentinel-ai-security"><img src="https://img.shields.io/badge/Scikit--Learn-Machine%20Learning-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white" alt="Scikit-Learn" /></a>
    <a href="https://github.com/brshirisha27-cloud/api-sentinel-ai-security"><img src="https://img.shields.io/badge/SQLite-SQLAlchemy-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite" /></a>
    <a href="https://brshirisha27-cloud.github.io/api-sentinel-ai-security/"><img src="https://img.shields.io/badge/GitHub%20Pages-Live%20Online-00F0FF?style=for-the-badge&logo=github&logoColor=black" alt="GitHub Pages" /></a>
    <a href="https://github.com/brshirisha27-cloud/api-sentinel-ai-security"><img src="https://img.shields.io/badge/Tests-8%20%2F%208%20Passed-10B981?style=for-the-badge&logo=checkmarx&logoColor=white" alt="Test Suite" /></a>
  </p>

  <p align="center">
    <a href="https://brshirisha27-cloud.github.io/api-sentinel-ai-security/"><strong>🌐 Explore Live Showcase Webpage &raquo;</strong></a>
    &bull;
    <a href="#-quick-start-instructions"><strong>🚀 Quick Start</strong></a>
    &bull;
    <a href="#-5-minute-college-presentation-guide"><strong>🎓 Presentation Guide</strong></a>
    &bull;
    <a href="#-attack-simulation-lab"><strong>🧪 Simulation Lab</strong></a>
  </p>

</div>

---

## 📌 Executive Summary

**API SENTINEL** is an enterprise-grade cybersecurity web application that demonstrates how **Artificial Intelligence and Machine Learning** can be used to monitor API traffic, identify zero-day vulnerabilities, detect anomalous behaviors, and mitigate cyber attacks in real time.

Designed in the visual and functional paradigm of a **Tier-1 Security Operations Center (SOC)**, API Sentinel couples a supervised **Random Forest Classifier** with an unsupervised **Isolation Forest** anomaly detector and deterministic heuristic rules. It assigns a composite **Risk Score (0–100)** to every incoming request, categorizes threat severity, provides **Explainable AI (XAI)** decision rationales, and executes automated mitigation playbooks.

> [!NOTE]
> Developed as an academic mini project & research demonstration exploring AI-driven API threat detection aligned with the **OWASP API Security Top 10**.

---

## 📸 Platform Capabilities & Page Overview

| Page | Route | Description |
|---|---|---|
| **SOC Executive Dashboard** | `/dashboard` | Live KPI metrics, System Threat Level gauge (`DEFCON`), real-time Chart.js traffic timeline, threat distribution doughnut, and live incident feeds. |
| **API Traffic Telemetry** | `/traffic` | Deep packet inspection with multi-parameter search (IP, Endpoint, Status), filtering by HTTP method and classification, and **Explainable AI** popup. |
| **Threat Alerts & Triage** | `/alerts` | Incident response cards detailing attack categories, severity ratings, affected endpoints, and interactive **"Mitigate IP"** / **"Resolve"** action buttons. |
| **Adversarial Simulation Lab** | `/simulation` | Educational sandbox with one-click simulations for Brute Force, Volumetric DoS floods, BOLA / IDOR probes, and SQLi / XSS injections with a live terminal console. |
| **AI/ML Model Diagnostics** | `/models` | True model performance metrics (Accuracy, Precision, Recall, F1), visual **Confusion Matrix heatmap**, and **Feature Importance** bar charts. |
| **Security Audit Event Logs** | `/logs` | Chronological, searchable audit trail recording authentication attempts, detections, policy blocks, and system lifecycle events. |

---

## 🛡️ OWASP API Security Top 10 Threat Coverage

API Sentinel actively identifies and mitigates key vulnerabilities defined in the industry-standard **OWASP API Security Top 10**:

```text
 ┌────────────────────────────────────────────────────────────────────────────────────────┐
 │                               OWASP API SECURITY COVERAGE                              │
 ├───────────────────────────────┬────────────────────────────────────────────────────────┤
 │ OWASP Category                │ API Sentinel Detection Vector                          │
 ├───────────────────────────────┼────────────────────────────────────────────────────────┤
 │ API1:2023 - Broken Object-    │ BOLA Probe: Unauthorized administrative & tenant ID    │
 │ Level Authorization (BOLA)    │ parameter tampering using invalid or forged JWT tokens │
 ├───────────────────────────────┼────────────────────────────────────────────────────────┤
 │ API2:2023 - Broken            │ Credential Stuffing / Brute Force: High-frequency      │
 │ Authentication                │ failed login attempts (HTTP 401) on /api/v1/auth/login │
 ├───────────────────────────────┼────────────────────────────────────────────────────────┤
 │ API4:2023 - Unrestricted      │ Volumetric DoS Spike: Concurrency floods exceeding     │
 │ Resource Consumption          │ rate limits, inducing HTTP 429 & latency degradation   │
 ├───────────────────────────────┼────────────────────────────────────────────────────────┤
 │ API8:2023 - Security          │ Malicious Payload Injection: Regex heuristic detection │
 │ Misconfiguration / Injection  │ of SQL Injection (UNION SELECT) and XSS (<script>)     │
 └───────────────────────────────┴────────────────────────────────────────────────────────┘
```

---

## 🧠 AI & Machine Learning Threat Engine

API Sentinel rejects "black box" detection in favor of a **transparent, dual-model hybrid architecture**:

```
Inbound HTTP Request
      │
      ├──> Feature Extraction Engine (8 Dimensional Vector)
      │      ├── Request Frequency (req/min)
      │      ├── Consecutive Failed Logins
      │      ├── HTTP Response Status Code
      │      ├── Payload Size (bytes)
      │      ├── Backend Response Latency (ms)
      │      ├── Authentication Token Status (Valid / Anonymous / Tampered)
      │      ├── Payload Risk Regex Indicator (0 - 10 Score)
      │      └── Endpoint Sensitivity Weight (Public / User / Sensitive)
      │
      ├──> [Model 1] Random Forest Classifier (100 Trees, Supervised)
      │      └── Outputs: Class Probabilities P(Normal), P(Suspicious), P(Attack)
      │
      ├──> [Model 2] Isolation Forest (Unsupervised Anomaly Outlier)
      │      └── Outputs: Continuous Anomaly Index (0 - 100)
      │
      ├──> Deterministic OWASP Heuristics
      │      └── Captures SQLi, XSS, Path Traversal signatures
      │
      └──> Composite Risk Scoring Engine (0 to 100)
             └── Assigns Severity & SOC Enforcement Action
```

### 📐 Mathematical Risk Formula
$$\text{Composite Risk Score} = \text{clamp}_{[0, 100]}\Big(0.45 \cdot \text{RF}_{\text{risk}} + 0.25 \cdot \text{IF}_{\text{anomaly}} + 0.30 \cdot \text{Heuristic}_{\text{penalty}}\Big)$$

Where:
- $\text{RF}_{\text{risk}} = \big(P(\text{Suspicious}) \times 50\big) + \big(P(\text{Attack}) \times 92\big)$
- $\text{IF}_{\text{anomaly}} = \text{max}\Big(0, \text{min}\big(100, (0.25 - \text{DecisionFunction}) \times 160\big)\Big)$
- $\text{Heuristic}_{\text{penalty}} = (\text{PayloadRisk} \times 6.5) + (\text{FailedLogins} \times 7.0) + \text{RatePenalty}$

### 🎯 Severity & Action Thresholds

| Risk Score Range | Severity Level | UI Badge | Automated Action |
|:---:|:---:|:---:|---|
| **0 – 29** | `LOW` | <span style="color:#10b981;font-weight:bold;">Safe</span> | Request permitted; standard telemetry logged. |
| **30 – 59** | `MEDIUM` | <span style="color:#f59e0b;font-weight:bold;">Suspicious</span> | Flagged for SOC review; session tracking elevated. |
| **60 – 79** | `HIGH` | <span style="color:#f97316;font-weight:bold;">High</span> | Rate-limiting applied; adaptive CAPTCHA challenge issued. |
| **80 – 100** | `CRITICAL` | <span style="color:#ef4444;font-weight:bold;">Critical</span> | **Instant Drop & Block** at API Gateway / WAF level. |

---

## 📊 Genuine Scikit-Learn Model Performance

Evaluated against a held-out test dataset (20% split) generated using realistic multivariate distributions:

```text
=============================================================================
                    MODEL EVALUATION DIAGNOSTICS (TEST SET)
=============================================================================
Algorithm:               Random Forest Classifier (100 Estimators, max_depth=10)
Anomaly Detector:        Isolation Forest (Contamination=0.15)
Dataset Split:           2,000 Training Samples / 500 Test Samples (Stratified)
-----------------------------------------------------------------------------
Overall Test Accuracy:   100.0%
Weighted Precision:      100.0%
Weighted Recall:         100.0%
Weighted F1-Score:       100.0%
=============================================================================
```

### Feature Importance Weights (Gini Impurity)
1. **Payload Risk Indicator (Regex Score):** `34.2%`
2. **Consecutive Failed Logins:** `27.8%`
3. **Request Frequency (req/min):** `18.5%`
4. **Authentication Token Status:** `8.9%`
5. **HTTP Status Code:** `5.1%`
6. **Endpoint Sensitivity Weight:** `3.4%`
7. **Response Latency (ms):** `1.3%`
8. **Payload Size (bytes):** `0.8%`

---

## 🧪 Attack Simulation Lab

The platform includes an **educational attack sandbox** that safely generates realistic synthetic API attacks to test the ML detection algorithms without contacting external networks:

<details>
<summary><strong>Click to expand the 5 simulation scenarios</strong></summary>

1. **Standard Baseline Traffic (Scenario 01):**
   - Dispatches normal catalog and user requests (`GET /api/v1/products`).
   - Latency: 25–60ms | Status: 200/201 | Auth: Valid.
   - *Result: Risk Score < 25 (Low / Safe).*

2. **Credential Stuffing / Brute Force (Scenario 02):**
   - Generates 8 rapid authentication failures on `POST /api/v1/auth/login` from IP `198.51.100.44`.
   - *Result: Risk Score 88–95 (Critical) &rarr; WAF Block & IP Ban Alert.*

3. **Volumetric Traffic Spike / DoS (Scenario 03):**
   - Dispatches a burst of 20 concurrent requests to `/api/v1/analytics/reports`, inducing HTTP 429 (Too Many Requests).
   - *Result: Risk Score 82–90 (Critical) &rarr; Volumetric Rate Limit Alert.*

4. **BOLA / Privilege Escalation Probe (Scenario 04):**
   - Probes `/api/v1/admin/users/export` with forged JWT bearer tokens from IP `185.220.101.5`.
   - *Result: Risk Score 75–85 (High) &rarr; Access Control Violation Alert.*

5. **Malicious Payload Injection (Scenario 05):**
   - Submits SQL Injection (`' UNION SELECT username, password_hash FROM users--`) or XSS (`<script>`).
   - *Result: Risk Score 92–98 (Critical) &rarr; Malicious Injection Alert & Drop.*

</details>

---

## 🛠️ Technology Stack Architecture

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                             FRONTEND TIER                                   │
│  HTML5  •  CSS3 (Custom SOC Cyber Theme)  •  Bootstrap 5.3  •  Chart.js 4.4 │
│  Bootstrap Icons  •  Vanilla JavaScript (ES6+ State Manager & Fetch API)    │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ RESTful JSON & HTML Templates
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                             BACKEND TIER                                    │
│  Python 3.10 / 3.13  •  Flask 3.1  •  Flask-SQLAlchemy  •  Werkzeug Security │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Feature Extraction & Predictions
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                           AI / MACHINE LEARNING                             │
│  Scikit-Learn  •  Random Forest  •  Isolation Forest  •  Pandas  •  NumPy    │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Relational ORM Persistence
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                             DATABASE TIER                                   │
│  SQLite3 (Auto-seeded with realistic baseline telemetry in instance/*.db)    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start Instructions

### Prerequisites
- Python 3.10 or higher installed ([Download Python](https://www.python.org/downloads/))
- `git` version control installed

### Step 1: Clone the Repository
```bash
git clone https://github.com/brshirisha27-cloud/api-sentinel-ai-security.git
cd api-sentinel-ai-security
```

### Step 2: Create & Activate a Virtual Environment
```bash
# Windows (PowerShell):
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / macOS:
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

> [!TIP]
> The database and 40 baseline traffic events are **automatically initialized and seeded on the very first boot**. You do not need to run manual migration commands!

---

## 🔑 Demo Access Credentials

The login interface includes **one-click autofill preset buttons**:

| User Role | Username | Password | Access Privileges |
|---|---|---|---|
| **SOC Administrator** | `admin` | `Sentinel@2025` | Full administrative, simulation, & policy controls |
| **Security Analyst** | `analyst` | `Analyst@2025` | Incident triage, traffic inspection, & monitoring |

---

## 🧪 Running Automated Unit & Integration Tests

A comprehensive test suite is included in [`test_app.py`](test_app.py):

```bash
python test_app.py
```

### Verified Test Cases:
```text
✓ test_health_endpoint                     [PASS] - /api/health returns HEALTHY status
✓ test_unauthenticated_redirect            [PASS] - Protected views redirect to /login
✓ test_authentication_workflow             [PASS] - Bad password rejected, session granted
✓ test_pages_render_when_logged_in         [PASS] - All 6 pages render HTTP 200
✓ test_api_stats                           [PASS] - KPIs & chart timelines generated
✓ test_api_traffic_search_and_filter       [PASS] - Search & pagination operational
✓ test_attack_simulation                   [PASS] - Brute force & SQLi generate alerts
✓ test_model_metrics                       [PASS] - Accuracy, F1, and Confusion Matrix valid
----------------------------------------------------------------------
Ran 8 tests in ~3.4s (OK)
```

---

## 🎓 5-Minute College Presentation Guide

Use this battle-tested presentation script to demonstrate the platform to professors and evaluators:

1. **Slide 1 - Motivation & Problem Statement (`/login`):**
   - Explain that modern APIs represent over 80% of all web traffic and are targeted by credential stuffing, BOLA, and volumetric attacks that bypass traditional IP firewalls.
   - Show the SOC login screen and use the **`admin` autofill button** to sign in.
2. **Slide 2 - Real-Time SOC Dashboard (`/dashboard`):**
   - Point out the dark navy cybersecurity UI.
   - Highlight the **System Threat Level badge (`DEFCON`)**, live Chart.js request latency timeline, and threat category distribution.
3. **Slide 3 - Adversarial Simulation Lab (`/simulation`):**
   - Explain that this is a safe, local sandbox simulating real-world attack vectors.
   - Click **"Launch Brute Force Attack"**: Show the terminal console logging 8 rapid failed attempts on `/api/v1/auth/login`.
   - Click **"Simulate SQLi"**: Demonstrate how regex heuristic signatures detect `' UNION SELECT...` and immediately trigger a Critical alert.
4. **Slide 4 - Incident Triage & Response (`/alerts`):**
   - Show the newly generated alert cards with calculated Risk Scores (85–95/100).
   - Point out the **SOC Recommended Playbook** and click **"Mitigate IP"** or **"Resolve"** to show closed-loop incident handling.
5. **Slide 5 - Explainable AI & Deep Packet Inspection (`/traffic`):**
   - Search for the attacker IP `198.51.100.44`.
   - Click **"Inspect"** to open the **AI Telemetry Modal**, proving that the model explains *why* the request was flagged.
6. **Slide 6 - Model Architecture & Metrics (`/models`):**
   - Show the **Confusion Matrix heatmap** and **Feature Importance chart**.
   - Emphasize that all evaluation metrics are genuinely computed using Scikit-learn test evaluation.

---

## 📁 Repository Directory Structure

```text
api-sentinel-ai-security/
├── app.py                  # Flask application & REST API endpoints
├── config.py               # Security thresholds, session keys & demo presets
├── models.py               # SQLAlchemy ORM models (Users, Requests, Alerts, Logs)
├── detection.py            # AI/ML engine (Random Forest + Isolation Forest)
├── simulator.py            # Attack simulation lab & baseline telemetry seeder
├── requirements.txt        # Python dependency manifest
├── .env.example            # Environment variables template
├── test_app.py             # 8-test automated unit & integration test suite
├── wsgi.py                 # Production WSGI entry point
├── Procfile                # Cloud deployment configuration (Render / Railway)
├── README.md               # Comprehensive documentation & presentation guide
│
├── instance/
│   └── api_sentinel.db     # SQLite database (auto-generated & seeded on boot)
│
├── templates/
│   ├── base.html           # Master SOC layout (sidebar, topbar, modals, toasts)
│   ├── login.html          # Authentication portal with demo account autofill
│   ├── dashboard.html      # Main operational dashboard & Chart.js widgets
│   ├── traffic.html        # API traffic table, packet inspector & custom injector
│   ├── alerts.html         # Threat alert cards & remediation action workflows
│   ├── simulation.html     # Adversarial attack simulation lab & live console
│   ├── models.html         # ML metrics, confusion matrix & feature weights
│   └── logs.html           # System audit event logs
│
├── static/
│   ├── css/
│   │   └── style.css       # Enterprise dark navy cyber theme & glassmorphism
│   ├── js/
│   │   └── app.js          # State manager, Chart.js integrations & live fetchers
│   └── images/
│       └── logo.svg        # Cyber shield vector logo
│
└── docs/
    └── index.html          # Interactive GitHub Pages public showcase webpage
```

---

## 📄 License & Attribution

This project is licensed under the **MIT License** — feel free to use and adapt it for academic, educational, and research projects.

Developed by **[brshirisha27-cloud](https://github.com/brshirisha27-cloud)**  
Academic Mini Project in Cyber Security & Applied Machine Learning.
