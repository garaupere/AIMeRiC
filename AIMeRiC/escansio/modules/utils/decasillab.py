"""
Resum
Aquest mòdul gestiona particularitats mètriques del decasíl·lab en el procés d'escansió: detecta i aplica el `tall`, calcula la model del vers i inclou una funció en desenvolupament per la cesura femenina.

## Dependències
- Mòduls interns:
  - `AIMeRiC.escansio.modules.utils.fonetica_sintactica.split_syllable`
  - `AIMeRiC.escansio.modules.utils.tools.seguent`
- Llibreria estàndard: `re`

## Propòsit
Proporcionar utilitats per:
- identificar la posició del tall en versos decasíl·labs,
- marcar la síl·laba de tall amb pes màxim (5.0),
- obtenir la model en còlons (`5+5`, etc.),
- gestionar casos especials de cesura femenina (funció en desenvolupament).
"""

import re

from .fonetica_sintactica import split_syllable
from .tools import seguent


def troba_tall_posible(self, tall, detect_nonBest: bool = False) -> str:
    """
    Avalua si una posició podria ser un tall. NO modifica res!
    Retorna 'best' si és òptim, 'discontinu' si és alternatiu, 'invalid' si no serveix.
    """
    # Si ja ha estat assignat pes de tall, no és vàlid
    if self.nomes_sillabes[tall].pes == 5.0:
        return 'invalid'

    word_at_tall = _get_word_at_position(self, tall)

    # -- NOVETAT: La síl·laba no pot ser tall si NO és l'última de la paraula --
    es_ultima_de_mot = False
    for paraula in self.words:
        if paraula.stress and paraula.stress[-1] == self.nomes_sillabes[tall] and self.nomes_sillabes[
            tall].fusionada is False and paraula.has_PRONe is False and tall != 10:
            es_ultima_de_mot = True
            break
    if not es_ultima_de_mot:
        if self.nomes_sillabes[tall].pes > 2.0:
            return 'continu'
        return 'kkk'
    # -------------------------------------------------
    if self.nomes_sillabes[tall].pes > 2.0:
        if not word_at_tall.has_PRONe:
            if detect_nonBest:
                if 4 > self.nomes_sillabes[tall].pes > 2.0:
                    return 'discontinu'
            return 'best'
    return 'invalid'


def aplica_tall(self, tall):
    """
    Aplica efectivament el tall (pes=5.0, marques) a la posició indicada.
    Retorna True si s'ha aplicat, False si no s'han complert les condicions.
    """
    word_at_tall = _get_word_at_position(self, tall)

    # Comprovacions de seguretat: la síl·laba ha de ser l'última de la paraula,
    # no estar fusionada i la paraula no haver de pronom enclític.
    if not word_at_tall:
        return False

    syl = self.nomes_sillabes[tall]
    if not getattr(syl, 'fusionada', False) and word_at_tall.stress and word_at_tall.stress[-1] == syl and not getattr(
            word_at_tall, 'has_PRONe', False):
        word_at_tall.stress[-1].pes = 5.0
        # actualitzem anotacions i patró
        try:
            self.anotat[self.words.index(word_at_tall)] = word_at_tall.stress
        except Exception:
            pass
        syl.pes = 5.0
        try:
            self.patro[tall] = 5
        except Exception:
            # patro podria ser més curt; ignorem si no existeix
            pass
        word_at_tall.paraula_tall = True
        # assegurem la coherència en la llista
        try:
            self.words[self.words.index(word_at_tall)] = word_at_tall
        except Exception:
            pass

        # Important: recordem la posició del tall (1-based)
        try:
            self.posicio_tall = int(tall) + 1
        except Exception:
            self.posicio_tall = tall

        return True

    return False


def tall(self) -> None | int | tuple[int, str]:
    """Aplica el tall mètric segons criteris prioritaris, evitant assignació prematura."""
    pos, result = None, None
    if self.recompte_sillabes_metriques != 10:
        return None

    talls = [3, 5, 4]  # Preferències de talls

    # === PRIMERA PASSADA: 'best' ===
    for tall_actual in talls:
        result = troba_tall_posible(self, tall_actual, True)
        if result == 'best':
            aplica_tall(self, tall_actual)
            # assegurem la coherència i retornem posició 1-based
            try:
                self.posicio_tall = int(tall_actual) + 1
            except Exception:
                pass
            return tall_actual + 1

    # === SEGONA PASSADA: 'discontinu'/alternatius ===
    for tall_actual in talls:
        result = troba_tall_posible(self, tall_actual, False)
        if result in {'discontinu', 'continu'}:
            pos = tall_actual + 1
            word_at_tall = _get_word_at_position(self, tall_actual)
            next_word = _get_next_word_at_position(self, tall_actual)
            if word_at_tall and next_word:
                if (word_at_tall.pos_ in ["NOUN", "VERB", "PRON", "ADJ", "PROPN"] and
                        next_word.pos_ in ["VERB"]):
                    aplica_tall(self, tall_actual)
                    self.posicio_tall = pos
                    return pos, result
                elif next_word.pos_ in ["NOUN", "VERB", "ADJ", "ADV", "PROPN"]:
                    continue
                else:
                    aplica_tall(self, tall_actual)
                    self.posicio_tall = pos
                    return pos, result
            else:
                aplica_tall(self, tall_actual)
                self.posicio_tall = pos
                return pos, result
    return pos, result  # No s'ha trobat tall vàlid


