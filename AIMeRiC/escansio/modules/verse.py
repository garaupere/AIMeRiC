"""Un mòdul per a la gestió mètrica dels versos"""
import time
from copy import deepcopy

from AIMeRiC.escansio.modules.word import Word
from AIMeRiC.escansio.modules.vers_utils.OT_constraints import analyze_OT
from AIMeRiC.escansio.modules.vers_utils.fonologia import new_sumvow, cv_get_info
from AIMeRiC.escansio.modules.vers_utils.POStagger import posTagger
from AIMeRiC.escansio.modules.vers_utils.meter import recompte_metric, metre_ajustat, abstract_pattern, \
    maximal_comparison_pattern
from AIMeRiC.escansio.modules.vers_utils.prosody import adjust_pes, cim_maxim
from AIMeRiC.escansio.modules.vers_utils.decasyllable import tall, subdivideix
from AIMeRiC.escansio.modules.vers_utils.display import anotate_verse, escansio_plana, escansio_accentual, metronome
from AIMeRiC.escansio.modules.vers_utils.licenses import aplica_llicencies
from AIMeRiC.escansio.modules.vers_utils.word_info import quants_mots, safe_words


class Vers:
    def __init__(self, nlp, text, goal):
        self.goal = goal
        self.text = text
        self.__prepara__(nlp)
        self.__uneix_mots__()
        self.__anota__()
        self.__patrons__()
        self.__subdivisio__()
        self.__disposicio__()
        self.llicencies = aplica_llicencies(self)
        self.__prosodia__()
        self.__ot_analisi__()
        self.__mot_info__()
        self.__contactes_vocalics__()
        self.__metronome__()
        self.__rima__()

    def __prepara__(self, nlp):
        self.pos = posTagger(nlp, self.text)
        self.words = [Word(token[0], token[1], self.pos.index(token)) for token in self.pos if token]
        safe_words(self)
        self.original = deepcopy(self.words)

    def __uneix_mots__(self):
        self.no_words = sum([word.stress for word in self.words], [])

    def __anota__(self):
        safe_words(self)
        self.recompte_sillabes_metriques = recompte_metric(self)
        self.ajustat = metre_ajustat(self)
        new_sumvow(self)
        self.annotated = anotate_verse(self)
        self.no_words = sum([word.stress for word in self.words], [])
        adjust_pes(self)
        self.no_words = sum([word.stress for word in self.words], [])

    def __patrons__(self):
        self.pattern = abstract_pattern(self.words)
        self.comparative_pattern = ''.join([str(x) for x in self.pattern]).rstrip('0')
        self.recompte_sillabes_metriques = recompte_metric(self)
        self.maxpattern = maximal_comparison_pattern(self)
        self.recompte_sillabes_extrametriques = len(self.pattern) - self.recompte_sillabes_metriques
        self.sillables_metriques = self.pattern[:self.recompte_sillabes_metriques]

    def __subdivisio__(self):
        self.posicio_tall = tall(self)
        self.subdivision = subdivideix(self)

    def __disposicio__(self):
        self.ajustat = metre_ajustat(self)
        self.string = escansio_plana(self)
        self.string_stress = escansio_accentual(self)

    def __rima__(self):
        self.rima = self.words[-1].plain()

    def __prosodia__(self):
        cim_maxim(self)
        adjust_pes(self)
        self.annotated = [
            [(syllable.save_metadata()["text"], syllable.save_metadata()["pes"]) for syllable in word.stress] for word
            in self.words]

    def __ot_analisi__(self):
        self._clash, self._lapse, self._ws_hl, self._non_initial, self._symetry = analyze_OT(self.maxpattern)

    def __mot_info__(self):
        self.n_words = len(self.words)
        self.h1_words = quants_mots(self)[0]
        self.h2_words = quants_mots(self)[1]

    def __contactes_vocalics__(self):
        self.cv_info = cv_get_info(self)

    def __metronome__(self):
        self.metronome = metronome(self)

    def __actualitza__(self):
        """Aquesta funció actualitza el vers després d'aplicar-hi llicències."""
        safe_words(self)
        self.__uneix_mots__()
        self.__prosodia__()
        self.__patrons__()
        self.__subdivisio__()
        self.__disposicio__()
        self.__mot_info__()
        self.__prosodia__()
        self.__ot_analisi__()
        self.__mot_info__()
        self.__contactes_vocalics__()
        self.__metronome__()

    def mostra(self):
        if self.subdivision is None:
            self.subdivision = 'Cap'
        for attr in ["ajustat", "text", "string", "string_stress", "pos", "annotated", "pattern",
                     "comparative_pattern",
                     "maxpattern",
                     "n_words",
                     "recompte_sillabes_metriques", "posicio_tall", "subdivision", "recompte_sillabes_extrametriques",
                     "llicencies", "_clash", "_lapse", "_ws_hl", "_non_initial", "_symetry", "h1_words", "h2_words",
                     "cv_info", "metronome"]:
            print(f"\t\t\t\t{attr}: {getattr(self, attr)}")

    @property
    def save(self):
        if self.subdivision is None:
            self.subdivision = 'Cap'
        return {self.text:
                    {"ajustat": self.ajustat,
                     "string": self.string,
                     "string_stress": self.string_stress,
                     "pos": self.pos,
                     "annotated": self.annotated,
                     "no_words": [syllable.save_metadata() for syllable in self.no_words],
                     "pattern": self.pattern,
                     "n_words": self.n_words,
                     "recompte_sillabes_metriques": self.recompte_sillabes_metriques,
                     "posicio_tall": self.posicio_tall,
                     "subdivision": self.subdivision,
                     "recompte_sillabes_extrametriques": self.recompte_sillabes_extrametriques,
                     "llicencies": self.llicencies,
                     "*CLASH": self._clash,
                     "*LAPSE": self._lapse,
                     "*WS_HL": self._ws_hl,
                     "*NON_INITIAL": self._non_initial,
                     "*SYMETRY": self._symetry,
                     "h1_words": self.h1_words,
                     "h2_words": self.h2_words,
                     "comparative_pattern": self.comparative_pattern,
                     "cv_info": self.cv_info,
                     "metronome": self.metronome
                     }
                }

    def to_csv(self):
        if self.subdivision is None:
            self.subdivision = 'Cap'

        if len(self.pattern) < self.goal:
            sc_col = self.pattern + [0] * (self.goal - len(self.pattern))
        elif len(self.pattern) > self.goal:
            sc_col = self.pattern[:self.goal]
        else:
            sc_col = self.pattern

        return [self.text, self.string_stress] + sc_col + [self.recompte_sillabes_metriques,
                                                           self.recompte_sillabes_extrametriques,
                                                           self.subdivision,
                                                           self.llicencies,
                                                           self._clash, self._lapse, self._ws_hl, self._non_initial,
                                                           self._symetry,
                                                           self.h1_words, self.h2_words, self.maxpattern,
                                                           self.metronome]

    def desa_prosa(self):
        return {self.text:
                    {"string": self.string,
                     "string_stress": self.string_stress,
                     "pos": self.pos,
                     "annotated": self.annotated,
                     "no_words": [syllable.save_metadata() for syllable in self.no_words],
                     "pattern": self.pattern,
                     "n_words": self.n_words,
                     "*CLASH": self._clash,
                     "*LAPSE": self._lapse,
                     "*WS_HL": self._ws_hl,
                     "*NON_INITIAL": self._non_initial,
                     "*SYMETRY": self._symetry,
                     "comparative_pattern": self.comparative_pattern,
                     "cv_info": self.cv_info,
                     "metronome": self.metronome
                     }
                }

    def prosa_to_csv(self):
        return [self.text, self.string_stress, self.recompte_sillabes_metriques, self.recompte_sillabes_extrametriques, self.pattern, self.maxpattern, self._clash, self._lapse, self._ws_hl,
                self._non_initial, self._symetry, self.metronome]


if __name__ == "__main__":
    import spacy

    start = time.time()
    nlp = spacy.load("ca_core_news_md", disable=["ner"])
    vers = Vers(nlp, "Crec que hi sóc.", 10)
    vers.mostra()
    print(time.time() - start)
