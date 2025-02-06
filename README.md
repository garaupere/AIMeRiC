Aquest repositori conté l'aplicatiu confeccionat per a la tesi <i>La variabilitat rítmica del decasíl·lab català</i> de Pere Garau Borràs (ORCID: <a href="https://orcid.org/0000-0002-0222-0096">0000-0002-022-0096</a>) a la Universitat de les Illes Balears (UIB) (ROR: <a href="https://ror.org/03e10x626">o3e10x626</a>).
Les eines aquí aplegades permeten la compilació de corpus de poesia etiquetats mètricament a través d'una eina que n'automatitza l'escansió.

Per accedir a l'aplicatiu, executau el fitxer `escancat.py`. Aquesta interfície desplega un menú amb les següents opcions:
> #### 1. Compilar un corpus 
> Aquesta funció permet compilar un corpus a partir d'un conjunt de fitxers de text pla (`.txt`) que segueixen una estructura determinada. L'estructura dels fitxers de text pla ha de ser la següent:
```
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
> Pel que fa a l'estructura dels fitxers `.info`, han de presentar aquesta estructura:
> > #### autor.info
>> ````
>> {
>>    "author_id": "Jacint Verdaguer", # Nom i primer llinatge
>>    "name": "Verdaguer i Santaló, Jacint",
>>    "gender": 0,  # H: 0, D: 1, A: 2
>>    "born_date": 1845,
>>    "death_date": 1902,
>>    "city": "Folgueroles",
>>    "dialect": "central",
>>    "viaf": "9841818",    # Identificador VIAF.
>>    "wiki_id": "Q379290" # Identificador de WikiData.
>> }
>> ```` 
>> #### book.info
> > ```
> > {
>> "title": "L'Atlàntida",
>> "year": 1877,            # Any de la primera publicació.
>> "publisher": "Edicions 62"   # Editor de l'edició usada.
> > }
>> ```
>> Pel que fa al format dels fitxers `.txt`, cal que incloguin els versos separats per un salt de línia `\n`.\
> El resultat del corpus compilat i sense etiquetar és un fitxer `.json`, que es desa dins una carpeta anomenada `corpora`. L'estuctura del corpus compilat és sempre:
> ````
> corpora
> └── corpus
>     └── sense etiquetat
>         └── json
>             ├── corpus_autor_1.json
>             └── corpus_autor_2.json
> ````
> 
>

> #### 2. Etiquetar un corpus
> Aquesta funció permet executar l'etiquetatge mètric del corpus, un cop ja ha estat compilat. L'etiquetatge actua sobre el corpus compilat (`.json`). Un cop acabi l'etiquetatge, el resultat és visible en la carpeta corpora, que pren aquesta estructura:
> ````
> corpora
> └── corpus
>     ├── sense etiquetat
>     │   └── json
>     │       ├── corpus_autor_1.json
>     │       └── corpus_autor_2.json
>     └── etiquetat
>             ├── csv
>             │    ├── corpus_autor_1.csv
>             │    └── corpus_autor_2.csv
>             ├── json
>             │    ├── corpus_autor_1.json
>             │    └── corpus_autor_2.json
>             └── log
>                  ├── corpus_autor_1.log
>                  └── corpus_autor_2.log
> ````
> La carpeta `csv` conté el corpus en format de fitxer delimitat per comes, exportable a qualsevol programa d'anàlisi de dades.
> La carpeta `json` conté el corpus en format json, que és el format que nativament maneja l'aplicació. La carpeta `log` conté en un fitxer de text pla els vesos que no compleixen amb l'objectiu de l'etiquetatge i que, per tant, no formen part del corpus resultant.
> 

> #### 3. Exploració estadística del corpus
> Amb aquest mòdul s'implementa una exploració estadística de les dades d'etiquetatge del corpus. La funció accedeix al corpus etiquetat i en processa factors com la mitjana de tonicitat per síl·laba, la distància entre el contorn rítmic i el model binari (iàmbic), la filiació entre autors a través de dendrogrames, l'extrametricitat, etc. El resultat d'aquesta explotació es recull en la carpeta `etiquetat`, en què s'inclouen dues carpetes més, `svg` per als gràfics resultants de l'exploració i `xlsx` per als documents de dades d'Excel. Dins la carpeta `svg` també s'inclou una carpeta per a cada autor amb els gràfics individuals del contorn rítmic i la distància respecte del model iàmbic.
> ````
> ...
>>     └── etiquetat
>             ├── csv
>             ├── json
>             ├── log
>             ├── svg
>             │    ├── contorn_rítmic.svg
>             │    ├── distància_iambe.svg
>             │    ├── ...
>             │    └── autors
>             │         └── autor_1
>             │               ├── contorn_rítmic.svg
>             │               └── distància_iambe.svg
>             └── xlsx
>                  ├── contorn_rítmic.xlsx
>                  ├── ...
>                  └── dendrograma.xlsx
> ````

> #### 4. Validar les dades __test
> El mòdul de validació de dades compara l'etiquetatge automàtic de l'aplicatiu amb l'etiquetatge manual. Opera a través de l'obra de testeig que és _Sol, i de dol_ de J. V. Foix. En el codi d'`escancat` s'emmagatzema l'etiquetatge manual de l'obra, que és comparada amb el resultat de l'escansió automàtica. Aquesta funció genera un índex de fiabilitat (sobre 100) de l'etiquetatge i en desa una sèrie de gràfics dins la carpeta `corpus/validacio`. Actualment, l'índex de fiabilitat del programa és del **97,56%**.

> #### 6. Analitzar un vers
> Aquesta funció permet analitzar un vers introduit per l'usuari, per defecte el mode d'anàlisi és el del decasíl·lab. Els resultats es mostren en pantalla i segueixen aquest esquema:
> ````
>>	ajustat: True
>>	text: Veles e vents han mos desigs complir
>>	string: ve.les#e#vents#han#mos#de.sigs#com.plir
>>	string_stress: VE.les#e#VENTS#han#MOS#de.SIGS#com.PLIR
>>	pos: [('Veles', 'PROPN', 'nsubj'), ('e', 'CCONJ', 'det'), ('vents', 'NOUN', 'appos'), ('han', 'AUX', 'aux'), ('mos', 'ADP', 'aux'), ('desigs', 'NOUN', 'ROOT'), ('complir', 'VERB', 'xcomp')]
>>	annotated: [[('ve', '4'), ('les', '0')], [('e', '0')], [('vents', '5')], [('han', '0')], [('mos', '3')], [('de', '0'), ('sigs', '4')], [('com', '0'), ('plir', '5')]]
>>	pattern: [4, 0, 0, 5, 0, 3, 0, 4, 0, 5]
>>	comparative_pattern: 4004030404
>>	maxpattern: SWWSWSWSWS
>>	n_words: 7
>>	recompte_sillabes_metriques: 10
>>	posicio_tall: 4
>>	subdivision: 4+6
>>	recompte_sillabes_extrametriques: 0
>>	llicencies: None
>>	_clash: 0
>>	_lapse: 0
>>	_ws_hl: 0
>>	_non_initial: 1
>>	_symetry: 1
>>	h1_words: 3
>>	h2_words: 4
>>	cv_info: {'hiats_a_fm': [], 'hiats_a_m': [], 'hiats_t_fm': [], 'hiats_t_m': [], 'diftong_a_fm': [], 'diftong_a_m': [], 'diftong_t_fm': [], 'diftong_t_m': [], 'triftong_a_fm': [], 'triftong_a_m': [], 'triftong_t_fm': [], 'triftong_t_m': []}
>>	metronome: Sw.w.S.w.S.wS.wS.|
> ````

> #### 7. Sortir
> Acaba amb l'execució del programa.

--- 
> Internament, aquest repositori s'estructura en dos paquets:
>> - `corpus` és el paquet que conté el corpus, les eines de compilació, la interfície d'etiquetatge i explotació del corpus de la tesi. :warning: Aquest paquet no és funcional sense el paquet `escansor_scr`.
>>- `escansor_scr` és el paquet que conté el nucli de l'escansor, l'aplicació encarregada d'analitzar mètricament els versos. Aquest paquet permet l'ús de l'escansor de manera independent de la resta de l'aplicatiu. A través del paquet `corpus` l'escansor és executat automàticament per al conjunt de versos que componen el corpus.
>> <!-- - :skull: `data` és el paquet encarregat de l'explotació estadística i visualització de dades del corpus. La seva funcionalitat és complementària a la de `corpus` i `escansor_scr`. :warning: Aquest paquet és obsolet i aviat serà suprimit. -->

> #### **© 2022-2025, Pere Garau Borràs**
> <img src="https://logo.uib.cat/digitalAssets/338/338690_logo-uib-horizontal300.png" alt="UIB" width="30%">