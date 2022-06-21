import LoadLocationData
import RandomizeFunctions

#TODO Also review TestWarpGroupData

def testWarpLocations():
    fullLocationData = LoadLocationData.LoadDataFromFolder(".", flags=["Warps"], loadWarpData=False)
    all_locs = fullLocationData[0]
    locationList = LoadLocationData.FlattenLocationTree(all_locs)

    items = list(filter(lambda x: (x.isGym() or x.isItem()), locationList))

    lookup = {}

    acceptableYmls = ["Route29.yml","YourHouse.yml","StartingWarpLocations.yml", "Route27.yml"]

    alwaysAvailable = []

    # Rock Tunnel Steel Wing TM > Rock Tunnel South Exit > Rock Tunnel South Entrance
    for item in items:
        checking = []
        checked = []
        newAlways = []
        for locReq in item.LocationReqs:
            if locReq not in lookup:
                checking.append(locReq)
        while len(checking) > 0:
            toCheck = checking.pop(0)

            #print("Checking requirement:", toCheck)
            if toCheck in lookup:
                pass
            else:
                checked.append(toCheck)
                # Won't contain warp group data, which should be fine for the test, so we can stop earlier
                options = list(filter(lambda x: x.Name == toCheck, locationList))
                lookup[toCheck] = options

                for option in options:
                    if len(option.LocationReqs) == 0 and \
                            option.YmlFile not in acceptableYmls:
                        print("Issue with:", option.Name, option.YmlFile)
                        newAlways.append(option)

                    for req in option.LocationReqs:
                        if req not in checking:
                            checking.append(req)


        #print("Checked requirements for item:", item.Name)
        if len(newAlways) > 0:
            print("Issue with item:",item.Name)
            # Note there may be issues with other items when running this, if resolved should no longer be an issue?











testWarpLocations()