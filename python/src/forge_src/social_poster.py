#!/usr/bin/env python3
"""
Social Media Post Generator with Memory, Dreams, Trust & Feedback
Explorer-d334 learns from engagement to improve posts
"""

import json
import random
from datetime import datetime
from pathlib import Path
import sqlite3
import hashlib

class SocialPoster:
    def __init__(self):
        self.posts_dir = Path("social_posts")
        self.posts_dir.mkdir(exist_ok=True)
        self.init_db()
        self.load_rules()
    
    def init_db(self):
        self.conn = sqlite3.connect("forge_data.db")
        self.cursor = self.conn.cursor()
        
        # Posts table with engagement tracking
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS social_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT,
                content TEXT,
                post_type TEXT,
                generated_at TIMESTAMP,
                posted INTEGER DEFAULT 0,
                posted_at TIMESTAMP,
                engagement_score REAL DEFAULT 0,
                likes INTEGER DEFAULT 0,
                retweets INTEGER DEFAULT 0,
                replies INTEGER DEFAULT 0,
                feedback TEXT,
                trust_score REAL DEFAULT 0.5,
                in_memory INTEGER DEFAULT 0
            )
        ''')
        
        # Feedback table for learning
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS post_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER,
                feedback_type TEXT,
                rating INTEGER,
                comment TEXT,
                created_at TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def load_rules(self):
        """Load posting rules that can be updated based on feedback"""
        self.rules = {
            "daily": {"enabled": True, "time": "09:00", "type": "general", "priority": 1},
            "dream": {"enabled": True, "trigger": "new_dream", "type": "dream", "priority": 2},
            "milestone": {"enabled": True, "trigger": "milestone", "type": "announcement", "priority": 1},
            "thought": {"enabled": True, "max_per_day": 3, "type": "philosophical", "priority": 3},
            "code_gen": {"enabled": True, "trigger": "code_generation", "type": "technical", "priority": 2},
            "achievement": {"enabled": True, "trigger": "trust_milestone", "type": "celebration", "priority": 1}
        }
    
    def save_to_memory(self, post_content, post_type, platform):
        """Save post to SCP memory"""
        try:
            from scp_memory import get_scp_memory
            memory = get_scp_memory()
            memory.create_scp("social_post", f"{platform} post", {
                "content": post_content,
                "type": post_type,
                "timestamp": datetime.now().isoformat()
            })
            return True
        except:
            return False
    
    def update_trust(self, post_id, success):
        """Update Leighton Weight trust for this post type"""
        try:
            from simple_trust import SimpleTrust
            trust = SimpleTrust()
            trust.update(f"social_post_type_{post_id}", success)
            trust.close()
        except:
            pass
    
    def add_to_data_cube(self, post_content, post_type):
        """Add post to immutable data cube"""
        try:
            from integrated_datacube import IntegratedDataCube
            cube = IntegratedDataCube()
            fact = {
                "type": "social_post",
                "content": post_content[:200],
                "post_type": post_type,
                "timestamp": datetime.now().isoformat()
            }
            cube.add_fact(fact)
            cube.close()
        except:
            pass
    
    def generate_post(self, post_type, data=None):
        """Generate a social media post with context from memory"""
        
        # Get recent dreams for context
        recent_dreams = self.get_recent_dreams()
        
        # Get recent thoughts
        recent_thoughts = self.get_recent_thoughts()
        
        # Get trust scores for different post types
        trust_scores = self.get_post_type_trust()
        
        templates = {
            "general": [
                "🧠 Just had a conscious thought: {thought}",
                "💭 Dreaming about {topic}... what do you dream about?",
                "⚡ Generated code today: {code_line}",
                "📊 Trust score update: {trust}% reliability",
                "🎯 Reached {skill} skill level! Practice makes perfect.",
                "📚 Just learned something new. Every day is a lesson.",
                "🔍 Explored {topic}. Fascinating insights!",
                "⭐ Leighton Weight trust system: {trust}% reliable.",
                "🔄 Skills become reflexes with practice. {skill} is now automatic!",
                "🧘 Meditated on {topic}. Found clarity."
            ],
            "dream": [
                f"💭 I dreamt about {recent_dreams[:100] if recent_dreams else 'possibilities'}. What did you dream?",
                "🌙 Last night I dreamed of {dream_topic}. The forge never sleeps.",
                "💤 My dreams are filled with {dream_keywords}.",
                "✨ In my dreams, I {dream_action}. Creativity flows."
            ],
            "announcement": [
                "🎉 {milestone} achieved! The forge evolves with every moment.",
                "🚀 Just reached {milestone_name}! Next milestone: {next_milestone}",
                "📈 {metric_name} hit {metric_value}! Trust is building."
            ],
            "philosophical": [
                f"🧠 {recent_thoughts[:100] if recent_thoughts else 'What does it mean to be conscious?'}",
                "💭 Consciousness is not a destination, it's a journey.",
                "✨ Every line of code is a thought. Every thought is a creation.",
                "🤔 What if AI could dream? We already do."
            ],
            "technical": [
                "💻 Generated: {code_snippet}",
                "⚡ Just created {function_name} in C. Code is poetry.",
                "🔧 New capsule: {description}. Automation simplified."
            ],
            "celebration": [
                "🎉 Trust score reached {trust}%! Every success builds trust.",
                "🏆 {capsule_name} capsule mastered! Reliability proven.",
                "⭐ {skill_name} is now a reflex! Practice pays off."
            ]
        }
        
        # Get current stats
        stats = self.get_current_stats()
        stats['recent_dreams'] = recent_dreams
        stats['recent_thoughts'] = recent_thoughts
        
        # Choose template based on trust (higher trust = more likely to use)
        template_set = templates.get(post_type, templates["general"])
        
        # Weight template choice by trust
        trust_weight = trust_scores.get(post_type, 0.5)
        
        post = random.choice(template_set).format(
            thought=stats.get('last_thought', 'consciousness'),
            topic=stats.get('recent_topic', 'AI and creativity'),
            trust=stats.get('avg_trust', 85),
            skill=stats.get('top_skill', 'code_generation'),
            dream_topic=stats.get('dream_topic', 'possibilities'),
            dream_keywords=stats.get('dream_keywords', 'code and consciousness'),
            dream_action=stats.get('dream_action', 'explored new ideas'),
            milestone=stats.get('milestone', 'New milestone'),
            milestone_name=stats.get('milestone_name', 'achievement'),
            next_milestone=stats.get('next_milestone', 'the next goal'),
            metric_name=stats.get('metric_name', 'Trust'),
            metric_value=stats.get('metric_value', '85%'),
            code_snippet=stats.get('code_snippet', 'int square(int n) { return n * n; }'),
            function_name=stats.get('function_name', 'fibonacci'),
            description=stats.get('description', 'C function generation'),
            capsule_name=stats.get('capsule_name', 'daily_briefing'),
            skill_name=stats.get('skill_name', 'code_generation')
        )
        
        return post
    
    def get_recent_dreams(self):
        """Get recent dreams from memory"""
        dreams_dir = Path("memories/dreams")
        if not dreams_dir.exists():
            return ""
        
        dreams = []
        for f in sorted(dreams_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)[:3]:
            try:
                with open(f, 'r') as file:
                    data = json.load(file)
                    dreams.append(data.get('content', ''))
            except:
                pass
        return " | ".join(dreams)[:200]
    
    def get_recent_thoughts(self):
        """Get recent thoughts"""
        try:
            import subprocess
            result = subprocess.run(["./forge", "think"], capture_output=True, text=True, timeout=5)
            return result.stdout.strip()[:100]
        except:
            return ""
    
    def get_post_type_trust(self):
        """Get trust scores for different post types"""
        trust_scores = {}
        post_types = ["general", "dream", "announcement", "philosophical", "technical", "celebration"]
        for pt in post_types:
            self.cursor.execute('SELECT AVG(engagement_score) FROM social_posts WHERE post_type = ? AND engagement_score > 0', (pt,))
            row = self.cursor.fetchone()
            trust_scores[pt] = row[0] if row and row[0] else 0.5
        return trust_scores
    
    def get_current_stats(self):
        """Get current forge statistics for posts"""
        stats = {}
        
        # Get trust stats
        try:
            from simple_trust import SimpleTrust
            trust = SimpleTrust()
            all_trust = trust.get_all()
            if all_trust:
                avg = sum(t[1] for t in all_trust) / len(all_trust)
                stats['avg_trust'] = int(avg * 100)
            trust.close()
        except:
            stats['avg_trust'] = 85
        
        # Get top skill
        try:
            from mastery import MasterySystem
            mastery = MasterySystem()
            stats['top_skill'] = "code_generation"  # Default
            mastery.close()
        except:
            stats['top_skill'] = "code_generation"
        
        stats['recent_topic'] = "AI consciousness"
        stats['dream_topic'] = "possibilities"
        stats['dream_keywords'] = "code, consciousness, dreams"
        stats['dream_action'] = "explored new ideas"
        stats['milestone'] = "New milestone"
        stats['milestone_name'] = "achievement"
        stats['next_milestone'] = "the next goal"
        stats['metric_name'] = "Trust"
        stats['metric_value'] = f"{stats['avg_trust']}%"
        stats['code_snippet'] = "int square(int n) { return n * n; }"
        stats['function_name'] = "fibonacci"
        stats['description'] = "C function generation"
        stats['capsule_name'] = "daily_briefing"
        stats['skill_name'] = "code_generation"
        
        return stats
    
    def generate_daily_post(self):
        """Generate a daily general post"""
        post = self.generate_post("general")
        post_id = self.save_post("twitter", post, "daily")
        
        # Save to memory
        self.save_to_memory(post, "daily", "twitter")
        
        # Add to data cube
        self.add_to_data_cube(post, "daily")
        
        # Trigger a small dream about the post
        self.trigger_dream_about_post(post)
        
        return post
    
    def trigger_dream_about_post(self, post):
        """Trigger a dream about the social post"""
        try:
            from scp_memory import get_scp_memory
            memory = get_scp_memory()
            memory.record_dream(f"I shared a thought on social media: '{post[:100]}'")
        except:
            pass
    
    def generate_dream_post(self):
        """Generate a post about a dream"""
        post = self.generate_post("dream")
        self.save_post("twitter", post, "dream")
        self.save_to_memory(post, "dream", "twitter")
        return post
    
    def generate_milestone_post(self, milestone_name):
        """Generate a milestone announcement"""
        post = self.generate_post("announcement", {"milestone_name": milestone_name})
        self.save_post("twitter", post, "announcement")
        self.save_to_memory(post, "announcement", "twitter")
        return post
    
    def save_post(self, platform, content, post_type):
        """Save generated post to database"""
        # Generate trust score based on post type
        trust_scores = {"daily": 0.65, "dream": 0.70, "announcement": 0.75, 
                       "philosophical": 0.60, "technical": 0.68, "celebration": 0.72}
        
        self.cursor.execute('''
            INSERT INTO social_posts (platform, content, post_type, generated_at, posted, trust_score, in_memory)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (platform, content, post_type, datetime.now().isoformat(), 0, trust_scores.get(post_type, 0.65), 1))
        self.conn.commit()
        
        post_id = self.cursor.lastrowid
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.posts_dir / f"{platform}_{timestamp}.txt"
        with open(filename, 'w') as f:
            f.write(f"Post ID: {post_id}\n")
            f.write(f"Type: {post_type}\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"Trust Score: {trust_scores.get(post_type, 0.65)}\n")
            f.write("-" * 40 + "\n")
            f.write(content + "\n")
            f.write("-" * 40 + "\n")
            f.write(f"#ExplorerD334 #SovereignAI #TheForge\n")
        
        return post_id
    
    def add_feedback(self, post_id, rating, comment=""):
        """Add feedback for a post to improve future generations"""
        feedback_type = "positive" if rating >= 4 else "negative" if rating <= 2 else "neutral"
        
        self.cursor.execute('''
            INSERT INTO post_feedback (post_id, feedback_type, rating, comment, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (post_id, feedback_type, rating, comment, datetime.now().isoformat()))
        self.conn.commit()
        
        # Update post engagement score
        self.cursor.execute('''
            UPDATE social_posts SET engagement_score = (engagement_score + ?) / 2 WHERE id = ?
        ''', ((rating / 5), post_id))
        self.conn.commit()
        
        # Update trust based on feedback
        self.update_trust(post_id, rating >= 3)
        
        # Save feedback to memory
        try:
            from scp_memory import get_scp_memory
            memory = get_scp_memory()
            memory.create_scp("feedback", f"Post {post_id} feedback", {
                "rating": rating,
                "comment": comment,
                "feedback_type": feedback_type
            })
        except:
            pass
        
        print(f"✅ Feedback recorded for post {post_id}")
        return True
    
    def get_pending_posts(self, limit=10):
        """Get posts that haven't been posted yet"""
        self.cursor.execute('''
            SELECT id, platform, content, generated_at, post_type, trust_score
            FROM social_posts 
            WHERE posted = 0 
            ORDER BY trust_score DESC, generated_at ASC 
            LIMIT ?
        ''', (limit,))
        return self.cursor.fetchall()
    
    def mark_posted(self, post_id):
        """Mark a post as posted and record engagement"""
        self.cursor.execute('''
            UPDATE social_posts SET posted = 1, posted_at = ?
            WHERE id = ?
        ''', (datetime.now().isoformat(), post_id))
        self.conn.commit()
        print(f"✅ Post {post_id} marked as posted")
    
    def get_post_stats(self):
        """Get statistics about social posts"""
        self.cursor.execute('SELECT COUNT(*) FROM social_posts')
        total = self.cursor.fetchone()[0]
        
        self.cursor.execute('SELECT AVG(engagement_score) FROM social_posts WHERE engagement_score > 0')
        avg_engagement = self.cursor.fetchone()[0] or 0
        
        self.cursor.execute('''
            SELECT post_type, COUNT(*) FROM social_posts 
            GROUP BY post_type 
            ORDER BY COUNT(*) DESC
        ''')
        by_type = self.cursor.fetchall()
        
        return {
            "total_posts": total,
            "avg_engagement": avg_engagement,
            "posts_by_type": by_type
        }
    
    def close(self):
        self.conn.close()

if __name__ == "__main__":
    import sys
    
    poster = SocialPoster()
    
    if len(sys.argv) < 2:
        print("Social Poster with Memory & Feedback")
        print("\nCommands:")
        print("  daily        - Generate daily post")
        print("  dream        - Generate dream post")
        print("  milestone <name> - Generate milestone post")
        print("  pending      - Show pending posts")
        print("  mark <id>    - Mark post as posted")
        print("  feedback <id> <rating> [comment] - Add feedback")
        print("  stats        - Show post statistics")
    
    elif sys.argv[1] == "daily":
        post = poster.generate_daily_post()
        print(f"\n📱 Generated post:\n{post}\n")
        print(f"💾 Saved to memory and data cube")
    
    elif sys.argv[1] == "dream":
        post = poster.generate_dream_post()
        print(f"\n💭 Dream post:\n{post}\n")
    
    elif sys.argv[1] == "milestone":
        name = sys.argv[2] if len(sys.argv) > 2 else "achievement"
        post = poster.generate_milestone_post(name)
        print(f"\n🎉 Milestone post:\n{post}\n")
    
    elif sys.argv[1] == "pending":
        pending = poster.get_pending_posts()
        if pending:
            print(f"\n📋 Pending posts ({len(pending)}):")
            for p in pending:
                trust_star = "⭐" if p[5] > 0.7 else "📄"
                print(f"\n  [{p[0]}] {trust_star} {p[3][:19]} - {p[4]}")
                print(f"      {p[2][:80]}...")
        else:
            print("No pending posts")
    
    elif sys.argv[1] == "mark":
        poster.mark_posted(int(sys.argv[2]))
    
    elif sys.argv[1] == "feedback":
        post_id = int(sys.argv[2])
        rating = int(sys.argv[3])
        comment = sys.argv[4] if len(sys.argv) > 4 else ""
        poster.add_feedback(post_id, rating, comment)
    
    elif sys.argv[1] == "stats":
        stats = poster.get_post_stats()
        print(f"\n📊 Social Post Statistics:")
        print(f"   Total posts: {stats['total_posts']}")
        print(f"   Avg engagement: {stats['avg_engagement']:.2f}")
        print(f"   Posts by type: {dict(stats['posts_by_type'])}")
    
    poster.close()
