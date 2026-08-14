#!/bin/bash
if [ $# -eq 0 ]; then
    echo "❌ Error: Missing arguments"
    echo "Usage: forge $0 <arguments>"
    exit 1
fi
