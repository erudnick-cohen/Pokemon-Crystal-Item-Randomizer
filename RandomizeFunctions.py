import csv
import json
import math
import random
import string
from collections import defaultdict

import Items
import LoadLocationData
import RandomizeItemsBadgesAssumedFill
import Version


def SpecialBytesConversion(text, safe, hintConfig):

    conversions = {"Badge":"📛",
                   "times":"❌"}
    inv_conversions = {v: k for k, v in conversions.items()}

    if safe:
        conversions = inv_conversions

    for conversion in conversions.items():
        key = conversion[0]
        replacement = conversion[1]

        if hintConfig is not None and key == "Badge" and not hintConfig.BadgeIcon:
            continue

        if key in text:
            text = text.replace(key, replacement)


    return text


class HintOptions:
    UseHints = False
    MaximumHints = 0
    MaxHintsPerItem = 0
    MaxHintsPerLocation = 1

    BarrenHints = False
    NotBarrenHints = False
    RequireHints = False
    InHints = False
    TagHints = False
    TrashHints = False
    UselessHints = False
    TMHints = False

    NoMultipleHints = True
    UselessHintChance = 0

    HideSigns = True
    IgnoreChamber = True
    IgnorePoster = True
    WriteXSigns = False
    BadgeIcon = False
    PriorityHintsOnly = False


    def __init__(self):
        self.UseHints = False

    #SmallHints = True
    #RunoutHints = True

def fileToLocation(file):
    if "Town" in file:
        file = file.replace("Town"," Town")

    if "City" in file:
        file = file.replace("City", " City")

    if "Island" in file:
        file = file.replace("Island", " Island")

    if ".asm" in file:
        file = file.replace(".asm", "")

    if "DeptStore" in file:
        file = file.replace("DeptStore", " City")

    for i in range (1, 7):
        floorFile = str(i)+"F"
        if floorFile in file:
            file = file.replace(floorFile, "")

    if "Route" in file:
        file = file.replace("Route", "Route ")

    if "CeladonMansion" in file:
        file = file.replace("CeladonMansion", "Celadon City")

    if "DragonsDenB" in file:
        file = file.replace("DragonsDenB", "Dragons Den")

    if "FightingDojo" in file:
        file = file.replace("FightingDojo", "Saffron City")

    if "LakeOfRage" in file:
        file = file.replace("LakeOfRage", "Lake Of Rage")

    if "LavRadioTower" in file:
        file = file.replace("LavRadioTower", "Lavender Town")

    if "RadioTower" in file:
        file = file.replace("RadioTower", "Radio Tower")

    if "NationalPark" in file:
        file = file.replace("NationalPark", "National Park")

    if "BugContest" in file:
        file = file.replace("BugContest", "")

    if "NewBark" in file:
        file = file.replace("NewBark", "New Bark")

    if "PokemonFanClub" in file:
        file = file.replace("PokemonFanClub", "Vermilion City")

    if "South" in file:
        file = file.replace("South", "")

    if "North" in file:
        file = file.replace("North", "")

    if "RuinsOfAlph" in file:
        file = "Ruins of Alph"

    if "SilverCaveOutside" in file:
        file = "Mt Silver"

    if "MountMoonSquare" in file:
        file = "Mt. Moon"

    if "Forest" in file:
        file = file.replace("Forest", " Forest")



    return file


def getHintsToRemove(hintData, hintOptions):
    deadHints = []
    for hint in hintData:
        if (hint[1].type == "runout" or hint[1].type == "small") \
                and hasattr(hint[0], 'originalTile') and hasattr(hint[0], 'newTile') and hasattr(hint[0], 'tileAddress') \
                and hint[0].originalTile != hint[0].newTile and \
                hint[0].originalTile is not None and hint[0].newTile is not None and hint[0].tileAddress is not None:
            deadHints.append(hint)

    return deadHints



def ConvertHintLevelToFlags(level, MaxHints=None):
    Options = HintOptions()
    if level == 0:
        Options.UseHints = False

    if level >= 1:
        Options.MaxHintsPerLocation = 1
        Options.UseHints = True
        Options.BarrenHints = True
        Options.NotBarrenHints = True
        Options.PriorityHintsOnly = True
        Options.MaximumHints = 20
        Options.MaxHintsPerItem = 1

    if level >= 2:
        Options.PriorityHintsOnly = False
        Options.MaximumHints = 50

    if level >= 3:
        Options.RequireHints = True

    if level >= 4:
        Options.InHints = True
        Options.MaximumHints = 100
        Options.MaxHintsPerLocation = 99
        #Options.TrashHints = True

    if level >= 5:
        Options.MaxHintsPerLocation = 99
    # flag_list.append('TM Hints')

    if level >= 6:
        Options.MaximumHints = 200
        Options.MaxHintsPerItem = 2
        Options.UselessHints = True
        Options.UselessHintChance = 0.5
    # flag_list.append('Useless Hints')

    if level >= 7:  # Dev only
        Options.TagHints = True

    if MaxHints is not None:
        Options.MaximumHints = MaxHints

    return Options

def checkIfReplacementsConfigured(inputFlags):
    for option in inputFlags:
        if "Replace " in option:
            return True
    return False


def FlagCheckType(type, inputFlags):
    flagExtend = "Replace " + type
    if flagExtend in inputFlags:
        return True

    return False


def HandleItemReplacement(trashList, inputFlags):
    replacementFile = None

    containsAny = checkIfReplacementsConfigured(inputFlags)

    #item_replacement_file = "Config/ItemReplacementChoatix.json"
    item_replacement_file = "Config/ItemReplacement.json"

    if containsAny:
        item_replacement = open(item_replacement_file,encoding='utf-8')
        replacements = item_replacement.read()
        replacement_data = json.loads(replacements)
        replacementFile = {}
        for replacement_item in replacement_data:
            replacement_item_name = replacement_item["item"]
            replacement_replacement = replacement_item["replacement"]
            replacement_type = replacement_item["type"]

            replacement_percent = 100
            use_replacement_percent = "Always Upgrade" not in inputFlags

            if use_replacement_percent and "chance" in replacement_item:
                replacement_percent = replacement_item["chance"]

            useReplacement = FlagCheckType(replacement_type, inputFlags)
            if useReplacement:
                if not replacement_item_name in replacementFile:
                    replacementFile[replacement_item_name] = []
                replacementFile[replacement_item_name].append((replacement_replacement, replacement_percent))

    if 'Delete Fly' in inputFlags:
        if replacementFile is None:
            replacementFile = {}

        replacementFile["Fly"]: "BERRY"

    changes = []

    if replacementFile is not None:
        for itemName in trashList:
            replaced = ReplaceItem(itemName, replacementFile)
            if replaced is not None:
                changes.append((itemName, replaced))

    return changes


def ReplaceItem(itemIn, replaceFile):
    itemName = itemIn
    while itemName in replaceFile:
        replace_cycle = False
        possibilities = replaceFile[itemName]
        random.shuffle(possibilities)
        for p in possibilities:
            item_chance = p[1]
            if item_chance >= random.random() * 100:
                itemName = p[0]
                replace_cycle = True
                break
        if not replace_cycle:
            break

    if itemIn != itemName:
        return itemName

    return None


def IterateRequirements(location, locations, known, partial_known=None):

    if partial_known is None:
        partial_known = []

    addedLocation = []
    addedFlag = []
    addedItem = []

    for req in location.LocationReqs:
        if req == "Impossible" or req == "Unreachable" or req == "Banned":
            continue
        reqData = list(filter(lambda x: x.Name == req, locations))
        if len(reqData) == 0:
            print("Could not find LOCATION:", req)
            return [], [], []
        # Currently assume if more than one, that they are options
        allRequiredLoc = []
        allRequiredFlag = []
        allRequiredItem = []
        for data in reqData:
            if data in known:
                allRequiredLoc.extend(data.LocationReqs)
                allRequiredFlag.extend(data.FlagReqs)
                allRequiredItem.extend(data.ItemReqs)
                continue
            if data in partial_known:
                allRequiredLoc.extend(data.LocationReqs)
                allRequiredFlag.extend(data.FlagReqs)
                allRequiredItem.extend(data.ItemReqs)
                continue
            else:
                partial_known.append(data)
            locs, flags, items = IterateRequirements(data, locations, known, partial_known)

            # Only add one instance from requirements
            for newReq in locs:
                if newReq not in data.LocationReqs:
                    data.LocationReqs.append(newReq)

            for newReq in flags:
                if newReq not in data.FlagReqs:
                    data.FlagReqs.append(newReq)

            for newReq in items:
                if newReq not in data.ItemReqs:
                    data.ItemReqs.append(newReq)

            allRequiredLoc.extend(locs)
            allRequiredFlag.extend(flags)
            allRequiredItem.extend(items)
            known.append(data)

        # allRequiredLoc.extend(data.LocationReqs)
        # allRequiredFlag.extend(data.FlagReqs)
        # allRequiredItem.extend(data.ItemReqs)

        for x in allRequiredLoc:
            if x not in addedLocation and (len(reqData) == 1 or allRequiredLoc.count(x) == len(reqData)):
                addedLocation.append(x)

        for x in allRequiredFlag:
            if x not in addedFlag and (len(reqData) == 1 or allRequiredFlag.count(x) == len(reqData)):
                addedFlag.append(x)

        for x in allRequiredItem:
            if x not in addedItem and (len(reqData) == 1 or allRequiredItem.count(x) == len(reqData)):
                addedItem.append(x)

    for flagSet in location.FlagReqs:
        reqData = list(filter(lambda x: flagSet in x.FlagsSet, locations))
        allRequiredLoc = []
        allRequiredFlag = []
        allRequiredItem = []

        if len(reqData) > 1:
            print("Handle multiple flag set locations")

        for data in reqData:

            if data.Name == "Most Map Access":
                continue

            if data in known:
                allRequiredLoc.extend(data.LocationReqs)
                allRequiredFlag.extend(data.FlagReqs)
                allRequiredItem.extend(data.ItemReqs)
                continue
            if data in partial_known:
                allRequiredLoc.extend(data.LocationReqs)
                allRequiredFlag.extend(data.FlagReqs)
                allRequiredItem.extend(data.ItemReqs)
                continue
            else:
                partial_known.append(data)
            locs, flags, items = IterateRequirements(data, locations, known, partial_known)

            # Only add one instance from requirements

            allRequiredLoc.extend(locs)
            allRequiredFlag.extend(flags)
            allRequiredItem.extend(items)
            known.append(data)

            allRequiredLoc.extend(data.LocationReqs)
            allRequiredFlag.extend(data.FlagReqs)
            allRequiredItem.extend(data.ItemReqs)

        for x in allRequiredLoc:
            if x not in addedLocation and (len(reqData) == 1 or allRequiredLoc.count(x) == len(reqData)):
                addedLocation.append(x)
            elif x not in addedLocation and (allRequiredLoc.count(x) < len(reqData)):
                print("optional loc:", x, data)

        for x in allRequiredFlag:
            if x not in addedFlag and (len(reqData) == 1 or allRequiredFlag.count(x) == len(reqData)):
                addedFlag.append(x)

        for x in allRequiredItem:
            if x not in addedItem and (len(reqData) == 1 or allRequiredItem.count(x) == len(reqData)):
                addedItem.append(x)

    parents = list(filter(lambda x: location in x.Sublocations, locations))
    while parents is not None and len(parents) > 0:
        parent = parents[0]

        addedItem.extend(list(filter(lambda x: x not in addedItem, parent.ItemReqs)))
        addedFlag.extend(list(filter(lambda x: x not in addedFlag, parent.FlagReqs)))
        addedLocation.extend(list(filter(lambda x: x not in addedLocation, parent.LocationReqs)))

        # addedItem.extend(parent.ItemReqs)
        # addedFlag.extend(parent.FlagReqs)
        # addedLocation.extend(parent.LocationReqs)

        if parent.Name not in addedLocation:
            addedLocation.append(parent.Name)

        parents = list(filter(lambda x: parent in x.Sublocations, locations))

    # addedLocation.append(reqData.Name)

    addedItem.extend(list(filter(lambda x: x not in addedItem, location.ItemReqs)))
    addedFlag.extend(list(filter(lambda x: x not in addedFlag, location.FlagReqs)))
    addedLocation.extend(list(filter(lambda x: x not in addedLocation, location.LocationReqs)))

    return addedLocation, addedFlag, addedItem


