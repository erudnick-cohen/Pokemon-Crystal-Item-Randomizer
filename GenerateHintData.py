import json
import os
import re

import Static

ROM_DIRECTORY = "RandomizerRom"
MAPS_DIRECTORY = "maps"



class MapDetail:
    blk_file = None
    width = None
    height = None
    sign_tile = None
    sign_pos = None
    tileset = None
    address = None
    label = None

    def __init__(self):
        self.address = None

    def printObj(self):
        print(self.label, self.blk_file, self.width, self.height,
              self.sign_tile, self.sign_pos, self.tileset, self.address)


class SignEntry:
    start_label = None
    end_label = None
    commands = None
    mapInfo = None
    mapFile = None
    blocks_before_label = None
    signLabel = None


def convertTile(tile, tileset):
    tileset_simple = tileset.replace("TILESET_", "")
    tileData = {('45', "JOHTO"): '1', \
                ('47', "JOHTO"): '2',
                ('8', "KANTO"): '1',
                ('56', "KANTO"): '77',
                ('79', "KANTO"): '7b',
                ('77', "JOHTO_MODERN"): '6',
                ('45', "JOHTO_MODERN"): '1',
                ('65', "JOHTO_MODERN"): '1',
                ('47', "JOHTO_MODERN"): '2',
                ('3c', "JOHTO_MODERN"): '2',
                ('3d', "JOHTO_MODERN"): '3f',
                ('78', "JOHTO_MODERN"): '49',
                ('15', "PARK"): '1',
                ('17', "PARK"): '1',
                ('2', "RADIO_TOWER"): '4',
                ('13', "RADIO_TOWER"): '1',

                ('25', "TRAIN_STATION"): '-1',  # Contains TWO signs!
                ('21', "BATTLE_TOWER_OUTSIDE"): '1',
                ('33', "JOHTO_MODERN"): '-1',  # Mart?
                ('78', "JOHTO"): '1',
                ('73', "KANTO"): '-1',  # Not Used
                ('12', "KANTO"): '-1',  # Gym Door??
                ('13', "FOREST"): '1',
                ('29', "HOUSE"): '3'
                }

    if (tile, tileset_simple) in tileData:
        return tileData[(tile, tileset_simple)]
    else:
        print("Unknown convert tile:", tile, tileset)

def textToLabelNames(orig_label):
    l = orig_label.replace("\n", "")
    #SlowpokeWellB2FGymGuyScript.ckir_BEFOREKINGSROCKGUY0ITEMCODE
    entry_key = ".ctir_{}_{}::\n"
    before_label = entry_key.format("BEFORE", l)
    end_label = entry_key.format("AFTER", l)

    return before_label, end_label

def blocksToLabelNames(orig_label):
    l = orig_label.replace("\n", "")
    entry_key = ".cbir_{}_{}_Blocks::\n"
    before_label = entry_key.format("BEFORE", l)
    after_label = entry_key.format("AFTER", l)

    return before_label, after_label


def getTilesetForMap(file):
    map_detail_file = "data/maps/maps.asm"
    map_file = ROM_DIRECTORY + "/" + map_detail_file

    map_file_data = open(map_file, encoding="utf8")
    data = map_file_data.readlines()
    map_file_data.close()

    file_name = file.replace(".asm", "")

    # How do we get the actual map name e.g. NewBarkTown / PlayersHouse1F

    tileset_get = "\tmap "+file_name+", (.*){1,}"
    tileset_match = re.compile(tileset_get)

#'	map NewBarkTown, TILESET_JOHTO, TOWN, LANDMARK_NEW_BARK_TOWN, MUSIC_NEW_BARK_TOWN, FALSE, PALETTE_AUTO, FISHGROUP_OCEAN

    find_calls = list(filter(tileset_match.match, data))
    if len(find_calls) != 1:
        return None

    tileset = find_calls[0].split(",")[1].strip()
    return tileset


