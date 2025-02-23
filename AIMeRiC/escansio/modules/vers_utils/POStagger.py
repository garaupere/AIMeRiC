"""Un mòdul per a l'etiquetatge morfosintàctic de textos en català."""
import re
import string

from .preprocess import clean_text


def correct_spacy(doc):
    """
        Corrects the POS tags in the given SpaCy document based on predefined corrections.

        Args:
            doc (list): A list of tokens with their POS tags and dependencies.

        Returns:
            list: A corrected list of tokens with updated POS tags.
                """
    corrections = {
        'e': 'CCONJ', 'y': 'CCONJ', 'puix': 'SCONJ',  'amb': 'ADPa', 'de': 'ADPa', 'en': 'ADPa', 'per': 'ADPa',
        'á': 'ADPa', 'à': 'ADPa', 'a': 'ADPa', 'dels': 'ADPa', 'del': 'ADPa', 'als': 'ADPa', 'al': 'ADPa',
        'des': 'ADPa', "me'ls": "PRON", "me": "PRON", "-me'ls": "PRON", "-me": "PRON",
        'res': 'NOUN', 'hom': 'NOUN', 'om': 'NOUN', 'així': 'ADV', 'cell': 'PRON', 'quell': 'PRON', '·quell': 'PRON', 'ceyl': 'PRON',
         'mi': 'PRON',  'què': 'PRON', 'qui': 'PRON', 'quin': 'PRON', 'quins': 'PRON',
        'quina': 'PRON', 'quines': 'PRON', 'yo': 'PRON', 'vós': 'NOUN', 'nós': 'NOUN', 'ne': 'CCONJ', 'ni': 'CCONJ',
        'seu': 'PRON', 'seus': 'PRON', 'seva': 'PRON', 'seves': 'PRON', 'seua': 'PRON', 'seues': 'PRON', 'sua': 'PRON',
        'sues': 'PRON', 'meu': 'PRON', 'meus': 'PRON', 'meva': 'PRON', 'meves': 'PRON', 'meua': 'PRON', 'meues': 'PRON',
        'teu': 'PRON', 'teus': 'PRON', 'teva': 'PRON', 'teves': 'PRON', 'teua': 'PRON', 'teues': 'PRON',
        'nostre': 'PRON',
        'nostres': 'PRON', 'nostra': 'PRON', 'vostre': 'PRON', 'vostres': 'PRON', 'vostra': 'PRON', 'un': 'NUM',
        'una': 'NUM',
        'uns': 'NUM', 'unes': 'NUM', 'aquests': 'PRON', 'aquestes': 'PRON', 'aquell': 'PRON', 'aquella': 'PRON',
        'tan': 'PRON', 'tant': 'PRON', 'tants': 'PRON', 'tanta': 'PRON', 'tantes': 'PRON', 'tu': 'PRON',
        'aquells': 'PRON', 'aquelles': 'PRON', 'aquest': 'PRON', 'aquesta': 'PRON', 'aqueix': 'PRON', 'aqueixa': 'PRON',
        'aqueixos': 'PRON', 'aqueixes': 'PRON', 'este': 'PRON', 'esta': 'PRON', 'estos': 'PRON', 'estes': 'PRON',
        'eixos': 'PRON', 'eixes': 'PRON', 'eixa': 'PRON', 'eixs': 'PRON', 'eixas': 'PRON', 'eix': 'PRON',
        'això': 'PRON',
        'açò': 'PRON', 'ço': 'PRON', 'so': 'NOUN', 'xo': 'PRON', 'xô': 'PRON', 'xò': 'PRON', "'xo": 'PRON',
        "'xô": 'PRON',
        "'xò": 'PRON', 'més': 'PRON', 'menys': 'PRON', 'molt': 'PRON', 'poc': 'PRON', 'pocs': 'PRON', 'molts': 'PRON',
        'ab': 'ADPa', 'com': 'PRON', 'quan': 'ADP', 'on': 'ADP', 'perquè': 'ADV', 'perque': 'ADV', 'perqué': 'ADV',
        'no': 'ADP', 'sí': 'ADP', 'ja': 'ADP', 'encara': 'ADV', 'ans': 'ADV', 'ara': 'ADV', 'ací': 'ADV', 'allà': 'ADV',
        'allí': 'ADV', 'açà': 'ADV', 'dallà': 'ADV', 'dallí': 'ADV', 'pus': 'ADV', 'am': 'VERB', 'cel': 'NOUN',
        'cert': 'ADJ', 'certs': 'ADJ', 'certa': 'ADJ', 'certes': 'ADJ', 'val': 'VERB', 'delit': 'NOUN',
        'delits': 'NOUN', 'las': 'PRON',
        'mon': 'PRON', 'ma': 'PRON', 'ton': 'PRON', 'ta': 'PRON', 'son': 'PRON', 'sa': 'DET', 'tos': 'PRON', 'llur': 'PRON', 'llurs': 'PRON',
        'tal': 'ADPa', 'tals': 'ADPa', 'mateix': 'PRON', 'mateixs': 'PRON', 'mateixa': 'PRON', 'mateixes': 'PRON',
        'mateixos': 'PRON', 'tot': 'PRON', 'tots': 'PRON', 'tota': 'PRON', 'totes': 'PRON', 'ses': 'ADP', 'mos': 'ADP',
        'sos': 'ADP', 'tes': 'ADP', 'es': 'DET', 'cada': 'ADP', 'mes': 'CCONJ', 'sens': 'ADP', 'sense': 'ADP',
        'dins': 'ADP', 'fora': 'ADP', 'entre': 'ADP', 'contra': 'ADP', 'davant': 'ADP', 'deçà': 'ADP', 'darrera': 'ADP',
        'damunt': 'ADP', 'envers': 'ADP', 'malgrat': 'ADP', 'mitjançant': 'ADP', 'prop': 'ADP', 'sota': 'ADP',
        'sobre': 'ADP', 'vers': 'ADP', 'rere': 'ADP', 'dedins': 'ADP', 'quen': 'ADP', 'quel': 'ADP', 'fe': 'NOUN',
        'oh': 'INTJ', 'ah': 'INTJ', 'eh': 'INTJ', 'uh': 'INTJ', 'ai': 'INTJ', 'oi': 'INTJ', 'ui': 'INTJ', 'uf': 'INTJ',
        'neva': 'VERB', 'eva': 'PROPN', 'altre': 'ADJ', 'altres': 'ADJ', 'altra': 'ADJ', 'cap': 'ADP', 'ex': 'ADP', "d'ex": 'ADP', 'pro': 'ADP'
        }

    new_doc = [[text, pos_, dep_] for text, pos_, dep_ in doc]
    for token in new_doc:
        token_text = token[0].lower()
        if token_text in corrections:
            token[1] = corrections[token_text]
        if token[1] == "PUNCT" and token[0] in string.punctuation:
            new_doc.remove(token)
        if '-' in token[0] and token[1] == 'PRON':
            token[1] = 'PRONe'
        if token[1] == 'PRON' and token[0] == 'que':
            token[1] = 'ADPa'
        if token[1] not in ["PRON", "PRONe", "VERB"] and '-' in token[0]: # Mosts compostos / ordinals
            while '-' in token[0]:
                split = re.split('-', token[0], 1)
                left = split[0]
                right = split[1]
                index = new_doc.index(token)
                new_doc.remove(token)

                left = [left, token[1], token[2]]
                right = [right, token[1], token[2]]

                if left[0] in corrections:
                    left = [left[0], corrections[left[0]], token[2]]
                if right[0] in corrections:
                    right = [right[0], corrections[right[0]], token[2]]

                new_doc.insert(index, left)
                new_doc.insert(index + 1, right)

                token = new_doc[index + 1]
    return new_doc


