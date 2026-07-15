"""
Mòdul: vers.py

Classe principal:
- Vers: gestiona l'escansió mètrica i l'anàlisi prosòdic d'un vers.

Descripció breu:
Aquest mòdul processa un vers proporcionat a través d'un pipeline spaCy,
construeix objectes Mot per cada token, resol contactes vocàlics, calcula
patrons mètrics i rítmics, aplica regles de prosòdia i exporta resultats
per visualització i serialització.
"""

__author__ = "Pere Garau"
__all__ = ["Vers"]

import re
import time
from typing import Dict, Any, List, Optional
from numpy import mean

import spacy
from colorama import Fore

from AIMeRiC.escansio.modules.mot import Mot
from AIMeRiC.escansio.modules.utils.POStagger import posTagger
from AIMeRiC.escansio.modules.utils.decasillab import identifica_model
from AIMeRiC.escansio.modules.utils.display import anota_vers, escansio_plana, escansio_accentual, scansion_array
from AIMeRiC.escansio.modules.utils.fonetica_sintactica import contactes_vocalics_info, resol_contactes_vocalics
from AIMeRiC.escansio.modules.utils.llicencies import llicencies
from AIMeRiC.escansio.modules.utils.metre import recompte_metric, metre_ajustat, abstract_pattern, \
    maximal_comparison_pattern, patro_metric_jerarquic, extreu_peus, identifica_xocs, identifica_valls
from AIMeRiC.escansio.modules.utils.mot_info import quants_mots, safe_words
from AIMeRiC.escansio.modules.utils.prosodia import accents_prosodics, cim_maxim
from AIMeRiC.escansio.modules.utils.syntax import encavalcament


