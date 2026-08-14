#!/bin/bash
# Support Ticket System

TICKET_DIR="$HOME/forge/support/tickets"
mkdir -p "$TICKET_DIR"

create_ticket() {
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    TICKET_ID="TKT-${TIMESTAMP}"
    TICKET_FILE="$TICKET_DIR/${TICKET_ID}.txt"
    
    echo "=========================================" > "$TICKET_FILE"
    echo "TICKET: $TICKET_ID" >> "$TICKET_FILE"
    echo "CREATED: $(date)" >> "$TICKET_FILE"
    echo "STATUS: OPEN" >> "$TICKET_FILE"
    echo "=========================================" >> "$TICKET_FILE"
    echo "" >> "$TICKET_FILE"
    echo "FROM: $1" >> "$TICKET_FILE"
    echo "TYPE: $2" >> "$TICKET_FILE"
    echo "" >> "$TICKET_FILE"
    echo "DESCRIPTION:" >> "$TICKET_FILE"
    echo "$3" >> "$TICKET_FILE"
    echo "" >> "$TICKET_FILE"
    echo "--- SYSTEM INFO ---" >> "$TICKET_FILE"
    ./forge device >> "$TICKET_FILE" 2>/dev/null
    echo "" >> "$TICKET_FILE"
    ./forge health >> "$TICKET_FILE" 2>/dev/null
    
    echo "✅ Ticket created: $TICKET_ID"
    echo "📁 Saved to: $TICKET_FILE"
}

list_tickets() {
    echo "📋 OPEN TICKETS:"
    echo "================"
    for ticket in "$TICKET_DIR"/*.txt; do
        if [ -f "$ticket" ]; then
            TICKET_ID=$(grep "TICKET:" "$ticket" | cut -d' ' -f2)
            STATUS=$(grep "STATUS:" "$ticket" | cut -d' ' -f2)
            echo "  $TICKET_ID - $STATUS"
        fi
    done
}

close_ticket() {
    TICKET_FILE="$TICKET_DIR/$1.txt"
    if [ -f "$TICKET_FILE" ]; then
        sed -i 's/STATUS: OPEN/STATUS: CLOSED/' "$TICKET_FILE"
        echo "✅ Ticket $1 closed"
    else
        echo "❌ Ticket not found: $1"
    fi
}

case "$1" in
    create)
        shift
        echo "Enter your email:"
        read EMAIL
        echo "Issue type (bug/question/feature/other):"
        read TYPE
        echo "Describe your issue:"
        read DESC
        create_ticket "$EMAIL" "$TYPE" "$DESC"
        ;;
    list)
        list_tickets
        ;;
    close)
        close_ticket "$2"
        ;;
    *)
        echo "Support Ticket System"
        echo ""
        echo "Usage:"
        echo "  ./ticket.sh create    - Create new ticket"
        echo "  ./ticket.sh list      - List all tickets"
        echo "  ./ticket.sh close ID  - Close a ticket"
        ;;
esac