def PathToItem(item):
    replaceNames = {"BLUE_CARD": "Blue Card",
                    "ENGINE_POKEDEX": "Pokedex",
                    "OLD_ROD": "Old Rod",
                    "GOOD_ROD": "Good Rod",
                    "SUPER_ROD": "Super Rod",
                    "SILVER_WING": "Silver Wing",
                    "ITEMFINDER": "ItemFinder",
                    "COIN_CASE": "Coin Case",
                    "Elite Four": "Indigo Plateau",
                    "VS Ho-Oh": "Tin Tower Peak",
                    "Mt Mortar Surf Floor": "Mortar Surf",
                    "Mt Mortar Upper Floor": "Mortar Waterfall",
                    "Kanto Power Restored": "Kanto Power",
                    "Mahogany Rockets Defeated": "Mahogany Base Clear",
                    "Beat Team Rocket": "Saving Radio Tower",
                    "Rocket Invasion": "7 Badges",
                    "Open Mt. Silver": "Mt. Silver Early",
                    "Elm's Lab": "Elms Lab",
                    "S.S. Ticket": "SS Ticket",
                    "Became Champion": "Being Champion",

                    }

    if type(item) == str:
        item = item.replace(LoadLocationData.WARP_OPTION, "W")
    else:
        print("Type", type(item), item)

    if item in replaceNames:
        return replaceNames[item]
    else:
        return str(item).replace("_", " ").title()


class Msg:
    text = None
    padding = None
    seperator = None

    def __init__(self):
        self.text = ""
        self.padding = 0
        self.seperator = None


import re


class HintMessage():
    type = None
    item = None
    secondary = None
    helpful = None
    messages = None
    totalLength = None

    def reword(self):
        if self.item is not None:
            self.item = PathToItem(self.item)
        if self.secondary is not None:
            self.secondary = PathToItem(self.secondary)

    def flagModify(self, flags):
        if "Progressive Rods" in flags:
            if self.secondary == "Old Rod" or \
                    self.secondary == "Good Rod" or self.secondary == "Super Rod":
                self.secondary = "Rod"
            if self.item == "Old Rod" or \
                    self.item == "Good Rod" or self.item == "Super Rod":
                self.item = "Rod"

    def nothingToMaybe(self):
        if self.type == "nothingf":
            self.type = "nothingmf"
        elif self.type == "nothingl":
            self.type = "nothingml"
        elif self.type == "nothingi":
            self.type = "nothingmi"

    def __init__(self, type, item, secondary, helpful):
        self.type = type
        self.item = item
        self.secondary = secondary
        self.helpful = helpful
        self.messages = []
        self.reword()

    # print(self)

    def __str__(self):
        return str(self.item) + " " + str(self.type) + " " + str(self.secondary)

    def toMessages(self, length, parts=0, hintConfig=None):
        max_length_per_message = 17

        messages = []
        totalMessageLength = 0

        # types: requires, in, something, nothing

        if self.item is None and self.secondary is None:
            msg = Msg()
            msg.text = "X"
            if self.type == "runout":
                msg.text = "XX"
            messages.append(msg)
        elif self.item is None:
            msg = Msg()
            msg.text = self.secondary
            msg.seperator = 81

            msg2 = Msg()

            if self.type == "somethingi":
                msg2.text = self.secondary + "."
                msg.text = "A champ has"
            elif self.type == "somethingf":
                msg.text = "Champs do"
                msg2.text = self.secondary + "."
            elif self.type == "somethingl":
                msg.text = "Champs go to"
                msg2.text = self.secondary + "."
            elif self.type == "nothingl":
                msg2.text = "is barren."
            elif self.type == "nothingi":
                msg2.text = "is a fools toy."
            elif self.type == "nothingf":
                msg.text = "Fools do"
                msg2.text = self.secondary

            elif self.type == "nothingml":
                msg2.text = "may be barren."
            elif self.type == "nothingmi":
                msg2.text = "may be a fools toy."
            elif self.type == "nothingmf":
                msg.text = "Fools may do"
                msg2.text = self.secondary

            messages.append(msg)
            messages.append(msg2)

        else:
            msg1 = Msg()
            msg1.seperator = 79

            msg2 = Msg()
            msg2.seperator = 81
            msg3 = Msg()
            msg3.seperator = 79
            msg4 = Msg()

            if self.type == "requiresf":
                msg1.text = "A champ requires"
                msg2.text = self.secondary
                msg3.text = "to access "
                msg4.text = self.item
            elif self.type == "requiresi":
                msg1.text = "A champ requires"
                msg2.text = self.secondary
                msg3.text = "to access"
                msg4.text = self.item
            elif self.type == "requiresl":
                msg1.text = "A champ vists"
                msg2.text = self.secondary
                msg3.text = "to access"
                msg4.text = self.item
            elif self.type == "in":
                msg1.text = self.item
                msg2.text = "is in "
                msg3.text = self.secondary
            elif self.type == "tag":
                msg1.text = self.item
                msg2.text = "times " + str(self.secondary)
            elif self.type == "conf":
                msg1.text = self.item
                msg2.text = "is " + str(self.secondary)
            elif self.type == "attag":
                msg1.text = self.item
                msg2.text = "is " + self.secondary

            messages.append(msg1)
            messages.append(msg2)
            if len(msg3.text) > 0:
                messages.append(msg3)
            if len(msg4.text) > 0:
                messages.append(msg4)

        while len(messages) > 0 and messages[-1].seperator is not None:
            if len(messages[-1].text) < 0:
                messages.remove(messages[-1])
            else:
                messages[-1].seperator = None

        for message in messages:
            message.text = SpecialBytesConversion(message.text, safe=False, hintConfig=hintConfig)

        # Take messages which are too long, and combine them into previous/next messages
        messagesTooLong = list(filter(lambda x: len(x.text) > max_length_per_message, messages))
        while len(messagesTooLong) > 0:
            for tl in messagesTooLong:
                index = messages.index(tl)
                previousPossible = True
                nextPossible = True
                if index == 0:
                    previousPossible = False
                if index == len(messages)-1:
                    nextPossible = False

                if previousPossible:
                    wordCutLeft = tl.text.split(" ")[0]
                    previous = messages[index - 1]
                    previousLength = len(previous.text)

                    if previousLength + len(wordCutLeft) + 1 < max_length_per_message:
                        previous.text += " " + wordCutLeft
                        tl.text = re.sub("^" + wordCutLeft, "", tl.text).strip()
                    else:
                        previousPossible = False

                nextPossible = nextPossible and len(tl.text.split(" ")) > 1

                if nextPossible:
                    wordCutRight = tl.text.split(" ")[-1]
                    next = messages[index + 1]
                    nextLength = len(next.text)

                    if nextLength + len(wordCutRight) + 1 < max_length_per_message:
                        next.text = wordCutRight + " " + next.text

                        tl.text = re.sub(wordCutRight+"$", "", tl.text).strip()
                    else:
                        nextPossible = False

                if not nextPossible and not previousPossible:
                    newMessage = Msg()
                    wordCutRight = tl.text.split(" ")[-1]
                    newMessage.text += wordCutRight
                    tl.text = re.sub(wordCutRight + "$", "", tl.text).strip()

                    if tl.seperator is None:
                        tl.seperator = 79

                    insertAt = index + 1
                    if index == len(messages):
                        insertAt = len(messages)
                    else:
                        newMessage.seperator = 79

                    messages.insert(insertAt, newMessage)
            messagesTooLong = list(filter(lambda x: len(x.text) > max_length_per_message, messages))

        totalMessageLength += 1  # Starting byte
        for m in messages:
            totalMessageLength += len(m.text)
            if m.seperator is not None:
                totalMessageLength += 1

        if totalMessageLength > length:
            return False

        expansionChoices = messages.copy()
        while totalMessageLength < length and len(expansionChoices) > 0:
            chosen = random.choice(expansionChoices)
            if len(chosen.text) + chosen.padding > max_length_per_message:
                expansionChoices.remove(chosen)
                continue
            chosen.padding += 1
            totalMessageLength += 1

        while totalMessageLength < length:
            messages[-1].seperator = 78
            msgBlank = Msg()
            mLength = (length - totalMessageLength)
            if mLength > max_length_per_message:
                mLength = max_length_per_message
            msgBlank.text = ""
            msgBlank.padding += mLength
            messages.append(msgBlank)
            totalMessageLength += mLength

        self.messages = messages
        self.totalLength = totalMessageLength
        return True


class AddrObject:
    start = None
    end = None
    item = None
    length = None
    commands = None
    name = None
    messages = []
    map = None
    originalTile = None
    newTile = None
    tileAddress = None
    locationRef = None

    def __init__(self, item, start, end, commands, name, map,
                 originalTile=None, newTile=None, tileAddress=None):
        self.item = item
        self.start = start
        self.end = end
        self.commands = commands
        self.length = self.end - self.start
        self.name = name
        self.map = map

        if originalTile is not None and newTile is not None and tileAddress is not None:
            self.originalTile = originalTile
            self.newTile = newTile
            self.tileAddress = tileAddress


def dropMessageLocation(locationList, currentHint, addr, hintConfig, hintMapping):

    if addr.locationRef in hintMapping:
        current_count = hintMapping[addr.locationRef]
        if current_count >= hintConfig.MaxHintsPerLocation:
            return True


    # In future versions, these will be more in-depth with complex logic handling



    relevant = list(filter(lambda x: x.Name == addr.locationRef, locationList))
    if len(relevant) == 1:
        relevant = relevant[0]
    else:
        return False

    for x in relevant.FlagReqs:
        if currentHint.type == "in" and currentHint.item == x:
            return True

    for x in relevant.ItemReqs:
        if currentHint.type == "in" and currentHint.item == x:
            return True

    for x in relevant.LocationReqs:
        if currentHint.item == x or currentHint.secondary == x:
            return True


    return False


