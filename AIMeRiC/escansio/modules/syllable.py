"""A module for the Syllable class."""
import re

from AIMeRiC.escansio.modules.sillaba_utils.get_vowel import get as get_vowel

class Syllable:
    def __init__(self, index: int, syllable: tuple, len_word: int, fusion_direction=None):
        self.text = syllable[0]
        self.s_index = index
        self.pes = syllable[1]
        self.len_word = len_word
        self.diftong = self.is_diftong() # Afegir a un mòdul independent: /escansio/utils/phonology.py
        self.fusion_direction = fusion_direction
        self.pes_fusion = None
        self.fusionada = True if fusion_direction is not None else False
        self.triftong = True if re.search("._._", self.text) else False
        self.starts_with_vowel = self.starts_with_vowel() # Afegir a un mòdul independent: /escansio/utils/phonology.py i reciclar el de la classe Word
        self.ends_with_vowel = self.ends_with_vowel() # Afegir a un mòdul independent: /escansio/utils/phonology.py i reciclar el de la classe Word
        self.fono_info = self.fono() # Afegir a un mòdul independent: /escansio/utils/phonology.py

    def save_metadata(self):
        return {attr: getattr(self, attr) for attr in
                ["s_index", "len_word", "text", "pes", "fusionada", "fusion_direction", "starts_with_vowel",
                 "ends_with_vowel", "fono_info"]}

    def starts_with_vowel(self):
        if re.search("^-?h?[aeoiuàáèéìíòóùúyýÿïüâêîôû]", self.text):
            if not re.search("^[iuy][aeoiuàáèéìíòóùúyýÿïüâêîôû]", self.text):
                return True
            else:
                return False
        else:
            return False

    def ends_with_vowel(self):
        if self.s_index == self.len_word - 1:
            if re.search(
                    "([^aeoiuàáèéìíòóùúyýÿïüâêîôû]*[aeoiuàáèéìíòóùúyýÿïüâêîôû]|[qg]u[aeoiuàáèéìíòóùúyýÿïüâêîôû]|^y)r?-?$",
                    self.text):
                if len(self.text) > 1:
                    if self.text[-1] == "y" and self.text[-2] == "n":
                        return False
                    elif self.text[-1] == '-':
                        return False
                    elif re.search("([aeoiuàáèéìíòóùúyýÿïüâêîôû][iuy])$", self.text):
                        if re.search("[qg]u[aeoiuàáèéìíòóùúyýÿïüâêîôû]$", self.text):
                            return True
                        else:
                            return False
                return True
            else:
                return False
        else:
            if re.search("[aeoiuàáèéìíòóùúyýÿïüâêîôû]$", self.text):
                return True
            else:
                return False

    def print_metadata(self):
        for attr in ["s_index", "len_word", "text", "pes", "fusionada", "fusion_direction", "starts_with_vowel",
                     "ends_with_vowel",
                     "fono_info"]:
            print(f"\t\t\t\t{attr}:", getattr(self, attr))
        print("\n")

    def fono(self):
        """Una funció que retorna informació fonològica de la síl·laba"""

        alta = False

        vocal = get_vowel(self.text)
        altes = "iu"
        if vocal in altes:
            alta = True

        cand_neutra = "ae"
        neutra = False
        if vocal in cand_neutra and int(self.pes) < 2:
            neutra = True

        rotica = False
        if self.text[-1] == "r":
            rotica = True
        return {"vocal": vocal, "alta": alta, "neutra": neutra, "rotica": rotica}

    def is_diftong(self):
        if re.search("([iuüy][aeiouàáèéìíòóùúyýâêîôû]|[aeiouàáèéìíòóùúyýâêîôû][iuüy])", self.text):
            if not re.search("([qg]u[eièéìíï]|[aeiouàáèéìíòóùúyýâêîôû][iy]x|ny[aeiouàáèéìíòóùúyýâêîôû]|igs?$)", self.text):
                return True
            else:
                return False
        else:
            return False
