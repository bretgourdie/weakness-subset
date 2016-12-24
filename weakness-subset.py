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
    teamWithTypes = {}
    for poke in team:
        teamWithTypes[poke] = ["Type1", "Type2"]

    return teamWithTypes

intro()
team = promptForTeam()
teamWithTypes = getTypes(team)
