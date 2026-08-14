# Payment Integration Setup

## Quick Setup (Gumroad - Easiest)

1. **Create Gumroad account** at https://gumroad.com
2. **Create products:**
   - Explorer-d334 Pro ($29/year)
   - Explorer-d334 Commercial ($49/year)
3. **Add webhook URL:** `https://your-server.com/webhook/gumroad`
4. **Set up license delivery** (auto after purchase)

## Stripe Setup (Advanced)

1. **Create Stripe account**
2. **Create products and prices**
3. **Set up webhook endpoint**
4. **Add license key generation**

## Files

| File | Purpose |
|------|---------|
| `config.py` | Payment configuration |
| `license_delivery.py` | License generation & email |
| `webhook.py` | Payment webhook handler |
| `checkout.html` | Simple checkout page |

## Environment Variables

```bash
export GUMROAD_TOKEN="your-token"
export STRIPE_SECRET_KEY="sk_..."
export WEBHOOK_SECRET="your-secret"
export SMTP_PASSWORD="your-email-password"
```

Testing

```bash
# Test license generation
python payment/license_delivery.py

# Run webhook server
python payment/webhook.py
```

Integration with Website

Add checkout links to your pricing page:

· Pro: https://gum.co/explorer-d334-pro
· Commercial: https://gum.co/explorer-d334-commercial

