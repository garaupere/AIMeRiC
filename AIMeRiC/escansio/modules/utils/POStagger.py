# AIMeRiC/escansio/modules/utils/POStagger.py
"""Un mòdul per a l'etiquetatge morfosintàctic de textos en català."""
import re
import string

from spacy.tokens import Doc, Token

from AIMeRiC.escansio.modules.utils.preproc import preproc_text


def correct_spacy(doc):
    """
    Corregeix les etiquetes POS i altres metadades en un document donat de Spacy
    a partir d'un conjunt de correccions predefinides.
    Args:
        doc (list): Una llista de tokens amb les seves etiquetes POS i dependències.
    Returns:
        list: Una llista corregida de tokens amb etiquetes actualitzades.
    """
    corrections = {
        'el': 'DET', 'la': 'DET', 'els': 'DET', 'les': 'DET', 'e': 'CCONJ', 'y': 'CCONJ', 'puix': 'SCONJ',
        'amb': 'ADPa', 'de': 'ADPa', 'en': 'ADPa', 'per': 'ADPa',
        'á': 'ADPa', 'à': 'ADPa', 'a': 'ADPa', 'dels': 'ADPa', 'del': 'ADPa', 'als': 'ADPa', 'al': 'ADPa',
        'des': 'ADPa', "me'ls": 'DET',
        'res': 'NOUN', 'hom': 'NOUN', 'om': 'NOUN', 'així': 'ADV', 'cell': 'PRON', 'quell': 'PRON', '·quell': 'PRON',
        'ceyl': 'PRON', 'cal': 'AUX',
        'mi': 'PRON', 'què': 'PRON', 'qui': 'PRON', 'quin': 'PRON', 'quins': 'PRON',
        'quina': 'PRON', 'quines': 'PRON', 'yo': 'PRON', 'vós': 'NOUN', 'nós': 'NOUN', 'ne': 'CCONJ', 'ni': 'CCONJ',
        'seu': 'PRON', 'seus': 'PRON', 'seva': 'PRON', 'seves': 'PRON', 'seua': 'PRON', 'seues': 'PRON', 'sua': 'PRON',
        'sues': 'PRON', 'meu': 'PRON', 'meus': 'PRON', 'meva': 'PRON', 'meves': 'PRON', 'meua': 'PRON', 'meues': 'PRON',
        'teu': 'PRON', 'teus': 'PRON', 'teva': 'PRON', 'teves': 'PRON', 'teua': 'PRON', 'teues': 'PRON',
        'nostre': 'PRON', 'em': 'PRON', 'et': 'PRON', 'te': 'PRON', 'me': 'PRON', '-me': 'PRON', '-te': 'PRON',
        'li': 'PRON', '-li': 'PRON', '-lo': 'PRON', '-la': 'PRON', '-los': 'PRON', '-les': 'PRON', '-nos': 'PRON',
        '-vos': 'PRON', '-mos': 'PRON',
        'se': 'PRON', 'los': 'DET', 'lo': 'DET', 'mos': 'PRON', 'vos': 'PRON',
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
        "'xò": 'PRON', 'més': 'PRON', 'mès': 'PRON', 'menys': 'PRON', 'molt': 'PRON', 'poc': 'PRON', 'pocs': 'PRON',
        'molts': 'PRON',
        'ab': 'ADPa', 'com': 'PRON', 'quan': 'ADP', 'on': 'ADPa', 'perquè': 'ADV', 'perque': 'ADV', 'perqué': 'ADV',
        'no': 'ADP', 'sí': 'ADP', 'ja': 'ADP', 'encara': 'ADV', 'ans': 'ADV', 'ara': 'ADV', 'ací': 'ADV', 'allà': 'ADV',
        'allí': 'ADV', 'açà': 'ADV', 'dallà': 'ADV', 'dallí': 'ADV', 'pus': 'ADV', 'am': 'VERB', 'cel': 'NOUN',
        'cert': 'ADJ', 'certs': 'ADJ', 'certa': 'ADJ', 'certes': 'ADJ', 'val': 'VERB', 'delit': 'NOUN',
        'delits': 'NOUN', 'las': 'PRON',
        'mon': 'PRON', 'ma': 'PRON', 'ton': 'PRON', 'ta': 'PRON', 'son': 'PRON', 'sa': 'DET', 'tos': 'PRON',
        'llur': 'PRON', 'llurs': 'PRON',
        'tal': 'ADPa', 'tals': 'ADPa', 'mateix': 'PRON', 'mateixs': 'PRON', 'mateixa': 'PRON', 'mateixes': 'PRON',
        'mateixos': 'PRON', 'tot': 'PRON', 'tots': 'PRON', 'tota': 'PRON', 'totes': 'PRON',
        'sos': 'ADP', 'tes': 'ADP', 'es': 'DET', 'cada': 'ADP', 'mes': 'CCONJ', 'sens': 'ADP', 'sense': 'ADP',
        'dins': 'ADP', 'fora': 'ADP', 'entre': 'ADP', 'contra': 'ADP', 'davant': 'ADP', 'deçà': 'ADP', 'darrera': 'ADP',
        'damunt': 'ADP', 'envers': 'ADP', 'malgrat': 'ADP', 'mitjançant': 'ADP', 'prop': 'ADP', 'sota': 'ADP',
        'sobre': 'ADP', 'vers': 'ADP', 'rere': 'ADP', 'dedins': 'ADP', 'quen': 'ADP', 'quel': 'ADP', 'fe': 'NOUN',
        'oh': 'INTJ', 'ah': 'INTJ', 'eh': 'INTJ', 'uh': 'INTJ', 'ai': 'INTJ', 'oi': 'INTJ', 'ui': 'INTJ', 'uf': 'INTJ',
        'neva': 'VERB', 'eva': 'PROPN', 'altre': 'ADJ', 'altres': 'ADJ', 'altra': 'ADJ', 'cap': 'ADP', 'ex': 'ADP',
        "d'ex": 'ADP', 'pro': 'ADP', 'desert': 'NOUN', 'deserts': 'NOUN', "d'en": 'DET', 'ben': 'DET', 'he': 'AUX',
        'vaig': 'AUX', 'ha': 'AUX', 'han': 'AUX', 'vam': 'AUX', 'vau': 'AUX', 'van': 'AUX', 'vàrem': 'AUX',
        'vàreu': 'AUX', 'varen': 'AUX', 'havia': 'AUX', 'havíem': 'AUX', 'havieu': 'AUX',
        'urss': 'PROPN', 'front': 'NOUN', "dú": 'VERB', 'vull': 'AUX', 'vol': 'AUX', 'és': 'AUX', 'ets': 'AUX',
        'soc': 'AUX', 'som': 'AUX', 'sou': 'AUX',
        'sóc': 'AUX', 'só': 'AUX',
        'era': 'AUX', 'eres': 'AUX', 'érem': 'AUX', 'éreu': 'AUX', 'eren': 'AUX', 'seré': 'AUX', 'seràs': 'AUX',
        'serà': 'AUX',
        'sereu': 'AUX', 'serem': 'AUX', 'seran': 'AUX', 'siguí': 'AUX', 'sigués': 'AUX', 'sigui': 'AUX',
        'siguem': 'AUX', 'sigueu': 'AUX', 'siguin': 'AUX',
        'haguí': 'AUX', 'hagués': 'AUX', 'hagi': 'AUX', 'haguem': 'AUX', 'hagueu': 'AUX', 'hagin': 'AUX', 'hàgiu': 'AUX',
        'nou': 'ADJ', 'mig': 'ADJ', 'fet': 'ADJ'
    }

    normalized = []
    for item in doc:
        # spacy Token object
        if hasattr(item, "text") and not isinstance(item, (list, tuple)):
            text = item.text
            pos_ = getattr(item, "pos_", None)
            dep_ = getattr(item, "dep_", None)
            lemma_ = getattr(item, "lemma_", None)
            morph = getattr(item, "morph", None)
            head = getattr(item, "head", None)
        elif isinstance(item, (list, tuple)):
            if len(item) >= 6:
                text, pos_, dep_, lemma_, morph, head = item[:6]
            elif len(item) == 3:
                text, pos_, dep_ = item
                lemma_, morph, head = None, None, None
            else:
                # pad shorter sequences
                parts = list(item) + [None] * (6 - len(item))
                text, pos_, dep_, lemma_, morph, head = parts
        else:
            # unknown item type, skip
            continue

        normalized.append([text, pos_, dep_, lemma_, morph, head])

    # Aplica les correccions definides a cada token
    new_doc = normalized
    for token in new_doc[:]:  # itera sobre una còpia per permetre-hi modificacions
        token_text = (token[0] or "").lower()
        if token_text in corrections:
            token[1] = corrections[token_text]

        elif token[1] == "PUNCT" and token_text in string.punctuation:
            try:
                punct_prev = new_doc.index(token)-1 # Fusiona el token de puntuació amb el token anterior: 'sol', ',' > 'sol,'
                new_doc[punct_prev][0] = new_doc[punct_prev][0] + token[0]
            except ValueError:
                pass
            try:
                new_doc.remove(token)
            except ValueError:
                pass
            continue
        elif '-' in token_text and token[1] == 'PRON':
            token[1] = 'PRONe'
        elif token[1] == 'PRON' and token_text == 'que':
            token[1] = 'ADPa'
        elif token[1] not in ["PRON", "PRONe", "VERB", 'PUNCT'] and '-' in token_text:  # Mosts compostos / ordinals
            if not (token_text and token_text.startswith('-')):
                # split repetidament fins que no hi hagi més guions
                while token[0] and '-' in token[0]:
                    split = re.split('-', token[0], 1)
                    left = split[0]
                    right = split[1]
                    try:
                        index = new_doc.index(token)
                    except ValueError:
                        break
                    # remove current token
                    try:
                        new_doc.pop(index)
                    except IndexError:
                        break

                    left_item = [left, token[1], token[2], token[3], token[4], token[5]]
                    right_item = [right, token[1], token[2], token[3], token[4], token[5]]

                    if left_item[0] in corrections:
                        left_item[1] = corrections[left_item[0]]
                    if right_item[0] in corrections:
                        right_item[1] = corrections[right_item[0]]

                    new_doc.insert(index, left_item)
                    new_doc.insert(index + 1, right_item)

                    # avança l'índex al següent token
                    if index + 1 < len(new_doc):
                        token = new_doc[index + 1]
                    else:
                        break

    return new_doc


