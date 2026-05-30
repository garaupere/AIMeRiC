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
    """Identifica el model subjacent al decasíl·lab."""
    if self.recompte_sillabes_metriques == 10 and self.model is None:
        subdpos = [3, 5, 4, 2, 6]  # Posicions: 4+6, 6+4, 5+5, 3+7, 7+3
        candidats = []

        for pos in subdpos:
            pts = 0
            if pos == 3 or pos == 5: # 4+6, 6+4
                pts += 3
            elif pos == 4: # 5+5
                pts += 2
            elif pos == 2 or pos == 6: # 3+7, 7+3
                pts += 1

            if self.nomes_sillabes[pos].has_PUNCT:
                signe_punt = self.nomes_sillabes[pos].which_PUNCT
                if signe_punt == ',':
                    pts += 0.25
                elif signe_punt == ';':
                    pts += 0.35
                elif signe_punt in ['.', ':', '?', '!']:
                    pts += 0.45

            pes = self.nomes_sillabes[pos].pes if pos < len(self.nomes_sillabes) else None
            #print(f'Candidat {pos}, pts: {pts}, pes: {pes}, text: {self.nomes_sillabes[pos].text}')
            candidats.append((pos, pts, pes))

        candidats_valids = [(pos, pts, pes) for pos, pts, pes in candidats if pes is not None and pes >= 1]
        candidats_valids.sort(key=lambda x: (-x[1], subdpos.index(x[0])))
        #print(candidats_valids)
        #if any(pos == 5 for pos, pts, pes in candidats_valids):
            #candidats_valids = [(pos, pts, pes) for pos, pts, pes in candidats_valids if pos != 2]

        # Evalua tipus de model per a cada candidat
        scores = []
        for pos, pts, pes in candidats_valids:
            word_at_pos = _get_word_at_position(self, pos)

            model_type = None
            if word_at_pos and word_at_pos.stress and word_at_pos.stress[-1] == self.nomes_sillabes[pos] and \
               not getattr(word_at_pos, 'has_PRONe', False) and not getattr(self.nomes_sillabes[pos], 'fusionada', False):

                if self.nomes_sillabes[pos].pes >= 4:
                    model_type = 'tall'
                elif self.nomes_sillabes[pos].pes > 0.5 and self.nomes_sillabes[pos].pes < 4:
                    model_type = 'discontinu'
                elif self.nomes_sillabes[pos].pes > 1:
                    model_type = 'continu'
            elif self.nomes_sillabes[pos].pes > 1:
                model_type = 'continu'

            if model_type:
                scores.append({
                    'pos': pos,
                    'pts': pts,
                    'pes': pes,
                    'type': model_type,
                    'word': word_at_pos
                })

        # Evalua tipus de model per a cada candidat i suma punts per prioritat
        scores = []
        for pos, pts, pes in candidats_valids:
            word_at_pos = _get_word_at_position(self, pos)
            pts_prioritat = pts  # Punts base de posició i puntuació

            model_type = None
            if word_at_pos and word_at_pos.stress and word_at_pos.stress[-1] == self.nomes_sillabes[pos] and \
                    not getattr(word_at_pos, 'has_PRONe', False) and not getattr(self.nomes_sillabes[pos],
                                                                                 'fusionada', False):

                if self.nomes_sillabes[pos].pes >= 4:
                    model_type = 'tall'
                    pts_prioritat += 1
                elif self.nomes_sillabes[pos].pes > 0.5 and self.nomes_sillabes[pos].pes < 4:
                    model_type = 'discontinu'
                    pts_prioritat += 0.5
                elif self.nomes_sillabes[pos].pes > 1:
                    model_type = 'continu'
                    pts_prioritat += 0.25
            elif self.nomes_sillabes[pos].pes > 1:
                model_type = 'continu'
                pts_prioritat += 0.25

            if model_type:
                scores.append({
                    'pos': pos,
                    'pts': pts_prioritat,  # ✅ Punts totals (base + prioritat)
                    'pes': pes,
                    'type': model_type,
                    'word': word_at_pos
                })

        # Ordena per punts totals (descendent) - candidat amb més punts és el millor
        scores.sort(key=lambda x: -x['pts'])
        #print(scores)
        if scores:
            best = scores[0]
            _apply_model(self, best['pos'], best['word'], best['type'])
            pos_1based = best['pos'] + 1
            return f'{pos_1based}+{10 - pos_1based}', best['type']

        return None, None


def _apply_model(self, pos, word_at_pos, model_type):
    """Aplica els canvis associats al model identificat"""

    if model_type == 'tall':
        self.nomes_sillabes[pos].pes = 5.0
        if word_at_pos:
            word_at_pos.paraula_tall = True




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


