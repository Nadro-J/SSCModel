#!/usr/bin/python3
import sys
import numpy as np
import tensorflow as tf

def main():
    if len(sys.argv) < 2:
        print("Usage: ./inference.py \"Your referendum title here\"")
        sys.exit(1)

    input_text = " ".join(sys.argv[1:])

    model_path = "model.keras"
    print(f"Loading model from {model_path}...")
    model = tf.keras.models.load_model(model_path, compile=False)
    print("Model loaded.\n")

    input_tensor = tf.constant([[input_text]], dtype=tf.string)

    logits = model.predict(input_tensor, verbose=0)
    probs = tf.nn.softmax(logits, axis=1).numpy()
    pred_label = int(np.argmax(probs[0]))

    if pred_label == 1:
        print("Model prediction: This title indicates a 'vote nay' request.")
    else:
        print("Model prediction: This title does NOT indicate a 'vote nay' request.")

if __name__ == "__main__":
    main()
