import json
import os
import re
import mmap

import yaml

import LoadLocationData

# A function which detects known possible warp changes and automatically enabled other modifiers

# This function is used for taking an address from a label and working out the values used to jump to it
# Ignore the bank as can assumed to not be needed for jumping within a script
# Return the 2-part address value
def AddressToIntValues(address):
    bytes = address.to_bytes(3, byteorder='little')
    return bytes[0:2]


def InterpretWarpChanges(file):
    json_file_1 = "Warp Data/crystal-speedchoice-warp-label-details.json"
    rom_file = file

    default_label_file = "crystal-speedchoice-label-details.json"

    f = open(rom_file, 'r+b')
    romMap = mmap.mmap(f.fileno(), 0)

    yamlfile1 = open(json_file_1, encoding='utf-8')
    yamltext1 = yamlfile1.read()
    addressLists1 = json.loads(yamltext1)
    addressData1 = {}
    for i in addressLists1:
        addressData1[i['label'].split(".")[-1]] = i

    #interpretableMapDetails = list(filter(lambda x: x != None, addressData1))

    json_file_2 = default_label_file

    yamlfile2 = open(json_file_2, encoding='utf-8')
    yamltext2 = yamlfile2.read()
    addressLists2 = json.loads(yamltext2)
    addressData2 = {}
    for i in addressLists2:
        addressData2[i['label'].split(".")[-1]] = i



    json_file_checks = "Warp Data/warp_checks.json"
    yamlfileF = open(json_file_checks, encoding='utf-8')
    yamltextF = yamlfileF.read()
    addressListsF = json.loads(yamltextF)

    addModifiers = []


    for check in addressListsF:
        print(check)

        LabelName = check["LabelName"]
        if "ckir" in LabelName:
            labelData = addressData2
        else:
            labelData = addressData1

        expectedOnValues = check["ExpectedOnValues"]
        expectedOffValues = check["ExpectedOffValues"]

        iterator=0
        for value in expectedOnValues:
            if type(value) != int:
                # TODO Lookup the value in the label as refers to a label address
                addressForOn = labelData[value]["address_range"]["begin"]
                jumpBytes = AddressToIntValues(addressForOn)
                expectedOnValues[iterator] = jumpBytes[0]
                expectedOnValues[iterator + 1] = jumpBytes[1]
                iterator += 1

            iterator += 1

        iterator = 0
        for value in expectedOffValues:
            if type(value) != int:
                # TODO Lookup the value in the label as refers to a label address
                addressForOff = labelData[value]["address_range"]["begin"]
                jumpBytes = AddressToIntValues(addressForOff)
                expectedOffValues[iterator] = jumpBytes[0]
                expectedOffValues[iterator + 1] = jumpBytes[1]
                iterator += 1

            iterator += 1


        lookupLabel = labelData[LabelName]
        romAddress = lookupLabel["address_range"]
        lookValues = list(romMap[romAddress["begin"]:romAddress["end"]])
        labelValuesCount = len(lookValues)

        if labelValuesCount != len(expectedOnValues) or labelValuesCount != len(expectedOffValues):
            print("unequal lookup values")
            print(lookValues)
        else:
            isOn = True
            isOff = True

            iterator=0
            while iterator < labelValuesCount:
                lookupI = lookValues[iterator]
                if lookupI != expectedOnValues[iterator]:
                    isOn = False
                if lookupI != expectedOffValues[iterator]:
                    isOff = False

                iterator += 1

            if not isOn and not isOff:
                print("Error: Neither on nor off")
            elif isOn and isOff:
                print("On AND Off... broken!")
            elif isOn:
                print("On")
                modifierChanges = check["ModifierChanges"]
                if "Add" in  modifierChanges:
                    addModifiers.extend(modifierChanges["Add"])
            elif isOff:
                print("Off")



    print(addModifiers)

    newModData = []

    for mod in addModifiers:
        yamlfile = open(mod)
        yamltext = yamlfile.read()

        loadedYaml = yaml.load(yamltext, Loader=yaml.FullLoader)
        newModData.append(loadedYaml)


    return newModData



def ReverseWarpLabels(label):
    entry_key = "cwri"
    base_label = ".{}_{}{}_{}_{}_{}_{}::"

    #cwri_BEFOREWiseTriosRoom_7_5_ECRUTEAK__CITY_5

    data = label.replace("__","##")
    entry_data = data.split("_")

    if len(entry_data) == 1:
        return None

    #print("ed",entry_data)

    MapName = entry_data[1].replace("BEFORE","").replace("##","_")
    MapX = entry_data[2]
    MapY = entry_data[3]
    MapDestName = entry_data[4].replace("##","_")
    MapDestId = entry_data[5]
    if MapDestId == "m":
        MapDestId = -1
    Iterator = int(entry_data[6]) + 1

    return {
        "MapName": MapName,
        "MapX": MapX,
        "MapY": MapY,
        "MapDestName": MapDestName,
        "MapDestId": MapDestId,
        "Iterator": Iterator
    }

