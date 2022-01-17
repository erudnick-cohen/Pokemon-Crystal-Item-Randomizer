import LoadLocationData
import RandomizeFunctions

def isExpectedBehaviour(location, expected_requirement):
    if expected_requirement is not None and expected_requirement not in location.LocationReqs:
        print((location.Name, expected_requirement, location.LocationReqs))

    if location.Sublocations is not None and len(location.Sublocations) > 0:
        for x in location.Sublocations:
            isExpectedBehaviour(x, location.Name)

def testSublocations():
    fullLocationData = LoadLocationData.LoadDataFromFolder(".", None, None, {}, [])
    all_locs = fullLocationData[0]

    oddcases = []

    for loc in all_locs:
        isExpectedBehaviour(loc, None)








testSublocations()