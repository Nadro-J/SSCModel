#!/usr/bin/python3
import csv
import os
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split

def clean_text(txt):
    txt = txt.strip()
    txt = txt.encode("ascii", errors="ignore").decode()
    return txt

def custom_weighted_loss(y_true, y_pred_logits):
    y_true_onehot = tf.one_hot(tf.cast(y_true, tf.int32), depth=2)

    ce_per_sample = tf.nn.softmax_cross_entropy_with_logits(
        labels=y_true_onehot,
        logits=y_pred_logits
    )

    class_weights = tf.constant([1.0, 2.0])
    sample_weights = tf.reduce_sum(class_weights * y_true_onehot, axis=1)

    weighted_ce = ce_per_sample * sample_weights
    return tf.reduce_mean(weighted_ce)

def main():
    learning_rate = 1e-4
    batch_size = 1024
    epochs = 300

    data_file = "data.csv"
    texts, labels = [], []

    with open(data_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            label_val = int(row["label"])
            if label_val not in [0, 1]:
                continue

            txt = clean_text(row["title"])
            if not txt:
                continue

            texts.append(txt)
            labels.append(label_val)

    labels = np.array(labels, dtype="int32")
    if len(texts) == 0:
        print("No valid data found after cleaning. Exiting.")
        return

    unique_labels, counts = np.unique(labels, return_counts=True)
    print(f"Total loaded samples: {len(texts)}")
    print("Label distribution:", dict(zip(unique_labels, counts)))

    X_train, X_val, y_train, y_val = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )
    print("X_train size:", len(X_train), " y_train size:", len(y_train))
    print("X_val size:", len(X_val), " y_val size:", len(y_val))

    max_tokens = 10000
    output_seq_length = 128

    vectorize_layer = tf.keras.layers.TextVectorization(
        max_tokens=max_tokens,
        output_sequence_length=output_seq_length,
        standardize="lower_and_strip_punctuation"
    )
    vectorize_layer.adapt(X_train)

    def make_dataset(text_list, label_arr, bs):
        ds = tf.data.Dataset.from_tensor_slices((text_list, label_arr))
        ds = ds.shuffle(len(text_list), seed=42)
        ds = ds.batch(bs)
        ds = ds.prefetch(tf.data.AUTOTUNE)
        return ds

    train_ds = make_dataset(X_train, y_train, batch_size)
    val_ds = make_dataset(X_val, y_val, batch_size)

    embed_dim = 32
    model = tf.keras.Sequential([
        tf.keras.Input(shape=(1,), dtype=tf.string),
        vectorize_layer,
        tf.keras.layers.Embedding(input_dim=max_tokens, output_dim=embed_dim),
        tf.keras.layers.Conv1D(filters=32, kernel_size=3, activation="relu"),
        tf.keras.layers.GlobalMaxPooling1D(),
        tf.keras.layers.Dense(16, activation="relu"),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(2, activation=None)
    ])

    model.compile(
        loss=custom_weighted_loss,
        optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate, clipnorm=1.0),
        metrics=["accuracy"]
    )

    model.summary()

    class DebugNanCallback(tf.keras.callbacks.Callback):
        def on_train_batch_end(self, batch, logs=None):
            loss_val = logs.get("loss", None)
            if loss_val is None:
                return
            if tf.math.is_nan(loss_val):
                print(f"NaN detected at batch {batch}. Stopping training.")
                self.model.stop_training = True

    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs,
        callbacks=[DebugNanCallback()]
    )

    val_loss, val_acc = model.evaluate(val_ds, verbose=0)
    print(f"\nValidation Loss: {val_loss:.4f}, Validation Accuracy: {val_acc:.4f}")

    model.save("model.keras")
    print(f"Saved model to model.keras.")

if __name__ == "__main__":
    main()