def mapEventToLabelNames(source,i):
    entry_key = "ckir"
    base_label = ".{}_{}_mapdetail_{}_{}::"

    map_source = source.replace("_","__").upper()

    before_label = base_label.\
        format(entry_key, "BEFORE", map_source, i)

    after_label = base_label. \
        format(entry_key, "AFTER", map_source, i)

    return before_label, after_label

def warpEventToLabelNames(source,entry,i):

    entry_key = "cwri"
    base_label = ".{}_{}{}_{}_{}_{}_{}_{}::"

    d = entry.split(",")
    map_source = source.replace("_","__").upper()
    warp_x = d[0].replace("warp_event", "").strip()
    warp_y = d[1].strip()
    warp_dest = d[2].strip().replace(" ","").replace("_","__").upper()

    warp_dest_id_form = d[3]
    if ";" in warp_dest_id_form:
        warp_dest_id_form = warp_dest_id_form[0:warp_dest_id_form.index(";")]# comment_handler

    warp_dest_id = warp_dest_id_form.strip()

    if int(warp_dest_id) == -1:
        warp_dest_id = "m"

    #warp_event  2,  5, BLACKTHORN_GYM_1F, 5 ; hole

    before_label = base_label.\
        format(entry_key, "BEFORE", map_source, warp_x, warp_y, warp_dest, warp_dest_id, i)

    after_label = base_label. \
        format(entry_key, "AFTER", map_source, warp_x, warp_y, warp_dest, warp_dest_id, i)

    return before_label, after_label


def LoadSpecialCaseWarps():
    special_cases_file = open("Warp Data/warp_special_cases.json")
    special_cases = json.loads(special_cases_file.read())
    special_cases_file.close()

    return special_cases


def handleSpecialCases(warpData, warpLocation, special_cases):

    for case in special_cases:
        if "From" in case:
            pass

        if "To" in case:
            toCase = case["To"]
            if warpData["Start Warp Name"] == toCase["WarpName"]:
                for change in toCase["Changes"].items():
                    if change[0] == "FlagsSet":
                        for setFlag in change[1]:
                            warpLocation["FlagsSet"].append(setFlag)

    return


def GenerateWarpLabels():
    romDirectory = "RandomizerRom"
    mapsDirectory = "maps"

    mapFiles = romDirectory + "/" + mapsDirectory
    map_files = os.listdir(mapFiles)

    map_mapping = getMapAttributesMapping()

    # warp_event  1,  3, CELADON_DEPT_STORE_1F, -1

    special_cases = []


    regex = "\s{0,}warp_event\s{1,}\d{1,},\s{1,}\d{1,},\s{0,}[a-zA-z_0-9]{1,},\s{1,}(\d|-){1,}\s{0,}"
    warp_data_match = re.compile(regex)

    #regex_minus = "\s{0,}warp_event\s{1,}\d{1,},\s{1,}\d{1,},\s{0,}[a-zA-z_0-9]{1,},\s{0,}-\d{1,}\s{0,}"
    #warp_data_minus_match = re.compile(regex_minus)

    for m in map_files:
        extension = m.split(".")[-1]
        if extension != "asm":
            continue

        map_file_data = open(mapFiles+"/"+m, encoding="utf8")
        data = map_file_data.readlines()
        map_file_data.close()

        warp_events = list(filter(warp_data_match.match, data))
        missed_warp_events = list(filter(lambda x: "warp_event" in x, data))

        not_found = list(filter(lambda x: x not in warp_events,missed_warp_events))
        for n in not_found:
                print("unknown", m, n)

        change = False
        iterator = 0
        for warp in warp_events:
            where = data.index(warp)

            better_name = map_mapping[m.replace(".asm","")]

            before,after = warpEventToLabelNames(better_name, warp, iterator)
            iterator += 1

            if data[where-1].strip() != before and data[where+1].strip() != after:
                data.insert(where, before + "\n")
                data.insert(where + 2, after + "\n")

                change = True

            # Future version to check tile, and therefore hole checking etc
            # If this field is a hole, then add a special case

            # For now, just hard-code the Lighthouse 4F Central Holes
            # Lighthouse 4F 8,3 & 9,3

            interpreted_label = ReverseWarpLabels(before.replace("::", ""))
            print(interpreted_label)

            if interpreted_label["MapName"] == "OLIVINE_LIGHTHOUSE_4F" and \
                interpreted_label["MapY"] == "3" and interpreted_label["MapX"] in ("8"):
                warpCase = {
                    "To":
                        {
                            "WarpName": "Lighthouse 4F North Drop",
                            "Changes":
                                {
                                    "FlagsSet": ["Lighthouse4FHoles"]
                                }

                        }
                }

                special_cases.append(warpCase)

            if interpreted_label["MapName"] == "OLIVINE_LIGHTHOUSE_4F" and \
                    interpreted_label["MapY"] == "3" and interpreted_label["MapX"] in ("9"):
                warpCase = {
                    "To":
                        {
                            "WarpName": "Lighthouse 4F North Drop 2",
                            "Changes":
                                {
                                    "FlagsSet": ["Lighthouse4FHoles"]
                                }

                        }
                }

                special_cases.append(warpCase)



        if change:
            map_file_data = open(mapFiles + "/" + m, "w", encoding="utf8")
            map_file_data.writelines(data)
            map_file_data.close()

    if len(special_cases) > 0:
        warp_special_cases = open("Warp Data/warp_special_cases.json", "w")
        warp_special_cases.writelines(json.dumps(special_cases, indent=4))
        map_file_data.close()

