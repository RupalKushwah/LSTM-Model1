import pandas as pd
import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit import DataStructs
from rdkit.Chem.Scaffolds import MurckoScaffold

from scipy.linalg import sqrtm
from scipy.stats import entropy

# Load the CSV file containing the generated SMILES strings
generated_file = "generated_smiles.csv"
training_file = "training_smiles.csv"

generated_df = pd.read_csv(
    generated_file
)

training_df = pd.read_csv(
    training_file
)

generated_smiles = generated_df[
    'SMILES'
].dropna().astype(str).tolist()

training_smiles = training_df[
    'SMILES'
].dropna().astype(str).tolist()

# Function to convert SMILES to molecule object
def smiles_to_molecule(smiles):
    return Chem.MolFromSmiles(smiles)

# Convert SMILES to Morgan fingerprint
def smiles_to_fingerprint(smiles):
    mol = smiles_to_molecule(smiles)
    if mol:
        return AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)
    return None

# Compute Morgan fingerprints for FCD
def get_fingerprints(smiles_list):
    fps = []
    for smi in smiles_list:
        mol = smiles_to_molecule(smi)
        if mol:
            fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)
            arr = np.zeros((2048,))
            DataStructs.ConvertToNumpyArray(fp, arr)
            fps.append(arr)
    return np.array(fps)

# Fréchet Distance between 

def frechet_distance(mu1, sigma1, mu2, sigma2):
    diff = mu1 - mu2
    covmean, _ = sqrtm(sigma1 @ sigma2, disp=False)
    if np.iscomplexobj(covmean):
        covmean = covmean.real
    return np.dot(diff, diff) + np.trace(sigma1 + sigma2 - 2 * covmean)

# Validity: % of valid SMILES
def calculate_validity(smiles_list):

    valid_smiles = [
        smiles
        for smiles in smiles_list
        if smiles_to_molecule(smiles) is not None
    ]

    if len(smiles_list) == 0:
        return 0, []

    validity_percentage = (
        len(valid_smiles) /
        len(smiles_list)
    ) * 100

    return validity_percentage, valid_smiles
# Uniqueness: % of unique SMILES
def calculate_uniqueness(smiles_list):

    unique_smiles = set(
        smiles_list
    )

    if len(smiles_list) == 0:
        return 0, set()

    uniqueness_percentage = (
        len(unique_smiles) /
        len(smiles_list)
    ) * 100

    return uniqueness_percentage, unique_smiles

def calculate_novelty(generated_smiles, training_smiles):

    training_set = set(training_smiles)

    if len(generated_smiles)==0:
        return 0

    novelty_count = sum(

        1
        for smiles in generated_smiles
        if smiles not in training_set
    )

    novelty_percentage = (
        novelty_count /
        len(generated_smiles)
    )*100

    return novelty_percentage

# Internal diversity using 1 - Tanimoto similarity
def calculate_internal_diversity(smiles_list):
    fingerprints = [smiles_to_fingerprint(smiles) for smiles in smiles_list]
    valid_fingerprints = [fp for fp in fingerprints if fp is not None]

    if len(valid_fingerprints) < 2:
        return 0

    similarities = []
    for i in range(len(valid_fingerprints)):
        for j in range(i + 1, len(valid_fingerprints)):
            similarity = DataStructs.TanimotoSimilarity(valid_fingerprints[i], valid_fingerprints[j])
            similarities.append(similarity)

    average_similarity = np.mean(similarities)
    diversity = 1 - average_similarity
    return diversity

# FCD: Fréchet ChemNet Distance
def calculate_fcd(generated_smiles, training_smiles):
    generated_fps = get_fingerprints(generated_smiles)
    training_fps = get_fingerprints(training_smiles)

    mu_generated = np.mean(generated_fps, axis=0)
    sigma_generated = np.cov(generated_fps, rowvar=False)

    mu_training = np.mean(training_fps, axis=0)
    sigma_training = np.cov(training_fps, rowvar=False)

    return frechet_distance(mu_generated, sigma_generated, mu_training, sigma_training)

# Nearest Neighbor Similarity

def calculate_snn(
generated_smiles,
training_smiles
):

    similarities=[]

    for gen in generated_smiles:

        gen_fp=smiles_to_fingerprint(gen)

        if gen_fp:

            max_similarity=max(

            DataStructs.TanimotoSimilarity(
            gen_fp,
            smiles_to_fingerprint(
            train
            )
            )

            for train in training_smiles

            if smiles_to_fingerprint(
            train
            ) is not None

            )

            similarities.append(
            max_similarity
            )

    return np.mean(
    similarities
    )
# Scaffold Diversity

def calculate_scaffold_diversity(
smiles_list
):

    scaffolds=[]

    for smiles in smiles_list:

        mol=smiles_to_molecule(
        smiles
        )

        if mol:

            scaffold=MurckoScaffold.MurckoScaffoldSmiles(
            mol=mol
            )

            scaffolds.append(
            scaffold
            )

    if len(scaffolds)==0:

        return 0

    return len(
        set(scaffolds)
    )/len(scaffolds)

# KL divergence

def calculate_kl_divergence(
generated_smiles,
training_smiles
):

    generated_lengths=[
    len(x)
    for x in generated_smiles
    ]

    training_lengths=[
    len(x)
    for x in training_smiles
    ]

    hist_gen,_=np.histogram(
    generated_lengths,
    bins=20,
    density=True
    )

    hist_train,_=np.histogram(
    training_lengths,
    bins=20,
    density=True
    )

    hist_gen+=1e-10
    hist_train+=1e-10

    return entropy(
    hist_gen,
    hist_train
    )

# Evaluation
# ==========================================

validity,valid_smiles=calculate_validity(
generated_smiles
)

print(f"Validity: {validity:.2f}%")

uniqueness,_=calculate_uniqueness(
generated_smiles
)

print(f"Uniqueness: {uniqueness:.2f}%")

novelty=calculate_novelty(
generated_smiles,
training_smiles
)

print(f"Novelty: {novelty:.2f}%")

diversity=calculate_internal_diversity(
valid_smiles
)

print(f"Internal Diversity: {diversity:.4f}")

fcd=calculate_fcd(
generated_smiles,
training_smiles
)

print(f"FCD: {fcd:.4f}")

snn=calculate_snn(
generated_smiles,
training_smiles
)

print(f"SNN: {snn:.4f}")

scaffold=calculate_scaffold_diversity(
generated_smiles
)

print(f"Scaffold Diversity: {scaffold:.4f}")

kl=calculate_kl_divergence(
generated_smiles,
training_smiles
)
print(f"KL Divergence: {kl:.4f}")
