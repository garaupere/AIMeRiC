"""
Mòdul: verse.py

Classe principal:
- Vers: gestiona l'escansió mètrica i l'anàlisi prosòdic d'un vers.

Descripció breu:
Aquest mòdul processa un vers proporcionat a través d'un pipeline spaCy,
construeix objectes Word per cada token, resol contactes vocàlics, calcula
patrons mètrics i rítmics, aplica regles de prosòdia i exporta resultats
per visualització i serialització.

"""
from copy import deepcopy

from AIMeRiC.escansio.modules.utils.tools import seguent

_author_ = "Pere Garau"
__all__ = ["Vers"]

import time
from typing import Dict, Any, List

import spacy
from colorama import Fore

from AIMeRiC.escansio.modules.utils.POStagger import posTagger
from AIMeRiC.escansio.modules.utils.decasyllable import tall, subdivideix
from AIMeRiC.escansio.modules.utils.display import anota_vers, escansio_plana, escansio_accentual, metronome, \
    scansion_array
from AIMeRiC.escansio.modules.utils.fonetica_sintactica import contactes_vocalics_info, resol_contactes_vocalics
from AIMeRiC.escansio.modules.utils.licenses import llicencies
from AIMeRiC.escansio.modules.utils.meter import recompte_metric, metre_ajustat, abstract_pattern, \
    maximal_comparison_pattern
from AIMeRiC.escansio.modules.utils.prosody import accents_prosodics, cim_maxim
from AIMeRiC.escansio.modules.utils.syntax import encavalcament
from AIMeRiC.escansio.modules.utils.word_info import quants_mots, safe_words
from AIMeRiC.escansio.modules.word import Word


