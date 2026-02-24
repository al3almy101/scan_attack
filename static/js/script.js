// ===== Global Variables (تعريف مرة واحدة فقط) =====
let currentScanId = null;
let scanInterval = null;
let scanResults = [];

// ===== Sanitize Input for DISPLAY ONLY (لا تستخدم للإرسال) =====
function sanitizeForDisplay(input) {
    if (!input) return '';
    return String(input)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#x27;')
        .replace(/`/g, '&#96;')
        .replace(/\$/g, '&#36;')
        .replace(/\(/g, '&#40;')
        .replace(/\)/g, '&#41;');
}

// ===== Original Input for SENDING (لا تعدل الرابط) =====
function getOriginalInput(input) {
    return input ? String(input).trim() : '';
}

// ===== Terminal Functions =====
function addTerminalLine(text, type = 'normal') {
    const terminal = document.getElementById('terminal');
    if (!terminal) return;
    
    const sanitizedText = sanitizeForDisplay(text);
    
    const line = document.createElement('div');
    line.classList.add('terminal-line');
    if (type !== 'normal') {
        line.classList.add(type);
    }
    const timestamp = new Date().toLocaleTimeString();
    line.textContent = `[${timestamp}] ${sanitizedText}`;
    terminal.appendChild(line);
    terminal.scrollTop = terminal.scrollHeight;
}

function clearTerminal() {
    const terminal = document.getElementById('terminal');
    if (terminal) {
        terminal.innerHTML = '';
    }
}

// ===== Debug Last Scan =====
async function debugLastScan() {
    try {
        const response = await fetch('/api/debug/last-scan');
        const data = await response.json();
        console.log('Last Scan Debug Info:', data);
        
        if (data.results && data.results.error) {
            console.error('Scan Error:', data.results.error);
            console.error('Traceback:', data.results.traceback);
            addTerminalLine(`❌ Scan error: ${data.results.error}`, 'error');
        }
        
        return data;
    } catch (error) {
        console.error('Debug error:', error);
    }
}

// ===== Check Scan Status =====
async function checkScanStatus(scanId) {
    try {
        const response = await fetch(`/api/scan/${scanId}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.status === 'running') {
            addTerminalLine('⚡ Scan in progress...', 'normal');
            
        } else if (data.status === 'completed') {
            if (scanInterval) {
                clearInterval(scanInterval);
                scanInterval = null;
            }
            
            addTerminalLine('✅ Scan completed successfully!', 'success');
            
            scanResults = data.results || [];
            displayResults(data);
            
            document.getElementById('scan-progress').style.display = 'none';
            document.getElementById('scan-results').style.display = 'block';
            
            addTerminalLine(`📊 Found ${scanResults.length} vulnerabilities`, 'success');
            
        } else if (data.status === 'failed') {
            if (scanInterval) {
                clearInterval(scanInterval);
                scanInterval = null;
            }
            
            addTerminalLine('❌ Scan failed!', 'error');
            
            document.getElementById('scan-progress').style.display = 'none';
            document.getElementById('scan-form').style.display = 'block';
            
            debugLastScan();
        }
        
    } catch (error) {
        console.error('Error checking scan status:', error);
        addTerminalLine(`⚠️ Status check error`, 'warning');
    }
}

