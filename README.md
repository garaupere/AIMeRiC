# AIMeRiC: Anàlisi Informatitzada del Metre i el Ritme del Català

Aquest repositori conté l'aplicatiu **AIMeRiC**, desenvolupat per a l'escansió automatitzada de textos en català, especialment poesia. L'aplicatiu forma part de la tesi doctoral "La variabilitat rítmica del decasíl·lab català" de Pere Garau Borràs (UIB).

## Requeriments

- Python 3.x
- Llibreries Python: `colorama`, `spacy`, `cfonts`
- Model de Spacy per a català: `ca_core_news_md`

## Instal·lació

1. Clonar el repositori.
2. Instal·lar les dependències:

```bash
pip install -r requirements.txt
```

3. Descarregar el model de Spacy:

```bash
python -m spacy download ca_core_news_md
```

## Ús

### Estructura del Corpus

El corpus ha de seguir aquesta estructura:

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

### Funcionalitats Principals

#### Compilar un Corpus

Compila els fitxers de text en un format processable:

```python
compile(raw_files_path, corpus)
```

#### Etiquetar un Corpus

Aplica etiquetes lingüístiques al corpus compilat:

```python
etiq(corpus)
```

### Resultats

Els resultats es guarden en format JSON dins la carpeta `corpora`:

```plaintext
corpora/
└── corpus/
    └── sense etiquetar/
        └── json/
            ├── corpus_autor_1.json
            └── corpus_autor_2.json
```

## Llicència

Aquest projecte està llicenciat sota els termes del Copyright ©2025, Pere Garau Borràs.

## Estructura del programa

Internament, aquest programa s'estructura en dos paquets:

- `corpus` és el paquet que conté el corpus, les eines de compilació, la interfície d'etiquetatge i explotació del corpus de la tesi. :warning: Aquest paquet no és funcional sense el paquet `escansio`.
- `escansio` és el paquet que conté el nucli de l'escansor, l'aplicació encarregada d'analitzar mètricament els versos. Aquest paquet permet l'ús de l'escansor de manera independent de l'aplicació de corpus.

---

#### **©2025, Pere Garau Borràs**
![](uib.png)