def identifica_model(self):
    """Identifica el model subjacent al decasíl·lab (4+6, 6+4 o 5+5)"""
    if self.recompte_sillabes_metriques == 10 and self.model is None:
        subdpos = [3, 5, 4]  # Preferències de modelns

        # Per a les síl·labes del vers, obtenim els pesos de les subdpos
        candidats = []
        for pos in subdpos:
            #print('Evaluant posició de model:', pos, f"amb la síl·laba corresponent:", self.nomes_sillabes[pos].text if pos < len(self.nomes_sillabes) else None, "pes: ", self.nomes_sillabes[pos].pes if pos < len(self.nomes_sillabes) else None)
            if pos == 3 or pos == 5:
                if self.nomes_sillabes[pos].pes is not None and self.nomes_sillabes[pos].pes == 3:
                    self.nomes_sillabes[pos].pes = 3.75
            elif pos == 4 and len(candidats) > 0:
                if 3 in [c[0] for c in candidats]:  # Si ja hem considerat el tall a la posició 4, no penalitza
                    if self.nomes_sillabes[pos].pes is not None and self.nomes_sillabes[pos].pes > 2:
                        self.nomes_sillabes[pos].pes -= 0.50
                        self.nomes_sillabes[pos].flag = 'penalitzat_per_tall'
            candidats.append((pos, self.nomes_sillabes[pos].pes if pos < len(self.nomes_sillabes) else None))
        # ordena els candidats per pes (descendent) i després per posició (segons la preferència). Elimina els candidats amb pes None o <= 2.0
        candidats_valids = [(pos, pes) for pos, pes in candidats if pes is not None and pes >= 2]
        candidats_valids.sort(
            key=lambda x: (-x[1], subdpos.index(x[0])))  # Ordena per pes descendent i després per preferència de posició
        #print('>> Candidats de model ordenats per pes i preferència:', candidats_valids)
        # Defineix el tipus de model.
        for pos, pes in candidats_valids:
            # si el candidat és la darrera síl·laba del mot i el mot no té PRONe, ni és fusionada
            word_at_pos = _get_word_at_position(self, pos)
            #print('\t> Candidat a model:', pos, 'Pes:', pes, 'Paraula:', word_at_pos.text if word_at_pos else None)
            if word_at_pos and word_at_pos.stress and word_at_pos.stress[-1] == self.nomes_sillabes[pos] and not getattr(
                    word_at_pos, 'has_PRONe', False) and not getattr(self.nomes_sillabes[pos], 'fusionada', False):
                #print('\t\t> És la darrera síl·laba del mot i el mot no té PRONe ni és fusionada')

                if self.nomes_sillabes[pos].pes >= 4 or (self.nomes_sillabes[pos].pes >= 3 and pos==3) or (pos == 4 and self.nomes_sillabes[pos].pes == 3.5):  # Si el pes és un accent lèxic, considera que és un tall
                    self.nomes_sillabes[pos].pes = 5.0  # Assegura que el pes de la síl·laba de tall és 5.0
                    #print('\t\t> Pes de la síl·laba de tall assegurat a 5.0')
                    if self.nomes_sillabes[pos + 1].flag and self.nomes_sillabes[pos + 1].pes is not None and self.nomes_sillabes[pos + 1].pes == 3.5:
                        self.nomes_sillabes[pos+1].pes = 4.0 # Restaura el pes original de la síl·laba següent si havia estat penalitzada per ser candidata a tall
                    pos = pos + 1  # Convertim a 1-based
                    word_at_pos.paraula_tall = True  # Marca la paraula com a tall
                    return f'{pos}+{10 - pos}', 'tall'
                elif self.nomes_sillabes[pos].pes > 0.5 and self.nomes_sillabes[
                    pos].pes < 4:  # Si el pes és d'accent bivalent o secundari, considera que és discontinu
                    #print('\t\t> Pes de la síl·laba indica accent bivalent o secundari, considerant com a discontinu')
                    self.nomes_sillabes[pos].pes = 5.0  # Assegura que el pes de la síl·laba de tall és alt
                    if self.nomes_sillabes[pos + 1].flag and self.nomes_sillabes[pos + 1].pes is not None and self.nomes_sillabes[pos + 1].pes == 3.5:
                        self.nomes_sillabes[pos+1].pes = 4.0 # Restaura el pes original de la síl·laba següent si havia estat penalitzada per ser candidata a tall
                    pos = pos + 1  # Convertim a 1-based
                    word_at_pos.paraula_tall = True  # Marca la paraula com a tall
                    return f'{pos}+{10 - pos}', 'discontinu'
            elif self.nomes_sillabes[
                pos].pes >= 2:  # Si no és la darrera síl·laba del mot però té accent, considera que és continu
                #print('\t\t> No és la darrera síl·laba del mot però té accent, considerant com a continu')
                if self.nomes_sillabes[pos + 1].flag and self.nomes_sillabes[pos + 1].pes is not None and self.nomes_sillabes[pos + 1].pes == 3.5:
                    self.nomes_sillabes[
                        pos + 1].pes = 4.0  # Restaura el pes original de la síl·laba següent si havia estat penalitzada per ser candidata a tall
                pos = pos + 1  # Convertim a 1-based
                word_at_pos.paraula_tall = True  # Marca la paraula com a tall
                return f'{pos}+{10 - pos}', 'continu'
        return None, None  # No s'ha trobat una model vàlida
    return None


