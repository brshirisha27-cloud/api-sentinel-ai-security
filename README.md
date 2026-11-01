# API SENTINEL
### AI-Powered API Security and Intelligent Threat Detection Platform

> **Tagline:** Intelligent API Protection. Real-Time Threat Detection.  
> **Academic Project:** Mini Project / Capstone Project in Cyber Security & Applied Machine Learning  
> **Architecture:** Full-Stack SOC Platform (Flask + SQLite + Scikit-Learn + Bootstrap 5 + Chart.js)

---

## 1. Project Overview

**API SENTINEL** is a web-based cybersecurity platform designed to monitor, analyze, and defend application programming interfaces (APIs) in real time. Built in the visual and functional style of an enterprise **Security Operations Center (SOC)**, the platform detects anomalous API requests, assigns composite risk scores (0–100), identifies sophisticated cyber threats (such as Credential Stuffing, Volumetric DoS, BOLA / Broken Object Level Authorization, and SQL Injection), and triggers automated mitigation workflows.

The system features a **dual-model Machine Learning engine** combining a supervised **Random Forest Classifier** with an unsupervised **Isolation Forest** anomaly detector to showcase how modern artificial intelligence augments traditional signature-based web application firewalls (WAF).

---

## 2. Key Features

- **SOC Executive & Operational Dashboard:**
  - Real-time KPI summary (Total API Requests, Safe Requests, Suspicious Events, Blocked Threats, Active Alerts).
  - Dynamic System Threat Level indicator (`LOW`, `GUARDED`, `ELEVATED`, `CRITICAL`).
  - Interactive **Chart.js** Timeline Chart plotting request latency and risk score progression.
  - Threat Category Distribution doughnut visualization.
  - Live streams of recent security incidents and inbound API requests.

- **API Traffic Monitoring & Deep Packet Inspection:**
  - Complete telemetry table (Request ID, Timestamp, HTTP Method, Endpoint, Client IP, Status Code, Latency, AI Classification, Risk Score).
  - Search across IP addresses, endpoints, and threat signatures.
  - Multi-parameter filtering (by HTTP Method, Status Code, and Classification).
  - Deep Packet Inspection modal with full JSON metadata and **AI Explainability breakdown** (the exact heuristics and features that triggered the risk score).
  - Custom Request Ingestion tool to test any custom payload or endpoint on demand.

- **Threat Detection & Incident Management:**
  - Automated alert generation when requests breach risk thresholds.
  - Detailed incident cards with Attack Category, Severity Badge, Source IP, Affected Endpoint, and Risk Meter.
  - SOC Recommended Action Playbooks (e.g., automated IP blacklisting, token revocation, CAPTCHA challenge).
  - Interactive status workflow: `Active` &rarr; `Investigating` &rarr; `Mitigated` &rarr; `Resolved`.

- **Adversarial Attack Simulation Lab:**
  - Safe, local sandbox for simulating 5 real-world attack vectors:
    1. **Normal API Traffic:** Legitimate e-commerce and catalog requests.
    2. **Credential Stuffing / Brute Force:** Rapid failed logins on `/api/v1/auth/login`.
    3. **Volumetric Traffic Spike / DoS:** High-frequency burst causing latency degradation and HTTP 429 throttling.
    4. **BOLA / Unauthorized Privilege Escalation:** Probing restricted administrative and tenant endpoints with forged tokens.
    5. **Malicious Payload Injection:** SQL Injection (`UNION SELECT`) and Cross-Site Scripting (`<script>`) payloads.
  - Terminal-style live execution console with typing output and packet telemetry.
  - Automatic database storage and instant dashboard chart refresh.

- **AI/ML Model Intelligence & Diagnostics:**
  - Evaluated on a held-out synthetic test dataset using **Scikit-learn**.
  - Displays genuine, computed **Accuracy**, **Precision**, **Recall**, and **F1-Score**.
  - Interactive visual **Confusion Matrix** heatmap (True vs. Predicted).
  - Horizontal bar chart of **Feature Importances** (Request Frequency, Failed Logins, Payload Risk, etc.).
  - Mathematical documentation of the composite risk scoring formula.

- **Security Audit Event Logs:**
  - Chronological audit trail of all `AUTH`, `TRAFFIC`, `DETECTION`, `BLOCK`, `SIMULATION`, and `SYSTEM` events.
  - Searchable by IP, endpoint, and event type.
  - Database re-seed button to easily reset demo scenarios.

