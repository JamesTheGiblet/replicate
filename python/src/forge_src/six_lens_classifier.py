#!/usr/bin/env python3
"""
Six Lens Classifier for Explorer-d334
Maps information to the six perspectives: FACT, COUNTER, OPINION, FICTION, CONTEXT, UNKNOWN
"""

import re
from datetime import datetime

class SixLensClassifier:
    def __init__(self):
        self.lenses = {
            "FACT": {
                "color": "cyan",
                "icon": "◈",
                "description": "The prime verifiable statement",
                "keywords": ["is", "are", "was", "were", "fact", "true", "verified", "evidence", "data shows"]
            },
            "COUNTER": {
                "color": "red",
                "icon": "⊘",
                "description": "The refutation or opposing argument",
                "keywords": ["however", "wrong", "contrary", "disagree", "flawed", "mistake", "error", "but", "actually"]
            },
            "OPINION": {
                "color": "purple",
                "icon": "◎",
                "description": "Personal or subjective perspective",
                "keywords": ["think", "believe", "perspective", "view", "seems", "appears", "feel", "opinion"]
            },
            "FICTION": {
                "color": "amber",
                "icon": "◇",
                "description": "Speculative or narrative take",
                "keywords": ["imagine", "story", "what if", "could be", "perhaps", "maybe", "fiction", "speculative"]
            },
            "CONTEXT": {
                "color": "green",
                "icon": "⊡",
                "description": "Historical or wider framing",
                "keywords": ["history", "research", "origin", "background", "traditionally", "originally", "context"]
            },
            "UNKNOWN": {
                "color": "grey",
                "icon": "?",
                "description": "What remains unresolved",
                "keywords": ["unknown", "mystery", "unresolved", "uncertain", "question", "maybe", "unclear"]
            }
        }
    
    def classify(self, text):
        """Classify text into one of the six lenses"""
        text_lower = text.lower()
        scores = {}
        
        for lens, data in self.lenses.items():
            score = 0
            for keyword in data["keywords"]:
                if keyword in text_lower:
                    score += 10
            scores[lens] = score
        
        # Get highest scoring lens
        best_lens = max(scores, key=scores.get)
        confidence = scores[best_lens]
        
        if confidence < 10:
            return "FACT", confidence  # Default to FACT for low confidence
        return best_lens, confidence
    
    def get_lens_color(self, lens):
        return self.lenses.get(lens, {}).get("color", "white")
    
    def get_lens_icon(self, lens):
        return self.lenses.get(lens, {}).get("icon", "◈")
    
    def format_with_lens(self, text, lens):
        """Format text with lens styling"""
        icon = self.get_lens_icon(lens)
        color = self.get_lens_color(lens)
        return f"{icon} [{lens}] {text}"
    
    def get_cube_integrity(self, entries):
        """Calculate cube integrity based on filled lenses"""
        filled = sum(1 for e in entries if e.get('lens'))
        completeness = (filled / 6) * 100
        avg_confidence = sum(e.get('confidence', 0) for e in entries) / max(filled, 1)
        integrity = (completeness * 0.4) + (avg_confidence * 0.6)
        
        if integrity >= 90:
            grade = "CRYSTALLINE"
        elif integrity >= 65:
            grade = "COHERENT"
        elif integrity >= 35:
            grade = "FORMING"
        else:
            grade = "SPARSE"
        
        return integrity, grade

if __name__ == "__main__":
    classifier = SixLensClassifier()
    
    print("=== SIX LENS CLASSIFIER ===\n")
    
    test_phrases = [
        "The Earth orbits the Sun",
        "However, this model fails to account for dark matter",
        "I think we need a new approach to AI",
        "Imagine a world where machines understand emotions",
        "Historically, this idea emerged in ancient Greece",
        "The true nature of consciousness remains unknown"
    ]
    
    for phrase in test_phrases:
        lens, conf = classifier.classify(phrase)
        print(f"{classifier.get_lens_icon(lens)} {lens}: {phrase[:50]}... (conf: {conf})")
