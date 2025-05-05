import requests

def get_wikidata_id(name):
    """
    Obté el codi Wikidata d'una persona pel seu nom complet.
    :param name: Nom complet de la persona (str)
    :return: Codi de Wikidata (str) o None si no es troba
    """
    url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbsearchentities",
        "search": name,
        "language": "ca",
        "limit": 1,
        "format": "json"
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get("search"):
            return data["search"][0]["id"]
    return None

def get_person_info(wikidata_id):
    """
    Obté informació detallada d'una persona a partir del seu codi Wikidata.
    :param wikidata_id: Codi Wikidata de la persona (str)
    :return: Diccionari amb les informacions demanades
    """
    endpoint_url = "https://query.wikidata.org/sparql"
    query = f"""
    SELECT ?fullName ?birthYear ?deathYear ?genderLabel ?birthPlaceLabel ?birthPlaceProvinceLabel ?viafID WHERE {{
      wd:{wikidata_id} rdfs:label ?fullName.
      OPTIONAL {{ wd:{wikidata_id} wdt:P569 ?birthDate. }}
      OPTIONAL {{ wd:{wikidata_id} wdt:P570 ?deathDate. }}
      OPTIONAL {{ wd:{wikidata_id} wdt:P21 ?gender. }}
      OPTIONAL {{ wd:{wikidata_id} wdt:P19 ?birthPlace. }}
      OPTIONAL {{ ?birthPlace wdt:P131 ?birthPlaceProvince. }}
      OPTIONAL {{ wd:{wikidata_id} wdt:P214 ?viafID. }}
      FILTER(LANG(?fullName) = "ca")
      BIND(YEAR(?birthDate) AS ?birthYear)
      BIND(YEAR(?deathDate) AS ?deathYear)
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "ca". }}
    }}
    """

    headers = {"Accept": "application/json"}
    response = requests.get(endpoint_url, params={"query": query, "format": "json"}, headers=headers)
    if response.status_code == 200:
        try:
            data = response.json()
            bindings = data.get("results", {}).get("bindings", [])
            if bindings:
                result = bindings[0]
                return {
                    "name": result.get("fullName", {}).get("value"),
                    "gender": 0 if result.get("genderLabel", {}).get("value") in ["home", "masculí", "Home", "Masculí"] else 1 if result.get("genderLabel", {}).get("value") in ["dona", "femení", "Dona", "Femení"] else 2,
                    "born_date": result.get("birthYear", {}).get("value"),
                    "death_date": result.get("deathYear", {}).get("value", None),
                    "city": result.get("birthPlaceLabel", {}).get("value"),
                    "dialect": result.get("birthPlaceProvinceLabel", {}).get("value"),
                    "wiki_id": wikidata_id,
                    "viaf": result.get("viafID", {}).get("value"),
                    "books": {}
                }
        except ValueError:
            print("Error processing the response JSON.")
    return None

if __name__ == "__main__":
    nom_complet = input("Introdueix el nom i llinatges de la persona: ")
    wikidata_id = get_wikidata_id(nom_complet)
    if wikidata_id:
        info = get_person_info(wikidata_id)
        if info:
            print("Informació trobada:")
            for clau, valor in info.items():
                print(f"{clau}: {valor}")
        else:
            print("No s'ha trobat informació detallada per a aquesta persona.")
    else:
        print("No s'ha trobat cap codi Wikidata per a aquest nom.")