---

## 3. Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons, Chart.js 4.4 |
| **Backend** | Python 3.10+ / 3.13, Flask 3.1, Werkzeug |
| **Database** | SQLite, Flask-SQLAlchemy 3.1, SQLAlchemy 2.0 |
| **Machine Learning** | Scikit-learn, Pandas, NumPy, Joblib |
| **Architecture** | RESTful JSON API + Server-Side Template Rendering |

---

## 4. Project Directory Structure

```text
AI-Powered API Security/
│
├── app.py                  # Main Flask application and REST API endpoints
├── config.py               # Application configuration and risk thresholds
├── models.py               # SQLAlchemy ORM models (User, Request, Alert, Sim, Log)
├── detection.py            # AI/ML dual-model engine (Random Forest + Isolation Forest)
├── simulator.py            # Attack simulation lab & baseline database seeder
├── requirements.txt        # Python dependency manifest
├── .env.example            # Environment variable template
├── test_app.py             # Automated unit & integration test suite
├── README.md               # Complete documentation & presentation guide
│
├── instance/
│   └── api_sentinel.db     # Persistent SQLite database (auto-generated on boot)
│
├── templates/
│   ├── base.html           # Master SOC layout (sidebar, topbar, modals, toasts)
│   ├── login.html          # Authentication portal with demo account autofill
│   ├── dashboard.html      # Main SOC operational dashboard & Chart.js widgets
│   ├── traffic.html        # API traffic table, packet inspector & custom injector
│   ├── alerts.html         # Threat alert cards & remediation action workflows
│   ├── simulation.html     # Adversarial attack simulation lab & live console
│   ├── models.html         # ML performance metrics, confusion matrix & feature weights
│   └── logs.html           # System audit event logs
│
└── static/
    ├── css/
    │   └── style.css       # Enterprise dark navy cyber theme, glassmorphism, animations
    ├── js/
    │   └── app.js          # Client-side state manager, API fetchers, Chart.js renderers
    └── images/
        └── logo.svg        # Vector cyber shield badge logo
```

---

## 5. Installation and Setup Instructions

### Prerequisites
- Python 3.10 or higher installed on your machine.
- `pip` package manager installed.

### Step 1: Clone or Navigate to the Project Directory
```bash
cd "d:\projects\AI-Powered API Security"
```

### Step 2: Create a Python Virtual Environment
```bash
# On Windows:
python -m venv venv

# On Linux / macOS:
python3 -m venv venv
```

### Step 3: Activate the Virtual Environment
```bash
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# On Windows (Command Prompt):
.\venv\Scripts\activate.bat

# On Linux / macOS:
source venv/bin/activate
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: (Optional) Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
# Windows:
copy .env.example .env

# Linux/macOS:
cp .env.example .env
```

---

## 6. Running the Application

Launch the Flask server:
```bash
python app.py
```

