import re

from AIMeRiC.escansio.modules.syllable import Syllable
from AIMeRiC.escansio.modules.utils.meter import recompte_metric
from AIMeRiC.escansio.modules.utils.stress import get_stress_index


def max_pes(syllable1, syllable2) -> int:
    if int(syllable1.pes) > int(syllable2.pes):
        return syllable1.pes
    else:
        return syllable2.pes


def score(syllable, vers):
    points = 0
    if syllable.fono_info['alta']:
        if syllable.fono_info['vocal'] == 'i':
            points += 2
        else:
            points += 1
    if not syllable.tonic and syllable.fono_info['neutra']:
        points += 3
    if syllable.triftong:
        points -= 20
    if not syllable.tonic:
        points += 2
    if syllable.fono_info['rotica']:
        points -= 3
    if syllable.fusionada:
        points -= 20
    #print(f'Punts: {syllable.text}: {points}')  # Debug
    if len(vers) > 6:
        if syllable == vers[3] and int(syllable.pes) > 2:  # Si és la síl·laba del tall 4
            points -= 8
        elif syllable == vers[4] and int(syllable.pes) > 2:  # Si és la síl·laba del tall 5
            points -= 4
        elif syllable == vers[5] and int(syllable.pes) > 2:  # Si és la síl·laba del tall 6
            points -= 2
    syllable.fusionable = points
    #print(f'Punts: {syllable.text}: {points}')  # Debug
    return points


def score_diftong(syll1, syll2):
    if not syll1.fusionada and not syll2.fusionada and syll1.fono_info['alta']:
        # Creixent
        return 10
    if not syll1.fusionada and not syll2.fusionada and syll1.fono_info['neutra'] and syll2.fono_info['neutra']:
        return 12
    elif not syll1.fusionada and not syll2.fusionada and syll1.fono_info['neutra'] or syll2.fono_info['alta']:
        return 1
    else:
        return 0


def best_contacte_vocalic(self):
    """Aquesta funció retorna els candidats de contacte vocàlic ordenats per l'índex de fusió"""
    vers = sum([x.stress for x in self.words], [])
    candidats = []
    for syllable in vers:
        next_syllable = vers[vers.index(syllable) + 1] if vers.index(syllable) < len(vers) - 1 else None
        if next_syllable is not None:
            points = 0
            if syllable.last and next_syllable.first:
                if syllable.ends_with_vowel and next_syllable.starts_with_vowel:
                    syll1_points = score(syllable, vers)
                    syll2_points = score(next_syllable, vers)
                    points = syll1_points + syll2_points
                    #print(f'Punts: [{syllable.text}: {syll1_points}], [{next_syllable.text}: {syll2_points}]: {points}; Vallverdú: {vallverdu_score(syllable, next_syllable)} + score_diftong ({score_diftong(syllable, next_syllable)}); Final: {points*vallverdu_score(syllable, next_syllable)+score_diftong(syllable, next_syllable)}')  # Debug
                    points = points * vallverdu_score(syllable, next_syllable) + score_diftong(syllable, next_syllable)
                    # Factor de correcció per a síl·labes fusionades
                    if syllable.fusionada or next_syllable.fusionada:
                        points -= 4
                    syllable.fusionable = points
                candidats.append((syllable, next_syllable, points)) if points > 0 else None
    # Ordena els candidats per puntuació de major a menor:
    candidats = sorted(candidats, key=lambda x: x[2], reverse=True)
    #print('> Candidats contacte:', [(x.text, y.text, z) for x, y, z in candidats])  # Debug
    return candidats


