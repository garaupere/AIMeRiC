"""Un mètode per gestionar la visualització de l'escansió"""
import re


def anota_vers(self):
    """
    Annotates each word in the verse with its syllables' text and weight.
    """
    return [{f"{word.text.lower()}_{word.w_index}": word.save_metadata()} for word in self.words]

def scansion_array(self):
    """
    Represents the scansion as an array of syllable weights.

    Returns:
        list: A list of lists where each inner list contains the weights of the syllables in a word.
    """
    return [[(syllable.text, int(syllable.pes), syllable.fusionada, syllable.fono_info) for syllable in word.stress] for
            word in self.words]


def escansio_plana(self):
    """
    Visualizes the scansion in a flat format.

    Returns:
        str: A string representation of the scansion where syllables in each word are joined by dots and words are joined by hashes.
    """
    return '#'.join(['.'.join([syllable.text for syllable in word.stress]) for word in self.words])


def escansio_accentual(self):
    """
    Visualizes the scansion in an accentual format.

    Returns:
        str: A string representation of the scansion where each word is represented by its syllables in uppercase for stressed and lowercase for unstressed, and words are joined by hashes.
    """

    return '#'.join(
        ['.'.join(
            [syllable.text.upper() if int(syllable.pes) > 1 else syllable.text.lower() for syllable in word.stress]) for
            word in self.words]).replace('_', '‿')


def metronome(self):
    """
    Generates a metrical pattern for the verse compatible with Metronome analysis.

    The pattern uses 'S' for stressed syllables, 'w' for unstressed syllables,
    '.' to separate words, and '|' to mark the end of the verse.

    Returns:
        str: A string representation of the metrical pattern.
    """
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
