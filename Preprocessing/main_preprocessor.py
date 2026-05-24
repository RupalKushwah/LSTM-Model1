#!/usr/bin/env python
# coding: utf-8

import os
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from tqdm import tqdm_notebook
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
from keras.utils import to_categorical

# Read the CSV file 
# Load your dataset
DF = pd.read_csv(r"C:\Users\HI\Desktop\AB_LSTM_SUBMISSION\antibacterial\LSTM_MODEL\ANTIBACTERIAL_DATA.csv")

# Remove missing values
DF = DF.dropna(subset=['SMILES'])

# Extract SMILES
Smiles_list = DF['SMILES'].astype(str).tolist()

# Maximum length
max_length = max(len(smiles) for smiles in Smiles_list)
print("Maximum length of SMILES strings:", max_length)

# Convert SMILES into text
raw_text = "\n".join(DF['SMILES'].str.strip())

# Character mapping
unique_chars = sorted(list(set(raw_text)))

char_to_int = {c:i for i,c in enumerate(unique_chars)}
int_to_char = {i:c for i,c in enumerate(unique_chars)}

# Number of characters and Vocabulary sizes
n_chars = len(raw_text)
n_vocab = len(unique_chars)

print("Vocabulary size:", n_vocab)

# Average sequence length
avg_seq_length = sum(len(smiles) for smiles in Smiles_list)//len(Smiles_list)

print("Average sequence length:", avg_seq_length)

seq_length = avg_seq_length

# Prepare Datasets
dataX=[]
dataY=[]

for i in range(0,n_chars-seq_length):

    seq_in=raw_text[i:i+seq_length]
    seq_out=raw_text[i+seq_length]

    dataX.append([char_to_int[char] for char in seq_in])
    dataY.append(char_to_int[seq_out])

n_patterns=len(dataX)
print("Total number of patterns:",n_patterns)

# Reshape X To be [samples, time steps, features]
X=np.reshape(dataX,(n_patterns,seq_length,1))

# Normalize data
X=X/float(n_vocab)

# One-hot encode the output variable
y=to_categorical(dataY)
