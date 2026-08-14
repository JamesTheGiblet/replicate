#!/usr/bin/env python3
import json
import sys

def generate_c(scp_file, output_file):
    with open(scp_file) as f:
        data = json.load(f)
    
    name = data.get("name", "generated_func")
    logic = data.get("logic", "return 0;")
    
    # Write the C code directly without any printf mangling
    c_code = f'''#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int {name}(int n) {{
    {logic}
}}

int main(int argc, char *argv[]) {{
    int n = (argc > 1) ? atoi(argv[1]) : 0;
    {name}(n);
    return 0;
}}
'''
    with open(output_file, 'w') as f:
        f.write(c_code)
    
    print(f"Generated {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python working_replicator.py <input.json> <output.c>")
        sys.exit(1)
    generate_c(sys.argv[1], sys.argv[2])
