import requests, sys
baseUrl = "https://pokeapi.co/"

def determineTypesByPoke(teamWithTypes):
    typesByPoke = {}
    for poke in teamWithTypes:
        print("Finding type info for \"{}\"".format(poke))
        typesByPoke[poke] = []
        for typeDef in teamWithTypes[poke]:
            typeAttributes = typeDef["type"]
            typeName = typeAttributes["name"]
            typeUrl = typeAttributes["url"]
            
            print("\tFinding type \"{}\"".format(typeName))
            try:
                response = requests.get(typeUrl)
            except requests.exceptions.ConnectionError as error:
                print("determineTypesByPoke(teamWithTypes) Error: exception {} for type \"{}\" for Pokemon \"{}\"".format(error, typeName, poke))
            
            if response.status_code != requests.codes.ok:
                print("determineTypesSummation(teamWithTypes, typesByPoke) Error: status code {} for type \"{}\" for Pokemon \"{}\"".format(response.status_code, typeName, poke))
            
            else:
                jResponse = response.json()
                dTypeInfo = {}
                dTypeInfo["name"] = jResponse["name"]
                dTypeInfo["damage_relations"] = jResponse["damage_relations"]
                typesByPoke[poke].append(dTypeInfo)
    
    return typesByPoke


def intro():
    print("****Weakness Subset Calculator****")

def promptForTeam():
    team = []
    print("Please enter the Pokemon to analyze, one at a time.\n"
            + "When finished, hit Enter with nothing typed.")

    curPoke = "blank"
    while curPoke != "":
        curPoke = input()
        if curPoke != "":
            team.append(curPoke)

    return team

def getTypes(team):
    url = baseUrl + "api/v2/pokemon/{}"
    teamWithTypes = {}
    for poke in team:
        print("Retrieving {}...".format(poke))
        lPoke = str.lower(poke)
        
        try:
            response = requests.get(url.format(lPoke))
        except requests.exceptions.ConnectionError as error:
            print("getTypes(team) Error: exception {} for Pokemon \"{}\"".format(error, poke))
            break

        if response.status_code != requests.codes.ok:
            print("getTypes(team) Error: status code {} for Pokemon \"{}\"".format(
                response.status_code, poke))
            break

        jResponse = response.json()

        curTypes = jResponse["types"]

        teamWithTypes[poke] = curTypes

    return teamWithTypes

def teamsAndTypesMatch(team, teamWithTypes):
    return len(team) == len(teamWithTypes)

intro()
team = promptForTeam()

teamWithTypes = getTypes(team)
if teamsAndTypesMatch(team, teamWithTypes):
    typesByPoke = determineTypesByPoke(teamWithTypes)

    print(typesByPoke)

else:
    print("teamsAndTypesMatch(team, teamWithTypes) Error: len(team) = {} != len(teamWithTypes) = {}".format(len(team), len(teamWithTypes)))


