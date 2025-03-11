#!/usr/bin/python3
import sys
import joblib

def main():
    if len(sys.argv) < 2:
        print("Usage: ./inference.py \"Your referendum title here\"")
        sys.exit(1)

    input_text = sys.argv[1]
    model_path = "model.keras"

    model = joblib.load(model_path)

    pred = model.predict([input_text])[0]

    if pred == 1:
        print("Model prediction: This title indicates a 'vote nay' request.")
    else:
        print("Model prediction: This title does NOT indicate a 'vote nay' request.")

if __name__ == "__main__":
    main()
