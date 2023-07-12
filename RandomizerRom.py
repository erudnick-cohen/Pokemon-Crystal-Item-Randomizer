import shutil
import struct

import Items
import re
import os
import time
import yaml
import json
import copy
import mmap
import math
import Gym
import RandomizeFunctions


def ResetRom():
	try:
		shutil.rmtree("RandomizerRom")
	except:
		print("No existing folder created, nothing to remove")
	shutil.copytree("Game Files/pokecrystal-speedchoice","RandomizerRom")

def CountFilesInDirectory(dir):
	count = 0
	files = os.listdir(dir)
	for f in files:
		if os.path.isfile(dir+"/"+f):
			count += 1
		elif os.path.isdir(dir+"/"+f):
			count += CountFilesInDirectory(dir+"/"+f)
	return count


def IsWithinLabels(before, after, index):
	for b_index in range(0, len(before)):
		beforeValue = before[b_index]
		afterValue = after[b_index]

		if index >= beforeValue and index < afterValue:
			return True

	return False



def GetLabelsDefinedWithinLines(manual_file):
	# Get any code sandwiched with .ckir
	manual_file = open(manual_file)
	manual_lines = manual_file.readlines()
	manual_file.close()

	isCKIRBeforeLabel = "\.ckir_BEFORE(.*){1,}::"
	isCKIRAfterLabel = "\.ckir_AFTER(.*){1,}::"
	ckirBefore = re.compile(isCKIRBeforeLabel)
	ckirAfter = re.compile(isCKIRAfterLabel)

	manuals_within_before = [manual_lines.index(x) for x in manual_lines if ckirBefore.match(x)]
	manuals_within_after = [manual_lines.index(x) for x in manual_lines if ckirAfter.match(x)]

	if len(manuals_within_before) == 0 or len(manuals_within_after) == 0:
		# This should not occur as all these files should have manual labels
		raise Exception("No Manual label in labelling file::", manual_file)

	if len(manuals_within_before) != len(manuals_within_after):
		raise Exception("Incorrect count of manual labels for:", manual_file,
						manuals_within_before, manuals_within_after)


	lines_between = [x.strip() for x in manual_lines if IsWithinLabels(manuals_within_before, manuals_within_after,
																   manual_lines.index(x))]

	return [ label.replace(":","") for label in lines_between if label.startswith(".") and ".ckir" not in label]
def CompareFileData(manual_file, base_file):
	manual_file = open(manual_file)
	manual_lines = manual_file.readlines()

	replace_file = open(base_file)
	replace_lines = replace_file.readlines()

	manual_file.close()
	replace_file.close()

	isCKIRBeforeLabel = "\.ckir_BEFORE(.*){1,}::"
	isCKIRAfterLabel = "\.ckir_AFTER(.*){1,}::"
	ckirBefore = re.compile(isCKIRBeforeLabel)
	ckirAfter = re.compile(isCKIRAfterLabel)

	manuals_within_before = [ manual_lines.index(x) for x in manual_lines if ckirBefore.match(x)]
	manuals_within_after = [manual_lines.index(x) for x in manual_lines if ckirAfter.match(x)]

	if len(manuals_within_before) == 0 or len(manuals_within_after) == 0:
		# This should not occur as all these files should have manual labels
		raise Exception("No Manual label in labelling file::", manual_file)

	if len(manuals_within_before) != len(manuals_within_after):
		raise Exception("Incorrect count of manual labels")

	# Ignore any changes within the labels, as these are meant to be different and handled accordingly
	# So only check for the other lines!

	replace_drop = [ x for x in replace_lines if not IsWithinLabels(manuals_within_before, manuals_within_after,
																	replace_lines.index(x))]

	# Replace drop contains the lines in REPLACE to ignore
	# However, we are looking for MISSING lines from the original
	# Maybe just handle with latest changes?


	manuals =  [ x.strip() for x in manual_lines if not (x.strip().endswith("::") or x.strip().startswith(";"))]
	replaces = [ x.strip() for x in replace_drop if not (x.strip().endswith(":") or x.strip().startswith(";"))]



	# TODO: Make these code changes work for old/new code in the labels, so this generated rom IS still the base rom
	# For now, ignore changes within before->after label sets



	missing_from_manual = [ x for x in replaces if x not in manuals ]
	if len(missing_from_manual) > 0:
		index = replaces.index(missing_from_manual[0])
		return index
	else:
		return_value = None if len(manuals) == len(manuals) else 1
		return return_value

def ResetRomForLabelling(wsl=False, romDir="7.4"):
	git_success = False
	try:
		os.chdir("RandomizerRom")
		os.listdir(os.curdir)
		if not os.path.isdir(".git"):
			git_success = False
			os.chdir("..")
		else:
			command = ("wsl " if wsl else "") + "git reset --hard"
			os.system(command)
			os.chdir("..")
			git_success = True
	except:
		git_success = False


	if not git_success:
		try:
			shutil.rmtree("RandomizerRom")
		except:
			print("No existing folder created, nothing to remove")
		shutil.copytree("Game Files/"+romDir,"RandomizerRom")
	#next overwrite the files which need custom labels


def UpdateDataDirectory():
	shutil.copy("RandomizerRom/data/items/attributes.asm", "Data/item_attributes.asm")
	shutil.copy("RandomizerRom/constants/event_flags.asm", "Data/event_flags.asm")

def InsertManualFiles(result_lines=None):
	manual_dir = "Files with manual labels"

	counted = CountFilesInDirectory(manual_dir)

	manual_copy_files = []

	for root, dir, files  in os.walk(manual_dir+"/maps"):
		for file in files:
			map_file = (manual_dir+"/maps/"+file,"RandomizerRom/maps/"+file)
			manual_copy_files.append(map_file)
	for root, dir, files  in os.walk(manual_dir+"/engine"):
		for engine in files:
			engine_file = (manual_dir+"/engine/"+engine,"RandomizerRom/engine/"+engine)
			manual_copy_files.append(engine_file)

	for root, dir, files in os.walk(manual_dir+"/menus"):
		for engine in files:
			engine_file = (manual_dir+"/menus/"+engine,"RandomizerRom/engine/menus/"+engine)
			manual_copy_files.append(engine_file)

	#manual_copy_files.append((manual_dir+"/blocks/blocks.asm","RandomizerRom/data/maps/blocks.asm"))
	manual_copy_files.append((manual_dir+"/pokemon/breeding.asm","RandomizerRom/engine/pokemon/breeding.asm"))
	manual_copy_files.append((manual_dir+"/events/magikarp_lengths.asm","RandomizerRom/data/events/magikarp_lengths.asm"))
	manual_copy_files.append((manual_dir+"/data/moves/tmhm_moves.asm","RandomizerRom/data/moves/tmhm_moves.asm"))
	manual_copy_files.append((manual_dir+"/events/overworld.asm", "RandomizerRom/engine/events/overworld.asm"))
	manual_copy_files.append((manual_dir + "/events/std_scripts.asm", "RandomizerRom/engine/events/std_scripts.asm"))
	manual_copy_files.append((manual_dir+"/overworld/map_setup.asm", "RandomizerRom/engine/overworld/map_setup.asm"))

	if len(manual_copy_files) != counted:
		print("Manual copied files:", len(manual_copy_files), counted)
		print("Copied files", manual_copy_files)
		raise Exception("Unused file in folder")

	# Check files for inconsistent line differences

	for item in manual_copy_files:
		# Code was complex, but secondary  solution below might work better
		#fine = CompareFileData(item[0], item[1])
		#if fine is not None:
		#	#pass
		#	raise Exception("File data does not correlate::", item)

		if result_lines is not None:
			definedLabels = GetLabelsDefinedWithinLines(item[0])
			for label in definedLabels:
				result_lines.append(label)

	for manual_file in manual_copy_files:
		shutil.copy(manual_file[0], manual_file[1])

def WriteOakBadgeCheckNumber(number, addressData, gameFile):
	#get where this is
	start = addressData['ckir_BEFORE_OAK_BADGES_CHECK']["address_range"]["begin"]
	#Change oak to a greater than check so that the game isn't unwinnable. This value is usually 10, unless it gets changed.
	gameFile[start] = 10
	#gameFile[start] = [int(s) for s in addressData['ckir_BEFORE_OAK_BADGES_CHECK']["integer_values"].split(' ')][0]
	#Write number. Badge count is 2nd value from start. Minus one because its greater than
	gameFile[start+1] = number-1



def WriteTrainerDataToMemory(locationDict,distDict,addressData,romMap, levelBonus = 0, maxLevel = 100):
	#load up the trainer data
	yamlfile = open("TrainerData/Trainers.yaml")
	yamltext = yamlfile.read()
	trainerData = yaml.load(yamltext, Loader=yaml.FullLoader)
	#loop through locations
	for i in distDict:
		if i in locationDict:
			location = locationDict[i]
			if location.Trainers is not None:
				for j in location.Trainers:
					trainer = trainerData[j]
					#print('Writing '+j)
					idTextB = "ckir_BEFORE"+"".join(j.upper().split())+"0TRAINER"
					if int(trainer['Type']) == 1:
						monJump = 6
					if int(trainer['Type']) == 0:
						monJump = 2
					if int(trainer['Type']) == 2:
						monJump = 3
					baseOffset = 0
					#find base offset (WHY ISN'T THIS CONSTANT???? Answer: Because there is a string in each entry!!!!)
					k = 0
					while k < len(addressData[idTextB]['integer_values'].split()):
						#print(romMap[addressData[idTextB]['address_range']['begin']+k])
						if romMap[addressData[idTextB]['address_range']['begin']+k] == int(trainer['Type']):
							baseOffset = k
							k = len(addressData[idTextB]['integer_values'].split())
						k = k+1
					for k in range(0,len(trainer['Pokemon'])):
						#print('Writing mon '+str(k))
						level = trainer['Pokemon'][k]['Level']
						newlevel = max(level-location.AreaLevel+distDict[i]+round(levelBonus*(distDict[i]/maxLevel)), 2)
						#print(romMap[addressData[idTextB]['address_range']['begin']+baseOffset+k*monJump+1])
						#print('to')
						#print(newlevel)
						romMap[addressData[idTextB]['address_range']['begin']+baseOffset+k*monJump+1] = max(newlevel,2)

