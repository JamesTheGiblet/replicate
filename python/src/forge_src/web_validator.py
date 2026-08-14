#!/usr/bin/env python3
"""
Web Validator for Data Cube Facts
Validates information by searching the web and cross-referencing
"""

import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
import hashlib
import sqlite3

class WebValidator:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Android 14; Explorer-d334 Validator)'
        })
        self.init_db()
    
    def init_db(self):
        self.conn = sqlite3.connect("forge_data.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS validation_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fact_hash TEXT,
                fact_content TEXT,
                search_query TEXT,
                source_url TEXT,
                source_title TEXT,
                confidence REAL,
                validated_at TIMESTAMP,
                matches INTEGER DEFAULT 0
            )
        ''')
        self.conn.commit()
    
    def search_web(self, query, num_results=3):
        """Search the web for information"""
        results = []
        
        # Use DuckDuckGo HTML search
        url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
        
        try:
            response = self.session.get(url, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for result in soup.find_all('a', class_='result__a')[:num_results]:
                title = result.get_text()
                link = result.get('href')
                if link and not link.startswith('/'):
                    results.append({
                        'title': title,
                        'url': link
                    })
        except Exception as e:
            print(f"Search error: {e}")
        
        return results
    
    def scrape_page(self, url):
        """Scrape and extract text from a page"""
        try:
            response = self.session.get(url, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text()
            # Clean up
            text = ' '.join(text.split())
            return text[:2000]  # Limit length
        except Exception as e:
            return None
    
    def validate_fact(self, fact_text, confidence_threshold=0.6):
        """Validate a fact by searching the web"""
        print(f"\n🔍 Validating: {fact_text[:100]}...")
        
        # Search for the fact
        search_results = self.search_web(fact_text)
        
        if not search_results:
            return {
                'validated': False,
                'confidence': 0,
                'sources': [],
                'message': 'No web sources found'
            }
        
        # Check each source
        valid_sources = []
        total_confidence = 0
        
        for result in search_results:
            content = self.scrape_page(result['url'])
            if content:
                # Check if fact appears in content
                fact_keywords = fact_text.lower().split()[:5]
                matches = sum(1 for kw in fact_keywords if kw in content.lower())
                confidence = matches / len(fact_keywords) if fact_keywords else 0
                
                if confidence >= confidence_threshold:
                    valid_sources.append({
                        'url': result['url'],
                        'title': result['title'],
                        'confidence': confidence
                    })
                    total_confidence += confidence
        
        # Calculate overall confidence
        avg_confidence = total_confidence / len(valid_sources) if valid_sources else 0
        
        # Store validation attempt
        self.store_validation(fact_text, search_results, avg_confidence)
        
        return {
            'validated': len(valid_sources) > 0,
            'confidence': avg_confidence,
            'sources': valid_sources,
            'message': f'Found {len(valid_sources)} corroborating sources' if valid_sources else 'No corroborating sources'
        }
    
    def validate_datacube_fact(self, fact_hash):
        """Validate a fact from the Data Cube"""
        try:
            from .integrated_datacube import IntegratedDataCube
            cube = IntegratedDataCube()
            fact = cube.get_fact(fact_hash)
            cube.close()
            
            if not fact:
                return {'validated': False, 'message': 'Fact not found'}
            
            fact_text = json.dumps(fact.get('data', {}))
            return self.validate_fact(fact_text)
        except Exception as e:
            return {'validated': False, 'message': str(e)}
    
    def store_validation(self, fact_text, sources, confidence):
        """Store validation results"""
        fact_hash = hashlib.md5(fact_text.encode()).hexdigest()
        
        for source in sources[:3]:
            self.cursor.execute('''
                INSERT INTO validation_attempts 
                (fact_hash, fact_content, search_query, source_url, source_title, confidence, validated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (fact_hash, fact_text[:200], fact_text[:50], source.get('url'), source.get('title'), 
                  confidence, datetime.now().isoformat()))
        self.conn.commit()
    
    def get_validation_history(self, limit=10):
        """Get validation history"""
        self.cursor.execute('''
            SELECT fact_content, source_title, confidence, validated_at 
            FROM validation_attempts 
            ORDER BY validated_at DESC 
            LIMIT ?
        ''', (limit,))
        return self.cursor.fetchall()
    
    def close(self):
        self.conn.close()

if __name__ == "__main__":
    import sys
    
    validator = WebValidator()
    
    if len(sys.argv) < 2:
        print("Web Validator Commands:")
        print("  validate <fact>     - Validate a fact")
        print("  history             - View validation history")
        print("  datacube <hash>     - Validate Data Cube fact")
    
    elif sys.argv[1] == "validate":
        fact = " ".join(sys.argv[2:])
        result = validator.validate_fact(fact)
        print(f"\n📊 Validation Result:")
        print(f"   Validated: {result['validated']}")
        print(f"   Confidence: {result['confidence']:.2f}")
        print(f"   Message: {result['message']}")
        if result.get('sources'):
            print(f"   Sources: {len(result['sources'])}")
            for s in result['sources'][:2]:
                print(f"     • {s['title']}")
    
    elif sys.argv[1] == "history":
        history = validator.get_validation_history()
        print("\n📋 Validation History:")
        for h in history:
            print(f"   [{h[3][:19]}] {h[1][:50]} (Conf: {h[2]:.2f})")
    
    validator.close()
