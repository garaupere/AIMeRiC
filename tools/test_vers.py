# Script de prova per al vers de control
# Prova: "Sol, i de dol, i vetusta gonella" (esperat: 4+6)

from importlib import import_module
import traceback

text = "Sol, i de dol, i amb vetusta gonella"

print(f"Vers de prova: {text!r}")

# Intentem usar la classe Vers si spaCy i el model estan disponibles
try:
    from AIMeRiC.escansio.modules.vers import Vers
    import spacy
    try:
        nlp = spacy.load("ca_core_news_md", disable=["ner"])  # pot fallar si el model no està instal·lat
        v = Vers(nlp, text, 10, permet_llicencies=True)
        print("--- Resultat amb Vers real (spaCy) ---")
        print("posicio_tall:", getattr(v, 'posicio_tall', None))
        print("subdivisio:", getattr(v, 'subdivisio', None))
        print("patro_metric:", getattr(v, 'patro_metric', None))
        print("patro_ritmic:", getattr(v, 'patro_ritmic', None))
        print("escansio_text:", getattr(v, 'escansio_text', None))
    except Exception as e:
        print("No es pot crear Vers amb spaCy/model (ca_core_news_md). Caigut a fallback.\n", e)
        raise

except Exception:
    print("Vers real no disponible; s'executa fallback minimal (mock) per provar `tall()` i `subdivideix()`).")
    traceback.print_exc()

    # Farem un mock mínim compatible amb `decasillab.tall` i `decasillab.subdivideix`
    from AIMeRiC.escansio.modules.utils.decasillab import tall, subdivideix

    class Syllable:
        def __init__(self, text, pes=3.0, fusionada=False, s_index=0):
            self.text = text
            self.pes = pes
            self.fusionada = fusionada
            self.s_index = s_index
        def __repr__(self):
            return f"S({self.text},{self.pes})"

    class WordMock:
        def __init__(self, stress, has_PRONe=False, pos_='NOUN', w_index=0):
            self.stress = stress
            self.has_PRONe = has_PRONe
            self.pos_ = pos_
            self.w_index = w_index
        def plain(self):
            return ''.join(s.text for s in self.stress)

    class VersMock:
        def __init__(self):
            # Construïm 10 síl·labes per representar un decasíl·lab
            syll_texts = ['Sol','i','de','dol','i','vetus','ta','go','nel','la']
            self.nomes_sillabes = [Syllable(t, pes=3.0, fusionada=False, s_index=i) for i,t in enumerate(syll_texts)]
            # Posem la síl·laba de tall (index 3 correspon a pos=4) amb pes>2 (p.ex. 4.0)
            self.nomes_sillabes[3].pes = 4.0
            # Organitzem mots perquè la síl·laba d'index 3 sigui l'última d'una paraula
            w0 = WordMock(self.nomes_sillabes[0:4], has_PRONe=False, pos_='NOUN', w_index=0)
            w1 = WordMock(self.nomes_sillabes[4:7], has_PRONe=False, pos_='VERB', w_index=1)
            w2 = WordMock(self.nomes_sillabes[7:10], has_PRONe=False, pos_='NOUN', w_index=2)
            self.words = [w0, w1, w2]
            # patró simulant (llarg 10)
            self.patro = [2]*10
            # anotacions per aplica_tall
            self.anotat = [None]*len(self.words)
            self.recompte_sillabes_metriques = 10
            self.sillables_metriques = self.patro[:10]

    vm = VersMock()
    pos = tall(vm)
    subdiv = subdivideix(vm)
    print('--- Resultat mock ---')
    print('posicio_tall (tall):', pos)
    print('subdivisio (subdivideix):', subdiv)

    # Apliquem aplica_tall per veure efectes (la funció aplica_tall està dins el mòdul decasillab)
    try:
        from AIMeRiC.escansio.modules.utils.decasillab import aplica_tall
        # aplica_tall espera l'index 0-based (tall_actual), però tall() retorna pos 1-based;
        # en el codi `aplica_tall(self, tall)` s'utilitza amb tall_actual (0-based). Així que per aplicar el tall
        # tal com tall() l'ha seleccionat, restem 1.
        if pos is not None:
            aplica_tall(vm, int(pos)-1)
            print('Després d`aplica_tall:')
            print('patro (pos assignada index):', vm.patro)
            # indiquem quin mot ha estat marcat
            print('paraules marcades (paraula_tall):', [getattr(w, 'paraula_tall', False) for w in vm.words])
    except Exception as e:
        print('No s\'ha pogut executar aplica_tall a la mock:', e)

print('\nTest complet.')

