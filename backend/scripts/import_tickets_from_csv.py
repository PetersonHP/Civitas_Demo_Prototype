#!/usr/bin/env python3
"""
Script to import tickets from a CSV file into the database.

Usage:
    python scripts/import_tickets_from_csv.py <csv_file_path>

CSV Format:
    ticket_subject,ticket_body,origin,status,priority,reporter_id,lat,lng
"""

import sys
import csv
from pathlib import Path
from uuid import UUID

# Add parent directory to path to import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from geoalchemy2.elements import WKTElement

from src.database import SessionLocal, engine
from src.models.civitas import Ticket, CivitasUser, TicketOrigin, TicketStatus, TicketPriority


def parse_coordinates(lat: str, lng: str) -> WKTElement | None:
    """Parse latitude and longitude into PostGIS geometry."""
    if not lat or not lng:
        return None
    try:
        lat_val = float(lat)
        lng_val = float(lng)
        return WKTElement(f"POINT({lng_val} {lat_val})", srid=4326)
    except ValueError:
        return None


def parse_uuid(uuid_str: str) -> UUID | None:
    """Parse UUID string, return None if invalid or empty."""
    if not uuid_str or not uuid_str.strip():
        return None
    try:
        return UUID(uuid_str.strip())
    except ValueError:
        return None


def import_tickets_from_csv(csv_file_path: str):
    """Import tickets from a CSV file."""
    if not Path(csv_file_path).exists():
        print(f"Error: File {csv_file_path} not found")
        sys.exit(1)

    db = SessionLocal()
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            # Validate required columns
            required_columns = {'ticket_subject', 'ticket_body', 'origin', 'status', 'priority'}
            if not required_columns.issubset(reader.fieldnames):
                print(f"Error: CSV must contain columns: {required_columns}")
                print(f"Found columns: {reader.fieldnames}")
                sys.exit(1)

            tickets_created = 0
            tickets_failed = 0

            for row_num, row in enumerate(reader, start=2):  # Start at 2 (1 for header)
                try:
                    # Parse origin
                    origin_str = row['origin'].lower().strip()
                    try:
                        origin = TicketOrigin(origin_str)
                    except ValueError:
                        print(f"Warning (row {row_num}): Invalid origin '{row['origin']}', defaulting to 'phone'")
                        origin = TicketOrigin.PHONE

                    # Parse status
                    status_str = row['status'].lower().strip()
                    try:
                        status = TicketStatus(status_str)
                    except ValueError:
                        print(f"Warning (row {row_num}): Invalid status '{row['status']}', defaulting to 'awaiting response'")
                        status = TicketStatus.AWAITING_RESPONSE

                    # Parse priority
                    priority_str = row['priority'].lower().strip()
                    try:
                        priority = TicketPriority(priority_str)
                    except ValueError:
                        print(f"Warning (row {row_num}): Invalid priority '{row['priority']}', defaulting to 'medium'")
                        priority = TicketPriority.MEDIUM

                    # Parse reporter_id
                    reporter_id = None
                    if 'reporter_id' in row and row['reporter_id']:
                        reporter_id = parse_uuid(row['reporter_id'])
                        if reporter_id is None:
                            print(f"Warning (row {row_num}): Invalid reporter_id '{row['reporter_id']}'")

                    # Parse location
                    location_coordinates = None
                    if 'lat' in row and 'lng' in row:
                        location_coordinates = parse_coordinates(row['lat'], row['lng'])

                    # Create ticket
                    ticket = Ticket(
                        ticket_subject=row['ticket_subject'].strip(),
                        ticket_body=row['ticket_body'].strip(),
                        origin=origin,
                        status=status,
                        priority=priority,
                        reporter_id=reporter_id,
                        location_coordinates=location_coordinates,
                    )

                    db.add(ticket)
                    db.commit()
                    tickets_created += 1
                    print(f"Created ticket (row {row_num}): {ticket.ticket_subject[:50]}...")

                except Exception as e:
                    db.rollback()
                    tickets_failed += 1
                    print(f"Failed to create ticket (row {row_num}): {e}")

            print(f"\n{'='*60}")
            print(f"Import complete!")
            print(f"Successfully created: {tickets_created} tickets")
            print(f"Failed: {tickets_failed} tickets")
            print(f"{'='*60}")

    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/import_tickets_from_csv.py <csv_file_path>")
        print("\nExample:")
        print("  python scripts/import_tickets_from_csv.py data/sample_tickets.csv")
        sys.exit(1)

    import_tickets_from_csv(sys.argv[1])
