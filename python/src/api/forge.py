#!/usr/bin/env python3
"""API endpoint for executing forge commands"""
import subprocess
import sys
import json
import urllib.parse

def handle_request(query_string):
    """Handle API request and return response"""
    # Parse query parameters
    params = urllib.parse.parse_qs(query_string)
    cmd = params.get('cmd', [''])[0]
    
    if not cmd:
        return json.dumps({'error': 'No command specified'})
    
    try:
        # Execute forge command
        result = subprocess.run(
            ['./forge', cmd],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return json.dumps({
            'success': True,
            'command': cmd,
            'output': result.stdout,
            'error': result.stderr,
            'exit_code': result.returncode
        })
    except subprocess.TimeoutExpired:
        return json.dumps({'error': f'Command {cmd} timed out'})
    except Exception as e:
        return json.dumps({'error': str(e)})

if __name__ == '__main__':
    # Get query string from environment or command line
    query = sys.argv[1] if len(sys.argv) > 1 else ''
    print(handle_request(query))