def WriteWildLevelsToMemory(locationDict, distDict,addressData,romMap, levelBonus = 0, maxLevel = 100):
	surfDist = max(distDict['Surf'],distDict['Fog Badge'])
	#loop through locations
	for i in distDict:
		if i in locationDict:
			location = locationDict[i]
			if location.WildTableList is not None:
				for j in location.WildTableList:
					idTextB = "ckir_BEFORE"+"".join(j.upper().replace("_","").split())+"0WILDGRASS"
					if(idTextB in addressData):
						#print('Writing '+j+" at "+location.Name)
						aData = addressData[idTextB]['integer_values'].split(" ")
						minLV = float('inf')
						#this is a hack to account for the fact that the larvitar in mt. silver are WAAAAYYYY too low level
						LVthresh = 0
						if "SILVERCAVE" in idTextB:
							LVthresh = 45
						for k in range(5,len(aData),2):
							minLV = min(max(int(aData[k]),LVthresh),minLV)
						for k in range(5,len(aData),2):
							cLV = max(int(aData[k]),LVthresh)
							nLV = max(cLV-minLV+distDict[i], 2)
							romMap[addressData[idTextB]['address_range']['begin']+k] = max(nLV+round(levelBonus*(distDict[i]/maxLevel)),2)

	#loop through locations
	for i in distDict:
		if i in locationDict:
			location = locationDict[i]
			if location.WildTableList is not None:
				for j in location.WildTableList:
					idTextB = "ckir_BEFORE"+"".join(j.upper().replace("_","").split())+"0WILDWATER"
					if(idTextB in addressData):
						#print('Writing '+j+" at "+location.Name)
						aData = addressData[idTextB]['integer_values'].split(" ")
						minLV = float('inf')
						for k in range(5,len(aData),2):
							minLV = min(int(aData[k]),minLV)
						for k in range(5,len(aData),2):
							cLV = int(aData[k])
							nLV = max(cLV-minLV+max(distDict[i],distDict['Surf']), 2)
							romMap[addressData[idTextB]['address_range']['begin']+k] = max(nLV+round(levelBonus*(max(distDict[i],distDict['Surf'])/maxLevel)),2)
	#loop through locations
	for i in distDict:
		if i in locationDict:
			location = locationDict[i]
			if location.WildTableList is not None:
				for j in location.WildTableList:
					idTextB = "ckir_BEFORE"+"".join(j.upper().replace("_","").split())+"0WILDSWARM"
					if(idTextB in addressData):
						#print('Writing '+j+" at "+location.Name)
						aData = addressData[idTextB]['integer_values'].split(" ")
						minLV = float('inf')
						for k in range(5,len(aData),2):
							minLV = min(int(aData[k]),minLV)
						for k in range(5,len(aData),2):
							cLV = int(aData[k])
							nLV = max(cLV-minLV+distDict[i], 2)
							romMap[addressData[idTextB]['address_range']['begin']+k] = max(nLV+round(levelBonus*(distDict[i]/maxLevel)),2)

def WriteSpecialWildToMemory(locationDict,distDict,addressData,romMap, levelBonus = 0, maxLevel = 100):
	monList = []
	#print("Editing Special Pokemon")
	for root, dir, files  in os.walk("Special Pokemon Locations"):
		for file in files:
			#print("File: "+file)
			entry = open("Special Pokemon Locations/"+file,'r')
			yamlData = yaml.load(entry, Loader=yaml.FullLoader)
			loc = yamlData["Location"]
			if(True):
				idTextB = "ckir_BEFORE"+"".join(loc.upper().split()).replace('.','_').replace("'","")+"0SPECIALWILD"
				cLV = addressData[idTextB]['integer_values'][2]
				mon = yamlData["NormalMon"]
				shift = yamlData["LevelShift"]
				type = yamlData["Type"]
				code = yamlData["Code"]
				#we don't bother with having restrictions on these, as in general these pokemon are potentially missable
				newmon = mon
				romMap[addressData[idTextB]['address_range']['begin']+2] = max(distDict[loc]+shift+round(levelBonus*(distDict[loc]/maxLevel)),2)


def LoadEventFlags():
	event_flags_filename = "Data/event_flags.asm"
	event_data = open(event_flags_filename, encoding="utf8")
	event_lines = event_data.readlines()
	event_data.close()

	event_flag_lookup = {}
	count = 0

	for event_line in event_lines:
		event_line = event_line.strip()
		if event_line.startswith("const EVENT_"):
			flag_name = event_line.split(" ")[1]
			count += 1
			event_flag_lookup[flag_name] = count

	return event_flag_lookup

def DirectWriteItemLocations(locations,addressData,gameFile, progRod = False):
	codeLookup = Items.makeRawItemCodeDict(progRod)
	yamlfile = open("BadgeData.yml",encoding='utf-8')
	yamltext = yamlfile.read()
	gymOffsets = yaml.load(yamltext, Loader=yaml.FullLoader)

	berryLookup = LoadEventFlags()

	for i in locations:
		if i.Dummy:
			findLocations = [location for location in locations if location.Name == i.TrueName]
			if len(findLocations) != 1:
				# ('Invalid Dummy for ', 'Ruins of Alph UnownDex Backup', 'Ruins of Alph UnownDex', '!')
				raise Exception("Invalid Dummy for ", i.Name, i.TrueName ,"!")

			i.item = findLocations[0].item
			#print("Dummy for", i.Name, i.TrueName, i.item)

		if i.isShop() and i.isItem():
			WriteShopToRomMemory(i, addressData, codeLookup, gameFile)
		elif i.isItem():
			if i.IsHidden:
				WriteMachinePartToRomMemory(i,addressData,codeLookup,gameFile)
			elif not i.IsSpecial:
				if i.Name == "Elm Aide Pokeballs": #currently a regular location with special rules due to labelling weirdness
					WriteAideBallsToRomMemory(i,addressData,codeLookup,gameFile)
				elif i.isVendingMachine():
					WriteRegularLocationToRomMemory(i,addressData,codeLookup,gameFile,berryLookup)
					WriteItemNameToBuffer(i,addressData,gameFile)
				elif i.isPrize():
					WriteRegularLocationToRomMemory(i, addressData, codeLookup, gameFile, berryLookup)
					WriteItemNameToBuffer(i, addressData, gameFile)
				else:
					WriteRegularLocationToRomMemory(i,addressData,codeLookup,gameFile,berryLookup)
			else:
				if i.Name == "Dragons Den Dragon Fang":
					#this just happens to work, its in the same byte offset (its also now just a regular location...)
					WriteRegularLocationToRomMemory(i,addressData,codeLookup,gameFile,berryLookup)
				if i.Name == "Hidden Machine Part":
					WriteMachinePartToRomMemory(i,addressData,codeLookup,gameFile)
				if i.Name == "Celadon Cafe Leftovers":
					WriteMachinePartToRomMemory(i, addressData, codeLookup, gameFile)
		elif i.isGym():
			WriteBadgeToRomMemory(i,addressData,gymOffsets,gameFile)

def ApplyGamePatches(gameFile, patches):
	for i in patches:
		if not 'Offset' in i['address_range']:
			for j in range(0,len(i['integer_values']['new'])):
				gameFile[i['address_range']['begin']+j] = i['integer_values']['new'][j]
		else:
			for j in range(i['address_range']['Offset'],len(i['integer_values']['new'])):
				gameFile[i['address_range']['begin']+j] = i['integer_values']['new'][j]

def WriteBadgeToRomMemory(location,labelData,gymOffsets,romMap):
	labelCodeB = "ckir_BEFORE"+("".join(location.Name.split())).upper().replace('.','_').replace("'","")+'0BADGECODE'
	labelCodeB2 = "ckir_BEFORE"+("".join(location.Name.split())).upper().replace('.','_').replace("'","")+'0BADGECODEB'
	#print('Writing '+labelCodeB)
	addressData = labelData[labelCodeB]
	romMap[addressData["address_range"]["begin"]+1] = location.badge.Code
	if(not location.SecondaryCode is None):
		addressData2 = labelData[labelCodeB2]
		romMap[addressData2["address_range"]["begin"]+1] = location.badge.Code

	#no longer borrowing this trick from goldenrules's key item randomizer
	# nString = "It's\n"+location.badge.Name.upper()
	# for i in range(0,len(nString)):
		# #+1 to dodge the initial byte that isn't part of the text
		# #note that this leaves the remaining text as "garbage", since we are terminating the string ourselves
		# #print(nString[i])
		# nByte = str.encode(nString[i],'ascii')
		# nByte = int.from_bytes(nByte,'big')-65+128
		# if nString[i] == '\n':
			# nByte = 79
		# if nString[i] == "'":
			# nByte = 224
		# if nString[i] == " ":
			# nByte = 127
		# #print(romMap[gymOffsets[location.Name]+i+1])
		# #print('to')
		# #print(nByte)
		# romMap[gymOffsets[location.Name]+i+1] = nByte
		# #print('---')
	# #add the done character to the end
	# romMap[gymOffsets[location.Name]+len(nString)+1] = 87
	# #then terminate the string
	# romMap[gymOffsets[location.Name]+len(nString)+2] = 50
