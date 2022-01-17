import LoadLocationData





# Add test to ensure no conflict crossover between standard warp location names and warp groups

warpFileLocation = "Warp Data/WarpFriendlyNames.tsv"

warpGroupData = LoadLocationData.readTSVFile(warpFileLocation)

fullLocationData = LoadLocationData.LoadDataFromFolder(".", None, None, {}, [])
all_locs = fullLocationData[0]
locationList = LoadLocationData.FlattenLocationTree(all_locs)


#reqData = list(filter(lambda x: x.Name == req, locations))

conflicts = []
for item in warpGroupData:
    groupName = item["Group"]
    res = list(filter(lambda x: x.Name == groupName and groupName not in x.WarpReqs \
                      and x.Type != "Transition", locationList))
    if len(res) > 0:
        conflicts.append(groupName)

#TODO: May want to make different names for warp reqs that are the same as the location names
print("Conflicting names:", conflicts)

# Add a test to check for no mispelling, etc of location names vs location requirements

allLocationReqs = []
allLocationNames = []
for x in locationList:
    if x.Type == "Transition":
        continue

    for i in x.LocationReqs:
        if i not in allLocationReqs and \
                "Warpie" not in i:
            allLocationReqs.append(i)
    if x not in allLocationNames:
        allLocationNames.append(x.Name)

foundReqs = []
for a in allLocationReqs:
    if a in allLocationNames:
        foundReqs.append(a)


for f in foundReqs:
    allLocationReqs.remove(f)

print("Unknown location requirements:", allLocationReqs)