def ortho_repair(text: str):
    """
    Repara errors ortogràfics comuns en el text donat utilitzant patrons regex predefinits.
    Args:
        text (str): El text d'entrada.
    Returns:
        str: El text amb errors ortogràfics corregits.
    """
    regex_patterns = {
        r'ý': r'í', r"ÿ": r"ï", r'ehi([ae][snmu]?)\b': r'ei\1', r'([aeiou])(h)u': r'\1ü',
        r'no\-res': r'no-rès', r'\Bas$': r'es', r'(ç)([ie])': r'c\2', r'([dD])uu': r'\1ú',
        r"qu'": r"qu·", r"\B([qg]u)'([aeiouàéèéìíòóúù])": r"\1\2 \2", r" +": r" ", r"(.') (.)": r"\1\2",
        r"([aeiouàéèéìíòóúù])·\1": r"\1 \1", r"([aeiouàéèéìíòóúù]) *· *([aeiouàéèéìíòóúù])": r"\1 \2", r"·": r"'",
        r"([aeiouy])h([iy]r)": r"\1\2", r"\Bch$": r"c", r"^ff": r"f"
    }
    for pattern, replacement in regex_patterns.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def ocr_errors(doc):
    """
   Corregeix errors comuns d'OCR en un document donat.
    Args:
        doc (list): Una llista de tokens amb les seves etiquetes POS i dependències.
    Returns:
        list: Una llista corregida de tokens amb errors d'OCR solucionats.
    """
    errors = {
        'cm': 'em', 'ct': 'et', 'cn': 'en', 'cl': 'el',
        'juhý': 'juí', 'juhi': 'juí', 'juhy': 'juí'
    }

    new_doc = [[token.text, token.pos_, token.dep_, token.lemma_, token.morph, token.head] for token in doc]
    for token in new_doc:
        token_text = token[0].lower()
        if token_text in errors:
            token[0] = errors[token_text]
    return new_doc