def ortho_repair(text: str):
    """
    Repairs orthographic errors in the given text based on predefined regex patterns.

    Args:
        text (str): The input text to be corrected.

    Returns:
        str: The corrected text.
    """
    regex_patterns = {
        r'ý': r'í', r"ÿ": r"ï", r'ehi([ae][snmu]?)\b': r'ei\1', r'([aeiou])(h)u': r'\1ü',
        r'no\-res': r'no-rès', r'\Bas$': r'es', r'(ç)([ie])': r'c\2', r'([dD])uu': r'\1u',
        r"qu'": r"qu·", r"\B([qg]u)'([aeiouàéèéìíòóúù])": r"\1\2 \2", r" +": r" ", r"(.') (.)": r"\1\2",
        r"([aeiouàéèéìíòóúù])·\1": r"\1 \1", r"([aeiouàéèéìíòóúù]) *· *([aeiouàéèéìíòóúù])": r"\1 \2", r"·": r"'",
        r"\b([sS][^aeiouàéèéìíòóúùyýÿhs]\B)": r"e\1", r"([aeiouy])h([iy]r)": r"\1\2", r"\Bch$": r"c", r"^ff": r"f"
        }
    for pattern, replacement in regex_patterns.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def ocr_errors(doc):
    """
    Corrects OCR errors in the given document based on predefined corrections.

    Args:
        doc (list): A list of tokens with their POS tags and dependencies.

    Returns:
        list: A corrected list of tokens with updated text.
    """
    errors = {
        'cm': 'em', 'ct': 'et', 'cn': 'en', 'cl': 'el',
        'juhý': 'juí', 'juhi': 'juí', 'juhy': 'juí'
        }

    new_doc = [[token.text, token.pos_, token.dep_] for token in doc]
    for token in new_doc:
        token_text = token[0].lower()
        if token_text in errors:
            token[0] = errors[token_text]
    return new_doc


