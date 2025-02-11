"""Un mòdul per a l'etiquetatge morfosintàctic de textos en català."""
import re
import string

from .preprocess import clean_text


def correct_spacy(doc):
    corrections = {'e': 'CCONJ', 'y': 'CCONJ', 'amb': 'ADP', 'de': 'ADP', 'en': 'ADP', 'per': 'ADP',
                   'á': 'ADP', 'à': 'ADP',
                   'a': 'ADP', 'dels': 'ADP', 'del': 'ADP', 'als': 'DET', 'al': 'DET',
                   'hom': 'NOUN', 'om': 'NOUN', "lo": "DET", "des": 'ADP',
                   'tal': 'PRON', 'tals': 'PRON', "cap": "NOUN", "caps": "NOUN", 'així': 'ADV',
                   'cell': 'PRON', "quell": "PRON", "·quell": "PRON", 'ceyl': 'PRON', 'si': 'PRON', 'mi': 'PRON',
                   'que': 'PRON', 'què': 'PRON', 'qui': 'PRON', 'quin': 'PRON', 'quins': 'PRON', 'quina': 'PRON', 'quines': 'PRON',
                   'yo': 'PRON', 'vós': 'NOUN', 'nós': 'NOUN', 'ne': 'CCONJ', 'ni': 'CCONJ',
                   'seu': 'ADJ', 'seus': 'ADJ', 'seva': 'ADJ', 'seves': 'ADJ', 'seua': 'ADJ', 'seues': 'ADJ',
                   'sua': 'ADJ', 'sues': 'ADJ', 'meu': 'ADJ', 'meus': 'ADJ', 'meva': 'ADJ', 'meves': 'ADJ',
                   'meua': 'ADJ', 'meues': 'ADJ', 'teu': 'ADJ', 'teus': 'ADJ', 'teva': 'ADJ', 'teves': 'ADJ',
                   'teua': 'ADJ', 'teues': 'ADJ', 'nostre': 'ADJ', 'nostres': 'ADJ', 'nostra': 'ADJ', 'vostre': 'ADJ',
                   'vostres': 'ADJ', 'vostra': 'ADJ', 'un': 'NUM', 'una': 'NUM', 'uns': 'NUM', 'unes': 'NUM',
                   'aquests': 'PRON', 'aquestes': 'PRON', 'aquell': 'PRON', 'aquella': 'PRON', 'aquells': 'PRON',
                   'aquelles': 'PRON', 'aquest': 'PRON', 'aquesta': 'PRON', 'aqueix': 'PRON', 'aqueixa': 'PRON',
                   'aqueixos': 'PRON', 'aqueixes': 'PRON', 'este': 'PRON', 'esta': 'PRON', 'estos': 'PRON',
                   'estes': 'PRON', 'eixos': 'PRON', 'eixes': 'PRON', 'eixa': 'PRON', 'eixs': 'PRON', 'eixas': 'PRON',
                   'eix': 'PRON', 'això': 'PRON', 'açò': 'PRON', 'ço': 'PRON', 'so': 'NOUN', 'xo': 'PRON', "xô": 'PRON',
                   'xò': 'PRON',
                   "'xo": 'PRON', "'xô": 'PRON', "'xò": 'PRON',
                   'més': 'PRON', 'menys': 'PRON', 'molt': 'PRON', 'poc': 'PRON', 'pocs': 'PRON', 'molts': 'PRON',
                   'me': 'DET', '-me': 'DET', 'te': 'DET', '-te': 'DET', 'se': 'DET', '-se': 'DET', 'li': 'DET',
                   'los': 'DET', 'ho': 'DET', '-ho': 'DET', 'hi': 'DET', '-hi': 'DET',
                   '-li': 'DET', '-los': 'DET', '-la': 'DET', '-les': 'DET', '-els': 'DET', '-ne': 'DET', '-en': 'DET',
                   '-mos': 'DET', '-us': 'DET', 'nos': 'DET', '-nos': 'DET', 'vos': 'DET', '-vos': 'DET', 'us': 'DET',
                   'el': 'DET', 'els': 'DET', 'la': 'DET', 'les': 'DET',
                   'ab': 'ADP', 'com': 'ADP', 'quan': 'ADP', 'on': 'ADP', 'perquè': 'ADV', 'perque': 'ADV',
                   'perqué': 'ADV', 'no': 'ADP', 'sí': 'ADP',
                   'ja': 'ADP', 'encara': 'ADV', 'ans': 'ADV', 'ara': 'ADV', 'ací': 'ADV', 'allà': 'ADV', 'allí': 'ADV',
                   'açà': 'ADV', 'dallà': 'ADV',
                   'dallí': 'ADV', 'pus': 'ADV',
                   'tot': 'NOUN', 'tots': 'NOUN', 'tota': 'NOUN', 'totes': 'NOUN',
                   'am': 'VERB', 'cel': 'NOUN', 'cert': 'ADJ', 'certs': 'ADJ', 'certa': 'ADJ', 'certes': 'ADJ',
                   'val': 'VERB', "delit": "NOUN", "delits": "NOUN",
                   'mon': 'ADP', 'ma': 'ADP', 'ton': 'ADP', 'ta': 'ADP', 'son': 'ADP', 'sa': 'ADP',
                   'ses': 'ADP', 'mos': 'ADP', 'sos': 'ADP', 'tes': 'ADP', 'es': 'DET',
                   'cada': 'ADP', 'mes': 'CCONJ', 'sens': 'ADP', 'sense': 'ADP', 'dins': 'ADP', 'fora': 'ADP',
                   'entre': 'ADP', 'contra': 'ADP', 'davant': 'ADP', 'deçà': 'ADP', 'darrera': 'ADP', 'damunt': 'ADP',
                   'envers': 'ADP', 'malgrat': 'ADP', 'mitjançant': 'ADP', 'prop': 'ADP', 'sota': 'ADP', 'sobre': 'ADP',
                   'vers': 'ADP', 'rere': 'ADP', 'dedins': 'ADP', 'quen': 'ADP', 'quel': 'ADP',
                   #'sóc': 'AUX', 'soc': 'AUX', 'só': 'AUX', 'som': 'AUX', 'és': 'AUX', "s'és": 'AUX', 'est': 'AUX', 'é': 'AUX',
                   #'fou': 'AUX', 'foi': 'AUX', 'fó': 'AUX', 'ser': 'AUX', 'esser': 'AUX', 'ésser': 'AUX', 'ecer': 'AUX', 'écer': 'AUX', 'cer': 'AUX',
                   'fe': 'NOUN'

                   }

    new_doc = [[text, pos_, dep_] for text, pos_, dep_ in doc]
    for token in new_doc:
        if token[0].lower() in corrections:
            token[1] = corrections[token[0].lower()]
        if token[1] == "PUNCT" and token[0] in string.punctuation:
            new_doc.pop(new_doc.index(token))
    return new_doc