You will see the startup banner:
```text
=======================================================
  API SENTINEL - AI-Powered API Security Platform
  SOC Dashboard Running at: http://127.0.0.1:5000
  Demo Credentials: admin / Sentinel@2025
=======================================================
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

> **Note:** The SQLite database (`instance/api_sentinel.db`) and baseline traffic telemetry are **automatically initialized and seeded** on the very first startup!

---

## 7. Demo Login Credentials

The login page provides one-click autofill buttons for evaluation:

| Role | Username | Password | Access Level |
|---|---|---|---|
| **SOC Administrator** | `admin` | `Sentinel@2025` | Full administrative, simulation, & policy controls |
| **Security Analyst** | `analyst` | `Analyst@2025` | Incident triage, traffic inspection, and threat monitoring |

*(Passwords are securely hashed using Werkzeug `scrypt`/`pbkdf2` algorithms).*

---

## 8. How the AI/ML Threat Detection Engine Works

API Sentinel employs a **dual-model pipeline** coupled with deterministic pattern heuristics:

### Model 1: Random Forest Classifier (Supervised)
- **Algorithm:** 100 decision trees, Gini impurity criterion, max depth of 10.
- **Classes:** `0: Normal`, `1: Suspicious`, `2: Potential Attack`.
- **Feature Vector (8 Dimensions):**
  1. `request_frequency`: Requests per minute from client IP.
  2. `failed_login_count`: Consecutive failed authentication attempts.
  3. `response_status`: HTTP status code (200, 401, 403, 429, 500).
  4. `payload_size`: Request size in bytes.
  5. `response_time_ms`: Backend latency in milliseconds.
  6. `auth_status`: `0` = Authenticated, `1` = Anonymous, `2` = Forged/Invalid Token.
  7. `payload_risk_indicator`: Regex heuristic score (0–10) capturing SQLi, XSS, and path traversal patterns.
  8. `endpoint_risk_weight`: `1` = Public endpoint, `2` = User profile, `3` = Sensitive auth/admin gateway.

### Model 2: Isolation Forest (Unsupervised)
- **Algorithm:** 100 isolation trees, contamination parameter 0.15.
- **Objective:** Detect zero-day outliers and abnormal multivariate distributions without requiring historical labeled examples.
- **Output:** Transformed into a normalized Anomaly Index (0–100).

### Composite Risk Scoring Formula (0 to 100)
```text
Risk Score = (0.45 × RF_Risk) + (0.25 × IF_Anomaly) + (0.30 × Heuristic_Penalty)
```
- **0 – 29 (Low / Safe):** Conforms to baseline; allowed.
- **30 – 59 (Medium / Suspicious):** Deviates from baseline; flagged for behavioral monitoring.
- **60 – 79 (High Severity):** Significant attack indicators; throttled or challenged.
- **80 – 100 (Critical Threat):** Definite malicious pattern; instantly blocked at WAF.

---

## 9. How to Demonstrate During Your Academic Presentation

Follow this 5-minute presentation script to impress evaluators:

1. **Slide 1 - Login & Authentication (`/login`):**
   - Highlight secure password hashing and role-based access.
   - Click the **"admin"** autofill pill and sign in.
2. **Slide 2 - Executive SOC Dashboard (`/dashboard`):**
   - Point out the dark enterprise cybersecurity interface.
   - Show dynamic KPIs, real-time Defcon status beacon, and Chart.js telemetry charts.
3. **Slide 3 - Adversarial Attack Simulation Lab (`/simulation`):**
   - Explain the educational sandbox concept.
   - Click **"Launch Brute Force Attack"**: Watch the terminal console log the 8 rapid failed attempts on `/api/v1/auth/login`.
   - Click **"Simulate SQLi"**: Watch the injection heuristic detect `' UNION SELECT...` and immediately trigger a Critical alert.
4. **Slide 4 - Incident Triage & Alerts (`/alerts`):**
   - Show the newly generated alert cards.
   - Highlight the **SOC Recommended Playbook** and click **"Mitigate IP"** or **"Resolve"** to demonstrate active response.
5. **Slide 5 - Traffic Inspection (`/traffic`):**
   - Filter by `Potential Attack` or search for IP `198.51.100.44`.
   - Click **"Inspect"** to reveal the **AI Explainability Modal**, demonstrating transparent reasoning.
6. **Slide 6 - Model Diagnostics (`/models`):**
   - Showcase the confusion matrix and feature importance chart.
   - Explain that all metrics are computed from a held-out test dataset using Scikit-learn.

---

## 10. Running the Automated Test Suite

A comprehensive test suite is included to verify all backend routes, security policies, and ML predictions:

```bash
python test_app.py
```

Expected output:
```text
Ran 8 tests in ~3.5s
OK
[PASS] /api/health returns HEALTHY and dual engines online
[PASS] Protected /dashboard redirects unauthenticated users
[PASS] Authentication workflow (bad credentials, login, logout)
[PASS] Page /dashboard, /traffic, /alerts, /simulation, /models, /logs rendered
[PASS] /api/stats returned dynamic KPIs and chart timelines
[PASS] /api/traffic retrieved paginated items with filtering
[PASS] Attack Simulation Lab executed normal, brute force, and SQLi attacks
[PASS] ML Model Metrics: Accuracy=100%, F1=100%
```

---

## 11. Important Academic & Educational Disclaimer

> **Educational Use Notice:**  
> API SENTINEL is built for academic demonstration, research, and educational purposes. The Machine Learning models are trained and evaluated on a structured synthetic API benchmark dataset. While the detection logic, heuristics, and mathematical formulas reflect industry-standard practices (OWASP API Security Top 10), synthetic test evaluations do not represent absolute guarantees of real-world production security.

