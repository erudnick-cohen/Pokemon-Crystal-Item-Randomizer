import json
import math
import random

import LoadLocationData

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
        file = file.replace("PokemonFanClub", "Vermillion City")

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
        Options.TrashHints = True

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

def getOptionsForItemModifications():
	return ["Replace Custom","Replace Healing","Replace Valuable","Replace Ball", "Replace Hope"]

def checkIfReplacementsConfigured(inputFlags):
    options = getOptionsForItemModifications()
    for option in options:
        if option in inputFlags:
            return True
    return False


def FlagCheckType(type, inputFlags):
    flagExtend = "Replace " + type
    if flagExtend in inputFlags:
        return True

    return False


def HandleItemReplacement(reachable, inputFlags):
    replacementFile = None

    containsAny = checkIfReplacementsConfigured(inputFlags)

    if containsAny:
        item_replacement = open("Config/ItemReplacement.json",encoding='utf-8')
        replacements = item_replacement.read()
        replacement_data = json.loads(replacements)
        replacementFile = {}
        for replacement_item in replacement_data:
            replacement_item_name = replacement_item["item"]
            replacement_replacement = replacement_item["replacement"]
            replacement_type = replacement_item["type"]

            replacement_percent = 100
            use_replacement_percent = True

            if use_replacement_percent and "chance" in replacement_item:
                replacement_percent = replacement_item["chance"]

            useReplacement = FlagCheckType(replacement_type, inputFlags)
            if useReplacement:
                replacementFile[replacement_item_name] = (replacement_replacement, replacement_percent)

    if 'Delete Fly' in inputFlags:
        if replacementFile is None:
            replacementFile = {}

        replacementFile["Fly"]: "BERRY"

    changes = {}

    if replacementFile is not None:
        for i in reachable.values():
            replaced = ReplaceItem(i, replacementFile)
            if replaced:
                changes[i.Name] = i.item

    return changes


def ReplaceItem(item, replaceFile):
    replaced = False
    if item.isItem():
        for i in replaceFile.keys():
            if item.item == i:
                replacement = replaceFile[item.item]
                item_chance = replacement[1]
                if item_chance >= random.random() * 100:
                    item.item = replacement[0]
                    replaced = True
                else:
                    break
    return replaced


def IterateRequirements(location, locations, known, partial_known=[]):
    addedLocation = []
    addedFlag = []
    addedItem = []

    for req in location.LocationReqs:
        if req == "Impossible":
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
                    "Mt. Silver Unlock": "Max Badges",
                    "Elm's Lab": "Elms Lab",
                    "S.S. Ticket": "SS Ticket",
                    "Became Champion": "Being Champion",

                    }

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
        if len(priority.HintTypes) != 0 and priority.HintKey != "":
            matches = list(filter(lambda x: x.type in priority.HintTypes and
                                            x.item == priority.HintKey, hints))
            hasPossible = len(matches) > 0
            hintOptions = list(set(hintOptions) | set(matches))
        elif priority.HintKey == "" and len(priority.HintTypes) != 0:
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
                                                 (a.HintKey == "" and x.type in a.HintTypes) or \
                                                 (a.HintKey != "" and x.type in a.HintTypes and a.HintKey == x.item) \
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
                if 'Impossible' in flags:
                    hintsToRemove.append(hint)
                    continue

        if hint.type == "in" or hint.type == "somethingf":
            if hint.secondary not in byLocationMapping:
                byLocationMapping[hint.secondary] = []
            byLocationMapping[hint.secondary].append(hint)

    for hint in hintsToRemove:
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





def isRequired(x, locationMapping, notRequiredItems, notRequiredFlags=[], requiredLocations=[]):
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

