#!/usr/bin/env python3
"""
Script to delete all tickets from the database.

WARNING: This will delete ALL tickets. Use with caution!

Usage:
    python scripts/delete_all_tickets.py [--confirm]
"""

import sys
from pathlib import Path

# Add parent directory to path to import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import SessionLocal
from src.models.civitas import Ticket


def delete_all_tickets(skip_confirmation: bool = False):
    """Delete all tickets from the database."""
    db = SessionLocal()
    try:
        # Count tickets
        ticket_count = db.query(Ticket).count()

        if ticket_count == 0:
            print("No tickets found in the database.")
            return

        print(f"Found {ticket_count} ticket(s) in the database.")

        # Confirm deletion
        if not skip_confirmation:
            response = input(f"\nAre you sure you want to delete ALL {ticket_count} tickets? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                print("Deletion cancelled.")
                return

        # Delete all tickets
        deleted_count = db.query(Ticket).delete()
        db.commit()

        print(f"\n{'='*60}")
        print(f"Successfully deleted {deleted_count} ticket(s)")
        print(f"{'='*60}")

    except Exception as e:
        db.rollback()
        print(f"Error deleting tickets: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    skip_confirmation = '--confirm' in sys.argv or '-y' in sys.argv

    if len(sys.argv) > 1 and sys.argv[1] not in ['--confirm', '-y']:
        print("Usage: python scripts/delete_all_tickets.py [--confirm]")
        print("\nOptions:")
        print("  --confirm, -y    Skip confirmation prompt")
        sys.exit(1)

    delete_all_tickets(skip_confirmation)