def vallverdu_score(syllable1, syllable2):
    """Aquesta funció resol els casos de contacte vocàlic segons Vallverdú"""
    score = 0
    # un cas concret meu: infinitiu + pronoms febles
    if syllable1.ends_with_vowel and syllable1.fono_info['rotica'] and syllable2.text[0] == '-':
        return score

    if syllable1.ends_with_vowel and syllable2.starts_with_vowel:
        vocal1 = syllable1.fono_info
        vocal2 = syllable2.fono_info

        #print(f'({syllable1.text}, {syllable1.pes}) + ({syllable2.text}, {syllable2.pes})')  # Debug

        if int(syllable1.pes) >= 3 and int(syllable2.pes) >= 3:  # Dues síl·labes tòniques
            return 0
        elif int(syllable1.pes) >= 3 and int(syllable2.pes) < 3:  # Tònica + àtona
            if vocal2['neutra']:  # 1.2. V́1+ə → elisió (arribaré el dia, arribaré avui) [GARAU]
                return 2  # Elisió
        elif int(syllable1.pes) < 3 and int(syllable2.pes) >= 3:  # Àtona + tònica
            if int(syllable2.pes) == 3:
                if vocal2['alta']:
                    #[GARAU] V1+V́2i/u → diftong (casa una)
                    return 1
            elif vocal1['alta'] and not vocal2['alta']:
                return 1
            # [GARAU] V1i/u+V́2i/u → hiat (i una), si les vocals no són idèntiques
            elif vocal1['alta'] and vocal2['vocal'] != vocal1['vocal']:
                return 1
            # 3.4. ə+V́2(no-tancada) → elisió (casa alta)
            elif vocal1['neutra'] and not vocal2['alta'] or vocal2['neutra']:
                return 2
            # 1.3. V1i/u+V́2 → hiat (canti himnes)
            elif vocal1['alta'] or not vocal1['alta'] or (vocal1['neutra'] and vocal2['alta']):
                return 0

        elif int(syllable1.pes) < 3 and int(syllable2.pes) < 3:  # Àtones
            # 3.2. ə+ə → elisió (compta estrelles)
            if vocal1['neutra'] and vocal2['neutra'] or vocal2['neutra'] or (vocal1['neutra'] and vocal2['alta']):
                return 2
            # 3.1. V1i/u=V2i/u → elisió (vegi insectes)
            elif vocal1['alta'] and vocal2['alta'] and vocal1['vocal'] == vocal2['vocal']:
                return 2
            # 2.1.4. V1(i/u)+V2 → diftong (compri-ho)
            elif vocal1['alta'] and not vocal2['alta'] or not vocal1['alta'] and vocal2['alta']:
                return 1
    return score


def join_syllables(syllable1, syllable2) -> Syllable:
    """Aquesta funció resol els casos de contacte vocàlic forçat"""
    if syllable1.ends_with_vowel and syllable2.starts_with_vowel:
        syllable1.text = f"{syllable1.text}_{syllable2.text}"
        syllable1.pes_fusion = f"{syllable1.pes}_{syllable2.pes}"
        syllable1.pes = syllable1.pes if int(syllable1.pes) > int(syllable2.pes) else syllable2.pes
        syllable1.fusion_direction = "dreta" if int(syllable1.pes) > int(syllable2.pes) else "esquerra"
        syllable1.fusionada = True
        if not re.findall(r"[aeiouyàáèéìíòóùú]", syllable1.text[-1]):
            syllable1.ends_with_vowel = False
        return syllable1


def split_syllable(syllable) -> (Syllable, Syllable):
    """Aquesta funció resol els casos de desfeta de contactes vocàlics"""
    if syllable.triftong:
        if re.findall(r"[_:]", syllable.text):
            syllabe1 = Syllable(index=syllable.s_index, syllable=(
                re.split(r"[_:]", syllable.text)[0], re.split(r"[_:]", syllable.pes_fusion)[0]),
                                len_word=syllable.len_word)

            text_syll2 = '_'.join(re.split(r"[_:]", syllable.text)[1:])
            pes_syll2 = '_'.join(re.split(r"[_:]", syllable.pes_fusion)[1:])

            syllabe2 = Syllable(index=syllable.s_index, syllable=(text_syll2, pes_syll2),
                                len_word=syllable.len_word)

            syllabe1.fusionada = False
            syllabe2.fusionada = True
            syllabe1.triftong = False
            return syllabe1, syllabe2
    elif syllable.fusionada and not syllable.triftong:
        if re.findall(r"[_:]", syllable.text):
            pes1 = re.split(r"[_:]", syllable.pes_fusion)[0]
            pes2 = re.split(r"[_:]", syllable.pes_fusion)[1]
            syllabe1 = Syllable(index=syllable.s_index, syllable=(re.split(r"[_:]", syllable.text)[0], pes1),
                                len_word=syllable.len_word)
            syllabe2 = Syllable(index=syllable.s_index, syllable=(re.split(r"[_:]", syllable.text)[1], pes2),
                                len_word=syllable.len_word)
            syllabe1.fusionada = False
            syllabe2.fusionada = False
            return syllabe1, syllabe2


