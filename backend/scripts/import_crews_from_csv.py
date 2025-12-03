#!/usr/bin/env python3
"""
Script to import support crews from a CSV file into the database.

Usage:
    python scripts/import_crews_from_csv.py <csv_file_path>

CSV Format:
    team_name,description,crew_type,status,lat,lng
"""

import sys
import csv
from pathlib import Path

# Add parent directory to path to import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from geoalchemy2.elements import WKTElement

from src.database import SessionLocal, engine
from src.models.civitas import SupportCrew, SupportCrewType, SupportCrewStatus


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


def import_crews_from_csv(csv_file_path: str):
    """Import support crews from a CSV file."""
    if not Path(csv_file_path).exists():
        print(f"Error: File {csv_file_path} not found")
        sys.exit(1)

    db = SessionLocal()
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            # Validate required columns
            required_columns = {'team_name', 'crew_type', 'status'}
            if not required_columns.issubset(reader.fieldnames):
                print(f"Error: CSV must contain columns: {required_columns}")
                print(f"Found columns: {reader.fieldnames}")
                sys.exit(1)

            crews_created = 0
            crews_failed = 0

            for row_num, row in enumerate(reader, start=2):  # Start at 2 (1 for header)
                try:
                    # Parse crew_type
                    crew_type_str = row['crew_type'].lower().strip()
                    try:
                        crew_type = SupportCrewType(crew_type_str)
                    except ValueError:
                        print(f"Warning (row {row_num}): Invalid crew_type '{row['crew_type']}', skipping")
                        crews_failed += 1
                        continue

                    # Parse status
                    status_str = row['status'].lower().strip()
                    try:
                        status = SupportCrewStatus(status_str)
                    except ValueError:
                        print(f"Warning (row {row_num}): Invalid status '{row['status']}', defaulting to 'active'")
                        status = SupportCrewStatus.ACTIVE

                    # Parse location
                    location_coordinates = None
                    if 'lat' in row and 'lng' in row:
                        location_coordinates = parse_coordinates(row['lat'], row['lng'])

                    # Parse description (optional)
                    description = row.get('description', '').strip() if row.get('description') else None

                    # Create crew
                    crew = SupportCrew(
                        team_name=row['team_name'].strip(),
                        description=description,
                        crew_type=crew_type,
                        status=status,
                        location_coordinates=location_coordinates,
                    )

                    db.add(crew)
                    db.commit()
                    crews_created += 1
                    print(f"Created crew (row {row_num}): {crew.team_name} ({crew.crew_type.value})")

                except Exception as e:
                    db.rollback()
                    crews_failed += 1
                    print(f"Failed to create crew (row {row_num}): {e}")

            print(f"\n{'='*60}")
            print(f"Import complete!")
            print(f"Successfully created: {crews_created} crew(s)")
            print(f"Failed: {crews_failed} crew(s)")
            print(f"{'='*60}")

    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/import_crews_from_csv.py <csv_file_path>")
        print("\nExample:")
        print("  python scripts/import_crews_from_csv.py data/sample_crews.csv")
        sys.exit(1)

    import_crews_from_csv(sys.argv[1])
