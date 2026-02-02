"""Un mòdul per a gestionar funcions de distribució de mots per vers"""


def safe_words(self):
    """Aquesta funció elimina les paraules sense síl·laba tònica del vers.
    Returns:
        bool: True si s'han eliminat paraules, False en cas contrari.
    """
    for word in self.words:
        if word.n_syllables == 0:
            self.words.remove(word)
    return True


def quants_mots(self):
    """Aquesta funció retorna el nombre de mots del vers per còlon.
    Returns:
        tuple: (nombre de mots abans del tall, nombre de mots després del tall o None si no hi ha tall)
    """
    h1 = len(self.words)
    h2 = None
    for word in self.words:
        if word.paraula_tall:
            h1 = word.w_index + 1
            h2 = len(self.words) - h1
            return h1, h2
    return h1, h2