def ortho_repair(string: str):
    regex = {r'ý': r'í', r"ÿ": r"ï", r'ehi([ae][snmu]?)\b': r'ei\1', r'([aeiou])(h)u': r'\1ü',
             r'no\-res': r'no-rès', r'\Bas$': r'es', r'(ç)([ie])': r'c\2', r'([dD])uu': r'\1u',
             r"qu'": r"qu·", r"\B([qg]u)'([aeiouàéèéìíòóúù])": r"\1\2 \2", " +": " ", r"(.') (.)": r"\1\2",
             r"([aeiouàéèéìíòóúù])·\1": r"\1 \1", r"([aeiouàéèéìíòóúù]) *· *([aeiouàéèéìíòóúù])": r"\1 \2", "·": "'",
             r"\b([sS][^aeiouàéèéìíòóúùyýÿhs]\B)": r"e\1", r"([aeiouy])h([iy]r)": r"\1\2", "\Bch$": "c", "^ff": "f"
             }
    # r'([aeiou])(h)[iy]': r'\1ï',
    # r"([aeiouàéèéìíòóúùy]) *' *([^aeiouàéèéìíòóúù]+)": r"\1·\2",
    for expression, solution in regex.items():
        string = re.sub(expression, solution, string, flags=re.IGNORECASE)
    return string