def spacy_asyllabic(doc):
    """
    Joins asyllabic words with the word they phonologically depend on.

    Args:
        doc (list): A list of tokens with their POS tags and dependencies.

    Returns:
        list: A corrected list of tokens with joined asyllabic words.
    """
    asyllabic_L = ["d'", "l'", "s'", "m'", "n'", "t'", "qu'", "qu", "qu·", "d", "p", "L", "m·", "t·", "l·", "s·", "n·",
                   "l'", "ll'", "ll·", "c'", "c·", "[^aàáeéèíìióòóúùuüïâêîôûyý]['·]"]
    asyllabic_R = ["'ns", "'ns", "'l", "'m", "'n", "'s", "'ls", "'t", "'ts", "l", "ll", "lls", "'ll", "'lls", "ls", "s",
                   "·ns", "·l", "·ll", "·lls", "·m", "·n", "·s", "·ls", "·t", "·ts", "·ns", "·y", '-te', '-me', '-se',
                   '-nos', '-vos', '-lo', '-la', '-los', '-les', '-las', '-els', '-ne', '-en', '-mos', '-us', '-li',
                   '-lis', "['·-][^aàáeéèíìióòóúùuâêîôûyý]"]

    new_doc = [(text, pos_, dep_) for text, pos_, dep_ in doc]
    i = 0
    while i < len(new_doc) - 1:
        token = new_doc[i]
        if token[0].lower() in asyllabic_L:
            new_doc[i + 1] = (f"{token[0]}{new_doc[i + 1][0]}", new_doc[i + 1][1], new_doc[i + 1][2])
            new_doc.pop(i)
        elif token[0].lower() in asyllabic_R:
            new_doc[i - 1] = (f"{new_doc[i - 1][0]}{token[0]}", new_doc[i - 1][1], new_doc[i - 1][2])
            new_doc.pop(i)
        else:
            i += 1
    return new_doc


def posTagger(nlp, text: str):
    """
    Tags the words in a given text with their grammatical categories.

    Args:
        nlp: The SpaCy language model.
        text (str): The input text to be tagged.

    Returns:
        doc: The SpaCy document with POS tags.
    """

    def inicials(text):
        """
        Replaces initials and abbreviations in the text with their full forms.

        Args:
            text (str): The input text.

        Returns:
            str: The text with initials and abbreviations replaced.
        """
        replacements = {
            "B": "be", "C": "ce", "D": "de", "F": "efa", "G": "ge", "H": "hac", "J": "jota", "K": "ka", "L": "ela",
            "M": "ema", "N": "ena", "P": "pe", "Q": "cu", "R": "erra", "S": "essa", "T": "te", "V": "ve",
            "W": "ve-doble", "X": "ics", "Y": "i", "Z": "zeta", "Sr.": "senyor", "Dr.": "doctor", "Sra.": "senyora",
            "Dra.": "doctora", "Srta.": "senyoreta"
            }
        return " ".join(replacements.get(word, word) for word in text.split())

    text = clean_text(text)
    text = ortho_repair(text)
    text = inicials(text)
    doc = nlp(text)
    doc = ocr_errors(doc)
    doc = spacy_asyllabic(doc)
    doc = correct_spacy(doc)
    return doc
