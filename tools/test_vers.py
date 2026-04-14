# Script de prova per al vers de control
# Prova: "Sol, i de dol, i vetusta gonella" (esperat: 4+6)

from importlib import import_module
import traceback

text = "Si de la mar faig el meu elixir,"

print(f"Vers de prova: {text!r}")


from AIMeRiC.escansio.modules.vers import Vers
import spacy

nlp = spacy.load("ca_core_news_md", disable=["ner"])  # pot fallar si el model no està instal·lat
v = Vers(nlp, text, 10, permet_llicencies=True)
v.mostra()


print('\nTest complet.')

