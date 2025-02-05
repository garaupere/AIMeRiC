"""Un mòdul amb eines recurrents per al programa."""
import re
from functools import reduce


def interize(string):
    """Aquesta funció converteix una cadena de text en una llista d'enters."""
    if len(string) > 1:
        pesos = string.split("_")
        return abs(reduce(lambda x, y: x - y, [int(pes) for pes in pesos]))
    else:
        return int(string)


def seguent(target, conjunt):
    """Aquesta funció retorna l'element següent a un element donat en un conjunt."""
    for index, element in enumerate(conjunt):
        if index < len(conjunt) - 1:
            if element == target:
                return conjunt[index + 1]


def get_vowel_keep_diftong(string: str):
    keep = [re.findall(r"([aeoiuàáèéìíòóùúyýÿïüâêîôû]_)", string)[0] if re.search(r"([aeoiuàáèéìíòóùúyýÿïüâêîôû]_)",
                                                                                  string) else ""][0]
    vocal = re.sub(r"(^[h']?[iuy](?=.)|[gq]u|[^aeoiuàáèéìíòóùúyýÿïüâêîôû])", r"", string)
    # vocal = re.sub(r"[aeoiuàáèéìíòóùúyýÿïüâêîôû]([iuy])", r"\g<1>", vocal)
    vocal = re.sub("[aàáâ]", "a", vocal)
    vocal = re.sub("[eèéê]", "e", vocal)
    vocal = re.sub("[iíìïyýÿî]", "i", vocal)
    vocal = re.sub("[oòóô]", "o", vocal)
    vocal = re.sub("[uúùüû]", "u", vocal)
    return keep + vocal
