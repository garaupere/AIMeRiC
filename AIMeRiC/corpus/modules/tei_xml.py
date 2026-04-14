from lxml import etree

TEI_NS = "http://www.tei-c.org/ns/1.0"
XML_NS = "http://www.w3.org/XML/1998/namespace"


def _tei_root():
    return etree.Element(f"{{{TEI_NS}}}TEI", nsmap={None: TEI_NS})


def _sub(parent, tag, text=None, **attrs):
    el = etree.SubElement(
        parent,
        f"{{{TEI_NS}}}{tag}",
        **{k: str(v) for k, v in attrs.items()}
    )
    if text is not None:
        el.text = text
    return el


def _patro_metric_to_plusminus(patro_metric) -> str | None:
    if patro_metric is None:
        return None

    if isinstance(patro_metric, (list, tuple)):
        out = []
        for x in patro_metric:
            if x == 0 or x == "0":
                out.append("-")
            elif x == 1 or x == "1":
                out.append("+")
            else:
                return None
        return "".join(out)

    if isinstance(patro_metric, str):
        digits = [ch for ch in patro_metric if ch in ("0", "1")]
        if not digits:
            return None
        return "".join("+" if d == "1" else "-" for d in digits)

    return None


# ------------------------------------------------------------
# INFERÈNCIA D’ESTROFISME
# ------------------------------------------------------------

def _infer_stanza_structure(num_verses: int) -> tuple[list[int], str | None]:
    """
    Retorna:
        ([llargades_estofes], tipus_global_poema)
    """

    # SONET canònic
    if num_verses == 14:
        return [4, 4, 3, 3], "sonet"

    # SEXTINA (6 sextets = 36 versos)
    if num_verses == 36:
        return [6, 6, 6, 6, 6, 6], "sextina"

    # SEXTET
    if num_verses == 6:
        return [6], None

    # QUARTET
    if num_verses == 4:
        return [4], None

    # TERCET
    if num_verses == 3:
        return [3], None

    # Per defecte: una sola estrofa
    return [num_verses], None


def _classify_stanza(length: int) -> str | None:
    if length == 3:
        return "tercet"
    if length == 4:
        return "quartet"
    if length == 6:
        return "sextet"
    return None


# ------------------------------------------------------------
# EXPORTADOR TEI
# ------------------------------------------------------------

