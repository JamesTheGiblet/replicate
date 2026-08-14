
Gumroad Setup Guide (15 minutes)

Step 1: Create Account

1. Go to https://gumroad.com
2. Sign up with your email
3. Verify your account

Step 2: Create Pro Product

1. Click "Add product"
2. Name: "Explorer-d334 Pro"
3. Price: $29 (recurring yearly)
4. Description: Copy from website
5. Add custom field: "License key" (text)
6. Save

Step 3: Create Commercial Product

1. Add another product
2. Name: "Explorer-d334 Commercial"
3. Price: $49 (recurring yearly)
4. Add license key field
5. Save

Step 4: Set Up Webhook

1. Go to Settings → Webhooks
2. Add endpoint: https://your-server.com/webhook/gumroad
3. Select events: "sale.created"
4. Save

Step 5: Add License Generation

1. In webhook handler, call license_delivery.py
2. Generate license key
3. Email to customer

Done! Your payment system is ready.

