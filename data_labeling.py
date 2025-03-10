#!/usr/bin/python3
import os
import csv

def main():
    input_dir = "titles_data"
    output_csv = "training_data.csv"

    with open(output_csv, mode="w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["title", "label"])

        for txt_file in os.listdir(input_dir):
            if txt_file.endswith(".txt"):
                file_path = os.path.join(input_dir, txt_file)
                print(f"Reading {file_path}...")

                with open(file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        title = line.strip()
                        if not title:
                            continue
                        while True:
                            user_input = input(f"Title: {title}\nLabel? (0=active / 1=requested-nay): ")
                            if user_input in ["0", "1"]:
                                writer.writerow([title, user_input])
                                break
                            else:
                                print("Please enter either 0 or 1.")

    print(f"\nData labeling complete. All labeled data saved to {output_csv}.")

if __name__ == "__main__":
    main()
