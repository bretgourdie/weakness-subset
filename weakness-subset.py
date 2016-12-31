import requests, sys
baseUrl = "https://pokeapi.co/"

def determineTypesSummation(teamWithTypes):
    typesSummation = {}
    for poke in teamWithTypes:
        typesSummation[poke] = []
        for typeDef in teamWithTypes[poke]:
            typeAttributes = typeDef["type"]
            typeName = typeAttributes["name"]
            typeUrl = typeAttributes["url"]
            
            response = requests.get(typeUrl)
            
            if response.status_code != 200:
                print("determineTypesSummation(teamWithTypes, typesSummation) Error: status code {} for type \"{}\" for Pokemon \"{}\"".format(typeName, poke))
            
            else:
                jResponse = response.json()
                curType = jResponse["name"]
                relations = jResponse["damage_relations"]
                typesSummation[poke].append(relations)
    
    return typesSummation


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
        response = requests.get(url.format(lPoke))
        
        if response.status_code != 200:
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
if not teamsAndTypesMatch(team, teamWithTypes):
    sys.exit("teamsAndTypesMatch(team, teamWithTypes) Error: len(team) = {} != len(teamWithTypes) = {}".format(len(team), len(teamWithTypes)))

typesSummation = determineTypesSummation(teamWithTypes)

print(typesSummation)
