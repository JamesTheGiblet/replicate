#!/bin/bash
echo "🌐 Starting website preview server..."
echo "   Open http://localhost:8080"
python3 -m http.server 8080 --directory website
