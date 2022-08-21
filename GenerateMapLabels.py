import json
import os
import re
import mmap

import yaml

import LoadLocationData

def blocksToLabelNames(orig_label):
    l = orig_label.replace("\n", "")
    entry_key = ".ckir_{}_{}_Blocks::\n"
    before_label = entry_key.format("BEFORE", l)
    after_label = entry_key.format("AFTER", l)

    return before_label, after_label

def LabelAllBlocks():
    ROM_DIRECTORY = "RandomizerRom"
    blocks_file = ROM_DIRECTORY + "/" + "data/maps/blocks.asm"

    map_file_data = open(blocks_file, encoding="utf8")
    blocks_data = map_file_data.readlines()

    regex_blocks = "[a-zA-Z0-9]{1,}_Blocks:"
    blocks_match = re.compile(regex_blocks)

    find_calls = list(filter(blocks_match.match, blocks_data))


    for found in find_calls:
        base_name = found[0:found.index("_Blocks")]
        start_label, end_label = blocksToLabelNames(base_name)

        instance = blocks_data.index(found)


        line_reverse = blocks_data[instance - 1]
        reverse_iterator = 0
        reverse_found = []

        while not line_reverse.strip().startswith("INCBIN"):
            reverse_iterator += 1
            if len(line_reverse.strip()) > 0:
                if not ("ir_AFTER" in line_reverse \
                        or "SECTION" in line_reverse): # Start of maps file
                    reverse_found.append(line_reverse.strip())

            line_reverse = blocks_data[instance - 1 - reverse_iterator]

        iterator = 0
        line = blocks_data[instance + 1]

        while not line.strip().startswith("INCBIN"):
            iterator += 1
            line = blocks_data[instance + 1 + iterator]

        blocks_data.insert(instance + 1 + iterator, start_label)
        blocks_data.insert(instance + iterator + 3, end_label)

    print(blocks_data)

    map_file_data = open(blocks_file, "w", encoding="utf8")
    map_file_data.writelines(blocks_data)
    map_file_data.close()


def CreateMapPatches():
    patchFile = "Patches Base/LightUpDarkCaves.json"
    default_label_file = "crystal-speedchoice-label-details.json"
    json_file_2 = default_label_file

    yamlfile2 = open(json_file_2, encoding='utf-8')
    yamltext2 = yamlfile2.read()
    addressLists2 = json.loads(yamltext2)
    addressData2 = {}
    for i in addressLists2:
        addressData2[i['label'].split(".")[-1]] = i

    mapEvents = list(filter(lambda x: "_mapdetail_" in x[0], addressData2.items()))

    all_map_events = []

    for mapEvent in mapEvents:
        print(mapEvent)
        mapEventInfo = mapEvent[1]

        ints_old = [ int(x) for x in mapEventInfo["integer_values"].split(" ") ]
        label = "MapGroup_Dungeons."+mapEvent[0]
        description = "Enable flash in all dark caves"
        address_range = mapEventInfo["address_range"]
        ints_new = ints_old.copy()

        # map WhirlIslandNW, TILESET_DARK_CAVE, CAVE, LANDMARK_WHIRL_ISLANDS, MUSIC_UNION_CAVE, TRUE, PALETTE_DARK, FISHG$

        NO_LONGER_PALETTE_DARK = 18
        ints_new[7] = NO_LONGER_PALETTE_DARK

        obj = {
            "integer_values": {
                "old": ints_old,
                "new": ints_new
            },
            "address_range" : address_range,
            "label": label,
            "description": description
        }

        all_map_events.append(obj)

    map_flash_patch = json.dumps(all_map_events, indent=4)
    patch = open(patchFile, "w")
    patch.write(map_flash_patch)
    patch.flush()
    patch.close()




    return


def GenerateWarpMapDataLabels():
    romDirectory = "RandomizerRom"
    mapsDataFile = "data/maps/maps.asm"

    mapsFile = romDirectory + "/" + mapsDataFile

    # warp_event  1,  3, CELADON_DEPT_STORE_1F, -1

    # map WhirlIslandNW, TILESET_DARK_CAVE, CAVE, LANDMARK_WHIRL_ISLANDS, MUSIC_UNION_CAVE, TRUE, PALETTE_DARK, FISHG$
    regex = "\s{0,}map [a-zA-Z_0-9]{1,}, TILESET_[a-zA-Z_0-9]{1,}, [a-zA-Z_0-9]{1,}, [a-zA-Z_0-9]{1,}, [a-zA-Z_0-9]{1,}, " \
            "[a-zA-Z_0-9]{1,}, PALETTE_DARK, [a-zA-Z_0-9]{1,}"
    warp_data_match = re.compile(regex)

    map_file_data = open(mapsFile, encoding="utf8")
    data = map_file_data.readlines()
    map_file_data.close()

    dark_maps = list(filter(warp_data_match.match, data))

    iterator = 0
    for dark in dark_maps:
        where = data.index(dark)

        darkData = dark.split(",")
        darkName = darkData[0].split(" ")[1]

        before, after = mapEventToLabelNames(darkName, iterator)

        iterator += 1

        if data[where - 1].strip() != before and data[where + 1].strip() != after:
            data.insert(where, before + "\n")
            data.insert(where + 2, after + "\n")

    map_file_data = open(mapsFile, "w", encoding="utf8")
    map_file_data.writelines(data)
    map_file_data.close()



def mapEventToLabelNames(source,i):
    entry_key = "ckir"
    base_label = ".{}_{}_mapdetail_{}_{}::"

    map_source = source.replace("_","__").upper()

    before_label = base_label.\
        format(entry_key, "BEFORE", map_source, i)

    after_label = base_label. \
        format(entry_key, "AFTER", map_source, i)

    return before_label, after_label


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


if __name__ == '__main__':
    LabelAllBlocks()



