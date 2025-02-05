"""Eines vinculades al mòdul Síl·laba."""
import re


def get(string: str):
    vocal = re.sub(r"(^[h']?[iuy](?=.)|[gq]u|[^aeoiuàáèéìíòóùúyýÿïüâêîôû])", r"", string)
    vocal = re.sub(r"([aeoiuàáèéìíòóùúyýÿïüâêîôû])([iuy])", r"\g<1>", vocal)
    vocal = re.sub("[aàáâ]", "a", vocal)
    vocal = re.sub("[eèéê]", "e", vocal)
    vocal = re.sub("[iíìïyýÿî]", "i", vocal)
    vocal = re.sub("[oòóô]", "o", vocal)
    vocal = re.sub("[uúùüû]", "u", vocal)
    return vocal
