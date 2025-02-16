import re
from copy import deepcopy

from AIMeRiC.escansio.modules.syllable import Syllable
from AIMeRiC.escansio.modules.vers_utils.meter import recompte_metric


def max_pes(syllable1, syllable2) -> int:
    if int(syllable1.pes) > int(syllable2.pes):
        return syllable1.pes
    else:
        return syllable2.pes


def score(syllable, vers):
    points = 0
    if not syllable.ends_with_vowel:
        if not syllable.starts_with_vowel:
            return points
    else:
        if syllable.fono_info['alta'] or syllable.fono_info['neutra']:
            points += 1
        if syllable.triftong:
            points -= 20
        if not syllable.tonic:
            points += 2
        if not syllable.fono_info['rotica']:
            points += 1
        if syllable.fusionada:
            points -= 20
        if len(vers) > 6:
            if syllable == vers[3] and int(syllable.pes) > 2:  # Si és la síl·laba del tall 4
                points -= 8
            elif syllable == vers[4] and int(syllable.pes) > 2:  # Si és la síl·laba del tall 5
                points -= 4
            elif syllable == vers[5] and int(syllable.pes) > 2:  # Si és la síl·laba del tall 6
                points -= 2
    syllable.fusionable = points
    return points


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
                    points = points + vallverdu_score(syllable, next_syllable)
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
    if syllable1.ends_with_vowel and syllable1.fono_info['rotica']:
        if syllable2.text[0] == '-':
            score -= 2

    if syllable1.ends_with_vowel and syllable2.starts_with_vowel:
        vocal1 = syllable1.fono_info
        vocal2 = syllable2.fono_info

        # ------ Hiats (score < 0) ------
        if syllable1.tonic and syllable2.tonic:
            # 1.1.	V́1≠V́2 → hiat (voler homes)
            if vocal1['vocal'] != vocal2['vocal']:
                score -= 1
            # 1.2.	V́1=V́2 → hiat (menjar algues)
            elif vocal1['vocal'] == vocal2['vocal']:
                score -= 1
        elif syllable1.tonic and not syllable2.tonic:
            # 1.3.	V1i/u+V́2 → hiat (canti himnes)
            if vocal1['alta']:
                score -= 1
            # 1.4.	V1e/o+V́2 → hiat (l’ego omple)
            elif not vocal1['alta']:
                score -= 1
            # 1.5.	V1ə+V́2i/u → hiat (terra útil)
            elif vocal1['neutra'] and vocal2['alta']:
                score -= 1

        # -------- Diftongs (score > 0) -------

        elif syllable1.tonic and syllable2.tonic:
            # 2.1.1.	V́1i/u+V́2i/u → diftong (sentir una cançó)
            if vocal1['alta'] and vocal2['alta']:
                score += 1
            # 2.1.1.2.	V́1(no-tancada)+V́2(no-tancada) → diftong (va portar herbes salvatges)
            elif not vocal1['alta'] and not vocal2['alta']:
                score += 1
            # 2.1.1.3.	V́1(no-tancada)+V́2i/u → diftong (va cantar himnes antiquats)
            elif not vocal1['alta'] and vocal2['alta']:
                score += 1
        elif syllable1.tonic and not syllable2.tonic:
            # 2.1.2.	V́1+V2i/u → diftong (va explicar idees)
            if not vocal1['alta'] and vocal2['alta']:
                score += 1
        elif not syllable1.tonic and syllable2.tonic:
            #  2.1.3.	V1i/u+ V́2 → diftong (que vingui ara mateix)
            if vocal1['alta'] and not vocal2['alta']:
                score += 1
        elif not syllable1.tonic and not syllable2.tonic:
            # 2.1.4.	V1(i/u)+V2 → diftong (compri-ho)
            if vocal1['alta'] and not vocal2['alta']:
                score += 1
            # 2.1.5. V1(no-alta)+V2(i/u) → diftong (camina-hi)
            elif not vocal1['alta'] and vocal2['alta']:
                score += 1

            # -------- Elisions (score > 3) --------
            # 3.1.	V1i/u=V2i/u → elisió (vegi insectes)
            if vocal1['alta'] and vocal2['alta'] and vocal1['vocal'] == vocal2['vocal']:
                score += 3
            # 3.2.	ə+ə → elisió (compta estrelles)
            elif vocal1['neutra'] and vocal2['neutra']:
                score += 3
            # 3.3.	V1+ə → elisió o diftong (dormi aviat)
            elif vocal2['neutra']:
                score += 3
            # 3.5.	ə+V2i/u → diftong o elisió (casa inhòspita)
            elif vocal1['neutra'] and vocal2['alta']:
                score += 3

        # 3.4.	ə+V́2(no-tancada) → elisió (casa alta)
        elif not syllable1.tonica and syllable2.tonica:
            if vocal1['neutra'] and not vocal2['alta']:
                score += 3
            elif vocal2['neutra']:
                score += 3
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


    best = get_best(best_mode)

    if best is not None and self.recompte_sillabes_metriques > self.objectiu: # Si hi ha contactes vocals i el recompte mètric no coincideix amb l'objectiu
        diff = self.recompte_sillabes_metriques - self.objectiu # Calcula la diferència
        while diff > 0 and best: # Mentre hi hagi diferència i hi hagi contactes vocals candidats
            #change = best.pop(0) # Treu el primer contacte vocal candidat
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
                            #print(f'Mètode 1: {word.text} + {next_word.text}')  # Debug
                            next_word.stress[0] = result
                            del self.words[wi]
                        elif word.n_syllables == 1 and next_word.n_syllables > 1:
                            """Mètode 2: un monosíl·lab i un polisíl·lab"""
                            #print(f'Mètode 2: {word.text} + {next_word.text}')  # Debug
                            next_word.stress[0] = result
                            next_word.stress_index = next_word.get_stress_index()
                            next_word.n_syllables = len(next_word.stress)
                            del self.words[wi]
                        elif word.n_syllables > 1 and next_word.n_syllables == 1:
                            """Mètode 3: un polisíl·lab i un monosíl·lab"""
                            #print(f'Mètode 3: {word.text} + {next_word.text}')  # Debug
                            word.stress[-1] = result
                            word.stress_index = word.get_stress_index()
                            word.n_syllables = len(word.stress)
                            del self.words[wi + 1]
                        elif word.n_syllables > 1 and next_word.n_syllables > 1:
                            """Mètode 4: dos polisíl·labs"""
                            #print(f'Mètode 4: {word.text} + {next_word.text}')  # Debug
                            word.stress[-1] = result
                            word.stress[-1].ends_with_vowel = word.stress[-1].vowel_end()
                            word.n_syllables = len(word.stress)
                            del next_word.stress[0]
                            word.stress_index = word.get_stress_index()
                            next_word.stress_index = next_word.get_stress_index()
                            next_word.stress[0].starts_with_vowel = next_word.stress[0].vowel_start()
                            next_word.n_syllables = len(next_word.stress)
                            if not word.stress: # Si la paraula no té síl·labes, s'elimina
                                del self.words[wi]
                                wi -= 1
                                continue
                        self.nomes_sillabes = sum([w.stress for w in self.words], []) # Actualitza la llista de síl·labes
                        self.recompte_sillabes_metriques = recompte_metric(self) # Actualitza el recompte de síl·labes mètriques
                        diff = self.recompte_sillabes_metriques - self.objectiu # Actualitza la diferència
                wi += 1 # Incrementa el comptador de paraules
        #print(f'Len(best): {len(best)}, Diff: {diff}')  # Debug