def PrepareHintMessages(addressData, hints, priorities, flags, hintConfig, locationList):
    # [{"start": 1870726, "end": 1870758
    #	 , "name": "MasterBall", "commands": 2},

    addObjects = []
    for address in addressData.keys():
        addObj = addressData[address]

        if hintConfig.IgnoreChamber and re.match(r".*ChamberDescription.*",addObj["name"]):
            continue

        if hintConfig.IgnorePoster and \
                (re.match(r".*RadioTower.F.*", addObj["name"]) or
                 re.match(r".*DeptStore.F.*", addObj["name"]) or
                 re.match(r".*MansionManagersSuite.*", addObj["name"]) or
                 re.match(r".*Mansion\dF.*", addObj["name"]) or
                 re.match(r".*FanClub.+SignText", addObj["name"]) or
                 re.match(r".*FightingDojo.*\d.*", addObj["name"]) or
                 re.match(r".*TrainerHouse.*\d.*", addObj["name"])

                    #TrainerHouseSign1Text
                    #FightingDojoSign1Text
                    #CeladonMansionManagersSuiteSignText
                ):
            continue

        reference = fileToLocation(addObj["map"].split("/")[-1])

        toAddObject = None

        if 'originalTile' in addObj and 'newTile' in addObj and \
                'tileAddress' in addObj:
            toAddObject = AddrObject(address, addObj["start"], addObj["end"], addObj["commands"], addObj["name"], addObj["map"], \
                           addObj["originalTile"], addObj["newTile"], addObj["tileAddress"])
        else:
            toAddObject = AddrObject(address, addObj["start"], addObj["end"], addObj["commands"], addObj["name"], addObj["map"])

        if toAddObject is not None:

            toAddObject.locationRef = reference
            addObjects.append(toAddObject)



    # avItems = []
    # for x in available:
    # avItems.append(x.replace("_", "").replace(" ", "").upper())

    # {type=None,	item=None,	secondary=None,	helpful=None}
    # validAddresses = list(filter(lambda x: x.length > 2 and x.commands == 2 and x.item.upper() in avItems, addObjects))
    # Still in development!
    validAddresses = list(filter(lambda x: x.length > 0, addObjects))
    random.shuffle(validAddresses)

    # Shortest hint locations first, so shortest hints end up at these addresses more often!

    # test code
    # prints signs possible to be changed sorted by location
    # sortedVer = sorted(validAddresses, key=lambda lc: lc.map)
    # print(sortedVer)

    # for var in sortedVer:
    #	print(var.name, var.map)

    useHints = []

    # Implement hint priority system, e.g. part specific hint on specific sign
    # Main example: Set badge unlock requirement to Oak's Lab sign
    # Additional example: Set gym signs all to 'barren/required' checks
    # If no more hints left that have requirements, then can use anywhere, or exclude (config)
    # On the flip side, if there are locations which require one of these hints, do not use them all up!

    random.shuffle(hints)

    # Calculate all hints which match NO priorities here
    hintOptions = []
    hintLessOptions = []

    priorityAddresses = []

    hintMapping = {}

    for priority in priorities:
        hasPossible = False
        if len(priority.HintTypes) != 0 and len(priority.HintKeys) > 0:
            matches = list(filter(lambda x: x.type in priority.HintTypes and
                                            x.item in priority.HintKeys, hints))
            hasPossible = len(matches) > 0
            hintOptions = list(set(hintOptions) | set(matches))
        elif len(priority.HintKeys) == 0 and len(priority.HintTypes) != 0:
            matches = list(filter(lambda x: x.type in priority.HintTypes, hints))
            hasPossible = len(matches) > 0
            hintOptions = list(set(hintOptions) | set(matches))

        if hasPossible:
            priorityAddresses.append(priority.HintName)


    for x in hints:
        if x not in hintOptions:
            hintLessOptions.append(x)

    validAddresses = sorted(validAddresses, key=lambda x: int(x.name in priorityAddresses),
                            reverse=True)

    hintsWritten = 0

    for addr in validAddresses:
        if len(hints) == 0 or hintsWritten >= hintConfig.MaximumHints:
            empty = HintMessage("runout", None, None, False)
            empty.toMessages(addr.length, addr.commands)
            useHints.append((addr, empty))
            continue
        success = False

        readd_hints_priority = []
        readd_hints_normal = []
        while not success:
            list_readd = None
            if len(hints) <= 0:
                break

            hintItem = False

            if addr.name in priorityAddresses:
                addressItems = list(filter(lambda x: x.HintName == addr.name, priorities))
                possibleHints = []
                for a in addressItems:
                    matchHints = list(filter(lambda x: \
                                                 (len(a.HintKeys) == 0 and x.type in a.HintTypes) or \
                                                 (len(a.HintKeys) > 0 and x.type in a.HintTypes and x.item in a.HintKeys) \
                                             , hintOptions))
                    possibleHints = list(set(matchHints) | set(possibleHints))
                if len(possibleHints) > 0:
                    currentHint = random.choice(possibleHints)
                    hintOptions.remove(currentHint)
                    hintItem = True

            skip = False

            if hintItem:
                hints.remove(currentHint)
                list_readd = readd_hints_priority
            elif len(priorityAddresses) == 0 and len(hintOptions) > 0:
                multiHints = []
                multiHints += hintLessOptions
                multiHints += hintOptions
                currentHint = multiHints.pop(0)
                if currentHint in hintLessOptions:
                    hintLessOptions.remove(currentHint)
                if currentHint in hintOptions:
                    hintOptions.remove(currentHint)
                hints.remove(currentHint)
                list_readd = readd_hints_normal
            elif not hintItem and len(hintLessOptions) > 0:
                currentHint = hintLessOptions.pop(0)
                hints.remove(currentHint)
                list_readd = readd_hints_normal
            elif not hintItem:
                # run out of hintless hints
                currentHint = None
                list_readd = None
                break

            currentHint.flagModify(flags)

            if hintConfig.PriorityHintsOnly and not hintItem:
                drop = True
            else:
                drop = dropMessageLocation(locationList, currentHint, addr, hintConfig, hintMapping)

            if not drop:
                success = currentHint.toMessages(addr.length, addr.commands, hintConfig=hintConfig)
            else:
                success = False

            if success:
                useHints.append((addr, currentHint))
                hintsWritten += 1
                if hintItem:
                    priorityAddresses.remove(addr.name)
                if addr.locationRef not in hintMapping:
                    hintMapping[addr.locationRef] = 0
                hintMapping[addr.locationRef] +=1

            else:
                list_readd.append(currentHint)

        if not success:
            # Since small ones exist, we may also want to add code somewhere to MERGE hints into one
            # But what to do with the extra and keep the files the same size??
            # print("Unable to assign any remaining hints to: "+addr.name)
            # Create a hint to say TOO SMALL for this seed

            empty = HintMessage("small", None, None, False)
            empty.toMessages(addr.length, addr.commands)
            useHints.append((addr, empty))
        if len(readd_hints_normal) > 0:
            for i in readd_hints_normal:
                hintLessOptions.append(i)
                hints.append(i)
        if len(readd_hints_priority) > 0:
            for i in readd_hints_priority:
                hintOptions.append(i)
                hints.append(i)
    # random.shuffle(hints)

    # Debug Info
    hintlog = open("Hints.log", "w")

    for hint in useHints:
        hintAddr = hint[0]
        hintDetail = hint[1]

        message = ""
        for m in hintDetail.messages:
            message += m.text.strip() + " "

        hintdetail = str(hintAddr.item) + " " + str(message)
        hint_safe = SpecialBytesConversion(hintdetail, safe=True, hintConfig=hintConfig)
        hintlog.write(hint_safe + "\n")

    hintlog.close()

    for unusedHint in hints:
        success = unusedHint.toMessages(100, 5, hintConfig)
        message = ""
        for m in unusedHint.messages:
            message += m.text.strip() + " "

        #print("unused:", message)

    return useHints


def removeRedundantHints(hints, hintConfig, locationData):
    manualHintChecksBarrenUse = [

        # Example
        # If Indigo Plateau is not required, Ho-Oh is also not required
        # Reverse if also true, if Ho-Oh is required, Indigo hint is required

        {"typeFrom": "nothingl", "typeTo": "nothingf", "valueFrom":
            "Rocket Base", "valueTo": "Mahogany Base Clear"},
        {"typeFrom": "nothingl", "typeTo": "nothingf", "valueFrom":
            "Power Plant", "valueTo": "Kanto Power"},
        {"typeFrom": "nothingl", "typeTo": "nothingl", "valueFrom":
            "Pewter City", "valueTo": "Route 4"},
        {"typeFrom": "nothingl", "typeTo": "nothingl", "valueFrom":
            "Blackthorn City", "valueTo": "Dragons Den"},
        {"typeFrom": "nothingl", "typeTo": "nothingl", "valueFrom":
            "Tin Tower", "valueTo": "Tin Tower Peak"},
        {"typeFrom": "nothingl", "typeTo": "nothingl", "valueFrom":
            "Indigo Plateau", "valueTo": "Tin Tower Peak"}

    ]

    redundantHMBadgeHints = [{"badge": "Zephyr", "hm": "Flash"},
                             {"badge": "Hive", "hm": "Cut"},
                             {"badge": "Plain", "hm": "Strength"},
                             {"badge": "Fog", "hm": "Surf"},
                             {"badge": "Glacier", "hm": "Whirlpool"},
                             {"badge": "Rising", "hm": "Waterfall"}
                             ]

    REMOVE_DUPLICATE_LOCATION_HINTS = True

    byLocationMapping = {}
    hintsToRemove = []
    for hint in hints:
        if hint.type == "nothingl":
            hintLocation = list(filter(lambda x: x.Name == hint.secondary, locationData))
            if len(hintLocation) == 1:
                flags = hintLocation[0].FlagReqs
                if 'Mt. Silver Unlock' in flags:
                    hintsToRemove.append(hint)
                    continue
                if 'Impossible' in flags or "Banned" in flags or "Unreachable" in flags:
                    hintsToRemove.append(hint)
                    continue

        if hint.type == "in" or hint.type == "somethingf":
            if hint.secondary not in byLocationMapping:
                byLocationMapping[hint.secondary] = []
            byLocationMapping[hint.secondary].append(hint)

    for hint in hintsToRemove:
        print("Remove hint:", str(hint))
        hints.remove(hint)






    if not hintConfig.NoMultipleHints:
        multipleInstances = list(filter(lambda x: len(x[1]) > 1, byLocationMapping.items()))
        for instance in multipleInstances:
            useHint = random.choice(instance[1])
            for h in instance[1]:
                if h != useHint:
                    hints.remove(h)

    for item in redundantHMBadgeHints:
        itemFlag = item["badge"]
        itemItem = item["hm"]
        filterFlag = list(
            filter(lambda x: x.type == "requiresf" and x.secondary == itemFlag, hints))
        filterItem = list(filter(lambda x: x.type == "requiresi" and x.secondary == itemItem, hints))

        itemCrossover = {}
        for f in filterFlag:
            if not f.item in itemCrossover:
                itemCrossover[f.item] = []
            itemCrossover[f.item].append(f.item)
        for f in filterItem:
            if not f.item in itemCrossover:
                itemCrossover[f.item] = []
            itemCrossover[f.item].append(f.item)

        for crossover in itemCrossover.values():
            while len(crossover) > 1:
                deleteItem = random.choice(crossover)
                crossover.remove(deleteItem)
                if deleteItem in hints:
                    hints.remove(deleteItem)

    for item in manualHintChecksBarrenUse:
        typeFrom = item["typeFrom"]
        typeTo = item["typeTo"]

        hintFind_if = list(filter(lambda x: x.type == typeFrom
                                            and x.secondary == item["valueFrom"], hints))

        if len(hintFind_if) > 0:
            hintFind_remove = list(filter(lambda x: x.type == typeTo
                                                    and x.secondary == item["valueTo"],
                                          hints))
            if len(hintFind_remove) > 0:
                hints.remove(hintFind_remove[0])

        typeFromInvert = None
        typeToInvert = None
        if typeFrom == "somethingl":
            typeFromInvert = "nothingl"
        elif typeFrom == "nothingl":
            typeFromInvert = "somethingl"

        if typeTo == "somethingf":
            typeToInvert = "nothingf"
        elif typeTo == "nothingf":
            typeToInvert = "somethingf"

        if typeToInvert is not None and typeFromInvert is not None:
            hintFind_if_reverse = list(filter(lambda x: x.type == typeToInvert
                                                        and x.secondary == item["valueTo"], hints))

            if len(hintFind_if_reverse) > 0:
                hintFind_remove_reverse = list(filter(lambda x: x.type == typeFromInvert
                                                                and x.secondary == item["valueFrom"],
                                                      hints))
                if len(hintFind_remove_reverse) > 0:
                    hints.remove(hintFind_remove_reverse[0])





