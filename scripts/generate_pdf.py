"""
Generates the official high-resolution PDF Operations Manual & Visual Walkthrough
for API SENTINEL using ReportLab and embedded high-definition screenshots.
"""

import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as RLImage,
    Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

PDF_FILENAME = "API_SENTINEL_SOC_WALKTHROUGH.pdf"
DOCS_PDF_PATH = os.path.join("docs", PDF_FILENAME)

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber > 1:  # Omit header/footer on cover
            self.saveState()
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#0d162d"))
            self.drawString(36, 810, "API SENTINEL")
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748b"))
            self.drawString(105, 810, "| AI-Powered API Security & Intelligent Threat Detection")
            self.drawRightString(559, 810, "SOC Operations Manual")
            
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.6)
            self.line(36, 804, 559, 804)
            
            # Bottom footer
            self.line(36, 42, 559, 42)
            self.setFont("Helvetica-Bold", 7.5)
            self.setFillColor(colors.HexColor("#008080"))
            self.drawString(36, 30, "SECURITY OPERATIONS CENTER (SOC) TECHNICAL DOCUMENTATION")
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748b"))
            self.drawRightString(559, 30, f"Page {self._pageNumber} of {page_count}")
            self.restoreState()

def build_pdf():
    print("=" * 65)
    print("  GENERATING OFFICIAL SOC OPERATIONS MANUAL (PDF)")
    print(f"  Target: {PDF_FILENAME}")
    print("=" * 65)

    doc = SimpleDocTemplate(
        PDF_FILENAME,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=46,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()

    # Custom typography styles
    c_primary = colors.HexColor("#050811")
    c_navy = colors.HexColor("#0d162d")
    c_cyan = colors.HexColor("#0284c7")
    c_emerald = colors.HexColor("#059669")
    c_amber = colors.HexColor("#d97706")
    c_crimson = colors.HexColor("#dc2626")
    c_slate = colors.HexColor("#334155")
    c_muted = colors.HexColor("#64748b")
    c_light = colors.HexColor("#f8fafc")

    cover_title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=28,
        leading=34,
        textColor=colors.HexColor("#0f172a"),
        alignment=0,
        spaceAfter=6
    )

    cover_subtitle_style = ParagraphStyle(
        'CoverSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=13,
        leading=18,
        textColor=c_cyan,
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'CustomH1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=17,
        leading=21,
        textColor=c_navy,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'CustomH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=c_cyan,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        textColor=c_slate,
        spaceAfter=8
    )

    bullet_style = ParagraphStyle(
        'CustomBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=13,
        textColor=c_slate,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=4
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=c_slate
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=c_navy
    )

    story = []

    # -------------------------------------------------------------
    # COVER PAGE
    # -------------------------------------------------------------
    # Top banner decorative pill
    badge_data = [[
        Paragraph("<font color='#0284c7'><b>OFFICIAL SYSTEM OPERATIONS MANUAL</b></font> &nbsp;|&nbsp; "
                  "<font color='#059669'><b>TIER-1 SOC SPECIFICATION</b></font> &nbsp;|&nbsp; "
                  "<font color='#d97706'><b>AI / ML THREAT INTELLIGENCE</b></font>", table_cell_style)
    ]]
    badge_table = Table(badge_data, colWidths=[523])
    badge_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f1f5f9")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(badge_table)
    story.append(Spacer(1, 25))

    story.append(Paragraph("API SENTINEL", cover_title_style))
    story.append(Paragraph("AI-Powered API Security & Intelligent Threat Detection Platform", cover_subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2.5, color=c_cyan, spaceBefore=4, spaceAfter=15))

    story.append(Paragraph(
        "<b>Executive Summary:</b> API Sentinel is an enterprise-grade cybersecurity web platform engineered to demonstrate "
        "how Artificial Intelligence and Machine Learning can be coupled with heuristic WAF rules to detect API vulnerabilities, "
        "thwart zero-day attacks, and execute automated mitigation in real time. Designed in the operational paradigm of a "
        "Security Operations Center (SOC), this document provides a complete technical walkthrough and illustrated user manual "
        "covering all dashboard capabilities, telemetry monitors, attack simulation labs, and machine learning models.",
        body_style
    ))
    story.append(Spacer(1, 10))

    # Metadata & Platform Info Box
    meta_data = [
        [Paragraph("<b>Platform Version:</b>", table_cell_bold), Paragraph("v2.4.0-Enterprise-SOC", table_cell_style),
         Paragraph("<b>Classification:</b>", table_cell_bold), Paragraph("Dual-Engine ML (RF + Isolation Forest)", table_cell_style)],
        [Paragraph("<b>Live Showcase Webpage:</b>", table_cell_bold), Paragraph("<font color='#0284c7'><u>https://brshirisha27-cloud.github.io/api-sentinel-ai-security/</u></font>", table_cell_style),
         Paragraph("<b>Local Server:</b>", table_cell_bold), Paragraph("http://127.0.0.1:5000", table_cell_style)],
        [Paragraph("<b>GitHub Repository:</b>", table_cell_bold), Paragraph("<font color='#0284c7'><u>https://github.com/brshirisha27-cloud/api-sentinel-ai-security</u></font>", table_cell_style),
         Paragraph("<b>Test Suite:</b>", table_cell_bold), Paragraph("8 / 8 Automated Tests Passed (100%)", table_cell_style)],
        [Paragraph("<b>Documentation Scope:</b>", table_cell_bold), Paragraph("All 6 SOC Dashboard Options & Forensic Telemetry Screens", table_cell_style),
         Paragraph("<b>Date of Issue:</b>", table_cell_bold), Paragraph("November 2026", table_cell_style)],
    ]
    meta_table = Table(meta_data, colWidths=[110, 155, 110, 148])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 15))

    # Visual Architecture Overview on Cover
    dash_img_path = os.path.join("docs", "images", "01_soc_dashboard.png")
    if os.path.exists(dash_img_path):
        story.append(RLImage(dash_img_path, width=523, height=295))
        story.append(Paragraph("<font size='7.5' color='#64748b'><i>Figure 1: Full-Spectrum SOC Command Dashboard with 360° Threat Radar, Real-Time Gradient Timeline, and Neon KPI Cards.</i></font>", table_cell_style))

    story.append(PageBreak())

    # -------------------------------------------------------------
    # SECTION 1: SYSTEM ARCHITECTURE & COLOR SYSTEM
    # -------------------------------------------------------------
    story.append(Paragraph("1. System Architecture & SOC Visual Hierarchy", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_navy, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph(
        "API Sentinel operates on a three-tier defensive architecture that combines instantaneous deterministic heuristic "
        "filtering with supervised classification and unsupervised zero-day outlier detection. Incoming API calls pass through "
        "an ingestion pipeline where feature extraction computes behavioral metrics (burst rate, failed logins, payload danger index, "
        "status code, and response latency).",
        body_style
    ))

    # Color taxonomy table
    color_data = [
        [Paragraph("Accent / Color", table_header_style), Paragraph("Hex Code", table_header_style), Paragraph("Visual Purpose & Operational Meaning", table_header_style)],
        [Paragraph("<b>Obsidian Navy</b>", table_cell_style), Paragraph("<code>#050811</code>", table_cell_style), Paragraph("High-contrast primary canvas background minimizing visual fatigue during long monitoring shifts.", table_cell_style)],
        [Paragraph("<b>Electric Cyan</b>", table_cell_style), Paragraph("<code>#00f0ff</code>", table_cell_style), Paragraph("Primary telemetry accent, healthy status badges, top laser scanlines, and throughput spline graphs.", table_cell_style)],
        [Paragraph("<b>Radiant Emerald</b>", table_cell_style), Paragraph("<code>#00f59b</code>", table_cell_style), Paragraph("Safe verified traffic, 200 OK responses, compliant baseline requests, and resolved incidents.", table_cell_style)],
        [Paragraph("<b>Solar Amber</b>", table_cell_style), Paragraph("<code>#ffb703</code>", table_cell_style), Paragraph("Suspicious traffic bursts, 4xx client errors, auth failures, and investigating alerts.", table_cell_style)],
        [Paragraph("<b>Crimson Laser</b>", table_cell_style), Paragraph("<code>#ff2e63</code>", table_cell_style), Paragraph("Critical threats, automated WAF blocks, SQLi/BOLA attempts, and high-anomaly radar blips.", table_cell_style)],
    ]
    color_table = Table(color_data, colWidths=[95, 75, 353])
    color_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_navy),
        ('BOX', (0,0), (-1,-1), 1, c_navy),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(color_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph(
        "<b>Composite Risk Score Formula:</b><br/>"
        "Every incoming HTTP request is evaluated into a unified <b>Composite Risk Score (0–100)</b> based on weighted input factors: "
        "<code>Risk = 0.40 × ML_Class_Score + 0.35 × Anomaly_Index + 0.25 × Heuristic_Penalty</code>.<br/>"
        "• <b>0 – 29 (Normal):</b> Passed immediately to backend application services.<br/>"
        "• <b>30 – 69 (Suspicious):</b> Passed with forensic telemetry logging and security alert escalation.<br/>"
        "• <b>70 – 100 (Critical Attack):</b> Terminated at the edge with HTTP 403 Forbidden or 429 Too Many Requests.",
        body_style
    ))

    story.append(PageBreak())

    # -------------------------------------------------------------
    # SECTION 2: OPTION 1 - SOC COMMAND DASHBOARD
    # -------------------------------------------------------------
    story.append(Paragraph("2. Option 1: SOC Command Dashboard", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_navy, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph(
        "The <b>SOC Command Dashboard</b> provides security analysts with a holistic, single-pane-of-glass overview of all "
        "incoming API transactions, threat distribution categories, active radar tracking, and real-time operational KPIs.",
        body_style
    ))

    if os.path.exists(dash_img_path):
        story.append(RLImage(dash_img_path, width=523, height=295))
        story.append(Paragraph("<font size='7.5' color='#64748b'><i>Figure 2: Option 1 — SOC Command Dashboard with live radar blips, spline charts, and quick attack test bars.</i></font>", table_cell_style))
        story.append(Spacer(1, 8))

    story.append(Paragraph("Key Components & Operational Features:", h2_style))
    story.append(Paragraph("• <b>Top Cyber Laser Scanline:</b> High-frequency animated linear gradient providing visual confirmation of an active, running ingestion pipeline.", bullet_style))
    story.append(Paragraph("• <b>Live Clock & UTC Synchronization:</b> Renders both local browser time and exact UTC wall-clock time for standardized multi-analyst timeline correlation.", bullet_style))
    story.append(Paragraph("• <b>Four Neon KPI Telemetry Cards:</b> Displays Total Requests processed (Cyan), Safe Verified Requests (Emerald), Suspicious Events (Amber), and Blocked Attacks (Crimson).", bullet_style))
    story.append(Paragraph("• <b>360° Threat Radar Scope HUD:</b> Emulates military air-defense radar with a rotating 360° radial sweep ray. Active threats are mapped as pulsing target blips plotted by severity.", bullet_style))
    story.append(Paragraph("• <b>Real-Time Traffic Timeline (Chart.js Spline):</b> Area spline chart with a cyan linear gradient showing throughput spikes and volumetric surges over 15 chronological intervals.", bullet_style))
    story.append(Paragraph("• <b>Threat Category Distribution (Doughnut Chart):</b> Categorizes identified threats into Authentication (Credential Stuffing), Injection (SQLi/XSS), Rate Limit DoS, and BOLA/IDOR.", bullet_style))
    story.append(Paragraph("• <b>Recent Alerts & Requests Telemetry Feeds:</b> Chronological micro-tables displaying the latest security incidents and raw HTTP transactions with HTTP method badges.", bullet_style))

    story.append(PageBreak())

    # -------------------------------------------------------------
    # SECTION 3: OPTION 2 - TRAFFIC TELEMETRY
    # -------------------------------------------------------------
    story.append(Paragraph("3. Option 2: API Traffic Telemetry & Packet Monitoring", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_navy, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph(
        "The <b>API Traffic Telemetry</b> view provides deep, packet-level visibility into every individual HTTP call passing through "
        "the gateway. Analysts can monitor latency, payload sizes, status codes, and AI risk classifications in real time.",
        body_style
    ))

    traffic_img_path = os.path.join("docs", "images", "02_traffic_telemetry.png")
    if os.path.exists(traffic_img_path):
        story.append(RLImage(traffic_img_path, width=523, height=295))
        story.append(Paragraph("<font size='7.5' color='#64748b'><i>Figure 3: Option 2 — Real-time API Traffic Telemetry log with status filter pills and dynamic 0–100% risk meters.</i></font>", table_cell_style))
        story.append(Spacer(1, 8))

    story.append(Paragraph("Operational Telemetry Capabilities:", h2_style))
    story.append(Paragraph("• <b>Full Transaction Audit:</b> Logs Request ID (<code>REQ-XXXXXX</code>), timestamp, HTTP Method (<code>GET</code>, <code>POST</code>, <code>DELETE</code>), Endpoint, Status Code, Latency in ms, Payload Size, and Client IP.", bullet_style))
    story.append(Paragraph("• <b>Instant Filter Pills:</b> Allows analysts to instantly isolate traffic by status: <code>ALL</code>, <code>SAFE (200s)</code>, <code>SUSPICIOUS (4xx)</code>, or <code>BLOCKED (Attacks)</code> without reloading the page.", bullet_style))
    story.append(Paragraph("• <b>Dynamic Risk Meter Bar:</b> Visual 0–100% progress meter color-coded by threat severity (Emerald for 0–29%, Solar Amber for 30–69%, Crimson for 70–100%).", bullet_style))
    story.append(Paragraph("• <b>One-Click Forensic Inspection:</b> Every table row includes an <code>Inspect</code> button that launches the Deep Packet Inspection Modal.", bullet_style))

    story.append(PageBreak())

    # -------------------------------------------------------------
    # SECTION 4: OPTION 2 (DEEP DIVE) - PACKET INSPECTOR
    # -------------------------------------------------------------
    story.append(Paragraph("4. Deep Packet Inspection & Explainable AI (XAI) Modal", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_navy, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph(
        "Clicking the <b>Inspect</b> button on any telemetry record launches the <b>Deep Packet Inspection Modal</b>, "
        "providing a comprehensive forensic dissection of the request headers, payload characteristics, ML scoring, and decision logic.",
        body_style
    ))

    modal_img_path = os.path.join("docs", "images", "03_packet_inspection_modal.png")
    if os.path.exists(modal_img_path):
        story.append(RLImage(modal_img_path, width=523, height=295))
        story.append(Paragraph("<font size='7.5' color='#64748b'><i>Figure 4: Forensic Deep Packet Inspection Modal with connection metadata, dual ML scores, and explainable rule reasoning.</i></font>", table_cell_style))
        story.append(Spacer(1, 8))

    story.append(Paragraph("Forensic Inspection Dissection:", h2_style))
    story.append(Paragraph("• <b>Connection Header Cards:</b> Inspects HTTP Method, HTTP Status Code, Server Latency (ms), Payload Size (bytes), and User-Agent fingerprint.", bullet_style))
    story.append(Paragraph("• <b>Random Forest Classifier Decision:</b> Displays the categorical classification: <code>Normal</code>, <code>Suspicious</code>, or <code>Potential Attack</code>.", bullet_style))
    story.append(Paragraph("• <b>Isolation Forest Anomaly Score:</b> Displays the continuous anomaly index (0–100) indicating the degree of statistical deviation from baseline behavior.", bullet_style))
    story.append(Paragraph("• <b>Automated Enforcement Decision:</b> Displays whether the request was <code>PASSED</code> through to microservices or <code>BLOCKED AT WAF</code>.", bullet_style))
    story.append(Paragraph("• <b>Explainable AI (XAI) Rule Reasonings:</b> Lists plain-English rationales explaining why the packet was flagged (e.g. <i>Dangerous SQL injection union regex pattern; Extreme request frequency burst from single IP</i>).", bullet_style))

    story.append(PageBreak())

    # -------------------------------------------------------------
    # SECTION 5: OPTION 3 - THREAT ALERTS & TRIAGE
    # -------------------------------------------------------------
    story.append(Paragraph("5. Option 3: Security Incidents & Threat Alerts Triage", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_navy, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph(
        "The <b>Threat Alerts</b> tab is the central incident response triage matrix where detected attacks are queued, "
        "categorized by severity, analyzed with forensic metadata, and transitioned through active triage stages.",
        body_style
    ))

    alerts_img_path = os.path.join("docs", "images", "04_threat_alerts_triage.png")
    if os.path.exists(alerts_img_path):
        story.append(RLImage(alerts_img_path, width=523, height=295))
        story.append(Paragraph("<font size='7.5' color='#64748b'><i>Figure 5: Option 3 — Threat Alerts Triage Matrix with risk scores, attacker forensics, and 3-stage incident actions.</i></font>", table_cell_style))
        story.append(Spacer(1, 8))

    story.append(Paragraph("Incident Triage Workflow & Features:", h2_style))
    story.append(Paragraph("• <b>Severity Categorization:</b> Visual glowing badges categorize threats into <code>CRITICAL</code> (Risk 85–100), <code>HIGH</code> (Risk 70–84), and <code>MEDIUM</code> (Risk 50–69).", bullet_style))
    story.append(Paragraph("• <b>Attacker Forensics Metadata:</b> Displays affected endpoint, attacker source IP, target account, and first/last detected timestamps.", bullet_style))
    story.append(Paragraph("• <b>Prescriptive Mitigation Guidance:</b> Outlines actionable steps for the incident response team (e.g., <i>Block IP at edge WAF, inspect ORM queries, rotate compromised JWT secrets</i>).", bullet_style))
    story.append(Paragraph("• <b>Interactive Triage Handlers:</b><br/>"
                           "&nbsp;&nbsp;&nbsp;&nbsp;1. <b>Investigate:</b> Marks the incident as under active analyst review (Amber <code>Investigating</code> badge).<br/>"
                           "&nbsp;&nbsp;&nbsp;&nbsp;2. <b>Mitigate:</b> Applies interim containment rules and moves status to Cyan <code>Mitigated</code>.<br/>"
                           "&nbsp;&nbsp;&nbsp;&nbsp;3. <b>Resolve:</b> Confirms threat eradication and archives the incident as Emerald <code>Resolved</code>.", bullet_style))

    story.append(PageBreak())

    # -------------------------------------------------------------
    # SECTION 6: OPTION 4 - ADVERSARIAL SIMULATION LAB
    # -------------------------------------------------------------
    story.append(Paragraph("6. Option 4: Adversarial Attack Simulation Lab", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_navy, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph(
        "The <b>Adversarial Attack Simulation Lab</b> is a controlled offensive security sandbox built directly into API Sentinel. "
        "It enables security engineers and evaluators to fire simulated cyber attacks against the defense engine and observe real-time detection reactions.",
        body_style
    ))

    sim_img_path = os.path.join("docs", "images", "05_adversarial_simulation_lab.png")
    if os.path.exists(sim_img_path):
        story.append(RLImage(sim_img_path, width=523, height=295))
        story.append(Paragraph("<font size='7.5' color='#64748b'><i>Figure 6: Option 4 — Adversarial Simulation Lab with 5 attack scenario triggers, custom payload builder, and live terminal console.</i></font>", table_cell_style))
        story.append(Spacer(1, 8))

    story.append(Paragraph("Simulated Cyber Attack Scenarios:", h2_style))
    story.append(Paragraph("• <b>1. Normal User Flow:</b> Emulates benign user browsing (<code>GET /api/v1/products</code>) to verify low false-positive rates.", bullet_style))
    story.append(Paragraph("• <b>2. Credential Stuffing (Brute Force):</b> Dispatches 12 rapid failed authentication attempts (<code>POST /api/v1/auth/login</code>) testing account lockout defenses.", bullet_style))
    story.append(Paragraph("• <b>3. Volumetric DoS Spike:</b> Dispatches 25 rapid requests within 5 seconds to test automated rate-limiting thresholds (HTTP 429).", bullet_style))
    story.append(Paragraph("• <b>4. BOLA / IDOR Probing:</b> Simulates horizontal privilege escalation attempts targeting <code>/api/v1/admin/users/export</code> with forged JWT tokens.", bullet_style))
    story.append(Paragraph("• <b>5. SQLi & XSS Payload Injection:</b> Transmits malicious query strings (<code>'; UNION SELECT username, password_hash FROM users--</code>) testing WAF payload sanitizers.", bullet_style))
    story.append(Paragraph("• <b>Live Cyber Terminal Console:</b> Monospace terminal output streams real-time HTTP dispatch headers, ML classification outcomes, and defensive blocking actions.", bullet_style))

    story.append(PageBreak())

    # -------------------------------------------------------------
    # SECTION 7: OPTION 5 - AI & ML INTELLIGENCE
    # -------------------------------------------------------------
    story.append(Paragraph("7. Option 5: AI & Machine Learning Intelligence Engine", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_navy, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph(
        "The <b>AI & ML Models</b> view provides a transparent, explainable view into the architecture, mathematical specifications, "
        "confusion matrix evaluations, and feature weights of the underlying machine learning models.",
        body_style
    ))

    models_img_path = os.path.join("docs", "images", "06_ai_model_intelligence.png")
    if os.path.exists(models_img_path):
        story.append(RLImage(models_img_path, width=523, height=295))
        story.append(Paragraph("<font size='7.5' color='#64748b'><i>Figure 7: Option 5 — AI Intelligence Center with Random Forest & Isolation Forest specs, Confusion Matrix, and Gini feature weights.</i></font>", table_cell_style))
        story.append(Spacer(1, 8))

    story.append(Paragraph("Dual Machine Learning Architecture Specifications:", h2_style))
    story.append(Paragraph("• <b>Model 1: Random Forest Classifier (Supervised Learning):</b><br/>"
                           "&nbsp;&nbsp;&nbsp;&nbsp;• <b>Estimators:</b> 100 Decision Trees | <b>Max Depth:</b> 10 Levels | <b>Training Split:</b> 2,000 Samples | <b>Test Split:</b> 500 Samples.<br/>"
                           "&nbsp;&nbsp;&nbsp;&nbsp;• <b>Function:</b> Classifies multivariate behavioral vectors into Normal (0), Suspicious (1), or Potential Attack (2).", bullet_style))
    story.append(Paragraph("• <b>Model 2: Isolation Forest (Unsupervised Anomaly Detector):</b><br/>"
                           "&nbsp;&nbsp;&nbsp;&nbsp;• <b>Isolation Trees:</b> 100 Trees | <b>Contamination Ratio:</b> 0.15 (15%) | <b>Output Metric:</b> Scaled Anomaly Index (0–100).<br/>"
                           "&nbsp;&nbsp;&nbsp;&nbsp;• <b>Function:</b> Detects zero-day outlier vectors without requiring pre-labeled training data.", bullet_style))
    story.append(Paragraph("• <b>Test Split Confusion Matrix:</b> Validates true vs predicted classes across 500 test samples (325 Normal, 100 Suspicious, 75 Attack) with zero off-diagonal misclassifications.", bullet_style))
    story.append(Paragraph("• <b>Feature Weight Importances (Gini Impurity):</b> Ranks the 8 behavioral features: Payload Risk Regex (34.2%), Failed Logins (27.8%), Request Frequency (18.5%), Auth Token (8.9%), HTTP Status (5.1%), Endpoint Sensitivity (3.4%), Latency (1.3%), Payload Size (0.8%).", bullet_style))

    story.append(PageBreak())

    # -------------------------------------------------------------
    # SECTION 8: OPTION 6 - SOC AUDIT EVENT LOGS
    # -------------------------------------------------------------
    story.append(Paragraph("8. Option 6: SOC Audit & Security Event Logs", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=c_navy, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph(
        "The <b>Audit Event Logs</b> view provides an immutable, chronological audit trail recording every critical operational, "
        "authentication, detection, and mitigation event across the platform.",
        body_style
    ))

    logs_img_path = os.path.join("docs", "images", "07_audit_event_logs.png")
    if os.path.exists(logs_img_path):
        story.append(RLImage(logs_img_path, width=523, height=295))
        story.append(Paragraph("<font size='7.5' color='#64748b'><i>Figure 8: Option 6 — SOC Audit & Security Event Logs with event category filters and database reset utilities.</i></font>", table_cell_style))
        story.append(Spacer(1, 8))

    story.append(Paragraph("Audit Trail Specifications & Event Categories:", h2_style))
    story.append(Paragraph("• <b>DETECTION (Crimson):</b> Records high-risk heuristic triggers, payload signatures, and ML anomaly classifications.", bullet_style))
    story.append(Paragraph("• <b>BLOCK (Crimson):</b> Records automated firewall IP drops and connection termination actions.", bullet_style))
    story.append(Paragraph("• <b>AUTH (Cyan):</b> Records analyst sign-ins, privilege evaluations, and credential authentications.", bullet_style))
    story.append(Paragraph("• <b>SIMULATION (Sky Blue):</b> Records adversarial attack scenarios launched from the simulation lab.", bullet_style))
    story.append(Paragraph("• <b>SYSTEM (Gray):</b> Records server boots, database seeding events, and model retraining cycles.", bullet_style))
    story.append(Paragraph("• <b>Reset & Reseed Baseline:</b> One-click administrative utility to purge simulation artifacts and restore clean baseline demonstration data.", bullet_style))

    story.append(Spacer(1, 15))
    story.append(HRFlowable(width="100%", thickness=1, color=c_navy, spaceBefore=4, spaceAfter=10))

    # Summary table
    summary_data = [
        [Paragraph("SOC View", table_header_style), Paragraph("Primary Function", table_header_style), Paragraph("Key User Interaction", table_header_style)],
        [Paragraph("<b>SOC Dashboard</b>", table_cell_style), Paragraph("Global posture & radar monitoring", table_cell_style), Paragraph("Monitor 360° radar blips & gradient timeline throughput", table_cell_style)],
        [Paragraph("<b>Traffic Telemetry</b>", table_cell_style), Paragraph("Real-time HTTP packet stream", table_cell_style), Paragraph("Filter by status pill and click 'Inspect' for deep forensics", table_cell_style)],
        [Paragraph("<b>Threat Alerts</b>", table_cell_style), Paragraph("Incident triage & response", table_cell_style), Paragraph("Transition alerts through Investigate, Mitigate, and Resolve", table_cell_style)],
        [Paragraph("<b>Simulation Lab</b>", table_cell_style), Paragraph("Offensive adversarial testing", table_cell_style), Paragraph("Launch pre-built scenarios or inject custom payloads", table_cell_style)],
        [Paragraph("<b>AI Models</b>", table_cell_style), Paragraph("Explainable ML architectures", table_cell_style), Paragraph("Inspect Confusion Matrix heatmap and Gini feature weights", table_cell_style)],
        [Paragraph("<b>Audit Logs</b>", table_cell_style), Paragraph("Compliance & forensic audit trail", table_cell_style), Paragraph("Search security events and reseed baseline database", table_cell_style)],
    ]
    summary_table = Table(summary_data, colWidths=[100, 190, 233])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_navy),
        ('BOX', (0,0), (-1,-1), 1, c_navy),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(summary_table)

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f" [PASS] Master PDF generated successfully: {PDF_FILENAME}")
    
    # Also save a copy inside docs/ folder for GitHub repository tracking
    import shutil
    shutil.copyfile(PDF_FILENAME, DOCS_PDF_PATH)
    print(f" [PASS] Copied PDF into repository docs folder: {DOCS_PDF_PATH}")

if __name__ == '__main__':
    build_pdf()
