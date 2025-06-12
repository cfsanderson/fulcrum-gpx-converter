# GPX to Fulcrum Geometry Updater

This tool processes GPX track files and updates corresponding records in Fulcrum with the track geometry. It's particularly useful for syncing GPS track data from devices like Garmin with Fulcrum records.

## Features

- Processes multiple GPX files in a directory
- Updates both local CSV and Fulcrum records
- Matches GPX files to records using date-based filenames (YYYY-MM-DD.gpx)
- Preserves existing record data while updating geometry
- Provides detailed logging of all operations

## Prerequisites

- Python 3.6+
- Required Python packages: `gpxpy`, `requests`
- Fulcrum API token with write access
- GPX files named in `YYYY-MM-DD.gpx` format
- CSV file with matching dates in the first column and Fulcrum record IDs in the second column

## Installation

1. Clone this repository or download the script
2. Install required packages:
   ```bash
   pip install gpxpy requests
   ```
3. Create a `.fulcrum_api_token` file in the project root containing your Fulcrum API token

## Project Structure

```
.
├── fulcrum_gpx_convert.py  # Main script
├── .fulcrum_api_token      # Contains Fulcrum API token
├── data.csv               # CSV with Fulcrum record data
└── garmin-GPX-files/      # Directory containing GPX files (YYYY-MM-DD.gpx)
    ├── 2024-01-15.gpx
    └── 2024-01-16.gpx
```

## CSV Format

The `data.csv` file should have the following structure (at minimum):

```csv
day,fulcrum_id,geometry,...
2024-01-15,abc123-123-456-789,...
2024-01-16,def456-789-012-345,...
```

- `day`: Date in YYYY-MM-DD format (must match GPX filenames)
- `fulcrum_id`: The Fulcrum record ID to update
- `geometry`: Will be updated with WKT LINESTRING format

## Usage

1. Place your GPX files in the `garmin-GPX-files` directory with names like `YYYY-MM-DD.gpx`
2. Ensure your `data.csv` has matching dates in the first column
3. Run the script:
   ```bash
   python fulcrum_gpx_convert.py
   ```

The script will:
1. Read all GPX files in the directory
2. Match them with records in the CSV by date
3. Update both the local CSV and Fulcrum records with the track geometry
4. Print detailed logs of all operations

## Output

The script provides detailed output, for example:

```
=== GPX to Fulcrum Geometry Updater ===
Found 2 records in CSV with dates: 2024-01-15, 2024-01-16

Processing GPX files in /path/to/garmin-GPX-files...

Processing 2024-01-15.gpx (Date: 2024-01-15):
  Extracted 120 points
  ✅ Updated Fulcrum record abc123-123-456-789

Processing 2024-01-16.gpx (Date: 2024-01-16):
  Extracted 95 points
  ✅ Updated Fulcrum record def456-789-012-345

✅ Updated 2 records in /path/to/runs/run.csv
```

## Error Handling

The script handles various error conditions:
- Missing or invalid API token
- Missing or malformed CSV file
- Missing or unreadable GPX files
- Network issues when communicating with Fulcrum API
- Mismatched dates between GPX files and CSV

## License

[MIT](https://choosealicense.com/licenses/mit/)