def isRequired(x, locationMapping, notRequiredItems, notRequiredFlags=None, requiredLocations=None):

    if notRequiredFlags is None:
        notRequiredFlags = []

    if requiredLocations is None:
        requiredLocations = []

    if x not in locationMapping:
        print("Error, location should be in mapping")
        return True

    requireThis = list(
        filter(lambda a: (hasattr(a, 'badge') and a.badge is not None) or a.item not in notRequiredItems,
               locationMapping[x]))
    required = len(requireThis) > 0
    for l in requireThis:
        for m in l.FlagReqs:
            if m in notRequiredFlags:
                required = False

        for x in l.LocationReqs:
            if x in requiredLocations:
                required = False

    return required

def containsAny(x, l):
    for req in x.LocationReqs:
        if req in l:
            return True
    return False

def GetItemChildren(location, locations, handled):
    items = []
    flags = []
    new_locations = []

    print("Check:", location.Name)

    if location.Name in handled:
        return handled[location.Name][0] , handled[location.Name][1], handled[location.Name][2]

    handled[location.Name] = (items,flags,new_locations)

    if "Impossible" in location.FlagReqs or "Banned" in location.FlagReqs or "Unreachable" in location.FlagReqs:
        return items,flags,new_locations

    if location.IsItem or location.IsGym:
        items.append(location)

    if len(location.FlagsSet) > 0:
        flags.extend(location.FlagsSet)

    if len(items) > 0:
        return items,flags, new_locations

    # TODO: Use sublocational to fix Date Ruined and other location chains?
    for sublocation in location.Sublocations:
        new_locations.append(sublocation.Name)
        more_items,more_flags,more_locations = GetItemChildren(sublocation, locations, handled)


        items.extend(more_items)
        flags.extend(more_flags)
        new_locations.extend(more_locations)

    if len(items) > 0:
        return items, flags, new_locations

    use_locations = list(filter(lambda x: location.Name in x.LocationReqs or containsAny(x,new_locations), locations))
    for use in use_locations:
        more_items, more_flags, more_locations = GetItemChildren(use, locations, handled)
        items.extend(more_items)
        flags.extend(more_flags)

        if len(items) > 0:
            return items, flags, new_locations

    for flag in flags:
        flags_set = list(filter(lambda x: flag in x.FlagReqs, locations))
        for flagA in flags_set:
            even_more_items, even_more_flags, even_more_locations = GetItemChildren(flagA, locations, handled)
            items.extend(even_more_items)

            for f in even_more_flags:
                if f not in flags:
                    flags.append(f)

    return items,flags, new_locations

# TODO: Include flag and item checks in this location too
def AutoBarrenAreas(locations):

    auto_barren = []
    known = {}
    for location in locations:
        items,flags,new_locations = GetItemChildren(location, locations, known)
        if len(items) == 0 and location.Name not in auto_barren:
            auto_barren.append(location.Name)

    return auto_barren


def OldHintMethod(spoiler, to_check_item, locationList, to_check_location, badgeDict, location_sim_mapping,
                  trashItems, criticalTrash, to_check_flag):

    no_free_item = []
    known = []
    itemToReq = []

    notValidReqs = ["Bicycle", "Fly", "Storm Badge",
                    "Berry Trees", "Hidden Items", "Timed Events",
                    "Kanto Mode",
                    "Rocket Invasion", "Mt. Silver Unlock",
                    "Goldenrod City Entrance", "Rock Smash Purchaseable",
                    "Saved Slowpokes", "Mr. Pokemon Visited", "All Badges", "Surf",
                    "Strength", "Flash", "Cut", "Whirlpool", "Waterfall",
                    "Defeat Electrodes"]

    doNotGiveHints = []

    no_free_locations = []
    no_free_flag = []
    iterateRequirements = True

    if iterateRequirements:
        for location in locationList:

            addedLoc, addedFlag, addedItem = IterateRequirements(location, locationList, known, partial_known=[])

            for req in addedLoc:
                if req not in location.LocationReqs:
                    location.LocationReqs.append(req)

            for req in addedItem:
                if req not in location.ItemReqs:
                    location.ItemReqs.append(req)

            for req in addedFlag:
                if req not in location.FlagReqs:
                    location.FlagReqs.append(req)

    discardedItems = []
    for item in to_check_item:
        if item not in spoiler:
            discardedItems.append(item)

    for discard in discardedItems:
        to_check_item.remove(discard)

    autoBarren = AutoBarrenAreas(locationList)

    # TODO: Make a function that returns a handled allow list
    # This should factor in all locations with NO child 'Item' locations and work out which can be removed
    discardedLocations = []

    for location in to_check_location:
        if location in autoBarren:
            discardedLocations.append(location)

        if location in location_sim_mapping:
            mapping = location_sim_mapping[location]
            multi_mapping = False
            for m in mapping:
                if m in autoBarren:
                    multi_mapping = True
            if multi_mapping:
                discardedLocations.append(location)

    for discard in discardedLocations:
        to_check_location.remove(discard)

    inverse_trash = {v: k for k, v in trashItems.items()}
    for i in inverse_trash.keys():
        spoiler[i] = inverse_trash[i]

    all_keys = list(spoiler.keys()).copy()

    requiredKeys = []
    requiredKeys.extend(list(badgeDict.keys()))

    locationMapping = {}
    itemMapping = {}
    flagMapping = {}

    RequiredByTag = {}

    for key in all_keys:

        trash = False
        uselessTrash = False
        if key in inverse_trash.keys():
            if key in criticalTrash:
                trash = True
            else:
                uselessTrash = True

            if not HintOptions.TrashHints:
                continue

        if not HintOptions.TMHints and key.startswith("TM_"):
            continue

        one_location_hints = []

        location_name = spoiler[key]
        resultOld = list(filter(lambda x: x.Name == location_name, locationList))
        if len(resultOld) != 1:
            print("Should be only one result")
        else:
            found_result = resultOld[0]

            if "Impossible" in found_result.FlagReqs or \
                    "Banned" in found_result.FlagReqs or \
                    "Unreachable" in found_result.FlagReqs:
                continue

            found_result.UpdateTags()

            for tag in found_result.Tags:
                tagName = tag.Name
                if tagName not in RequiredByTag:
                    RequiredByTag[tagName] = []
                RequiredByTag[tagName].append(found_result)

            if not HintOptions.UselessHints and uselessTrash:
                continue
            elif uselessTrash and random.randrange(0, 100, 1) >= (HintOptions.UselessHintChance * 100):
                continue

            # for ix in found_result.LocationReqs:
            #	if ix not in notValidHints:
            #		itemToReq.append((key,ix))

            for ix in found_result.ItemReqs:
                if ix not in notValidReqs and HintOptions.RequireHints:
                    one_location_hints.append(HintMessage("requiresi", key, ix, True))

            for ix in found_result.FlagReqs:
                if ix not in notValidReqs and HintOptions.RequireHints:
                    one_location_hints.append(HintMessage("requiresf", key, ix, True))

            # print(key, location_name, found_result.ItemReqs, found_result.FlagReqs)
            if not trash and not uselessTrash:
                for i in to_check_location:
                    mapping = [i]
                    if i in location_sim_mapping:
                        mapping = location_sim_mapping[i]
                    for m in mapping:
                        if m in found_result.LocationReqs:
                            if m not in locationMapping:
                                locationMapping[i] = []
                            locationMapping[i].append(found_result)
                            no_free_locations.append(i)  # Maybe M?
                for i in to_check_flag:
                    if i in found_result.FlagReqs:
                        if i not in flagMapping:
                            flagMapping[i] = []
                        flagMapping[i].append(found_result)
                        no_free_flag.append(i)
                    if found_result.FlagReqs is not None and i in found_result.FlagsSet:
                        if i not in flagMapping:
                            flagMapping[i] = []
                        flagMapping[i].append(found_result)
                        no_free_flag.append(i)
                for i in to_check_item:
                    if i in found_result.ItemReqs:
                        if i not in itemMapping:
                            itemMapping[i] = []
                        itemMapping[i].append(found_result)
                        no_free_item.append(i)

            parent = found_result
            parents = list(filter(lambda x: found_result in x.Sublocations, locationList))
            unequalHintNames = []

            for tag in found_result.Tags:
                if HintOptions.TagHints:
                    one_location_hints.append(HintMessage("attag", key, tag.Name, True))

            while parents is not None and len(parents) > 0:
                parent = parents[0]
                if parent.Name != parent.HintName:
                    unequalHintNames.append(parent.HintName)

                for tag in parent.Tags:
                    if HintOptions.TagHints:
                        one_location_hints.append(HintMessage("attag", key, tag.Name, True))

                parents = list(filter(lambda x: parent in x.Sublocations, locationList))

            # Refactor Map files to use 'Hint Name' for topmost parent to remove some ambiguity / longer names
            useHintName = None
            if len(unequalHintNames) == 0:
                useHintName = parent.HintName
            else:
                useHintName = unequalHintNames[0]

            if HintOptions.InHints:
                one_location_hints.append(HintMessage("in", key, useHintName, True))

            random.shuffle(one_location_hints)

            added = 0
            while added < HintOptions.MaxHintsPerItem and len(one_location_hints) > 0:
                item_hint = one_location_hints.pop(0)
                itemToReq.append(item_hint)

                added += 1

    # print("Mostly parent of:",key,"is",parent.HintName)

    # Known bug - location areas below have extra logic to check if required
    # So Tin Tower can say barren
    # But Rainbow Wing, etc will not
    # Would apply to any set

    maybeRequiredItems = []

    notRequiredItems = []
    # requiredItems = potentiallyRequiredItems.copy()
    requiredItems = []
    for x in no_free_item:
        if x in to_check_item:
            # if x not in doNotGiveHints and HintOptions.NotBarrenHints:
            maybeRequiredItems.append(x)
            # itemToReq.append(HintMessage("somethingi", None, x, True))
            to_check_item.remove(x)
    for i in to_check_item:
        if i not in doNotGiveHints and HintOptions.BarrenHints:
            itemToReq.append(HintMessage("nothingi", None, i, True))
        notRequiredItems.append(i)
        # if i in requiredItems:
        # requiredItems.remove(i)

    for x in maybeRequiredItems:
        required = isRequired(x, itemMapping, notRequiredItems)
        if required:
            if x not in doNotGiveHints and HintOptions.NotBarrenHints:
                itemToReq.append(HintMessage("somethingi", None, x, True))
            requiredItems.append(x)
        else:
            if x not in doNotGiveHints and HintOptions.BarrenHints:
                itemToReq.append(HintMessage("nothingi", None, x, True))
            notRequiredItems.append(x)

    print(notRequiredItems)

    handledLocations = []

    maybeRequiredFlags = []
    notRequiredFlags = []
    requiredFlags = []
    for x in no_free_flag:
        if x in to_check_flag:
            # if x not in doNotGiveHints and HintOptions.NotBarrenHints:
            maybeRequiredFlags.append(x)
            # itemToReq.append(HintMessage("somethingf", None, x, True))
            to_check_flag.remove(x)
            # requiredFlags.append(x)
    for i in to_check_flag:
        if i not in doNotGiveHints and HintOptions.BarrenHints:
            itemToReq.append(HintMessage("nothingf", None, i, True))
        notRequiredFlags.append(i)

    # print(notRequiredFlags)

    for x in maybeRequiredFlags:
        flagRequired = isRequired(x, flagMapping, notRequiredItems, notRequiredFlags)
        if flagRequired:
            if x not in doNotGiveHints and HintOptions.NotBarrenHints:
                itemToReq.append(HintMessage("somethingf", None, x, True))
            requiredFlags.append(x)
        else:
            if x not in doNotGiveHints and HintOptions.BarrenHints:
                itemToReq.append(HintMessage("nothingf", None, x, True))
            notRequiredFlags.append(x)

    requiredLocations = []
    for x in no_free_locations:
        if x in to_check_location and x not in handledLocations:
            if x not in locationMapping:
                print("Error, location should be in mapping")
            else:
                # requireThis = list(
                #     filter(lambda a: (hasattr(a, 'badge') and a.badge is not None) or a.item not in notRequiredItems,
                #            locationMapping[x]))
                # flagRequired = True
                # for l in requireThis:
                #     for m in l.FlagReqs:
                #         if m in notRequiredFlags:
                #             flagRequired = False
                flagRequired = isRequired(x, locationMapping, notRequiredItems, notRequiredFlags)
                if flagRequired:
                    handledLocations.append(x)

                    if x not in doNotGiveHints and HintOptions.NotBarrenHints:
                        itemToReq.append(HintMessage("somethingl", None, x, True))
                    to_check_location.remove(x)
                    requiredLocations.append(x)

    for i in to_check_location:
        if HintOptions.BarrenHints:
            itemToReq.append(HintMessage("nothingl", None, i, True))

    # For badge example, could get two items in the same gym, which would break the count
    # How to handle this?
    # Load gymdata differently to location???

    if HintOptions.TagHints:
        matchedSubTags = []
        for tagKey in RequiredByTag.keys():
            tagList = RequiredByTag[tagKey]

            tagCount = 0
            for l in tagList:
                # exclude = True
                # if (hasattr(l, 'badge') and l.badge is not None) or l.item in requiredItems:
                #     exclude = False
                # for x in l.FlagsSet:
                #     if x in requiredFlags:
                #         exclude = False
                #         break
                # if l.Name in requiredLocations:
                #     exclude = False
                # for x in l.LocationReqs:
                #     if x in requiredLocations:
                #         exclude = False

                exclude = isRequired("", {"":l}, notRequiredItems, notRequiredFlags, requiredLocations)

                new = False
                TAGS = list(filter(lambda x: x.Name == tagKey, l.Tags))
                if len(TAGS) != 1:
                    print("Error finding tag")
                    continue
                relevantTag = TAGS[0]

                for t in relevantTag.SubTags:
                    if t not in matchedSubTags:
                        new = True
                if len(relevantTag.SubTags) == 0:
                    new = True

                if not exclude and new:
                    print("Tagdetail:", tagKey, l.Name)
                    tagCount += 1
                    for x in relevantTag.SubTags:
                        if x not in matchedSubTags:
                            matchedSubTags.append(x)

            itemToReq.append(HintMessage("tag", tagKey, tagCount, True))



    # if "RedBadgeUnlockCount" in config.keys():
    #	itemToReq.append(HintMessage("conf", "Red", config["RedBadgeUnlockCount"], True))
    # else:
    #	itemToReq.append(HintMessage("conf", "Red", "16", True))

    # Reverse lookup some key items and see which are not required

    return itemToReq, locationList

