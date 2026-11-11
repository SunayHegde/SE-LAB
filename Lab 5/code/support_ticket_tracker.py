"""Support ticket tracker.

Creates tickets with a priority and category, assigns them to agents,
updates their status, searches and reports on them, and saves them to a
JSON file.
"""

import json
import logging
import os

TICKETS = {}
VALID_STATUSES = ("open", "in_progress", "closed")


def _next_ticket_id():
    """Return the next free ticket id as a string."""
    if not TICKETS:
        return "1"
    return str(max(int(ticket_id) for ticket_id in TICKETS) + 1)


# Six inputs are part of the ticket API; the optional ones are keyword-only.
# pylint: disable-next=too-many-arguments
def create_ticket(title, description, reporter, *,
                  priority="medium", category="general", audit_log=None):
    """Create a ticket, store it in TICKETS and return it.

    Returns None if no title is given. If an audit_log list is passed, a
    line describing the new ticket is appended to it.
    """
    if not title:
        return None
    if audit_log is None:
        audit_log = []
    ticket_id = _next_ticket_id()
    ticket = {
        "id": ticket_id,
        "title": title,
        "description": description,
        "priority": priority,
        "category": category,
        "status": "open",
        "reporter": reporter,
        "assignee": None,
    }
    TICKETS[ticket_id] = ticket
    audit_log.append(f"Created ticket {ticket_id} for {reporter}")
    return ticket


def assign_ticket(ticket_id, agent, notify=False):
    """Assign a ticket to an agent. Return True on success."""
    try:
        TICKETS[ticket_id]["assignee"] = agent
    except KeyError:
        logging.warning("Cannot assign: ticket %s does not exist", ticket_id)
        return False
    if notify:
        logging.info("Notified %s about ticket %s", agent, ticket_id)
    return True


def update_status(ticket_id, status):
    """Set the status of a ticket and return the ticket.

    Raises KeyError for an unknown ticket and ValueError for an
    unknown status.
    """
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {status}")
    TICKETS[ticket_id]["status"] = status
    return TICKETS[ticket_id]


def search_tickets(status=None, priority=None):
    """Return the tickets matching the given status and priority."""
    results = []
    for ticket in TICKETS.values():
        if status is not None and ticket["status"] != status:
            continue
        if priority and ticket["priority"] != priority:
            continue
        results.append(ticket)
    return results


def save_tickets(path="tickets.json"):
    """Write all tickets to a JSON file."""
    with open(path, "w", encoding="utf-8") as file:
        json.dump(TICKETS, file, indent=2)


def load_tickets(path="tickets.json"):
    """Replace the tickets in memory with those stored in a JSON file."""
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
    TICKETS.clear()
    TICKETS.update(data)


def print_ticket_report():
    """Print one line per ticket with its id, title and status."""
    print("Support Tickets")
    if not TICKETS:
        print("No tickets yet")
    for ticket_id, ticket in TICKETS.items():
        print(ticket_id, ticket["title"], ticket["status"])


def close_ticket(ticket_id):
    """Close a ticket. Return False if the ticket does not exist."""
    if ticket_id not in TICKETS:
        return False
    TICKETS[ticket_id]["status"] = "closed"
    return True


def is_open(ticket_id):
    """Return True if the ticket exists and is open or in progress."""
    ticket = TICKETS.get(ticket_id)
    return ticket is not None and ticket["status"] in ("open", "in_progress")


def main():
    """Run a short demo of the tracker."""
    logging.basicConfig(level=logging.INFO)
    create_ticket("Cannot sign in", "Password reset link fails",
                  "alex@example.com")
    create_ticket("Billing question", "Charged twice", "lee@example.com",
                  priority="high")
    assign_ticket("1", "agent-01")
    update_status("1", "in_progress")
    print_ticket_report()
    logging.info("Tickets created: %d", len(TICKETS))
    print("Ticket 1 open?", is_open("1"))
    ticket_id = input("Ticket id to close (Enter to skip): ").strip()
    if ticket_id and not close_ticket(ticket_id):
        print(f"No ticket with id {ticket_id}")
    save_tickets()
    if os.environ.get("RUN_UNSAFE_DEMO") == "1":
        print("unsafe demo")


if __name__ == "__main__":
    main()