def spacy_asyllabic(doc):
    """
   Ajunta tokens asil·làbics en un document donat.
    Args:
        doc (list): Una llista de tokens amb les seves etiquetes POS i dependències.
    Returns:
        list: Una llista de tokens amb asil·làbics ajuntats.
    """
    asyllabic_L = ["d'", "l'", "s'", "m'", "n'", "t'", "qu'", "qu", "qu·", "d", "p", "L", "m·", "t·", "l·", "s·", "n·",
                   "l'", "ll'", "ll·", "c'", "c·", "[^aàáeéèíìióòóúùuüïâêîôûyý]['·]"]
    asyllabic_R = ["'ns", "'ns", "'l", "'m", "'n", "'s", "'ls", "'t", "'ts", "l", "ll", "lls", "'ll", "'lls", "ls", "s",
                   "·ns", "·l", "·ll", "·lls", "·m", "·n", "·s", "·ls", "·t", "·ts", "·ns",
                   "·y"]  #,'-te', '-me', '-se',
    #'-nos', '-vos', '-lo', '-la', '-los', '-les', '-las', '-els', '-ne', '-en', '-mos', '-us', '-li', '-hi'
    #'-lis', "['·-][^aàáeéèíìióòóúùuâêîôûyý]"]

    new_doc = [(text, pos_, dep_, lemma_, morph, head) for text, pos_, dep_, lemma_, morph, head in doc]
    i = 0
    while i < len(new_doc) - 1:
        token = new_doc[i]
        if token[0].lower() in asyllabic_L:
            # merge left into next
            new_doc[i + 1] = (f"{token[0]}{new_doc[i + 1][0]}", new_doc[i + 1][1], new_doc[i + 1][2], new_doc[i + 1][3],
                              new_doc[i + 1][4], new_doc[i + 1][5])
            new_doc.pop(i)
        elif token[0].lower() in asyllabic_R:
            # merge right into previous
            new_doc[i - 1] = (f"{new_doc[i - 1][0]}{token[0]}", new_doc[i - 1][1], new_doc[i - 1][2], new_doc[i - 1][3],
                              new_doc[i - 1][4], new_doc[i - 1][5])
            new_doc.pop(i)
        else:
            i += 1
    return new_doc