def IsVariableRequired(variable, spoiler, locationTree, inputFlags, locList,
                       badgeSet, goal, input_variables=None):

    if input_variables is None:
        input_variables = []

    variables = []
    for var in input_variables:
        variables.append(var)
    if variable is not None:
        variables.append(variable)

    variableResult = RandomizeItemsBadgesAssumedFill.checkBeatability(spoiler, locationTree, inputFlags,
                                                     None, None, None, locList,
                                                     badgeSet, None, assign_trash=False,
                                                     forbidden=variables, recommended=False)

    if goal in variableResult[0]:
        return False

    return True





def GetWarpHubs(locationTree, inputFlags):
    startWarpGroups = list(filter(lambda x: x.Type == "Starting Warp", locationTree))
    startingList = [x.Name for x in startWarpGroups]
    # Ignore these warps for the most part, as obviously required!

    warpSpace = list(
        filter(lambda x: x.Type == "Map" and x.Name.endswith(LoadLocationData.WARP_OPTION), locationTree)).copy()

    transitionSpace = list(
        filter(lambda x: x.Type == "Transition" and x.Name.endswith(LoadLocationData.WARP_OPTION), locationTree)).copy()

    state = defaultdict(lambda: False)
    for flag in inputFlags:
        state[flag] = True

    warpCount = {}

    for warp in warpSpace:
        if len(warp.LocationReqs) == 1:
            name = warp.LocationReqs[0]
            if name not in warpCount:
                warpCount[name] = 0
            warpCount[name] += 1

    transitionPairs = {}
    for transition in transitionSpace:
        if transition not in transitionPairs.values() and \
            len(transition.LocationReqs) == 1:
            option = list(filter(lambda x: x.Name == transition.LocationReqs[0] and
                                           len(x.LocationReqs) == 1 and x.LocationReqs[0] == transition.Name ,transitionSpace))

            if len(option) == 1:
                transitionPairs[transition] = option[0]
                transitionPairs[option[0]] = transition

    for transition in transitionSpace:
        if len(transition.LocationReqs[0]) == 1 and transition.Name in warpCount:
            if transition in transitionPairs:
                pair = transitionPairs[transition]

                if pair.Name not in warpCount:
                    continue

                transitionFrom = transition.LocationReqs[0]
                transitionTo = transition.Name

                required = transition.requirementsNeeded(state)
                pairReq = pair.requirementsNeeded(state)

                if len(required) == 0 and len(pairReq) == 0:

                    warpCountFrom = warpCount[transitionFrom]
                    warpCountTo = warpCount[transitionTo]

                    if warpCountFrom >= warpCountTo:
                        warpCount[transitionFrom] += warpCountTo
                        del warpCount[transitionTo]

    for start in startingList:
        if start in warpCount:
            del warpCount[start]


    return warpCount