#STILL NEED TO WRITE THE REST OF THESE
def WriteRegularLocationToRomMemory(location,labelData,itemScriptLookup,romMap,berryLookup):
	if(not isinstance(location, Gym.Gym)):
		labelCodeB = "ckir_BEFORE"+("".join(location.Name.split())).upper().replace('.','_').replace("'","")+'0ITEMCODE'
		labelCodeB2 = "ckir_BEFORE"+("".join(location.Name.split())).upper().replace('.','_').replace("'","")+'0ITEMCODEB'
	else:
		labelCodeB = "ckir_BEFORE"+("".join(location.Name.split())).upper().replace('.','_').replace("'","")+'0BADGECODE'
		labelCodeB2 = "ckir_BEFORE"+("".join(location.Name.split())).upper().replace('.','_').replace("'","")+'0BADGECODEB'

	#print('Writing '+labelCodeB)
	addressData = labelData[labelCodeB]

	nItemCodeData = itemScriptLookup(location.item)
	nItemCode = nItemCodeData[0]
	itemType = nItemCodeData[1]
	if(itemType == 'Item'):
		commandVerbose = 158
		commandBall = 1
		endVal = 1
	elif(itemType == 'Flag'):
		commandVerbose = 175
		commandBall = 3
		endVal = 1
	elif(itemType == 'Rod'):
		commandVerbose = 177
		commandBall = 4
		endVal = 176
		nItemCode = 176
	if location.IsBall:
		labelCodeBNPC = "ckir_BEFORE"+("".join(location.Name.split())).upper().replace('.','_').replace("'","")+'0NPCCODE'
		labelCodeBNPC2 = "ckir_BEFORE"+("".join(location.Name.split())).upper().replace('.','_').replace("'","")+'0NPCCODEB'
		addressDataNPC = labelData[labelCodeBNPC]
		#need to extract the nibble out
		#print(list(map(int, addressDataNPC["integer_values"].split(' '))))
		#print(addressDataNPC["integer_values"].split(' '))
		combobyte = bin(list(map(int, addressDataNPC["integer_values"].split(' ')))[7])
		#form full binary expression
		fullByte = (10-len(combobyte))*'0'+combobyte[2:]
		#split it into two nibbles
		nb1 = fullByte[0:4]
		nb2 = fullByte[4:8]
		#now generate the correct nibble for the object type
		nibbleBall = bin(commandBall)
		#print(nibbleBall)
		fullNibble = nb1+((6-len(combobyte))*'0'+nibbleBall[2:])
		#print(fullNibble)
		newBallByte = int(fullNibble,2)
		#print(newBallByte)
		romMap[addressDataNPC["address_range"]["begin"]+7] = newBallByte
		romMap[addressData["address_range"]["begin"]] = nItemCode
		if(not location.SecondaryCode is None):
			addressData2 = labelData[labelCodeB2]
			addressDataNPC2 = labelData[labelCodeBNPC2]
			combobyte = bin(list(map(int, addressDataNPC2["integer_values"].split(' ')))[7])
			#form full binary expression
			fullByte = (10-len(combobyte))*'0'+combobyte[2:]
			#split it into two nibbles
			nb1 = fullByte[0:4]
			nb2 = fullByte[4:8]
			#now generate the correct nibble for the object type
			nibbleBall = bin(commandBall)
			fullNibble = nb1+((6-len(combobyte))*'0'+nibbleBall[2:])
			newBallByte = int(fullNibble,2)
			romMap[addressDataNPC2["address_range"]["begin"]+7] = newBallByte
			romMap[addressData2["address_range"]["begin"]] = nItemCode
	elif location.IsBerry:
		labelCodeBNPC = "ckir_BEFORE" + ("".join(location.Name.split())).upper().replace('.', '_').replace("'","") + '0NPCCODE'
		labelCodeBNPC2 = "ckir_BEFORE" + ("".join(location.Name.split())).upper().replace('.', '_').replace("'","") + '0NPCCODEB'
		addressDataNPC = labelData[labelCodeBNPC]


		# need to extract the nibble out
		# print(list(map(int, addressDataNPC["integer_values"].split(' '))))
		# print(addressDataNPC["integer_values"].split(' '))

		berry_lookup = "EVENT_GOT_"+location.BerryFlag
		if berry_lookup in berryLookup:
			berry_flag = berryLookup[berry_lookup]
		else:
			berry_flag = location.BerryFlag

		# Add a flag to the berry item and replace the event with a normal item ball (in behaviour)
		# Still shows as tree
		flag_bytes = berry_flag.to_bytes(2, 'little')
		combobyte = bin(list(map(int, addressDataNPC["integer_values"].split(' ')))[7])
		# form full binary expression
		fullByte = (10 - len(combobyte)) * '0' + combobyte[2:]
		# split it into two nibbles
		nb1 = fullByte[0:4]
		nb2 = fullByte[4:8]
		# now generate the correct nibble for the object type
		nibbleBall = bin(commandBall)
		# print(nibbleBall)
		fullNibble = nb1 + ((6 - len(combobyte)) * '0' + nibbleBall[2:])
		# print(fullNibble)
		newBallByte = int(fullNibble, 2)
		# print(newBallByte)
		romMap[addressDataNPC["address_range"]["begin"] + 7] = newBallByte
		romMap[addressDataNPC["address_range"]["begin"] + 11] = flag_bytes[0]
		romMap[addressDataNPC["address_range"]["begin"] + 12] = flag_bytes[1]
		romMap[addressData["address_range"]["begin"]] = nItemCode
		romMap[addressData["address_range"]["begin"] + 1] = endVal
	else:
		#this converts giveitem commands into verbose giveitem (conveniently the same size!!)
		romMap[addressData["address_range"]["begin"]] = commandVerbose
		romMap[addressData["address_range"]["begin"]+1] = nItemCode
		romMap[addressData["address_range"]["begin"]+2] = endVal
		if(not location.SecondaryCode is None):
			addressData2 = labelData[labelCodeB2]
			romMap[addressData2["address_range"]["begin"]] = commandVerbose
			romMap[addressData2["address_range"]["begin"]+1] = nItemCode
			romMap[addressData2["address_range"]["begin"]+2] = endVal


def WriteItemNameToBuffer(location,labelData,romMap):
	vendingLabel = "ckir_BEFORE"+("".join(location.Name.split())).upper().replace('.','_').replace("'","")+'0VENDINGCODE'
	addressInfo = labelData[vendingLabel]
	addressWrite = addressInfo["address_range"]["begin"]

	vendingString = location.HardcodedName[location.HardcodedName.index("\"")+1 : location.HardcodedName.rindex("\"")]

	vendSpaceMax = vendingString.rindex(" ")

	#TODO: Replace TM with TM Number (shorter)
	itemNameToWrite = Items.GetCorrectItemName(location.item)

	itemNameToWrite = itemNameToWrite.replace("_"," ")

	#TODO: Looks weird if price ends up small
	#if len(itemNameToWrite) >= vendSpaceMax and " " in itemNameToWrite:
	#	itemNameToWrite = itemNameToWrite.replace(" ", "")

	itemNameToWrite = itemNameToWrite[0:min(len(itemNameToWrite),vendSpaceMax)]

	#print("Write to buffer:", itemNameToWrite, "for", location.Name)

	for i in range(0, vendSpaceMax):
		if i >= len(itemNameToWrite):
			character = " "
		else:
			character = itemNameToWrite[i]

		byteToWrite = ByteToGBCCharacterByte(character)

		romMap[addressWrite+i] = byteToWrite


def WriteShopToRomMemory(location, labelData, itemScriptLookup, romMap):
	potentialFilenames = location.FileName.split(",")
	# Handle a shop which might change stock over time but shares some items
	for pFileName in potentialFilenames:
		if len(potentialFilenames) == 1:
			beforeLabel = "ckir_BEFORE"+ \
					  (("".join(location.Name.split())+"0ITEMCODE").upper())
		else:
			beforeLabel = "ckir_BEFORE" + \
						  (("".join(location.Name.split()) + "0ITEMCODE"
							+"_"+str(potentialFilenames.index(pFileName))).upper())


		addressData = labelData[beforeLabel]

		nItemCodeData = itemScriptLookup(location.item, forceItem=True)
		nItemCode = nItemCodeData[0]
		itemType = nItemCodeData[1]
		if itemType == "Item" or itemType == "Flag":
			if location.isBargainShop() or location.isBuenaItem():
				# Bargain shop item contains price also, so is different
				romMap[addressData["address_range"]["begin"]] = nItemCode
			else:
				romMap[addressData["address_range"]["begin"] + 1] = nItemCode
		else:
			# This will write the other byte of shopitem macro in future
			# This is not yet supported by speedchoice engine changes
			raise Exception("Not yet supported::", itemType, location.Name, location.item)


def WriteAideBallsToRomMemory(location,labelData,itemScriptLookup,romMap):
	labelCodeB = "ckir_BEFORE"+("".join(location.Name.split())).upper().replace('.','_').replace("'","")+'0ITEMCODE'
	#print('Writing'+labelCodeB)
	addressData = labelData[labelCodeB]
	nItemCodeData = itemScriptLookup(location.item)
	nItemCode = nItemCodeData[0]
	itemType = nItemCodeData[1]
	if(itemType == 'Item'):
		commandVerbose = 158
		nextVal = nItemCode
		endVal = 5
	elif(itemType == 'Flag'):
		commandVerbose = 175
		nextVal = nItemCode
		endVal = 1
	elif(itemType == 'Rod'):
		commandVerbose = 177
		nextVal = 0
		endVal = 176
		nItemCode = 176
	romMap[addressData["address_range"]["begin"]] = commandVerbose
	romMap[addressData["address_range"]["begin"]+1] = nItemCode
	romMap[addressData["address_range"]["begin"]+2] = endVal
	# if(itemType == 'Item'):
		# romMap[addressData["address_range"]["begin"]+6] = nItemCode
		# romMap[addressData["address_range"]["begin"]+12] = nItemCode
	# else:
		# if itemType != 'ROD':
			# romMap[addressData["address_range"]["begin"]+6] = nItemCode
		# else:
			# romMap[addressData["address_range"]["begin"]+6] = 58
		# romMap[addressData["address_range"]["begin"]+11] = commandVerbose
		# romMap[addressData["address_range"]["begin"]+12] = nItemCode
		# romMap[addressData["address_range"]["begin"]+6] = 168
		# romMap[addressData["address_range"]["begin"]+11] = commandVerbose
		# romMap[addressData["address_range"]["begin"]+12] = nItemCode
		# romMap[addressData["address_range"]["begin"]+13] = endVal

