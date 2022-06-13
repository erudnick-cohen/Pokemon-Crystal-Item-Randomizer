import LoadLocationData
import RandomizeFunctions
import os
import yaml

def testModifiers():
    modList = []

    modifierFiles = os.listdir("Modifiers")
    for i in modifierFiles:
        if os.path.isfile("Modifiers/"+i):
            yamlfile = open("Modifiers/"+i)
            yamltext = yamlfile.read()
            modList.append(yaml.load(yamltext, Loader=yaml.FullLoader))
            modList[-1]['fileName'] = i

    # Do not load from modifier dict when modifying data
    # As we are checking the functionality of all modifiers manually

    fullLocationData = LoadLocationData.LoadDataFromFolder(".", None, None , {}, [])
    all_locs = fullLocationData[0]
    locationList = LoadLocationData.FlattenLocationTree(all_locs)

    for mod in modList:
        if 'Changes' in mod:
            for change in mod['Changes']:
                location = change["Location"]
                possibilities = list(filter(lambda x: x.Name == location,locationList))
                if len(possibilities) == 0:
                    print("Error with mod, location not found!")
                    print(mod["Name"], location)
                    continue


                if "RemoveFlagReqs" in change:
                    for flagR in change["RemoveFlagReqs"]:
                        anyContains = False
                        for poss in possibilities:
                            if flagR in poss.FlagReqs:
                                anyContains = True
                        if not anyContains:
                            print("No flag found for:", flagR, location)

                if "RemoveItemReqs" in change:
                    for itemR in change["RemoveItemReqs"]:
                        anyContains = False
                        for poss in possibilities:
                            if itemR in poss.ItemReqs:
                                anyContains = True
                        if not anyContains:
                            print("No item found for:", itemR, location)

                if "RemoveLocationReqs" in change:
                    for locR in change["RemoveLocationReqs"]:
                        anyContains = False
                        for poss in possibilities:
                            if locR in poss.LocationReqs:
                                anyContains = True
                        if not anyContains:
                            print("No item found for:", locR, location)










testModifiers()