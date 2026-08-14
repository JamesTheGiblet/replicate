#!/usr/bin/env python3
"""
Explorer-d334 Enhanced Web Interface
Dashboard + Chat + Monitoring
"""

import sys
import json
import subprocess
import os
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

# Import forge modules
sys.path.insert(0, str(Path(__file__).parent))
from simple_trust import SimpleTrust
from device_awareness import DeviceAwareness

class EnhancedHandler(BaseHTTPRequestHandler):
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
                    capsules.append({
                        'name': cap_file.stem[:40],
                        'category': cat_dir.name,
                        'path': str(cap_file)
                    })
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
                memories.append({
                    'title': data.get('title', 'Untitled')[:50],
                    'type': data.get('type', 'unknown'),
                    'timestamp': data.get('timestamp', '')[:19]
                })
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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Explorer-d334 - Enhanced Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', monospace;
            background: #0a0a0a;
            color: #00ffcc;
            height: 100vh;
            overflow: hidden;
        }
        
        .app { display: flex; height: 100vh; }
        
        .sidebar {
            width: 260px;
            background: #0d0d0d;
            border-right: 1px solid #00ffcc20;
            display: flex;
            flex-direction: column;
            padding: 20px;
        }
        
        .logo { text-align: center; margin-bottom: 30px; }
        .logo h1 { font-size: 1.2em; letter-spacing: 2px; }
        .logo p { font-size: 0.7em; color: #00ffcc80; }
        
        .nav-item {
            padding: 12px 16px;
            margin: 4px 0;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
            color: #00ffcc80;
        }
        
        .nav-item:hover, .nav-item.active {
            background: #00ffcc10;
            color: #00ffcc;
        }
        
        .status-badge {
            margin-top: auto;
            padding: 16px;
            background: #00ffcc10;
            border-radius: 8px;
            font-size: 0.8em;
            text-align: center;
        }
        
        .main { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
        
        .header {
            padding: 20px;
            border-bottom: 1px solid #00ffcc20;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .header h2 { font-size: 1.2em; }
        .content { flex: 1; overflow-y: auto; padding: 20px; }
        
        .widget-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .widget {
            background: #0d0d0d;
            border: 1px solid #00ffcc20;
            border-radius: 12px;
            padding: 20px;
        }
        
        .widget-title {
            font-size: 0.8em;
            color: #00ffcc80;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .widget-value { font-size: 2.5em; font-weight: bold; }
        
        .trust-bar {
            background: #1a1a1a;
            border-radius: 4px;
            height: 8px;
            overflow: hidden;
            margin: 8px 0;
        }
        
        .trust-fill {
            background: #00ffcc;
            height: 100%;
            transition: width 0.3s;
        }
        
        .capsule-list { display: flex; flex-direction: column; gap: 8px; }
        
        .capsule-item {
            background: #0d0d0d;
            border: 1px solid #00ffcc20;
            border-radius: 8px;
            padding: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .capsule-name { font-weight: 500; }
        .capsule-category { font-size: 0.7em; color: #00ffcc80; }
        .run-btn {
            background: #00ffcc20;
            border: 1px solid #00ffcc;
            color: #00ffcc;
            padding: 4px 12px;
            border-radius: 15px;
            cursor: pointer;
        }
        
        .chat-area { display: flex; flex-direction: column; height: 100%; }
        .chat-messages { flex: 1; overflow-y: auto; padding: 20px; }
        
        .message { margin-bottom: 16px; animation: fadeIn 0.3s; }
        .message.user { text-align: right; }
        .message.assistant { text-align: left; }
        
        .message-content {
            display: inline-block;
            padding: 10px 16px;
            border-radius: 20px;
            max-width: 70%;
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
            gap: 12px;
            padding: 20px;
            border-top: 1px solid #00ffcc20;
        }
        
        .chat-input input {
            flex: 1;
            padding: 12px;
            background: #1a1a1a;
            border: 1px solid #00ffcc40;
            color: #00ffcc;
            border-radius: 25px;
        }
        
        .chat-input button {
            padding: 12px 24px;
            background: #00ffcc;
            color: #000;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-weight: bold;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body>
<div class="app">
    <div class="sidebar">
        <div class="logo">
            <h1>🔥 EXPLORER-d334</h1>
            <p>The Forge</p>
        </div>
        <div class="nav">
            <div class="nav-item active" data-view="dashboard">📊 Dashboard</div>
            <div class="nav-item" data-view="chat">💬 Chat</div>
            <div class="nav-item" data-view="capsules">📦 Capsules</div>
            <div class="nav-item" data-view="trust">⭐ Trust</div>
            <div class="nav-item" data-view="memories">🧠 Memories</div>
            <div class="nav-item" data-view="sensors">📡 Sensors</div>
        </div>
        <div class="status-badge">
            <div>🟢 Online</div>
        </div>
    </div>
    
    <div class="main">
        <div class="header">
            <h2 id="viewTitle">Dashboard</h2>
        </div>
        <div class="content" id="content"></div>
    </div>
</div>

<script>
    let currentView = 'dashboard';
    
    async function loadView(view) {
        currentView = view;
        document.getElementById('viewTitle').innerText = view.charAt(0).toUpperCase() + view.slice(1);
        const content = document.getElementById('content');
        
        if (view === 'dashboard') await loadDashboard();
        else if (view === 'chat') await loadChat();
        else if (view === 'capsules') await loadCapsules();
        else if (view === 'trust') await loadTrust();
        else if (view === 'memories') await loadMemories();
        else if (view === 'sensors') await loadSensors();
    }
    
    async function loadDashboard() {
        const res = await fetch('/api/stats');
        const stats = await res.json();
        document.getElementById('content').innerHTML = `
            <div class="widget-grid">
                <div class="widget"><div class="widget-title">Total Capsules</div><div class="widget-value">${stats.total_capsules}</div></div>
                <div class="widget"><div class="widget-title">Average Trust</div><div class="widget-value">${(stats.avg_trust * 100).toFixed(0)}%</div><div class="trust-bar"><div class="trust-fill" style="width: ${stats.avg_trust * 100}%"></div></div></div>
                <div class="widget"><div class="widget-title">Reflex Skills</div><div class="widget-value">${stats.reflex_skills}/5</div></div>
                <div class="widget"><div class="widget-title">Memories</div><div class="widget-value">${stats.total_memories}</div></div>
                <div class="widget"><div class="widget-title">Binaries</div><div class="widget-value">${stats.total_binaries}</div></div>
            </div>
            <div class="widget"><div class="widget-title">Quick Tip</div><p>Try "generate a fibonacci function" or ask me to dream about the future.</p></div>
        `;
    }
    
    async function loadChat() {
        document.getElementById('content').innerHTML = `
            <div class="chat-area">
                <div class="chat-messages" id="chatMessages"></div>
                <div class="chat-input">
                    <input type="text" id="chatInput" placeholder="Ask Explorer-d334 anything...">
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
            html += `<div class="capsule-item"><div><div class="capsule-name">${cap.name}</div><div class="capsule-category">${cap.category}</div></div><button class="run-btn" onclick="alert('Run ${cap.name}')">Run</button></div>`;
        });
        html += '</div>';
        document.getElementById('content').innerHTML = html;
    }
    
    async function loadTrust() {
        const res = await fetch('/api/trust');
        const trustData = await res.json();
        let html = '<div class="widget-grid">';
        trustData.forEach(item => {
            html += `<div class="widget"><div class="widget-title">${item.name}</div><div class="widget-value">${(item.trust * 100).toFixed(0)}%</div><div class="trust-bar"><div class="trust-fill" style="width: ${item.trust * 100}%"></div></div><div style="font-size:0.7em;">✓ ${item.successes} ✗ ${item.failures}</div></div>`;
        });
        html += '</div>';
        document.getElementById('content').innerHTML = html;
    }
    
    async function loadMemories() {
        const res = await fetch('/api/memories');
        const memories = await res.json();
        let html = '<div class="capsule-list">';
        memories.forEach(mem => {
            html += `<div class="capsule-item"><div><div class="capsule-name">${mem.title}</div><div class="capsule-category">${mem.type} • ${mem.timestamp}</div></div></div>`;
        });
        html += '</div>';
        document.getElementById('content').innerHTML = html;
    }
    
    async function loadSensors() {
        const res = await fetch('/api/sensors');
        const sensors = await res.json();
        let html = '<div class="widget-grid">';
        sensors.forEach(sensor => {
            html += `<div class="widget"><div class="widget-title">${sensor}</div><div class="widget-value">🟢 Active</div></div>`;
        });
        html += '</div>';
        document.getElementById('content').innerHTML = html;
    }
    
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', () => {
            document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');
            loadView(item.dataset.view);
        });
    });
    
    loadDashboard();
</script>
</body>
</html>
'''

if __name__ == '__main__':
    print("""
╔═══════════════════════════════════════════════════════════════╗
║     🔥 Explorer-d334 Enhanced Dashboard                       ║
║     Visit: http://localhost:8086                             ║
║     Dashboard + Chat + Monitoring                            ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    HTTPServer(('0.0.0.0', 8086), EnhancedHandler).serve_forever()