def contactes_vocalics_info(self):
    clean = deepcopy(self.escansio_text)
    dic_clean = {"[aàáâ]": "a", "[eèéê]": "e", "[iíìïyýÿî]": "i", "[oòóô]": "o", "[uúùüû]": "u", "[AÀÁÂ]": "A",
                 "[EÈÉÊ]": "E", "[IÍÌÏYÝŸÎ]": "I", "[OÒÓÔ]": "O", "[UÚÙÜÛ]": "U"}
    for key, value in dic_clean.items():
        clean = re.sub(key, value, clean)

    hiats_a_fm = re.findall(r"[aeiou]#[aeiou]", clean)
    hiats_a_m = re.findall(r"[aeiou]\.[aeiou]", clean)
    hiats_t_fm = re.findall(r"[AEIOUaeiou]#[AEIOU]", clean) + re.findall(r"[AEIOU]#[AEIOUaeiou]", clean)
    hiats_t_m = re.findall(r"[AEIOUaeiou]\.[AEIOU]", clean) + re.findall(r"[AEIOU]\.[AEIOUaeiou]", clean)
    diftong_a_fm = re.findall(r"[aeiou]_[aeiou]", clean)
    diftong_a_m = re.findall(r"[aeiou][aeiou]", clean)
    diftong_t_fm = re.findall(r"[AEIOUaeiou]_[AEIOU]", clean) + re.findall(r"[AEIOU]_[AEIOUaeiou]", clean)
    diftong_t_m = re.findall(r"[AEIOUaeiou][AEIOU]", clean) + re.findall(r"[AEIOU][AEIOUaeiou]", clean)
    triftong_a_fm = re.findall(r"[aeiou]_[aeiou]_[aeiou]", clean)
    triftong_a_m = re.findall(r"[aeiou][aeiou][aeiou]", clean)
    triftong_t_fm = re.findall(r"[AEIOUaeiou]_[AEIOU]_[AEIOU]", clean) + re.findall(r"[AEIOU]_[AEIOUaeiou]_[AEIOU]",
                                                                                    clean) + re.findall(
        r"[AEIOU]_[AEIOU]_[AEIOUaeiou]", clean) + re.findall(r"[AEIOUaeiou]_[AEIOU]_[AEIOUaeiou]", clean)
    triftong_t_m = re.findall(r"[AEIOUaeiou][AEIOU][AEIOU]", clean) + re.findall(r"[AEIOU][AEIOUaeiou][AEIOU]",
                                                                                 clean) + re.findall(
        r"[AEIOU][AEIOU][AEIOUaeiou]", clean) + re.findall(r"[AEIOUaeiou][AEIOU][AEIOUaeiou]", clean)

    return {"hiats_a_fm": hiats_a_fm, "hiats_a_m": hiats_a_m, "hiats_t_fm": [x.lower() for x in hiats_t_fm],
            "hiats_t_m": [x.lower() for x in hiats_t_m],
            "diftong_a_fm": diftong_a_fm, "diftong_a_m": diftong_a_m,
            "diftong_t_fm": [x.lower() for x in diftong_t_fm],
            "diftong_t_m": [x.lower() for x in diftong_t_m], "triftong_a_fm": triftong_a_fm,
            "triftong_a_m": triftong_a_m,
            "triftong_t_fm": [x.lower() for x in triftong_t_fm], "triftong_t_m": [x.lower() for x in triftong_t_m]}


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
    #print('> Candidats sineresi:', [(x.text, y.text, z) for x, y, z in candidats])  # Debug
    return candidats