def WriteMachinePartToRomMemory(location,labelData,itemScriptLookup,romMap):
	labelCodeB = "ckir_BEFORE"+("".join(location.Name.split())).upper().replace('.','_').replace("'","")+'0ITEMCODE'
	labelCodeBNPC = "ckir_BEFORE"+("".join(location.Name.split())).upper().replace('.','_').replace("'","")+'0ITEMCODEB'

	#print('Writing '+labelCodeB+' with '+location.item)
	addressData = labelData[labelCodeB]
	addressDataNPC = labelData[labelCodeBNPC]
	nItemCodeData = itemScriptLookup(location.item)
	nItemCode = nItemCodeData[0]
	itemType = nItemCodeData[1]
	if(itemType == 'Item'):
		command = 7
		nextVal = nItemCode
	elif(itemType == 'Flag'):
		command = 9
		nextVal = nItemCode
	elif(itemType == 'Rod'):
		command = 10
		nextVal = 0
		nItemCode = 0
	romMap[addressDataNPC["address_range"]["begin"]+2] = command
	romMap[addressData["address_range"]["begin"]+2] = nItemCode
	
	# if not location.OtherName is None:
	# 	labelCodeB = "ckir_BEFORE"+("".join(location.OtherName.split())).upper().replace('.','_').replace("'","")+'0ITEMCODE'
	# 	labelCodeBNPC = "ckir_BEFORE"+("".join(location.OtherName.split())).upper().replace('.','_').replace("'","")+'0ITEMCODEB'
	#
	# 	#print('Writing '+labelCodeB+' with '+location.item)
	# 	addressData = labelData[labelCodeB]
	# 	addressDataNPC = labelData[labelCodeBNPC]
	# 	nItemCodeData = itemScriptLookup(location.item)
	# 	nItemCode = nItemCodeData[0]
	# 	itemType = nItemCodeData[1]
	# 	if(itemType == 'Item'):
	# 		command = 7
	# 		nextVal = nItemCode
	# 	elif(itemType == 'Flag'):
	# 		command = 9
	# 		nextVal = nItemCode
	# 	elif(itemType == 'Rod'):
	# 		command = 10
	# 		nextVal = 0
	# 		nItemCode = 0
	# 	romMap[addressDataNPC["address_range"]["begin"]+2] = command
	# 	romMap[addressData["address_range"]["begin"]+2] = nItemCode



def LabelAllLocations(locations):
	#codeLookup = Items.makeItemCodeDict()
	#textLookup = Items.makeItemTextDict()
	for i in locations:
		if i.isShop():
			LabelShopLocation(i)
		elif i.isItem() or i.Type == 'Dummy' or i.isVendingMachine() or i.isPrize():
			LabelItemLocation(i)
		elif i.isGym():
			LabelBadgeLocation(i)

def LabelBadgeLocation(location):
	print("Labeling "+location.Name)

	#open the relevant file and get it as a string
	file = open("RandomizerRom/maps/"+location.FileName)
	filecode = file.read()
	newfile = filecode
	#constuct new script that gives the new item
	#replace is technically deprecated, but this is more readable

	#find the code we need to replace
	coderegexstr = "("+re.escape(location.Code.replace("    ","\t").replace("\tBADGELINE","REPTHIS")).replace("REPTHIS","(.+)")+")"
	codeSearchResults = re.findall(coderegexstr,filecode)
	if len(codeSearchResults) == 0:
		print("Invalid::test", location.Name)
		#return
		raise Exception("Invalid code search results")
	codeSearch = codeSearchResults[0]
	oldcode = codeSearch[0]

	#TODO: Add a check that this is actually the right line in here!
	splitCode = location.Code.split("\n")
	badgeLineValue = [ x for x in splitCode if "BADGELINE" in x ]
	if len(badgeLineValue) == 0:
		raise Exception("Not badge line found in badge description")
	badgeIndex = splitCode.index(badgeLineValue[0])
	foundLine = oldcode.split("\n")[badgeIndex]

	if "verbosesetflag" not in foundLine:
		raise Exception("Invalid badge line code given::"+foundLine)

	#print(codeSearch)
	labelCodeB = ".ckir_BEFORE"+("".join(location.Name.split())).upper().replace('.','_').replace("'","")+'0BADGECODE::\n'
	labelCodeA = "\n.ckir_AFTER"+("".join(location.Name.split())).upper().replace('.','_').replace("'","")+'0BADGECODE::\n'
	newCode = ""
	newcode = oldcode.replace(codeSearch[1],labelCodeB+codeSearch[1]+labelCodeA)

	newfile = filecode.replace(oldcode,newcode)
	#write the new file into the files for the randomizer rom
	newfilestream = open("RandomizerRom/maps/"+location.FileName,'w')
	newfilestream.seek(0)
	newfilestream.write(newfile)
	newfilestream.truncate()
	newfilestream.flush()
	os.fsync(newfilestream.fileno())
	newfilestream.close()

	if(not location.SecondaryCode is None):
		print("Secondary Labelling "+location.Name)
		#open the relevant file and get it as a string
		file = open("RandomizerRom/maps/"+location.SecondaryFile)
		filecode = file.read()
		newfile = filecode
		#constuct new script that gives the new item
		#replace is technically deprecated, but this is more readable

		#find the code we need to replace
		coderegexstr = "("+re.escape(location.SecondaryCode.replace("    ","\t").replace("\tBADGELINE","REPTHIS")).replace("REPTHIS","(.+)")+")"
		codeSearch = re.findall(coderegexstr,filecode)[0]
		oldcode = codeSearch[0]
		#print(codeSearch)
		labelCodeB = ".ckir_BEFORE"+("".join(location.Name.split())).upper().replace('.','_').replace("'","")+'0BADGECODEB::\n'
		labelCodeA = "\n.ckir_AFTER"+("".join(location.Name.split())).upper().replace('.','_').replace("'","")+'0BADGECODEB::\n'
		newCode = ""
		newcode = oldcode.replace(codeSearch[1],labelCodeB+codeSearch[1]+labelCodeA)

		newfile = filecode.replace(oldcode,newcode)
		#write the new file into the files for the randomizer rom
		newfilestream = open("RandomizerRom/maps/"+location.SecondaryFile,'w')
		newfilestream.seek(0)
		newfilestream.write(newfile)
		newfilestream.truncate()
		newfilestream.flush()
		os.fsync(newfilestream.fileno())
		newfilestream.close()

def LabelWild():
	#load up the trainer file
	jgfile = open("VanillaSpeedCrystal/pokecrystal-speedchoice/data/wild/johto_grass.asm")
	kgfile = open("VanillaSpeedCrystal/pokecrystal-speedchoice/data/wild/kanto_grass.asm")
	jwfile = open("VanillaSpeedCrystal/pokecrystal-speedchoice/data/wild/johto_water.asm")
	kwfile = open("VanillaSpeedCrystal/pokecrystal-speedchoice/data/wild/kanto_water.asm")
	sfile = open("VanillaSpeedCrystal/pokecrystal-speedchoice/data/wild/swarm_grass.asm")
	wildDict = {}
	surfDict = {}
	swarmDict = {}
	wildDict["johto_grass.asm"] = jgfile.read()
	wildDict["kanto_grass.asm"] = kgfile.read()
	surfDict["johto_water.asm"] = jwfile.read()
	surfDict["kanto_water.asm"] = kwfile.read()
	swarmDict["swarm_grass.asm"] = sfile.read()
	#loop through locations
	#load up the grass data
	yamlfile = open("Wild Data/wildGrass.yaml")
	yamltext = yamlfile.read()
	wildData = yaml.load(yamltext, Loader=yaml.FullLoader)
	for j in wildData:
		#print('Writing '+j)
		areaData = wildData[j.upper()]
		newcode = areaData['Code']
		minLV = areaData['Level']
		idTextB = "\nckir_BEFORE"+"".join(j.upper().replace("_","").split())+"0WILDGRASS"+"::\n\n\t"
		idTextA = "\nckir_AFTER"+"".join(j.upper().replace("_","").split())+"0WILDGRASS"+"::\n\n"
		wildDict[areaData["File"]] = wildDict[areaData["File"]].replace(areaData['Code'],idTextB+areaData['Code']+idTextA)
	for i in wildDict:
		newfilestream = open("RandomizerRom/data/wild/"+i,'r+')
		newfilestream.seek(0)
		newfilestream.write(wildDict[i])
		newfilestream.flush()
		newfilestream.truncate()
		newfilestream.flush()
		os.fsync(newfilestream.fileno())
		newfilestream.close()
	#loop through locations
	#load up the water data
	yamlfile = open("Wild Data/surfGrass.yaml")
	yamltext = yamlfile.read()
	wildData = yaml.load(yamltext, Loader=yaml.FullLoader)
	for j in wildData:
		#print('Writing '+j)
		areaData = wildData[j.upper()]
		newcode = areaData['Code']
		minLV = areaData['Level']
		idTextB = "\nckir_BEFORE"+"".join(j.upper().replace("_","").split())+"0WILDWATER"+"::\n\n\t"
		idTextA = "\nckir_AFTER"+"".join(j.upper().replace("_","").split())+"0WILDWATER"+"::\n"
		surfDict[areaData["File"]] =  surfDict[areaData["File"]].replace(areaData['Code'],idTextB+areaData['Code']+idTextA)
	for i in surfDict:
		newfilestream = open("RandomizerRom/data/wild/"+i,'w')
		newfilestream.seek(0)
		newfilestream.write(surfDict[i])
		newfilestream.flush()
		newfilestream.truncate()
		newfilestream.flush()
		os.fsync(newfilestream.fileno())
		newfilestream.close()
	#loop through locations
	#load up the swarm data
	yamlfile = open("Wild Data/swarmGrass.yaml")
	yamltext = yamlfile.read()
	wildData = yaml.load(yamltext, Loader=yaml.FullLoader)
	for j in wildData:
		#print('Writing '+j)
		areaData = wildData[j.upper()]
		newcode = areaData['Code']
		minLV = areaData['Level']
		idTextB = "\n.ckir_BEFORE"+"".join(j.upper().replace("_","").split())+"0WILDSWARM"+"::\n\n\t"
		idTextA = "\n.ckir_AFTER"+"".join(j.upper().replace("_","").split())+"0WILDSWARM"+"::\n"
		swarmDict[areaData["File"]] =  swarmDict[areaData["File"]].replace(areaData['Code'],idTextB+areaData['Code']+idTextA)
	for i in swarmDict:
		newfilestream = open("RandomizerRom/data/wild/"+i,'w')
		newfilestream.seek(0)
		newfilestream.write(swarmDict[i])
		newfilestream.flush()
		newfilestream.truncate()
		newfilestream.flush()
		os.fsync(newfilestream.fileno())
		newfilestream.close()