def ocr_errors(doc):
    errors = {'cm': 'em', 'ct': 'et', 'cn': 'en', 'cl': 'el', 'juhý': 'juí', 'juhi': 'juí', 'juhy': "juí"}

    new_doc = [[token.text, token.pos_, token.dep_] for token in doc]
    for token in new_doc:
        if token[0].lower() in errors:
            token[0] = errors[token[0].lower()]
    return new_doc


def spacy_asyllabic(doc):
    """Un mòdul per juntar els mots assil·làbics amb el mot de què depenen fonològicament"""
    asyllabic_L = ["d'", "l'", "s'", "m'", "n'", "t'", "qu'", "qu", "qu·", "d", "p", "L", "m·", "t·", "l·", "s·", "n·",
                   "l'", "ll'", "ll·", "c'", "c·", "[^aàáeéèíìióòóúùuüïâêîôûyý]['·]"]
    asyllabic_R = ["'ns", "'ns", "'l", "'m", "'n", "'s", "'ls", "'t", "'ts", "l", "ll", "lls", "'ll", "'lls", "ls", "s",
                   "·ns", "·l", "·ll", "·lls", "·m", "·n",
                   "·s", "·ls", "·t", "·ts", "·ns", "·y", '-te', '-me', '-se', '-nos', '-vos', '-lo', '-la', '-los',
                   '-les', '-las', '-els', '-ne', '-en', '-mos', '-us', '-li', '-lis', "['·-][^aàáeéèíìióòóúùuâêîôûyý]"]

    new_doc = [(text, pos_, dep_) for text, pos_, dep_ in doc]
    # for token in new_doc:
    len_doc = len(new_doc) - 1
    i = 0
    while i < len_doc:
        token = new_doc[i]
        if token[0].lower() in asyllabic_L:
            next_token = i + 1
            if next_token < len(new_doc):
                new_doc[i + 1] = (f"{token[0]}{new_doc[i + 1][0]}", new_doc[i + 1][1], new_doc[i + 1][2])
                new_doc.pop(i)
                len_doc -= 1
                i -= 1
        elif token[0].lower() in asyllabic_R:
            new_doc[i - 1] = (f"{new_doc[i - 1][0]}{token[0]}", new_doc[i - 1][1], new_doc[i - 1][2])
            new_doc.pop(i)
            len_doc -= 1
            i -= 1
        i += 1
    return new_doc


def posTagger(nlp, text: str):
    """Etiqueta les paraules d'un text donat amb les seves categories gramaticals."""

    def inicials(text):
        returned = []
        dict = {"B": "be", "C": "ce", "D": "de", "F": "efa", "G": "ge", "H": "hac", "J": "jota", "K": "ka", "L": "ela",
                "M": "ema", "N": "ena", "P": "pe", "Q": "cu", "R": "erra", "S": "essa", "T": "te", "V": "ve",
                "W": "ve-doble", "X": "ics", "Y": "i", "Z": "zeta", "Sr.": "senyor", "Dr.": "doctor", "Sra.": "senyora",
                "Dra.": "doctora", "Srta.": "senyoreta"}
        for word in text.split():
            if word in dict:
                returned.append(dict[word])
            else:
                returned.append(word)
        return " ".join(returned)

    text = clean_text(text)
    text = ortho_repair(text)
    text = inicials(text)
    doc = nlp(text)
    doc = ocr_errors(doc)
    doc = correct_spacy(doc)
    doc = spacy_asyllabic(doc)
    return doc