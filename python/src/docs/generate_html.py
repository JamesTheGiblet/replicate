#!/usr/bin/env python3
"""
Generate HTML documentation from markdown
"""

import subprocess
from pathlib import Path

Try to install markdown converter

try:
import markdown
except ImportError:
subprocess.run(["pip", "install", "markdown"], capture_output=True)
import markdown

def convert_md_to_html(md_file, html_file):
with open(md_file, 'r') as f:
md_content = f.read()

<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Explorer-d334 Documentation</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', monospace;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: #0a0a0a;
            color: #00ffcc;
        }}
        h1, h2, h3 {{ color: #00ffcc; border-bottom: 1px solid #00ffcc; }}
        a {{ color: #00ffcc; }}
        code {{ background: #1a1a1a; padding: 2px 5px; border-radius: 3px; }}
        pre {{ background: #1a1a1a; padding: 10px; border-radius: 5px; overflow-x: auto; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #00ffcc; padding: 8px; text-align: left; }}
        .container {{ background: #111; padding: 20px; border-radius: 10px; }}
    </style>
</head>
<body>
<div class="container">
    {markdown.markdown(md_content, extensions=['tables'])}
</div>
</body>
</html>"""

Convert all markdown files

docs_dir = Path("docs")
for md_file in docs_dir.rglob("*.md"):
if md_file.name != "README.md" or md_file.parent == docs_dir:
html_file = md_file.with_suffix('.html')
convert_md_to_html(md_file, html_file)

print("\n✅ HTML documentation generated!")
