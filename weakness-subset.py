import requests, sys
baseUrl = "https://pokeapi.co/"
sName = "name"
sDamage = "damage_relations"
sType = "type"
sTypes = "types"
sUrl = "url"
sHalf = "half_damage_from"
sDouble = "double_damage_from"
sNo = "no_damage_from"

def calculateWeaknessByPoke(typesByPoke):
    dWeaknessByPoke = {}

    for poke, typeInfo in typesByPoke.items():
        print("Calculating weaknesses for \"{}\"".format(poke))

        dPokeWeakness = {}

        for oneTypeInfo in typeInfo:
            name = oneTypeInfo[sName].lower()
            print("\tDetermining \"{}\" weaknesses/resistances...".format(name))

            dDamageRelations = oneTypeInfo[sDamage]

            for relation, lTypes in dDamageRelations.items():
                for dType in lTypes:
                    sFrom = dType[sName]

                    # initialize if not in matrix
                    if relation in [sHalf, sDouble, sNo] and sFrom not in dPokeWeakness:
                       dPokeWeakness[sFrom] = 1
                    if relation == sHalf:
                        dPokeWeakness[sFrom] /= 2
                    elif relation == sDouble:
                        dPokeWeakness[sFrom] *= 2
                    elif relation == sNo:
                        dPokeWeakness[sFrom] *= 0

        dWeaknessByPoke[poke] = dPokeWeakness

    return dWeaknessByPoke

def determineTypesByPoke(teamWithTypes):
    typesByPoke = {}
    for poke in teamWithTypes:
        print("Finding type info for \"{}\"".format(poke))
        typesByPoke[poke] = []
        for typeDef in teamWithTypes[poke]:
            typeAttributes = typeDef[sType]
            typeName = typeAttributes[sName]
            typeUrl = typeAttributes[sUrl]
            
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
                dTypeInfo[sName] = jResponse[sName]
                dTypeInfo[sDamage] = jResponse[sDamage]
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

        curTypes = jResponse[sTypes]

        teamWithTypes[poke] = curTypes

    return teamWithTypes

def teamsAndTypesMatch(team, teamWithTypes):
    return len(team) == len(teamWithTypes)

intro()
team = promptForTeam()

teamWithTypes = getTypes(team)
if teamsAndTypesMatch(team, teamWithTypes):
    typesByPoke = determineTypesByPoke(teamWithTypes)

    dByPoke = calculateWeaknessByPoke(typesByPoke)

else:
    print("teamsAndTypesMatch(team, teamWithTypes) Error: len(team) = {} != len(teamWithTypes) = {}".format(len(team), len(teamWithTypes)))


