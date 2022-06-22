import LoadLocationData


def checkNumbers(x1, y1, x2, y2):
    x1 = int(x1)
    x2 = int(x2)
    y1 = int(y1)
    y2 = int(y2)

    if x1 == x2 and y1 == y2:
        return True

    if x1 == x2 and y1 == y2 + 1:
        return True

    if x1 == x2 and y1 == y2 - 1:
        return True

    if x1 - 1 == x2 and y1 == y2:
        return True

    if x1 + 1 == x2 and y1 == y2:
        return True

    return False

# Add test to ensure no conflict crossover between standard warp location names and warp groups

warpFileLocation = "Warp Data/WarpFriendlyNames.tsv"

warpGroupData = LoadLocationData.readTSVFile(warpFileLocation)

fullLocationData = LoadLocationData.LoadDataFromFolder(".", None, None, {}, [])
all_locs = fullLocationData[0]
locationList = LoadLocationData.FlattenLocationTree(all_locs)


#reqData = list(filter(lambda x: x.Name == req, locations))

warpCounter = {}

conflicts = []
for item in warpGroupData:
    groupName = item["Group"]
    res = list(filter(lambda x: x.Name == groupName and groupName not in x.WarpReqs \
                      and x.Type != "Transition", locationList))
    if len(res) > 0:
        conflicts.append(groupName)


    # Add check here if warp already in list that is adjacent
    if groupName not in warpCounter:
        warpCounter[groupName] = []

#	#   Map Name	*	MapX	MapY	Default Destination	DestX	DestY	Non-Default Warp Name	E/X	Group	Friendly Warp Name
#   92	ROUTE_28	2	7	3	ROUTE_28_STEEL_WING_HOUSE	2	7		E	28 Cut	ROUTE_28_STEEL_WING_HOUSE Entrance
    hasAdjacent = False
    for current in warpCounter[groupName]:
        # There are some niche cases where these ARE next to each other!
        # Such as celadon mansion
        hasAdjacent = hasAdjacent or (checkNumbers(current['X'], current['Y'], item['X'], item['Y']))

    if not hasAdjacent:
        warpCounter[groupName].append(item)



#TODO: May want to make different names for warp reqs that are the same as the location names
print("Conflicting names:", conflicts)

# Add a test to check for no mispelling, etc of location names vs location requirements

allLocationReqs = []
allLocationNames = []

invalidWarpReqs =[]

for x in locationList:
    if x.Type == "Transition":
        continue

    for i in x.LocationReqs:
        if i not in allLocationReqs and \
                "Warpie" not in i:
            allLocationReqs.append(i)
    if x not in allLocationNames:
        allLocationNames.append(x.Name)

    for w in x.WarpReqs:
        if w not in warpCounter:
            invalidWarpReqs.append((w, x.Name))

foundReqs = []
for a in allLocationReqs:
    if a in allLocationNames:
        foundReqs.append(a)


for f in foundReqs:
    allLocationReqs.remove(f)

print("Unknown location requirements:", allLocationReqs)

print("Unknown warp requirements:", invalidWarpReqs)

# This does not handle DOOR warps which have 2 warps adjacent to one another!

# Remember to exclude groups if ever adding anything to logic
# Such as shop-sanity or stupid-sanity
knownSingleGroups = ['Blackthorn Lowest', 'Olivine Trade House', 'Olivine Punishment House', 'Olivine Mart', 'Miltank Barn', 'Mahogoney Gyarados House', 'Ecruteak Lugia House', 'Ecruteak Mart', 'Blackthorn Dragon Speech House', 'Blackthorn Trade House', 'Blackthorn Mart', 'Move Deleters', 'Cerulean Gym Badge House', 'Cerulean Dig House', 'Cerulean Trade Speech House', 'Cerulean Mart', 'Azalea Mart', 'Violet Mart', 'Violet School', 'Violet Nickname House', 'Violet Trade House', 'Goldenrod Happiness House', 'Bills House', 'Goldenrod PP House', 'Goldenrod Name Rater', 'Goldenrod Dept. Store Roof', 'Goldenrod Game Corner', 'Vermilion Fishing House', 'Vermilion Train House', 'Vermilion Mart', 'Vermilion Diglett House', 'Reds House 2F', 'Blues House', 'Pewter Nidoran House', 'Pewter Mart', 'Pewter Snooze House', 'Top Far Right Ship Room', 'Top Right Ship Room', 'Bottom Far Left Ship Room', 'Bottom Left Ship Room', 'Bottom Right Ship Room', 'Bottom Far Right Ship Room', 'Mount Moon Gift Shop', 'Hall Of Fame', 'Fuchsia Mart', 'Safari Zone Office', 'Fuchsia Bills Brothers House', 'Wardens House', 'Fujis House', 'Lavender Speech House', 'Lavender Name Rater', 'Lavender Mart', 'Soul House', 'Pokemon Center Upstairs', 'Celadon Mansion 2F Back', 'Celadon Mansion 2F', 'Celadon Mansion Back 3F', 'Celadon Mansion 3F', 'Celadon Mansion Roof', 'Celadon Game Corner', 'Celadon Prize Corner', 'Route 16 Hidden House', 'Shuckle House', 'Cianwood Photo House', 'Cianwood Lugia House', 'Cianwood Seers House', 'Viridian House', 'Trainer House 2F', 'Viridian Mart', 'Players House', 'Players Room', 'Players House 2F', 'New Bark House', 'Elms House', 'Route 26 Heal House', 'Siblings House', 'Saffron Mart', 'Cherrygrove Mart', 'Cherrygrove Gym House', 'Cherrygrove Guide House', 'Cherrygrove Evolution House']

singular = list(filter(lambda x: len(x[1]) == 1 and x[0] not in knownSingleGroups, warpCounter.items()))

singleGroups = []
singleUsedGroups = []
transitionalSingletons = []
transitionalOuts = []
for s in singular:
    sGroup = s[0]
    validTransitions = list(filter(lambda x: x.Type == "Transition" and x.Name == sGroup ,locationList))

    if len(validTransitions) > 0:
        transitionalSingletons.append(sGroup)
    else:

        validTransitionsOut = list(filter(lambda x: x.Type == "Transition" and sGroup in x.LocationReqs, locationList))
        if len(validTransitionsOut) > 0:
            transitionalOuts.append(sGroup)
        else:

            singluarUsed = list(filter(lambda x: x.Type != "Transition" and sGroup in x.WarpReqs, locationList))
            if len(singluarUsed) > 0:
                singleUsedGroups.append(sGroup)
            else:
                singleGroups.append(sGroup)

# Manually review this list, there are no items here, if there is something unexpected here, it needs to be fixed
print("single",singleGroups)


print("transOut",transitionalOuts)
print("transIn",transitionalSingletons)
print("singleUsed",singleUsedGroups)