def detecta_cesura_femenina(self):
    """
    Detecta si el vers és un decasíl·lab 5+5 amb cesura femenina.
    Retorna (model, tipus) si la detecta, sinó (None, None).

    Criteris:
    - Recompte total de síl·labes = 11
    - Síl·laba 5 és tònica (pes >= 2)
    - Síl·laba 6 és àtona (pes < 2) - EXTRAMETRICAL
    - Síl·laba 7 és tònica (pes >= 2) - Inicia el 2n hemistiqui
    """
    if self.recompte_sillabes_metriques != 11 or self.model is not None:
        return None, None

    # Verifica que la síl·laba 5 és tònica
    if self.nomes_sillabes[4].pes is None or self.nomes_sillabes[4].pes < 2:
        return None, None

    # Verifica que la síl·laba 6 és àtona (extrametrical)
    if self.nomes_sillabes[5].pes is None or self.nomes_sillabes[5].pes >= 2:
        return None, None

    # Verifica que la síl·laba 7 és tònica
    #if self.nomes_sillabes[6].pes is None or self.nomes_sillabes[6].pes < 2:
    #    return None, None

    # Verifica que la síl·laba 11 (última) és tònica
    if self.nomes_sillabes[9].pes is None or self.nomes_sillabes[9].pes < 2.5:
        return None, None

    # Determina el tipus (tall, discontinu, continu) segons la síl·laba 5
    syl_5 = self.nomes_sillabes[4]
    word_at_5 = _get_word_at_position(self, 4)

    model_type = None
    if word_at_5 and word_at_5.stress and word_at_5.stress[-1] == syl_5 and \
       not getattr(word_at_5, 'has_PRONe', False) and not getattr(syl_5, 'fusionada', False):

        if syl_5.pes >= 4:
            model_type = 'tall'
        elif syl_5.pes > 0.5 and syl_5.pes < 4:
            model_type = 'discontinu'
        elif syl_5.pes > 1:
            model_type = 'continu'
    elif syl_5.pes > 2.5:
        model_type = 'continu'

    if model_type:
        # Marca la síl·laba 6 com extrametrical
        self.nomes_sillabes[5].extrametrical = True
        syl_5.pes = 5.0
        if word_at_5:
            word_at_5.paraula_tall = True

        return "5'+5", model_type

    return None, None