def BytesToEasyString(bytes):
    s = ""
    for b in bytes:
        s += str(hex(b)).replace("0x","").zfill(2).upper()
    return s


def interpretDataForMapIDs():
    json_file = "Warp Data/crystal-speedchoice-warp-label-details.json"
    rom_file = "warp-test.gbc" # For this function, needs vanilla rom
    output_file = "Warp Data/map_ids.conf"

    f = open(rom_file, 'r+b')
    romMap = mmap.mmap(f.fileno(), 0)

    yamlfile = open(json_file, encoding='utf-8')
    yamltext = yamlfile.read()
    addressLists = json.loads(yamltext)
    addressData = {}
    for i in addressLists:
        addressData[i['label'].split(".")[-1]] = i

    map_name_to_id = {}

    for label in addressData.keys():
        obj = ReverseWarpLabels(label)
        if obj is None:
            continue
        #print(obj)

        data_range = addressData[label]
        addr_start = data_range["address_range"]["begin"]
        addr_end = data_range["address_range"]["end"]

        bytes = romMap[addr_start:addr_end]
        dest_map_bytes = bytes[3:5]
        store_bytes = BytesToEasyString(dest_map_bytes)

        if not obj["MapDestName"] in map_name_to_id:
            map_name_to_id[obj["MapDestName"]] = store_bytes
        else:
            if store_bytes != map_name_to_id[obj["MapDestName"]]:
                print("Did not match")

    #print("mp2i", map_name_to_id)

    o_file = open(output_file, "w")
    for key in map_name_to_id:
        value = map_name_to_id[key]
        o_file.write("{}={}\n".format(key,value))
    o_file.flush()
    o_file.close()


def getMapAttributesMapping():
    romDirectory = "RandomizerRom"
    attr_file="data/maps/attributes.asm"

    file_path = romDirectory+"/"+attr_file
    #map_attributes AzaleaTown, AZALEA_TOWN, $05, WEST | EAST

    f = open(file_path, "r")
    data = f.readlines()
    f.close()

    result = {}

    for line in data:
        line = line.strip()
        if not line.startswith("map_attributes"):
            continue

        if line.startswith("map_attributes:"):
            continue

        s = line.split(",")
        map_path = s[0].replace("map_attributes ","")
        map_desired = s[1].strip()

        result[map_path] = map_desired

    return result




def getMapLookupForById(addressData):
    res = {}
    for label in addressData.keys():
        obj = ReverseWarpLabels(label)

        if obj is None:
            continue

        key_name = obj["MapName"]+"_"+str(obj["Iterator"])
        value_to_add = [obj["MapX"],obj["MapY"]]

        res[key_name] = value_to_add

    # Hard-code National Park BGC

    res["NATIONAL_PARK_BUG_CONTEST_1"] = [33,18]
    res["NATIONAL_PARK_BUG_CONTEST_2"] = [33, 19]
    res["NATIONAL_PARK_BUG_CONTEST_3"] = [10, 47]
    res["NATIONAL_PARK_BUG_CONTEST_4"] = [11, 47]


    return res

def getWarpGroupData():
    warpFileLocation = "Warp Data/WarpFriendlyNames.tsv"
    warpGroupData = LoadLocationData.readTSVFile(warpFileLocation)
    return warpGroupData

