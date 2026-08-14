#!/bin/bash

Main support interface

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

show_help() {
echo -e "${CYAN}Explorer-d334 Support System${NC}"
echo ""
echo "  ${GREEN}./support.sh faq${NC}        - Browse FAQ"
echo "  ${GREEN}./support.sh ticket${NC}     - Create support ticket"
echo "  ${GREEN}./support.sh diagnose${NC}   - Run diagnostics"
echo "  ${GREEN}./support.sh knowledge${NC}  - Search knowledge base"
echo "  ${GREEN}./support.sh contact${NC}    - Contact support"
}

show_faq() {
cat support/faq/README.md | less
}

run_diagnostics() {
echo "🔍 RUNNING DIAGNOSTICS"
echo "======================"
echo ""

}

search_knowledge() {
echo "🔍 SEARCH KNOWLEDGE BASE"
echo "========================"
echo ""
echo "Enter search term:"
read TERM
grep -r -i "$TERM" support/knowledge_base/ docs/ 2>/dev/null | head -20
}

contact_support() {
echo "📧 CONTACT SUPPORT"
echo "================="
echo ""
echo "Email: support@explorer-d334.com"
echo "Response time: 24-48 hours"
echo ""
echo "Include in your email:"
echo "  - Your license type (personal/commercial/enterprise)"
echo "  - Your issue description"
echo "  - Output of: ./support.sh diagnose"
echo ""
echo "Priority support (commercial license):"
echo "  - Email: priority@explorer-d334.com"
echo "  - Response: 12-24 hours"
}

case "$1" in
faq)
show_faq
;;
ticket)
./support/tickets/ticket.sh create
;;
diagnose)
run_diagnostics
;;
knowledge)
search_knowledge
;;
contact)
contact_support
;;
*)
show_help
;;
esac
