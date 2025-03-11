"""Un mòdul per detectar fenòmens relacionats amb la sintaxi"""

import re


def encavalcament(text):
    """Detecta encavalcaments en els versos"""
    final = re.search("[.?!]$", text)
    meitat = re.search("[.?!]", text)
    if not final and meitat:
        return True