// ===== Display Results =====
function displayResults(data) {
    const results = data.results || [];
    const summary = data.summary || {};
    
    document.getElementById('total-vulns').textContent = results.length;
    document.getElementById('critical-count').textContent = summary.critical || 0;
    document.getElementById('high-count').textContent = summary.high || 0;
    document.getElementById('medium-count').textContent = summary.medium || 0;
    
    if (summary.origin_ips && summary.origin_ips.length > 0) {
        const ipList = document.getElementById('origin-ips');
        ipList.innerHTML = '';
        summary.origin_ips.forEach(ip => {
            const li = document.createElement('li');
            li.textContent = sanitizeForDisplay(ip);
            ipList.appendChild(li);
        });
        document.getElementById('origin-ips-container').style.display = 'block';
    }
    
    const vulnList = document.getElementById('vuln-list');
    vulnList.innerHTML = '';
    
    if (results.length === 0) {
        vulnList.innerHTML = '<div class="alert alert-success">No vulnerabilities found!</div>';
        return;
    }
    
    results.forEach(vuln => {
        const card = document.createElement('div');
        card.classList.add('card', 'vuln-card');
        card.setAttribute('data-severity', (vuln.severity || 'INFO').toUpperCase());
        
        const vulnType = sanitizeForDisplay(vuln.type || 'Unknown');
        const vulnSeverity = sanitizeForDisplay(vuln.severity || 'INFO');
        const vulnUrl = sanitizeForDisplay(vuln.url || 'N/A');
        const vulnParam = vuln.param ? sanitizeForDisplay(vuln.param) : null;
        const vulnPayload = vuln.payload ? sanitizeForDisplay(vuln.payload.substring(0, 50)) : null;
        const vulnConfidence = sanitizeForDisplay(vuln.confidence || 'MEDIUM');
        
        let details = '';
        if (vuln.details) {
            details = '<div class="vuln-details">';
            for (const [key, value] of Object.entries(vuln.details)) {
                if (value) {
                    const safeKey = sanitizeForDisplay(key);
                    let safeValue;
                    try {
                        safeValue = sanitizeForDisplay(JSON.stringify(value).substring(0, 50));
                    } catch {
                        safeValue = sanitizeForDisplay(String(value).substring(0, 50));
                    }
                    details += `<p><small>${safeKey}: ${safeValue}</small></p>`;
                }
            }
            details += '</div>';
        }
        
        card.innerHTML = `
            <div class="vuln-header">
                <h3>${vulnType}</h3>
                <span class="badge badge-${vulnSeverity.toLowerCase()}">${vulnSeverity}</span>
            </div>
            <div class="vuln-body">
                <p><strong>URL:</strong> ${vulnUrl}</p>
                ${vulnParam ? `<p><strong>Parameter:</strong> ${vulnParam}</p>` : ''}
                ${vulnPayload ? `<p><strong>Payload:</strong> <code>${vulnPayload}...</code></p>` : ''}
                <p><strong>Confidence:</strong> ${vulnConfidence}</p>
                ${details}
            </div>
        `;
        
        vulnList.appendChild(card);
        addTerminalLine(`🔍 Found ${vulnType} - ${vulnSeverity} on ${vulnUrl}`, vulnSeverity.toLowerCase());
    });
}

// ===== Start Scan =====
async function startScan() {
    console.log('Start scan clicked');
    const targetInput = document.getElementById('target').value;
    const cookiesInput = document.getElementById('cookies').value;
    
    console.log('Target:', targetInput);
    console.log('Cookies:', cookiesInput);
    
    if (!targetInput) {
        alert('Please enter a target URL');
        return;
    }
    
    // IMPORTANT: Use original input for sending, NOT sanitized
    const target = getOriginalInput(targetInput);
    const cookies = getOriginalInput(cookiesInput);
    
    document.getElementById('scan-form').style.display = 'none';
    document.getElementById('scan-progress').style.display = 'block';
    document.getElementById('scan-results').style.display = 'none';
    
    clearTerminal();
    
    addTerminalLine(`🚀 Starting scan on target: ${target}`, 'success');
    
    if (cookies) {
        addTerminalLine(`🍪 Cookies provided`, 'normal');
    }
    
    try {
        const response = await fetch('/api/scan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ target, cookies })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        currentScanId = data.scan_id;
        
        addTerminalLine(`✅ Scan initiated with ID: ${currentScanId}`, 'success');
        addTerminalLine(`⏳ Waiting for results...`, 'warning');
        
        if (scanInterval) {
            clearInterval(scanInterval);
        }
        
        scanInterval = setInterval(() => checkScanStatus(currentScanId), 2000);
        
    } catch (error) {
        console.error('Error starting scan:', error);
        addTerminalLine(`❌ Error: ${sanitizeForDisplay(error.message)}`, 'error');
        
        document.getElementById('scan-form').style.display = 'block';
        document.getElementById('scan-progress').style.display = 'none';
    }
}

// ===== Email Configuration =====
async function loadEmailConfig() {
    try {
        const response = await fetch('/api/email/status');
        
        if (!response.ok) {
            throw new Error('Failed to load config');
        }
        
        const config = await response.json();
        
        const toggle = document.getElementById('email-toggle');
        const configDiv = document.getElementById('email-config');
        const emailInput = document.getElementById('email-address');
        
        if (toggle) toggle.checked = config.enabled;
        if (configDiv) configDiv.style.display = config.enabled ? 'block' : 'none';
        if (emailInput && config.email) emailInput.value = sanitizeForDisplay(config.email);
        
    } catch (error) {
        console.error('Error loading email config:', error);
    }
}

async function saveEmailConfig() {
    const enabled = document.getElementById('email-toggle')?.checked || false;
    const email = document.getElementById('email-address')?.value || '';
    const password = document.getElementById('email-password')?.value || '';
    
    if (enabled && (!email || !password)) {
        alert('Please fill in all fields');
        return;
    }
    
    try {
        const response = await fetch('/api/email/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ enabled, email, password })
        });
        
        if (!response.ok) {
            throw new Error('Failed to save settings');
        }
        
        alert('Email settings saved successfully!');
        
    } catch (error) {
        console.error('Error saving email config:', error);
        alert('Error saving settings');
    }
}

