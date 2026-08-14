#!/usr/bin/env python3
"""
License Delivery System
Generates and emails license keys after payment
"""

import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from licensing.license_manager import LicenseManager

class LicenseDelivery:
    def __init__(self):
        self.lm = LicenseManager()
        self.email_config = self.load_email_config()
    
    def load_email_config(self):
        """Load email configuration from environment"""
        return {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "licenses@explorer-d334.com",
            "sender_password": "",  # Set via environment
        }
    
    def generate_license_key(self, tier, email):
        """Generate license key for customer"""
        key = self.lm.generate_license_key(tier, email)
        return key
    
    def send_license_email(self, email, tier, license_key):
        """Send license key to customer"""
        subject = f"Your Explorer-d334 {tier.capitalize()} License"
        
        body = f"""
Hello,

Thank you for purchasing Explorer-d334 {tier.capitalize()}!

Your license key: {license_key}

To activate:
1. Save this key to a file named 'license.key' in your forge directory
2. Or run: echo '{license_key}' > license.key

Your license includes:
"""
        
        # Add features based on tier
        from payment.config import TIERS
        for feature in TIERS[tier]["features"]:
            body += f"  ✓ {feature}\n"
        
        body += f"""

License expires: 1 year from purchase date

Need help? Visit: https://explorer-d334.com/support

Thank you for supporting sovereign AI!

— The Explorer-d334 Team
"""
        
        # Send email (requires SMTP config)
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender_email']
            msg['To'] = email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            # Uncomment when SMTP is configured
            # server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            # server.starttls()
            # server.login(self.email_config['sender_email'], self.email_config['sender_password'])
            # server.send_message(msg)
            # server.quit()
            
            # For now, save to file
            with open(f"license_{email}.txt", 'w') as f:
                f.write(body)
            
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
    
    def process_purchase(self, tier, email, transaction_id):
        """Process a completed purchase"""
        print(f"Processing {tier} purchase for {email}")
        
        # Generate license
        license_key = self.generate_license_key(tier, email)
        
        # Send email
        self.send_license_email(email, tier, license_key)
        
        # Log sale
        self.log_sale(tier, email, transaction_id, license_key)
        
        return license_key
    
    def log_sale(self, tier, email, transaction_id, license_key):
        """Log sale for record keeping"""
        import sqlite3
        from datetime import datetime
        
        conn = sqlite3.connect("sales.db")
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP,
                tier TEXT,
                email TEXT,
                transaction_id TEXT,
                license_key TEXT
            )
        ''')
        c.execute('INSERT INTO sales (timestamp, tier, email, transaction_id, license_key) VALUES (?, ?, ?, ?, ?)',
                 (datetime.now().isoformat(), tier, email, transaction_id, license_key))
        conn.commit()
        conn.close()

if __name__ == "__main__":
    # Test the system
    delivery = LicenseDelivery()
    key = delivery.process_purchase("pro", "test@example.com", "test_123")
    print(f"Generated license: {key}")