def export_author_results_dict_to_tei(
    results_dict: dict,
    output_path: str,
    versio: str | None = None,
    corpus_id: str = "CoVerCat.Deca",
    corpus_title: str = "CoVerCat.Deca",
    corpus_principal: str = "Pere Garau Borràs",
    corpus_resp_name: str = "Pere Garau Borràs",
    corpus_resp_desc: str = "AiMeRiC (automatic metrical annotation and TEI export)",
):

    tei = _tei_root()

    # ------------------------------------------------------------
    # HEADER
    # ------------------------------------------------------------

    teiHeader = _sub(tei, "teiHeader")
    fileDesc = _sub(teiHeader, "fileDesc")
    titleStmt = _sub(fileDesc, "titleStmt")

    author_name = results_dict.get("name") or results_dict.get("author_id") or "unknown-author"

    _sub(titleStmt, "title", f"{corpus_title} — {author_name} (TEI export)")
    _sub(titleStmt, "principal", corpus_principal)

    respStmt = _sub(titleStmt, "respStmt")
    _sub(respStmt, "name", corpus_resp_name)
    _sub(respStmt, "resp", corpus_resp_desc)

    publicationStmt = _sub(fileDesc, "publicationStmt")
    _sub(publicationStmt, "publisher", "CoVerCat / AiMeRiC")
    if versio:
        _sub(publicationStmt, "idno", f"AiMeRiC {versio}")

    sourceDesc = _sub(fileDesc, "sourceDesc")
    bibl = _sub(sourceDesc, "bibl")
    _sub(bibl, "title", corpus_title)
    _sub(bibl, "idno", corpus_id)
    _sub(bibl, "author", corpus_principal)

    # encodingDesc
    encodingDesc = _sub(teiHeader, "encodingDesc")
    metDecl = _sub(
        encodingDesc,
        "metDecl",
        **{f"{{{XML_NS}}}id": "aimeric"},
        type="met",
        pattern=r"((\+|\-)+)*",
    )
    _sub(metDecl, "metSym", "stressed syllable", value="+")
    _sub(metDecl, "metSym", "unstressed syllable", value="-")

    # profileDesc
    profileDesc = _sub(teiHeader, "profileDesc")
    particDesc = _sub(profileDesc, "particDesc")
    listPerson = _sub(particDesc, "listPerson")

    author_id = results_dict.get("author_id") or "unknown_author"
    person = _sub(listPerson, "person", **{f"{{{XML_NS}}}id": str(author_id)})

    persName = _sub(person, "persName")
    _sub(persName, "name", str(results_dict.get("name") or ""))

    if results_dict.get("gender") is not None:
        _sub(person, "sex", str(results_dict.get("gender")))

    if results_dict.get("born_date") is not None:
        _sub(person, "birth", when=str(results_dict.get("born_date")))

    if results_dict.get("death_date") is not None:
        _sub(person, "death", when=str(results_dict.get("death_date")))

    if results_dict.get("city"):
        _sub(person, "note", f"city: {results_dict.get('city')}")

    if results_dict.get("dialect"):
        _sub(person, "note", f"dialect: {results_dict.get('dialect')}")

    if results_dict.get("viaf"):
        idno = _sub(person, "idno", str(results_dict.get("viaf")))
        idno.set("type", "VIAF")

    if results_dict.get("wiki_id"):
        idno = _sub(person, "idno", str(results_dict.get("wiki_id")))
        idno.set("type", "Wikidata")

    if versio:
        revisionDesc = _sub(teiHeader, "revisionDesc")
        _sub(revisionDesc, "change", f"Generated with AiMeRiC version {versio}")

    # ------------------------------------------------------------
    # TEXT
    # ------------------------------------------------------------

    text = _sub(tei, "text")
    body = _sub(text, "body")

    div_author = _sub(body, "div", type="author", **{f"{{{XML_NS}}}id": str(author_id)})
    _sub(div_author, "head", str(author_name))

    books = results_dict.get("books", {})

    for book_id, book_data in books.items():
        div_book = _sub(div_author, "div", type="book", n=str(book_id))
        _sub(div_book, "head", (book_data or {}).get("title") or str(book_id))

        poems = (book_data or {}).get("poems", {})

        for poem_title, poem_data in poems.items():
            div_poem = _sub(div_book, "div", type="poem")
            head = _sub(div_poem, "head")
            _sub(head, "title", str(poem_title))

            verses = (poem_data or {}).get("verses", {})
            verses_items = list(verses.items())
            num_verses = len(verses_items)

            stanza_structure, poem_type = _infer_stanza_structure(num_verses)

            if poem_type:
                div_poem.set("subtype", poem_type)

            n_global = 1
            cursor = 0

            for stanza_len in stanza_structure:
                lg = _sub(div_poem, "lg")

                stanza_type = _classify_stanza(stanza_len)
                if stanza_type:
                    lg.set("type", stanza_type)

                for _ in range(stanza_len):
                    verse_text_key, verse_payload = verses_items[cursor]
                    cursor += 1

                    patro_metric_raw = (verse_payload or {}).get("patró mètric")
                    met_pm = _patro_metric_to_plusminus(patro_metric_raw)
                    extram = (verse_payload or {}).get("síl·labes extramètriques")

                    if extram is not None:
                        if met_pm is not None:
                            met_pm += "-" * extram
                        else:
                            met_pm = "-" * extram

                    attrs = {"n": str(n_global)}
                    if met_pm is not None:
                        attrs["met"] = met_pm

                    _sub(lg, "l", str(verse_text_key), **attrs)
                    n_global += 1

    xml_bytes = etree.tostring(
        tei,
        xml_declaration=True,
        encoding="UTF-8",
        pretty_print=True
    )

    with open(output_path, "wb") as f:
        f.write(xml_bytes)