def LabelSpecialWild(locationList):
	monList = []
	locationDict = {}
	for i in locationList:
		locationDict[i.Name] = i
	#print("Editing Special Pokemon")
	for root, dir, files  in os.walk("Special Pokemon Locations"):
		for file in files:
			#print("File: "+file)
			entry = open("Special Pokemon Locations/"+file,'r')
			yamlData = yaml.load(entry, Loader=yaml.FullLoader)
			loc = yamlData["Location"]
			if(True):
				fileName = locationDict[loc].FileName
				mon = yamlData["NormalMon"]
				shift = yamlData["LevelShift"]
				type = yamlData["Type"]
				code = yamlData["Code"]
				#we don't bother with having restrictions on these, as in general these pokemon are potentially missable
				newmon = mon

				idTextB = ".ckir_BEFORE"+"".join(loc.upper().split()).replace('.','_').replace("'","")+"0SPECIALWILD"+"::\n"
				idTextA = "\n.ckir_AFTER"+"".join(loc.upper().split()).replace('.','_').replace("'","")+"0SPECIALWILD"+"::\n"
				#find the code we need to replace
				coderegexstr = "("+re.escape(yamlData['Code'].replace('MONNAME',newmon).replace("    ","\t").replace("\tMONLINE","REPTHIS")).replace("REPTHIS","(.+)")+")"
				file = open("RandomizerRom/maps/"+fileName)
				filecode = file.read()
				#print(coderegexstr)
				codeSearch = re.findall(coderegexstr,filecode)[0]
				oldcode = codeSearch[0]
				newcode = oldcode.replace(codeSearch[1],idTextB+codeSearch[1]+idTextA)
				#print(newcode)
				newfile = filecode.replace(oldcode,newcode)
				#write the new file into the files for the randomizer rom
				newfilestream = open("RandomizerRom/maps/"+fileName,'w')
				newfilestream.seek(0)
				newfilestream.write(newfile)
				newfilestream.truncate()
				newfilestream.flush()
				#os.fsync(newfilestream.fileno())
				newfilestream.close()


def LabelTrainerData(trainerData):
	trainerfile = open("VanillaSpeedCrystal/pokecrystal-speedchoice/trainers/trainers.asm")
	newfile = trainerfile.read()
	#loop through locations
	for j in trainerData:
		trainer = trainerData[j]
		#print('Labeling '+j)
		nCode = trainer['Code']
		idTextA = "\n.ckir_BEFORE"+"".join(j.upper().split())+"0TRAINER::\n\t"
		idTextB = "\n.ckir_AFTER"+"".join(j.upper().split())+"0TRAINER::\n\t"
		# for k in range(0,len(trainer['Pokemon'])):
		# 	#print('Labeling mon '+str(k))
		# 	pCode = trainer['Pokemon'][k]['Code'][:-1]
		# 	idTextPB = "\n.ckir_BEFORE"+"".join(j.upper().split())+"0TRAINER0MON"+str(k)+"::\n\t"
		# 	idTextPA = "\n.ckir_AFTER"+"".join(j.upper().split())+"0TRAINER0MON"+str(k)+"::\n"
		# 	#nCode = nCode.replace("\t"+pCode,idTextPB+pCode+idTextPA,1)
		# 	nCode = nCode+idTextPB+pCode+idTextPA
		#newfile = newfile.replace("\t"+trainer['Code'],idText+nCode,1)
		newfile = newfile.replace("\t"+trainer['Code'],idTextA+nCode+idTextB)
	newfilestream = open("RandomizerRom/trainers/trainers.asm",'w')
	newfilestream.seek(0)
	newfilestream.write(newfile)
	newfilestream.truncate()
	newfilestream.flush()
	os.fsync(newfilestream.fileno())
	newfilestream.close()

def LabelBargainShopLocation(location):
	multiData = location.FileName
	shopFilename = multiData.split("/")[0]
	shopName = multiData.split("/")[1]

	shopFile = "RandomizerRom/data/items/" + shopFilename
	file = open(shopFile)
	filecode_unreplaced = file.read()
	filecode = filecode_unreplaced.replace("    ", "\t")
	file.close()

	shopRegex = "(" + shopName + ":\n(;([A-Za-z _\(\)/.]){1,}\n|\tdb \d(.*)\n)(\tdb(w){0,} (.*){1,},(\s){1,}(\d){1,},(\s){1,}(\d){1,}\n|(.ckir_(.*){1,}::\n)){1,}(\tdb -1, -1, -1|\.End)" + ")"
	currentShopDesc = re.findall(shopRegex, filecode)
	shopDetail = currentShopDesc[0][0]

	itemRegex = "db(?:w){0,} " + location.NormalItem + ",\s{1,}\d{1,},\s{1,}\d{1,}\n"
	itemDesc = re.findall(itemRegex, shopDetail)

	beforeLabel = ".ckir_BEFORE" + "".join(location.Name.upper().split()) + "0ITEMCODE::\n"
	afterLabel = ".ckir_AFTER" + "".join(location.Name.upper().split()) + "0ITEMCODE::\n"
	toReplace = "\t" + itemDesc[0]
	replacement = beforeLabel + toReplace + afterLabel

	shopSave = shopDetail.replace(toReplace, replacement)

	changedCode = filecode.replace(shopDetail, shopSave)

	newfilestream = open(shopFile, "w")
	newfilestream.seek(0)
	newfilestream.write(changedCode)
	newfilestream.truncate()
	newfilestream.flush()
	newfilestream.close()


def LabelDrinksMachine(location):
	# TODO: For completeness checklist:
	# GOLDENRODDEPTSTORE6F_FRESH_WATER_PRICE    EQU 350 (Price locked here)
	# verbosegiveitem FRESH_WATER (Actual give item)
	# getitemname STRING_BUFFER_3, FRESH_WATER (Same script, uses hardcoded item lookup again)
	#.MenuData:
    # db STATICMENU_CURSOR ; flags
    # db 4 ; items
    # db "FRESH WATER  ¥200@" (String contains the item and price)
	return

def LabelShopLocation(location):
	print("Labelling", location.Name)

	if location.isBargainShop() or location.isBuenaItem():
		LabelBargainShopLocation(location)
		return

	mart_data_file = "RandomizerRom/data/items/marts.asm"
	file = open(mart_data_file)
	filecode = file.read()
	file.close()

	shopDupeSet = location.FileName.split(",")
	for shopName in shopDupeSet:
		#print(shopName)
		shopRegex = "("+shopName + ":\n\tdb \d(.*)\n(\tshopitem\t\d,.*\n|(.ckir_(.*){1,}::\n)){1,}\tdb -1, -1"+")"
		currentShopDesc = re.findall(shopRegex, filecode.replace("    ","\t"))
		shopDetail = currentShopDesc[0][0]

		itemRegex = "shopitem\t\d{1,}, "+location.NormalItem+"\n"
		itemDesc = re.findall(itemRegex, shopDetail)

		labelExtra = "" if len(shopDupeSet) == 1 else "_"+str(shopDupeSet.index(shopName))

		beforeLabel = ".ckir_BEFORE"+"".join(location.Name.upper().split())+"0ITEMCODE"+labelExtra+"::\n"
		afterLabel = ".ckir_AFTER"+"".join(location.Name.upper().split())+"0ITEMCODE"+labelExtra+"::\n"
		toReplace = "\t" + itemDesc[0]
		replacement = beforeLabel + toReplace + afterLabel

		shopDetailReplaced = shopDetail.replace(toReplace, replacement)
		filecode = filecode.replace(shopDetail, shopDetailReplaced)

	newfilestream = open(mart_data_file, "w")
	newfilestream.seek(0)
	newfilestream.write(filecode)
	newfilestream.truncate()
	newfilestream.flush()
	newfilestream.close()

	return



