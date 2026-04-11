# prova_subdivideix.py (exemple)
from AIMeRiC.escansio.modules.utils.decasillab import subdivideix, tall

class MockVers:
    def __init__(self, posicio=None, recompte=None):
        # si posicio és None, tall(self) ha de retornar None
        self.posicio_tall = posicio
        self.recompte_sillabes_metriques = recompte
        # dades mínimes per a altres funcions si cal
        self.nomes_sillabes = []
        self.words = []
        self.patro = []

# cas 1: posicio ja assignada
v1 = MockVers(posicio=4, recompte=10)
print(subdivideix(v1))   # hauria de mostrar '4+6'

# cas 2: posicio no assignada però tall(self) implementada externament:
def fake_tall(v): return 3
import AIMeRiC.escansio.modules.utils.decasillab as dc
dc.tall = fake_tall
v2 = MockVers(posicio=None, recompte=10)
print(subdivideix(v2))   # hauria de trucar tall() i mostrar '3+7'

# cas 3: no hi ha tall (tall retorna None) o recompte != 10 -> None
def fake_tall_none(v):
    return None
dc.tall = fake_tall_none
v3 = MockVers(posicio=None, recompte=9)
print(subdivideix(v3))   # hauria de mostrar None
