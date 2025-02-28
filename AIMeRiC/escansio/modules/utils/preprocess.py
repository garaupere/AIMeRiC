"""A module to preprocess the text input to prepare it for automatic scansion analysis"""
import re


def clean_text(line: str) -> str:
    """A function to supress all non-linguistic symbols from text (colons, dots, marks, etc.).
    :param line: a string to be cleansed
    :return: a cleansed string
    """

    cleansed_text = re.sub(r"l·l", "ŀl", line)  # First correct <l·l> dygraph to <ŀl>
    cleansed_text = re.sub(r"['’´‘]", "'",
                           cleansed_text)  # Then replace catalan apostrophes and <·> contraction to <'>
    cleansed_text = re.sub(r"' +", " ", cleansed_text) # Substitueix els apòstrofs que representen elisions en mots (ex.: dón', històri', etc.)
    cleansed_text = re.sub(r" *(['·] *)", r"\1", cleansed_text)  # Then delete all spaces before and after apostrophes
    cleansed_text = re.sub(r"\{.*}", "", cleansed_text)  # Then delete all text between curly brackets (poetic licenses)
    cleansed_text = re.sub(r"[ .:,;¿?!¡)(«»“”\"–_•—…─−*}{■\[\]<>|&~$#@£%+©^¶/\\×≈❚‖]", "", cleansed_text,
                           flags=re.U).strip()  # Then delete all typographic symbols
    cleansed_text = re.sub(r"\s+", " ", cleansed_text)  # Then delete all multiple spaces
    cleansed_text.replace(r"\r", "").replace(r"\t", "").replace("\0", "")  # Then delete all carriage returns, tabs and newlines
    cleansed_text = re.sub(r"(\d+)", "", cleansed_text)  # Then delete all numbers
    return cleansed_text.lower()  # Return cleansed text


