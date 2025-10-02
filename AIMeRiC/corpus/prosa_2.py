import os
import re

import spacy
import pandas as pd
from tqdm import tqdm

from AIMeRiC.escansio.escansor import escaneja

print(f"Carregant el model de Spacy 'ca_core_news_md' (versió {spacy.__version__})...")
nlp = spacy.load("ca_core_news_md", disable=["ner"])
print("Model carregat correctament.")
print("--" * 40)


def etiqueta_wikicorpus():
    path = r"C:\Users\pereg\Downloads\raw.ca"

    for file in tqdm(os.listdir(path)):
        dataframe = pd.DataFrame()
        with open(os.path.join(path, file), "r", encoding="ansi") as f:
            content = f.read()
            content = re.sub(r"(<.*>|ENDOFARTICLE\.)", "", content)  # Elimina les etiquetes HTML
            text = content.split("\n")
            text = [line for line in text if line.strip() != ""]
            for paragraph in text:
                metadata = pd.DataFrame({"id": f"file_{text.index(paragraph)}"}, index=[0])
                try:
                    scan = escaneja(nlp, paragraph, goal=10).desa_prosa_2()
                except Exception as e:
                    #print(f"Error processant el paràgraf: {e}")
                    scan = None
                if scan is not None:
                    # Ajunta els dataframe metadata i scan dins un nou dataframe
                    combined_df = pd.concat([metadata, scan], axis=1)
                    dataframe = pd.concat([dataframe, combined_df], ignore_index=True)
        # Guarda el dataframe a un fitxer CSV
        dataframe.to_csv(f"wikicorpus/{file}.csv", index=False, encoding="utf-8", lineterminator="\n", sep=";")


if __name__ == "__main__":
    etiqueta_wikicorpus()
    print("Etiquetatge completat i guardat a 'wikicorpus_etiquetat.csv'.")
