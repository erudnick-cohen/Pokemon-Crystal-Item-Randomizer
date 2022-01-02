import LoadLocationData





# Add test to ensure no conflict crossover between standard warp location names and warp groups

warpFileLocation = "WarpFriendlyNames.tsv"

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

print(conflicts)