def resol_contactes_vocalics(self, best_mode):
    """Resolves vowel contacts in the verse according to Catalan phonology"""

    def get_best(mode):
        if mode == 'natural':
            return best_contacte_vocalic(self)
        elif mode == 'sinalefa':
            return best_sinalefa(self)
        return None

    best = get_best(best_mode)

    if best is not None and self.recompte_sillabes_metriques > self.objectiu:  # Si hi ha contactes vocals i el recompte mètric no coincideix amb l'objectiu
        diff = self.recompte_sillabes_metriques - self.objectiu  # Calcula la diferència
        safety = 0  # Comptador de seguretat
        while diff > 0 and safety < 10:  # Mentre hi hagi diferència i hi hagi contactes vocals candidats (comptador de seguretat)
            # change = best.pop(0) # Treu el primer contacte vocal candidat
            if get_best(best_mode):
                change = get_best(best_mode).pop(0)
            else:
                break
            wi = 0
            while wi < len(self.words) - 1:
                word = self.words[wi]
                if change[0] in word.stress:
                    result = join_syllables(change[0], change[1])
                    if result:
                        next_word = self.words[wi + 1]
                        if word.n_syllables == 1 and next_word.n_syllables == 1:
                            """Mètode 1: dos monosíl·labs"""
                            # print(f'Mètode 1: {word.text} + {next_word.text}')  # Debug
                            next_word.stress[0] = result
                            del self.words[wi]
                        elif word.n_syllables == 1 and next_word.n_syllables > 1:
                            """Mètode 2: un monosíl·lab i un polisíl·lab"""
                            # print(f'Mètode 2: {word.text} + {next_word.text}')  # Debug
                            next_word.stress[0] = result
                            next_word.stress_index = get_stress_index(next_word)
                            next_word.n_syllables = len(next_word.stress)
                            del self.words[wi]
                        elif word.n_syllables > 1 and next_word.n_syllables == 1:
                            """Mètode 3: un polisíl·lab i un monosíl·lab"""
                            # print(f'Mètode 3: {word.text} + {next_word.text}')  # Debug
                            word.stress[-1] = result
                            word.stress_index = get_stress_index(word)
                            word.n_syllables = len(word.stress)
                            del self.words[wi + 1]
                        elif word.n_syllables > 1 and next_word.n_syllables > 1:
                            """Mètode 4: dos polisíl·labs"""
                            # print(f'Mètode 4: {word.text} + {next_word.text}')  # Debug
                            word.stress[-1] = result
                            word.stress[-1].ends_with_vowel = word.stress[-1].vowel_end()
                            word.n_syllables = len(word.stress)
                            del next_word.stress[0]
                            word.stress_index = get_stress_index(word)
                            next_word.stress_index = get_stress_index(next_word)
                            next_word.stress[0].starts_with_vowel = next_word.stress[0].vowel_start()
                            next_word.n_syllables = len(next_word.stress)
                            if not word.stress:  # Si la paraula no té síl·labes, s'elimina
                                del self.words[wi]
                                wi -= 1
                                continue
                        self.nomes_sillabes = sum([w.stress for w in self.words],
                                                  [])  # Actualitza la llista de síl·labes
                        self.recompte_sillabes_metriques = recompte_metric(
                            self)  # Actualitza el recompte de síl·labes mètriques
                        diff = self.recompte_sillabes_metriques - self.objectiu  # Actualitza la diferència
                wi += 1  # Incrementa el comptador de paraules
            safety += 1  # Incrementa el comptador de seguretat
        # print(f'Len(best): {len(best)}, Diff: {diff}')  # Debug


