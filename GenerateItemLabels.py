import json
import os
import re
import mmap

import yaml

import LoadLocationData
import Static
import sys

class Item:
    Name = ""
    Price = 0
    HoldType = None
    Parameter = None
    Property = None
    Pocket = None
    Field = None
    Battle = None

def readAttributesFile(file):
    items = []
    attr_file = open(file)
    lines = attr_file.readlines()
    attr_file.close()
    start = False
    item_name = True
    currentObj = None
    for line in lines:
        line = line.strip()
        if start:
            if line == "; entries correspond to item ids":
                continue
            if item_name:
                name = line[2:]
                item_name = False
                currentObj = Item()
                currentObj.Name = name
            else:
                sp = line.split(",")
                maybe_price = sp[0].replace("item_attribute", "").strip()

                if maybe_price.startswith("$"):
                    maybe_price = 0

                currentObj.Price = int(maybe_price)
                currentObj.Pocket = sp[4].strip()

                items.append(currentObj)
                currentObj = None
                item_name = True
        else:
            if line == "ItemAttributes:":
                start = True
                item_name = True

    return items

def GenerateAttributeLabels():
    romDirectory = "RandomizerRom"
    attribute_file_location = romDirectory+"/"+"data/items/attributes.asm"

    item_attr_file_data = open(attribute_file_location, encoding="utf8")
    data = item_attr_file_data.read()
    item_attr_file_data.close()

    items = readAttributesFile("Data/item_attributes.asm")

    #; MASTER_BALL
	#item_attribute 0, HELD_NONE, 0, CANT_SELECT, BALL, ITEMMENU_NOUSE, ITEMMENU_CLOSE

#item_attribute $0, HELD_NONE, 0, CANT_SELECT | CANT_TOSS, KEY_ITEM, ITEMMENU_NOUSE, ITEMMENU_NOUSE
    item_match_regex_base = "; {ITEMNAME}\s{2,}item_attribute [\d$]{1,5}, HELD_[A-Z_]{1,20}, [\d-]{1,3}, [A-Z_ |]{1,35}, [A-Z_]{1,10}, ITEMMENU_[A-Z]{1,20}, ITEMMENU_[A-Z]{1,20}\n"

    for item in items:
        if "$" in item.Name:
            continue

        specific_regex = item_match_regex_base.replace("{ITEMNAME}",item.Name)

        matches = re.findall(specific_regex, data)
        if len(matches) == 0:
            raise Exception("Cannot find item to label::", item.Name)

        match = matches[0]

        labelBase = ".ckir_{}_ItemAttribute_{}::"
        labelBefore = labelBase.format("BEFORE", item.Name)
        labelAfter = labelBase.format("AFTER", item.Name)

        change_to_make = labelBefore + "\n" + match + labelAfter + "\n"
        data = data.replace(match, change_to_make)

    item_attr_file_data = open(attribute_file_location, "w", encoding="utf8")
    item_attr_file_data.write(data)
    item_attr_file_data.close()

    return



if __name__ == '__main__':
    sys.exit(0)



