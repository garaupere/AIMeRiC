```markdown
                                 ╔═╗ ╦ ╔╦╗ ╔═╗ ╦═╗ ╦ ╔═╗ 
                                 ╠═╣ ║ ║║║ ║╣  ╠╦╝ ║ ║   
                                 ╩ ╩ ╩ ╩ ╩ ╚═╝ ╩╚═ ╩ ╚═╝ 
                 Anàlisi Informatitzada del Metre i el Ritme del Català
                              ©2025, Pere Garau Borràs

````
---
Aquest repositori conté l'aplicatiu _**AIMeRiC**: **A**nàlisi **I**nformatitzada del **Me**tre i el **Ri**tme del **C**atalà_ confeccionat en el marc la tesi **<i>La variabilitat rítmica del decasíl·lab català</i>** de Pere Garau Borràs a la Universitat de les Illes Balears.
Les eines aplegades sota aquest aplicatiu permeten l'escansió (i.e. anàlisi mètrica i rítmica) automatitzada de textos en català. Principalment, el programa ha estat desevolupat per a l'anàlisi de poesia catalana.

## Requeriments

- Python 3.x
- [colorama](https://pypi.org/project/colorama/)
- [spacy](https://spacy.io/)
- [cfonts](https://pypi.org/project/cfonts/)
- [AIMeRiC](https://github.com/garaupere/AIMeRiC)

## Instal·lació

1. Clonar el repositori.
2. Instal·lar les dependències:


```bash
pip install colorama spacy cfonts
```

3. Descarregar el model de Spacy per a català:

```bash
python -m spacy download ca_core_news_md
```

## Ús

### Funcions

L'aplicatiu **AIMeRiC** necessita una memòria externa per funcionar. Aquesta memòria ha de contenir una carpeta `compile_files` amb els fitxers de text que conformen el corpus, segons l'estructura següent:

```filesystem
 compile_files
    └── corpus
        └── subcorpus
            ├── autor_1.info
            └─── autor_1
                ├── obra_1.info
                └──── obra_1
                    ├── book.info
                    ├── fitxer_1.txt
                    └── fitxer_2.txt 
```

Pel que fa a l'estructura dels fitxers `.info`, han de presentar aquesta estructura:

#### autor.info
```json
{
    "author_id": "Jacint Verdaguer",
    "name": "Verdaguer i Santaló, Jacint",
    "gender": 0,
    "born_date": 1845,
    "death_date": 1902,
    "city": "Folgueroles",
    "dialect": "central",
    "viaf": "9841818", 
    "wiki_id": "Q379290"
}
```

#### book.info
```json
{
    "title": "L'Atlàntida",
    "year": 1877,
    "publisher": "Edicions 62"
}
```

Pel que fa al format dels fitxers `.txt`, cal que incloguin els versos separats per un salt de línia `\n`.
El resultat del corpus compilat i sense etiquetar és un fitxer `.json`, que es desa dins una carpeta anomenada `corpora`. L'estructura del corpus compilat és sempre:

```filesystem
 corpora
 └── corpus
     └── sense etiquetat
         └── json
             ├── corpus_autor_1.json
             └── corpus_autor_2.json
```

### Compilar un Corpus

Per compilar un corpus:

```python
compile(raw_files_path, corpus)
```

### Etiquetar un Corpus

Per etiquetar un corpus:

```python
etiq(corpus)
```

### Exploració Estadística del Corpus

Per realitzar una exploració estadística del corpus:

```python
explota(corpus)
```

### Escanejar un Vers

Per escanejar un vers:

```python
scan(nlp, verse, goal=10)
```

### Ajuda

Per obtenir ajuda:

```python
help()
```

### Funció Principal

La funció `main()` és la funció principal del programa. Aquí es gestionen les diferents opcions disponibles:
```python
- **-list**: Llista de corpus disponibles per compilar.
- **-help**: Mostra les opcions disponibles.
- **-comp**: Compilar un corpus.
- **-etiq**: Etiquetar un corpus.
- **-desc**: Descripció estadística del corpus.
- **-expl**: Exploració estadística del corpus.
- **-ot**: Avaluació de les restriccions OT.
- **-test**: Validar les dades de test.
- **-scan**: Analitzar un vers.
- **-prosa**: Analitzar un corpus de prosa.
- **-bkp**: Còpia de seguretat del corpus.

````

### Exemple d'Execució

Per executar el programa:

```bash
python AIMeRiC.py
```

## Llicència

Aquest projecte està llicenciat sota els termes del Copyright ©2025, Pere Garau Borràs.

## Estructura del programa

Internament, aquest programa s'estructura en dos paquets:

- `corpus` és el paquet que conté el corpus, les eines de compilació, la interfície d'etiquetatge i explotació del corpus de la tesi. :warning: Aquest paquet no és funcional sense el paquet `escansor`.
- `escansor_scr` és el paquet que conté el nucli de l'escansor, l'aplicació encarregada d'analitzar mètricament els versos. Aquest paquet permet l'ús de l'escansor de manera independent de l'aplicació de corpus.

---

#### **©2025, Pere Garau Borràs**
<img src="https://logo.uib.cat/digitalAssets/338/338690_logo-uib-horizontal300.png" alt="UIB" width="30%">