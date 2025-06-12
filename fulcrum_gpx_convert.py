import gpxpy
import json
import requests
import csv
import os
import sys
from pathlib import Path

def extract_linestring_from_gpx(gpx_path):
    """Extract coordinates from a GPX file and return as a list of [lon, lat] pairs."""
    with open(gpx_path, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)
    coordinates = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                coordinates.append([point.longitude, point.latitude])
    return coordinates

def linestring_wkt(coords):
    """Convert coordinates to WKT LINESTRING format."""
    if not coords:
        return ''
    coord_str = ', '.join(f"{lon} {lat}" for lon, lat in coords)
    return f"LINESTRING({coord_str})"

def read_api_token():
    """Read the Fulcrum API token from .fulcrum_api_token file."""
    token_file = ".fulcrum_api_token"
    if os.path.isfile(token_file):
        with open(token_file, "r") as f:
            token = f.read().strip()
            if token:
                return token
    print(f"API token file '{token_file}' not found or empty.")
    sys.exit(1)

def update_fulcrum_record(record_id, coords, api_token):
    """Update a Fulcrum record's geometry."""
    url = f"https://api.fulcrumapp.com/api/v2/records/{record_id}.json"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-ApiToken": api_token
    }

    # Fetch existing record data
    get_resp = requests.get(url, headers=headers)
    if get_resp.status_code != 200:
        print(f"  ❌ Failed to fetch record {record_id}: {get_resp.status_code}")
        print(f"  {get_resp.text}")
        return False

    record_data = get_resp.json()["record"]
    
    # Prepare payload with existing form values and new geometry
    payload = {
        "record": {
            "form_values": record_data.get("form_values", {}),
            "geometry": {
                "type": "LineString",
                "coordinates": coords
            }
        }
    }

    # Update the record
    patch_resp = requests.patch(url, headers=headers, json=payload)
    if patch_resp.status_code == 200:
        print(f"  ✅ Updated Fulcrum record {record_id}")
        return True
    else:
        print(f"  ❌ Error updating record {record_id}: {patch_resp.status_code}")
        print(f"  {patch_resp.text}")
        return False

def main():
    print("=== GPX to Fulcrum Geometry Updater ===")
    
    # Set up paths
    base_dir = Path(__file__).parent
    gpx_dir = base_dir / "garmin-GPX-files"
    csv_path = base_dir / "data.csv"
    
    # Check if directories and files exist
    if not gpx_dir.exists() or not gpx_dir.is_dir():
        print(f"Error: Directory not found: {gpx_dir}")
        sys.exit(1)
    if not csv_path.exists():
        print(f"Error: CSV file not found: {csv_path}")
        sys.exit(1)

    # Read API token
    try:
        api_token = read_api_token()
    except Exception as e:
        print(f"Error reading API token: {e}")
        sys.exit(1)

    # Read CSV file
    try:
        with open(csv_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)  # Read header
            rows = list(reader)
            
            # Find column indices
            try:
                day_idx = 0  # First column is day number
                fulcrum_id_idx = 1  # Second column is fulcrum_id
                geometry_idx = header.index('geometry')
            except ValueError as e:
                print(f"Error: Required column not found in CSV: {e}")
                sys.exit(1)
            
            # Create mapping from date string to row index and fulcrum_id
            day_to_row = {}
            for i, row in enumerate(rows):
                if len(row) > max(day_idx, fulcrum_id_idx):
                    # Use the exact value from the day column as the key
                    day_to_row[row[day_idx]] = (i, row[fulcrum_id_idx])
                    
            print(f"Found {len(day_to_row)} records in CSV with dates: {', '.join(sorted(day_to_row.keys())[:5])}{'...' if len(day_to_row) > 5 else ''}")
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        sys.exit(1)

    # Process GPX files
    print(f"\nProcessing GPX files in {gpx_dir}...")
    gpx_files = list(gpx_dir.glob("*.gpx")) + list(gpx_dir.glob("*.GPX"))
    
    if not gpx_files:
        print("No GPX files found in the directory.")
        return

    updated_count = 0
    for gpx_file in sorted(gpx_files):
        # Get date from filename (without extension)
        date_str = gpx_file.stem
        print(f"\nProcessing {gpx_file.name} (Date: {date_str}):")
        
        # Find matching row in CSV (exact match for the date in the 'day' column)
        if date_str not in day_to_row:
            print(f"  ⚠️  No matching date {date_str} in CSV 'day' column")
            continue
            
        row_idx, fulcrum_id = day_to_row[date_str]
        if not fulcrum_id:
            print(f"  ⚠️  No fulcrum_id for date {date_str}")
            continue
        
        # Extract coordinates from GPX
        try:
            coords = extract_linestring_from_gpx(gpx_file)
            if not coords:
                print("  ⚠️  No coordinates found in GPX file")
                continue
            print(f"  Extracted {len(coords)} points")
            
            # Update Fulcrum record
            if update_fulcrum_record(fulcrum_id, coords, api_token):
                # Update local CSV with WKT geometry
                wkt_geom = linestring_wkt(coords)
                if len(rows[row_idx]) > geometry_idx:
                    rows[row_idx][geometry_idx] = wkt_geom
                updated_count += 1
                
        except Exception as e:
            print(f"  ❌ Error processing {gpx_file.name}: {e}")
    
    # Save updated CSV
    if updated_count > 0:
        try:
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(rows)
            print(f"\n✅ Updated {updated_count} records in {csv_path}")
        except Exception as e:
            print(f"\n❌ Error saving CSV file: {e}")
    else:
        print("\nNo updates were made.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExited.")
