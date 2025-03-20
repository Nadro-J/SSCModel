#!/usr/bin/env python3
import os
import csv
import json
import time
import requests
import argparse
from bs4 import BeautifulSoup
import re
from rejection_patterns import RejectionPattern

NETWORKS = ["polkadot", "kusama", "moonbeam"]
OUTPUT_DIR = "referendum_data"
REQUEST_DELAY = 0.5  # Delay between API requests in seconds
MAX_RETRIES = 3      # Maximum number of retries for failed requests


def html_to_text(html_content):
    """Convert HTML content to plain text."""
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    return re.sub(r'\s+', ' ', text).strip()


def fetch_referendum_details(ref_id, network="polkadot", retries=MAX_RETRIES):
    """Fetch details for a specific referendum from Polkassembly API."""
    url = "https://api.polkassembly.io/api/v1/posts/on-chain-post"
    params = {
        "postId": ref_id,
        "proposalType": "referendums_v2"
    }
    headers = {
        "x-network": network
    }

    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            if not data:
                print(f"Referendum {ref_id} not found or has no data")
                return None

            return data
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                print(f"Error fetching referendum {ref_id}, retrying ({attempt + 1}/{retries}): {e}")
                time.sleep(1 + attempt)  # Exponential backoff
            else:
                print(f"Failed to fetch referendum {ref_id} after {retries} attempts: {e}")
                return None


