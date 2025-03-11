# SSCModel: Polkadot Governance Referendum Classification

## Overview
SSCModel (Sequential Semantic Classification Model) is a machine learning model designed to assist in Polkadot governance by identifying referendums that contain explicit requests to vote "NAY." By analyzing referendum titles, this model helps automate governance actions such as triggering automated votes or alerting human moderators for review.

## Features
- Classifies referendum titles into two categories:
  - `0`: Active referendum (default)
  - `1`: Referendum requesting a "vote nay"
- Uses a TensorFlow/Keras-based neural network for text classification.
- Implements custom loss functions and weighting to handle class imbalances.
- Can be used for both real-time inference and batch processing.

---

## Model Architecture
The model is a sequential neural network with the following layers:

| Layer (type)                  | Output Shape       | Param #   |
|--------------------------------|--------------------|-----------|
| TextVectorization              | (None, 128)       | 0         |
| Embedding                      | (None, 128, 32)   | 320,000   |
| Conv1D                         | (None, 126, 32)   | 3,104     |
| GlobalMaxPooling1D             | (None, 32)        | 0         |
| Dense                          | (None, 16)        | 528       |
| Dropout                        | (None, 16)        | 0         |
| Dense (Output Layer)           | (None, 2)         | 34        |

**Total Parameters:** 323,666 (~1.23MB)  
**Trainable Parameters:** 323,666  
**Non-trainable Parameters:** 0  

---

## Installation & Setup
### Requirements
Ensure you have the following dependencies installed:
```sh
pip install tensorflow numpy scikit-learn requests
```

### Download the Repository
```sh
git clone git@github.com:stake-plus/SSCModel.git
cd SSCModel
```

---

## Usage

### 1. Training the Model
To train the model, ensure that `data.csv` is correctly labeled, then run:
```sh
python3 train.py
```
This will train and save the model as `model.keras`.

### 2. Running Inference on Referendum Titles
To classify a single referendum title, run:
```sh
python3 inference.py "YOUR REFERENDUM TITLE HERE"
```
Example output:
```sh
Model prediction: This title indicates a 'vote nay' request.
```

### 3. Automating Data Labeling
To manually label referendum titles:
```sh
python3 data_labeling.py
```
This script iterates through referendum titles and asks for a `0` or `1` label.

### 4. Validating Labeled Data
To validate and correct existing labels:
```sh
python3 data_validate.py
```

### 5. Fetching Referendum Titles from Polkassembly API
To retrieve recent referendum titles for labeling:
```sh
python3 download_titles.py
```
This fetches titles from multiple Polkadot ecosystem networks and saves them in `titles_data/`.

---

## Implementation in an Existing Python Script
To integrate the trained model into another Python project, use:
```python
import tensorflow as tf
import numpy as np

# Load the trained model
model = tf.keras.models.load_model("model.keras", compile=False)

# Preprocess the input title
def preprocess_text(title):
    return np.array([[title]])

# Predict referendum classification
input_title = "Please vote nay"
logits = model.predict(preprocess_text(input_title), verbose=0)
probs = tf.nn.softmax(logits, axis=1).numpy()

# Output result
if np.argmax(probs[0]) == 1:
    print("This title indicates a 'vote nay' request.")
else:
    print("This title does NOT indicate a 'vote nay' request.")
```

---

## Model Performance

### Test Results
Example predictions from the test dataset:

#### Referendums Requesting a Vote Nay (Should be Label `1`)
```
Title: Please vote nay
Prob(class0)=0.0021, Prob(class1)=0.9979 => Prediction=1 | Expected=1, PASS
...
```
#### Normal Referendums (Should be Label `0`)
```
Title: Treasury Proposal by 727.ventures: Polkadot Wink
Prob(class0)=0.9842, Prob(class1)=0.0158 => Prediction=0 | Expected=0, PASS
...
```

The model has demonstrated **high accuracy** in correctly identifying referendums that request a "vote nay."

---

## Contribution
If you’d like to improve the model, contribute new training data, or refine the inference pipeline, feel free to submit a pull request or create an issue on GitHub.

---

## License
This project is open-source and provided under the MIT License.

**Stake Plus - 2025**

