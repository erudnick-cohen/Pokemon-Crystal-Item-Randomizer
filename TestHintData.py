
import json

def testHintData():
    sign_desc = open("Config/SignData.json")
    s_descs = sign_desc.read()
    sign_desc_addr = json.loads(s_descs)
    sign_addr_data = {}
    for i in sign_desc_addr:
        sign_addr_data[i['name'].split(".")[-1]] = i

    details = list(sorted(sign_addr_data.items(), key=lambda x: x[1]["map"]))
    for d in details:
        print(d[0], ":", d[1]["map"].split("/")[-1])

testHintData()