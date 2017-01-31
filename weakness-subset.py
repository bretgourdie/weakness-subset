import requests, operator, sys
baseUrl = "https://pokeapi.co/"
sName = "name"
sDamage = "damage_relations"
sType = "type"
sTypes = "types"
sUrl = "url"
sHalf = "half_damage_from"
sDouble = "double_damage_from"
sNo = "no_damage_from"
lAllTypes = ["normal",
             "fire",
             "fighting",
             "water",
             "flying",
             "grass",
             "poison",
             "electric",
             "ground",
             "psychic",
             "rock",
             "ice",
             "bug",
             "dragon",
             "ghost",
             "dark",
             "steel",
             "fairy"]

def rankWeaknesses(dWeaknessByPoke):
    dRankedSorted = {}

    for poke, dWeaknesses in dWeaknessByPoke.items():
        lSorted = sorted(dWeaknesses.items(), key=operator.itemgetter(1), reverse=True)
        dRankedSorted[poke] = lSorted

    return dRankedSorted

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

        print()
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

def quickFacts(dRankedWeaknessesByPoke):
    print("****Quick Facts!****")
    
    dImmuneTypesByPoke = getImmuneTypes(dRankedWeaknessesByPoke)
    printImmuneQuickFacts(dImmuneTypesByPoke)

    dFourTimesWeakByPoke = getFourTimesTypes(dRankedWeaknessesByPoke)
    printFourTimesQuickFacts(dFourTimesWeakByPoke)

    lUsefulTypes = getUsefulTypes(dRankedWeaknessesByPoke)
    printUsefulTypesQuickFacts(lUsefulTypes)

    lUselessTypes = getUselessTypes(dRankedWeaknessesByPoke)
    printUselessTypesQuickFacts(lUselessTypes)

def getTargetScore(dRankedWeaknessesByPoke, piScore):
    dTypesByPoke = {}

    for poke, lScoresByTypes in dRankedWeaknessesByPoke.items():
        lTypes = []

        for tScoreByType in lScoresByTypes:
            sType, iScore = tScoreByType

            if iScore == piScore and sType not in lTypes:
                lTypes.append(sType)

        if len(lTypes) > 0:
            dTypesByPoke[poke] = lTypes

    return dTypesByPoke

def printImmuneQuickFacts(dImmuneTypesByPoke):
    return printSpecificQuickFacts(dImmuneTypesByPoke, "immune")

def getImmuneTypes(dRankedWeaknessesByPoke):
    return getTargetScore(dRankedWeaknessesByPoke, 0)

def printFourTimesQuickFacts(dFourTimesTypesByPoke):
    return printSpecificQuickFacts(dFourTimesTypesByPoke, "four-times weak")

def getFourTimesTypes(dRankedWeaknessesByPoke):
    return getTargetScore(dRankedWeaknessesByPoke, 4)

def printSpecificQuickFacts(dTypesByPoke, sSpecific):
    for sPoke, lTypes in dTypesByPoke.items():
        if len(lTypes) > 0:
            print("{} is {} to {} moves".format(sPoke, sSpecific, ", ".join(lTypes)))

def getUsefulTypes(dRankedWeaknessesByPoke):
    lUsefulTypes = list(lAllTypes)

    for sPoke, lTypes in dRankedWeaknessesByPoke.items():
        for tScoreByType in lTypes:
            sType, iScore = tScoreByType

            if iScore < 2 and sType in lUsefulTypes:
                lUsefulTypes.remove(sType)

    return lUsefulTypes

def printUsefulTypesQuickFacts(lTypes):
    return printSpecificTypesQuickFacts(lTypes, "useful (1x or greater effective)")

def getUselessTypes(dRankedWeaknessesByPoke):
    dUselessTypes = {}

    for sPoke, lTypes in dRankedWeaknessesByPoke.items():
        for tScoreByType in lTypes:
            sType, iScore = tScoreByType

            if sType not in dUselessTypes:
                dUselessTypes[sType] = True

            isUseless = iScore < 1
            hasAlwaysBeenUseless = dUselessTypes[sType]

            dUselessTypes[sType] = isUseless and hasAlwaysBeenUseless

    lUselessTypes = [sType for sType, isUseless in dUselessTypes.items() if isUseless]

    return lUselessTypes

def printUselessTypesQuickFacts(lTypes):
    return printSpecificTypesQuickFacts(lTypes, "useless (worse than 1x effective)")

def printSpecificTypesQuickFacts(lTypes, sPhrase):
    print("List of {} types: {}".format(sPhrase, ", ".join(lTypes)))

def getSpecificTypes(dRankedWeaknessesByPoke, piMinInclusive, piMaxExclusive):
    lSpecificTypes = []

    for sPoke, lTypes in dRankedWeaknessesByPoke.items():
        for tScoreByType in lTypes:
            sType, iScore = tScoreByType

            if iScore >= piMinInclusive and iScore < piMaxExclusive:
                if sType not in lSpecificTypes:
                    lSpecificTypes.append(sType)

    return lSpecificTypes

def comprehensiveFacts(dRanked):
    dTypeMatrix = calculateTypeMatrix(dRanked)
    printTypeMatrix(dTypeMatrix)

def calculateTypeMatrix(dRanked):
    dTypeMatrix = {}

    for sPoke, lTypes in dRanked.items():
        for tScoreByType in lTypes:
            sType, iScore = tScoreByType
            
            if sType not in dTypeMatrix:
                dTypeMatrix[sType] = 1

            dTypeMatrix[sType] *= iScore

    return dTypeMatrix
    
def printTypeMatrix(dTypeMatrix):
    print("\n****Type Matrix****")

    maxLen = max(len(sType) for sType in dTypeMatrix.keys())

    for sType, iScore in dTypeMatrix.items():
        # maxLen describes the longest right padding for sType; read as:
        # "{:<maxLen>}"
        print("{:{}}: {:06.5f}".format(sType, maxLen, iScore))

intro()
team = promptForTeam()

teamWithTypes = getTypes(team)
if teamsAndTypesMatch(team, teamWithTypes):
    typesByPoke = determineTypesByPoke(teamWithTypes)

    dByPoke = calculateWeaknessByPoke(typesByPoke)

    dRanked = rankWeaknesses(dByPoke)

    quickFacts(dRanked)

    comprehensiveFacts(dRanked)
else:
    print("teamsAndTypesMatch(team, teamWithTypes) Error: len(team) = {} != len(teamWithTypes) = {}".format(len(team), len(teamWithTypes)))