def getMapSize(file):
    file_name = file.replace(".asm", "")

    attr_file = "data/maps/attributes.asm"
    attr_file_name = ROM_DIRECTORY + "/" + attr_file

    map_file_data = open(attr_file_name, encoding="utf8")
    data_map = map_file_data.readlines()
    map_file_data.close()

    attr_get = "\tmap_attributes "+file_name+",(.*){1,}"
    attr_match = re.compile(attr_get)
    find_calls = list(filter(attr_match.match, data_map))
    if len(find_calls) != 1:
        return None

    attr_name = find_calls[0].split(",")[1].strip()

    size_file = "constants/map_constants.asm"
    size_file_name = ROM_DIRECTORY + "/" + size_file

    map_file_data = open(size_file_name, encoding="utf8")
    data_size = map_file_data.readlines()
    map_file_data.close()

    size_get = "\tmap_const "+attr_name+",(.*){1,}"
    size_match = re.compile(size_get)
    find_calls = list(filter(size_match.match, data_size))
    if len(find_calls) != 1:
        return None

    size_split = find_calls[0].split(",")
    width = size_split[1].strip()
    height = size_split[2].split(";")[0].strip()

    return int(width), int(height)


def loadBlkFile(blk_file):
    f = open(blk_file, "rb")

    bs = f.read(1)
    blk_data = []
    while bs != b"":
        for b in bs:
            hex_rep = str(hex(int(str(b))))[2:]
            blk_data.append(hex_rep)
            bs = f.read(1)

    f.close()

    return blk_data


def getAssociatedMapData(label, file, file_data):
    blk_file = file.replace("asm", "blk")
    blk_path = ROM_DIRECTORY+"/"+MAPS_DIRECTORY+"/"+blk_file

    label = label.replace(":","").strip()

    if not os.path.isfile(blk_path):
        return None

    regex_call = "\tjumptext {}".format(label)
    call_match = re.compile(regex_call)

    find_calls = list(filter(call_match.match, file_data))
    if len(find_calls) != 1:
        return None

    element = file_data.index(find_calls[0])
    call_label = file_data[element-1].replace(":","")

    # bg_event  8,  8, BGEVENT_READ, NewBarkTownSign

    regex_sign = "\tbg_event\s{1,}\d{1,},\s{0,}\d{1,},\s{0,}BGEVENT_READ,\s{0,}"+call_label
    map_entry = re.compile(regex_sign)
    map_references = list(filter(map_entry.match, file_data))

    if len(map_references) != 1:
        return None

    lineToSplit = map_references[0]
    eventUsage = lineToSplit.split(",")
    x_value = int(eventUsage[0].replace("bg_event","").strip())
    y_value = int(eventUsage[1].strip())

    tileset = getTilesetForMap(file)
    width, height = getMapSize(file)

    blk_data = loadBlkFile(blk_path)

    if x_value % 2 == 0:
        x_blk = int(x_value / 2)
    else:
        x_blk = int((x_value - 1) / 2)

    if y_value % 2 == 0:
        y_blk = int(y_value / 2)
    else:
        y_blk = int((y_value - 1) / 2)

    blk_pos = (y_blk * width) + x_blk
    t_detail = blk_data[blk_pos]

    detail = MapDetail()
    detail.label = label
    detail.blk_file = blk_file
    detail.width = width
    detail.height = height
    detail.sign_tile = t_detail
    detail.sign_pos = blk_pos
    detail.tileset = tileset


    return detail












