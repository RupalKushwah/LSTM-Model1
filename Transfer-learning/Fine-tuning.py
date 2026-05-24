import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model, Model, Sequential
from tensorflow.keras.layers import Dense, LSTM, Embedding, Input
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint
from keras.callbacks import EarlyStopping
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.utils import to_categorical
from rdkit import Chem

# Load the pre-trained model
pretrained_model = load_model("ABlayers_LSTM")

dataset_type = "GTP"
# Change to "IDC" when required
 
if dataset_type=="GTP":

    # Load your fine-tuning dataset
    small_df = pd.read_csv(
    r"C:\Users\HI\Desktop\AB_LSTM_SUBMISSION\antibacterial\LSTM_MODEL\GTP_finetuning.csv"
    )

elif dataset_type=="IDC":

    small_df = pd.read_excel(
    r"C:\Users\HI\Desktop\AB_LSTM_SUBMISSION\antibacterial\ftsz_docprojcts\models\IDC_SMILES.xlsx"
    )
# Remove missing values
small_df = small_df.dropna(subset=['SMILES'])

# Assuming the SMILES strings are in a column
raw_text = "\n".join(
small_df['SMILES'].astype(str).str.strip()
)

# Creating mapping for each character to integer
unique_chars = sorted(list(set(raw_text)))

# Maps each unique character as an int
char_to_int = dict((c, i) for i, c in enumerate(unique_chars))

# Int to char dictionary
int_to_char = dict((i, c) for i, c in enumerate(unique_chars))
int_to_char.update({"\\n": -1})

# Summarize the loaded data to provide lengths for preparing datasets
n_chars = len(raw_text)
n_vocab = len(unique_chars)

print("Total number of characters in the file is:", n_chars)
print("Total number of unique characters in the file is:", n_vocab)

# Calculate average sequence length from the dataset
avg_seq_length = sum(len(smiles) for smiles in small_df['SMILES']) // len(small_df)
print("Average sequence length in the dataset is:", avg_seq_length)

# Define sequence length
seq_length = avg_seq_length

# Preparing datasets by matching the dataset lengths
dataX = []
dataY = []

for i in range(0, n_chars - seq_length, 1):
    seq_in = raw_text[i:i + seq_length]
    seq_out = raw_text[i + seq_length]
    dataX.append([char_to_int[char] for char in seq_in])
    dataY.append(char_to_int[seq_out])

n_patterns = len(dataX)
print("Total number of patterns (sequences) is:", n_patterns)

# Reshape X to be [samples, time steps, features]
X = np.reshape(dataX, (n_patterns, seq_length, 1))
# Normalize data
X = X / float(n_vocab)

# One-hot encode the output variable
y = to_categorical(dataY)

# Fine-tuning the model

# Freeze the layers of the pre-trained model
for layer in pretrained_model.layers:
    layer.trainable = False

# Add new layers for fine-tuning
fine_tuned_model = Sequential()
fine_tuned_model.add(LSTM(256, input_shape=(seq_length, 1), return_sequences=True))
fine_tuned_model.add(LSTM(256))
fine_tuned_model.add(Dense(n_vocab, activation='softmax'))

# Compile the fine-tuned model
fine_tuned_model.compile(optimizer=Adam(), loss='categorical_crossentropy', metrics=['accuracy'])

# Model names

if dataset_type=="GTP":

    model_name="FtsZ-GTP-LSTM"

elif dataset_type=="IDC":

    model_name="FtsZ-IDC-LSTM"

# Train the fine-tuned model
checkpoint = ModelCheckpoint(model_name, save_best_only=True)
fine_tuned_model.fit(X, y, epochs=40, batch_size=64, callbacks=[checkpoint])

# Save the fine-tuned model
fine_tuned_model.save(model_name)