def _get_word_at_position(self, pos: int):
    """Retorna la paraula que conté la síl·laba a la posició donada."""
    if pos >= len(self.nomes_sillabes):
        return None

    for word in self.words:
        if self.nomes_sillabes[pos] in word.stress:
            return word
    return None


def _get_next_word_at_position(self, pos: int):
    """Retorna la paraula següent a la que conté la síl·aba a la posició donada."""
    word_at_pos = _get_word_at_position(self, pos)

    if word_at_pos and word_at_pos.w_index + 1 < len(self.words):
        return self.words[word_at_pos.w_index + 1]
    return None


def subdivideix(self):
    """Aquesta funció subdivideix el vers en còlons si conté un tall.

    - Si `self.posicio_tall` no existeix (o és None), intenta obtenir-la cridant
      `tall(self)` i l'assigna explícitament. Això evita que `subdivideix` retorni
      sempre `None` quan abans no s'hagi calculat el tall.
    - Fa comprovacions robustes dels tipus (int) i del recompte de síl·labes
      mètriques abans de fer l'operació aritmètica.
    - Si no es pot determinar el recompte mètric, retorna una cadena indicativa
      en lloc de tirar una excepció.
    """
    # Intentem usar l'atribut existent
    pos = getattr(self, 'posicio_tall', None)

    # Si no existeix, prova de calcular-lo cridant tall(self)
    if pos is None:
        try:
            pos = tall(self)[0]
        except Exception:
            pos = None
        # Assignem si l'hem obtingut
        if pos is not None:
            self.posicio_tall = pos
        else:
            return None

    # Assegura que és un enter vàlid
    try:
        pos_int = int(pos)
    except Exception:
        return None

    # Obté el recompte de síl·labes mètriques (int) de forma segura
    recompte = getattr(self, 'recompte_sillabes_metriques', None)
    if recompte is None:
        # Intentem recalcular-lo sense importar la dependència exterior si ja existeix
        try:
            from AIMeRiC.escansio.modules.utils.metre import recompte_metric
            recompte = recompte_metric(self)
            self.recompte_sillabes_metriques = recompte
        except Exception:
            # No podem obtenir el recompte, retornem una forma parcial
            return f'{pos_int}+?'

    try:
        right = int(recompte) - pos_int
    except Exception:
        return f'{pos_int}+?'

    return f'{pos_int}+{right}'


def cesura_femenina(self):
    """Aquesta funció aplica la cesura femenina al vers. [FUNCIÓ EN DESENVOLUPAMENT, INACTIVA]"""
    if len(self.sillables_metriques) == 11:
        # if len(re.findall("[_:]", ''.join([x.text for x in self.no_words[4:6]]))) < 0:
        if int(self.nomes_sillabes[4].pes) >= 4:
            for word in self.words:
                for syllable in word.stress:
                    if syllable == self.nomes_sillabes[4]:
                        if seguent(syllable, word.stress) is not None:
                            if re.findall("[:_]", seguent(syllable, word.stress).text):
                                # Gestiona els casos de sinalefa en la cesura, ex.: *jo som la page<sa_amb> els records honrats
                                fsubs = split_syllable(self, seguent(syllable, word.stress))
                                syl1 = fsubs[0]
                                syl2 = fsubs[1]
                                word.stress[syllable.s_index + 1] = syl1
                                self.words[word.w_index + 1].stress.insert(0, syl2)
                                break
                            syllable.pes = 5.0
                            self.nomes_sillabes[4].pes = 5.0
                            self.patro[4] = 5
                            ignore_syll = word.stress[word.stress.index(syllable) + 1]
                            del word.stress[word.stress.index(syllable) + 1:]
                            self.actualitza()
                            self.model = "5'+5"
                            self.string = '#'.join(
                                ['.'.join([syllable.text for syllable in word.stress]) for word in
                                 self.words[:word.w_index + 1]]) + ".<" + ignore_syll.text + '>#' + '#'.join(
                                ['.'.join([syllable.text for syllable in word.stress]) for word in
                                 self.words[word.w_index + 1:]])
                            self.escansio_text = '#'.join(
                                [word.plain() for word in
                                 self.words[:word.w_index + 1]]) + ".<" + ignore_syll.text + '>#' + '#'.join(
                                [word.plain() for word in self.words[word.w_index + 1:]])
