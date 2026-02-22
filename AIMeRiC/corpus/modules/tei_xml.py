from lxml import etree

TEI_NS = "http://www.tei-c.org/ns/1.0"
XML_NS = "http://www.w3.org/XML/1998/namespace"


def _tei_root():
    # Namespace TEI com a DEFAULT (evita prefixos ns0)
    return etree.Element(f"{{{TEI_NS}}}TEI", nsmap={None: TEI_NS})


def _sub(parent, tag, text=None, **attrs):
    # Tots els elements TEI dins el mateix namespace
    el = etree.SubElement(parent, f"{{{TEI_NS}}}{tag}", **{k: str(v) for k, v in attrs.items()})
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

    # teiHeader
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
    # xml:id és atribut del namespace XML, no TEI
    metDecl = _sub(
        encodingDesc,
        "metDecl",
        **{f"{{{XML_NS}}}id": "aimeric"},
        type="met",
        pattern=r"((\+|\-)+)*",
    )
    _sub(metDecl, "metSym", "stressed syllable", value="+")
    _sub(metDecl, "metSym", "unstressed syllable", value="-")

    # profileDesc (metadades autor)
    profileDesc = _sub(teiHeader, "profileDesc")
    particDesc = _sub(profileDesc, "particDesc")
    listPerson = _sub(particDesc, "listPerson")

    author_id = results_dict.get("author_id") or "unknown_author"
    person = _sub(listPerson, "person", **{f"{{{XML_NS}}}id": str(author_id)})

    persName = _sub(person, "persName")
    _sub(persName, "name", str(results_dict.get("name") or ""))

    gender = results_dict.get("gender")
    if gender is not None:
        _sub(person, "sex", str(gender))

    born_date = results_dict.get("born_date")
    death_date = results_dict.get("death_date")
    if born_date is not None:
        _sub(person, "birth", when=str(born_date))
    if death_date is not None:
        _sub(person, "death", when=str(death_date))

    city = results_dict.get("city")
    if city:
        _sub(person, "note", f"city: {city}")
    dialect = results_dict.get("dialect")
    if dialect:
        _sub(person, "note", f"dialect: {dialect}")

    viaf = results_dict.get("viaf")
    if viaf:
        idno = _sub(person, "idno", str(viaf))
        idno.set("type", "VIAF")

    wiki_id = results_dict.get("wiki_id")
    if wiki_id:
        idno = _sub(person, "idno", str(wiki_id))
        idno.set("type", "Wikidata")

    # revisionDesc
    if versio:
        revisionDesc = _sub(teiHeader, "revisionDesc")
        _sub(revisionDesc, "change", f"Generated with AiMeRiC version {versio}")

    # text/body
    text = _sub(tei, "text")
    body = _sub(text, "body")

    div_author = _sub(body, "div", type="author", **{f"{{{XML_NS}}}id": str(author_id)})
    _sub(div_author, "head", str(author_name))

    books = results_dict.get("books", {})
    for book_id, book_data in books.items():
        div_book = _sub(div_author, "div", type="book", n=str(book_id))
        book_title = (book_data or {}).get("title") or str(book_id)
        _sub(div_book, "head", str(book_title))

        poems = (book_data or {}).get("poems", {})
        for poem_title, poem_data in poems.items():
            div_poem = _sub(div_book, "div", type="poem")
            head = _sub(div_poem, "head")
            _sub(head, "title", str(poem_title))

            lg = _sub(div_poem, "lg")

            verses = (poem_data or {}).get("verses", {})
            n = 1
            for verse_text_key, verse_payload in verses.items():
                verse_text = verse_text_key  # KEY del diccionari

                patro_metric_raw = (verse_payload or {}).get("patró mètric")
                met_pm = _patro_metric_to_plusminus(patro_metric_raw)
                extram = (verse_payload or {}).get("síl·labes extramètriques")
                if extram is not None:
                    if met_pm is not None:
                        met_pm += "-" * extram
                    else:
                        met_pm = "-" * extram
                attrs = {"n": str(n)}
                if met_pm is not None:
                    attrs["met"] = met_pm

                _sub(lg, "l", str(verse_text), **attrs)
                n += 1

    xml_bytes = etree.tostring(
        tei,
        xml_declaration=True,
        encoding="UTF-8",
        pretty_print=True
    )
    with open(output_path, "wb") as f:
        f.write(xml_bytes)