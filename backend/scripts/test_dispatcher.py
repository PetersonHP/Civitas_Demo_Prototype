#!/usr/bin/env python3
"""
Test Script for Dispatcher Agent

This script tests the dispatcher agent by:
1. Randomly sampling n tickets from the database
2. Running the dispatcher on each ticket and timing the response
3. Outputting results row by row to a JSON Lines file
4. Calculating accuracy by checking if assigned users' email domains match
   the agency from the original NYC 311 data

Usage:
    python test_dispatcher.py <n>

    where <n> is the number of tickets to test

Example:
    python test_dispatcher.py 10
"""

import sys
import os
import json
import time
import re
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID

# Add backend directory to path to import src as a package
script_dir = Path(__file__).parent
backend_dir = script_dir.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import func
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from src.database import SessionLocal
from src.models.civitas import Ticket as TicketModel
from src.services.dispatcher_agent import dispatch_ticket_model
from src.config import get_settings


# Mapping of email domains to agency codes
EMAIL_DOMAIN_TO_AGENCY = {
    'dep.nyc.gov': 'DEP',
    'dhs.nyc.gov': 'DHS',
    'buildings.nyc.gov': 'DOB',
    'schools.nyc.gov': 'DOE',
    'health.nyc.gov': 'DOHMH',
    'dot.nyc.gov': 'DOT',
    'parks.nyc.gov': 'DPR',
    'dsny.nyc.gov': 'DSNY',
    'edc.nyc': 'EDC',
    'sheriff.nyc.gov': 'OOS',
}


def load_nyc_311_agency_mapping(csv_path: str) -> Dict[str, str]:
    """
    Load the mapping of unique_key to agency from the original NYC 311 data.

    Args:
        csv_path: Path to the NYC 311 CSV file

    Returns:
        Dictionary mapping unique_key to agency code
    """
    mapping = {}

    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                unique_key = row.get('unique_key', '').strip()
                agency = row.get('agency', '').strip()
                if unique_key and agency:
                    mapping[unique_key] = agency

        print(f"Loaded {len(mapping)} unique_key -> agency mappings")
    except Exception as e:
        print(f"Warning: Could not load NYC 311 agency mapping: {e}")

    return mapping


def extract_unique_key_from_subject(subject: str) -> Optional[str]:
    """
    Extract the unique_key from a ticket subject.

    Args:
        subject: Ticket subject line

    Returns:
        Unique key string or None if not found
    """
    # Pattern: (unique_key: 12345678)
    match = re.search(r'\(unique_key:\s*(\d+)\)', subject, re.IGNORECASE)
    if match:
        return match.group(1)
    return None


def get_agency_from_email(email: str) -> Optional[str]:
    """
    Extract the agency code from a user's email address.

    Args:
        email: User email address

    Returns:
        Agency code or None if not matched
    """
    if not email:
        return None

    email_lower = email.lower()

    for domain, agency in EMAIL_DOMAIN_TO_AGENCY.items():
        if f'@{domain}' in email_lower:
            return agency

    return None


def calculate_accuracy(
    assigned_user_emails: List[str],
    expected_agency: str
) -> bool:
    """
    Check if any assigned user's email domain matches the expected agency.

    Args:
        assigned_user_emails: List of assigned user email addresses
        expected_agency: Expected agency code from NYC 311 data

    Returns:
        True if any user matches the expected agency, False otherwise
    """
    if not assigned_user_emails or not expected_agency:
        return False

    for email in assigned_user_emails:
        user_agency = get_agency_from_email(email)
        if user_agency == expected_agency:
            return True

    return False


