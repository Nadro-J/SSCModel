#!/usr/bin/python3
import csv

def main():
    input_file = "training_data.csv"
    output_rows = []

    with open(input_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames

        for row in reader:
            title = row["title"]
            label = row["label"]
            
            title_lower = title.lower()
            keywords = ["nay", "plz", "please", "vote", "error", "image", "test"]
            
            condition_met = (any(kw in title_lower for kw in keywords) or len(title) < 10)
            
            if condition_met and label != "1":
                print(f"\nTitle: {title}\nCurrent label: {label}")
                while True:
                    user_input = input("Update label? (0 or 1): ")
                    if user_input in ["0", "1"]:
                        row["label"] = user_input
                        break
                    else:
                        print("Invalid input. Please enter 0 or 1.")
            
            output_rows.append(row)

    with open(input_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    print("\nData check complete. Updated labels saved to training_data.csv.")

if __name__ == "__main__":
    main()
