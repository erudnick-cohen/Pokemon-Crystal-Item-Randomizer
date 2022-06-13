import LoadLocationData
import RandomizeFunctions


def testLocations():
    fullLocationData = LoadLocationData.LoadDataFromFolder(".", None, None , {}, [])
    all_locs = fullLocationData[0]
    locationList = LoadLocationData.FlattenLocationTree(all_locs)

    foundLocations = []
    recursiveLocations = []
    unfoundLocations = []

    for loc in locationList:
        if loc.Name in unfoundLocations:
            foundLocations.append(loc.Name)
            unfoundLocations.remove(loc.Name)

        if loc.Name not in foundLocations:
            foundLocations.append(loc.Name)

        # Handle this differently
        if loc.Type == "Transition":
            continue

        for req in loc.LocationReqs:
            if req not in foundLocations and req not in unfoundLocations and req not in recursiveLocations:
                unfoundLocations.append(req)
            if req == loc.Name:
                recursiveLocations.append(loc)

    print("Unfound:",unfoundLocations)
    print("Recusive:", recursiveLocations)

    assert(len(unfoundLocations)==0)
    assert(len(recursiveLocations)==0)



testLocations()