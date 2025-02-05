Aquest repositori conté l'aplicatiu confeccionat per a la tesi <i>La variabilitat rítmica del decasíl·lab català</i> de Pere Garau Borràs (ORCID: <a href="https://orcid.org/0000-0002-0222-0096">0000-0002-022-0096</a>) a la Universitat de les Illes Balears (UIB) (ROR: <a href="https://ror.org/03e10x626">o3e10x626</a>).
Les eines aquí aplegades permeten la compilació de corpus de poesia etiquetats mètricament a través d'una eina que n'automatitza l'escansió.

Aquest repositori s'estructura en tres paquets:

- `corpus` és el paquet que conté el corpus, les eines de compilació, la interfície d'etiquetatge i explotació del corpus de la tesi. :warning: Aquest paquet no és funcional sense el paquet `escansor_scr`.

- `escansor_scr` és el paquet que conté el nucli de l'escansor, l'aplicació encarregada d'analitzar mètricament els versos. Aquest paquet permet l'ús de l'escansor de manera independent de la resta de l'aplicatiu. A través del paquet `corpus` l'escansor és executat automàticament per al conjunt de versos que componen el corpus.

- :skull: `data` és el paquet encarregat de l'explotació estadística i visualització de dades del corpus. La seva funcionalitat és complementària a la de `corpus` i `escansor_scr`. :warning: Aquest paquet és obsolet i aviat serà suprimit.

#### **© 2022-2025, Pere Garau Borràs**
<img src="https://logo.uib.cat/digitalAssets/338/338690_logo-uib-horizontal300.png" alt="UIB" width="30%">