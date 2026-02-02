"""Un mòdul per a l'obtenció d'informaicó fonològica dels mots i síl·labes"""
import re


def starts_with_vowel(self):
    if re.search("^-?h?[aeiouàáèéíìóòúùïüy]", self.text):
        if not re.search("^[iuy][aeiouàáèéíìóòúùïüy]", self.text):
            return True
        else:
            return False
    else:
        return False


def ends_with_vowel(self):
    list = ['per', 'llur']
    if self.text in list:
        self.stress[0].ends_with_vowel = False
        return False
    if self.text[-1] == 'r':
        if len(self.stress) > 2:
            if int(self.stress[-3].pes) > 1:  # Esdrúixola acabada en -r
                return False
        if len(self.stress) > 1:
            if int(self.stress[-2].pes) > 1:  # Plana acabada en -r
                return False

    if re.search("([^aeiouàáèéíìóòúùïü]*[aeiouàáèéíìóòúùïüy]|[qg]u[aeioàáèéíìóòúùïü]|^y)r?-?$", self.text):
        if self.text[-1] == "r" and self.pos_ == "ADP":
            return False
        else:
            if len(self.text) > 1:
                if self.text[-1] == "y" and self.text[-2] == "n":
                    return False
                elif re.search("([aeiouàáèéíìóòúùïüy][iuy])$", self.text):
                    if re.search("[qg]u[aeiouàáèéíìóòúùïüy]$", self.text):
                        return True
                    else:
                        return False
        return True
    if re.search("[aeiouàáèéíìóòúùïü]yr$", self.text):
        return False
    else:
        return False


def get_vowel(string: str):
    vocal = re.sub(r"(^[h']?[iuy](?=.)|[gq]u|[^aeoiuàáèéìíòóùúyýÿïüâêîôû])", r"", string)
    vocal = re.sub(r"([aeoiuàáèéìíòóùúyýÿïüâêîôû])([iuy])", r"\g<1>", vocal)
    vocal = re.sub("[aàáâ]", "a", vocal)
    vocal = re.sub("[eèéê]", "e", vocal)
    vocal = re.sub("[iíìïyýÿî]", "i", vocal)
    vocal = re.sub("[oòóô]", "o", vocal)
    vocal = re.sub("[uúùüû]", "u", vocal)
    return vocal