#
# def identifica_model_antic(self):
#     """Identifica el model subjacent al decasíl·lab (4+6, 6+4 o 5+5)"""
#     if self.recompte_sillabes_metriques == 10 and self.model is None:
#         subdpos = [3, 5, 4, 2, 6]  # Preferències de models: 4+6, 6+4, 5+5, 3+7, 7+3.
#         # Per a les síl·labes del vers, obtenim els pesos de les subdpos
#         candidats = []
#         for pos in subdpos:
#             pts = 0
#             #print('Evaluant posició de model:', pos, f"amb la síl·laba corresponent:", self.nomes_sillabes[pos].text if pos < len(self.nomes_sillabes) else None, "pes: ", self.nomes_sillabes[pos].pes if pos < len(self.nomes_sillabes) else None)
#             if pos == 3 or pos == 5:
#                 pts = self.nomes_sillabes[pos].pes
#             elif pos == 3 or pos == 5:
#                 if self.nomes_sillabes[pos].pes is not None and self.nomes_sillabes[pos].pes == 3:
#                     #self.nomes_sillabes[pos].pes = 3.75
#                     pts = self.nomes_sillabes[pos].pes
#             elif pos == 4 and len(candidats) > 0:
#                 if 3 in [c[0] for c in candidats]:
#                     if self.nomes_sillabes[pos].pes is not None and self.nomes_sillabes[pos].pes > 2:
#                         pts = self.nomes_sillabes[pos].pes
#                         self.nomes_sillabes[pos].flag = 'penalitzat_per_tall'
#             elif pos == 2 and len(candidats) > 0:
#                 self.nomes_sillabes[pos].flag = 'penalitzat_per_tall'
#                 pts = self.nomes_sillabes[pos].pes - self.nomes_sillabes[pos+1].pes
#                 if pos == 2:
#                     if self.nomes_sillabes[6].pes < 2 or self.nomes_sillabes[4].pes >= self.nomes_sillabes[pos].pes: # Si la síl·laba 7 no és tònica o la 5 és major que la 3, omet el candidat
#                         continue
#             elif pos == 6 and len(candidats) > 0:
#                 self.nomes_sillabes[pos].flag = 'penalitzat_per_tall'
#                 pts = self.nomes_sillabes[pos].pes - self.nomes_sillabes[pos+1].pes
#                 if self.nomes_sillabes[2].pes < 2 or self.nomes_sillabes[3].pes >= self.nomes_sillabes[pos].pes: # Si la síl·laba 3 no és tònica o la 4 és major que la 7, omet el candidat
#                     continue
#
#             if self.nomes_sillabes[pos].has_PUNCT:
#                 pts = self.nomes_sillabes[pos].pes + 1
#
#             candidats.append((pos, pts, self.nomes_sillabes[pos].pes if pos < len(self.nomes_sillabes) else None))
#         # ordena els candidats per pes (descendent) i després per posició (segons la preferència). Elimina els candidats amb pes None o <= 2.0
#         candidats_valids = [(pos, pts, pes) for pos, pts, pes in candidats if pes is not None and pes >= 2]
#
#         if any(pos == 5 for pos, pts, pes in candidats_valids): # Si hi ha cap candidat de la posició 6 (model 6+4) i hi ha candidat de la posició 3 (model 3+7) descarta el 3+7.
#             candidats_valids = [(pos, pts, pes) for pos, pts, pes in candidats_valids if pos != 2]
#
#         candidats_valids.sort(
#             key=lambda x: (-x[1], subdpos.index(x[0])))  # Ordena per pes descendent i després per preferència de posició
#
#
#         #print('>> Candidats de model ordenats per pes i preferència:', candidats_valids)
#         # Defineix el tipus de model.
#         for pos, pts, pes in candidats_valids:
#             # si el candidat és la darrera síl·laba del mot i el mot no té PRONe, ni és fusionada
#             word_at_pos = _get_word_at_position(self, pos)
#             #print('\t> Candidat a model:', pos, 'Pes:', 'Punts:', pts, pes,'Paraula:', word_at_pos.text if word_at_pos else None)
#             if word_at_pos and word_at_pos.stress and word_at_pos.stress[-1] == self.nomes_sillabes[pos] and not getattr(
#                     word_at_pos, 'has_PRONe', False) and not getattr(self.nomes_sillabes[pos], 'fusionada', False):
#                 #print('\t\t> És la darrera síl·laba del mot i el mot no té PRONe ni és fusionada')
#
#                 if self.nomes_sillabes[pos].pes >= 4 or (self.nomes_sillabes[pos].pes >= 3 and pos==3) or (pos == 4 and self.nomes_sillabes[pos].pes == 3.5):  # Si el pes és un accent lèxic, considera que és un tall
#                     self.nomes_sillabes[pos].pes = 5.0  # Assegura que el pes de la síl·laba de tall és 5.0
#                     #print('\t\t> Pes de la síl·laba de tall assegurat a 5.0')
#                     if self.nomes_sillabes[pos + 1].flag and self.nomes_sillabes[pos + 1].pes is not None and self.nomes_sillabes[pos + 1].pes == 3.5:
#                         self.nomes_sillabes[pos+1].pes = 4.0 # Restaura el pes original de la síl·laba següent si havia estat penalitzada per ser candidata a tall
#                     pos = pos + 1  # Convertim a 1-based
#                     word_at_pos.paraula_tall = True  # Marca la paraula com a tall
#                     return f'{pos}+{10 - pos}', 'tall'
#                 elif self.nomes_sillabes[pos].pes > 0.5 and self.nomes_sillabes[
#                     pos].pes < 4:  # Si el pes és d'accent bivalent o secundari, considera que és discontinu
#                     #print('\t\t> Pes de la síl·laba indica accent bivalent o secundari, considerant com a discontinu')
#                     self.nomes_sillabes[pos].pes = 5.0  # Assegura que el pes de la síl·laba de tall és alt
#                     if self.nomes_sillabes[pos + 1].flag and self.nomes_sillabes[pos + 1].pes is not None and self.nomes_sillabes[pos + 1].pes == 3.5:
#                         self.nomes_sillabes[pos+1].pes = 4.0 # Restaura el pes original de la síl·laba següent si havia estat penalitzada per ser candidata a tall
#                     pos = pos + 1  # Convertim a 1-based
#                     word_at_pos.paraula_tall = True  # Marca la paraula com a tall
#                     return f'{pos}+{10 - pos}', 'discontinu'
#             elif self.nomes_sillabes[
#                 pos].pes >= 2:  # Si no és la darrera síl·laba del mot però té accent, considera que és continu
#                 #print('\t\t> No és la darrera síl·laba del mot però té accent, considerant com a continu')
#                 if self.nomes_sillabes[pos + 1].flag and self.nomes_sillabes[pos + 1].pes is not None and self.nomes_sillabes[pos + 1].pes == 3.5:
#                     self.nomes_sillabes[
#                         pos + 1].pes = 4.0  # Restaura el pes original de la síl·laba següent si havia estat penalitzada per ser candidata a tall
#                 pos = pos + 1  # Convertim a 1-based
#                 word_at_pos.paraula_tall = True  # Marca la paraula com a tall
#                 return f'{pos}+{10 - pos}', 'continu'
#         return None, None  # No s'ha trobat una model vàlida
#     return None