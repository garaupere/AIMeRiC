def agrupa_peus_colons(seq:str, model:str):
    from functools import lru_cache

    peus = [
        ('(001)', "001", 1),   # anapest
        ('(01)',  "01",  2),   # iambe
        ('(10)',  "10",  3),   # troqueu
        ('(010)', "010", 4),   # amfíbrac
        ('(100)', "100", 5),   # dàctil
        ('(1)',   "1",   6),   # degenerat
    ]
    prio_dict = {p[0]: p[2] for p in peus}

    def sil_labes(u):
        if u == "0": return 1
        return sum(1 for c in u if c in "01")

    def totes_les_agrupacions(bits):
        @lru_cache(maxsize=None)
        def rec(i):
            if i == len(bits): return [([], 0, 0, ())]
            opcions = []
            for nom, patro, prio in peus:
                l = len(patro)
                if i + l <= len(bits) and bits[i:i+l] == patro:
                    for llista, z, m, seq in rec(i + l):
                        opcions.append(([nom]+llista, z, m + (1 if nom == '(1)' else 0), (prio,)+seq))
            if bits[i] == "0":
                for llista, z, m, seq in rec(i + 1):
                    opcions.append((["0"] + llista, z+1, m, (99,)+seq))
            return opcions

        tot = rec(0)
        if not tot:
            return []
        # Restricció mínima: zeros, monosil·làbics
        min_zeros = min(x[1] for x in tot)
        tot = [x for x in tot if x[1] == min_zeros]
        min_mono = min(x[2] for x in tot)
        tot = [x for x in tot if x[2] == min_mono]
        # Aquí pots tenir diverses agrupacions igualment bones però que es diferencien en l'ordre (10) vs (01)
        # Per preferir lexicogràficament per la dreta (p.ex. [1,6,2] < [1,3,6]) cal ordenar per prio[::-1]
        tot.sort(key=lambda x: x[3][::-1])
        return tot

    # Si model és None, retorna els peus en un únic còlon
    if model is None:
        opcions = totes_les_agrupacions(seq)
        if not opcions:
            raise ValueError("Cap agrupació en peus vàlida")
        u = opcions[0][0]
        return f"[{''.join(u)}]"

    # Troba el tall sil·làbic
    if model == "4+6":
        n1, n2 = 4, 6
    elif model == "6+4":
        n1, n2 = 6, 4
    elif model == "5+5":
        n1, n2 = 5, 5
    else:
        raise ValueError("Estructura desconeguda")

    compte, tall = 0, None
    for i, c in enumerate(seq):
        compte += 1
        if compte == n1:
            tall = i + 1
            break
    if tall is None:
        raise ValueError("No es troba el tall mètric.")

    bits1 = seq[:tall]
    bits2 = seq[tall:]

    opcions1 = totes_les_agrupacions(bits1)
    if not opcions1: raise ValueError("Cap agrupació en peus vàlida pel còlon 1")
    u1 = opcions1[0][0]

    opcions2 = totes_les_agrupacions(bits2)
    if not opcions2: raise ValueError("Cap agrupació en peus vàlida pel còlon 2")
    u2 = opcions2[0][0]

    return f"[{''.join(u1)}][{''.join(u2)}]"



