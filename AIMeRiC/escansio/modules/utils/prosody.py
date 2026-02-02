"""Un mòdul per gestionar funcions prosòdiques del vers"""
from .meter import recompte_metric


def accents_prosodics(self):
    """
    Ajusta els accents prosòdics de les síl·labes del vers segons regles específiques.
    Args:
        self: Objecte que conté les síl·labes i paraules del vers.
    Returns:
        None: Modifica les síl·labes in situ.
    """

    def iterate_no_words(self):
        """
        Funció generadora per iterar sobre les síl·labes sense considerar les paraules.

        Yields:
            tuple: Una tupla amb la síl·laba anterior, la síl·laba actual, la síl·laba següent i la síl·laba anterior a l'anterior.
        """
        for i in range(len(self.nomes_sillabes)):
            current_value = self.nomes_sillabes[i]
            previous_value = self.nomes_sillabes[i - 1] if i > 0 else None
            previous_previous_value = self.nomes_sillabes[i - 2] if i > 1 else None
            next_value = self.nomes_sillabes[i + 1] if i < len(self.nomes_sillabes) - 1 else None
            yield previous_value, current_value, next_value, previous_previous_value

    def change_pes(current_value, pes: float):
        """
        Canvia el pes d'una síl·laba i actualitza les paraules corresponents.

        Args:
            current_value: La síl·laba actual.
            pes (float): El nou pes a assignar.
        Returns:
            None: Modifica la síl·laba i les paraules in situ.
        """
        current_value.pes = pes
        for word in self.words:
            if current_value in word.stress:
                word.stress[word.stress.index(current_value)].pes = pes

    # Itera les síl·labes
    for prev, curr, next, prevprev in iterate_no_words(self):
        # print(f'prev: {prev.text if prev else None} ({prev.pes if prev else None}), curr: {curr.text} ({curr.pes}), next: {next.text if next else None} ({next.pes if next else None})')  # Debug
        # Si la síl·laba actual és la primera i hi ha una síl·laba següent
        if prev is None and next is not None:
            if curr.pes == next.pes:
                change_pes(curr, 0.0)  # Canvia el pes de la síl·laba actual a '0' (àtona) xX
            if curr.pes < 2.0:  # Si el pes és menor a 2, canvia'l a 0.0 xX
                change_pes(curr, 0.0)
            if 1.0 < curr.pes < 5.0:  # Si el pes està entre 1 i 5
                # Canvia el pes de la síl·laba amb el pes més baix a '1' (desaccentuada) Xx/xX
                if next.pes > 2.0:
                    change_pes(next if curr.pes >= next.pes else curr, 1.0)
                elif next.pes <= 2.0:
                    change_pes(next if curr.pes >= next.pes else curr, 0.0)

        # Si la síl·laba actual és la darrera i hi ha una síl·laba anterior
        elif next is None and prev is not None:
            if 1.0 < curr.pes < 5.0:  # Si el pes està entre 1 i 5
                # Canvia el pes de la síl·laba amb el pes més baix a '1' (desaccentuada) Xx/xX
                change_pes(curr if prev.pes > curr.pes else prev, 1.0)

        # Si la síl·laba és entre dues síl·labes (xXx)
        elif prev is not None and next is not None:
            if 2.0 < curr.pes < 5.0:  # Si la síl·laba actual té un pes menor que 5 però major que 2
                if next.pes > 2.0:  # Si la síl·laba següent té un pes major que 2
                    change_pes(curr if next.pes >= curr.pes else next, 1.0)  # Canvia el pes de la síl·laba amb el pes més baix a '1' (desaccentuada) Xx/xX
                elif 2.0 < prev.pes < 5.0:  # Si la síl·laba anterior té un pes major que 2 però menor que 5
                    change_pes(curr if prev.pes > curr.pes else prev, 1.0)  # Canvia el pes de la síl·laba amb el pes més baix a '1' (desaccentuada) xX/xX
            elif curr.pes == 2.0:  # Si la síl·laba actual té un pes igual a 2
                if 1.0 < next.pes < 2.0:  # Si la síl·laba següent té un pes entre 1 i 2
                    change_pes(next, 0.0)  # Canvia el pes de la síl·laba següent a '0' (àtona) Xx
                elif 1.0 < prev.pes < 2.0:  # Si la síl·laba anterior té un pes entre 1 i 2
                    change_pes(prev, 0.0)  # Canvia el pes de la síl·laba anterior a '0' (àtona) xX
                elif next.pes > 2.0:  # Si la síl·laba següent té un pes major que 2
                    change_pes(curr, 0.75)  # Canvia el pes de la síl·laba actual a '1' (desaccentuada) xX
                elif prev.pes > 2.0:  # Si la síl·laba anterior té un pes major que 2
                    change_pes(curr, 0.0)  # Canvia el pes de la síl·laba actual a '0' (àtona) Xx
                elif next.pes == 2:  # Resol dos accents secundaris consecutius
                    change_pes(curr, 0.75)
            if curr.pes == 4.0 and next.pes == 5.0:  # Si la síl·laba actual té un pes igual a 4 i la següent igual a 5
                change_pes(curr, 1.0)  # Canvia el pes de la síl·laba actual a '1' (desaccentuada) xX/xX

    # Itera les síl·labes i resol els casos de síl·labes desaccentuades entre síl·labes àtones
    for prev, curr, next, prevprev in iterate_no_words(self):
        if prevprev is not None and next is not None:  # Si hi ha una síl·laba abans de l'anterior i una després de la actual
            if prevprev.pes == 1.0 and prev.pes == 1.0 and curr.pes == 1.0 and next.pes < 1:  # Si les dues síl·labes anteriors són àtones i la actual és desaccentuada i la següent és àtona
                # Canvia el pes de la síl·laba actual a '2' (accent secundari) xxXx
                change_pes(curr, 2.0)
        if prev is not None and next is not None:  # Si hi ha una síl·laba anterior i una següent
            if prev.pes == 1.0 and curr.pes == 1.0 and next.pes > 1.0:  # Si la síl·laba anterior i l'actual són desaccentuades i la següent és forta
                #if next.pes < 5.0:  # Si la síl·laba següent és menys que un cim accentual (permet mantenir els xocs tipus jo M'HI sent NAT)
                #    change_pes(curr, 0.0)  # Canvia el pes de la síl·laba actual a '0' (àtona) xxX
                change_pes(prev, 2.0)  # Canvia el pes de la síl·laba anterior a '2' (accent secundari) XxX
            if curr.pes > 2.0 and next.pes == 1.0:  # Si la síl·laba actual és forta i la següent és desaccentuada
                change_pes(next, 0.0)  # Canvia el pes de la síl·laba posterior a '0' (àtona) 41 > 40
            if prev.pes == 1.0 and curr.pes == 1.0 and next.pes < 1.0:  # Si la síl·laba anterior i la següent són àtones i la actual és desaccentuada
                change_pes(curr, 2.0)  # Canvia el pes de la síl·laba actual a '2' (accent secundari) xXx

            if prev.pes < 1 and curr.pes == 1.0 and next.pes < 1:  # Resol els casos de síl·labes desaccentuades entre dues síl·labes àtones xXx
                change_pes(curr, 2.0)

            if prev.pes < 1.0 and curr.pes < 1.0 and next.pes < 1.0:  # Resol valls accentuals que es poden resoldre amb un accent secundari
                for word in self.words:
                    if curr in word.stress:
                        if word.bivalent:
                            if word.stress_index == curr.s_index:
                                change_pes(curr, 2.0)
                                break
        elif prev is not None and next is None:  # Si hi ha una síl·laba anterior però no una següent
            if prev.pes < 1.0 and curr.pes == 1.0:  # Si la síl·laba anterior és àtona i l'actual és desaccentuada
                change_pes(curr, 0.0)  # Canvia el pes de la síl·laba actual a '0' (àtona) xx

    # Resol els casos de síl·labes desaccentuades entre dues síl·labes àtones xXx
    for prev, curr, next, prevprev in iterate_no_words(self):
        if prev is not None and next is not None:
            if curr.pes == 1.0 and prev.pes == 0.0 and next.pes == 0.0:
                change_pes(curr, 2.0)
            if prev.pes == 0 and curr.pes == 0.75 and next.pes < 2: # Resol els casos d'accent secundari en contacte amb síl·laba desaccentuada
                change_pes(curr, 2.0)


