"""
Payment Configuration for Explorer-d334
"""

# Product tiers
TIERS = {
    "pro": {
        "name": "Explorer-d334 Pro",
        "price": 29,
        "price_display": "$29",
        "period": "year",
        "features": [
            "Unlimited custom capsules",
            "Commercial use allowed",
            "Email support",
            "No code watermark",
            "All updates"
        ]
    },
    "commercial": {
        "name": "Explorer-d334 Commercial",
        "price": 49,
        "price_display": "$49",
        "period": "year",
        "features": [
            "All Pro features",
            "Priority support (24h)",
            "Team collaboration (up to 3)",
            "White-label option",
            "SLA available"
        ]
    },
    "enterprise": {
        "name": "Explorer-d334 Enterprise",
        "price": "Custom",
        "price_display": "Contact us",
        "period": "negotiable",
        "features": [
            "All Commercial features",
            "Unlimited team seats",
            "Dedicated support (4h)",
            "Full white-label",
            "Custom integration",
            "SLA guarantee"
        ]
    }
}

# Gumroad product IDs (replace with actual)
GUMROAD_PRODUCTS = {
    "pro": "explorer-d334-pro",
    "commercial": "explorer-d334-commercial"
}

# Stripe price IDs (replace with actual)
STRIPE_PRICES = {
    "pro": "price_pro_annual",
    "commercial": "price_commercial_annual"
}

# License server (self-hosted option)
LICENSE_SERVER = os.getenv("LICENSE_SERVER", "https://licenses.explorer-d334.com")

# Webhook secret for payment verification
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "your-webhook-secret-here")
