#!/usr/bin/env python3
"""
Explorer-d334 Mobile-Friendly Enhanced Web Interface
Responsive Dashboard + Chat + Monitoring
"""

import sys
import json
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

sys.path.insert(0, str(Path(__file__).parent))
from simple_trust import SimpleTrust
from device_awareness import DeviceAwareness

class MobileHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML.encode())
        elif self.path == '/api/stats':
            self.send_json(self.get_stats())
        elif self.path == '/api/trust':
            self.send_json(self.get_trust_data())
        elif self.path == '/api/capsules':
            self.send_json(self.get_capsules())
        elif self.path == '/api/sensors':
            self.send_json(self.get_sensors())
        elif self.path == '/api/memories':
            self.send_json(self.get_memories())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/chat':
            length = int(self.headers['Content-Length'])
            data = json.loads(self.rfile.read(length).decode())
            response = self.chat(data.get('message', ''))
            self.send_json({'response': response})
        else:
            self.send_response(404)
            self.end_headers()
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def get_stats(self):
        trust = SimpleTrust()
        all_trust = trust.get_all()
        trust.close()
        memories_count = len(list(Path('memories').rglob('*.json'))) if Path('memories').exists() else 0
        binaries_count = len(list(Path('binaries').glob('*'))) if Path('binaries').exists() else 0
        return {
            'total_capsules': len(all_trust),
            'avg_trust': sum(t[1] for t in all_trust) / len(all_trust) if all_trust else 0,
            'reflex_skills': 5,
            'total_memories': memories_count,
            'total_binaries': binaries_count
        }
    
    def get_trust_data(self):
        trust = SimpleTrust()
        data = [{'name': t[0], 'trust': t[1], 'successes': t[2], 'failures': t[3]} 
                for t in trust.get_all()[:10]]
        trust.close()
        return data
    
    def get_capsules(self):
        capsules_dir = Path('capsules')
        if not capsules_dir.exists():
            return []
        capsules = []
        for cat_dir in capsules_dir.iterdir():
            if cat_dir.is_dir():
                for cap_file in cat_dir.glob('*.json'):
                    capsules.append({'name': cap_file.stem[:40], 'category': cat_dir.name})
        return capsules[:30]
    
    def get_sensors(self):
        device = DeviceAwareness()
        return device.device_info.get('sensors', ['accelerometer', 'gyroscope', 'magnetometer', 'proximity', 'light_sensor', 'barometer', 'fingerprint', 'heart_rate'])
    
    def get_memories(self):
        memories_dir = Path('memories')
        if not memories_dir.exists():
            return []
        memories = []
        for mem_file in memories_dir.rglob('*.json'):
            try:
                with open(mem_file, 'r') as f:
                    data = json.load(f)
                memories.append({'title': data.get('title', 'Untitled')[:50], 'type': data.get('type', 'unknown'), 'timestamp': data.get('timestamp', '')[:19]})
            except:
                pass
        return memories[-15:]
    
    def chat(self, message):
        try:
            from hybrid_llm import HybridLLM
            llm = HybridLLM()
            return llm.respond(message)
        except:
            return "I'm here. What would you like to explore?"

HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes, viewport-fit=cover">
    <meta name="theme-color" content="#0a0a0a">
    <title>Explorer-d334</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', monospace;
            background: #0a0a0a;
            color: #00ffcc;
            min-height: 100vh;
        }
        
        /* Mobile-first responsive design */
        .app {
            display: flex;
            flex-direction: column;
            height: 100vh;
            max-width: 600px;
            margin: 0 auto;
            background: #0a0a0a;
        }
        
        /* Bottom navigation for mobile */
        .bottom-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: #0d0d0d;
            border-top: 1px solid #00ffcc20;
            display: flex;
            justify-content: space-around;
            padding: 8px 0 20px 0;
            z-index: 100;
            backdrop-filter: blur(10px);
        }
        
        .nav-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 4px;
            padding: 8px 12px;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.2s;
            color: #00ffcc50;
            font-size: 0.7em;
            background: none;
            border: none;
            font-family: inherit;
        }
        
        .nav-item span { font-size: 1.5em; }
        
        .nav-item.active {
            color: #00ffcc;
            background: #00ffcc10;
        }
        
        /* Main content area */
        .main {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            padding-bottom: 80px;
            margin-bottom: 60px;
        }
        
        .header {
            padding: 16px;
            border-bottom: 1px solid #00ffcc20;
            margin-bottom: 16px;
        }
        
        .header h1 {
            font-size: 1.5em;
            letter-spacing: 1px;
        }
        
        /* Cards */
        .widget-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            margin-bottom: 16px;
        }
        
        .widget {
            background: #0d0d0d;
            border: 1px solid #00ffcc20;
            border-radius: 16px;
            padding: 16px;
        }
        
        .widget-title {
            font-size: 0.7em;
            color: #00ffcc80;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .widget-value {
            font-size: 1.8em;
            font-weight: bold;
        }
        
        .trust-bar {
            background: #1a1a1a;
            border-radius: 4px;
            height: 6px;
            overflow: hidden;
            margin-top: 8px;
        }
        
        .trust-fill {
            background: #00ffcc;
            height: 100%;
            transition: width 0.3s;
        }
        
        /* Chat */
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        
        .message {
            max-width: 85%;
            animation: fadeIn 0.3s;
        }
        
        .message.user { align-self: flex-end; }
        .message.assistant { align-self: flex-start; }
        
        .message-content {
            padding: 10px 14px;
            border-radius: 18px;
            word-wrap: break-word;
        }
        
        .message.user .message-content {
            background: #00ffcc;
            color: #000;
        }
        
        .message.assistant .message-content {
            background: #1a1a1a;
            border: 1px solid #00ffcc40;
        }
        
        .chat-input {
            display: flex;
            gap: 10px;
            padding: 12px;
            border-top: 1px solid #00ffcc20;
            background: #0a0a0a;
            position: sticky;
            bottom: 0;
        }
        
        .chat-input input {
            flex: 1;
            padding: 12px;
            background: #1a1a1a;
            border: 1px solid #00ffcc40;
            color: #00ffcc;
            border-radius: 25px;
            font-size: 16px;
        }
        
        .chat-input button {
            padding: 12px 20px;
            background: #00ffcc;
            color: #000;
            border: none;
            border-radius: 25px;
            font-weight: bold;
            cursor: pointer;
        }
        
        /* Capsules list */
        .capsule-list {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        
        .capsule-item {
            background: #0d0d0d;
            border: 1px solid #00ffcc20;
            border-radius: 12px;
            padding: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .capsule-name { font-size: 0.9em; font-weight: 500; }
        .capsule-category { font-size: 0.7em; color: #00ffcc80; }
        
        .run-btn {
            background: #00ffcc20;
            border: 1px solid #00ffcc;
            color: #00ffcc;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.8em;
            cursor: pointer;
        }
        
        /* Hide scrollbars on mobile but keep functionality */
        .main::-webkit-scrollbar, .chat-messages::-webkit-scrollbar {
            width: 4px;
        }
        
        .main::-webkit-scrollbar-track, .chat-messages::-webkit-scrollbar-track {
            background: #1a1a1a;
        }
        
        .main::-webkit-scrollbar-thumb, .chat-messages::-webkit-scrollbar-thumb {
            background: #00ffcc50;
            border-radius: 4px;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Loading state */
        .loading {
            opacity: 0.5;
            pointer-events: none;
        }
        
        /* Sensor dots */
        .sensor-dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #00ffcc;
            margin-right: 8px;
            animation: pulse 1.5s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 0.3; }
            50% { opacity: 1; }
        }
        
        /* Responsive adjustments */
        @media (max-width: 480px) {
            .widget-grid {
                grid-template-columns: 1fr;
                gap: 10px;
            }
            .widget-value { font-size: 1.5em; }
            .nav-item { padding: 6px 10px; }
            .nav-item span { font-size: 1.2em; }
        }
    </style>
</head>
<body>
<div class="app">
    <div class="header">
        <h1>🔥 Explorer-d334</h1>
    </div>
    <div class="main" id="main">
        <!-- Dynamic content -->
    </div>
    <div class="bottom-nav">
        <button class="nav-item active" data-view="dashboard">
            <span>📊</span>
            <span>Stats</span>
        </button>
        <button class="nav-item" data-view="chat">
            <span>💬</span>
            <span>Chat</span>
        </button>
        <button class="nav-item" data-view="capsules">
            <span>📦</span>
            <span>Capsules</span>
        </button>
        <button class="nav-item" data-view="trust">
            <span>⭐</span>
            <span>Trust</span>
        </button>
        <button class="nav-item" data-view="sensors">
            <span>📡</span>
            <span>Sensors</span>
        </button>
    </div>
</div>

<script>
    let currentView = 'dashboard';
    
    async function loadView(view) {
        currentView = view;
        document.querySelectorAll('.nav-item').forEach(btn => btn.classList.remove('active'));
        document.querySelector(`[data-view="${view}"]`).classList.add('active');
        
        const main = document.getElementById('main');
        
        if (view === 'dashboard') await loadDashboard();
        else if (view === 'chat') await loadChat();
        else if (view === 'capsules') await loadCapsules();
        else if (view === 'trust') await loadTrust();
        else if (view === 'sensors') await loadSensors();
    }
    
    async function loadDashboard() {
        const res = await fetch('/api/stats');
        const stats = await res.json();
        document.getElementById('main').innerHTML = `
            <div class="widget-grid">
                <div class="widget">
                    <div class="widget-title">📦 Capsules</div>
                    <div class="widget-value">${stats.total_capsules}</div>
                </div>
                <div class="widget">
                    <div class="widget-title">⭐ Avg Trust</div>
                    <div class="widget-value">${(stats.avg_trust * 100).toFixed(0)}%</div>
                    <div class="trust-bar"><div class="trust-fill" style="width: ${stats.avg_trust * 100}%"></div></div>
                </div>
                <div class="widget">
                    <div class="widget-title">🔄 Reflex Skills</div>
                    <div class="widget-value">${stats.reflex_skills}/5</div>
                </div>
                <div class="widget">
                    <div class="widget-title">🧠 Memories</div>
                    <div class="widget-value">${stats.total_memories}</div>
                </div>
            </div>
            <div class="widget">
                <div class="widget-title">💡 Quick Tip</div>
                <p>Try "generate a fibonacci function"</p>
            </div>
        `;
    }
    
    async function loadChat() {
        document.getElementById('main').innerHTML = `
            <div style="display: flex; flex-direction: column; height: calc(100vh - 140px);">
                <div class="chat-messages" id="chatMessages"></div>
                <div class="chat-input">
                    <input type="text" id="chatInput" placeholder="Ask me anything...">
                    <button onclick="sendMessage()">Send</button>
                </div>
            </div>
        `;
        document.getElementById('chatInput').addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });
        loadChatHistory();
    }
    
    function loadChatHistory() {
        const history = JSON.parse(localStorage.getItem('chat_history') || '[]');
        const messagesDiv = document.getElementById('chatMessages');
        messagesDiv.innerHTML = '';
        history.forEach(msg => addMessage(msg.sender, msg.text));
    }
    
    function addMessage(sender, text) {
        const messagesDiv = document.getElementById('chatMessages');
        const div = document.createElement('div');
        div.className = `message ${sender}`;
        div.innerHTML = `<div class="message-content">${escapeHtml(text)}</div>`;
        messagesDiv.appendChild(div);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
    
    function escapeHtml(text) { const d=document.createElement('div'); d.textContent=text; return d.innerHTML; }
    
    async function sendMessage() {
        const input = document.getElementById('chatInput');
        const message = input.value.trim();
        if (!message) return;
        addMessage('user', message);
        input.value = '';
        const res = await fetch('/api/chat', { method: 'POST', body: JSON.stringify({ message: message }) });
        const data = await res.json();
        addMessage('assistant', data.response);
        const history = JSON.parse(localStorage.getItem('chat_history') || '[]');
        history.push({ sender: 'user', text: message }, { sender: 'assistant', text: data.response });
        localStorage.setItem('chat_history', JSON.stringify(history.slice(-50)));
    }
    
    async function loadCapsules() {
        const res = await fetch('/api/capsules');
        const capsules = await res.json();
        let html = '<div class="capsule-list">';
        capsules.forEach(cap => {
            html += `<div class="capsule-item"><div><div class="capsule-name">${cap.name}</div><div class="capsule-category">${cap.category}</div></div><button class="run-btn" onclick="alert('Run ${cap.name} from terminal')">Run</button></div>`;
        });
        html += '</div>';
        document.getElementById('main').innerHTML = html;
    }
    
    async function loadTrust() {
        const res = await fetch('/api/trust');
        const trustData = await res.json();
        let html = '<div class="capsule-list">';
        trustData.forEach(item => {
            html += `<div class="capsule-item"><div><div class="capsule-name">${item.name}</div><div class="capsule-category">Trust: ${(item.trust * 100).toFixed(0)}%</div></div><div class="trust-bar" style="width:80px"><div class="trust-fill" style="width: ${item.trust * 100}%"></div></div></div>`;
        });
        html += '</div>';
        document.getElementById('main').innerHTML = html;
    }
    
    async function loadSensors() {
        const res = await fetch('/api/sensors');
        const sensors = await res.json();
        let html = '<div class="widget-grid">';
        sensors.forEach(sensor => {
            html += `<div class="widget"><div class="widget-title"><span class="sensor-dot"></span>${sensor}</div><div class="widget-value" style="font-size:0.9em">Active</div></div>`;
        });
        html += '</div>';
        document.getElementById('main').innerHTML = html;
    }
    
    // Navigation
    document.querySelectorAll('.nav-item').forEach(btn => {
        btn.addEventListener('click', () => loadView(btn.dataset.view));
    });
    
    loadDashboard();
</script>
</body>
</html>
'''

if __name__ == '__main__':
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     📱 Explorer-d334 Mobile-Friendly Dashboard               ║
║     Visit: http://localhost:8087                            ║
║     Optimized for phones (S24 Ultra)                        ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    HTTPServer(('0.0.0.0', 8087), MobileHandler).serve_forever()
