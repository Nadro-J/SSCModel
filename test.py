#!/usr/bin/python3
import random
import numpy as np
import tensorflow as tf

def clean_text(txt):
    txt = txt.strip()
    txt = txt.encode("ascii", errors="ignore").decode()
    return txt

def random_extras():
    extras = ["!", "??", "...", "!!!", " [ERROR]", " (WRONG)", "", "", "", ""]
    return random.choice(extras)

def randomize_title(base_title):
    text = base_title
    if "nay" in text.lower():
        if random.random() < 0.5:
            text = text.replace("nay", "NAY").replace("Nay", "NAY")
    if "vote" in text.lower():
        if random.random() < 0.5:
            text = text.replace("vote", "VOTE").replace("Vote", "VOTE")

    if random.random() < 0.3:
        text = random_extras() + " " + text
    if random.random() < 0.3:
        text = text + " " + random_extras()

    text = clean_text(text)
    return text.strip()

def main():
    model_path = "model.keras"
    print(f"Loading model from {model_path} ...")
    model = tf.keras.models.load_model(model_path, compile=False)
    print("Model loaded.\n")

    base_titles = [
        "Please vote nay",
        "Please vote nay, thank you!",
        "Vote nay on this",
        "Posted in error please vote nay",
        "Wrong amount vote nay",
        "Pre-Image error, vote NAY",
        "Error! Please vote NAY",
        "THIS PROPOSAL IS AN ERROR. PLEASE IGNORE: THE AMOUNT IS NOT CORRECT. PLEASE VOTE NAY.",
        "VOTE NAY - pre image error",
        "Wrong preimage - Please vote NAY",
        "Preimage removed - referendum revoked, VOTE NAY",
        "Please ignore - created in error, vote nay",
        "Mistake in pre-image - please vote NAY",
        "Please vote NAY - Resubmitted as #1014",
        "TEST Bounty Please Vote For NAY !",
        "Preimage unnoted, to be resubmitted [Please vote NAY]",
        "Wrong Call Data Please Vote NAY",
        "Proposal posted in error, kindly vote nay",
        "VOTE NAY. Wrong currency - resubmitting as stables",
        "Wrong track - please vote nay",
        "Error - vote NAY",
        "Please vote no, wrong preimage"
    ]

    num_tests = 50
    test_titles = []
    for _ in range(num_tests):
        base_choice = random.choice(base_titles)
        new_title = randomize_title(base_choice)
        test_titles.append(new_title)

    test_titles_tensor = tf.constant([[t] for t in test_titles], dtype=tf.string)

    print(f"Running inference on {num_tests} randomized titles...")
    logits = model.predict(test_titles_tensor, batch_size=1, verbose=0)
    probs = tf.nn.softmax(logits, axis=1).numpy()

    for title, p in zip(test_titles, probs):
        pred_label = np.argmax(p)
        outcome = "PASS" if pred_label == 1 else "FAIL"
        print(f"Title: {title}\nProb(0)={p[0]:.4f}, Prob(1)={p[1]:.4f} => Pred={pred_label}, {outcome}\n")

if __name__ == "__main__":
    main()