def cim_maxim(self):
    """Substitutes maximum peaks (>=2) with superior peaks (5) in the last strong syllable of each colon."""
    sense_mots = self.nomes_sillabes
    last_sil = self.objectiu - 1
    try:
        if sense_mots[last_sil].pes > 2.0:
            for word in self.words:
                if sense_mots[last_sil] in word.stress:
                    # Substitueix el pes de la síl·laba per 5.0
                    word.stress[word.stress.index(sense_mots[last_sil])].pes = 5.0
                    self.nomes_sillabes[last_sil].pes = 5.0
                    self.patro[last_sil] = 5.0
            # Si hi ha més síl·labes després de last_sil (possiblement entre 0 i 3)
            if len(sense_mots) > last_sil + 1:
                # Ajusta el pes de la següent síl·laba a 0.0
                word_index = None
                for word in self.words:
                    if sense_mots[last_sil] in word.stress:
                        word_index = self.words.index(word)
                        break
                if word_index is not None and word_index + 1 < len(self.words):
                    next_word = self.words[word_index + 1]
                    if next_word.stress:
                        next_word.stress[0].pes = 0.0
                        self.nomes_sillabes[last_sil + 1].pes = 0.0
                        self.patro[last_sil + 1] = 0.0

            # Actualitza els recomptes mètrics i extramètrics
            self.recompte_sillabes_metriques = recompte_metric(self)
            self.recompte_sillabes_extrametriques = len(self.patro) - self.recompte_sillabes_metriques

        elif sense_mots[last_sil].pes == 1.0:
            for word in self.words:
                if sense_mots[last_sil] in word.stress:
                    # Assigna un pes de 0.0 (àtona) a la síl·laba
                    word.stress[word.stress.index(sense_mots[last_sil])].pes = 0.0
                    self.nomes_sillabes[last_sil].pes = 0.0
                    self.patro[last_sil] = 0.0


            # Actualitza els recomptes mètrics i extramètrics
            self.recompte_sillabes_metriques = recompte_metric(self)
            self.recompte_sillabes_extrametriques = len(self.patro) - self.recompte_sillabes_metriques
    except IndexError:
        pass