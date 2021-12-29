import LoadLocationData


def readTSVFile(filename):
    file = open(filename)
    data = file.readlines()

    objs = []

    first_line = True
    for line in data:
        if first_line:
            field_names = line.split("\t")
            first_line = False
        else:
            d = line.split("\t")
            obj = {}
            iterator = 0
            for name in field_names:
                obj[name] = d[iterator]
                iterator += 1

            objs.append(obj)

    return objs



# Add test to ensure no conflict crossover between standard warp location names and warp groups

warpFileLocation = "WarpFriendlyNames.tsv"

warpGroupData = readTSVFile(warpFileLocation)

fullLocationData = LoadLocationData.LoadDataFromFolder(".", None, None, {}, [])
all_locs = fullLocationData[0]
locationList = LoadLocationData.FlattenLocationTree(all_locs)


#reqData = list(filter(lambda x: x.Name == req, locations))

conflicts = []
for item in warpGroupData:
    groupName = item["Group"]
    res = list(filter(lambda x: x.Name == groupName and groupName not in x.WarpReqs, locationList))
    if len(res) > 0:
        conflicts.append(groupName)

print(conflicts)

