"""Un mòdul amb eines recurrents per al programa."""
import re


def seguent(target, conjunt):
    """Aquesta funció retorna l'element següent a un element donat en un conjunt.
    Args:
        target: L'element del qual es vol trobar el següent.
        conjunt: La llista on es busca l'element següent.
    Returns:
        L'element següent al target en el conjunt, o None si no existeix.
    """
    for index, element in enumerate(conjunt):
        if index < len(conjunt) - 1:
            if element == target:
                return conjunt[index + 1]


def get_vowel_keep_diftong(string: str):
    """Aquesta funció extreu les vocals d'una cadena de text, mantenint el primer element d'un diftong si existeix.
    Args:
        string (str): La cadena de text d'on s'extreuen les vocals.
    Returns:
        str: Una cadena amb les vocals extretes i el primer element del diftong mantingut.
    """
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
