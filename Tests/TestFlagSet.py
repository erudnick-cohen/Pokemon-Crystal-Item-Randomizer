import LoadLocationData
import RandomizeFunctions

# This test requires manual review as the test is incomplete

def testFlags():
    fullLocationData = LoadLocationData.LoadDataFromFolder(".", None, None, {}, [])
    all_locs = fullLocationData[0]
    locationList = LoadLocationData.FlattenLocationTree(all_locs)

    allFlagsSet = []
    allFlagsReq = []

    locationsWhichSet = []

    for l in locationList:
        for req in l.FlagReqs:
            if req not in allFlagsReq:
                allFlagsReq.append(req)
        for set in l.FlagsSet:
            if set not in allFlagsSet:
                allFlagsSet.append(set)
        if len(l.FlagsSet) > 0:
            locationsWhichSet.append(l)

    correctFlagUse = []
    incorrectFlagUse = allFlagsReq.copy()

    for flag in allFlagsReq:
        if flag in allFlagsSet:
            correctFlagUse.append(flag)

    # Incorrect flag use does not yet factor in Flags set by badges
    # Or Flags for locking items (e.g. Hidden/Warps)
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

    incorrectUsedLocReqs = []
    incorrectWarpReqFlagSets = []

    # Many of these are subjective per use case, so manually review

    for loc in locationsWhichSet:
        lookupLocationReqsForSet = list(filter(lambda x: loc.Name in x.LocationReqs, locationList))

        for entry in lookupLocationReqsForSet:
            if entry not in loc.Sublocations:
                incorrectUsedLocReqs.append((loc, entry))
            if len(entry.WarpReqs) > 0:
                incorrectWarpReqFlagSets.append((loc, entry))



    return






testFlags()