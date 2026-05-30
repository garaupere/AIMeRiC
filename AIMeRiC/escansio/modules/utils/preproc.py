"""Un mòdul per netejar el text d'entrada abans de l'anàlisi automàtica de l'escansió."""
import re


def preproc_text(line: str) -> str:
    """Una funció per netejar el text d'entrada abans de l'anàlisi automàtica de l'escansió.
    Args:
        line (str): La línia de text a netejar.
    Returns:
        str: La línia de text netejada.
    """

    cleansed_text = re.sub(r"l·l", "ŀl", line)  # First correct <l·l> dygraph to <ŀl>
    cleansed_text = re.sub(r"['’´‘]", "'",
                           cleansed_text)  # Then replace catalan apostrophes and <·> contraction to <'>
    cleansed_text = re.sub(r"' +", " ", cleansed_text) # Substitueix els apòstrofs que representen elisions en mots (ex.: dón', històri', etc.)
    cleansed_text = re.sub(r" *(['·] *)", r"\1", cleansed_text)  # Then delete all spaces before and after apostrophes
    cleansed_text = re.sub(r"\{.*}", "", cleansed_text)  # Then delete all text between curly brackets (poetic licenses)
    cleansed_text = re.sub(r"[ ﻿)}{(«»“”\"‟_‒–—―•*}{■\[\]<>|&~$#@£%+©^¶/\\×≈❚‖]", "", cleansed_text,
                           flags=re.U).strip()  # Then delete all typographic symbols
    #cleansed_text = re.sub(r"[.:,;¿?!¡…]", " ", cleansed_text)  # Signes de puntuació
    cleansed_text = re.sub(r"\.\.\.|…", "…", cleansed_text)  # Normalitza punts suspensius



    cleansed_text = re.sub(r"\s+", " ", cleansed_text)  # Then delete all multiple spaces
    cleansed_text.replace(r"\r", "").replace(r"\t", "").replace("\0", "")  # Then delete all carriage returns, tabs and newlines
    cleansed_text = re.sub(r"(\d+)", "", cleansed_text)  # Then delete all numbers
    #cleansed_text = re.sub(r"-([^hslmneu])", r" \1", cleansed_text)
    return cleansed_text.lower()  # Return cleansed text


