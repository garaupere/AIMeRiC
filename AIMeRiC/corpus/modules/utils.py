"""Un mòdul amb eines usades en l'etiquetatge del corpus"""
def aplica_filtre(dades, filtre):
    """Selecciona només les dades que presenten la model indicada"""
    return dades[dades['model'] == filtre]