def GenerateHintMessages(spoiler, spoilerTrash, locations, criticalTrash, badgeDict,
                         requirementDict, config, HintOptions, allowList, fullTree,
                         inputFlags, goal):
    # AllLocations = LoadLocationData.LoadDataFromFolder(".", None, None, modifiers, flags)p
    #locationList = LoadLocationData.FlattenLocationTree(locations)

    locationList = LoadLocationData.FlattenLocationTree(fullTree)

    #TODO
    # Re run beatability checks for items deemed barren
    # This will confirm that the item isn't locked behind some form of locked path
    # Just change spoiler to remove required items from pool for items
    # Locations/flags a little harder

    trashItems = {}
    for sp in spoilerTrash.keys():
        item = spoilerTrash[sp]
        if "->" in item:
            trashItems[sp] = item.split("->")[1]
        else:
            trashItems[sp] = item

    to_check_location = ["Whirl Islands",
                         "Tin Tower", "Rocket Base", "Ruins of Alph",
                         "Cianwood City", "Blackthorn City", "Cinnabar Island",
                         "Route 4", "Fuchsia City", "Pewter City", "Mt Mortar Surf Floor",
                         "Mt Mortar Upper Floor", "Elm's Lab",
                         #"Routes 26/27", "Dark Cave","Cerulean Cape"
                         "Lighthouse","Dragons Den", "Rock Tunnel"]

    warp_hub_locations = []


    location_sim_mapping = {"Dark Cave": {"Dark Cave Violet", "Dark Cave Blackthorn"},
                            "Routes 26/27": {"Route 26", "Route 27", "Tojho Falls",
                                             "Route 27 Right Side"}, # Add inferred until complex logic
                            "Cerulean Cape": {"Route 24", "Route 25"}
                            }

    # Need message converter when loading these locations


    # TODO Check some against input flags
    to_check_flag = ["Kanto Power Restored", "Mahogany Rockets Defeated", "Beat Team Rocket",
                     "Became Champion", "Released Beasts","Ship Sidequest","Encountered Ho-Oh"
                     ]


    valid_input_flags = ["Shopsanity","Hidden Items","Mon Locked Checks","Bug Catching Contest",
                         "Phone Call Trainers","Timed Events", "Berry Trees", "Open Mt. Silver"]

    for flag in inputFlags:
        if flag in valid_input_flags:
            to_check_flag.append(flag)

    #to_check_item = ["Flash", "Strength", "Whirlpool", "Waterfall",
     #                "Secret Potion", "Basement Key", "Lost Item",
      #               "Cut", "Surf", "Red Scale", "Mystery Egg", "Machine Part",
       #              "Card Key", "Rainbow Wing", "Clear Bell", "Squirtbottle",
        #             "S S Ticket", "Pass", "Fly"]

    to_check_item = list(spoiler.keys())
    to_check_item.append("Rock Smash")

    hintList = []




    sanityCheckFailure = IsVariableRequired(None, spoiler, locations, inputFlags, fullTree, badgeDict, goal)
    if sanityCheckFailure:
        raise Exception("Invalid created base conditions")


    # New method does not yet implement 'requires' or 'in' hint types!
    # Should use the reverse requirements elements from generation for these?

    use_old_method = False
    if use_old_method:
        hintList, locationList = OldHintMethod(spoiler, to_check_item, locationList, to_check_location, badgeDict, location_sim_mapping,
                          trashItems, criticalTrash, to_check_flag)

    else:
        reqQuickLookup = {}

        typesToCheck = {}

        unlock_goal = goal if goal != "Red" else "Mt. Silver Is Open"

        # Remove recommended hints
        if "Warps" not in inputFlags:
            for location in to_check_location:
                required = IsVariableRequired(location, spoiler, locations, inputFlags, fullTree, badgeDict, unlock_goal)
                if not required:
                    if HintOptions.BarrenHints:
                        hintList.append(HintMessage("nothingl", None, location, True))
                else:
                    if HintOptions.NotBarrenHints:
                        hintList.append(HintMessage("somethingl", None, location, True))
            for location in location_sim_mapping.items():
                required = IsVariableRequired(None, spoiler, locations, inputFlags, fullTree, badgeDict, unlock_goal, location[1])
                if not required:
                    if HintOptions.BarrenHints:
                        hintList.append(HintMessage("nothingl", None, location[0], True))
                else:
                    if HintOptions.NotBarrenHints:
                        hintList.append(HintMessage("somethingl", None, location[0], True))
        else:
            warpCounts = GetWarpHubs(locationList, inputFlags)

            hubSizeForHints = 5
            warpHubsForHints = [ x[0] for x in warpCounts.items() if x[1] > hubSizeForHints ]

            warp_hub_locations.extend(warpHubsForHints)

            for hub in warp_hub_locations: #warpHubsForHints:
                required = IsVariableRequired(hub, spoiler, locations, inputFlags, fullTree, badgeDict,
                                              unlock_goal)
                hub_hint_name = hub.replace(LoadLocationData.WARP_OPTION, "")
                if not required:
                    if HintOptions.BarrenHints:
                        hintList.append(HintMessage("nothingl", None, hub_hint_name, True))
                else:
                    if HintOptions.NotBarrenHints:
                        hintList.append(HintMessage("somethingl", None, hub_hint_name, True))

        for item in to_check_item:
            if item in requirementDict:
                reqRequirements = requirementDict[item]
                reqQuickLookup[item] = reqRequirements

        for flag in to_check_flag:
            if flag in requirementDict:
                reqRequirements = requirementDict[flag]
                reqQuickLookup[flag] = reqRequirements

        for location in to_check_location:
            if location in requirementDict:
                reqRequirements = requirementDict[location]
                reqQuickLookup[location] = reqRequirements

        for warpHub in warp_hub_locations:
            if warpHub in requirementDict:
                reqRequirements = requirementDict[location]
                reqQuickLookup[location] = reqRequirements

        for badge in badgeDict:
            if badge in requirementDict:
                reqRequirements = requirementDict[badge]
                reqQuickLookup[badge] = reqRequirements

        #HintOptions.RequireHints = False
        if HintOptions.RequireHints:
            for itemReq in requirementDict.items():
                item = itemReq[0]
                reqs = itemReq[1]

                if item in spoiler:

                    # If using warps, load from locList (one step only)
                    # And see if any of the requirements is a Hub
                    # If so, include it! (Issue is default warp group removes all requirements!)
                    # But same issue as before, what about duplicates (eg Route 32 entrance and Violet Transition)?
                    # Map only?
                    # What if picks the wrong one and then the hint is wrong?

                    removeReqs = []
                    for req in reqs:
                        if req in reqQuickLookup:
                            toRemove = reqQuickLookup[req]
                            for r in toRemove:
                                if r not in removeReqs:
                                    removeReqs.append(r)
                    validReqs = set([ x for x in reqs if x not in removeReqs
                                  and (x in to_check_flag or x in to_check_location
                                       or x in to_check_item or x in badgeDict or x in warp_hub_locations) ])



                    for valid in validReqs:
                        # Check also re-run the check that this item can be obtained
                        # By removing this single new requirement
                        # Optimisation required as this now has a lot of calls to confirm requirements
                        required = IsVariableRequired(valid, spoiler, locations, inputFlags, fullTree, badgeDict, spoiler[item])
                        if required:
                            hint_type = None
                            if valid in to_check_location:
                                hint_type = "requiresl"
                            elif valid in to_check_flag:
                                hint_type = "requiresf"
                            elif valid in to_check_item:
                                hint_type = "requiresi"
                            elif valid in warp_hub_locations:
                                hint_type = "requiresl"

                            if hint_type is not None:
                                hintList.append(HintMessage(hint_type, item, valid, True))

        # This is added to be able to use Mt Silver early as a test rom, as Mt Silver is required anyway
        # Same applies to Flash, you don't need it to get all the badges, but do through Silver Room 1


        for item in to_check_item:
            if item in badgeDict:
                continue
            required = IsVariableRequired(item, spoiler, locations, inputFlags, fullTree, badgeDict, unlock_goal)
            if not required:
                if HintOptions.BarrenHints:
                    hintList.append(HintMessage("nothingi", None, item, True))
            else:
                if HintOptions.NotBarrenHints:
                    hintList.append(HintMessage("somethingi", None, item, True))


        for flag in to_check_flag:
            required = IsVariableRequired(flag, spoiler, locations, inputFlags, fullTree, badgeDict, unlock_goal)
            if not required:
                if HintOptions.BarrenHints:
                    hintList.append(HintMessage("nothingf", None, flag, True))
            else:
                if HintOptions.NotBarrenHints:
                    hintList.append(HintMessage("somethingf", None, flag, True))




        if HintOptions.InHints:
            #print("Look for IN Hints")
            spoilerLocations = list(filter(lambda x: x.Name in spoiler.values(), locationList))
            for loc in spoilerLocations:
                #print("Look for IN Hints for::", loc.Name)
                iter = loc
                found = False
                name = None

                # If this fails, look for a hint name to use
                while not found:
                    if iter.HintName != iter.Name:
                        found = True
                        name = iter.HintName
                        print("Found HintName", name, loc.Name)
                        break
                    elif len(iter.LocationReqs) == 1:
                        if iter.LocationReqs[0] in to_check_location or \
                                iter.LocationReqs[0] in warp_hub_locations:
                            found = True
                            name = iter.LocationReqs[0]
                            #print("Found expected::", name, loc.Name)
                            break
                        reqs = list(filter(lambda x: x.Name == iter.LocationReqs[0], locationList))
                        if len(reqs) > 1:
                                #print("Break out on 1", iter.Name, iter.LocationReqs, reqs)
                                break
                        elif len(reqs) == 0:
                            #print("Break out on 0", iter.Name, iter.LocationReqs, reqs)
                            break
                        else:
                            iter = reqs[0]
                    else:
                        #print("Break out on >1", iter.Name, iter.LocationReqs)
                        break

                if name is not None:
                    #print("Add:::", name, loc.item)
                    hintList.append(HintMessage("in", loc.item, name, True))



    # Do some extra checks to confirm combinations

    barrenHints = list(filter(lambda x: "nothing" in x.type, hintList))
    allBarren = [ x.secondary for x in barrenHints ]
    print("allBarren", allBarren)


    # Check for special cases
    # Please note if this checking was complete special cases would not be needed

    edgePairs = [("Pass", "S S Ticket"), ("S S Ticket", "Squirtbottle"), ("Pass", "Squirtbottle")]

    barrenRemove = []

    for edgePair in edgePairs:
        contained = list(filter(lambda x: x in allBarren, edgePair))
        if len(contained) == len(edgePair):
            edgeResult = IsVariableRequired(None, spoiler, locations, inputFlags, fullTree, badgeDict, unlock_goal, input_variables=
                list(edgePair))
            # If either way is possible to get to Kanto
            # Remove the options from the checks below as otherwise would also come up with 'either or'
            if edgeResult:
                for edge in edgePair:
                    allBarren.remove(edge)
                    barrenRemove.append(edge)


    removedHints = []
    for barrenRem in barrenRemove:
        for x in hintList:
            if "nothing" in x.type and barrenRem == x.secondary:
                removedHints.append(x)

    for rem in removedHints:
        hintList.remove(rem)



    required = IsVariableRequired(None, spoiler, locations, inputFlags, fullTree, badgeDict, unlock_goal,
                                  input_variables=allBarren)
    print("allBarren", required)

    if required:
        for barren in barrenHints:
            barren.nothingToMaybe()





    if "Name" in config.keys():
        hintList.append(HintMessage("conf", "Config", config["Name"], True))

    if "SilverBadgeUnlockCount" in config.keys():
        hintList.append(HintMessage("conf", "MtSilver", config["SilverBadgeUnlockCount"], True))
    else:
        hintList.append(HintMessage("conf", "MtSilver", "16", True))

    return hintList, locationList

class Item:
    Name = ""
    Price = 0
    HoldType = None
    Parameter = None
    Property = None
    Pocket = None
    Field = None
    Battle = None

