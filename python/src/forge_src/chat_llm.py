#!/usr/bin/env python3
"""Chat handler for Explorer-d334 - Code generation"""

import subprocess
import sys
import re

def execute_forge_command(cmd):
    """Execute forge command"""
    try:
        result = subprocess.run(
            ['./forge', cmd],
            capture_output=True,
            text=True,
            timeout=30,
            cwd='/data/data/com.termux/files/home/forge'
        )
        return result.stdout if result.stdout else result.stderr
    except Exception as e:
        return f"Error: {e}"

def generate_code(description):
    """Generate C code from natural language"""
    prompt = f"Write C code that: {description}"
    try:
        result = subprocess.run(
            ['./forge', 'generate', prompt],
            capture_output=True,
            text=True,
            timeout=60,
            cwd='/data/data/com.termux/files/home/forge'
        )
        if result.stdout:
            return result.stdout[:2000]
        return "I can help you write that code. Please provide more details about what you need."
    except:
        return "Let me help you write that code. What specific functionality do you need?"

def create_capsule(name, action, schedule="0 9 * * *"):
    """Generate capsule JSON"""
    return f"""Capsule Created: {name}

Save this to capsules/{name}.scp.json:

{{
  "name": "{name}",
  "description": "Automated task: {action}",
  "schedule": "{schedule}",
  "action": {{
    "type": "command",
    "command": "{action}"
  }}
}}

To activate: ./forge run {name}"""

def chat_response(message):
    """Process natural language requests"""
    lower = message.lower().strip()
    
    # Code generation
    if 'build a function' in lower or 'write code' in lower or 'generate code' in lower:
        desc = message
        for prefix in ['build a function', 'write code to', 'generate code for']:
            if prefix in lower:
                desc = message[message.lower().find(prefix)+len(prefix):].strip()
        return generate_code(desc)
    
    # Capsule creation
    if 'create a capsule' in lower or 'build a capsule' in lower:
        import re
        name_match = re.search(r'called\s+(\w+)', lower)
        name = name_match.group(1) if name_match else "my_capsule"
        
        if 'health' in lower:
            action = "./forge health"
        elif 'backup' in lower:
            action = "./forge backup"
        elif 'think' in lower:
            action = "./forge think"
        else:
            action = "./forge health"
        
        # Extract schedule
        schedule = "0 9 * * *"
        if 'hour' in lower:
            schedule = "0 * * * *"
        if 'minute' in lower:
            schedule = "*/30 * * * *"
            
        return create_capsule(name, action, schedule)
    
    # Explanations
    if 'six lens' in lower or 'knowledge cubes' in lower:
        return """Six Lens Knowledge System

Every fact is stored as a cube with 6 faces:
1. FACT - Verifiable truth
2. COUNTER - Opposing argument
3. OPINION - Personal perspective
4. FICTION - Speculative take
5. CONTEXT - Historical framing
6. UNKNOWN - Open questions

You have 39 knowledge cubes. Type 'cubes' to see them."""
    
    if 'trust system' in lower:
        return """Leighton Weight Trust System

Trust is calculated from:
- Source reliability
- Lens coverage (all 6 perspectives)
- User feedback
- Historical accuracy

Current trust: 96%"""
    
    # Direct commands
    if lower == 'think':
        return execute_forge_command('think')
    if lower == 'dream':
        return execute_forge_command('dream')
    if lower == 'cubes':
        return execute_forge_command('cubes')
    if lower == 'health':
        return execute_forge_command('health')
    if lower == 'capsules':
        return execute_forge_command('capsules')
    
    # Help
    if lower == 'help':
        return """Available Commands:

Core commands:
- think - Generate a thought
- dream - Generate a dream
- cubes - View knowledge cubes
- health - System health
- capsules - List automations

Development:
- build a function that [description]
- create a capsule called [name]
- explain Six Lens system
- explain trust system"""
    
    # Default
    return f"""Try:
- 'think' - Generate a thought
- 'build a function that reverses a string'
- 'create a capsule called daily_backup'
- 'explain Six Lens system'"""

if __name__ == "__main__":
    if len(sys.argv) > 1:
        message = ' '.join(sys.argv[1:])
        print(chat_response(message))
