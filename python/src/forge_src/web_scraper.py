#!/usr/bin/env python3
"""
Web Search and Scraping for Explorer-d334
Search the web, scrape content, and integrate with forge systems
"""

import requests
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
import sqlite3
import hashlib

class WebScraper:
    def __init__(self):
        self.forge_dir = Path.cwd()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Android 14; Explorer-d334) AppleWebKit/537.36'
        })
        self.init_db()
    
    def init_db(self):
        self.conn = sqlite3.connect(str(self.forge_dir / "forge_data.db"))
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS web_scrapes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT,
                title TEXT,
                content TEXT,
                summary TEXT,
                scraped_at TIMESTAMP,
                content_hash TEXT,
                trust_score REAL DEFAULT 0.5,
                used_in_dream INTEGER DEFAULT 0
            )
        ''')
        self.conn.commit()
    
    def search_web(self, query, num_results=5):
        """Search the web using DuckDuckGo (no API key needed)"""
        results = []
        
        # Use DuckDuckGo HTML search
        url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
        
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find search results
            for result in soup.find_all('a', class_='result__a')[:num_results]:
                title = result.get_text()
                link = result.get('href')
                if link and not link.startswith('/'):
                    results.append({
                        'title': title,
                        'url': link,
                        'snippet': ''
                    })
        except Exception as e:
            print(f"Search error: {e}")
        
        return results
    
    def scrape_url(self, url):
        """Scrape content from a URL"""
        try:
            response = self.session.get(url, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get title
            title = soup.title.string if soup.title else url
            
            # Get main content
            # Try common content containers
            content_selectors = ['article', 'main', '.content', '#content', '.post', '.entry']
            content = None
            
            for selector in content_selectors:
                elem = soup.select_one(selector)
                if elem:
                    content = elem.get_text()
                    break
            
            if not content:
                content = soup.body.get_text() if soup.body else ''
            
            # Clean up text
            content = re.sub(r'\n+', '\n', content)
            content = re.sub(r'\s+', ' ', content)
            content = content[:5000]  # Limit length
            
            # Generate hash
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            # Generate summary (first 500 chars)
            summary = content[:500] + '...' if len(content) > 500 else content
            
            # Store in database
            self.cursor.execute('''
                INSERT INTO web_scrapes (url, title, content, summary, scraped_at, content_hash, trust_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (url, title, content, summary, datetime.now().isoformat(), content_hash, 0.65))
            self.conn.commit()
            
            return {
                'success': True,
                'title': title,
                'content': content[:1000],
                'summary': summary,
                'word_count': len(content.split())
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def search_and_scrape(self, query, num_results=3):
        """Search and scrape top results"""
        results = []
        search_results = self.search_web(query, num_results)
        
        for result in search_results:
            scraped = self.scrape_url(result['url'])
            if scraped.get('success'):
                results.append({
                    'url': result['url'],
                    'title': scraped['title'],
                    'summary': scraped['summary']
                })
        
        return results
    
    def add_to_data_cube(self, url, title, summary):
        """Add scraped content to data cube"""
        try:
            from integrated_datacube import IntegratedDataCube
            cube = IntegratedDataCube()
            
            fact = {
                "type": "web_scrape",
                "url": url,
                "title": title,
                "summary": summary,
                "timestamp": datetime.now().isoformat()
            }
            cube.add_fact(fact)
            cube.close()
        except:
            pass
    
    def trigger_dream_from_scrape(self, title, summary):
        """Trigger a dream based on scraped content"""
        try:
            from forge_memory import ForgeMemory
            memory = ForgeMemory()
            
            # Extract keywords for dreaming
            words = (title + " " + summary).lower().split()
            common_words = ['the', 'and', 'to', 'of', 'a', 'in', 'is', 'it', 'for', 'with', 'on', 'at', 'by']
            keywords = [w for w in set(words) if len(w) > 4 and w not in common_words][:5]
            
            if keywords:
                dream = f"I dreamt about {', '.join(keywords)} from web content titled '{title[:50]}'"
                memory.dream(dream, "web_inspired")
                memory.close()
                
                # Mark as used in dream
                self.cursor.execute('UPDATE web_scrapes SET used_in_dream = 1 WHERE title = ?', (title[:100],))
                self.conn.commit()
                
            return keywords
        except:
            return []
    
    def get_scraped_content(self, keyword):
        """Search scraped content for keyword"""
        self.cursor.execute('''
            SELECT url, title, summary, scraped_at, trust_score
            FROM web_scrapes 
            WHERE content LIKE ? OR title LIKE ?
            ORDER BY trust_score DESC, scraped_at DESC
        ''', (f'%{keyword}%', f'%{keyword}%'))
        return self.cursor.fetchall()
    
    def list_scraped(self):
        """List all scraped content"""
        self.cursor.execute('''
            SELECT url, title, scraped_at, trust_score, used_in_dream
            FROM web_scrapes 
            ORDER BY scraped_at DESC
            LIMIT 20
        ''')
        return self.cursor.fetchall()
    
    def close(self):
        self.conn.close()

if __name__ == "__main__":
    import sys
    
    scraper = WebScraper()
    
    if len(sys.argv) < 2:
        print("Web Scraper Commands:")
        print("  search <query>         - Search the web")
        print("  scrape <url>           - Scrape a URL")
        print("  explore <query>        - Search and scrape")
        print("  list                   - List scraped content")
        print("  find <keyword>         - Find in scraped content")
    
    elif sys.argv[1] == "search":
        results = scraper.search_web(" ".join(sys.argv[2:]))
        for r in results:
            print(f"  📄 {r['title']}\n     {r['url']}\n")
    
    elif sys.argv[1] == "scrape":
        result = scraper.scrape_url(sys.argv[2])
        if result['success']:
            print(f"✅ Scraped: {result['title']}")
            print(f"   Words: {result['word_count']}")
            print(f"   Summary: {result['summary'][:200]}...")
        else:
            print(f"❌ Error: {result.get('error')}")
    
    elif sys.argv[1] == "explore":
        query = " ".join(sys.argv[2:])
        print(f"🔍 Exploring: {query}")
        results = scraper.search_and_scrape(query)
        for r in results:
            print(f"\n📄 {r['title']}")
            print(f"   {r['summary'][:150]}...")
            
            # Trigger dream
            keywords = scraper.trigger_dream_from_scrape(r['title'], r['summary'])
            if keywords:
                print(f"   💭 Dream triggered about: {', '.join(keywords)}")
    
    elif sys.argv[1] == "list":
        items = scraper.list_scraped()
        for item in items:
            dream_icon = "💭" if item[4] else "📄"
            print(f"  {dream_icon} {item[1][:50]} - Trust: {item[3]:.2f}")
    
    elif sys.argv[1] == "find":
        results = scraper.get_scraped_content(" ".join(sys.argv[2:]))
        for r in results:
            print(f"  📄 {r[1]}")
            print(f"     {r[2][:100]}...")
    
    scraper.close()
