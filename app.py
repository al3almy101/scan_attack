#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
import os
import threading
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import urlparse
import logging
import sys
import traceback
import subprocess
import html
from scanner_engine import AdvancedScanner, AdvancedWAFBypassV2

# تعريف الألوان للطباعة في التيرمينال
G = "\033[92m"  # الأخضر
Y = "\033[93m"  # الأصفر
R = "\033[91m"  # الأحمر
W = "\033[0m"   # الأبيض (إعادة ضبط)
C = "\033[96m"  # السماوي
B = "\033[94m"  # الأزرق

# ===== مسارات أدوات الـ Recon =====
# المسار الذي يحتوي على الأدوات (ثبته حسب مجلدك)
TOOLS_DIR = r"C:\Users\CAVO TECH\Desktop\security_scanner\tool"

# التأكد من كتابة المسار كاملاً لكل أداة مع إضافة .exe
SUBFINDER_EXE = os.path.join(TOOLS_DIR, "subfinder.exe")
GAU_EXE = os.path.join(TOOLS_DIR, "gau.exe")
KATANA_EXE = os.path.join(TOOLS_DIR, "katana.exe")

# التحقق من وجود الأدوات
print(f"{B}[*] Checking tools in: {TOOLS_DIR}{W}")
for tool in [SUBFINDER_EXE, GAU_EXE, KATANA_EXE]:
    if os.path.exists(tool):
        print(f"{G}[✓] Found: {os.path.basename(tool)}{W}")
    else:
        print(f"{R}[✗] Missing: {os.path.basename(tool)}{W}")

