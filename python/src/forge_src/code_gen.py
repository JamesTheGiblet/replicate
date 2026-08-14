#!/usr/bin/env python3
"""Simple but effective code generator"""

import sys
import re

def reverse_string_code():
    return '''#include <stdio.h>
#include <string.h>

void reverse_string(char *str) {
    int len = strlen(str);
    for (int i = 0; i < len / 2; i++) {
        char temp = str[i];
        str[i] = str[len - 1 - i];
        str[len - 1 - i] = temp;
    }
}

int main() {
    char text[] = "Hello World";
    printf("Original: %s\\n", text);
    reverse_string(text);
    printf("Reversed: %s\\n", text);
    return 0;
}'''

def fibonacci_code():
    return '''#include <stdio.h>

int fibonacci(int n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

int main() {
    int n = 10;
    printf("Fibonacci sequence up to %d:\\n", n);
    for (int i = 0; i < n; i++) {
        printf("%d ", fibonacci(i));
    }
    printf("\\n");
    return 0;
}'''

def factorial_code():
    return '''#include <stdio.h>

unsigned long long factorial(int n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}

int main() {
    int n = 5;
    printf("Factorial of %d = %llu\\n", n, factorial(n));
    return 0;
}'''

def generate_code(prompt):
    prompt_lower = prompt.lower()
    
    if 'reverse' in prompt_lower and 'string' in prompt_lower:
        return reverse_string_code()
    elif 'fibonacci' in prompt_lower:
        return fibonacci_code()
    elif 'factorial' in prompt_lower:
        return factorial_code()
    elif 'hello' in prompt_lower:
        return '#include <stdio.h>\n\nint main() {\n    printf("Hello World!\\n");\n    return 0;\n}'
    else:
        return f'// Code for: {prompt}\n// Please be more specific or try:\n// - "reverse a string"\n// - "fibonacci sequence"\n// - "factorial calculation"'

if __name__ == "__main__":
    if len(sys.argv) > 1:
        prompt = ' '.join(sys.argv[1:])
        print(generate_code(prompt))
    else:
        print("Usage: python code_gen.py 'your request'")