def GenerateHintLabels():

    mapFiles = ROM_DIRECTORY + "/" + MAPS_DIRECTORY
    map_files = os.listdir(mapFiles)
    # warp_event  1,  3, CELADON_DEPT_STORE_1F, -1



    #regex = "NewBarkTownSignText:"
    regex = "[A-Za-z0-9]{0,}(TrainerTips[A-Za-z0-9]{0,}Text|SignpostText|SquareText|NoticeText|DescriptionText|Directory[A-Za-z0-9]{0,}Text|(Sign(?!(al))[A-Za-z0-9]{0,}Text))[A-Za-z0-9]{0,}:"
    hint_box_match = re.compile(regex)

    blocks_file = ROM_DIRECTORY + "/" + "data/maps/blocks.asm"

    map_file_data = open(blocks_file, encoding="utf8")
    blocks_data = map_file_data.readlines()
    map_file_data.close()

    signEntries = []

    for m in map_files:

        extension = m.split(".")[-1]
        if extension != "asm":
            continue

        map_file_data = open(mapFiles+"/"+m, encoding="utf8")
        data = map_file_data.readlines()
        map_file_data.close()

        text_instances = list(filter(hint_box_match.match, data))
        for match in text_instances:

            if "Unused" in match:
                continue
            # These labels are already present in the code
            # So we just need to find them, verify they are text only
            # And then store in a list

            start_line = data.index(match)
            line = data[start_line].strip()
            line_iterator = 0
            command_count = 1
            is_unused = False
            pass_til_else = False
            while True:
                if line == "done":
                    if not pass_til_else:
                        break
                if pass_til_else:
                    if line == "else":
                        pass_til_else = False
                    else:
                        pass
                elif line.startswith("text"):
                    command_count += 1
                elif line.startswith("para"):
                    command_count += 1
                elif line.startswith("line"):
                    command_count += 1
                elif line.startswith("cont"):
                    command_count += 1
                elif line.endswith(":"):
                    pass
                elif len(line.strip()) == 0:
                    pass
                elif line == "if DEF(_CRYSTAL_AU)":
                    pass
                    pass_til_else = True
                elif "unused" in line:
                    is_unused = True
                    break
                elif "jumpstd" in line:
                    is_unused = True
                    break
                elif "jumptext" in line:
                    is_unused = True
                else:
                    print("unknown line handle:", line)

                line_iterator += 1
                line = data[start_line+line_iterator].strip()

            # End label can contain all the needed info?
            # Still need the other label for the BEFORE/AFTER to work correctly

            if is_unused:
                continue

            start_label, end_label = textToLabelNames(match.replace(":", ""))
            data.insert(start_line + 1, start_label)
            data.insert(start_line + line_iterator + 2, end_label)

            map_details = getAssociatedMapData(match, m, data)

            sign = SignEntry()
            sign.start_label = start_label.strip()[1:-2]
            sign.end_label = end_label.strip()[1:-2]
            sign.commands = command_count
            sign.mapInfo = map_details
            sign.mapFile = m
            sign.signLabel = match.strip()[0:-1]
            # Also label the blocks file in data/maps/blocks.asm
            # So we have a before/after for these too

            if map_details is not None:
                base_file_from_blk = map_details.blk_file.replace(".blk","")

                start_label, end_label = blocksToLabelNames(base_file_from_blk)
                if start_label not in  blocks_data:
                    regex_blocks = "{}_Blocks:".format(base_file_from_blk)
                    blocks_match = re.compile(regex_blocks)

                    find_calls = list(filter(blocks_match.match, blocks_data))
                    if len(find_calls) != 1:
                        return None

                    element = find_calls[0]
                    ind = blocks_data.index(element)

                    reverse_iterator = 0
                    line_reverse = blocks_data[ind - 1]

                    reverse_found = []

                    while not line_reverse.strip().startswith("INCBIN"):
                        reverse_iterator += 1
                        if len(line_reverse.strip()) > 0:
                            if not ("ir_AFTER" in line_reverse \
                                    or "SECTION" in line_reverse): # Start of maps file
                                reverse_found.append(line_reverse.strip())

                        line_reverse = blocks_data[ind - 1 - reverse_iterator]

                    if len(reverse_found) > 0:
                        # This is a shared map so harder to safely say
                        # May not succeed in finding map in earlier step
                        print("Cannot use:",match.strip(), "due to surronding other map data")
                        continue

                    iterator = 0
                    line = blocks_data[ind+1]
                    labels_found = []

                    while not line.strip().startswith("INCBIN"):
                        if line.strip().endswith(":"):
                            labels_found.append(line.strip())
                        iterator += 1
                        line = blocks_data[ind+1+iterator]

                    problem_labels = 0
                    label_counter = 0
                    for l in labels_found:
                        if "ir_BEFORE_" in l or "ir_AFTER" in l:
                            label_counter += 1
                            print("Found other label")
                        elif l != "NationalParkBugContest_Blocks:":
                            problem_labels += 1
                        else:
                            label_counter += 1

                    if problem_labels > 0:
                        print("Unable to use ", match.strip(), "due to ", element.strip() ,"multi-map")
                        continue

                    blocks_data.insert(ind+1 + label_counter, start_label)
                    blocks_data.insert(ind+iterator+3, end_label)

                sign.blocks_before_label = start_label.strip()[1:-2]


            signEntries.append(sign)


        if len(text_instances) > 0:
            map_file_data = open(mapFiles + "/" + m, "w", encoding="utf8")
            map_file_data.writelines(data)
            map_file_data.close()

        # GoldenrodDeptStoreRoof_Blocks
        # Blocks labels are defined like this, so long as these match an example we can get the details

    map_file_data = open(blocks_file, "w", encoding="utf8")
    map_file_data.writelines(blocks_data)
    map_file_data.close()


    return signEntries