def interpretDataForRandomisedRom(file, out_file="warp-output.tsv"):
    json_file = "Warp Data/crystal-speedchoice-warp-label-details.json"
    rom_file = file
    conf_file = "Warp Data/map_ids.conf"

    f = open(rom_file, 'r+b')
    romMap = mmap.mmap(f.fileno(), 0)

    yamlfile = open(json_file, encoding='utf-8')
    yamltext = yamlfile.read()
    addressLists = json.loads(yamltext)
    addressData = {}
    for i in addressLists:
        addressData[i['label'].split(".")[-1]] = i

    map_id_to_name = {}

    map_ids=open(conf_file, "r")
    map_ids_data = map_ids.readlines()
    for line in map_ids_data:
        line = line.strip()
        s = line.split("=")
        map_ID = s[1]
        map_id_to_name[map_ID] = s[0]

    map_ids.close()

    # TODO Hardcode National Park for now?
    map_id_to_name["0310"] = "NATIONAL_PARK_BUG_CONTEST"


    map_lookup = getMapLookupForById(addressData)

    group_data = getWarpGroupData()

    resulting_data = []

    for label in addressData.keys():
        obj = ReverseWarpLabels(label)

        if obj is None:
            print("None", label)
            continue

        if obj["MapDestId"] == -1:
            continue

        #print(obj)

        o_map = obj["MapName"]
        o_x = int(obj["MapX"])
        o_y = int(obj["MapY"])

        data_range = addressData[label]
        addr_start = data_range["address_range"]["begin"]
        addr_end = data_range["address_range"]["end"]

        relevant_rom = romMap[addr_start:addr_end]
        y_value = relevant_rom[0]
        x_value = relevant_rom[1]
        dest_id = relevant_rom[2]
        dest_map_bytes = relevant_rom[3:5]

        if (y_value != o_y) or (o_x != x_value):
            # This is NOT a valid rom of the right version, etc!
            print("continue...", y_value, "!=", o_y, x_value, "!=", o_x, obj)
            continue

        dest_id_string = str(dest_id)

        easy_bytes = BytesToEasyString(dest_map_bytes)

        if easy_bytes not in map_id_to_name:
            print("Skipping as bytes not found for:", easy_bytes, label)
            continue

        dest_map_name = map_id_to_name[easy_bytes]
        key_search = dest_map_name+"_"+dest_id_string

        if key_search not in map_lookup:
            print("Not found:", key_search)
            continue


        dest_x,dest_y = map_lookup[key_search]

        group_data_start = list(filter(lambda x: x['Start Map']==o_map \
                                                 and x['X']==str(o_x) and x["Y"]==str(o_y), group_data))

        group_data_end = list(filter(lambda x: x['Start Map'] == dest_map_name \
                                                 and x['X'] == str(dest_x) and x["Y"] == str(dest_y), group_data))

        if len(group_data_start) != 1 or len(group_data_end) != 1:
            #print("Incorrect number found", dest_map_name)
            continue

        if len(group_data_start[0]["Group"]) == 0:
            # As yet unnamed group
            #print("0 start", o_map, o_x, o_y)
            continue

        if len(group_data_end[0]["Group"]) == 0:
            # As yet unnamed group
            #print("0 end", dest_map_name, dest_x, dest_y)
            continue

        newObj = {
            "Start Name": group_data_start[0]["Friendly Name"],
            "Start Group": group_data_start[0]["Group"],
            "End Name": group_data_end[0]["Friendly Name"],
            "End Group": group_data_end[0]["Group"],
        }

        resulting_data.append(newObj)

    output_warp_data_file = "Warp Data/" + out_file
    out_file = open(output_warp_data_file, "w")
    out_file.write("Start Warp Name\tStart Warp Group\t->\tEnd Warp Name\tEnd Warp Group\n")

    for res in resulting_data:
        l_string = "{}\t({})\t->\t{}\t({})\n"
        toFile = l_string.format(res["Start Name"], res["Start Group"], res["End Name"], res["End Group"])
        out_file.write(toFile)
    out_file.flush()
    out_file.close()

if __name__ == '__main__':
    pass
    #InterpretWarpChanges("C:\\Users\\Alex\\Downloads\\CrystalEtc\\debugfix\\base.gbc")
    #InterpretWarpChanges("C:\\Users\\Alex\\Downloads\\CrystalEtc\\debugfix\\triggers.gbc")
    #InterpretWarpChanges("C:\\Users\\Alex\\Downloads\\CrystalEtc\\debugfix\\flashless.gbc")

    #GenerateWarpLabels()

    # No step yet to run ruby script to generate the changed labels file

    # After processing, process with map ID is each warp, may be better to generate this at another stage
    #interpretDataForMapIDs()

    # Main function to eventually be called before each rom is generated
    #interpretDataForRandomisedRom(file="C:/Users/Alex/Downloads/CrystalWarpRando/out.gbc")



