import json

from RandomizeFunctions import fileToLocation


def testHintData():
    sign_desc = open("Config/SignData.json")
    s_descs = sign_desc.read()
    sign_desc_addr = json.loads(s_descs)
    sign_addr_data = {}
    for i in sign_desc_addr:
        sign_addr_data[i['name'].split(".")[-1]] = i

    details = list(sorted(sign_addr_data.items(), key=lambda x: x[1]["map"]))

    for d in details:
        d_file = d[1]["map"].split("/")[-1]
        d_file = fileToLocation(d_file)

        printString = "{{\"{}\":\"{}\"}}"
        x = printString.format(d[0], d_file)
        print(x)

    # seperated = {}
    # for d in details:
    #     mapFile = d[1]["map"].split("/")[-1]
    #     if not mapFile in seperated:
    #         seperated[mapFile] = []
    #     seperated[mapFile].append(d[0])
    #
    # for key in seperated.keys():
    #     printString = "{{\"{}\":{}}}"
    #     printMe = printString.format(key, seperated[key]).replace("\'","\"")
    #     print(printMe)


testHintData()
