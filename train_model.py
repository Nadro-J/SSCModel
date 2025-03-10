#!/usr/bin/python3
import csv
import os
import random
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split

def clean_text(txt):
    txt = txt.strip()
    txt = txt.encode("ascii", errors="ignore").decode()
    return txt

def main():
    learning_rate = 1e-6
    batch_size = 256

    data_file = "training_data.csv"
    texts, labels = [], []
    
    with open(data_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            label_val = int(row["label"])
            if label_val not in [0, 1]:
                print(f"Warning: encountered label={label_val}, skipping.")
                continue

            txt = clean_text(row["title"])
            if not txt:
                print("Warning: encountered empty text, skipping.")
                continue

            texts.append(txt)
            labels.append(label_val)

    labels = np.array(labels, dtype="int32")

    if len(texts) == 0:
        print("No valid data found. Exiting.")
        return

    unique_labels = set(labels.tolist())
    print(f"Loaded {len(texts)} rows. Unique labels={unique_labels}")

    X_train, X_val, y_train, y_val = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )

    max_tokens = 10000
    output_seq_length = 128

    vectorize_layer = tf.keras.layers.TextVectorization(
        max_tokens=max_tokens,
        output_sequence_length=output_seq_length
    )
    vectorize_layer.adapt(X_train)

    def make_dataset(texts_list, labels_arr, bs):
        ds = tf.data.Dataset.from_tensor_slices((texts_list, labels_arr))
        ds = ds.shuffle(buffer_size=len(texts_list))
        ds = ds.batch(bs).prefetch(tf.data.AUTOTUNE)
        return ds

    train_ds = make_dataset(X_train, y_train, batch_size)
    val_ds = make_dataset(X_val, y_val, batch_size)

    embed_dim = 32

    model = tf.keras.Sequential([
        tf.keras.Input(shape=(1,), dtype=tf.string),
        vectorize_layer,
        tf.keras.layers.Embedding(input_dim=max_tokens, output_dim=embed_dim, mask_zero=True),
        tf.keras.layers.GlobalAveragePooling1D(),
        tf.keras.layers.Dense(16, activation="relu"),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(1, activation="sigmoid")
    ])

    optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate, clipnorm=1.0)

    model.compile(
        loss="binary_crossentropy",
        optimizer=optimizer,
        metrics=["accuracy"]
    )

    print("\n==== Model Summary ====")
    model.summary()

    print("\n==== Trainable Variables ====")
    for var in model.trainable_variables:
        print(f"{var.name}, shape={var.shape}")

    epochs = 50
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs
    )

    val_loss, val_acc = model.evaluate(val_ds, verbose=0)
    print(f"\nValidation Loss: {val_loss:.4f}, Validation Accuracy: {val_acc:.4f}")

    model.save("trained_model.keras")
    print(f"Saved model to ./trained_model.keras.")

if __name__ == "__main__":
    main()
