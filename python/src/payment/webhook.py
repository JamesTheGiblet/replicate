#!/usr/bin/env python3
"""
Gumroad/Stripe Webhook Handler
Automatically generates licenses after successful payment
"""

import json
import hmac
import hashlib
from http.server import HTTPServer, BaseHTTPRequestHandler
from license_delivery import LicenseDelivery

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/webhook/gumroad':
            self.handle_gumroad()
        elif self.path == '/webhook/stripe':
            self.handle_stripe()
        else:
            self.send_response(404)
            self.end_headers()
    
    def handle_gumroad(self):
        """Handle Gumroad webhook"""
        length = int(self.headers.get('Content-Length', 0))
        data = self.rfile.read(length)
        
        # Verify signature (add your Gumroad webhook secret)
        # signature = self.headers.get('X-Gumroad-Signature')
        
        payload = json.loads(data)
        
        if payload.get('sale'):
            sale = payload['sale']
            email = sale.get('email')
            product_id = sale.get('product_id')
            
            # Map product to tier
            if 'pro' in product_id:
                tier = 'pro'
            elif 'commercial' in product_id:
                tier = 'commercial'
            else:
                tier = 'personal'
            
            # Generate and send license
            delivery = LicenseDelivery()
            license_key = delivery.process_purchase(tier, email, sale.get('id'))
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok', 'license': license_key}).encode())
        else:
            self.send_response(200)
            self.end_headers()
    
    def handle_stripe(self):
        """Handle Stripe webhook"""
        # Implement Stripe webhook handling
        self.send_response(200)
        self.end_headers()

if __name__ == '__main__':
    print("Payment webhook server running on port 8088")
    HTTPServer(('0.0.0.0', 8088), WebhookHandler).serve_forever()