class Vers:
    """Classe per a la gestió mètrica d'un vers.
    
    Arguments:
    - nlp: objecte spacy carregat
    - text: text del vers
    - objectiu: longitud objectiu del patró (per exportacions)
    - permet_llicencies: si permet aplicar llicències
    - minimal: mode mínim (calcula menys informació per agilitar)
    
    Aquesta implementació manté la mateixa funcionalitat que l'original, amb
    optimitzacions i comprovacions addicionals per evitar errors en modes parcials.
    """

    def __init__(self, nlp, text: str, objectiu: int = 10, permet_llicencies: bool = True, minimal: bool = False):
        self.objectiu = objectiu
        self.text = text
        self.encavalcament = encavalcament(self.text)
        self._minimal = minimal

        # Preparació bàsica (etiquetatge i construcció d'objectes Word)
        self.__prepara__(nlp)

        # Resol contactes i calcular si està ajustat (un cop després de preparar)
        resol_contactes_vocalics(self, best_mode='natural')
        self.ajustat = metre_ajustat(self)
        if not minimal:
            if self.ajustat:
                self.__subdivisio__()
                self.__disposicio__()

                self.__prosodia__()
                self.__subdivisio__()
                self.__patrons__()
                self.__anota__()

                self.__mot_info__()
                self.__contactes_vocalics__()
                self.__metronome__()
                self.__rima__()
                self.llicencies = None
                self.__disposa_tall__()
            else:
                # Si no està ajustat, calcula possibles llicències
                self.llicencies = llicencies(self, permet_llicencies, doc=self.pos)

        else:
            # Mode mínim: només patrons i informació bàsica
            self.__disposicio__()
            self.__patrons__()
            self.__anota__()

    def __prepara__(self, nlp) -> None:
        """Prepara el vers: etiquetatge POS, crear objects Word i neteja inicial."""
        self.pos = posTagger(nlp, self.text)

        self.words: List[Word] = [Word(token, len(self.pos)) for token in self.pos]
        safe_words(self)
        self.original = self.words.copy()
        self.__uneix_mots__()  # crea self.nomes_sillabes
        # Calcular patrons bàsics ja que alguns passos posteriors els usaran
        self.__patrons__()
        self.__anota__()

    def __uneix_mots__(self) -> None:
        """Unifica totes les síl·labes dels mots en una sola llista."""
        self.nomes_sillabes = [s for word in self.words for s in word.stress]

    def __patrons__(self) -> None:
        """Calcula patrons rítmics i mètrics i recompte de síl·labes mètriques/extramètriques."""
        self.patro = abstract_pattern(self.words)
        self.patro_ritmic = ''.join(str(int(x)) for x in self.patro).rstrip('0')
        self.recompte_sillabes_metriques = recompte_metric(self)
        self.patro_metric = maximal_comparison_pattern(self)
        self.recompte_sillabes_extrametriques = max(0, len(self.patro) - self.recompte_sillabes_metriques)
        self.sillables_metriques = self.patro[:self.recompte_sillabes_metriques]

    def __subdivisio__(self) -> None:
        """Calcula la subdivisió i actualitza el patró mètric."""
        self.posicio_tall = tall(self)
        self.subdivisio = subdivideix(self)
        # Actualitzar representacions derivades
        self.patro_ritmic = ''.join(str(int(x)) for x in self.patro).rstrip('0')
        self.patro_metric = maximal_comparison_pattern(self)

    def __anota__(self) -> None:
        """Genera l'etiquetatge del vers."""
        self.anotat = anota_vers(self)
        self.__uneix_mots__()

    def __disposicio__(self) -> None:
        """Genera representacions textuals de l'escansió (plana, array, accentual)."""
        self.string = escansio_plana(self)
        self.escansio_array = scansion_array(self)
        self.escansio_text = escansio_accentual(self)

    def __rima__(self) -> None:
        """Info de rima [INÚTIL]."""
        if self.words:
            self.rima = self.words[-1].plain()
        else:
            self.rima = None

    def __prosodia__(self) -> None:
        """Càlculs prosòdics addicionals (accents prosòdics, cim màxim)."""
        cim_maxim(self)
        #self.prosodia_original = deepcopy(self)

        accents_prosodics(self, debug=False)
        #self.actualitza_pesos()
        #cim_maxim(self)
        # Actualitza anotacions i representacions
        self.anotat = anota_vers(self)
        self.escansio_array = scansion_array(self)
        self.escansio_text = escansio_accentual(self)

    def __mot_info__(self) -> None:
        """Nombre de mots i distribució respecte al còlon (informació de quants_mots)."""
        self.n_mots = len(self.words)
        qm = quants_mots(self)
        # quants_mots pot retornar una tupla; usem indices amb seguretat
        self.mots_colon1 = qm[0] if len(qm) > 0 else 0
        self.mots_colon2 = qm[1] if len(qm) > 1 else 0

    def __contactes_vocalics__(self) -> None:
        """Agrupa informació sobre contactes vocàlics i sobreescriu valors anteriors."""
        result = contactes_vocalics_info(self)
        if not result:
            self.contactes_vocalics = None
            return

        # Si és un dict i tots els valors estan buits, considerea que no hi ha info
        if isinstance(result, dict):
            if all(not v for v in result.values()):
                self.contactes_vocalics = None
            else:
                self.contactes_vocalics = result
        else:
            # Si no és un dict, assigna directament (o None si falsy)
            self.contactes_vocalics = result if result else None

    def __metronome__(self) -> None:
        """Patró per a metronome."""
        self.metronome = metronome(self)

    def __disposa_tall__(self) -> None:
        """Disposa la representació del patró afegint l'espai després de la posició de tall."""
        if getattr(self, 'subdivisio', None) is None:
            self.subdivisio = 'Cap'
        elif self.subdivisio != 'Cap':
            pos = getattr(self, 'posicio_tall', None)
            if pos is not None and isinstance(self.patro_metric, str):
                self.patro_metric = self.patro_metric[:pos] + ' ' + self.patro_metric[pos:]
                self.patro_ritmic = self.patro_ritmic[:pos] + ' ' + self.patro_ritmic[pos:].rstrip('0')

    def __actualitza__(self) -> None:
        """Actualitza l'estat del vers després d'aplicar llicències."""
        safe_words(self)
        self.__uneix_mots__()
        self.__patrons__()
        # Reset del cim màxim
        self.__kill_cim_maxim__()
        self.__subdivisio__()
        self.__disposicio__()
        self.ajustat = metre_ajustat(self)
        if self.ajustat or self.words[-1].stress[-1].pes < 3:
            self.__prosodia__()
            self.__subdivisio__()
        self.__patrons__()
        self.__anota__()
        self.__mot_info__()
        self.__contactes_vocalics__()
        self.__metronome__()
        self.__disposa_tall__()

    def mostra(self) -> None:
        """Mostra informació del vers amb colors per consola."""

        def color_metric(pattern: str) -> str:
            return ''.join([Fore.CYAN + ch + Fore.RESET if ch == '1' else ch for ch in pattern])

        def color_ritmic(pattern: str) -> str:
            # intenta processar cada caràcter com a número; si no es pot, deixar'l com està
            out = []
            for ch in pattern:
                try:
                    val = int(ch)
                except Exception:
                    out.append(ch)
                    continue
                if val == 2:
                    out.append(Fore.CYAN + ch + Fore.RESET)
                elif val > 2:
                    out.append(Fore.RED + ch + Fore.RESET)
                elif val == 1:
                    out.append(Fore.YELLOW + ch + Fore.RESET)
                else:
                    out.append(ch)
            return ''.join(out)

        # Mapatge d'atributs amb valors per defecte per evitar AttributeError
        attrs = {
            "escansio_text": getattr(self, 'escansio_text', None),
            "patro": getattr(self, 'patro', None),
            "patro_metric": getattr(self, 'patro_metric', None),
            "recompte_sillabes_metriques": getattr(self, 'recompte_sillabes_metriques', None),
            "recompte_sillabes_extrametriques": getattr(self, 'recompte_sillabes_extrametriques', None),
            "ajustat": getattr(self, 'ajustat', None),
            "subdivisio": getattr(self, 'subdivisio', None),
            "n_mots": getattr(self, 'n_mots', None),
            "mots_colon1": getattr(self, 'mots_colon1', None),
            "mots_colon2": getattr(self, 'mots_colon2', None),
            "llicencies": getattr(self, 'llicencies', None),
        }

        if attrs["escansio_text"] is not None:
            print(Fore.CYAN, f"\t➥", Fore.RESET, f"Escansió: {attrs['escansio_text']}")

        if attrs["patro"] is not None:
            print(Fore.CYAN, f"\t➥", Fore.RESET, f"Patró rítmic:",
                  color_ritmic(''.join(str(x) for x in attrs['patro'])))

        if attrs["patro_metric"] is not None:
            print(Fore.CYAN, f"\t➥", Fore.RESET, f"Patró mètric:", color_metric(str(attrs['patro_metric'])))

        if attrs["recompte_sillabes_metriques"] is not None:
            print(Fore.CYAN, f"\t➥", Fore.RESET, f"Síl·labes mètriques:", Fore.CYAN,
                  attrs["recompte_sillabes_metriques"], Fore.RESET)

        if attrs["recompte_sillabes_extrametriques"] is not None:
            print(Fore.CYAN, f"\t➥", Fore.RESET, f"Síl·labes extramètriques:", Fore.CYAN,
                  attrs["recompte_sillabes_extrametriques"], Fore.RESET)

        print(Fore.CYAN, f"\t➥", Fore.RESET, f"Ajustat:", attrs["ajustat"])
        print(Fore.CYAN, f"\t➥", Fore.RESET, f"Subdivisió:",
              attrs["subdivisio"] if attrs["subdivisio"] is not None else 'Cap')
        print(Fore.CYAN, f"\t➥", Fore.RESET, f"Número de mots:", attrs["n_mots"])
        print(Fore.CYAN, f"\t\t➥", Fore.RESET, f"Mots al primer colon:", attrs["mots_colon1"])
        print(Fore.CYAN, f"\t\t➥", Fore.RESET, f"Mots al segon colon:", attrs["mots_colon2"])
        print(Fore.CYAN, f"\t➥", Fore.RESET, f"Llicències:",
              attrs["llicencies"] if attrs["llicencies"] is not None else 'Cap')

    @property
    def desa(self) -> Dict[str, Any]:
        """Retorna un diccionari amb la informació del vers"""
        return {
            self.text: {
                "string": getattr(self, 'string', None),
                "escansió": getattr(self, 'escansio_text', None),
                "patró rítmic": getattr(self, 'patro_ritmic', None),
                "patró mètric": getattr(self, 'patro_metric', None),
                "síl·labes mètriques": getattr(self, 'recompte_sillabes_metriques', None),
                "síl·labes extramètriques": getattr(self, 'recompte_sillabes_extrametriques', None),
                "posició tall": getattr(self, 'posicio_tall', None),
                "subdivisió": getattr(self, 'subdivisio', None),
                "llicències": getattr(self, 'llicencies', None),
                "mots": getattr(self, 'n_mots', None),
                "mots al còlon 1": getattr(self, 'mots_colon1', None),
                "mots al còlon 2": getattr(self, 'mots_colon2', None),
                "cv_info": getattr(self, 'contactes_vocalics', None),
                "encavalcament": getattr(self, 'encavalcament', None),
                "metronome": getattr(self, 'metronome', None),
                "etiquetatge": getattr(self, 'anotat', None)
            }
        }

    def to_csv(self) -> List[Any]:
        """Retorna una llista amb la informació del vers per a guardar-la en un fitxer CSV."""
        patro_local = getattr(self, 'patro', [])
        if len(patro_local) < self.objectiu:
            sc_col = patro_local + [0] * (self.objectiu - len(patro_local))
        else:
            sc_col = patro_local[:self.objectiu]

        return [
            self.text,
            getattr(self, 'escansio_text', None),
            *sc_col,
            getattr(self, 'recompte_sillabes_metriques', None),
            getattr(self, 'recompte_sillabes_extrametriques', None),
            getattr(self, 'subdivisio', None),
            getattr(self, 'llicencies', None),
            getattr(self, 'mots_colon1', None),
            getattr(self, 'mots_colon2', None),
            str(getattr(self, 'patro_metric', '')),
            str(getattr(self, 'patro_ritmic', '')),
            getattr(self, 'encavalcament', None),
            getattr(self, 'metronome', None)
        ]

    def save_minimal(self) -> Dict[str, Any]:
        """Retorna un diccionari amb informació essencial del vers."""
        return {
            self.text: {
                "string": getattr(self, 'string', None),
                "string_stress": getattr(self, 'escansio_text', None),
                "pattern": getattr(self, 'patro', None),
                "sillabes_metriques": getattr(self, 'sillables_metriques', None),
                "sillabes_extrametriques": getattr(self, 'recompte_sillabes_extrametriques', None),
                "n_words": getattr(self, 'n_mots', None),
                "comparative_pattern": getattr(self, 'patro_ritmic', None),
                "array": [[syllable.save_metadata() for syllable in mot.stress] for mot in getattr(self, 'words', [])]
            }
        }

    def mostra_minimal(self) -> None:
        """Mostra la informació mínima del vers en format compacte."""

        def color_tonic(pattern: str) -> str:
            return ''.join([Fore.CYAN + ch + Fore.RESET if ch == '1' else ch for ch in str(pattern)])

        esc = getattr(self, 'escansio_text', None)
        patro_rit = getattr(self, 'patro_ritmic', None)
        patro_met = getattr(self, 'patro_metric', None)
        r_met = getattr(self, 'recompte_sillabes_metriques', None)
        r_ext = getattr(self, 'recompte_sillabes_extrametriques', None)
        n_w = getattr(self, 'n_mots', None)

        if esc is not None:
            print(Fore.CYAN, f"\t➥", Fore.RESET, f"Escansió: {esc}")
        if patro_rit is not None:
            print(Fore.CYAN, f"\t➥", Fore.RESET, f"Patró rítmic:", color_tonic(patro_rit))
        if patro_met is not None:
            print(Fore.CYAN, f"\t➥", Fore.RESET, f"Patró mètric:", color_tonic(patro_met))
        if r_met is not None:
            print(Fore.CYAN, f"\t➥", Fore.RESET, f"Síl·labes mètriques:", Fore.CYAN, r_met, Fore.RESET)
        if r_ext is not None:
            print(Fore.CYAN, f"\t➥", Fore.RESET, f"Síl·labes extramètriques:", Fore.CYAN, r_ext, Fore.RESET)
        if n_w is not None:
            print(Fore.CYAN, f"\t➥", Fore.RESET, f"Número de mots:", n_w)

    def __kill_cim_maxim__(self) -> None:
        """Elimina el cim màxim existent (per quan es torna a processar el vers)."""
        for word in getattr(self, 'words', []):
            for syllable in getattr(word, 'stress', []):
                try:
                    if getattr(syllable, 'pes', None) == 5.0:
                        syllable.pes = 4.0
                except Exception:
                    # Si la síl·laba no té atribut pes, continua
                    continue
        # Actualitzar el repertori de síl·labes
        self.__uneix_mots__()

    def __repr__(self) -> str:
        return f"<Vers text={self.text!r} n_words={len(getattr(self, 'words', []))}>"

    def actualitza_w_index(self):
        """Actualitza els w_index de les paraules després de canvis en la llista."""
        for i, word in enumerate(self.words):
            word.w_index = i

    def actualitza_pesos(self):
        """Actualitza el valor de pes de les síl·labes de mots.stress depsrés de canvis a self.nomes_sillabes."""
        for word in getattr(self, 'words', []):
            for syllable in getattr(word, 'stress', []):
                # Cerca la síl·laba corresponent a self.nomes_sillabes i actualitza el pes
                for s in getattr(self, 'nomes_sillabes', []):
                    if syllable.text == s.text:
                        syllable.pes = s.pes
                        break


# Exemple d'ús
if __name__ == "__main__":
    start = time.time()
    sentence = "D'antics casals marquem-hi solcs pregons."
    nlp = spacy.load("ca_core_news_md", disable=["ner"])
    vers = Vers(nlp, sentence, 10, permet_llicencies=True)
    vers.mostra()
