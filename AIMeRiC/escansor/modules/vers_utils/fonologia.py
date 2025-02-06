import re
from copy import deepcopy

from AIMeRiC.escansor.modules.syllable import Syllable


def max_pes(syllable1, syllable2) -> int:
    if int(syllable1.pes) > int(syllable2.pes):
        return syllable1.pes
    else:
        return syllable2.pes


def vowel_sum(syllable1, syllable2):
    """Aquesta funció resol els casos de contacte vocàlic segons Vallverdú"""

    # un cas concret meu: infinitiu + pronoms febles
    if syllable1.ends_with_vowel and syllable1.fono_info['rotica']:
        if syllable2.text[0] == '-':
            return syllable1, syllable2, "hiat"
    if syllable1.ends_with_vowel and syllable2.starts_with_vowel:
        vocal1 = syllable1.fono_info
        vocal2 = syllable2.fono_info
        # 1. HIATS
        if int(syllable1.pes) > 2 and syllable1.pes == syllable2.pes:
            # 1.1.	V́1≠V́2 → hiat (voler homes)
            if vocal1['vocal'] != vocal2['vocal']:
                return syllable1, syllable2, "hiat"
            # 1.2.	V́1=V́2 → hiat (menjar algues)
            elif vocal1['vocal'] == vocal2['vocal']:
                return syllable1, syllable2, "hiat"
        elif int(syllable1.pes) < 2 < int(syllable2.pes):
            # 1.3.	V1i/u+V́2 → hiat (canti himnes)
            if vocal1['alta']:
                return syllable1, syllable2, "hiat"
            # 1.4.	V1e/o+V́2 → hiat (l’ego omple)
            elif not vocal1['alta']:
                return syllable1, syllable2, "hiat"
            # 1.5.	V1ə+V́2i/u → hiat (terra útil)
            elif vocal1['neutra'] and vocal2['alta']:
                return syllable1, syllable2, "hiat"



        # 2. DIFTONGS
        # 2.1.1.	V́1+V́2
        elif 2 < int(syllable1.pes) < 5 and 2 < int(syllable2.pes) < 5:
            # 2.1.1.1.	V́1i/u+V́2i/u → diftong (sentir una cançó)
            if vocal1['alta'] and vocal2['alta']:
                diftong = Syllable(index=syllable1.s_index,
                                   syllable=(f"{syllable1.text}_{syllable2.text}", f"{max_pes(syllable1, syllable2)}"),
                                   len_word=syllable1.len_word)
                diftong.pes_fusion = f'{syllable1.pes}_{syllable2.pes}'
                return diftong, "diftong"
            # 2.1.1.2.	V́1(no-tancada)+V́2(no-tancada) → diftong (va portar herbes salvatges)
            elif not vocal1['alta'] and not vocal2['alta']:
                diftong = Syllable(index=syllable1.s_index,
                                   syllable=(f"{syllable1.text}_{syllable2.text}", f"{max_pes(syllable1, syllable2)}"),
                                   len_word=syllable1.len_word)
                diftong.pes_fusion = f'{syllable1.pes}_{syllable2.pes}'
                return diftong, "diftong"
            # 2.1.1.3.	V́1(no-tancada)+V́2i/u → diftong (va cantar himnes antiquats)
            elif not vocal1['alta'] and vocal2['alta']:
                diftong = Syllable(index=syllable1.s_index,
                                   syllable=(f"{syllable1.text}_{syllable2.text}", f"{max_pes(syllable1, syllable2)}"),
                                   len_word=syllable1.len_word)
                diftong.pes_fusion = f'{syllable1.pes}_{syllable2.pes}'
                return diftong, "diftong"
        elif 5 > int(syllable1.pes) > 2 > int(syllable2.pes):
            # 2.1.2.	V́1+V2i/u → diftong (va explicar idees)
            if not vocal1['alta'] and vocal2['alta']:
                diftong = Syllable(index=syllable1.s_index,
                                   syllable=(f"{syllable1.text}_{syllable2.text}", f"{max_pes(syllable1, syllable2)}"),
                                   len_word=syllable1.len_word)
                diftong.pes_fusion = f'{syllable1.pes}_{syllable2.pes}'
                return diftong, "diftong"
        elif int(syllable1.pes) < 2 < int(syllable2.pes) < 5:
            # 2.1.3.	V1i/u+ V́2 → diftong (que vingui ara mateix)
            if vocal1['alta'] and not vocal2['alta']:
                diftong = Syllable(index=syllable1.s_index,
                                   syllable=(f"{syllable1.text}_{syllable2.text}", f"{max_pes(syllable1, syllable2)}"),
                                   len_word=syllable1.len_word)
                diftong.pes_fusion = f'{syllable1.pes}_{syllable2.pes}'
                return diftong, "diftong"
        elif int(syllable1.pes) < 2 and int(syllable2.pes) < 2:
            # 2.1.4.	V1(i/u)+V2 → diftong (compri-ho)
            if vocal1['alta'] and not vocal2['alta']:
                diftong = Syllable(index=syllable1.s_index,
                                   syllable=(f"{syllable1.text}_{syllable2.text}", f"{max_pes(syllable1, syllable2)}"),
                                   len_word=syllable1.len_word)
                diftong.pes_fusion = f'{syllable1.pes}_{syllable2.pes}'
                return diftong, "diftong"
            # 2.1.5. V1(no-alta)+V2(i/u) → diftong (camina-hi)
            elif not vocal1['alta'] and vocal2['alta']:
                diftong = Syllable(index=syllable1.s_index,
                                   syllable=(f"{syllable1.text}_{syllable2.text}", f"{max_pes(syllable1, syllable2)}"),
                                   len_word=syllable1.len_word)
                diftong.pes_fusion = f'{syllable1.pes}_{syllable2.pes}'
                return diftong, "diftong"

            # 3. ELISIONS
            # 3.1.	V1i/u=V2i/u → elisió (vegi insectes)
            elif vocal1['alta'] and vocal2['alta'] and vocal1['vocal'] == vocal2['vocal']:
                elisio = Syllable(index=syllable1.s_index,
                                  syllable=(f"{syllable1.text}:{syllable2.text}", f"{max_pes(syllable1, syllable2)}"),
                                  len_word=syllable1.len_word)
                elisio.pes_fusion = f'{syllable1.pes}_{syllable2.pes}'
                return (elisio, "elisió")
            # 3.2.	ə+ə → elisió (compta estrelles)
            elif vocal1['neutra'] and vocal2['neutra']:
                elisio = Syllable(index=syllable1.s_index,
                                  syllable=(f"{syllable1.text}:{syllable2.text}", f"{max_pes(syllable1, syllable2)}"),
                                  len_word=syllable1.len_word)
                elisio.pes_fusion = f'{syllable1.pes}_{syllable2.pes}'
                return (elisio, "elisió")
            # 3.3.	V1+ə → elisió o diftong (dormi aviat)
            elif vocal2['neutra']:
                elisio = Syllable(index=syllable1.s_index,
                                  syllable=(f"{syllable1.text}:{syllable2.text}", f"{max_pes(syllable1, syllable2)}"),
                                  len_word=syllable1.len_word)
                elisio.pes_fusion = f'{syllable1.pes}_{syllable2.pes}'
                return (elisio, "elisió")
        # 3.4.	ə+V́2(no-tancada) → elisió (casa alta)
        elif int(syllable1.pes) < 2 and int(syllable2.pes) > 2:
            if vocal1['neutra'] and not vocal2['alta']:
                elisio = Syllable(index=syllable1.s_index,
                                  syllable=(f"{syllable1.text}:{syllable2.text}", f"{max_pes(syllable1, syllable2)}"),
                                  len_word=syllable1.len_word)
                elisio.pes_fusion = f'{syllable1.pes}_{syllable2.pes}'
                return (elisio, "elisió")
        # 3.5.	ə+V2i/u → diftong o elisió (casa inhòspita)
        elif int(syllable1.pes) < 2 and int(syllable2.pes) < 2:
            if vocal1['neutra'] and vocal2['alta']:
                elisio = Syllable(index=syllable1.s_index,
                                  syllable=(f"{syllable1.text}:{syllable2.text}", f"{max_pes(syllable1, syllable2)}"),
                                  len_word=syllable1.len_word)
                elisio.pes_fusion = f'{syllable1.pes}_{syllable2.pes}'
                return (elisio, "elisió")


