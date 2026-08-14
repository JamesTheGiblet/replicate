#!/usr/bin/env python3
import json
import re
from pathlib import Path

class CodeGenerator:
    def __init__(self, template_dir="templates"):
        self.template_dir = Path(template_dir)
        self.template_dir.mkdir(exist_ok=True)
        
    def generate_c_from_scp(self, scp_path):
        """Generate C code from SCP JSON prompt"""
        with open(scp_path) as f:
            scp = json.load(f)
        
        scp_type = scp.get("type", "function")
        
        if scp_type == "function":
            return self._gen_function(scp)
        elif scp_type == "daemon":
            return self._gen_daemon(scp)
        elif scp_type == "filter":
            return self._gen_filter(scp)
        else:
            return self._gen_generic(scp)
    
    def _gen_function(self, scp):
        name = scp["name"]
        params = scp.get("params", [])
        logic = scp.get("logic", "return 0;")
        
        code = f"""#include <stdio.h>
#include <stdlib.h>

int {name}({', '.join([f'{p["type"]} {p["name"]}' for p in params])}) {{
    {logic}
}}

int main(int argc, char *argv[]) {{
"""
        # Add argument parsing
        for i, p in enumerate(params):
            code += f"""    {p['type']} {p['name']};
    if (argc > {i+1}) {{
        {p['name']} = ({p['type']})atoi(argv[{i+1}]);
    }} else {{
        {p['name']} = 0;
    }}
"""
        
        code += f"    int result = {name}({', '.join([p['name'] for p in params])});\n"
        code += f"    printf(\"%d\\n\", result);\n"
        code += f"    return 0;\n"
        code += f"}}\n"
        return code
    
    def _gen_daemon(self, scp):
        name = scp["name"]
        interval = scp.get("interval", 1000)
        
        return f"""#include <stdio.h>
#include <unistd.h>

int main() {{
    while(1) {{
        printf("{name} running\\n");
        usleep({interval} * 1000);
    }}
    return 0;
}}
"""
    
    def _gen_filter(self, scp):
        input_type = scp.get("input", "int")
        output_type = scp.get("output", "int")
        transform = scp.get("transform", "x")
        
        return f"""#include <stdio.h>

int main() {{
    {input_type} x;
    while(scanf("%d", &x) != EOF) {{
        {output_type} result = {transform};
        printf("%d\\n", result);
    }}
    return 0;
}}
"""
    
    def _gen_generic(self, scp):
        """Generic template-based generator"""
        template = self.template_dir / f"{scp.get('template', 'default')}.c"
        if template.exists():
            with open(template) as f:
                base = f.read()
            for key, value in scp.items():
                base = base.replace(f"{{{{{key}}}}}", str(value))
            return base
        else:
            return f"// Generated from {scp.get('name', 'unknown')}\nint main() {{ return 0; }}\n"
    
    def generate_json_from_scp(self, scp_path):
        """Generate JSON output schema from SCP"""
        with open(scp_path) as f:
            scp = json.load(f)
        
        output_schema = {
            "input": scp.get("input_schema", {}),
            "output": scp.get("output_schema", {}),
            "transform": scp.get("transform", "identity")
        }
        return json.dumps(output_schema, indent=2)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: code_generator.py <scp.json> <output.c|output.json>")
        sys.exit(1)
    
    gen = CodeGenerator()
    scp_file = sys.argv[1]
    out_file = sys.argv[2]
    
    if out_file.endswith('.c'):
        code = gen.generate_c_from_scp(scp_file)
        with open(out_file, 'w') as f:
            f.write(code)
        print(f"Generated {out_file}")
    elif out_file.endswith('.json'):
        schema = gen.generate_json_from_scp(scp_file)
        with open(out_file, 'w') as f:
            f.write(schema)
        print(f"Generated {out_file}")
