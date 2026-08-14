#!/usr/bin/env python3
"""Enhanced web server with API and LLM chat support"""
import os
import subprocess
import json
import sys
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Add project root to Python path so 'from src.*' imports work correctly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.capsule_executor import CapsuleExecutor
from src.simple_trust import SimpleTrust

class APIHandler(SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path == '/api/forge':
            self.handle_api(parsed.query)
        elif path == '/api/chat':
            self.handle_chat(parsed.query)
        elif path == '/api/capsules/sync':
            self.handle_sync_capsules()
        else:
            super().do_GET()
    
    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path == '/api/capsule/execute':
            self.handle_execute_capsule()
        elif path == '/api/capsule/upload':
            self.handle_upload_capsule()
        else:
            self.send_error(404, 'Not Found')
            
    def handle_upload_capsule(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            payload = json.loads(post_data.decode('utf-8'))
            
            filename = payload.get('filename')
            content = payload.get('content')
            
            if not filename or not content:
                self.send_error(400, 'Missing filename or content')
                return
                
            # Ensure it ends with .scp.json for security/consistency
            safe_name = os.path.basename(filename)
            if not safe_name.endswith('.scp.json'):
                safe_name += '.scp.json'
                
            capsules_dir = Path(os.path.dirname(os.path.dirname(__file__))) / "capsules"
            capsules_dir.mkdir(exist_ok=True)
            
            file_path = capsules_dir / safe_name
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2)
                
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "message": f"Successfully deployed {safe_name} to Foundry. Ready for distribution."}).encode('utf-8'))
            print(f"[API] New capsule deployed via Architect: {safe_name}")
            
        except Exception as e:
            print(f"[API] Error uploading capsule: {e}")
            self.send_error(500, str(e))

    def handle_sync_capsules(self):
        try:
            capsules_dir = Path(os.path.dirname(os.path.dirname(__file__))) / "capsules"
            capsules_dir.mkdir(exist_ok=True)
            capsule_list = {}
            for cap_file in capsules_dir.glob("*.scp.json"):
                try:
                    with open(cap_file, 'r', encoding='utf-8') as f:
                        capsule_list[cap_file.name] = json.load(f)
                except:
                    pass
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "capsules": capsule_list}).encode('utf-8'))
            print(f"[API] Foundry distributed {len(capsule_list)} capsules to an Edge Node.")
        except Exception as e:
            print(f"[API] Error syncing capsules: {e}")
            self.send_error(500, str(e))

    def handle_execute_capsule(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            payload = json.loads(post_data.decode('utf-8'))
            
            capsule_name = payload.get('capsule_name')
            if not capsule_name:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": "Missing capsule_name parameter"}).encode('utf-8'))
                return
                
            print(f"[API] Executing capsule: {capsule_name}")
            
            trust_sys = SimpleTrust()
            current_trust = trust_sys.get_trust(capsule_name)['trust']
            
            # Block execution if trust drops too low (e.g., < 0.2)
            if current_trust < 0.2:
                self.send_response(403)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "status": "blocked", 
                    "message": f"Execution blocked: Trust score too low ({current_trust:.2f})"
                }).encode('utf-8'))
                trust_sys.close()
                return

            executor = CapsuleExecutor()
            result = executor.execute_capsule(capsule_name)
            
            # Update trust score based on execution outcome
            is_success = (result.get('status') == 'success')
            new_trust = trust_sys.update(capsule_name, success=is_success)
            result['new_trust_score'] = str(new_trust)
            trust_sys.close()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
            
            print(f"[API] Capsule {capsule_name} completed with status {result.get('status')}")
            
        except json.JSONDecodeError:
            self.send_error(400, 'Invalid JSON payload')
        except Exception as e:
            print(f"[API] Error: {e}")
            self.send_error(500, str(e))

    def handle_api(self, query_string):
        try:
            params = parse_qs(query_string)
            cmd = params.get('cmd', [''])[0]
            
            if not cmd:
                self.send_error(400, 'Missing cmd parameter')
                return
            
            print(f"[API] Executing: forge {cmd}")
            
            result = subprocess.run(
                ['./forge', cmd],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=os.path.dirname(os.path.dirname(__file__))
            )
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            output = result.stdout
            if result.stderr:
                output += '\n' + result.stderr
            self.wfile.write(output.encode('utf-8'))
            
            print(f"[API] Command completed with exit code {result.returncode}")
            
        except subprocess.TimeoutExpired:
            self.send_error(500, 'Command timed out')
        except Exception as e:
            print(f"[API] Error: {e}")
            self.send_error(500, str(e))
    
    def handle_chat(self, query_string):
        try:
            params = parse_qs(query_string)
            message = params.get('message', [''])[0]
            
            if not message:
                self.send_error(400, 'No message provided')
                return
            
            print(f"[CHAT] Processing: {message[:50]}...")
            
            # Use the chat_llm.py script
            result = subprocess.run(
                ['python3', 'src/chat_llm.py', message],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=os.path.dirname(os.path.dirname(__file__))
            )
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
            self.wfile.write(response.encode('utf-8'))
            
            print(f"[CHAT] Response sent")
            
        except subprocess.TimeoutExpired:
            self.send_error(500, 'Chat timeout')
        except Exception as e:
            print(f"[CHAT] Error: {e}")
            self.send_error(500, str(e))
    
    def log_message(self, format, *args):
        print(f"[{self.address_string()}] {format % args}")

def main():
    port = 8085
    os.chdir(os.path.dirname(os.path.dirname(__file__)))
    server = HTTPServer(('0.0.0.0', port), APIHandler)
    print(f"🔥 Explorer-d334 API Server running on port {port}")
    print(f"🌐 http://localhost:{port}")
    print(f"📁 Serving from: {os.getcwd()}")
    print(f"🔄 API endpoints:")
    print(f"   - /api/forge?cmd=think")
    print(f"   - /api/chat?message=hello")
    print(f"   - POST /api/capsule/execute (JSON: {{\"capsule_name\": \"...\"}})")
    print("Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()

if __name__ == '__main__':
    main()