def download_referendum_data(start_id=1, end_id=1500, network="polkadot", output_dir=OUTPUT_DIR):
    """Download details for referendums and save to CSV file."""
    # Set up directories
    os.makedirs(output_dir, exist_ok=True)

    # Create output CSV file
    csv_file = os.path.join(output_dir, f"{network}_referendums.csv")

    # Create JSON directory for raw data
    json_dir = os.path.join(output_dir, network, "json")
    os.makedirs(json_dir, exist_ok=True)

    # Initialize the nay vote detector
    detector = RejectionPattern()

    # Check if the CSV exists and has data
    existing_ids = set()
    if os.path.exists(csv_file):
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("id") and row["id"].isdigit():
                    existing_ids.add(int(row["id"]))
        print(f"Found {len(existing_ids)} existing records in {csv_file}")

    # Headers for the CSV file
    headers = ["id", "title", "content", "is_nay_request", "confidence", "explanation", "status", "created_at", "proposer"]

    # Collection of new rows to append
    new_rows = []

    for ref_id in range(start_id, end_id + 1):
        if ref_id in existing_ids:
            print(f"\rSkipping referendum {ref_id} (already processed)...", end="")
            continue

        print(f"\rFetching referendum {ref_id}/{end_id}...", end="")

        data = fetch_referendum_details(ref_id, network)
        if not data:
            time.sleep(REQUEST_DELAY)
            continue

        # Save raw JSON data
        json_file = os.path.join(json_dir, f"referendum_{ref_id}.json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        # Extract basic data
        title = data.get("title", "")
        content = html_to_text(data.get("content", ""))

        # Apply NayVoteDetector
        result = detector.detect(title, content[:100])

        row = {
            "id": str(data.get("post_id", "")),
            "title": title,
            "content": content[:100],  # Limit to 200 characters as requested
            "is_nay_request": "1" if result["is_nay_request"] else "0",
            "confidence": str(result["confidence"]),
            "explanation": result["explanation"],
            "status": data.get("status", ""),
            "created_at": data.get("created_at", ""),
            "proposer": data.get("proposer", "")
        }

        new_rows.append(row)

        # Be nice to the API
        time.sleep(REQUEST_DELAY)

    # Write all new rows to the CSV file
    if new_rows:
        file_exists = os.path.exists(csv_file) and os.path.getsize(csv_file) > 0

        with open(csv_file, "a" if file_exists else "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)

            if not file_exists:
                writer.writeheader()

            writer.writerows(new_rows)

        print(f"\nAdded {len(new_rows)} new records to {csv_file}")
    else:
        print(f"\nNo new records to add to {csv_file}")


def process_json_files(network="polkadot", json_dir=None, output_dir=OUTPUT_DIR):
    """Process existing JSON files to create a CSV file."""
    if json_dir is None:
        json_dir = os.path.join(output_dir, network, "json")

    if not os.path.exists(json_dir):
        print(f"Error: JSON directory {json_dir} does not exist.")
        return

    # Initialize the nay vote detector
    detector = RejectionPattern()

    # Create output CSV file
    csv_file = os.path.join(output_dir, f"{network}_referendums.csv")

    # Check if the CSV exists and has data
    existing_ids = set()
    if os.path.exists(csv_file):
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("id") and row["id"].isdigit():
                    existing_ids.add(int(row["id"]))
        print(f"Found {len(existing_ids)} existing records in {csv_file}")

    # Headers for the CSV file
    headers = ["id", "title", "content", "is_nay_request", "confidence", "explanation", "status", "created_at", "proposer"]

    # Find all JSON files
    json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]
    total_files = len(json_files)

    print(f"Found {total_files} JSON files in {json_dir}")

    # Collection of new rows to append
    new_rows = []

    for i, json_file in enumerate(json_files):
        # Extract referendum ID from filename
        ref_id = None
        match = re.search(r'referendum_(\d+)\.json', json_file)
        if match:
            ref_id = int(match.group(1))
        else:
            print(f"Skipping file with invalid name format: {json_file}")
            continue

        if ref_id in existing_ids:
            print(f"\rSkipping referendum {ref_id} (already in CSV)...", end="")
            continue

        print(f"\rProcessing file {i + 1}/{total_files}: {json_file}...", end="")

        # Read JSON file
        file_path = os.path.join(json_dir, json_file)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Extract data
            title = data.get("title", "")
            content = html_to_text(data.get("content", ""))

            # Apply NayVoteDetector
            result = detector.detect(title, content[:100])

            # Extract basic data
            row = {
                "id": str(data.get("post_id", "")),
                "title": title,
                "content": content[:100],  # Limit to 200 characters as requested
                "is_nay_request": "1" if result["is_nay_request"] else "0",
                "confidence": str(result["confidence"]),
                "explanation": result["explanation"],
                "status": data.get("status", ""),
                "created_at": data.get("created_at", ""),
                "proposer": data.get("proposer", "")
            }

            new_rows.append(row)

        except Exception as e:
            print(f"\nError processing {json_file}: {e}")

    # Write all new rows to the CSV file
    if new_rows:
        file_exists = os.path.exists(csv_file) and os.path.getsize(csv_file) > 0

        with open(csv_file, "a" if file_exists else "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)

            if not file_exists:
                writer.writeheader()

            writer.writerows(new_rows)

        print(f"\nAdded {len(new_rows)} new records to {csv_file}")
    else:
        print(f"\nNo new records to add to {csv_file}")


def main():
    parser = argparse.ArgumentParser(description="Download referendum data")
    parser.add_argument("--network", choices=NETWORKS, default="polkadot", help="Network to process")
    parser.add_argument("--start", type=int, default=1, help="Starting referendum ID")
    parser.add_argument("--end", type=int, default=1500, help="Ending referendum ID")
    parser.add_argument("--output", default=OUTPUT_DIR, help="Output directory")
    parser.add_argument("--process-json", action="store_true", help="Process existing JSON files instead of downloading")
    parser.add_argument("--json-dir", help="Directory containing JSON files (optional)")

    args = parser.parse_args()

    if args.process_json:
        print(f"Processing existing JSON files for {args.network}...")
        process_json_files(
            network=args.network,
            json_dir=args.json_dir,
            output_dir=args.output
        )
    else:
        print(f"Processing {args.network} network (IDs {args.start}-{args.end})...")
        download_referendum_data(
            start_id=args.start,
            end_id=args.end,
            network=args.network,
            output_dir=args.output
        )


if __name__ == "__main__":
    main()