#currently only labels "regular" items
def LabelItemLocation(location):
	print("Labelling "+location.Name)
	#open the relevant file and get it as a string
	file = open("RandomizerRom/maps/"+location.FileName, encoding="utf-8")
	print("Opening:", location.FileName)
	filecode = file.read()

	#constuct new script that gives the new item
	#replace is technically deprecated, but this is more readable


	#find the code we need to replace
	coderegexstr = "("+re.escape(location.Code.replace("    ","\t").replace("\tITEMLINE","REPTHIS")).replace("REPTHIS","(.+)")+")"
	# print(repr(re.escape(location.Code.replace("    ","\t"))))
	# print(repr(location.Code.replace("    ","\t")))
	# print(repr("\tITEMLINE"))
	# print(repr("\tITEMLINE") in (repr(location.Code.replace("    ","\t"))))
	# print("\tITEMLINE" in (location.Code.replace("    ","\t")))
	# print(coderegexstr)
	codeSearch = None
	if not location.IsSpecial:
		try:
			codeSearchResults = re.findall(coderegexstr,filecode)
			if len(codeSearchResults) == 0:
				raise Exception("Couldnt find code for::"+location.Name)

			codeSearch = codeSearchResults[0]
		except:
			print(coderegexstr)
			print("fail on", location.Name)
			raise Exception("fail to run on:", location.Name)
			return

		oldcode = codeSearch[0]
		#print(codeSearch)
	else:
		coderegexstr = re.escape(location.Code.replace("    ","\t")).replace("ITEMLINE",".+")
		oldcode = re.findall(coderegexstr,filecode)[0]

	splitCode = location.Code.split("\n")
	itemLineValue = [x for x in splitCode if "ITEMLINE" in x]
	if len(itemLineValue) == 0:
		raise Exception("Not item line found in item code description")
	itemIndex = splitCode.index(itemLineValue[0])
	foundLine = oldcode.split("\n")[itemIndex]

	if "giveitem" not in foundLine and "hiddenitem" not in foundLine and "verbosesetflag" not in foundLine\
			and "itemball" not in foundLine and "fruittree" not in foundLine:
		raise Exception("Invalid item line code given::" + foundLine)

	#if this is an itemball, we need to find out what the command is because we're also going to need to find the line that actually
	if location.IsBall or location.IsBerry:
		#find the code on the line BEFORE the one we need to modify
		#fortunately, we have these lines already labeled, we need them to label something else
		commandregexstr = "(\w+):"
		commandSearch = re.findall(commandregexstr,location.Code)[0]
		npcRegex = ("[^\n]+")+commandSearch+",[^\n]+\n"
		npcSearchT = re.findall(npcRegex,filecode)
		if len(npcSearchT) == 0:
			raise Exception("Unable to find NPC Data for itemball/berry::"+npcRegex)
		else:
			npcSearch = npcSearchT[0]

	labelCodeB = ".ckir_BEFORE"+("".join(location.Name.split())).upper().replace('.','_').replace("'","")+'0ITEMCODE::\n'
	labelCodeA = "\n.ckir_AFTER"+("".join(location.Name.split())).upper().replace('.','_').replace("'","")+'0ITEMCODE::\n'
	labelCodeBNPC = ".ckir_BEFORE"+("".join(location.Name.split())).upper().replace('.','_').replace("'","")+'0NPCCODE::\n'
	labelCodeANPC = ".ckir_AFTER"+("".join(location.Name.split())).upper().replace('.','_').replace("'","")+'0NPCCODE::\n'
	newCode = ""

	if not location.IsSpecial:
		newcode = oldcode.replace(codeSearch[1],labelCodeB+codeSearch[1]+labelCodeA)
		#switch spaces to tabs.....
		newcode = newcode.replace("    ","\t")
		#newcode = newcode.replace("verbosegiveitem", "giveitem")
	if not location.IsSpecial:
		newfile = filecode.replace(oldcode,newcode)
		if(location.IsBall or location.IsBerry):
			newfile = newfile.replace(npcSearch,labelCodeBNPC+npcSearch+labelCodeANPC)
	else:
		labelCodeB = ".ckir_BEFORE"+("".join(location.Name.split())).upper().replace('.','_').replace("'","")+'0ITEMCODE::\n'
		labelCodeA = "\n.ckir_AFTER"+("".join(location.Name.split())).upper().replace('.','_').replace("'","")+'0ITEMCODE::\n'
		#need to do this because asm label weirdness (more accurately regex weirdness with them)
		if ":" in oldcode:
			lines = oldcode.partition('\n')
			newfile = filecode.replace(oldcode,lines[0]+"\n"+labelCodeB+"".join(lines[1:])+labelCodeA)
		else:
			newfile = filecode.replace(oldcode,labelCodeB+oldcode+labelCodeA)

	if location.HardcodedName is not None:
		vendingLabelB = ".ckir_BEFORE" + ("".join(location.Name.split())).upper().replace('.', '_')\
			.replace("'","") + '0VENDINGCODE::\n'
		vendingLabelA = "\n.ckir_AFTER" + ("".join(location.Name.split())).upper().replace('.', '_')\
			.replace("'","") + '0VENDINGCODE::\n'

		vendingLine = re.escape(location.HardcodedName)
		codeSearchResults = re.findall(vendingLine, newfile)
		item = codeSearchResults[0]

		newfile = newfile.replace(item, vendingLabelB + item + vendingLabelA)

	hardcoded_prize_labelling = False
	if location.isVendingMachine():
		hardcoded_prize_labelling = True
		label_desc = "checkmoney YOUR_MONEY,"
	elif location.isPrize():
		hardcoded_prize_labelling = True
		label_desc = "checkcoins"

	if hardcoded_prize_labelling:
		#checkmoney YOUR_MONEY, GOLDENRODDEPTSTORE6F_FRESH_WATER_PRICE
		name_regex = label_desc + " ([A-Z0-9_]{1,}_(PRICE|COINS))"
		foundPrice = re.search(name_regex, location.Code)
		if foundPrice:
			priceVariable = foundPrice.group(1)
			#GOLDENRODDEPTSTORE6F_FRESH_WATER_PRICE EQU 200
			#variable_defined_regex = priceVariable+"\s{1,}EQU\s{1,}\d{1,5}\n"
			variable_used_regex = "\t(?:check|take)[a-zA-Z, _]{1,} "+priceVariable+"\n"
			priceUses = re.findall(variable_used_regex, newfile)

			if len(priceUses) != 2:
				raise Exception("Invalid price set handling", priceVariable, priceUses)

			priceCheck = priceUses[0]
			vendingPriceLabelB = ".ckir_BEFORE" + ("".join(location.Name.split())).upper().replace('.', '_') \
				.replace("'", "") + '0VENDINGPRICECODE1::\n'
			vendingPriceLabelA = ".ckir_AFTER" + ("".join(location.Name.split())).upper().replace('.', '_') \
				.replace("'", "") + '0VENDINGPRICECODE1::\n'

			priceTake = priceUses[1]
			vendingPriceLabelB2 = ".ckir_BEFORE" + ("".join(location.Name.split())).upper().replace('.', '_') \
				.replace("'", "") + '0VENDINGPRICECODE2::\n'
			vendingPriceLabelA2 = ".ckir_AFTER" + ("".join(location.Name.split())).upper().replace('.', '_') \
				.replace("'", "") + '0VENDINGPRICECODE2::\n'

			print("cc", priceCheck, priceTake, priceUses, variable_used_regex, priceVariable)

			newfile = newfile.replace(priceCheck, vendingPriceLabelB+priceCheck+vendingPriceLabelA)
			newfile = newfile.replace(priceTake, vendingPriceLabelB2 + priceTake + vendingPriceLabelA2)

		else:
			raise Exception("Could not find price")





	#write the new file into the files for the randomizer rom
	newfilestream = open("RandomizerRom/maps/"+location.FileName,'w', encoding="utf-8")
	newfilestream.seek(0)
	newfilestream.write(newfile)
	newfilestream.truncate()
	newfilestream.flush()
	#os.fsync(newfilestream.fileno())
	newfilestream.close()

	#if there is a secondary set of code that also needs to be written, write it
	if(not location.SecondaryCode is None):
		print("Secondary Labelling "+location.Name)
		#open the relevant file and get it as a string
		file = open("RandomizerRom/maps/"+location.SecondaryFile, encoding="utf-8")
		filecode = file.read()

		#constuct new script that gives the new item
		#replace is technically deprecated, but this is more readable


		#find the code we need to replace
		coderegexstr = "("+re.escape(location.SecondaryCode.replace("    ","\t").replace("\tITEMLINE","REPTHIS")).replace("REPTHIS","(.+)")+")"
		#print(repr(re.escape(location.Code.replace("    ","\t"))))
		#print(repr(location.Code.replace("    ","\t")))
		#print(repr("\tITEMLINE"))
		#print(repr("\tITEMLINE") in (repr(location.Code.replace("    ","\t"))))
		#print("\tITEMLINE" in (location.Code.replace("    ","\t")))
		#print(coderegexstr)
		codeSearch = None
		if not location.IsSpecial:
			#print(coderegexstr)
			codeSearch = re.findall(coderegexstr,filecode)[0]
			oldcode = codeSearch[0]
			#print(codeSearch)
		else:
			coderegexstr = re.escape(location.SecondaryCode.replace("    ","\t")).replace("ITEMLINE",".+")
			#print(repr(coderegexstr))
			#print(repr(filecode))
			oldcode = re.findall(coderegexstr,filecode)[0]
		#if this is an itemball, we need to find out what the command is because we're also going to need to find the line that actually
		if location.IsBall or location.IsBerry:
			#find the code on the line BEFORE the one we need to modify
			#fortunately, we have these lines already labeled, we need them to label something else
			commandregexstr = "(\w+):"
			commandSearch = re.findall(commandregexstr,location.SecondaryCode)[0]
			npcRegex = ("[^\n]+")+commandSearch+",[^\n]+\n"
			npcSearch = re.findall(npcRegex,filecode)[0]
		labelCodeB = ".ckir_BEFORE"+("".join(location.Name.split())).upper().replace('.','_').replace("'","")+'0ITEMCODEB::\n'
		labelCodeA = "\n.ckir_AFTER"+("".join(location.Name.split())).upper().replace('.','_').replace("'","")+'0ITEMCODEB::\n'
		labelCodeBNPC = ".ckir_BEFORE"+("".join(location.Name.split())).upper().replace('.','_').replace("'","")+'0NPCCODEB::\n'
		labelCodeANPC = ".ckir_AFTER"+("".join(location.Name.split())).upper().replace('.','_').replace("'","")+'0NPCCODEB::\n'
		newCode = ""
		if not location.IsSpecial:
			newcode = oldcode.replace(codeSearch[1],labelCodeB+codeSearch[1]+labelCodeA)
			#switch spaces to tabs.....
			newcode = newcode.replace("    ","\t")
			#newcode = newcode.replace("verbosegiveitem", "giveitem")

		if not location.IsSpecial:
			newfile = filecode.replace(oldcode,newcode)
			if(location.IsBall):
				newfile = newfile.replace(npcSearch,labelCodeBNPC+npcSearch+labelCodeANPC)
		else:
			labelCodeB = ".ckir_BEFORE"+("".join(location.Name.split())).upper().replace('.','_').replace("'","")+'0ITEMCODEB::\n'
			labelCodeA = "\n.ckir_AFTER"+("".join(location.Name.split())).upper().replace('.','_').replace("'","")+'0ITEMCODEB::\n'
			#need to do this because asm label weirdness (more accurately regex weirdness with them)
			if ":" in oldcode:
				lines = oldcode.partition('\n')
				newfile = filecode.replace(oldcode,lines[0]+"\n"+labelCodeB+"".join(lines[1:])+labelCodeA)
			else:
				newfile = filecode.replace(oldcode,labelCodeB+oldcode+labelCodeA)
		#write the new file into the files for the randomizer rom
		newfilestream = open("RandomizerRom/maps/"+location.SecondaryFile,'w', encoding="utf-8")
		newfilestream.seek(0)
		newfilestream.write(newfile)
		newfilestream.truncate()
		newfilestream.flush()
		#os.fsync(newfilestream.fileno())
		newfilestream.close()

