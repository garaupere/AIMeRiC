"""Un mòdul amb eines usades en l'etiquetatge del corpus"""
def aplica_filtre(dades, filtre):
    """Selecciona només les dades que presenten la subdivisió indicada"""
    return dades[dades['subdivisió'] == filtre]
