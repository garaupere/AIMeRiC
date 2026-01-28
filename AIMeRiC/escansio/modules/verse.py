"""Un mòdul per a la gestió mètrica dels versos"""
import time

import pandas as pd
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
    def __init__(self, nlp, text: str, objectiu: int = 10, permet_llicencies: bool = True, minimal: bool = False):
        if not minimal:
            self.objectiu = objectiu
            self.text = text
            self.encavalcament = encavalcament(self.text)
            self.__prepara__(nlp)

            resol_contactes_vocalics(self, best_mode='natural')
            self.ajustat = metre_ajustat(self)

            if self.ajustat:
                self.__subdivisio__()
                self.__disposicio__()

                self.__prosodia__()
                self.__patrons__()
                self.__anota__()

                self.__mot_info__()
                self.__contactes_vocalics__()
                self.__metronome__()
                self.__rima__()
                self.llicencies = None
                self.__disposa_tall__()
            else:
                self.llicencies = llicencies(self, permet_llicencies, doc=self.pos)
        else:
            # Minimal mode for faster processing without full analysis
            self.objectiu = objectiu
            self.text = text
            self.encavalcament = encavalcament(self.text)
            self.__prepara__(nlp)
            resol_contactes_vocalics(self, best_mode='natural')
            self.__disposicio__()
            self.__patrons__()
            self.__anota__()

    def __prepara__(self, nlp):
        self.pos = posTagger(nlp, self.text)
        self.words = [Word(token, len(self.pos)) for token in self.pos]
        safe_words(self)
        self.original = self.words.copy()
        self.__uneix_mots__()
        self.__patrons__()
        self.__anota__()

    def __uneix_mots__(self):
        self.nomes_sillabes = sum([word.stress for word in self.words], [])

    def __patrons__(self):
        self.patro = abstract_pattern(self.words)
        self.contorn_cru = ''.join([str(x) for x in self.patro]).rstrip('0')
        self.recompte_sillabes_metriques = recompte_metric(self)
        self.contorn_accentual = maximal_comparison_pattern(self)
        self.recompte_sillabes_extrametriques = len(self.patro) - self.recompte_sillabes_metriques
        self.sillables_metriques = self.patro[:self.recompte_sillabes_metriques]

    def __subdivisio__(self):
        self.posicio_tall = tall(self)
        self.subdivisio = subdivideix(self)
        cim_maxim(self)
        self.contorn_cru = ''.join([str(x) for x in self.patro]).rstrip('0')
        self.contorn_accentual = maximal_comparison_pattern(self)

    def __anota__(self):
        self.anotat = anota_vers(self)
        self.__uneix_mots__()

    def __disposicio__(self):
        self.ajustat = metre_ajustat(self)
        self.string = escansio_plana(self)
        self.escansio_array = scansion_array(self)
        self.escansio_text = escansio_accentual(self)

    def __rima__(self):
        self.rima = self.words[-1].plain()

    def __prosodia__(self):
        cim_maxim(self)
        accents_prosodics(self)
        self.anotat = anota_vers(self)
        self.escansio_array = scansion_array(self)
        self.escansio_text = escansio_accentual(self)

    def __mot_info__(self):
        self.n_mots = len(self.words)
        self.mots_colon1 = quants_mots(self)[0]
        self.mots_colon2 = quants_mots(self)[1]

    def __contactes_vocalics__(self):
        """Compute contactes_vocalics info and overwrite any previous value.

        If the computed result is falsy or all contained lists are empty, store
        None so previous data is not preserved across updates.
        """
        result = contactes_vocalics_info(self)
        if not result:
            # Nothing returned -> clear previous info
            self.contactes_vocalics = None
            return

        # If all values in the dict are empty (no contours found), clear as well
        try:
            if all(not v for v in result.values()):
                self.contactes_vocalics = None
            else:
                self.contactes_vocalics = result
        except AttributeError:
            # If result is not a dict-like object, just assign it (or None if falsy)
            self.contactes_vocalics = result if result else None

    def __metronome__(self):
        self.metronome = metronome(self)

    def __disposa_tall__(self):
        if self.subdivisio is None:
            self.subdivisio = 'Cap'
        elif self.subdivisio != 'Cap':
            self.contorn_accentual = self.contorn_accentual[:self.posicio_tall] + '|' + self.contorn_accentual[
                self.posicio_tall:]
            self.contorn_cru = self.contorn_cru[:self.posicio_tall] + ' ' + self.contorn_cru[self.posicio_tall:]
            #self.escansio_text = self.escansio_text.split('.')

            #self.escansio_text = '.'.join(
            #    self.escansio_text[:self.posicio_tall] + ['|'] + self.escansio_text[self.posicio_tall:]).replace('.|.', '|')

    def __actualitza__(self):
        """Aquesta funció actualitza el vers després d'aplicar-hi llicències."""
        safe_words(self)
        self.__uneix_mots__()
        self.__patrons__()
        self.__subdivisio__()
        self.__disposicio__()
        self.__prosodia__()
        self.__patrons__()
        self.__anota__()
        self.__mot_info__()
        self.__mot_info__()
        self.__contactes_vocalics__()
        self.__metronome__()
        self.__disposa_tall__()

    def mostra(self):
        """Mostra la informació del vers."""

        def color_tonic(pattern):
            return ''.join([Fore.CYAN + str(x) + Fore.RESET if x == '1' else str(x) for x in pattern])

        for attr in ["escansio_text", "contorn_accentual", "recompte_sillabes_metriques",
                     "recompte_sillabes_extrametriques",
                     "ajustat", "subdivisio",
                     "anotat", "n_mots", "mots_colon1", "mots_colon2",
                     "llicencies"]:
            if attr == "escansio_text":
                print(Fore.CYAN, f"\t➥", Fore.RESET, f"Escansió: {(getattr(self, attr))}")
            elif attr == "contorn_accentual":
                print(Fore.CYAN, f"\t➥", Fore.RESET, f"Contorn accentual:", f"{color_tonic(getattr(self, attr))}")
            elif attr == "recompte_sillabes_metriques":
                print(Fore.CYAN, f"\t➥", Fore.RESET, f"Síl·labes mètriques:", Fore.CYAN, f"{getattr(self, attr)}",
                      Fore.RESET)
            elif attr == "recompte_sillabes_extrametriques":
                print(Fore.CYAN, f"\t➥", Fore.RESET, f"Síl·labes extramètriques:", Fore.CYAN, f"{getattr(self, attr)}",
                      Fore.RESET)
            elif attr == "subdivisio":
                print(Fore.CYAN, f"\t➥", Fore.RESET, f"Subdivisió:",
                      f"{getattr(self, attr) if getattr(self, attr) is not None else 'Cap'}")
            elif attr == "n_mots":
                print(Fore.CYAN, f"\t➥", Fore.RESET, f"Número de mots:", f"{getattr(self, attr)}")
            elif attr == "mots_colon1":
                print(Fore.CYAN, f"\t\t➥", Fore.RESET, f"Mots al primer colon:", f"{getattr(self, attr)}")
            elif attr == "mots_colon2":
                print(Fore.CYAN, f"\t\t➥", Fore.RESET, f"Mots al segon colon:", f"{getattr(self, attr)}")
            elif attr == "llicencies":
                print(Fore.CYAN, f"\t➥", Fore.RESET, f"Llicències:",
                      f"{getattr(self, attr) if getattr(self, attr) is not None else 'Cap'}")
            else:
                print(Fore.CYAN, f"\t➥", Fore.RESET, f"{attr[0].upper() + attr.replace('_', ' ')[1:]}:",
                      f"{getattr(self, attr)}")

    @property
    def save(self):
        """Retorna un diccionari amb la informació del vers."""
        return {self.text:
                    {"ajustat": self.ajustat,
                     "string": self.string,
                     "string_stress": self.escansio_text,
                     "annotated": self.anotat,
                     "no_words": [syllable.save_metadata() for syllable in self.nomes_sillabes],
                     "pattern": self.patro,
                     "n_words": self.n_mots,
                     "recompte_sillabes_metriques": self.recompte_sillabes_metriques,
                     "posicio_tall": self.posicio_tall,
                     "subdivision": self.subdivisio,
                     "recompte_sillabes_extrametriques": self.recompte_sillabes_extrametriques,
                     "llicencies": self.llicencies,
                     "h1_words": self.mots_colon1,
                     "h2_words": self.mots_colon2,
                     "comparative_pattern": self.contorn_cru,
                     "cv_info": self.contactes_vocalics,
                     "encavalcament": self.encavalcament,
                     "metronome": self.metronome
                     }
                }

    def to_csv(self):
        """Retorna una llista amb la informació del vers per a guardar-la en un fitxer CSV."""
        if len(self.patro) < self.objectiu:
            sc_col = self.patro + [0] * (self.objectiu - len(self.patro))
        elif len(self.patro) > self.objectiu:
            sc_col = self.patro[:self.objectiu]
        else:
            sc_col = self.patro

        return [self.text, self.escansio_text] + sc_col + [self.recompte_sillabes_metriques,
                                                           self.recompte_sillabes_extrametriques,
                                                           self.subdivisio,
                                                           self.llicencies,
                                                           self.mots_colon1, self.mots_colon2,
                                                           str(self.contorn_accentual), str(self.contorn_cru), self.encavalcament,
                                                           self.metronome]

    def prosa_to_csv(self):
        return [self.text, self.escansio_text,
                self.recompte_sillabes_metriques,
                self.recompte_sillabes_extrametriques,
                self.subdivisio,
                self.llicencies,
                self.mots_colon1, self.mots_colon2,
                str(self.contorn_accentual), str(self.contorn_cru), self.encavalcament,
                self.metronome]

    def save_minimal(self):
        """Retorna un diccionari amb la informació mínima del vers."""
        return {self.text:
                    {"string": self.string,
                     "string_stress": self.escansio_text,
                     "pattern": self.patro,
                     "sillabes_metriques": self.sillables_metriques,
                     "sillabes_extrametriques": self.recompte_sillabes_extrametriques,
                     "n_words": self.n_mots,
                     "comparative_pattern": self.contorn_cru,
                     "array": [[syllable.save_metadata() for syllable in mot.stress] for mot in self.words]
                     }
                }

    def mostra_minimal(self):
        """Mostra la informació mínima del vers."""

        def color_tonic(pattern):
            return ''.join([Fore.CYAN + str(x) + Fore.RESET if x == '1' else str(x) for x in pattern])

        for attr in ["escansio_text", "contorn_accentual", "recompte_sillabes_metriques",
                     "recompte_sillabes_extrametriques",
                     "n_words"]:
            if attr == "escansio_text":
                print(Fore.CYAN, f"\t➥", Fore.RESET, f"Escansió: {(getattr(self, attr))}")
            elif attr == "contorn_accentual":
                print(Fore.CYAN, f"\t➥", Fore.RESET, f"Contorn accentual:", f"{color_tonic(getattr(self, attr))}")
            elif attr == "recompte_sillabes_metriques":
                print(Fore.CYAN, f"\t➥", Fore.RESET, f"Síl·labes mètriques:", Fore.CYAN, f"{getattr(self, attr)}",
                      Fore.RESET)
            elif attr == "recompte_sillabes_extrametriques":
                print(Fore.CYAN, f"\t➥", Fore.RESET, f"Síl·labes extramètriques:", Fore.CYAN, f"{getattr(self, attr)}",
                      Fore.RESET)
            elif attr == "n_mots":
                print(Fore.CYAN, f"\t➥", Fore.RESET, f"Número de mots:", f"{getattr(self, attr)}")


if __name__ == "__main__":
    start = time.time()
    sentence = "Sol, i de dol, i amb vetusta gonella"
    nlp = spacy.load("ca_core_news_md", disable=["ner"])
    vers = Vers(nlp, sentence, 10, permet_llicencies=True)
    vers.mostra()
    print(vers.save)