def WriteLocationToRom(location, itemScriptLookup, itemTextLookup):
	#print("Writing "+location.Name+" which contains "+location.item)
	#open the relevant file and get it as a string
	file = open("RandomizerRom/maps/"+location.FileName)
	filecode = file.read()

	#constuct new script that gives the new item
	#replace is technically deprecated, but this is more readable
	newcode = location.Code.replace("ITEMLINE",itemScriptLookup(location.item,location.IsBall,location.IsSpecial))
	#switch spaces to tabs.....
	newcode = newcode.replace("    ","\t")

	#find the code we need to replace
	coderegexstr = re.escape(location.Code.replace("    ","\t")).replace("ITEMLINE",".+")
	oldcode = re.findall(coderegexstr,filecode)[0]


	newtext = ""
	if location.Text is not None:
		#construct a new script that updates text about the new item
		newtext = location.Text.replace("ITEMNAME",itemTextLookup(location.item))
		#switch spaces to tabs.....
		newtext = newtext.replace("    ","\t")

		#find the text we need to replace
		textregexstr = re.escape(location.Text.replace("    ","\t")).replace("ITEMNAME",".+")
		oldtext = re.findall(textregexstr,filecode)[0]
	else:
		oldtext = ""

	#make new file with the new text
	newfile = filecode.replace(oldcode,newcode).replace(oldtext,newtext)

	#write the new file into the files for the randomizer rom
	newfilestream = open("RandomizerRom/maps/"+location.FileName,'w')
	newfilestream.seek(0)
	newfilestream.write(newfile)
	newfilestream.truncate()
	newfilestream.flush()
	#os.fsync(newfilestream.fileno())
	newfilestream.close()

def WriteBadgeToRom(location):
	#print("Writing "+location.Name+" which contains "+location.badge.Name)

	#open the relevant file and get it as a string
	file = open("RandomizerRom/maps/"+location.FileName)
	filecode = file.read()
	newfile = filecode
	#constuct new script that gives the new item
	#replace is technically deprecated, but this is more readable

	newcode = location.Code.replace("BADGELINE","ENGINE_"+location.badge.Name.replace(" ","").upper())
	#switch spaces to tabs.....
	newcode = newcode.replace("    ","\t")
	#find the code we need to replace
	coderegexstr = re.escape(location.Code.replace("    ","\t")).replace("BADGELINE",".+")
	oldcode = re.findall(coderegexstr,filecode)[0]
	newfile = filecode.replace(oldcode,newcode)
	#write the new file into the files for the randomizer rom
	newfilestream = open("RandomizerRom/maps/"+location.FileName,'w')
	newfilestream.seek(0)
	newfilestream.write(newfile)
	newfilestream.truncate()
	newfilestream.flush()
	os.fsync(newfilestream.fileno())
	newfilestream.close()

	newtext = ""
	if location.Text is not None:
		for i in location.Text:
			file = open("RandomizerRom/maps/"+i["File"])
			filecode = file.read()
			newfile = filecode
			#construct a new script that updates text about the new item
			newtext = i['Text'].replace("BADGENAME",location.badge.Name.upper())
			#switch spaces to tabs.....
			newtext = newtext.replace("    ","\t")
			#find the text we need to replace
			textregexstr = re.escape(i['Text'].replace("    ","\t")).replace("BADGENAME",".+")
			oldtext = re.findall(textregexstr,filecode)[0]
			newfile = newfile.replace(oldtext,newtext)
			newfilestream = open("RandomizerRom/maps/"+i["File"],'w')
			newfilestream.seek(0)
			newfilestream.write(newfile)
			newfilestream.truncate()
			newfilestream.flush()
			#os.fsync(newfilestream.fileno())
			newfilestream.close()


	#make new file with the new text
	newfile = filecode.replace(oldcode,newcode).replace(oldtext,newtext)

	#write the new file into the files for the randomizer rom
	newfilestream = open("RandomizerRom/maps/"+location.FileName,'w')
	newfilestream.seek(0)
	newfilestream.write(newfile)
	newfilestream.truncate()
	newfilestream.flush()
	os.fsync(newfilestream.fileno())
	newfilestream.close()


def WriteItemLocations(locations):
	codeLookup = Items.makeItemCodeDict()
	textLookup = Items.makeItemTextDict()
	for i in locations:
		if i.isItem():
			WriteLocationToRom(i,codeLookup,textLookup)
		elif i.isGym():
			WriteBadgeToRom(i)

def WriteTrainerLevels(locationDict, distDict, trainerData):
	trainerfile = open("Game Files/pokecrystal-speedchoice/trainers/trainers.asm")
	newfile = trainerfile.read()
	#loop through locations
	for i in distDict:
		if i in locationDict:
			location = locationDict[i]
			if location.Trainers is not None:
				for j in location.Trainers:
					#print('Writing '+j+" at "+location.Name)
					trainer = trainerData[j]
					newcode = trainer['Code']
					for k in trainer['Pokemon']:
						pokemon = k['Pokemon']
						pCode = k['NewCode']
						level = k['Level']
						newlevel = max(level-location.AreaLevel+distDict[i], 2)
						npCode = pCode.replace("db "+str(level),"db "+str(newlevel),1)
						newcode = newcode.replace(k['Code'],npCode,1)
					newfile = newfile.replace(trainer['Code'],newcode)
	newfilestream = open("RandomizerRom/trainers/trainers.asm",'w')
	newfilestream.seek(0)
	newfilestream.write(newfile)
	newfilestream.truncate()
	newfilestream.flush()
	os.fsync(newfilestream.fileno())
	newfilestream.close()

def WriteWildLevels(locationDict, distDict,monFun):
	#load up the trainer file
	jgfile = open("Game Files/pokecrystal-speedchoice/data/wild/johto_grass.asm")
	kgfile = open("Game Files/pokecrystal-speedchoice/data/wild/kanto_grass.asm")
	jwfile = open("Game Files/pokecrystal-speedchoice/data/wild/johto_water.asm")
	kwfile = open("Game Files/pokecrystal-speedchoice/data/wild/kanto_water.asm")
	sfile = open("Game Files/pokecrystal-speedchoice/data/wild/swarm_grass.asm")
	wildDict = {}
	surfDict = {}
	swarmDict = {}
	wildDict["johto_grass.asm"] = jgfile.read()
	wildDict["kanto_grass.asm"] = kgfile.read()
	surfDict["johto_water.asm"] = jwfile.read()
	surfDict["kanto_water.asm"] = kwfile.read()
	swarmDict["swarm_grass.asm"] = sfile.read()
	surfDist = max(distDict['Surf'],distDict['Fog Badge'])
	#loop through locations
	#load up the grass data
	yamlfile = open("Wild Data/wildGrass.yaml")
	yamltext = yamlfile.read()
	wildData = yaml.load(yamltext, Loader=yaml.FullLoader)
	for i in distDict:
		if i in locationDict:
			location = locationDict[i]
			if location.WildTableList is not None:
				for j in location.WildTableList:
					#print('Writing '+j+" at "+location.Name)
					if j.upper() in wildData:
						areaData = wildData[j.upper()]
						newcode = areaData['Code']
						minLV = areaData['Level']
						for k in areaData['Pokemon']:
							for l in areaData['Pokemon'][k]:
								pokemon = monFun(k,distDict[i])
								level = l
								newlevel = max(level-minLV+distDict[i], 2)
								newcode = newcode.replace("db "+str(level)+", "+k,"db "+str(newlevel)+", "+pokemon )
						#print(areaData["Code"] in areaData["File"])
						wildDict[areaData["File"]] = wildDict[areaData["File"]].replace(areaData['Code'],newcode)
	for i in wildDict:
		newfilestream = open("RandomizerRom/data/wild/"+i,'w')
		newfilestream.seek(0)
		newfilestream.write(wildDict[i])
		newfilestream.truncate()
		newfilestream.flush()
		os.fsync(newfilestream.fileno())
		newfilestream.close()
	#loop through locations
	#load up the water data
	yamlfile = open("Wild Data/surfGrass.yaml")
	yamltext = yamlfile.read()
	wildData = yaml.load(yamltext, Loader=yaml.FullLoader)
	for i in distDict:
		if i in locationDict:
			location = locationDict[i]
			if location.WildTableList is not None:
				for j in location.WildTableList:
					#print('Writing '+j+" at "+location.Name)
					if j.upper() in wildData:
						areaData = wildData[j.upper()]
						newcode = areaData['Code']
						minLV = areaData['Level']
						for k in areaData['Pokemon']:
							for l in areaData['Pokemon'][k]:
								pokemon = monFun(k,distDict[i])
								level = l
								newlevel = max(level-minLV+max(distDict[i],surfDist), 2)
								newcode = newcode.replace("db "+str(level)+", "+k,"db "+str(newlevel)+", "+pokemon )
						surfDict[areaData["File"]] = surfDict[areaData["File"]].replace(areaData['Code'],newcode)
	for i in surfDict:
		newfilestream = open("RandomizerRom/data/wild/"+i,'w')
		newfilestream.seek(0)
		newfilestream.write(surfDict[i])
		newfilestream.truncate()
		newfilestream.flush()
		os.fsync(newfilestream.fileno())
		newfilestream.close()
	#loop through locations
	#load up the swarm data
	yamlfile = open("Wild Data/swarmGrass.yaml")
	yamltext = yamlfile.read()
	wildData = yaml.load(yamltext, Loader=yaml.FullLoader)
	for i in distDict:
		if i in locationDict:
			location = locationDict[i]
			if location.WildTableList is not None:
				for j in location.WildTableList:
					if j.upper() in wildData:
						#print('Writing '+j+" at "+location.Name)
						areaData = wildData[j.upper()]
						newcode = areaData['Code']
						minLV = areaData['Level']
						for k in areaData['Pokemon']:
							for l in areaData['Pokemon'][k]:
								pokemon = monFun(k,distDict[i])
								level = l
								newlevel = max(level-minLV+distDict[i], 2)
								newcode = newcode.replace("db "+str(level)+", "+k,"db "+str(newlevel)+", "+pokemon )
						swarmDict[areaData["File"]] = swarmDict[areaData["File"]].replace(areaData['Code'],newcode)
	for i in swarmDict:
		newfilestream = open("RandomizerRom/data/wild/"+i,'w')
		newfilestream.seek(0)
		newfilestream.write(swarmDict[i])
		newfilestream.truncate()
		newfilestream.flush()
		os.fsync(newfilestream.fileno())
		newfilestream.close()

