import cProfile
import pstats
import spacy
from AIMeRiC.escansio.modules.vers import Vers

# Carrega el model spaCy
nlp = spacy.load("ca_core_news_md", disable=["ner"])
sentence = "(Tot és inesperadament absurd."

# Executa cProfile
def run_vers():
    vers = Vers(nlp, sentence, 10, permet_llicencies=True)
    return vers

# Profile
profiler = cProfile.Profile()
profiler.enable()

result = run_vers()

profiler.disable()

# Mostra resultats ordenats per temps acumulat
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(30)

# Top 10 funcions més lentes
stats.print_stats(10)

# Ordenar per nombre de crides
stats.sort_stats('calls')
stats.print_stats(10)

# Veure qui crida a una funció específica
stats.print_callers('accentua')

# Veure a qui crida una funció
stats.print_callees('__patrons__')