class Vers:
    """Classe per a la gestió mètrica d'un vers.

    Arguments:
        nlp: objecte spacy carregat
        text: text del vers
        objectiu: longitud objectiu del patró (per exportacions)
        permet_llicencies: si permet aplicar llicències
        minimal: mode mínim (calcula menys informació per agilitar)

    Aquesta implementació manté la mateixa funcionalitat que l'original,
    amb optimitzacions i comprovacions addicionals per evitar errors.
    """

    def __init__(
            self,
            nlp: spacy.Language,
            text: str,
            objectiu: int = 10,
            permet_llicencies: bool = True,
            minimal: bool = False
    ):
        self.objectiu = objectiu
        self.text = text
        self.encavalcament = encavalcament(self.text)
        self._minimal = minimal
        self.sinalefa, self.sineresi, self.dialefa = 0, 0, 0

        # Inicialitzar tots els atributs potencials per evitar AttributeError
        self._init_attributes()

        # Preparació bàsica
        self.__prepara__(nlp)

        # Resoldre contactes vocàlics i determinar ajustament
        resol_contactes_vocalics(self, best_mode='natural')
        self.ajustat = metre_ajustat(self)

        # Processar segons mode
        if minimal:
            self.__process_minimal__()
        else:
            self.__process_full__(permet_llicencies)

    def _init_attributes(self) -> None:
        """Inicialitza tots els atributs per evitar AttributeError."""
        self.colon_1: Optional[str] = None
        self.colon_2: Optional[str] = None
        self.model: Optional[str] = None
        self.correspondencia_model: Optional[str] = None
        self.patro_metric_jerarquic: Optional[str] = None
        self.llicencies: Optional[Any] = None
        self.contactes_vocalics: Optional[Dict] = None
        self.words: List[Mot] = []
        self.nomes_sillabes: List = []

    def _get_safe(self, attr: str, default: Any = None) -> Any:
        """Obté un atribut de forma segura amb valor per defecte."""
        return getattr(self, attr, default)

    def __prepara__(self, nlp: spacy.Language) -> None:
        """Prepara el vers: etiquetatge POS, crear objects Mot i neteja inicial."""
        self.pos = posTagger(nlp, self.text)
        self.words: List[Mot] = [Mot(token, len(self.pos)) for token in self.pos]
        safe_words(self)
        self.original = self.words.copy()
        self.__uneix_mots__()
        self.__patrons__()
        self.__anota__()

    def __uneix_mots__(self) -> None:
        """Unifica totes les síl·labes dels mots en una sola llista."""
        self.nomes_sillabes = [s for word in self.words for s in word.stress]

    def __actualitza_patro_jerarquic__(self) -> None:
        """Actualitza el patró mètric jeràrquic de forma segura."""
        if self.model:
            try:
                self.patro_metric_jerarquic = patro_metric_jerarquic(
                    self.patro_metric, self.model
                )
            except Exception:
                self.patro_metric_jerarquic = None

    def __patrons__(self) -> None:
        """Calcula patrons rítmics i mètrics."""
        self.patro = abstract_pattern(self.words)
        self.patro_ritmic = str(''.join(str(int(x)) for x in self.patro).rstrip('0'))
        self.recompte_sillabes_metriques = recompte_metric(self)
        self.patro_metric = str(maximal_comparison_pattern(self))
        self.__actualitza_patro_jerarquic__()
        self.contorn_ritmic = '-'.join(
            str(i + 1) for i, ch in enumerate(self.patro_metric) if ch == '1'
        )
        self.recompte_sillabes_extrametriques = max(
            0, len(self.patro) - self.recompte_sillabes_metriques
        )
        self.sillables_metriques = self.patro[:self.recompte_sillabes_metriques]
        self.num_toniques = len(re.findall('1', self.patro_metric)) if self.patro_metric else 0
        self.num_atones = len(re.findall('0', self.patro_metric)) if self.patro_metric else 0
        self.densitat_accents = self.num_toniques / self.recompte_sillabes_metriques if self.recompte_sillabes_metriques else 0
        self.accents_secundaris = len(re.findall(r'2', self.patro_ritmic)) / 10 if self.patro_ritmic else 0
        self.index_iambicitat = (sum(1 for i in range(min(len(self.patro_metric), 10))
                                    if self.patro_metric[i] == "0101010101"[i]) / 10) if self.patro_metric else 0

        if self.patro_metric_jerarquic and self.ajustat:
            self.peus = extreu_peus(self.patro_metric_jerarquic)
            if self.peus:
                self.iambes = self.peus.count('01')
                self.troqueus = self.peus.count('10')
                self.anapests = self.peus.count('001')
                self.amfibracs = self.peus.count('010')
                self.dactils = self.peus.count('100')
                self.degenerats = self.peus.count('1')
            xocs_ = identifica_xocs(self.patro_ritmic)
            valls_ = identifica_valls(self.patro_ritmic)
            self.xocs = xocs_[0] if xocs_ else None
            self.valls = valls_[0] if valls_ else None
            self.xocs_pos = xocs_[1] if xocs_ else None
            self.valls_pos = valls_[1] if valls_ else None

    def __anota__(self) -> None:
        """Genera l'etiquetatge del vers."""
        self.anotat = anota_vers(self)
        self.__uneix_mots__()

    def __disposicio__(self) -> None:
        """Genera representacions textuals de l'escansió."""
        self.string = escansio_plana(self)
        self.escansio_array = scansion_array(self)
        self.escansio_text = escansio_accentual(self)

    def __prosodia__(self, subdi: bool = False) -> None:
        """Càlculs prosòdics addicionals."""
        if not self.ajustat:
            return

        cim_maxim(self)
        accents_prosodics(self, subdividit=subdi, debug=False)

        # Actualitzar anotacions
        self.__anota__()
        self.__disposicio__()

        # Recalcular model si necessari
        if not self.model:
            try:
                self.__detecta_model__(debug_index='prosòdia')
            except Exception:
                pass

    def __mot_info__(self) -> None:
        """Nombre de mots i distribució respecte al còlon."""
        self.n_mots = len(self.original)
        self.l_mots = [len(word.stress) for word in self.original]
        self.longitud_mitjana_mots = mean(self.l_mots) if self.l_mots else 0

        qm = quants_mots(self)
        self.mots_colon1 = qm[0] if len(qm) > 0 else 0
        self.mots_colon2 = qm[1] if len(qm) > 1 else 0

    def __contactes_vocalics__(self) -> None:
        """Agrupa informació sobre contactes vocàlics."""
        result = contactes_vocalics_info(self)

        if isinstance(result, dict):
            self.contactes_vocalics = result if any(result.values()) else None
        else:
            self.contactes_vocalics = result if result else None

    def __detecta_model__(self, debug_index=None) -> None:
        """Detecta la model del vers."""
        # Recompute model info (do not early-return; revalidate on each call)
        model_info = identifica_model(self)

        if isinstance(model_info, (tuple, list)) and len(model_info) >= 2:
            self.model = model_info[0]
            self.correspondencia_model = model_info[1]
        elif isinstance(model_info, str):
            self.model = model_info
            self.correspondencia_model = None
        else:
            self.model = None
            self.correspondencia_model = None

        # Ensure patro_metric is a string and safe to iterate
        try:
            self.patro_metric = str(maximal_comparison_pattern(self))
        except Exception:
            self.patro_metric = ''

        if not self.patro_metric_jerarquic:
            self.__actualitza_patro_jerarquic__()

        # Update colons based on final patro_metric
        self.__actualitza_colons__()

        # Safely build contorn_ritmic only when patro_metric is valid
        if self.patro_metric:
            try:
                self.contorn_ritmic = '-'.join(
                    str(i + 1) for i, ch in enumerate(self.patro_metric) if ch == '1'
                )
            except Exception:
                self.contorn_ritmic = None
        else:
            self.contorn_ritmic = None

        # Apply local model rules after colons/contorn have been computed
        #self.__model_local__()



    def __model_local__(self) -> None:
        """Aplica regles locals de model basades en contorn_ritmic."""
        if self.model:
            if self.model in ['3+7', '7+3']:
                self.model = 'S/M'
                if self.correspondencia_model == 'tall':
                    self.correspondencia_model = 'discontinu'
            elif self.model == '5+5':
                if self.correspondencia_model != 'tall':
                    self.model = 'S/M'

    def __actualitza_colons__(self) -> None:
        """Actualitza els còlons del vers basats en model."""
        if self.model and '+' in self.model:
            pos = int(self.model.split('+')[0])
            self.colon_1 = self.patro_metric[:pos]
            self.colon_2 = self.patro_metric[pos:]
        else:
            self.colon_1 = None
            self.colon_2 = None

    def __verifica_model__(self) -> None:
        """Verifica que la model sigui vàlida al patró mètric."""
        if not self.model or '+' not in self.model:
            return

        pos = int(self.model.split('+')[0]) - 1

        if pos >= len(self.patro_metric) or self.patro_metric[pos] != '1':
            self.model = None
            self.correspondencia_model = None
            self.__detecta_model__(debug_index='verifica')

    def __reset_cim_maxim__(self) -> None:
        """Elimina el cim màxim existent."""
        for word in self.words:
            for syllable in word.stress:
                try:
                    if getattr(syllable, 'pes', None) == 5.0:
                        syllable.pes = 4.0
                except Exception:
                    continue
        self.__uneix_mots__()

    def __process_minimal__(self) -> None:
        """Processa el vers en mode mínim."""
        self.__disposicio__()
        self.__patrons__()
        self.__anota__()

    def __process_full__(self, permet_llicencies: bool) -> None:
        """Processa el vers en mode complet."""
        if not self.ajustat:
            self.llicencies = llicencies(self, permet_llicencies, doc=self.pos)
            self.sinalefa = self.llicencies.count('sinalefa') if self.llicencies else 0
            self.sineresi = self.llicencies.count('sinèresi') if self.llicencies else 0
            self.dialefa = self.llicencies.count('dialefa') if self.llicencies else 0

            return

        # Processar components en ordre
        self.__disposicio__()
        self.__detecta_model__(debug_index='proses')
        self.__prosodia__(subdi=True)
        self.__patrons__()
        self.__actualitza_colons__()
        self.__anota__()
        self.__mot_info__()
        self.__contactes_vocalics__()
        #self.__verifica_model__()
        self.__ensure_tall_spacing__()
        self.__info_contactes_vocalics__()
        self.__info_gramatical__()

    def __ensure_tall_spacing__(self) -> None:
        """Assegura que la representació del patró té espai després del tall."""
        if self.model is None:
            self.__detecta_model__(debug_index='ensure_tall_spacing')
            if self.model is None:
                self.patro_metric_jerarquic = self.patro_metric

    def __info_contactes_vocalics__(self):
        self.tipus_cv = []
        self.tonicitat_cv = []
        self.frontera_cv = []
        self.vocals_cv = []
        self.index_cv = []
        if self.contactes_vocalics:
            for contacte_id, info in self.contactes_vocalics.items():
                self.tipus_cv.append(info['tipus'])
                self.tonicitat_cv.append(info['tonicitat'])
                self.frontera_cv.append(info['frontera'])
                self.vocals_cv.append(info['vocals'])
                self.index_cv.append(info['s_index'])

    def __info_gramatical__(self):
        if self.words:
            self.cat_gramaticals = [word.pos_ for word in self.words]

    def __actualitza__(self) -> None:
        """Actualitza l'estat del vers després d'aplicar llicències."""
        safe_words(self)
        self.__uneix_mots__()
        self.__patrons__()
        self.__reset_cim_maxim__()
        self.ajustat = metre_ajustat(self)
        self.__detecta_model__(debug_index='actualitza')
        self.__disposicio__()

        if self.ajustat:
            self.__prosodia__(subdi=True)
            if not self.model:
                self.__detecta_model__(debug_index='actualitza2')

        self.__patrons__()
        self.__actualitza_colons__()
        self.__anota__()
        self.__mot_info__()
        self.__contactes_vocalics__()
        self.__ensure_tall_spacing__()
        #self.__verifica_model__()
        self.__info_contactes_vocalics__()
        self.__info_gramatical__()

    def mostra(self) -> None:
        """Mostra informació del vers amb colors per consola."""
        self._print_escansio()
        self._print_patrons()
        self._print_metriques()
        self._print_model()
        self._print_mots()
        self._print_llicencies()

    def _print_escansio(self) -> None:
        """Imprimeix l'escansió."""
        escansio = self._get_safe('escansio_text')
        if escansio:
            print(Fore.CYAN, f"\t➥", Fore.RESET, f"Escansió: {escansio}")

    def _print_patrons(self) -> None:
        """Imprimeix els patrons."""
        patro_rit = self._get_safe('patro_ritmic')
        if patro_rit:
            print(Fore.CYAN, f"\t➥", Fore.RESET, f"Patró rítmic:",
                  self._color_ritmic(patro_rit))

        patro_met = self._get_safe('patro_metric')
        if patro_met:
            print(Fore.CYAN, f"\t➥", Fore.RESET, f"Patró mètric:",
                  self._color_metric(patro_met))

        patro_jer = self._get_safe('patro_metric_jerarquic')
        if patro_jer:
             print(Fore.CYAN, f"\t➥", Fore.RESET, f"Patró mètric jeràrquic:", patro_jer)

    def _print_metriques(self) -> None:
        """Imprimeix les mètriques."""
        contorn_ritmic = self._get_safe('contorn_ritmic')
        if contorn_ritmic:
            print(Fore.CYAN, f"\t➥", Fore.RESET, f"contorn_ritmic:",
                  Fore.CYAN, contorn_ritmic, Fore.RESET)

        r_met = self._get_safe('recompte_sillabes_metriques')
        if r_met is not None:
            print(Fore.CYAN, f"\t➥", Fore.RESET, f"Síl·labes mètriques:",
                  Fore.CYAN, r_met, Fore.RESET)

        r_ext = self._get_safe('recompte_sillabes_extrametriques')
        if r_ext is not None:
            print(Fore.CYAN, f"\t➥", Fore.RESET, f"Síl·labes extramètriques:",
                  Fore.CYAN, r_ext, Fore.RESET)

        ajustat = self._get_safe('ajustat')
        print(Fore.CYAN, f"\t➥", Fore.RESET, f"Ajustat:", ajustat)

    def _print_model(self) -> None:
        """Imprimeix informació de model."""
        model = self._get_safe('model', 'N/I')
        tipus = self._get_safe('correspondencia_model', 'N/A')
        colon_1 = self._get_safe('colon_1', 'N/A')
        colon_2 = self._get_safe('colon_2', 'N/A')

        print(Fore.CYAN, f"\t➥", Fore.RESET, f"model:", model)
        print(Fore.CYAN, f"\t\t➥", Fore.RESET, f"Correspondència amb el model:", tipus)
        print(Fore.CYAN, f"\t\t➥", Fore.RESET, f"Còlon 1:", colon_1)
        print(Fore.CYAN, f"\t\t➥", Fore.RESET, f"Còlon 2:", colon_2)

    def _print_mots(self) -> None:
        """Imprimeix informació de mots."""
        n_mots = self._get_safe('n_mots')
        l_mots = self._get_safe('l_mots')
        mots_c1 = self._get_safe('mots_colon1')
        mots_c2 = self._get_safe('mots_colon2')

        print(Fore.CYAN, f"\t➥", Fore.RESET, f"Número de mots:", n_mots)
        print(Fore.CYAN, f"\t➥", Fore.RESET, f"Longitud sil·làbica dels mots:", l_mots)
        print(Fore.CYAN, f"\t\t➥", Fore.RESET, f"Mots al primer colon:", mots_c1)
        print(Fore.CYAN, f"\t\t➥", Fore.RESET, f"Mots al segon colon:", mots_c2)

    def _print_llicencies(self) -> None:
        """Imprimeix informació de llicències."""
        llicencies = self._get_safe('llicencies')
        llicencies_text = llicencies if llicencies is not None else 'Cap'
        print(Fore.CYAN, f"\t➥", Fore.RESET, f"Llicències:", llicencies_text)

    @staticmethod
    def _color_metric(pattern: str) -> str:
        """Afegeix color al patró mètric."""
        return ''.join(
            Fore.CYAN + ch + Fore.RESET if ch == '1' else ch
            for ch in str(pattern)
        )

    @staticmethod
    def _color_ritmic(pattern: str) -> str:
        """Afegeix color al patró rítmic."""
        out = []
        for ch in str(pattern):
            try:
                val = int(ch)
                if val == 2:
                    out.append(Fore.CYAN + ch + Fore.RESET)
                elif val > 2:
                    out.append(Fore.RED + ch + Fore.RESET)
                elif val == 1:
                    out.append(Fore.YELLOW + ch + Fore.RESET)
                else:
                    out.append(ch)
            except ValueError:
                out.append(ch)
        return ''.join(out)

    def mostra_minimal(self) -> None:
        """Mostra la informació mínima del vers en format compacte."""
        esc = self._get_safe('escansio_text')
        if esc:
            print(Fore.CYAN, f"\t➥", Fore.RESET, f"Escansió: {esc}")

        patro_rit = self._get_safe('patro_ritmic')
        if patro_rit:
            print(Fore.CYAN, f"\t➥", Fore.RESET, f"Patró rítmic:",
                  self._color_metric(patro_rit))

        patro_met = self._get_safe('patro_metric')
        if patro_met:
            print(Fore.CYAN, f"\t➥", Fore.RESET, f"Patró mètric:",
                  self._color_metric(patro_met))

        r_met = self._get_safe('recompte_sillabes_metriques')
        if r_met is not None:
            print(Fore.CYAN, f"\t➥", Fore.RESET, f"Síl·labes mètriques:",
                  Fore.CYAN, r_met, Fore.RESET)

        r_ext = self._get_safe('recompte_sillabes_extrametriques')
        if r_ext is not None:
            print(Fore.CYAN, f"\t➥", Fore.RESET, f"Síl·labes extramètriques:",
                  Fore.CYAN, r_ext, Fore.RESET)

        n_w = self._get_safe('n_mots')
        if n_w is not None:
            print(Fore.CYAN, f"\t➥", Fore.RESET, f"Número de mots:", n_w)

    @property
    def desa(self) -> Dict[str, Any]:
        """Retorna un diccionari amb la informació del vers."""
        return {
            self.text: {
                "string": self._get_safe('string'),
                "escansió": self._get_safe('escansio_text'),
                "patró rítmic": self._get_safe('patro_ritmic'),
                "patró mètric": self._get_safe('patro_metric'),
                "contorn_ritmic": self._get_safe('contorn_ritmic'),
                "síl·labes mètriques": self._get_safe('recompte_sillabes_metriques'),
                "síl·labes extramètriques": self._get_safe('recompte_sillabes_extrametriques'),
                "posició tall": self._get_safe('posicio_tall'),
                "model": self._get_safe('model'),
                "correspondència model": self._get_safe('correspondencia_model'),
                "còlon 1": self._get_safe('colon_1'),
                "còlon 2": self._get_safe('colon_2'),
                "llicències": self._get_safe('llicencies'),
                "mots": self._get_safe('n_mots'),
                "l_mots": self._get_safe('l_mots'),
                "mots al còlon 1": self._get_safe('mots_colon1'),
                "mots al còlon 2": self._get_safe('mots_colon2'),
                "cv_info": self._get_safe('contactes_vocalics'),
                "encavalcament": self._get_safe('encavalcament'),
                "etiquetatge": self._get_safe('anotat')
            }
        }

    def to_csv(self) -> List[str]:
        """Retorna una llista amb la informació del vers per a guardar en CSV."""
        patro_local = self._get_safe('patro', [])

        # Preparar columna de patró
        if len(patro_local) < self.objectiu:
            sc_col = patro_local + [0] * (self.objectiu - len(patro_local))
        else:
            sc_col = patro_local[:self.objectiu]

        # Convertir a cadena amb prefix d'apòstrof en una sola passada
        sc_col = ["'" + str(x) for x in sc_col]

        # Compilar resultats
        result = [
            self.text,  # text_vers
            self._get_safe('escansio_text'),  # escansio
            *sc_col,  # scansion_cols
            self._get_safe('contorn_ritmic'),  # contorn_ritmic
            "'" + str(self._get_safe('patro_metric')),  # patro_lineal
            "'" + str(self._get_safe('patro_ritmic')),  # patro_ritmic
            "'" + str(self._get_safe('patro_metric_jerarquic')),  # patro_metric
            self._get_safe('densitat_accents', default=0),  # densitat_accents
            self._get_safe('accents_secundaris', default=0),
            self._get_safe('index_iambicitat', default=0),
            self._get_safe('model'),  # model
            self._get_safe('correspondencia_model'),  # correspondencia_model
            "'" + str(self._get_safe('colon_1')),  # colon_1
            "'" + str(self._get_safe('colon_2')),  # colon_2
            self._get_safe('iambes', default=0),
            self._get_safe('troqueus', default=0),
            self._get_safe('anapests', default=0),
            self._get_safe('amfibracs', default=0),
            self._get_safe('dactils', default=0),
            self._get_safe('degenerats', default=0),
            self._get_safe('xocs', default=0),
            self._get_safe('xocs_pos'),
            self._get_safe('valls', default=0),
            self._get_safe('valls_pos'),
            self._get_safe('recompte_sillabes_metriques', default=0),  # sil_metriques
            self._get_safe('recompte_sillabes_extrametriques', default=0),  # sil_extrametriques
            #self._get_safe('llicencies'),  # llicencies
            self._get_safe('sinalefa', default=0),
            self._get_safe('sineresi', default=0),
            self._get_safe('dialefa', default=0),
            self._get_safe('n_mots', default=0),  # mots
            self._get_safe('l_mots'),  # longitud_mots
            self._get_safe('longitud_mitjana_mots', default=0),
            self._get_safe('mots_colon1', default=0),  # mots_colon_1
            self._get_safe('mots_colon2', default=0),  # mots_colon_2
            self._get_safe('tipus_cv', default=[]),
            self._get_safe('tonicitat_cv', default=[]),
            self._get_safe('frontera_cv', default=[]),
            self._get_safe('vocals_cv', default=[]),
            self._get_safe('index_cv', default=[]),
            self._get_safe('cat_gramaticals', default=[]),
            self._get_safe('encavalcament', default=False),  # encavalcament
        ]

        return [str(x) if x is not None else '' for x in result]

    def save_minimal(self) -> Dict[str, Any]:
        """Retorna un diccionari amb informació essencial del vers."""
        return {
            self.text: {
                "string": self._get_safe('string'),
                "string_stress": self._get_safe('escansio_text'),
                "pattern": str(self._get_safe('patro')),
                "contorn_ritmic": str(self._get_safe('contorn_ritmic')),
                "sillabes_metriques": self._get_safe('sillables_metriques'),
                "sillabes_extrametriques": self._get_safe('recompte_sillabes_extrametriques'),
                "n_words": self._get_safe('n_mots'),
                "l_words": self._get_safe('l_mots'),
                "comparative_pattern": str(self._get_safe('patro_ritmic')),
                "array": [
                    [syllable.save_metadata() for syllable in mot.stress]
                    for mot in self._get_safe('words', [])
                ]
            }
        }

    def actualitza_w_index(self) -> None:
        """Actualitza els w_index de les paraules."""
        for i, word in enumerate(self.words):
            word.w_index = i

    def actualitza_pesos(self) -> None:
        """Actualitza el valor de pes de les síl·labes."""
        for word in self.words:
            for syllable in word.stress:
                for s in self.nomes_sillabes:
                    if syllable.text == s.text:
                        syllable.pes = s.pes
                        break

    def __repr__(self) -> str:
        return f"<Vers text={self.text!r} n_words={len(self.words)}>"


# Exemple d'ús
if __name__ == "__main__":
    start = time.time()
    sentence = "el sant de pedra sobre el portal"
    nlp = spacy.load("ca_core_news_md", disable=["ner"])
    vers = Vers(nlp, sentence, 10, permet_llicencies=True)
    vers.mostra()
    print([[(s.text, s.pes) for s in word.stress] for word in vers.words])
    print(vers.desa)
