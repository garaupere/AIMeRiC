"""Un mòdul per gestionar els fenòmens de contactes vocàlics."""

from escansor_scr.modules.word.word import Word


def seguent(target, conjunt):
    """Aquesta funció retorna l'element següent a un element donat en un conjunt."""
    for index, element in enumerate(conjunt):
        if index < len(conjunt) - 1:
            if element == target:
                return conjunt[index + 1]


def fusiona_sillaba(sillaba1, sillaba2, direccio):
    """Aquesta funció fusiona dues síl·labes en una sola."""
    return f'{sillaba1.text}_{sillaba2.text}', f'{sillaba1.pes}_{sillaba2.pes}', direccio