def test_dispatcher_on_tickets(
    n: int,
    output_dir: Path,
    db: Session,
    agency_mapping: Dict[str, str]
) -> Dict[str, Any]:
    """
    Test the dispatcher agent on n randomly sampled tickets.

    Args:
        n: Number of tickets to test
        output_dir: Directory to save output file
        db: Database session
        agency_mapping: Mapping of unique_key to agency code

    Returns:
        Summary statistics dictionary
    """
    settings = get_settings()

    # Check API key
    if not settings.anthropic_api_key:
        raise ValueError("ANTHROPIC_API_KEY not configured in environment")

    # Query n random tickets from the database
    print(f"Sampling {n} random tickets from database...")
    tickets = db.query(TicketModel).order_by(func.random()).limit(n).all()

    if not tickets:
        raise ValueError("No tickets found in database")

    print(f"Found {len(tickets)} tickets to test")

    # Create output file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"dispatcher_test_results_{timestamp}.jsonl"

    print(f"Output file: {output_file}")
    print(f"Processing tickets...\n")

    # Open output file for writing (JSON Lines format)
    results = []
    total_time = 0.0
    correct_assignments = 0
    total_with_expected_agency = 0

    with open(output_file, 'w', encoding='utf-8') as f:
        for i, ticket in enumerate(tickets, 1):
            print(f"[{i}/{len(tickets)}] Processing ticket {ticket.ticket_id}...")
            print(f"  Subject: {ticket.ticket_subject[:80]}...")

            # Extract unique_key from ticket subject
            unique_key = extract_unique_key_from_subject(ticket.ticket_subject)
            expected_agency = None

            if unique_key and unique_key in agency_mapping:
                expected_agency = agency_mapping[unique_key]
                print(f"  Expected agency: {expected_agency}")
            else:
                print(f"  Warning: Could not determine expected agency (unique_key: {unique_key})")

            # Time the dispatcher call
            start_time = time.time()

            try:
                result = dispatch_ticket_model(
                    ticket_model=ticket,
                    db=db,
                    api_key=settings.anthropic_api_key
                )

                elapsed_time = time.time() - start_time
                total_time += elapsed_time

                print(f"  Time: {elapsed_time:.2f}s")
                print(f"  Priority: {result.get('priority', 'N/A')}")
                print(f"  User assignees: {len(result.get('user_assignees', []))}")
                print(f"  Crew assignees: {len(result.get('crew_assignees', []))}")

                # Get assigned user emails for accuracy calculation
                assigned_user_ids = result.get('user_assignees', [])
                assigned_user_emails = []

                if assigned_user_ids:
                    from src.models.civitas import CivitasUser
                    for user_id_str in assigned_user_ids:
                        try:
                            user_uuid = UUID(user_id_str)
                            user = db.query(CivitasUser).filter(
                                CivitasUser.user_id == user_uuid
                            ).first()
                            if user and user.email:
                                assigned_user_emails.append(user.email)
                        except Exception as e:
                            print(f"  Warning: Could not fetch user {user_id_str}: {e}")

                # Calculate accuracy
                is_correct = False
                if expected_agency:
                    total_with_expected_agency += 1
                    is_correct = calculate_accuracy(assigned_user_emails, expected_agency)
                    if is_correct:
                        correct_assignments += 1
                        print(f"  ✓ Correct assignment!")
                    else:
                        print(f"  ✗ Incorrect assignment")
                        if assigned_user_emails:
                            assigned_agencies = [
                                get_agency_from_email(email) or "Unknown"
                                for email in assigned_user_emails
                            ]
                            print(f"    Assigned agencies: {', '.join(assigned_agencies)}")

                # Prepare result record
                result_record = {
                    'ticket_id': str(ticket.ticket_id),
                    'ticket_subject': ticket.ticket_subject,
                    'unique_key': unique_key,
                    'expected_agency': expected_agency,
                    'assigned_user_emails': assigned_user_emails,
                    'assigned_agencies': [
                        get_agency_from_email(email) for email in assigned_user_emails
                    ],
                    'is_correct': is_correct if expected_agency else None,
                    'elapsed_time_seconds': round(elapsed_time, 2),
                    'status': 'success',
                    'dispatcher_result': result
                }

                # Write result immediately (JSON Lines format)
                f.write(json.dumps(result_record) + '\n')
                f.flush()  # Ensure it's written immediately

                results.append(result_record)

            except Exception as e:
                elapsed_time = time.time() - start_time
                total_time += elapsed_time

                print(f"  ✗ Error: {e}")

                # Record error
                error_record = {
                    'ticket_id': str(ticket.ticket_id),
                    'ticket_subject': ticket.ticket_subject,
                    'unique_key': unique_key,
                    'expected_agency': expected_agency,
                    'elapsed_time_seconds': round(elapsed_time, 2),
                    'status': 'error',
                    'error': str(e)
                }

                # Write error immediately
                f.write(json.dumps(error_record) + '\n')
                f.flush()

                results.append(error_record)

            print()  # Blank line between tickets

        # Calculate summary statistics
        success_count = sum(1 for r in results if r['status'] == 'success')
        error_count = len(results) - success_count
        avg_time = total_time / len(results) if results else 0.0
        accuracy = (correct_assignments / total_with_expected_agency * 100) if total_with_expected_agency > 0 else 0.0

        summary = {
            'type': 'summary',
            'timestamp': datetime.now().isoformat(),
            'total_tickets': len(results),
            'successful': success_count,
            'errors': error_count,
            'tickets_with_expected_agency': total_with_expected_agency,
            'correct_assignments': correct_assignments,
            'accuracy_percent': round(accuracy, 2),
            'total_time_seconds': round(total_time, 2),
            'average_time_seconds': round(avg_time, 2)
        }

        # Write summary as final line
        f.write(json.dumps(summary) + '\n')

    return summary


def main():
    """Main entry point for the test script."""
    # Check command line arguments
    if len(sys.argv) != 2:
        print("Usage: python test_dispatcher.py <n>")
        print("  where <n> is the number of tickets to test")
        sys.exit(1)

    try:
        n = int(sys.argv[1])
        if n <= 0:
            raise ValueError("n must be positive")
    except ValueError as e:
        print(f"Error: Invalid argument. {e}")
        print("Usage: python test_dispatcher.py <n>")
        sys.exit(1)

    # Load environment variables
    env_path = backend_dir / ".env"
    load_dotenv(env_path)

    # Set up paths
    data_dir = backend_dir / "data"
    data_dir.mkdir(exist_ok=True)

    nyc_311_csv = data_dir / "nyc_311_data.csv"

    # Load agency mapping
    print("Loading NYC 311 agency mapping...")
    agency_mapping = load_nyc_311_agency_mapping(str(nyc_311_csv))
    print()

    # Create database session
    db = SessionLocal()

    try:
        # Run the test
        print(f"Starting dispatcher test with n={n}\n")
        print("=" * 80)
        print()

        summary = test_dispatcher_on_tickets(n, data_dir, db, agency_mapping)

        # Print summary
        print()
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Total tickets tested: {summary['total_tickets']}")
        print(f"Successful: {summary['successful']}")
        print(f"Errors: {summary['errors']}")
        print(f"Tickets with expected agency: {summary['tickets_with_expected_agency']}")
        print(f"Correct assignments: {summary['correct_assignments']}")
        print(f"Assignment accuracy: {summary['accuracy_percent']}%")
        print(f"Total time: {summary['total_time_seconds']}s")
        print(f"Average time per ticket: {summary['average_time_seconds']}s")
        print("=" * 80)

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user. Results saved up to this point.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError during test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
