1.	Using the Code
i.	Sampling from a pre-trained model
ii.	Training a model
iii.	Fine-tuning a model 
Using the code
Sampling from a pre-trained model

In this repository, one pre-trained model was provided that you can use for sampling (stored in the model). This model was trained on 55,308 bioactive molecules from the ChEMBL database for 40 epochs.

Parameters:
•	experiment_name (str): name of the experiment with the pre-trained model you want to sample from (you can find a pre-trained model in the model)
•	stor_dir (str): directory where the models are stored. The sampled SMILES will also be saved there (if write_csv=True)
•	N (int): number of SMILES to sample
•	T (float): sampling temperature
•	epoch (list of int): epoch(s) to use for sampling

Notes:
•	For the provided pre-trained models epoch [40] are provided.
•	The available model and their description are provided in the “model file” 
Training a New Model

Alternatively, if you want to pre-train a model on your data, you will need to execute three steps:
(i) Data collection
(ii) Data processing
(iii) Moddel training. 

Preprocessing
Data can be processed by using preprocessing/main_preprocessor.py:
from main_preprocessor import preprocess_data

preprocess_data(filename_in='../Training data, model_type='AB-LSTM')
Parameters:
•	filename_in (str): name of the file containing the SMILES strings (.csv)
•	model_type (str): name of the chosen generative method
Training Parameters
Section	Parameter	Description	Comments
Model	model	Type	Backpropagation through time
	hidden_units	Number of hidden units	Suggested value: 256 for backward RNN, 
Data	data	Name of the data file	It has to be located in the data/
	encoding_size	Number of different SMILES tokens	44
	molecular_size	Length of string with padding	121
Training	epochs	Number of epochs	Suggested value: 40
	learning_rate	Learning rate	Suggested value: 0.001
	batch_size	Batch size	Suggested value: 1024
Evaluation	samples	Number of generated SMILES after each epoch	
	temp	Sampling temperature	Suggested value: 0.8

Fine-tuning a model
Fine-tuning requires both a pre-trained model and an associated parameter file.
This process was independently conducted for:
(i) the GTP binding site 
(ii) the inter-domain cleft (IDC) of the SaFtsZ protein.

As a result, two specialized models were generated: (i) FtsZ-LSTM-GTP and (ii) FtsZ-LSTM-IDC.
You can start the sampling procedure with _fine_tuning.py
Section	Parameter	Description	Comments
Model	model	Type(LSTM, GRU, BiLSTM)	BPTT
	hidden_units	Number of hidden units	Suggested value: 256
Data	data	Name of the data file	Has to be located in the data/
	encoding_size	Number of different SMILES tokens	55
	molecular_size	Length of string with padding	121
Training	epochs	Number of epochs	Suggested value: 40
	learning_rate	Learning rate	Suggested value: 0.001
	batch_size	Batch size	Suggested value: 64

	temp	Sampling temperature	Suggested value: 0.8

Authors
•	Sapna Nikam (https://github.com/sapnanik/LSTM-Model)
•	Rupal Kushwah (https://github.com/RupalKushwah/LSTM-Model1/tree/main)

Installation

The required dependencies can be installed using:

pip install -r requirements.txt

Alternatively, a create  Conda environment:

conda env create -f Environment/environment.yml

Repository Structure

├── Preprocessing/              
│   └── main_preprocessor.py
│
├── Transfer-learning/        
│   └── Fine-tuning.py
│
├── Generation/              
│   └── Smiles-generation/
│
├── Evaluation/                
│   └── evaluation-metrics
│
├── MODEL/                     
│   └── AB-LSTM
│
├── Environment/               
│
├── dataset/                    # Input datasets
│   └── Table S1.xlsx
│
├── gtp.ipynb                   # GTP-specific notebook
├── idc_model.ipynb             # IDC-specific notebook
├── requirements.txt            # Dependency configuration
├── README.md                   # Documentation


Example Workflow

Step 1: Data preprocessing

python Preprocessing/main_preprocessor.py

Step 2: Train the AB-LSTM model

Use scripts in MODEL/AB-LSTM.py

Step 3: Fine-tuning for site-specific generation

python Transfer-learning/Fine-tuning.py

This generates:

• FtsZ-LSTM-GTP
• FtsZ-LSTM-IDC

Step 4: Generate molecular SMILES

python Generation/Smiles-generation.py

Step 5: Evaluate generated molecules

python Evaluation/evaluation-metrics.py