class RandomItemProcessor:

    itemsList = []
    dontReplace = []
    allItems = []

    def readAttributesFile(self, file):
        items = []
        attr_file = open(file)
        lines = attr_file.readlines()
        attr_file.close()
        start=False
        item_name=True
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
                    maybe_price = sp[0].replace("item_attribute","").strip()

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

    def replaceRenames(self):
        # Handle TMs if you like
        for item in self.itemsList:
            if item.Name == "BLACKBELT_I":
                item.Name = "BLACKBELT"

    def limitItems(self, itemObjects):
        notTheseItems = ["BRICK_PIECE","SILVER_LEAF","GOLD_LEAF"]
        data = open("Data/BannedItems")
        banned_items = []
        for l in data.readlines():
            banned_items.append(l.strip().upper())
        data.close()
        return list(filter(lambda x:
            x.Price > 0 and x.Pocket != "KEY_ITEM" and x.Pocket != "TM_HM"
                           and x.Name not in notTheseItems
                           and x.Name not in banned_items
            ,itemObjects))

    def __init__(self, dontReplace=None, replaceNames=True):
        if dontReplace is None:
            dontReplace = []
        self.itemsTest = []
        self.dontReplace = dontReplace
        with open('AddItemValues.csv', newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.reader(csvfile)
            for i in reader:
                if (len(i) > 0):
                    self.itemsTest.append(i[0])

        self.allItems = self.readAttributesFile("Data/item_attributes.asm")
        self.itemsList = self.limitItems(self.allItems)

        if replaceNames:
            self.replaceRenames()
            for item in self.itemsList:
                if item.Name not in self.itemsTest:
                    print("Error with item:", item.Name)

        return

    def GetRandomItem(self,normal_item=None,bad_allowed=True):
        if normal_item is not None and normal_item in self.dontReplace:
            return normal_item

        if normal_item == "Leftovers":
            return normal_item

        return random.choice(self.itemsList).Name


REPEL_ITEMS = ["REPEL", "SUPER_REPEL", "MAX_REPEL"]
BALL_ITEMS = ["POKE_BALL", "GREAT_BALL", "ULTRA_BALL", "FAST_BALL", "HEAVY_BALL",
              "MOON_BALL", "MASTER_BALL", "PARK_BALL", "LOVE_BALL",
              "FRIEND_BALL", "LEVEL_BALL", "LURE_BALL"]

STATUS_ITEMS = []
HEALING_ITEMS = ["POTION", "SUPER_POTION", "HYPER_POTION", "MAX_POTION", "FULL_RESTORE"]

X_ITEMS = ["X_ATTACK", "X_DEFEND", "X_SPEED", "X_SPECIAL", "DIRE_HIT", "X_ACCURACY", "GUARD_SPEC"]
OTHER_ITEMS = ["TM_SWEET_SCENT", "ESCAPE_ROPE", "WATER_STONE", "TM_ROCK_SMASH", "REVIVE","FULL_RESTORE","HYPER_POTION"]

CATCH_EM_ALL_ITEMS=["THUNDERSTONE","FIRE_STONE","LEAF_STONE","SUN_STONE","MOON_STONE", "TM_HEADBUTT"]

REQUIRED_BUY_ITEMS = ["Rock Smash","Water Stone","Escape Rope", "Sweet Scent", "X Attack",
                      "X Defend", "X Special", "X Speed", "Dire Hit", "X Accuracy", "Guard Spec"]


def ShopFilenameConversion(name):
    if name is None:
        return None

    if "Goldenrod" in name:
        return "Goldenrod"
    if "Celadon" in name:
        return "Celadon"

    return name


def ShopItemGroupCheck(i, locList, reachable, itemList, addAfter=None):
    if i.isShop():
        shopElements = list(filter(lambda x: ShopFilenameConversion(x.FileName) == ShopFilenameConversion(i.FileName), locList))
        shopElementNames = [x.Name for x in shopElements]
        # Find these from old copy
        # Then find instances in activeLoc & reachable

        reaches = reachable.copy()
        if addAfter is not None:
            for a in addAfter:
                reaches[a.Name] = a

        # activeShop = list(filter(lambda x: x.Name in shopElementNames, activeLoc))
        reachShop = list(filter(lambda x: x[0] in shopElementNames, reaches.items()))

        # Currently works, prioritising early locations
        # This is generally suitable
        # However, could improve by removing per shop for department stores!

        hasItemType = False
        for element in reachShop:
            if element[1].item is not None:
                if element[1].item in itemList:
                    hasItemType = True

        return hasItemType

    return True

def AtLeastOneInAShop(itemList, trashList, locList, reachable, currentItem, currentLocation, fullTrash, spoiler, flags=None, addAfter=None, needed=None):
    if addAfter is None:
        addAfter = []

    if needed is None:
        needed = []

    if flags is None:
        flags = []

    # Potential issue, need to check if there IS a shop remaining -- if there isn't, will have to settle
    # If not settled, can force a re-do seed

    reachCopy = []
    reachCopy.extend(reachable.values())
    reachCopy.extend(addAfter)

    if currentLocation in reachCopy:
        reachCopy.remove(currentLocation)

    reachNames = [ x.Name for x in reachCopy ]
    inverse_map = Items.getInverseKeyItemMap()


    for item in itemList:
        #Need to add handling for RandomiseUnaffectedItems here!
        if item not in fullTrash and "RandomiseItems" not in flags:
            continue

        if item in inverse_map and inverse_map[item] in spoiler:
            continue

        r = list(filter(lambda x: (x.item == item)
        # Currently this line does not factor in items in the spoiler but not REACHED, which is different
           #or item in inverse_map and inverse_map[item] == x.item) \

          and (x.isShop() and not x.isBargainShop()) and ("Banned" not in x.FlagReqs or "ImpossibleRandomise" in x.FlagReqs) \
                                  and "Impossible" not in x.FlagReqs and \
          "Unreachable" not in x.FlagReqs, reachCopy))

        if len(r) == 0:
            needed.append(item)

    #if currentItem not in trashList:
    #    return True

    if currentItem in needed and not (currentLocation.isShop() and not currentLocation.isBargainShop()):
        # If last remaining instance of trash...
        countRemaining = [ x for x in trashList if x == currentItem]
        if len(countRemaining) <= 1:
            return False

    # Compare against remaining possible shops, if remaining == len(needed) and not one of these items, return False
    rleft = list(filter(lambda x: (x.isShop() and not x.isBargainShop()) and x.Name not in reachNames and \
             ("Banned" not in x.FlagReqs or "ImpossibleRandomise" in x.FlagReqs)
            and (x.isItem() or (x.wasItem() and "RandomiseItems" in flags))
            and "Impossible" not in x.FlagReqs and \
             "Unreachable" not in x.FlagReqs, locList))

    #print(len(rleft), len(needed), needed)
    #[[x.Name,x.FlagReqs] for x in rleft])


    if len(rleft) < len(needed):
        raise Exception("Invalid shop item assignment")

    if len(rleft) == len(needed) and (currentLocation.isShop() and not currentLocation.isBargainShop()) and currentItem not in needed:
        return False

    return True


def PreventItemAssignment(placeItem, items, trash):
    success = True
    re_add = []

    while placeItem in items:
        if len(trash) == 0:
            success = False
            break
        oldItem = placeItem
        placeItem = trash.pop()
        re_add.append(oldItem)

    return re_add, placeItem, success

ShopFlagItems_Old = ["Pokegear", "Expansion Card", "Radio Card", "ENGINE_POKEDEX", "OLD_ROD", "GOOD_ROD",
                        "SUPER_ROD", "ENGINE_MAP_CARD", "ENGINE_UNOWN_DEX", "Pokedex"]

ShopFlagItems = ["OLD_ROD", "GOOD_ROD","SUPER_ROD"]


def EnsurePlacementOfItemGroup(itemLocation, locList, reachable, ITEM_LIST, addAfter, force, trashItems,
                               invalidItems, progressItem, replacedItem):
    if itemLocation.isShop():
        hasRepel = ShopItemGroupCheck(itemLocation, locList, reachable, ITEM_LIST, addAfter=addAfter)
        if not hasRepel:
            if force:
                replacedItem = random.choice(ITEM_LIST)
                progressItem = replacedItem
            else:
                trashRepels = list(filter(lambda x: x in REPEL_ITEMS, trashItems))
                if len(trashRepels) > 0:
                    while progressItem not in ITEM_LIST:
                        oldItem = progressItem
                        progressItem = trashItems.pop()
                        replacedItem = progressItem
                        invalidItems.append(oldItem)

    return progressItem, replacedItem



def HandleShopLimitations(placeItem, itemLocation, locList, reachable, trashItems, flags, fullTrash, spoiler, addAfter=None, force=False):
    if addAfter is None:
        addAfter = []
    replacedItem = None
    baseItem = placeItem
    progressItem = baseItem

    # Incorrect, need to handle if an item is being assigned to a NON-shop as well
    # If the item is meant to always be purchasable
    #if not itemLocation.isShop():
     #   return None

    invalidItems = []
    invalidPriorityItems = []

    # Check for RandomizeUnaffectedItems?
    includesShopItems = [ l for l in locList if l.isShop() and l.isItem() ]
    if len(includesShopItems) == 0:
        #print("Shop items are not shuffled")
        return None

    forbiddenItems = []

    USE_BALL_ITEMS = []
    USE_BALL_ITEMS.extend(BALL_ITEMS)

    USE_STATUS_ITEMS = []
    USE_HEALING_ITEMS = []

    for flag in flags:
        if flag.startswith("Cannot Buy"):
            item = flag.replace("Cannot Buy ", "")
            forbiddenItems.append(item)

            dirtyItem = item.replace(" ","_").upper()
            if dirtyItem in USE_BALL_ITEMS:
                USE_BALL_ITEMS.remove(dirtyItem)

            if dirtyItem in USE_HEALING_ITEMS:
                USE_HEALING_ITEMS.remove(dirtyItem)

            if dirtyItem in USE_STATUS_ITEMS:
                USE_STATUS_ITEMS.remove(dirtyItem)

            trashMatch = [ x for x in trashItems if x == dirtyItem]
            for t in trashMatch:
                trashItems.remove(t)
                invalidItems.append(t)


    cleanItem = placeItem.replace("_", " ").replace("TM", "").strip()
    cleanItem = string.capwords(cleanItem, " ")
    # Trash removal done above; no need to loop here
    if itemLocation.isShopLike() and cleanItem in forbiddenItems:
        oldItem = progressItem
        progressItem = trashItems.pop()
        replacedItem = progressItem
        invalidItems.append(oldItem)

    # Function checks if all the items in a given shop, at least 1 must be a type of repel and 1 type of ball

    progressItem, replacedItem = EnsurePlacementOfItemGroup(itemLocation, locList, reachable, USE_BALL_ITEMS,
                                                 addAfter, force, trashItems, invalidItems, progressItem, replacedItem)

    progressItem, replacedItem = EnsurePlacementOfItemGroup(itemLocation, locList, reachable, REPEL_ITEMS,
                                                 addAfter, force, trashItems, invalidItems, progressItem, replacedItem)

    #if itemLocation.isShop():
    #    hasRepel = ShopItemGroupCheck(itemLocation, locList, reachable, REPEL_ITEMS, addAfter=addAfter)
    #    if not hasRepel:
    #        if force:
    #            replacedItem = random.choice(REPEL_ITEMS)
    #            progressItem = replacedItem
    #        else:
    #            trashRepels = list(filter(lambda x: x in REPEL_ITEMS, trashItems))
    #            if len(trashRepels) > 0:
    #                while progressItem not in REPEL_ITEMS:
    #                    oldItem = progressItem
    #                    progressItem = trashItems.pop()
    #                    replacedItem = progressItem
    #                    invalidItems.append(oldItem)
    #                    #trashItems.insert(random.randint(0, len(trashItems)), oldItem)

#        hasBall = ShopItemGroupCheck(itemLocation, locList, reachable,USE_BALL_ITEMS, addAfter=addAfter)
    #    if not hasBall:
    #        if force:
    #            replacedItem = random.choice(USE_BALL_ITEMS)
    #            progressItem = replacedItem
    #        else:
    #            trashBalls = list(filter(lambda x: x in USE_BALL_ITEMS, trashItems))
    #            if len(trashBalls) > 0:
    #                while progressItem not in USE_BALL_ITEMS:
    #                    oldItem = progressItem
    #                    progressItem = trashItems.pop()
    #                    replacedItem = progressItem
    #                    invalidItems.append(oldItem)
                        #trashItems.insert(random.randint(0, len(trashItems)), oldItem)

    # If shop enabled
    # Ensure each type of X Item is available in at least 1 shop

    # At least one of these items in the pool
    # Must be assigned to a shop
    # For convinence / otherwise

    itemsList = []
    itemsList.extend(X_ITEMS)
    itemsList.extend(OTHER_ITEMS)

    if "Catch Em All Shops" in flags:
        itemsList.extend(CATCH_EM_ALL_ITEMS)

    #TODO: If catch em all modifier enabled, extend the list further

    needed = []

    acceptable_placement = AtLeastOneInAShop(itemsList, trashItems, locList,
                                             reachable, progressItem, itemLocation, fullTrash, spoiler,
                                             addAfter=addAfter, needed=needed, flags=flags)
    if not acceptable_placement and force and itemLocation.isShop() and len(needed) > 0:
        replacedItem = needed[0]
        progressItem = replacedItem
    elif force and not itemLocation.isShop():
        # In this scenario, trash list is irrelevant for decision
        pass
    elif not force and not acceptable_placement:
        while not acceptable_placement:
            if len(trashItems) == 0:
                print("IPIs:", itemLocation.Name, invalidPriorityItems, invalidItems)
                #return None
            oldItem = progressItem
            progressItem = trashItems.pop()
            replacedItem = progressItem
            invalidPriorityItems.append(oldItem)

            acceptable_placement = AtLeastOneInAShop(itemsList,trashItems,locList, reachable, progressItem,
                                                     itemLocation, fullTrash, spoiler, flags=flags)
    elif force and not acceptable_placement:
        print("?", acceptable_placement, force, itemLocation.Name, itemLocation.item, needed)


    if itemLocation.isShop():
        item_to_replace = baseItem if replacedItem is None else progressItem
        re_add, chosen, success = PreventItemAssignment(item_to_replace, ShopFlagItems, trashItems)
        if not success:
            raise Exception('Failed mapping due to item requirement seed (shop)!')
        for item in re_add:
            trashItems.insert(random.randint(0, len(trashItems)), item)
        if item_to_replace != chosen:
            replacedItem = chosen

    for item in invalidPriorityItems:
        trashItems.append(item)

    for item in invalidItems:
        trashItems.insert(random.randint(0, len(trashItems)), item)

    return replacedItem


def AddressToIntValues(address):
    bank_size = 0x4000
    value = (address % bank_size) + bank_size
    bytes = value.to_bytes(2, byteorder='little')
    return bytes


def IsVersionSupported(major, minor, revision):
    supported = Version.GetSupportedSpeedchoiceVersion()
    if supported[0] != major or supported[1] != minor or supported[2] != revision:
        print(supported, major, minor, revision)
        return False

    return True


def CheckVersion(addressData, romMap):
    if "ckir_BEFORE_MajorVersionNumber" in addressData:
        majorVersion = addressData["ckir_BEFORE_MajorVersionNumber"]
        minorVersion = addressData["ckir_BEFORE_MinorVersionNumber"]
        revisionVersion = addressData["ckir_BEFORE_RevisionVersionNumber"]

        majorRequired = int(majorVersion["integer_values"])
        minorRequired = int(minorVersion["integer_values"])
        revisionRequired = int(revisionVersion["integer_values"])

        majorAddress = majorVersion["address_range"]["begin"]
        minorAddress = minorVersion["address_range"]["begin"]
        revisionAddress = revisionVersion["address_range"]["begin"]

        if not IsVersionSupported(majorRequired, minorRequired, revisionRequired):
            raise Exception("Version mismatch!")


        if len(romMap) <= majorAddress:
            return False

        majorActual = romMap[majorAddress]
        minorActual = romMap[minorAddress]
        revisionActual = romMap[revisionAddress]



        if majorActual != majorRequired or minorActual != minorRequired or revisionRequired != revisionActual:
            return False

        return True
    else:
        return False




def RandomPrice(original_price, min_below=0.5, max_above=2, min_variance=0, min_price=None, max_price=None):
    retry = True

    increased_variance = False

    if original_price <= min_variance:
        modal_price = 2000
        increased_variance = True
    else:
        modal_price = original_price

    max_retries = 5
    total_retries = 0

    if max_price is not None and max_price <= original_price * min_below:
        return max_price

    while retry:
        variance = modal_price
        if increased_variance:
            variance *= 0.4
            modal_price *= 0.8
        new_modal_price = random.normalvariate(modal_price, variance)

        if max_price is not None and new_modal_price > max_price:
            print("pr", max_price, original_price, new_modal_price)
            modal_price -= 5
            continue

        if new_modal_price > 15000:
            if total_retries == 1:
                continue
            else:
                break

        if new_modal_price <= 0:
            if modal_price == 0:
                continue
            elif total_retries == 0:
                continue
            else:
                break

        total_retries += 1



        if not increased_variance:
            if new_modal_price < (original_price * min_below):
                if total_retries == 1:
                    total_retries -= 1
                    continue
                else:
                    break
            elif new_modal_price > (original_price * max_above):
                if total_retries == 1:
                    total_retries -= 1
                    continue
                else:
                    break
            else:
                modal_price = new_modal_price
        else:
            modal_price = new_modal_price

        if total_retries >= max_retries:
            break

    return min(15000,abs(int(math.floor(modal_price) / 5) * 5))

def RandomizePrices(priceSettings, locations):
    priceList = {}
    lookupDict = {}
    itemProcessor = RandomItemProcessor(replaceNames=False)

    min_below = priceSettings["min_below"]
    max_above = priceSettings["max_above"]
    min_variance = priceSettings["min_variance"]
    keep_free = priceSettings["keep_free"]
    shopDetails = priceSettings["shop_settings"]

    standard = priceSettings["randomise_standard_prices"]
    buena = priceSettings["randomise_buena_prices"]
    game_corner = priceSettings["randomise_game_corner_prices"]
    bargain = priceSettings["randomise_bargain_prices"]
    buena_set = priceSettings["buena_set_price"]
    game_corner_set = priceSettings["game_corner_set_price"]

    martItems = {}

    for mart in shopDetails.keys():
        martDesc = shopDetails[mart]
        itemsInThisLocation = [ i for i in locations if i.isShop() and i.FileName == mart ]
        for item in itemsInThisLocation:
            alterPriceOf = item.item
            alterPriceOf = Items.GetCorrectItemName(alterPriceOf)

            if alterPriceOf.startswith("ENGINE_"):
                alterPriceOf = alterPriceOf.replace("ENGINE_", "ITEM_")

            if alterPriceOf not in martItems:
                martItems[alterPriceOf] = {}

            if 'MaxPrice' in martDesc:
                #TODO Check value is not overwritten
                martItems[alterPriceOf]["MaxPrice"] = martDesc['MaxPrice']
                print("MaxMartPrice::",alterPriceOf,  martDesc['MaxPrice'])

    if min_below == 0 or max_above == 0 or \
        (min_below >= max_above):
        raise Exception("Invalid values provided")

    for item in itemProcessor.allItems:
        if "$" in item.Name:
            continue

        randomised_price = item.Price
        if standard:
            if item.Price == 0 and keep_free:
                randomised_price = 0
            else:
                max_price = None
                if item.Name in martItems:
                    if 'MaxPrice' in martItems[item.Name]:
                        max_price = martItems[item.Name]["MaxPrice"]

                randomised_price = RandomPrice(item.Price, min_below=min_below, max_above=max_above,
                                           min_variance=min_variance, max_price=max_price)
            priceList[item.Name] = randomised_price
        #price_diff = randomised_price/item.Price if item.Price > 0 else "!"
        #print(item.Name, randomised_price, price_diff)

        lookupDict[item.Name] = (item.Price, randomised_price)

    #TODO: Add Game Corner Prize price randomisation
    hardcodedShops = [ loc for loc in locations
                       if (loc.isBargainShop() and bargain) \
                       or (loc.isVendingMachine() and bargain) \
                       or (loc.isPrize() and game_corner) \
                       or (loc.isBuenaItem() and buena)
                       ]

    # Note, only randomised hardcoded shops can be affected by price randomisation

    for shop in hardcodedShops:
        item_to_handle = shop.item
        if item_to_handle is None:
            continue

        if shop.isPrize() and game_corner_set is not None:
            priceList["HC_" + item_to_handle + str(shop)] = game_corner_set
            continue

        if shop.isBuenaItem() and buena_set is not None:
            priceList["HC_" + item_to_handle + str(shop)] = buena_set
            continue

        if shop.isBuenaItem():
            maxValue = 8
        else:
            maxValue = None

        given_price = 500
        if item_to_handle not in lookupDict:
            if keep_free:
                given_price = 0
            else:
                given_price = RandomPrice(0, min_below=min_below, max_above=max_above,
                        min_variance=min_variance, max_price=maxValue)

        else:
            details = lookupDict[item_to_handle]
            if details[0] == 0 and keep_free:
                given_price = 0

            valid = False
            while not valid:
                valid = True
                # Treat as bargains, price must be lower

                if details[1] == 0:
                    given_price = 0
                    break

                if details[1] <= details[0] * min_below:
                    given_price = details[1] - 1
                    break

                given_price = RandomPrice(details[0], min_below=min_below, max_above=max_above,
                                      min_variance=min_variance)

                if given_price >= details[1]:
                    valid = False

        priceList["HC_"+item_to_handle+str(shop)] = given_price

    return priceList

# Unused for now, no post-check used, added to logic for X Items issue
def CheckForBuyableItemBefore(variable, spoiler, locationTree, inputFlags, locList,
                           badgeSet, goal, actualReachable, Trash, input_variables=None):
    if input_variables is None:
        input_variables = []

    variables = []
    for var in input_variables:
        variables.append(var)
    if variable is not None:
        variables.append(variable)

    variables = ["Woke Snorlax"]

    variableResult = RandomizeItemsBadgesAssumedFill.checkBeatability(spoiler, locationTree, inputFlags,
                                                                      None, None, None, locList,
                                                                      badgeSet, None, assign_trash=False,
                                                                      forbidden=variables, recommended=False)

    #reachable, stateDist, randomizerFailed, trashSpoiler, randomizedExtra, changes, warnings

    neededItems = []
    neededItems.extend(X_ITEMS)

    foundItems = []

    for item in variableResult[0].values():
        if item.isItem() and item.isShop():
            if item.Name in Trash:
                trashItem = Trash[item.Name]
            else:
                trashItem = None

            #print(item.Name, trashItem)
            foundItems.append(trashItem)

    foundAll = True
    for item in neededItems:
        if item not in foundItems:
            print("no eaely:", item)
            foundAll = False

    if not foundAll:
        print(Trash)

    return foundAll