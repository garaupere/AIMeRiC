def sillabes_fins_tonica(paraula):
    sillabes = paraula.split(".")
    ultima_tonica = -1

    for i, s in enumerate(sillabes):
        if any(c.isupper() for c in s):
            ultima_tonica = i

    if ultima_tonica == -1:
        return 0  # paraula sense síl·laba tònica marcada

    return ultima_tonica + 1


def cut_first10_to_text(text):
    paraules = text.split("#")
    resultat = []
    comptador = 0

    for p in paraules:
        num_sillabes = sillabes_fins_tonica(p)
        paraula_neta = p.replace(".", "").lower()

        resultat.append(paraula_neta)
        comptador += num_sillabes

        if comptador >= 10:
            break

    return " ".join(resultat).replace('‿', ' ')


def cut_last10_to_text(text):
    paraules = text.split("#")
    resultat = []
    comptador_sillabes = 0

    for p in reversed(paraules):
        sillabes = p.split(".")
        num_sillabes = len(sillabes)
        paraula_neta = "".join(sillabes)

        resultat.insert(0, paraula_neta.lower())
        comptador_sillabes += num_sillabes

        if comptador_sillabes >= 10:
            break

    return " ".join(resultat).replace('‿', ' ')


def sillabes_i_tonicitat(paraula):
    return [(s, any(c.isupper() for c in s)) for s in paraula.split(".")]


def extreure_10_sillabes_medials(text):
    paraules = text.split("#")
    n = len(paraules)

    # començam només en posicions internes
    for start in range(1, n - 1):
        comptador = 0

        for i in range(start, n):
            for s, es_tonica in sillabes_i_tonicitat(paraules[i]):
                comptador += 1

                if comptador == 10:
                    # la 10a ha de ser tònica
                    if not es_tonica:
                        break

                    # no pot acabar al final absolut
                    if i == n - 1:
                        break

                    resultat = [
                        paraules[j].replace(".", "").lower()
                        for j in range(start, i + 1)
                    ]
                    return " ".join(resultat).replace('‿', ' ')
            else:
                continue
            break

    return None