# إعداد logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-it'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scanner.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ===== دالة تشغيل الأدوات الخارجية (معدلة للويندوز) =====
def run_external_tool(tool_path, args, timeout=120):
    """تشغيل أداة خارجية وإرجاع الناتج - معدلة للويندوز"""
    try:
        tool_name = os.path.basename(tool_path)
        print(f"{B}[*] Running: {tool_name} {' '.join(args)}{W}")
        
        # في ويندوز، نستخدم shell=True أحياناً
        result = subprocess.run(
            f'"{tool_path}" {" ".join(args)}',
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=True
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            if output:
                print(f"{G}[+] {tool_name} completed successfully{W}")
                return output
            else:
                print(f"{Y}[!] {tool_name} returned no output{W}")
                return ""
        else:
            error_msg = result.stderr.strip() if result.stderr else "Unknown error"
            print(f"{R}[!] {tool_name} error: {error_msg[:200]}{W}")
            return ""
            
    except subprocess.TimeoutExpired:
        print(f"{Y}[!] {tool_name} timeout after {timeout}s{W}")
        return ""
    except FileNotFoundError:
        print(f"{R}[!] {tool_name} not found at: {tool_path}{W}")
        return ""
    except Exception as e:
        print(f"{R}[!] Failed to run {tool_name}: {str(e)}{W}")
        return ""

# ===== Email Configuration =====
user_email_config = {}

def send_vulnerability_report(scan_id, user_email, report_data, user_config):
    """إرسال تقرير الثغرات عبر الإيميل"""
    if not user_config.get('enabled'):
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = user_config['email']
        msg['To'] = user_email
        msg['Subject'] = f"SCAN ATTACK - Vulnerability Report #{scan_id}"
        
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background: #0a0c0f; color: #e0e0e0; }}
                .header {{ background: linear-gradient(135deg, #00ff9d, #00b8ff); padding: 20px; color: black; text-align: center; }}
                .summary {{ display: flex; gap: 20px; margin: 20px 0; flex-wrap: wrap; }}
                .stat {{ flex: 1; min-width: 100px; padding: 15px; border-radius: 5px; text-align: center; }}
                .critical {{ background: rgba(255, 59, 59, 0.2); border-left: 4px solid #ff3b3b; }}
                .high {{ background: rgba(255, 170, 0, 0.2); border-left: 4px solid #ffaa00; }}
                .medium {{ background: rgba(255, 255, 0, 0.2); border-left: 4px solid #ffff00; }}
                .low {{ background: rgba(0, 255, 157, 0.2); border-left: 4px solid #00ff9d; }}
                .vuln {{ margin: 15px 0; padding: 15px; border-radius: 5px; background: #1e2429; }}
                .vuln.critical {{ border-left: 4px solid #ff3b3b; }}
                .vuln.high {{ border-left: 4px solid #ffaa00; }}
                .vuln.medium {{ border-left: 4px solid #ffff00; }}
                .vuln.low {{ border-left: 4px solid #00ff9d; }}
                code {{ background: #0a0c0f; padding: 5px; border-radius: 3px; color: #00ff9d; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔍 SCAN ATTACK - Security Scan Report</h1>
                <p>Target: {report_data['target']}</p>
                <p>Scan Time: {report_data['scan_time']}</p>
            </div>
            
            <h2>📊 Summary</h2>
            <div class="summary">
                <div class="stat critical">Critical<br>{report_data['summary']['critical']}</div>
                <div class="stat high">High<br>{report_data['summary']['high']}</div>
                <div class="stat medium">Medium<br>{report_data['summary']['medium']}</div>
                <div class="stat low">Low<br>{report_data['summary']['low']}</div>
            </div>
            <p><strong>Total Vulnerabilities:</strong> {report_data['summary']['total']}</p>
            
            <h2>🎯 Vulnerabilities Found</h2>
        """
        
        for vuln in report_data['vulnerabilities']:
            severity = vuln.get('severity', 'INFO').lower()
            html_content += f"""
            <div class="vuln {severity}">
                <h3>{vuln.get('type', 'Unknown')}</h3>
                <p><strong>URL:</strong> {vuln.get('url', 'N/A')}</p>
                <p><strong>Parameter:</strong> {vuln.get('param', 'N/A')}</p>
                <p><strong>Confidence:</strong> {vuln.get('confidence', 'MEDIUM')}</p>
                <p><strong>Payload:</strong> <code>{vuln.get('payload', 'N/A')}</code></p>
            </div>
            """
        
        html_content += "</body></html>"
        
        msg.attach(MIMEText(html_content, 'html'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(user_config['email'], user_config['password'])
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        logger.error(f"Email error: {e}")
        return False

# ===== Database Models =====
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    scans = db.relationship('Scan', backref='user', lazy=True)

class Scan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    target = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(20), default='pending')
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    results = db.Column(db.Text)
    summary = db.Column(db.Text)
    recon_data = db.Column(db.Text)  # تخزين نتائج الـ Recon

class VulnerabilityInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20), nullable=False)
    impact = db.Column(db.Text, nullable=False)
    remediation = db.Column(db.Text, nullable=False)
    cwe = db.Column(db.String(20))
    owasp_category = db.Column(db.String(50))

class Vulnerability(db.Model):
    __tablename__ = 'vulnerabilities'
    
    id = db.Column(db.Integer, primary_key=True)
    target = db.Column(db.String(500), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    severity = db.Column(db.String(20), nullable=False)
    payload = db.Column(db.Text)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    confidence = db.Column(db.String(20), default='MEDIUM')
    parameter = db.Column(db.String(100))
    discovery_date = db.Column(db.DateTime, default=datetime.utcnow)
    scan_id = db.Column(db.Integer, db.ForeignKey('scan.id'), nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'target': self.target,
            'type': self.type,
            'severity': self.severity,
            'payload': self.payload,
            'description': self.description,
            'confidence': self.confidence,
            'parameter': self.parameter,
            'discovery_date': self.discovery_date.isoformat() if self.discovery_date else None
        }

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def init_vulnerability_info():
    vulns = [
        {
            'name': 'SQL Injection (SQLi)',
            'description': 'SQL Injection allows attackers to interfere with database queries.',
            'severity': 'CRITICAL',
            'impact': 'Data breach, authentication bypass',
            'remediation': 'Use parameterized queries',
            'cwe': 'CWE-89',
            'owasp_category': 'A03:2021-Injection'
        },
        {
            'name': 'Cross-Site Scripting (XSS)',
            'description': 'XSS enables attackers to inject malicious scripts.',
            'severity': 'HIGH',
            'impact': 'Session theft, account takeover',
            'remediation': 'Validate input, encode output',
            'cwe': 'CWE-79',
            'owasp_category': 'A03:2021-Injection'
        },
        {
            'name': 'Remote Code Execution (RCE)',
            'description': 'RCE allows executing arbitrary code on the server.',
            'severity': 'CRITICAL',
            'impact': 'Full system compromise',
            'remediation': 'Avoid system calls',
            'cwe': 'CWE-94',
            'owasp_category': 'A03:2021-Injection'
        },
        {
            'name': 'Local File Inclusion (LFI)',
            'description': 'LFI allows reading arbitrary files on the server.',
            'severity': 'HIGH',
            'impact': 'Source code disclosure',
            'remediation': 'Validate file paths',
            'cwe': 'CWE-98',
            'owasp_category': 'A05:2021-Security Misconfiguration'
        },
        {
            'name': 'Server-Side Request Forgery (SSRF)',
            'description': 'SSRF allows making requests to internal systems.',
            'severity': 'HIGH',
            'impact': 'Internal network scanning',
            'remediation': 'Validate URLs',
            'cwe': 'CWE-918',
            'owasp_category': 'A10:2021-SSRF'
        },
        {
            'name': 'Open Redirect',
            'description': 'Open redirect sends users to external URLs.',
            'severity': 'MEDIUM',
            'impact': 'Phishing attacks',
            'remediation': 'Validate redirect URLs',
            'cwe': 'CWE-601',
            'owasp_category': 'A03:2021-Injection'
        },
        {
            'name': 'CORS Misconfiguration',
            'description': 'CORS allows unauthorized domains to access resources.',
            'severity': 'MEDIUM',
            'impact': 'Data theft',
            'remediation': 'Restrict Access-Control-Allow-Origin',
            'cwe': 'CWE-942',
            'owasp_category': 'A05:2021-Security Misconfiguration'
        },
        {
            'name': 'Secrets Exposure',
            'description': 'Exposed API keys and passwords in source code.',
            'severity': 'CRITICAL',
            'impact': 'Account compromise',
            'remediation': 'Remove secrets from code',
            'cwe': 'CWE-312',
            'owasp_category': 'A04:2021-Insecure Design'
        },
        {
            'name': 'XXE',
            'description': 'XXE attacks exploit XML parsers.',
            'severity': 'HIGH',
            'impact': 'File disclosure, SSRF',
            'remediation': 'Disable XML external entities',
            'cwe': 'CWE-611',
            'owasp_category': 'A05:2021-Security Misconfiguration'
        },
        {
            'name': 'SSTI',
            'description': 'SSTI allows template injection.',
            'severity': 'CRITICAL',
            'impact': 'Remote code execution',
            'remediation': 'Sandbox templates',
            'cwe': 'CWE-1336',
            'owasp_category': 'A03:2021-Injection'
        },
        {
            'name': 'IDOR',
            'description': 'IDOR allows unauthorized access to objects.',
            'severity': 'HIGH',
            'impact': 'Unauthorized data access',
            'remediation': 'Implement proper access controls',
            'cwe': 'CWE-639',
            'owasp_category': 'A01:2021-Broken Access Control'
        },
        {
            'name': 'Subdomain Takeover',
            'description': 'Subdomain takeover from unused services.',
            'severity': 'HIGH',
            'impact': 'Phishing, malware hosting',
            'remediation': 'Remove unused DNS records',
            'cwe': 'CWE-840',
            'owasp_category': 'A05:2021-Security Misconfiguration'
        },
        {
            'name': 'WordPress Vulnerabilities',
            'description': 'WordPress-specific vulnerabilities.',
            'severity': 'MEDIUM',
            'impact': 'Site defacement',
            'remediation': 'Keep WordPress updated',
            'cwe': 'CWE-200',
            'owasp_category': 'A05:2021-Security Misconfiguration'
        }
    ]
    
    for vuln in vulns:
        if not VulnerabilityInfo.query.filter_by(name=vuln['name']).first():
            v = VulnerabilityInfo(**vuln)
            db.session.add(v)
    db.session.commit()

# ===== Routes =====
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('signup'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('signup'))
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('dashboard'))
    
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    scans = Scan.query.filter_by(user_id=current_user.id).order_by(Scan.start_time.desc()).limit(10).all()
    return render_template('dashboard.html', scans=scans)

@app.route('/vulnerabilities')
@login_required
def vulnerabilities_list():
    return render_template('vulnerabilities.html')

@app.route('/api/test')
def test_api():
    return jsonify({'status': 'ok', 'message': 'API is working'})

@app.route('/api/vulnerabilities')
@login_required
def get_vulnerabilities():
    vulns = Vulnerability.query.filter_by(user_id=current_user.id).order_by(Vulnerability.discovery_date.desc()).all()
    return jsonify([v.to_dict() for v in vulns])

@app.route('/api/vulnerabilities/info')
def get_vulnerabilities_info():
    vulns = VulnerabilityInfo.query.all()
    return jsonify([{
        'id': v.id,
        'name': v.name,
        'description': v.description,
        'severity': v.severity,
        'impact': v.impact,
        'remediation': v.remediation,
        'cwe': v.cwe,
        'owasp': v.owasp_category
    } for v in vulns])

@app.route('/api/vulnerabilities/detailed')
@login_required
def get_detailed_vulnerabilities():
    vulns = [
        {
            'name': 'SQL Injection (SQLi)',
            'severity': 'CRITICAL',
            'description': 'SQL Injection allows attackers to interfere with database queries.',
            'payloads': [
                {'value': "' OR '1'='1", 'description': 'Basic authentication bypass'},
                {'value': "' UNION SELECT NULL--", 'description': 'Union-based data extraction'},
                {'value': "'; WAITFOR DELAY '00:00:05'--", 'description': 'Time-based blind SQLi'},
                {'value': "' AND SLEEP(5)--", 'description': 'MySQL time-based detection'}
            ],
            'remediation': 'Use parameterized queries and input validation',
            'example': "https://example.com/page?id=1' OR '1'='1"
        },
        {
            'name': 'Cross-Site Scripting (XSS)',
            'severity': 'HIGH',
            'description': 'XSS allows attackers to inject malicious scripts into web pages.',
            'payloads': [
                {'value': '<script>alert(1)</script>', 'description': 'Basic script injection'},
                {'value': '<img src=x onerror=alert(1)>', 'description': 'Image tag XSS'},
                {'value': 'javascript:alert(1)', 'description': 'JavaScript protocol XSS'},
                {'value': '"><svg/onload=alert(1)>', 'description': 'SVG XSS'}
            ],
            'remediation': 'Validate and encode all user input',
            'example': "https://example.com/search?q=<script>alert(1)</script>"
        },
        {
            'name': 'Remote Code Execution (RCE)',
            'severity': 'CRITICAL',
            'description': 'RCE allows attackers to execute arbitrary code on the server.',
            'payloads': [
                {'value': ';id', 'description': 'Command injection (Linux)'},
                {'value': '&&whoami', 'description': 'Command chaining'},
                {'value': '| cat /etc/passwd', 'description': 'Pipe command execution'},
                {'value': '`uname -a`', 'description': 'Backtick execution'}
            ],
            'remediation': 'Avoid system calls, use safe APIs',
            'example': "https://example.com/ping?host=127.0.0.1;id"
        },
        {
            'name': 'Local File Inclusion (LFI)',
            'severity': 'HIGH',
            'description': 'LFI allows attackers to read arbitrary files on the server.',
            'payloads': [
                {'value': '../../../../etc/passwd', 'description': 'Basic path traversal'},
                {'value': '....//....//....//etc/passwd', 'description': 'WAF bypass'},
                {'value': '/etc/passwd', 'description': 'Absolute path'},
                {'value': '..\\..\\..\\windows\\win.ini', 'description': 'Windows file'}
            ],
            'remediation': 'Validate file paths, use whitelist',
            'example': "https://example.com/view?file=../../../../etc/passwd"
        },
        {
            'name': 'Server-Side Request Forgery (SSRF)',
            'severity': 'HIGH',
            'description': 'SSRF allows attackers to make requests from the server to internal systems.',
            'payloads': [
                {'value': 'http://127.0.0.1:80', 'description': 'Localhost access'},
                {'value': 'http://169.254.169.254/latest/meta-data/', 'description': 'AWS metadata'},
                {'value': 'http://[::1]:80', 'description': 'IPv6 localhost'},
                {'value': 'file:///etc/passwd', 'description': 'File protocol'}
            ],
            'remediation': 'Validate and whitelist URLs',
            'example': "https://example.com/fetch?url=http://169.254.169.254/latest/meta-data/"
        },
        {
            'name': 'Open Redirect',
            'severity': 'MEDIUM',
            'description': 'Open redirect allows attackers to redirect users to malicious sites.',
            'payloads': [
                {'value': 'https://evil.com', 'description': 'External redirect'},
                {'value': '//evil.com', 'description': 'Protocol-relative'},
                {'value': 'https://evil.com@google.com', 'description': 'Credential confusion'},
                {'value': 'https://evil.com/..', 'description': 'Path traversal'}
            ],
            'remediation': 'Validate redirect URLs',
            'example': "https://example.com/redirect?url=https://evil.com"
        },
        {
            'name': 'CORS Misconfiguration',
            'severity': 'MEDIUM',
            'description': 'CORS misconfiguration allows unauthorized domains to access resources.',
            'payloads': [
                {'value': 'Origin: https://evil.com', 'description': 'Test with evil origin'},
                {'value': 'Origin: null', 'description': 'Test with null origin'},
                {'value': 'Origin: https://attacker.com', 'description': 'Custom origin'},
                {'value': 'Origin: *', 'description': 'Wildcard test'}
            ],
            'remediation': 'Restrict Access-Control-Allow-Origin',
            'example': "Add Origin header to request"
        },
        {
            'name': 'Secrets Exposure',
            'severity': 'CRITICAL',
            'description': 'Exposed secrets like API keys and passwords in source code.',
            'payloads': [
                {'value': 'Check .env files', 'description': 'Environment files'},
                {'value': 'Search for API keys', 'description': 'Pattern: AIza, AKIA'},
                {'value': 'Check JavaScript files', 'description': 'Hardcoded tokens'},
                {'value': 'Look for JWT tokens', 'description': 'JWT format: eyJ...'}
            ],
            'remediation': 'Remove secrets from code',
            'example': "https://example.com/.env"
        },
        {
            'name': 'XXE (XML External Entity)',
            'severity': 'HIGH',
            'description': 'XXE attacks exploit XML parsers to read files or cause SSRF.',
            'payloads': [
                {'value': '<?xml version="1.0"?><!DOCTYPE root [<!ENTITY test SYSTEM "file:///etc/passwd">]><root>&test;</root>', 'description': 'File read'},
                {'value': '<?xml version="1.0"?><!DOCTYPE root [<!ENTITY test SYSTEM "http://169.254.169.254/latest/meta-data/">]><root>&test;</root>', 'description': 'SSRF via XXE'}
            ],
            'remediation': 'Disable external entity processing',
            'example': "POST XML data with Content-Type: application/xml"
        },
        {
            'name': 'SSTI (Server-Side Template Injection)',
            'severity': 'CRITICAL',
            'description': 'SSTI allows injection into template engines for RCE.',
            'payloads': [
                {'value': '{{7*7}}', 'description': 'Jinja2/Twig calculation'},
                {'value': '${7*7}', 'description': 'Freemarker'},
                {'value': '{{999*999}}', 'description': 'Look for 998001'},
                {'value': '<%= 7*7 %>', 'description': 'ERB'}
            ],
            'remediation': 'Sandbox templates',
            'example': "https://example.com/page?name={{7*7}}"
        },
        {
            'name': 'IDOR (Insecure Direct Object References)',
            'severity': 'HIGH',
            'description': 'IDOR allows access to unauthorized objects by changing IDs.',
            'payloads': [
                {'value': 'id=2 instead of id=1', 'description': 'Change numeric ID'},
                {'value': 'user_id=admin', 'description': 'Try string values'},
                {'value': 'file=../../etc/passwd', 'description': 'Path traversal'},
                {'value': '?id=1&id=2', 'description': 'Parameter pollution'}
            ],
            'remediation': 'Implement proper access controls',
            'example': "https://example.com/profile?id=2 (while logged in as user 1)"
        },
        {
            'name': 'Subdomain Takeover',
            'severity': 'HIGH',
            'description': 'Subdomain takeover occurs when a subdomain points to an unused service.',
            'payloads': [
                {'value': 'Check CNAME records', 'description': 'Find dangling CNAMEs'},
                {'value': 'Try to claim the service', 'description': 'Register on cloud platform'},
                {'value': 'Look for error pages', 'description': 'NoSuchBucket, 404'},
                {'value': 'Check GitHub Pages', 'description': '.github.io'}
            ],
            'remediation': 'Remove unused DNS records',
            'example': "subdomain.example.com -> s3.amazonaws.com (unused bucket)"
        },
        {
            'name': 'WordPress Vulnerabilities',
            'severity': 'MEDIUM',
            'description': 'WordPress-specific vulnerabilities.',
            'payloads': [
                {'value': '/wp-admin/', 'description': 'Admin panel exposure'},
                {'value': '/wp-config.php', 'description': 'Config file exposure'},
                {'value': '/xmlrpc.php', 'description': 'XML-RPC enabled'},
                {'value': '/wp-content/plugins/', 'description': 'Plugin enumeration'}
            ],
            'remediation': 'Keep WordPress updated',
            'example': "https://example.com/wp-admin/"
        }
    ]
    return jsonify(vulns)

@app.route('/api/email/config', methods=['POST'])
@login_required
def save_email_config():
    data = request.json
    user_email_config[current_user.id] = {
        'enabled': data.get('enabled', False),
        'email': data.get('email', ''),
        'password': data.get('password', '')
    }
    return jsonify({'status': 'success'})

@app.route('/api/email/status')
@login_required
def get_email_status():
    config = user_email_config.get(current_user.id, {'enabled': False})
    return jsonify(config)

@app.route('/api/scan', methods=['POST'])
@login_required
def start_scan():
    data = request.json
    target = data.get('target')
    
    # فك ترميز HTML entities إذا وجدت (للأمان)
    if target:
        target = html.unescape(target).strip()
    
    cookies_input = data.get('cookies', '')
    
    cookies = {}
    if cookies_input:
        for cookie in cookies_input.split(';'):
            if '=' in cookie:
                key, value = cookie.strip().split('=', 1)
                cookies[key] = value
    
    logger.debug(f"Starting scan for target: {target}")
    logger.debug(f"Cookies: {cookies}")
    
    scan = Scan(
        user_id=current_user.id,
        target=target,
        status='pending'
    )
    db.session.add(scan)
    db.session.commit()
    
    logger.debug(f"Scan record created with ID: {scan.id}")
    
    thread = threading.Thread(target=run_scan, args=(scan.id, target, cookies))
    thread.daemon = True
    thread.start()
    
    return jsonify({'scan_id': scan.id, 'status': 'started'})

def run_scan(scan_id, target, cookies):
    with app.app_context():
        scan = Scan.query.get(scan_id)
        scan.status = 'running'
        db.session.commit()
        
        try:
            logger.debug("="*50)
            logger.debug(f"Starting scan for target: {target}")
            logger.debug(f"Scan ID: {scan_id}")
            logger.debug(f"Cookies: {cookies}")
            logger.debug("="*50)
            
            # استخراج الدومين الأساسي للأدوات
            parsed = urlparse(target)
            domain = parsed.netloc if parsed.netloc else target
            domain = domain.replace('www.', '')
            
            # ===== المرحلة الأولى: تشغيل أدوات الـ Recon الخارجية =====
            print(f"\n{Y}{'='*60}{W}")
            print(f"{Y}[*] PHASE 1: Running External Recon Tools{W}")
            print(f"{Y}{'='*60}{W}")
            
            recon_data = {}
            
            # 1. Subfinder - اكتشاف النطاقات الفرعية
            print(f"{B}[*] Running Subfinder on {domain}...{W}")
            sub_out = run_external_tool(SUBFINDER_EXE, ['-d', domain, '-silent'])
            subdomains = [line.strip() for line in sub_out.split('\n') if line.strip()] if sub_out else []
            recon_data['subdomains'] = subdomains[:50]  # حفظ أول 50 فقط
            print(f"{G}[+] Subfinder found {len(subdomains)} subdomains{W}")
            
            # 2. GAU - جلب الروابط من الأرشيف
            print(f"{B}[*] Running GAU on {domain}...{W}")
            gau_out = run_external_tool(GAU_EXE, [domain, '--subs', '--limit', '50'])
            gau_urls = [line.strip() for line in gau_out.split('\n') if line.strip()] if gau_out else []
            recon_data['gau_urls'] = gau_urls[:30]  # حفظ أول 30 فقط
            print(f"{G}[+] GAU found {len(gau_urls)} archived URLs{W}")
            
            # 3. Katana - Crawling وجلب الـ Endpoints
            print(f"{B}[*] Running Katana on {target}...{W}")
            katana_out = run_external_tool(KATANA_EXE, ['-u', target, '-silent', '-f', 'qurl', '-d', '2', '-c', '50'])
            katana_urls = [line.strip() for line in katana_out.split('\n') if line.strip()] if katana_out else []
            recon_data['katana_urls'] = katana_urls[:30]  # حفظ أول 30 فقط
            print(f"{G}[+] Katana found {len(katana_urls)} endpoints{W}")
            
            # حفظ نتائج الـ Recon في قاعدة البيانات
            scan.recon_data = json.dumps(recon_data)
            db.session.commit()
            
            print(f"{G}[+] Recon Phase Completed! Found {len(subdomains)} subdomains, {len(gau_urls)} archived URLs, {len(katana_urls)} endpoints{W}")
            
            # ===== المرحلة الثانية: فحص الثغرات =====
            print(f"\n{Y}{'='*60}{W}")
            print(f"{Y}[*] PHASE 2: Starting Vulnerability Scanner{W}")
            print(f"{Y}{'='*60}{W}")
            
            # جمع كل الروابط التي سنفحصها
            all_urls_to_scan = [target]  # نبدأ بالرابط الأصلي
            
            # إضافة روابط Katana (الـ endpoints) للفحص
            if katana_urls and len(katana_urls) > 0:
                print(f"{B}[*] Adding {len(katana_urls)} endpoints from Katana to scan list{W}")
                all_urls_to_scan.extend(katana_urls)
            
            # إضافة روابط GAU للفحص (اختياري - نأخذ أول 10 فقط)
            if gau_urls and len(gau_urls) > 0:
                print(f"{B}[*] Adding {min(10, len(gau_urls))} archived URLs from GAU to scan list{W}")
                all_urls_to_scan.extend(gau_urls[:10])
            
            print(f"{G}[+] Total URLs to scan: {len(all_urls_to_scan)}{W}")
            
            # Discover origin IP if domain
            origin_ips = []
            if parsed.netloc:
                logger.debug(f"Discovering origin IP for: {parsed.netloc}")
                try:
                    origin_ips = AdvancedWAFBypassV2.discover_origin_ip(parsed.netloc)
                    logger.debug(f"Found origin IPs: {origin_ips}")
                except Exception as e:
                    logger.error(f"Error discovering origin IP: {e}")
            
            # فحص كل رابط
            all_results = []
            scanned_count = 0
            vuln_count = 0
            
            for url_to_scan in all_urls_to_scan:
                scanned_count += 1
                print(f"\n{C}{'='*50}{W}")
                print(f"{C}[{scanned_count}/{len(all_urls_to_scan)}] Scanning: {url_to_scan}{W}")
                print(f"{C}{'='*50}{W}")
                
                try:
                    # Initialize scanner with cookies and database session
                    scanner = AdvancedScanner(
                        target=url_to_scan,
                        cookies=cookies,
                        db_session=db.session,
                        VulnerabilityModel=Vulnerability,
                        user_id=scan.user_id
                    )
                    
                    # Run the scan on this URL
                    results = scanner.scan_url(url_to_scan)
                    
                    if results and len(results) > 0:
                        all_results.extend(results)
                        vuln_count += len(results)
                        print(f"{G}[+] Found {len(results)} vulnerabilities on {url_to_scan}{W}")
                    
                except Exception as e:
                    print(f"{R}[!] Error scanning {url_to_scan}: {str(e)}{W}")
                    continue
            
            # Generate summary
            summary = {
                'total': len(all_results) if all_results else 0,
                'critical': sum(1 for r in all_results if r.get('severity') == 'CRITICAL') if all_results else 0,
                'high': sum(1 for r in all_results if r.get('severity') == 'HIGH') if all_results else 0,
                'medium': sum(1 for r in all_results if r.get('severity') == 'MEDIUM') if all_results else 0,
                'low': sum(1 for r in all_results if r.get('severity') == 'LOW') if all_results else 0,
                'info': sum(1 for r in all_results if r.get('severity') == 'INFO') if all_results else 0,
                'origin_ips': origin_ips,
                'recon_summary': {
                    'subdomains': len(subdomains),
                    'gau_urls': len(gau_urls),
                    'katana_urls': len(katana_urls)
                },
                'scan_summary': {
                    'total_urls_scanned': scanned_count,
                    'vulnerable_urls': len(set([r.get('url') for r in all_results if r])) if all_results else 0
                }
            }
            
            logger.debug(f"Summary generated: {summary}")
            
            # Update scan record
            scan.status = 'completed'
            scan.end_time = datetime.utcnow()
            scan.results = json.dumps(all_results) if all_results else json.dumps([])
            scan.summary = json.dumps(summary)
            db.session.commit()
            
            logger.debug("Scan record updated successfully")
            logger.debug(f"Results saved: {len(all_results) if all_results else 0} vulnerabilities from {scanned_count} URLs")
            
            # Send email if configured
            user_config = user_email_config.get(scan.user_id, {})
            if user_config.get('enabled'):
                logger.debug("Sending email report...")
                report_data = {
                    'target': target,
                    'scan_time': scan.end_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'summary': summary,
                    'vulnerabilities': all_results if all_results else []
                }
                email_thread = threading.Thread(
                    target=send_vulnerability_report,
                    args=(scan_id, User.query.get(scan.user_id).email, report_data, user_config)
                )
                email_thread.daemon = True
                email_thread.start()
            
        except Exception as e:
            logger.error("!"*50)
            logger.error(f"SCAN FAILED WITH ERROR: {str(e)}")
            logger.error(traceback.format_exc())
            logger.error("!"*50)
            
            scan.status = 'failed'
            scan.end_time = datetime.utcnow()
            scan.results = json.dumps({'error': str(e), 'traceback': traceback.format_exc()})
            db.session.commit()

@app.route('/api/scan/<int:scan_id>')
@login_required
def get_scan(scan_id):
    scan = Scan.query.get_or_404(scan_id)
    if scan.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({
        'id': scan.id,
        'target': scan.target,
        'status': scan.status,
        'start_time': scan.start_time.isoformat() if scan.start_time else None,
        'end_time': scan.end_time.isoformat() if scan.end_time else None,
        'results': json.loads(scan.results) if scan.results else [],
        'summary': json.loads(scan.summary) if scan.summary else {},
        'recon_data': json.loads(scan.recon_data) if scan.recon_data else {}
    })

@app.route('/api/debug/scan/<int:scan_id>')
@login_required
def debug_scan(scan_id):
    scan = Scan.query.get_or_404(scan_id)
    if scan.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({
        'id': scan.id,
        'target': scan.target,
        'status': scan.status,
        'start_time': str(scan.start_time) if scan.start_time else None,
        'end_time': str(scan.end_time) if scan.end_time else None,
        'results': json.loads(scan.results) if scan.results else None,
        'summary': json.loads(scan.summary) if scan.summary else None,
        'recon_data': json.loads(scan.recon_data) if scan.recon_data else None
    })

@app.route('/api/debug/last-scan')
@login_required
def debug_last_scan():
    """جلب آخر scan للمستخدم الحالي مع تفاصيل الخطأ"""
    scan = Scan.query.filter_by(user_id=current_user.id).order_by(Scan.start_time.desc()).first()
    if not scan:
        return jsonify({'error': 'No scans found'}), 404
    
    return jsonify({
        'id': scan.id,
        'target': scan.target,
        'status': scan.status,
        'start_time': str(scan.start_time) if scan.start_time else None,
        'end_time': str(scan.end_time) if scan.end_time else None,
        'results': json.loads(scan.results) if scan.results else None,
        'summary': json.loads(scan.summary) if scan.summary else None,
        'recon_data': json.loads(scan.recon_data) if scan.recon_data else None
    })

@app.route('/api/debug/last-error')
@login_required
def debug_last_error():
    """جلب آخر خطأ للمستخدم الحالي"""
    scan = Scan.query.filter_by(user_id=current_user.id).order_by(Scan.start_time.desc()).first()
    if not scan:
        return jsonify({'error': 'No scans found'}), 404
    
    return jsonify({
        'id': scan.id,
        'target': scan.target,
        'status': scan.status,
        'results': json.loads(scan.results) if scan.results else None
    })

@app.route('/api/ai/ask', methods=['POST'])
@login_required
def ask_ai():
    data = request.json
    question = data.get('question')
    
    responses = {
        'sql': 'SQL Injection (SQLi) test with: \' OR \'1\'=\'1, sleep(5)',
        'xss': 'XSS test with: <script>alert(1)</script>, <img src=x onerror=alert(1)>',
        'rce': 'RCE test with: ;id, &&whoami, | cat /etc/passwd',
        'lfi': 'LFI test with: ../../../../etc/passwd',
        'ssrf': 'SSRF test with: http://127.0.0.1, http://169.254.169.254/latest/meta-data/',
        'open redirect': 'Open Redirect test with: ?redirect=https://evil.com',
        'cors': 'CORS test with Origin: https://evil.com header',
        'secrets': 'Check .env files, JavaScript files for API keys',
        'xxe': 'XXE test with XML containing external entities',
        'ssti': 'SSTI test with: {{7*7}}, ${7*7}',
        'idor': 'IDOR test: change IDs in parameters (id=1 to id=2)',
        'subdomain': 'Check CNAME records for dangling services',
        'wordpress': 'Check /wp-admin/, /wp-config.php, /xmlrpc.php'
    }
    
    response = "Ask about specific vulnerabilities like SQLi, XSS, RCE, etc."
    
    question_lower = question.lower()
    for key, answer in responses.items():
        if key in question_lower:
            response = answer
            break
    
    return jsonify({'response': response, 'question': question})

@app.route('/api/recon/<domain>')
@login_required
def recon_info(domain):
    try:
        # 1. اكتشاف الـ Origin IP (من ملف المحرك بتاعك)
        origin_ips = AdvancedWAFBypassV2.discover_origin_ip(domain)
        
        return jsonify({
            'status': 'success',
            'domain': domain,
            'origin_ips': origin_ips
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    # 1. تهيئة قاعدة البيانات قبل التشغيل
    with app.app_context():
        db.create_all()
        init_vulnerability_info()
        print(f"{G}[+] Database initialized locally.{W}")
    
    # 2. تشغيل السيرفر (تأكد من عدم وجود return بعد هذا السطر)
    print(f"{G}[+] Dashboard running on http://127.0.0.1:5000{W}")
    app.run(debug=True, port=5000)