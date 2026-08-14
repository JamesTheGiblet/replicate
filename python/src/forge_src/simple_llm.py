#!/usr/bin/env python3
import random
import sys

# Simple Markov chain text generator
class MiniLLM:
    def __init__(self):
        self.words = {}
    
    def train(self, text):
        words = text.split()
        for i in range(len(words)-1):
            if words[i] not in self.words:
                self.words[words[i]] = []
            self.words[words[i]].append(words[i+1])
    
    def generate(self, start_word, length=50):
        if start_word not in self.words:
            start_word = random.choice(list(self.words.keys()))
        result = [start_word]
        for _ in range(length):
            last = result[-1]
            if last not in self.words:
                break
            next_word = random.choice(self.words[last])
            result.append(next_word)
        return ' '.join(result)

# Train on C code patterns
c_code_samples = """
int main int printf return include define if else for while
function calculate input output result value number array pointer
struct malloc free size sizeof char string double float void
static const volatile auto register continue break switch case
default goto do typedef enum union extern
"""

llm = MiniLLM()
llm.train(c_code_samples)

print(llm.generate("int", 20))
