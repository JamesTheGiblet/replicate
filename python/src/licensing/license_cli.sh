#!/bin/bash
# License management CLI

LICENSE_DIR="licensing"

generate_license() {
    TIER=$1
    EMAIL=$2
    
    if [ -z "$TIER" ] || [ -z "$EMAIL" ]; then
        echo "Usage: $0 generate <tier> <email>"
        echo "Tiers: personal, commercial, enterprise"
        return 1
    fi
    
    python3 << PYEOF
from licensing.license_manager import LicenseManager
lm = LicenseManager()
key = lm.generate_license_key('$TIER', '$EMAIL')
print(f'✅ License generated for $EMAIL')
print(f'   Tier: $TIER')
print(f'   Key: {key}')
print(f'   Valid for: 1 year')
lm.close()
PYEOF
}

validate_license() {
    KEY=$1
    
    if [ -z "$KEY" ]; then
        echo "Usage: $0 validate <license-key>"
        return 1
    fi
    
    python3 << PYEOF
from licensing.license_manager import LicenseManager
lm = LicenseManager()
result = lm.validate_license('$KEY')
if result['valid']:
    print('✅ License VALID')
    print(f'   Tier: {result["tier"]}')
    print(f'   Expires: {result["expires_at"][:10]}')
    features = result.get('features', {})
    if features:
        print(f'   Features: {", ".join([k for k,v in features.items() if v])[:50]}...')
else:
    print(f'❌ License INVALID: {result["reason"]}')
lm.close()
PYEOF
}

list_licenses() {
    python3 << PYEOF
from licensing.license_manager import LicenseManager
lm = LicenseManager()
licenses = lm.list_licenses()
print('='*60)
print('ACTIVE LICENSES')
print('='*60)
if licenses:
    for lic in licenses:
        print(f'  {lic[0][:20]}... | {lic[1]} | {lic[2]} | expires: {lic[3][:10]} | validations: {lic[4]}')
else:
    print('  No active licenses')
lm.close()
PYEOF
}

revoke_license() {
    KEY=$1
    
    if [ -z "$KEY" ]; then
        echo "Usage: $0 revoke <license-key>"
        return 1
    fi
    
    python3 << PYEOF
from licensing.license_manager import LicenseManager
lm = LicenseManager()
if lm.revoke_license('$KEY'):
    print('✅ License revoked')
else:
    print('❌ License not found')
lm.close()
PYEOF
}

pricing() {
    echo "=== EXPLORER-d334 PRICING ==="
    echo ""
    echo "PERSONAL - FREE"
    echo "  • Core functionality"
    echo "  • Code generation"
    echo "  • Consciousness features"
    echo "  • Web interface"
    echo "  • No commercial use"
    echo ""
    echo "COMMERCIAL - $49/year"
    echo "  • All personal features"
    echo "  • Commercial use allowed"
    echo "  • Priority support (24h)"
    echo "  • All updates"
    echo ""
    echo "ENTERPRISE - Custom pricing"
    echo "  • All commercial features"
    echo "  • Team collaboration"
    echo "  • White-label rights"
    echo "  • Dedicated support (4h)"
    echo "  • Custom integration"
}

case "$1" in
    generate)
        generate_license "$2" "$3"
        ;;
    validate)
        validate_license "$2"
        ;;
    list)
        list_licenses
        ;;
    revoke)
        revoke_license "$2"
        ;;
    pricing)
        pricing
        ;;
    *)
        echo "License Management CLI"
        echo ""
        echo "Usage:"
        echo "  $0 generate <tier> <email>  - Generate license key"
        echo "  $0 validate <key>           - Validate license key"
        echo "  $0 list                     - List all licenses"
        echo "  $0 revoke <key>             - Revoke license"
        echo "  $0 pricing                  - Show pricing tiers"
        ;;
esac
