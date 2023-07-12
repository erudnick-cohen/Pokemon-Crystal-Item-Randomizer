import LoadLocationData



# Add test to ensure no conflict crossover between standard warp location names and warp groups

warpFileLocation = "Warp Data/WarpFriendlyNames.tsv"
warpGroupData = LoadLocationData.readTSVFile(warpFileLocation)

warpGroups = { x["Group"] for x in warpGroupData }

fullLocationData = LoadLocationData.LoadDataFromFolder(".", None, None, {}, [])
all_locs = fullLocationData[0]
locationList = LoadLocationData.FlattenLocationTree(all_locs)

hasTo = []
hasFrom = []
missing = []
multipleLocations = []

transitions = list(filter(lambda x: x.Type == "Transition", locationList))
for t in transitions:
    if len(t.LocationReqs) == 0:
        multipleLocations.append(t.Name)
    elif len(t.LocationReqs) > 1:
        multipleLocations.append(t.Name)

    transitionFrom = t.LocationReqs[0]
    transitionTo = t.Name

    if transitionFrom not in warpGroups:
        missing.append(transitionFrom)

    if transitionTo not in warpGroups:
        missing.append(transitionTo)

    if transitionFrom not in hasFrom:
        hasFrom.append(transitionFrom)
    if transitionTo not in hasTo:
        hasTo.append(transitionTo)

missingFrom = [x for x in hasTo if x not in hasFrom]
missingTo = [x for x in hasFrom if x not in hasTo]

print("missingAtAll", missing)


print("missingTo",len(missingTo), missingTo)
print("missingFrom", len(missingFrom), missingFrom)

print("multipleLocations",multipleLocations)

# Note failing on these tests is not required
# But if an item is related to one of these, then purging will remove access to it
# e.g. te Radio Tower Maybe Card Key route blocked off without the Impossible route to counterbalance

# Actively deciding not to have this route may lead to logic changes, such as not sending down
# Dead ends, maybe?

# Likewise, routes involving Ruins Top Ledge had an impossible added
# To then be removed with IFatRain modifier as patched to make not one-way and therefore passable


# This test should also load and ensure all transitions are valid warp groups in the warp file!