def WriteSpecialWildLevels(locationDict,distDict,monFun):
	monList = []
	#print("Editing Special Pokemon")
	for root, dir, files  in os.walk("Special Pokemon Locations"):
		for file in files:
			#print("File: "+file)
			entry = open("Special Pokemon Locations/"+file,'r')
			yamlData = yaml.load(entry, Loader=yaml.FullLoader)
			loc = yamlData["Location"]
			if(loc in locationDict):
				fileName = locationDict[loc].FileName
				mon = yamlData["NormalMon"]
				shift = yamlData["LevelShift"]
				type = yamlData["Type"]
				code = yamlData["Code"]
				#we don't bother with having restrictions on these, as in general these pokemon are potentially missable
				newmon = monFun(mon,1001)
				givestr = ""
				if(type == 'Give Mon with Berry'):
						givestr = 'givepoke '+newmon+', '+str(distDict[loc]+shift)+', BERRY'
				if(type == 'Wild Pokemon'):
					givestr = 'loadwildmon '+newmon+', '+str(distDict[loc]+shift)
				if(type == 'Give Egg'):
					givestr = 'giveegg '+newmon+', '+str(distDict[loc]+shift)
				if(type == 'Give Poke'):
					givestr = 'givepoke '+newmon+', '+str(distDict[loc]+shift)
				newcode = code.replace("MONLINE",givestr).replace("MONNAME",newmon)
				#switch spaces to tabs.....
				newcode = newcode.replace("    ","\t")

				#find the code we need to replace
				coderegexstr = re.escape(code.replace("    ","\t")).replace("MONLINE",".+").replace("MONNAME",".+")
				file = open("RandomizerRom/maps/"+fileName)
				filecode = file.read()
				oldcode = re.findall(coderegexstr,filecode)[0]
				newfile = filecode.replace(oldcode,newcode)
				#write the new file into the files for the randomizer rom
				newfilestream = open("RandomizerRom/maps/"+fileName,'w')
				newfilestream.seek(0)
				newfilestream.write(newfile)
				newfilestream.truncate()
				newfilestream.flush()
				#os.fsync(newfilestream.fileno())
				newfilestream.close()

import string
def ByteToGBCCharacterByte(charr):
	# TODO: This should be generated and checked against codes in charmap.asm
	upper=string.ascii_uppercase
	lower=string.ascii_lowercase
	digits = "0123456789"

	if charr in upper:
		return 128+upper.index(charr)
	elif charr in lower:
		return 160+lower.index(charr)
	elif charr == " ":
		return 127
	elif charr == "!":
		return 231
	elif charr == ".":
		return 232
	elif charr == "…":
		return 117
	elif charr == "=":
		return 61
	elif charr in digits:
		return 246+digits.index(charr)
	elif charr == "#":
		return 198

	#Special characters
	elif charr == "📛":
		return 199
	elif charr == "❌":
		return 241
	elif charr == "¥":
		return 240

	else:
		return 127

STATIC_DB_COMMAND = 80
STATIC_NEXT_COMMAND = 78
STATIC_TEXT_COMMAND = 0
STATIC_LINE_COMMAND = 79
STATIC_PARA_COMMAND = 81

def WriteHideUnusedSigns(romMap, deadHints):
	for hint in deadHints:
		#oldTile = hint[0].originalTile
		newTile = hint[0].newTile
		mapData = hint[0].tileAddress

		romMap[mapData] = newTile


def WriteDescriptionsToMemory(romMap, hints, hintConfig):
	for hint in hints:
		addrData = hint[0]
		hintData = hint[1]

		if hintConfig.WriteXSigns and hintData.type == "runout" or hintData.type == "small":
			continue

		if hintData.totalLength != addrData.end-addrData.start:
			print("Length decrepency: ", hintData.totalLength,addrData.end-addrData.start)

		for i in range(addrData.start,addrData.end):
			byteToWrite = None

			index = i-addrData.start
			if index == 0:
				byteToWrite = STATIC_TEXT_COMMAND
			else:
				i_dex=1
				for msg in hintData.messages:
					message_length = len(msg.text)
					if index < i_dex + message_length:
						str_index = index - i_dex
						byteToWrite = ByteToGBCCharacterByte(msg.text[str_index])
						break
					i_dex+=message_length
					if index < i_dex + msg.padding:
						byteToWrite = ByteToGBCCharacterByte(" ")
						break
					i_dex+=msg.padding
					if msg.seperator is not None:
						if index - i_dex == 0:
							byteToWrite = msg.seperator
							break
						i_dex += 1


			romMap[i] = byteToWrite


	return

#In future, may wish to use depth into the game for shop items to determine prices
def WriteItemPricesToMemory(addressData, romMap, itemPrices):
	for item in itemPrices.keys():
		if item.startswith("HC_"):
			continue

		price = itemPrices[item]

		#ItemAttributes.ckir_BEFORE_ItemAttribute_REPEL
		labelReference = "ckir_BEFORE_ItemAttribute_{}".format(item)
		labelInfo = addressData[labelReference]

		bytes = list(struct.pack('<H', price))

		# First two bytes dictate price
		romMap[labelInfo["address_range"]["begin"]] = bytes[0]
		romMap[labelInfo["address_range"]["begin"]+1] = bytes[1]


def WriteHardCodedPricesToMemory(addressData, romMap, itemPrices, locations, priceSettings):
	# Bargain shops are hardcoded price values
	# Vending machines prices are hardcoded AND the string must be updated

	buena = priceSettings["randomise_buena_prices"]
	game_corner = priceSettings["randomise_game_corner_prices"]
	bargain = priceSettings["randomise_bargain_prices"]

	if bargain:
		bargainItems = [ l for l in locations if l.isBargainShop() and l.isItem()]
		for bargain in bargainItems:
			bargainData = "ckir_BEFORE{}0ITEMCODE".format(
				"".join(bargain.Name.split()).upper().replace('.', '_') \
					.replace("'", ""))
			bargainCode = addressData[bargainData]["address_range"]["begin"]

			codedPrice = itemPrices["HC_"+bargain.item+str(bargain)]
			bytes = list(struct.pack('<H', codedPrice))

			romMap[bargainCode+1] = bytes[0]
			romMap[bargainCode+2] = bytes[1]

	if buena:
		buenaItems = [l for l in locations if l.isBuenaItem()]
		for buena in buenaItems:
			bargainData = "ckir_BEFORE{}0ITEMCODE".format(
				"".join(buena.Name.split()).upper().replace('.', '_') \
					.replace("'", ""))
			bargainCode = addressData[bargainData]["address_range"]["begin"]

			codedPrice = itemPrices["HC_" + buena.item + str(buena)]
			bytes = list(struct.pack('<H', codedPrice))

			romMap[bargainCode + 1] = bytes[0]


	vendingLocations = [ l for l in locations if
						 ((l.isVendingMachine()  and bargain) or \
							 ( l.isPrize() and game_corner))
						  and l.isItem()]
	for vend in vendingLocations:
		vendPriceLabel1 = "ckir_BEFORE{}0VENDINGPRICECODE1".format(
			"".join(vend.Name.split()).upper().replace('.', '_') \
			.replace("'", ""))
		vendPriceLabel2 = "ckir_BEFORE{}0VENDINGPRICECODE2".format(
			"".join(vend.Name.split()).upper().replace('.', '_') \
				.replace("'", ""))
		labelInfo1 = addressData[vendPriceLabel1]
		labelInfo2 = addressData[vendPriceLabel2]

		vendingStringLabel = "ckir_BEFORE" + ("".join(vend.Name.split())).upper().replace('.', '_')\
			.replace("'","") + '0VENDINGCODE'

		vendingAddressData = addressData[vendingStringLabel]

		codedPrice = itemPrices["HC_" + vend.item + str(vend)]
		price_string = str(codedPrice)

		#print("Vending price:", vend.Name, vend.item, price_string)

		backwards_iterator = vendingAddressData["address_range"]["end"]-2
		for i in range(0, len(price_string)):
			byteToWrite = ByteToGBCCharacterByte(price_string[len(price_string) - i - 1])
			romMap[backwards_iterator] = byteToWrite
			backwards_iterator -= 1

		extra_byte = 0
		if vend.isVendingMachine():
			romMap[backwards_iterator] = ByteToGBCCharacterByte("¥")
			backwards_iterator -= 1
			extra_byte = 1

		romMap[backwards_iterator] = ByteToGBCCharacterByte(" ")
		backwards_iterator -= 1

		# TODO: Write additional spaces if price string is longer

		vendingString = vend.HardcodedName[vend.HardcodedName.index("\"")+1 : vend.HardcodedName.rindex("\"")]
		priceLength = len(vendingString)-vendingString.rindex(" ")-2 # Skip the space and the @ as newline
		extraSpaces = priceLength - len(price_string) - 1 - extra_byte
		for space in range(0, extraSpaces):
			romMap[backwards_iterator] = ByteToGBCCharacterByte(" ")
			backwards_iterator -= 1

		# Bytes are BIG ENDIAN when stored in these EQU variables...


		#print(labelInfo1["address_range"]["begin"], bytes[0], bytes[1])

		# Price is used in variable checkmoney YOUR_MONEY, GOLDENRODDEPTSTORE6F_FRESH_WATER_PRICE
		byteOffset = 0
		bytes = None
		if vend.isVendingMachine():
			byteOffset = 3
			bytes = list(struct.pack('>H', codedPrice))
		elif vend.isPrize():
			byteOffset = 1
			bytes = list(struct.pack('>H', codedPrice))

		romMap[labelInfo1["address_range"]["begin"] + byteOffset] = bytes[0]
		romMap[labelInfo1["address_range"]["begin"] + byteOffset + 1] = bytes[1]
		romMap[labelInfo2["address_range"]["begin"] + byteOffset] = bytes[0]
		romMap[labelInfo2["address_range"]["begin"] + byteOffset + 1] = bytes[1]