def force_sum(syllable1, syllable2):
    """Aquesta funció resol els casos de contacte vocàlic forçat"""
    if syllable1.ends_with_vowel and syllable2.starts_with_vowel:
        syllable1.text = f"{syllable1.text}_{syllable2.text}"
        syllable1.pes_fusion = f"{syllable1.pes}_{syllable2.pes}"
        syllable1.pes = syllable1.pes if int(syllable1.pes) > int(syllable2.pes) else syllable2.pes
        syllable1.fusion_direction = "dreta" if int(syllable1.pes) > int(syllable2.pes) else "esquerra"
        # syllable1.pes = f"{syllable1.pes}_{syllable2.pes}"
        syllable1.fusionada = True
        if not re.findall(r"[aeiouyàáèéìíòóùú]", syllable1.text[-1]):
            syllable1.ends_with_vowel = False
        return syllable1, "sinalefa"


def force_subs(syllable, mode=None):
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
            return syllabe1, syllabe2, "dialefa"
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
            return syllabe1, syllabe2, "dialefa"


def new_sumvow(self):
    len_words = len(self.words)
    i = 0
    while i < len_words - 1:
        word1_syll = self.words[i].stress[-1]
        word2_syll = self.words[i + 1].stress[0]
        result = vowel_sum(word1_syll, word2_syll)
        if result is not None:
            if result[1] == 'diftong' or result[1] == 'elisió':
                if self.words[i].n_syllables == 1 and self.words[i + 1].n_syllables == 1:
                    """Mètode 1: dos mots monosil·làbics"""
                    # print("Mètode 1")
                    self.words[i + 1].stress[0] = result[0]
                    del self.words[i]
                    self.words[i].stress[0].fusion_direction = "1"
                    self.words[i].stress[0].fusionada = True
                    len_words -= 1
                    i -= 1

                elif self.words[i].n_syllables == 1 and self.words[i + 1].n_syllables > 1:
                    """Mètode 2: monosil·lab i polisil·lab"""
                    # print("Mètode 2")
                    self.words[i + 1].stress[0] = result[0]
                    self.words[i + 1].stress[0].fusion_direction = "2"
                    self.words[i + 1].stress[0].fusionada = True
                    del self.words[i]

                    len_words -= 1
                    i -= 1

                elif self.words[i].n_syllables > 1 and self.words[i + 1].n_syllables == 1:
                    """Mètode 3: polisil·lab i monosil·lab"""
                    # print("Mètode 3")
                    self.words[i].stress[-1] = result[0]
                    self.words[i].stress[-1].fusion_direction = "3"
                    self.words[i].stress[-1].fusionada = True
                    del self.words[i + 1]
                    len_words -= 1
                    i -= 1

                elif self.words[i].n_syllables > 1 and self.words[i + 1].n_syllables > 1:
                    """Mètode 4: dos polisil·labs"""
                    # print("Mètode 4")
                    self.words[i + 1].stress[0] = result[0]
                    self.words[i + 1].stress[0].fusion_direction = "4"
                    self.words[i + 1].stress[0].fusionada = True
                    del self.words[i].stress[-1]

        i += 1


def cv_get_info(self):
    clean = deepcopy(self.string_stress)
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
