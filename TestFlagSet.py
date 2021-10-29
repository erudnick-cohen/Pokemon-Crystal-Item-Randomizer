import LoadLocationData
import RandomizeFunctions


def testFlags():
    fullLocationData = LoadLocationData.LoadDataFromFolder(".", None, None , {}, [])
    all_locs = fullLocationData[0]
    locationList = LoadLocationData.FlattenLocationTree(all_locs)

    allFlagsSet = []
    allFlagsReq = []

    for l in locationList:
        for req in l.FlagReqs:
            if req not in allFlagsReq:
                allFlagsReq.append(req)
        for set in l.FlagsSet:
            if set not in allFlagsSet:
                allFlagsSet.append(set)

    correctFlagUse = []
    incorrectFlagUse = allFlagsReq.copy()

    for flag in allFlagsReq:
        if flag in allFlagsSet:
            correctFlagUse.append(flag)

    for correct in correctFlagUse:
        incorrectFlagUse.remove(correct)

    incorrect_location_exists =[]
    incorrect_no_location = []

    for incorrect in incorrectFlagUse:
        lookupLocationWithFlagName = list(filter(lambda x: x.Name == incorrect, locationList))
        if len(lookupLocationWithFlagName) > 0:
            incorrect_location_exists.append(incorrect)
        else:
            incorrect_no_location.append(incorrect)

    # TODO
    # Update results of these items for consistency, eventually especially with Hints

    return






testFlags()