def contactes_vocalics_info(self):
    """Return vowel-contact information as an ordered mapping including syllable index (s_index)."""
    from copy import deepcopy
    clean = deepcopy(self.escansio_text)
    dic_clean = {
        r"([qg])u([ei])": r"\1\2",
        "[aàáâ]": "a", "[eèéê]": "e", "[iíìïyýÿî]": "i",
        "[oòóô]": "o", "[uúùüû]": "u",
        "[AÀÁÂ]": "A", "[EÈÉÊ]": "E", "[IÍÌÏYÝŸÎ]": "I",
        "[OÒÓÔ]": "O", "[UÚÙÜÛ]": "U",
        "[Hh]": ""
    }
    for key, value in dic_clean.items():
        clean = re.sub(key, value, clean)

    candidates = []
    consumed_spans = []

    def overlaps(span):
        s, e = span
        for cs, ce in consumed_spans:
            if not (e <= cs or s >= ce):
                return True
        return False

    def mark(span):
        consumed_spans.append(span)

    def make_entry(mgroups, tipo, separator=None):
        vocals = ''.join([g for g in mgroups if g is not None]).lower()
        tonicitat = any(any(ch.isupper() for ch in (g or "")) for g in mgroups)
        frontera = 'exterior' if separator in ("#", "‿", "_") else 'interior'
        return {'tipus': tipo, 'tonicitat': tonicitat, 'frontera': frontera, 'vocals': vocals}

    # find triftongs (with tie and adjacency)
    for m in re.finditer(r'([AEIOUaeiou])[‿_]([AEIOUaeiou])[‿_]([AEIOUaeiou])', clean):
        span = m.span()
        if not overlaps(span):
            entry = make_entry((m.group(1), m.group(2), m.group(3)), 'triftong', separator='‿')
            candidates.append((span[0], span[1], entry))
            mark(span)
    for m in re.finditer(r'([AEIOUaeiou])([AEIOUaeiou])([AEIOUaeiou])', clean):
        span = m.span()
        if not overlaps(span):
            entry = make_entry((m.group(1), m.group(2), m.group(3)), 'triftong', separator=None)
            candidates.append((span[0], span[1], entry))
            mark(span)

    # diftongs
    for m in re.finditer(r'([AEIOUaeiou])[‿_]([AEIOUaeiou])', clean):
        span = m.span()
        if not overlaps(span):
            entry = make_entry((m.group(1), m.group(2)), 'diftong', separator='‿')
            candidates.append((span[0], span[1], entry))
            mark(span)
    for m in re.finditer(r'([AEIOUaeiou])([AEIOUaeiou])', clean):
        span = m.span()
        if not overlaps(span):
            entry = make_entry((m.group(1), m.group(2)), 'diftong', separator=None)
            candidates.append((span[0], span[1], entry))
            mark(span)

    # hiats
    for m in re.finditer(r'([AEIOUaeiou])#([AEIOUaeiou])', clean):
        span = m.span()
        if not overlaps(span):
            entry = make_entry((m.group(1), m.group(2)), 'hiat', separator='#')
            candidates.append((span[0], span[1], entry))
            mark(span)
    for m in re.finditer(r'([AEIOUaeiou])\.([AEIOUaeiou])', clean):
        span = m.span()
        if not overlaps(span):
            entry = make_entry((m.group(1), m.group(2)), 'hiat', separator='.')
            candidates.append((span[0], span[1], entry))
            mark(span)

    candidates.sort(key=lambda x: x[0])

    # Substitute each contact by a single marker to compute syllable (vowel-nucleus) index
    temp_text = clean
    offset = 0
    for start, end, entry in candidates:
        temp_text = temp_text[:start + offset] + "¤" + temp_text[end + offset:]
        offset += 1 - (end - start)

    # Remove consonants to leave only vowel nuclei and markers
    temp_text_nocons = re.sub(r"[^AEIOUaeiou¤]", "", temp_text)

    # Build accumulative dict with 1-based integer keys
    result = {}
    idx = 1
    for start, end, entry in candidates:
        # skip empty vocal results
        if not entry.get('vocals'):
            continue

        # find first marker occurrence (corresponds to this candidate)
        try:
            marker_index = temp_text_nocons.index("¤")
        except ValueError:
            # no marker found (shouldn't happen), skip
            continue

        entry['s_index'] = marker_index + 1  # 1-based syllable index
        result[idx] = entry
        idx += 1

        # remove this marker for next iteration
        temp_text_nocons = temp_text_nocons.replace("¤", "", 1)

    # overwrite previous stored info so repeated calls replace earlier results
    setattr(self, 'contactes_vocalics', result)
    return result



def best_sinalefa(self):
    candidats = []
    vers = sum([x.stress for x in self.words], [])
    for syllable in vers:
        next_syllable = vers[vers.index(syllable) + 1] if vers.index(syllable) < len(vers) - 1 else None
        if next_syllable is not None:
            if syllable.last and next_syllable.first:
                if syllable.ends_with_vowel and next_syllable.starts_with_vowel:
                    punts = score(syllable, vers) + score(next_syllable, vers)
                    candidats.append((syllable, next_syllable, punts))

    candidats = sorted(candidats, key=lambda x: x[2], reverse=True)
    #print('> Candidats sinalefa:', [(x.text, y.text, z) for x, y, z in candidats])  # Debug
    return candidats


def best_sineresi(self):
    vers = sum([x.stress for x in self.words], [])
    candidats = []
    for syllable in vers:
        next_syllable = vers[vers.index(syllable) + 1] if vers.index(syllable) < len(vers) - 1 else None
        if next_syllable is not None:
            if syllable.ends_with_vowel and next_syllable.starts_with_vowel:
                punts = score(syllable, vers) + score(next_syllable, vers)
                candidats.append((syllable, next_syllable, punts))

    candidats = sorted(candidats, key=lambda x: x[2], reverse=True)
    # print('> Candidats sineresi:', [(x.text, y.text, z) for x, y, z in candidats])  # Debug
    return candidats

