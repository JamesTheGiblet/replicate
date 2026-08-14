#!/usr/bin/env python3
"""
License Key Management System for Explorer-d334
Handles personal, commercial, and enterprise tiers
"""

import hashlib
import json
import secrets
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import uuid

class LicenseManager:
    def __init__(self):
        self.licenses_dir = Path.cwd() / "licensing"
        self.licenses_dir.mkdir(exist_ok=True)
        self.db_path = self.licenses_dir / "licenses.db"
        self.init_db()
    
    def init_db(self):
        """Initialize license database"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.cursor = self.conn.cursor()
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS licenses (
                license_key TEXT PRIMARY KEY,
                tier TEXT,
                customer_email TEXT,
                issued_at TIMESTAMP,
                expires_at TIMESTAMP,
                validated INTEGER DEFAULT 0,
                last_validated TIMESTAMP,
                features TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS validations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                license_key TEXT,
                validated_at TIMESTAMP,
                success INTEGER,
                machine_id TEXT
            )
        ''')
        
        self.conn.commit()
    
    def generate_license_key(self, tier, customer_email, duration_days=365):
        """Generate a unique license key"""
        # Generate random key
        random_part = secrets.token_hex(8).upper()
        tier_code = {"personal": "P", "pro": "R", "commercial": "C", "enterprise": "E"}[tier]
        timestamp_part = datetime.now().strftime("%Y%m")
        hash_input = f"{customer_email}{random_part}{datetime.now().isoformat()}"
        hash_part = hashlib.md5(hash_input.encode()).hexdigest()[:8].upper()
        
        license_key = f"{tier_code}-{timestamp_part}-{random_part}-{hash_part}"
        
        # Set expiration
        issued_at = datetime.now()
        expires_at = issued_at + timedelta(days=duration_days)
        
        # Define features per tier
        features = self.get_tier_features(tier)
        
        # Store in database
        self.cursor.execute('''
            INSERT INTO licenses (license_key, tier, customer_email, issued_at, expires_at, features)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (license_key, tier, customer_email, issued_at.isoformat(), expires_at.isoformat(), json.dumps(features)))
        
        self.conn.commit()
        return license_key
    
    def get_tier_features(self, tier):
        """Get features for each tier"""
        common_features = {
            "core_functionality": True,
            "code_generation": True,
            "consciousness": True,
            "web_interface": True
        }
        
        if tier == "personal":
            return {
                **common_features,
                "commercial_use": False,
                "priority_support": False,
                "team_collaboration": False,
                "white_label": False,
                "updates": "security_only"
            }
        elif tier == "commercial":
            return {
                **common_features,
                "commercial_use": True,
                "priority_support": True,
                "team_collaboration": False,
                "white_label": False,
                "updates": "all",
                "max_seats": 1,
                "response_time_hours": 24
            }
        elif tier == "enterprise":
            return {
                **common_features,
                "commercial_use": True,
                "priority_support": True,
                "team_collaboration": True,
                "white_label": True,
                "updates": "all",
                "max_seats": "unlimited",
                "response_time_hours": 4,
                "dedicated_support": True,
                "custom_integration": True
            }
        return common_features
    
    def validate_license(self, license_key, machine_id=None):
        """Validate a license key"""
        self.cursor.execute('''
            SELECT tier, expires_at, features, customer_email FROM licenses WHERE license_key = ?
        ''', (license_key,))
        row = self.cursor.fetchone()
        
        if not row:
            self._log_validation(license_key, False, machine_id)
            return {"valid": False, "reason": "License key not found"}
        
        tier, expires_at_str, features_json, email = row
        expires_at = datetime.fromisoformat(expires_at_str)
        
        if expires_at < datetime.now():
            self._log_validation(license_key, False, machine_id)
            return {"valid": False, "reason": "License expired", "expired_at": expires_at_str}
        
        # Update validation count
        self.cursor.execute('''
            UPDATE licenses SET validated = validated + 1, last_validated = ?
            WHERE license_key = ?
        ''', (datetime.now().isoformat(), license_key))
        self.conn.commit()
        
        self._log_validation(license_key, True, machine_id)
        
        return {
            "valid": True,
            "tier": tier,
            "features": json.loads(features_json),
            "customer_email": email,
            "expires_at": expires_at_str
        }
    
    def _log_validation(self, license_key, success, machine_id):
        """Log validation attempt"""
        self.cursor.execute('''
            INSERT INTO validations (license_key, validated_at, success, machine_id)
            VALUES (?, ?, ?, ?)
        ''', (license_key, datetime.now().isoformat(), 1 if success else 0, machine_id))
        self.conn.commit()
    
    def list_licenses(self):
        """List all licenses"""
        self.cursor.execute('''
            SELECT license_key, tier, customer_email, expires_at, validated 
            FROM licenses ORDER BY issued_at DESC
        ''')
        return self.cursor.fetchall()
    
    def revoke_license(self, license_key):
        """Revoke a license"""
        self.cursor.execute('DELETE FROM licenses WHERE license_key = ?', (license_key,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def close(self):
        self.conn.close()

# Pricing configuration
PRICING = {
    "personal": {
        "price": 0,
        "price_display": "FREE",
        "duration": "forever",
        "features": [
            "✓ Core functionality",
            "✓ Code generation",
            "✓ Consciousness features",
            "✓ Web interface",
            "✗ Commercial use",
            "✗ Priority support",
            "✗ Team collaboration"
        ]
    },
    "commercial": {
        "price": 49,
        "price_display": "$49",
        "duration": "year",
        "features": [
            "✓ All personal features",
            "✓ Commercial use allowed",
            "✓ Priority support (24h)",
            "✓ All updates",
            "✗ Team collaboration",
            "✗ White-label"
        ]
    },
    "enterprise": {
        "price": "Custom",
        "price_display": "Custom",
        "duration": "negotiable",
        "features": [
            "✓ All commercial features",
            "✓ Team collaboration",
            "✓ White-label rights",
            "✓ Dedicated support (4h)",
            "✓ Custom integration",
            "✓ Unlimited seats"
        ]
    }
}

if __name__ == "__main__":
    lm = LicenseManager()
    
    print("=== LICENSE MANAGEMENT SYSTEM ===")
    print("\n📊 Current Licenses:")
    for lic in lm.list_licenses():
        print(f"   {lic[0]} - {lic[1]} - {lic[2]} - expires: {lic[3][:10]}")
    
    if len(lm.list_licenses()) == 0:
        print("   No licenses yet. Generate one with:")
        print("   python licensing/license_manager.py generate commercial user@example.com")
    
    lm.close()
