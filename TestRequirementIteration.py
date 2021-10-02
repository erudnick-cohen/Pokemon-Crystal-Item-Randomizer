import LoadLocationData
import RandomizeFunctions


def testIteration(l):
    fullLocationData = LoadLocationData.LoadDataFromFolder(".", None, None , {}, [])
    all_locs = fullLocationData[0]
    locationList = LoadLocationData.FlattenLocationTree(all_locs)

    for search_for in l:
        testLocation = list(filter(lambda x: x.Name == search_for ,locationList))
        known = []
        if len(testLocation) == 0:
            print("Test failed, none found")
            exit(1)
        else:
            for found in testLocation:
                addedLoc, addedFlag, addedItem = RandomizeFunctions.IterateRequirements(found, locationList, known,
                                                                                        partial_known=[])
        print("Done")

testIteration(["Mt Mortar Ultra Ball", "Viridian Dream Eater TM", "Route 45 Max Potion",
               "Rock Tunnel Elixer", "Goldenrod Tunnel Sleep Talk TM",
               "Cerulean City Hidden Berserk Gene", "Pink Bow"])