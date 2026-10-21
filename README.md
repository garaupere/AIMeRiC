<div align="center">
    
<img src="logo.png" alt="aimeric" width="400"/>

<hr>
    
[![CC BY-NC-ND 4.0][cc-by-nc-nd-image]][cc-by-nc-nd]

[cc-by-nc-nd]: http://creativecommons.org/licenses/by-nc-nd/4.0/
[cc-by-nc-nd-image]: https://licensebuttons.net/l/by-nc-nd/4.0/88x31.png
[cc-by-nc-nd-shield]: https://img.shields.io/badge/License-CC%20BY--NC--ND%204.0-lightgrey.svg
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
</div>

<h2>📖 Sobre el repositori</h2>
Aquest repositori conté l'aplicació **AIMeRiC**, desenvolupada per a l'escansió automatitzada de textos en català, especialment poesia. L'eina ha estat gestada com a part de la tesi doctoral <i>La variabilitat rítmica del decasíl·lab català</i> de Pere Garau Borràs (UIB).

<h2>📦 Requeriments</h2>

- Python 3.x
- Llibreries Python: `colorama`, `spacy`, `cfonts`
- Model de Spacy per a català: `ca_core_news_md`

<h2>⚙️ Instal·lació</h2>

1. Clonar el repositori.
2. Instal·lar les dependències:

```bash
pip install -r requirements.txt
```

3. Descarregar el model de Spacy:

```bash
python -m spacy download ca_core_news_md
```

<h2>🛠️ Ús</h2>
<h3>🧱 Estructura del programa</h3>

Aquest programa s'estructura en dos paquets:

- `corpus` és el paquet que conté el corpus, les eines de compilació, la interfície d'etiquetatge i explotació del corpus de la tesi. :warning: Aquest paquet no és funcional sense el paquet `escansio`.
- `escansio` és el paquet que conté el nucli de l'escansor, l'aplicació encarregada d'analitzar mètricament els versos. Aquest paquet permet l'ús de l'escansor de manera independent de l'aplicació de corpus.


<h3>📚 El mòdul corpus</h3>
El paquet corpus s’encarrega de la compilació i etiquetatge mètric dels
corpus poètics i prosístics. Aquest paquet inclou les següents funcions principals:
compilació de corpus, etiquetatge mètric, preparació de dades per a l’exploració
estadística i còpia de seguretat. El paquet presenta tres funcions principals: disposar
els texts en un format processable per l’escansor, establir una interfície entre el
corpus sense etiquetat i l’eina d’etiquetatge i, finalment, permetre la disposició de
les dades per a l’exploració.

Els fitxers que han de ser compilats en el corpus han de seguir aquesta estructura de directoris:

```plaintext
compile_files/
└── corpus/
    └── subcorpus/
        ├── autor_1.info
        └── autor_1/
            ├── obra_1.info
            └── obra_1/
                ├── book.info
                ├── fitxer_1.txt
                └── fitxer_2.txt
```

- **autor.info**: Informació de l'autor en format JSON.
- **book.info**: Informació de l'obra en format JSON.
- **fitxers `.txt`**: Contenen els versos separats per línies.

Els fitxers `.info` han de ser fitxers en format JSON i han de seguir aquestes estructures:
- `autor.info`
```json
{
    "author_id": "Blai Bonet",
    "name": "Bonet i Rigo, Blai",
    "gender": 0,
    "born_date": 1926,
    "death_date": 1997,
    "city": "Santanyí",
    "dialect": "balear",
    "viaf": "69056909",
    "wiki_id": "Q8248572",
    "font": "donació"
}
```
- `book.info`
```json
{
"title": "Esbós de tres oratoris",
"year": 1957,
"publisher": "J. Pedreira editor",
"translation": false,
"font": "Corpus Literari Digital de la Càtedra Màrius Torres"
}
```
<h4>Funcions del mòdul corpus</h4>

1. Compilar un Corpus: compila els fitxers de text en un format processable per l'escansor.

```python
compile(raw_files_path, corpus)
```

2. Etiquetar un corpus: analitza prosòdicament un corpus (crida l'escansor).

```python
etiq(corpus)
```

<h4>Resultats del mòdul corpus</h4>
Els resultats dels corpus compilats es desen en format JSON dins la carpeta corpora/nom_del_corpus/sense etiquetar/.

Un cop etiquetats amb l'escansor. Els fitxers del corpus etiquetat es desen en format JSON i CSV i són dipositats dins la carpeta corpora/nom del corpus/etiquetat/.

<h3>🔬 Escansió</h3>
El mòdul d'escansió rep un vers com una cadena de text que fa d’input i en proposa un output com una anàlisi amb una bateria d’atributs propis de l’escansió en un diccionari:

- Escansió representada textualment
- Patró rítmic
- Patró mètric
- Contorn rítmic
- Síl·labes mètriques
- Síl·labes extramètriques
- Booleà d'ajustament a les síl·labes esperades
- Model mètric
    - Tipus de correspondència entre model i material prosòdic (cesura, tall, discontinu o continu)
    - Patró mètric del primer còlon
    - Patró mètric del segon còlon
- Número de mots
- Longitud sil·làbica dels mots
    - Mots al primer còlon
    - Mots al segon còlon
- Longitud mitjana dels mots
- Llicències mètriques


<hr>
<div align="center">
©2026, Pere Garau Borràs
<p></p>
<img src="uib.png" alt="uib" width="200"/>
</div>
