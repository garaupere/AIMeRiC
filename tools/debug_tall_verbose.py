"""Script de diagnòstic per comprendre per què `tall()` retorna None.
Utilitza la classe `Vers` si el model spaCy està disponible; si no, mostra un missatge.
"""

import sys
# Afegim el directori del projecte al sys.path per poder importar el paquet AIMeRiC
PROJECT_ROOT = r"c:\PhD Thesis\AIMeRiC"
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from AIMeRiC.escansio.modules.vers import Vers
import spacy
from AIMeRiC.escansio.modules.utils.decasillab import troba_tall_posible, tall
import sys as _sys

# Acceptem el text per argument; si no, fem servir un valor per defecte
text = _sys.argv[1] if len(_sys.argv) > 1 else "beneirà els qui temen el seu nom,"
print(f"Vers a diagnosticar: {text!r}\n")

try:
    nlp = spacy.load("ca_core_news_md", disable=["ner"])  # pot fallar si el model no està instal·lat
except Exception as e:
    print("No s'ha pogut carregar el model spaCy 'ca_core_news_md' al teu entorn.\n", e)
    raise

# Creem un vers en mode minimal per poder fer una traça pas a pas
v = Vers(nlp, text, 10, permet_llicencies=True, minimal=True)

def print_state(stage: str, vers_obj):
    print(f"\n== Estat després de: {stage} ==")
    print('posicio_tall:', getattr(vers_obj, 'posicio_tall', None))
    print('subdivisio:', getattr(vers_obj, 'subdivisio', None))
    print('patro_metric:', getattr(vers_obj, 'patro_metric', None))
    print('patro_ritmic:', getattr(vers_obj, 'patro_ritmic', None))
    print('escansio_text:', getattr(vers_obj, 'escansio_text', None))
    print('\nSíl·labes (index, text, pes, fusionada):')
    for i, s in enumerate(getattr(vers_obj, 'nomes_sillabes', [])):
        print(i, s.text, getattr(s, 'pes', None), getattr(s, 'fusionada', None))


print_state('preparació (minimal)', v)

# 1) Resolució de contactes vocàlics
try:
    from AIMeRiC.escansio.modules.utils.fonetica_sintactica import resol_contactes_vocalics
    resol_contactes_vocalics(v, best_mode='natural')
except Exception as e:
    print('ERROR en resol_contactes_vocalics:', e)
print_state('resol contacte vocalics', v)

# 2) Recalculem recompte mètric
try:
    from AIMeRiC.escansio.modules.utils.metre import recompte_metric
    v.recompte_sillabes_metriques = recompte_metric(v)
except Exception as e:
    print('ERROR recompte_metric:', e)
print_state('recompte_metric', v)

# llicències
if getattr(v, 'recompte_sillabes_metriques', None) is not None:
    if v.recompte_sillabes_metriques > 10:
        print(f"\n== El recompte mètric és {v.recompte_sillabes_metriques}, que excedeix l'objectiu de 10. Es poden aplicar llicències per ajustar-ho. ==")
        # aplica llicències (exemple)
        try:
            from AIMeRiC.escansio.modules.utils.llicencies import llicencies
            llicencies(v, True, doc=getattr(v, 'nlp', None))
        except Exception as e:
            print('ERROR llicencies:', e)
        print_state('llicencies', v)
else:    print("\n== No s'ha pogut calcular el recompte mètric, per tant no es poden aplicar llicències. ==")


# 3) Subdivisió i tall
try:
    from AIMeRiC.escansio.modules.utils.decasillab import tall, subdivideix
    v.posicio_tall = tall(v)
    v.subdivisio = subdivideix(v)
except Exception as e:
    print('ERROR tall/subdivideix:', e)
print_state('subdivisió/tall', v)

# 4) Prosòdia (cim + regles)
try:
    from AIMeRiC.escansio.modules.utils.prosodia import cim_maxim, accents_prosodics
    cim_maxim(v)
    accents_prosodics(v, debug=True)
except Exception as e:
    print('ERROR prosodia:', e)
print_state('prosodia completa', v)

print('\n== Avaluació de candidats de tall (3,5,4) ==')
from AIMeRiC.escansio.modules.utils.decasillab import troba_tall_posible, tall
for t in [3,5,4]:
    try:
        res = troba_tall_posible(v, t, True)
    except Exception as e:
        res = f'ERROR: {e}'
    print(f'pos index {t} -> troba_tall_posible(..., detect_nonBest=True) =', res)
    try:
        res2 = troba_tall_posible(v, t, False)
    except Exception as e:
        res2 = f'ERROR: {e}'
    print(f'pos index {t} -> troba_tall_posible(..., detect_nonBest=False) =', res2)

print('\n== Crida directa a tall() ==')
print('tall(v) ->', tall(v))

print('\nDiagnòstic final: comprova si la síl·laba candidata és l\'última de la paraula i si la paraula té `has_PRONe`.')