def prones(doc):
    def previous_token(token, doc):
        """Comprova si el token anterior existeix i retorna'l, sinó retorna None."""
        index = doc.index(token)
        if index > 0:
            return doc[index - 1]
        return None

    for token in doc:
        if '-' in token[0]:
            if token[0].startswith('-'):
                token[1] = 'PRONe'
                if previous_token(token, doc):
                    prev = previous_token(token, doc)
                    prev[0] = f"{prev[0]}-"

    return doc


def posTagger(nlp, text: str):
    """
    Realitza l'etiquetatge morfosintàctic d'un text en català utilitzant SpaCy i diverses correccions específiques.
    Args:
        nlp: Un objecte SpaCy carregat amb el model de català.
        text (str): El text d'entrada a etiquetar.
    Returns:
        list: Una llista de SpaCy Token objects amb les etiquetes morfosintàctiques corregides.
    """
    text = preproc_text(text)
    text = ortho_repair(text)
    doc = nlp(text)
    doc = ocr_errors(doc)
    doc = spacy_asyllabic(doc)
    doc = correct_spacy(doc)
    doc = prones(doc)

    # Assegura que les extensions de Token existeixen
    ext_names = {
        "upos_corr": None,
        "lemma_corr": None,
        "morph_corr": None,
        "dep_corr": None,
        "head_corr": None
    }
    for name, default in ext_names.items():
        if not Token.has_extension(name):
            Token.set_extension(name, default=default)

    # `doc`és ara una llista de tuples corregides
    tokens = doc
    words = []
    for tok in tokens:
        # Safe unpack / pad
        if isinstance(tok, (list, tuple)):
            parts = list(tok) + [None] * (6 - len(tok))
            text_, pos_, dep_, lemma_, morph, head = parts[:6]
        else:
            # fallback (shouldn't happen because correct_spacy normalizes), treat as str
            text_ = str(tok)
        words.append(text_ or "")

    # Build a new Doc from corrected token texts
    new_doc = Doc(nlp.vocab, words=words)  # valors buits

    # Assigna les etiquetes corregides als tokens del nou Doc
    for i, tok in enumerate(tokens):
        # pad/unpack els tuples
        if isinstance(tok, (list, tuple)):
            parts = list(tok) + [None] * (6 - len(tok))
            text_, pos_, dep_, lemma_, morph, head = parts[:6]
        else:
            text_, pos_, dep_, lemma_, morph, head = tok, None, None, None, None, None

        token = new_doc[i]
        # Assigna les etiquetes corregides POS si es pot
        if pos_:
            try:
                token.pos_ = pos_
            except Exception:
                pass
        # Desa les etiquetes corregides com a extensions
        token._.upos_corr = pos_
        token._.lemma_corr = lemma_
        token._.morph_corr = morph
        token._.dep_corr = dep_
        token._.head_corr = head

    # Retorna el nou Doc amb les correccions aplicades
    return list(new_doc)


if __name__ == "__main__":
    text = "de dol,"
    import spacy
    nlp = spacy.load("ca_core_news_md")
    words = posTagger(nlp, text)
    for w in words:
        print(w.i, w.text, w.lower_, w.pos_, w.dep_, w.head.i, w.has_head())
        print(
            f"  Corrections: UPOS={w._.upos_corr}, LEMMA={w._.lemma_corr}, MORPH={w._.morph_corr}, DEP={w._.dep_corr}, HEAD={w._.head_corr}")
