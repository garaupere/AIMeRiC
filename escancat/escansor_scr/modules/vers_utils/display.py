"""Un mètode per gestionar la visualització de l'escansió"""


def anotate_verse(self):
    return [[(syllable.save_metadata()["text"], syllable.save_metadata()["pes"]) for syllable in word.stress] for word
            in self.words]


def escansio_plana(self):
    """Un mètode per a visualitzar l'escansió de forma plana"""
    return '#'.join(['.'.join([syllable.text for syllable in word.stress]) for word in self.words])


def escansio_accentual(self):
    return '#'.join([word.plain() for word in self.words])


def metronome(self):
    patro = []
    for word in self.words:
        for syllable in word.stress:
            if int(syllable.pes) > 1:
                patro.append('S')
            else:
                patro.append('w')
        patro.append('.')
    patro.append('|')
    return ''.join(patro)
