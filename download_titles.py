#!/usr/bin/env python3

import requests
import os

def fetch_referendum_titles(network, listing_limit=1000000):
    base_url = "https://api.polkassembly.io/api/v1/latest-activity/all-posts"
    headers = {
        "x-network": network
    }
    params = {
        "govType": "open_gov",
        "listingLimit": listing_limit
    }

    try:
        resp = requests.get(base_url, headers=headers, params=params, timeout=900)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"Error fetching data for {network}: {e}")
        print("Response text was:", resp.text if 'resp' in locals() else "No response")
        return []

    if not isinstance(data, dict) or "posts" not in data:
        print(f"Unexpected response format for network '{network}'. Response:\n{data}")
        return []

    all_titles = []
    for post in data["posts"]:
        if post.get("type", "") == "ReferendumV2":
            title = post.get("title")
            if title and isinstance(title, str):
                all_titles.append(title.strip())

    return all_titles

def main():
    networks = [
        "polkadot",
        "kusama",
        "moonbeam",
        "moonriver",
        "hydradx",
        "centrifuge",
        "kilt",
        "polimec"
    ]

    os.makedirs("titles_data", exist_ok=True)

    for net in networks:
        print(f"\nFetching ReferendumV2 titles for network: {net}")
        titles = fetch_referendum_titles(net)
        if not titles:
            print(f"No ReferendumV2 titles found (or an error occurred) for {net}.")
            continue

        out_file = os.path.join("titles_data", f"{net}.txt")
        with open(out_file, "w", encoding="utf-8") as f:
            for t in titles:
                f.write(t + "\n")

        print(f"Saved {len(titles)} ReferendumV2 titles to {out_file}")

if __name__ == "__main__":
    main()
