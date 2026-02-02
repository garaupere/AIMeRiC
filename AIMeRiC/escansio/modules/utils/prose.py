

def sillabes_fins_tonica(paraula) -> int:
    sillabes = paraula.split(".")
    ultima_tonica = -1

    for i, s in enumerate(sillabes):
        if any(c.isupper() for c in s):
            ultima_tonica = i

    if ultima_tonica == -1:
        return 0  # paraula sense síl·laba tònica marcada

    return ultima_tonica + 1


def cut_first10_to_text(text) -> str:
    paraules = text.split("#")
    resultat = []
    comptador = 0

    for p in paraules:
        # Obtenir totes les síl·labes de la paraula
        sillabes = list(sillabes_i_tonicitat(p))
        num_sillabes = len(sillabes)
        paraula_neta = p.replace(".", "").lower()

        # Afegir la paraula al resultat
        resultat.append(paraula_neta)
        comptador += num_sillabes

        # Aturar quan la suma arribi o superi 10 síl·labes i assegurar que acaba un mot
        if comptador >= 10:
            # Assegurar que la 10a síl·laba és la darrera de la paraula
            darrera_sillaba_final = comptador == 10 or comptador - num_sillabes < 10
            if darrera_sillaba_final:
                break

    return " ".join(resultat).replace("‿", " ")


def cut_last10_to_text(text) -> str:
    paraules = text.split("#")
    resultat = []
    comptador_sillabes = 0

    for p in reversed(paraules):
        # Obtenir totes les síl·labes de la paraula
        sillabes = list(sillabes_i_tonicitat(p))  # Obtenim síl·labes i tonicitat
        num_sillabes = len(sillabes)
        paraula_neta = p.replace(".", "").lower()

        # Afegim la paraula al resultat
        resultat.insert(0, paraula_neta)
        comptador_sillabes += num_sillabes

        # Aturar quan la suma arribi o superi 10 síl·labes i assegurar que acaba un mot
        if comptador_sillabes >= 10:
            # Assegurar que la 10a síl·laba és la darrera d'una paraula
            darrera_sillaba_final = comptador_sillabes == 10 or comptador_sillabes - num_sillabes < 10
            if darrera_sillaba_final:
                break

    return " ".join(resultat).replace("‿", " ")


def sillabes_i_tonicitat(paraula) -> list[tuple[str, bool]]:
    return [(s, any(c.isupper() for c in s)) for s in paraula.split(".")]


def extreure_10_sillabes_medials(text) -> str | None:
    paraules = text.split("#")
    n = len(paraules)

    # Funció auxiliar per comptar el total de síl·labes
    def comptar_total_sillabes(paraules):
        total = 0
        for paraula in paraules:
            total += sum(1 for _, _ in sillabes_i_tonicitat(paraula))
        return total

    # Calcular el total de síl·labes i la posició inicial basada en la meitat (-10 síl·labes)
    total_sillabes = comptar_total_sillabes(paraules)
    posicio_mitja = max(1, (total_sillabes // 2) - 10)

    # Trobar el punt d'inici sense tallar paraules
    comptador = 0
    start = 0
    for i in range(n):
        sillabes_a_i = list(sillabes_i_tonicitat(paraules[i]))
        if comptador + len(sillabes_a_i) >= posicio_mitja:
            start = i
            break
        comptador += len(sillabes_a_i)

    # Extreure les 10 síl·labes sense tallar paraules
    comptador = 0
    resultat = []
    for i in range(start, n):
        sillabes_a_i = list(sillabes_i_tonicitat(paraules[i]))
        comptador += len(sillabes_a_i)
        resultat.append(paraules[i])
        if comptador >= posicio_mitja + 10:
            break

    # Verificació: la selecció acaba amb la darrera síl·laba d'un mot i no al final absolut
    if comptador < posicio_mitja + 10:
        return None  # No s'arriba a 10 síl·labes
    if i == n - 1:
        return None  # No pot acabar al final absolut

    return " ".join(p.replace(".", "").lower() for p in resultat).replace("‿", " ")