def GenerateHintMessages(spoiler, spoilerTrash, locations, criticalTrash, badgeDict, requirementDict, config, HintOptions):
    # AllLocations = LoadLocationData.LoadDataFromFolder(".", None, None, modifiers, flags)p
    locationList = LoadLocationData.FlattenLocationTree(locations)

    known = []


    trashItems = {}
    for sp in spoilerTrash.keys():
        item = spoilerTrash[sp]
        if "->" in item:
            trashItems[sp] = item.split("->")[1]
        else:
            trashItems[sp] = item

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

    to_check_location = ["Elite Four", "Whirl Islands",
                         "Tin Tower", "VS Ho-Oh", "Rocket Base", "Ruins of Alph",
                         "Cianwood City", "Blackthorn City", "Cinnabar Island",
                         "Route 4", "Fuchsia City", "Pewter City", "Mt Mortar Surf Floor",
                         "Mt Mortar Upper Floor", "Elm's Lab", "Routes 26/27", "Lighthouse",
                         "Dark Cave", "Dragons Den", "Rock Tunnel", "Cerulean Cape"]

    location_sim_mapping = {"Dark Cave": {"Dark Cave Violet", "Dark Cave Blackthorn"},
                            "Routes 26/27": {"Route 26", "Route 27", "Tojho Falls"},
                            "Cerulean Cape": {"Route 24", "Route 25"}
                            }

    # Need message converter when loading these locations

    no_free_locations = []

    to_check_flag = ["Kanto Power Restored", "Mahogany Rockets Defeated", "Beat Team Rocket"]
    no_free_flag = []

    to_check_item = ["Flash", "Strength", "Whirlpool", "Waterfall",
                     "Secret Potion", "Basement Key", "Lost Item",
                     "Cut", "Surf", "Red Scale", "Mystery Egg", "Machine Part",
                     "Card Key", "Rainbow Wing", "Clear Bell"]

    no_free_item = []

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

    discardedItems = []
    for item in to_check_item:
        if item not in spoiler:
            discardedItems.append(item)

    for discard in discardedItems:
        to_check_item.remove(discard)

    potentiallyRequiredItems = list(spoiler.keys()).copy()

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
        result = list(filter(lambda x: x.Name == location_name, locationList))
        if len(result) != 1:
            print("Should be only one result")
        else:
            found_result = result[0]

            if "Impossible" in found_result.LocationReqs:
                continue

            found_result.UpdateTags()

            for tag in found_result.Tags:
                tagName = tag.Name
                if tagName not in RequiredByTag:
                    RequiredByTag[tagName] = []
                RequiredByTag[tagName].append(found_result)

            if not HintOptions.UselessHints and uselessTrash:
                continue
            elif uselessTrash and random.randrange(0, 100, 1) >= (HintOptions.UselessHintChance*100):
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
    #requiredItems = potentiallyRequiredItems.copy()
    requiredItems = []
    for x in no_free_item:
        if x in to_check_item:
            #if x not in doNotGiveHints and HintOptions.NotBarrenHints:
            maybeRequiredItems.append(x)
                #itemToReq.append(HintMessage("somethingi", None, x, True))
            to_check_item.remove(x)
    for i in to_check_item:
        if i not in doNotGiveHints and HintOptions.BarrenHints:
            itemToReq.append(HintMessage("nothingi", None, i, True))
        notRequiredItems.append(i)
        #if i in requiredItems:
            #requiredItems.remove(i)

    for x in maybeRequiredItems:
        required = isRequired(x, itemMapping,notRequiredItems)
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
            #if x not in doNotGiveHints and HintOptions.NotBarrenHints:
            maybeRequiredFlags.append(x)
            #itemToReq.append(HintMessage("somethingf", None, x, True))
            to_check_flag.remove(x)
            #requiredFlags.append(x)
    for i in to_check_flag:
        if i not in doNotGiveHints and HintOptions.BarrenHints:
            itemToReq.append(HintMessage("nothingf", None, i, True))
        notRequiredFlags.append(i)

    #print(notRequiredFlags)

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

    if "Name" in config.keys():
        itemToReq.append(HintMessage("conf", "Config", config["Name"], True))

    if "SilverBadgeUnlockCount" in config.keys():
        itemToReq.append(HintMessage("conf", "MtSilver", config["SilverBadgeUnlockCount"], True))
    else:
        itemToReq.append(HintMessage("conf", "MtSilver", "16", True))

    # if "RedBadgeUnlockCount" in config.keys():
    #	itemToReq.append(HintMessage("conf", "Red", config["RedBadgeUnlockCount"], True))
    # else:
    #	itemToReq.append(HintMessage("conf", "Red", "16", True))

    # Reverse lookup some key items and see which are not required

    return itemToReq, locationList