def createSignJson(entries):
    yamlfile = open(Static.hint_labels_file, encoding='utf-8')
    yamltext = yamlfile.read()
    addressLists = json.loads(yamltext)
    addressData = {}
    for i in addressLists:
        addressData[i['label'].split(".")[-1]] = i


    yamlfile_b = open(Static.blocks_labels_file, encoding='utf-8')
    yamltext_b = yamlfile_b.read()
    addressLists_b = json.loads(yamltext_b)
    addressDataBlocks = {}
    for i in addressLists_b:
        addressDataBlocks[i['label'].split(".")[-1]] = i

    json_list = []

    for entry in entries:
        addrInfo = addressData[entry.start_label]
        mapInfo = entry.mapInfo

        valid_tile = None
        if mapInfo is not None:
            addrInfoBlocks = addressDataBlocks[entry.blocks_before_label]

            int_values = addrInfoBlocks["integer_values"].split(" ")
            hex_values = addrInfoBlocks["hex_values"].split(" ")
            sign_reference = hex_values[mapInfo.sign_pos]

            if sign_reference[1:] == mapInfo.sign_tile:
                tile_hex = convertTile(str(mapInfo.sign_tile), mapInfo.tileset)
                tile_int = int(tile_hex,16)
                if tile_int != -1:
                    valid_tile = tile_int

        if valid_tile is not None:
            obj = {
                "start": addrInfo["address_range"]["begin"],
                "end": addrInfo["address_range"]["end"]-1,
                "name": entry.signLabel,
                "map": entry.mapFile,
                "commands": entry.commands,
                "originalTile" : int(int_values[mapInfo.sign_pos]),
                "newTile": tile_int,
                "tileAddress": addrInfoBlocks["address_range"]["begin"] + mapInfo.sign_pos
            }

        else:
            obj = {
                "start": addrInfo["address_range"]["begin"],
                "end": addrInfo["address_range"]["end"]-1,
                "name": entry.signLabel,
                "map": entry.mapFile,
                "commands": entry.commands
                #"originalTile": None,
                #"newTile": None,
                #"tileAddress": None
            }

        json_list.append(obj)

    newfilestream = open("Config/NewSignData.json", "w")
    json_string = json.dumps(json_list, indent=4)
    newfilestream.write(json_string)
    newfilestream.close()


    # Take created data file and get address data from this
    # Use entry data and formulate complete (current) hint json file
    return