// ===== Load Vulnerability Info =====
async function loadVulnerabilityInfo() {
    try {
        const response = await fetch('/api/vulnerabilities/detailed');
        
        if (!response.ok) {
            throw new Error('Failed to load vulnerabilities');
        }
        
        const vulns = await response.json();
        
        const container = document.getElementById('vuln-info-list');
        if (!container) return;
        
        container.innerHTML = '';
        
        vulns.slice(0, 6).forEach(vuln => {
            const card = document.createElement('div');
            card.classList.add('card', 'vuln-info-card');
            
            const vulnName = sanitizeForDisplay(vuln.name);
            const vulnSeverity = sanitizeForDisplay(vuln.severity);
            const vulnDesc = sanitizeForDisplay(vuln.description.substring(0, 80));
            const vulnPayload = vuln.payloads && vuln.payloads[0] ? sanitizeForDisplay(vuln.payloads[0].value) : '';
            
            card.innerHTML = `
                <span class="badge badge-${vulnSeverity.toLowerCase()}">${vulnSeverity}</span>
                <h3>${vulnName}</h3>
                <p>${vulnDesc}...</p>
                <div class="vuln-payloads">
                    <h4>Example:</h4>
                    <code>${vulnPayload}</code>
                </div>
            `;
            
            container.appendChild(card);
        });
        
    } catch (error) {
        console.error('Error loading vuln info:', error);
    }
}

// ===== AI Chat =====
function initAIChat() {
    const input = document.getElementById('chat-input');
    const sendBtn = document.getElementById('chat-send');
    const messages = document.getElementById('chat-messages');
    
    if (!input || !sendBtn || !messages) return;
    
    addChatMessage('Hello! Ask me about any vulnerability (SQLi, XSS, RCE, etc.)', 'ai');
    
    sendBtn.addEventListener('click', async () => {
        const question = input.value.trim();
        if (!question) return;
        
        addChatMessage(sanitizeForDisplay(question), 'user');
        input.value = '';
        
        try {
            const response = await fetch('/api/ai/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question })
            });
            
            if (!response.ok) {
                throw new Error('Failed to get response');
            }
            
            const data = await response.json();
            addChatMessage(sanitizeForDisplay(data.response), 'ai');
            
        } catch (error) {
            console.error('Error in AI chat:', error);
            addChatMessage('Sorry, I encountered an error.', 'ai');
        }
    });
    
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendBtn.click();
        }
    });
}

function addChatMessage(text, sender) {
    const messages = document.getElementById('chat-messages');
    if (!messages) return;
    
    const div = document.createElement('div');
    div.classList.add('chat-message', sender);
    div.innerHTML = `<div class="message-content">${text}</div>`;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
}

function logout() {
    window.location.href = '/logout';
}

// ===== Initialize on Page Load =====
document.addEventListener('DOMContentLoaded', function() {
    // Test API connection
    fetch('/api/test')
        .then(response => response.json())
        .then(data => console.log('API Test:', data))
        .catch(error => console.error('API Test Failed:', error));
    
    // Email toggle
    const toggle = document.getElementById('email-toggle');
    if (toggle) {
        toggle.addEventListener('change', function(e) {
            const config = document.getElementById('email-config');
            if (config) {
                config.style.display = e.target.checked ? 'block' : 'none';
            }
        });
    }
    
    // Load email config
    if (document.getElementById('email-toggle')) {
        loadEmailConfig();
    }
    
    // Load vulnerability info
    if (document.getElementById('vuln-info-list')) {
        loadVulnerabilityInfo();
    }
    
    // Initialize AI chat
    if (document.getElementById('chat-messages')) {
        initAIChat();
    }
});

// ===== Clean up on page leave =====
window.addEventListener('beforeunload', function() {
    if (scanInterval) {
        clearInterval(scanInterval);
        scanInterval = null;
    }
});