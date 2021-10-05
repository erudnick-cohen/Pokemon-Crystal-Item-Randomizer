import shutil
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

def ResetRom():
	try:
		shutil.rmtree("RandomizerRom")
	except:
		print("No existing folder created, nothing to remove")
	shutil.copytree("Game Files/pokecrystal-speedchoice","RandomizerRom")

def ResetRomForLabelling():
	try:
		shutil.rmtree("RandomizerRom")
	except:
		print("No existing folder created, nothing to remove")
	shutil.copytree("Speedchoice Current/pokecrystal-speedchoice","RandomizerRom")
	#next overwrite the files which need custom labels
	for root, dir, files  in os.walk("Files with manual labels/maps"):
		for file in files:
			shutil.copy("Files with manual labels/maps/"+file,"RandomizerRom/maps/"+file)
	for root, dir, files  in os.walk("Files with manual labels/engine"):
		for file in files:
			shutil.copy("Files with manual labels/engine/"+file,"RandomizerRom/engine/"+file)
	shutil.copy("Files with manual labels/blocks/blocks.asm","RandomizerRom/data/maps/blocks.asm")
	shutil.copy("Files with manual labels/pokemon/breeding.asm","RandomizerRom/engine/pokemon/breeding.asm")
	shutil.copy("Files with manual labels/events/magikarp_lengths.asm","RandomizerRom/data/events/magikarp_lengths.asm")

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


def DirectWriteItemLocations(locations,addressData,gameFile, progRod = False):
	codeLookup = Items.makeRawItemCodeDict(progRod)
	yamlfile = open("badgeData.yml",encoding='utf-8')
	yamltext = yamlfile.read()
	gymOffsets = yaml.load(yamltext, Loader=yaml.FullLoader)
	for i in locations:
		if i.isItem():
			if i.IsHidden:
				WriteMachinePartToRomMemory(i,addressData,codeLookup,gameFile)
			elif not i.IsSpecial:
				WriteRegularLocationToRomMemory(i,addressData,codeLookup,gameFile)
			else:
				if i.Name == "Elm Aide Pokeballs":
					WriteAideBallsToRomMemory(i,addressData,codeLookup,gameFile)
				if i.Name == "Dragons Den Dragon Fang":
					#this just happens to work, its in the same byte offset (its also now just a regular location...)
					WriteRegularLocationToRomMemory(i,addressData,codeLookup,gameFile)
				if i.Name == "Hidden Machine Part":
					WriteMachinePartToRomMemory(i,addressData,codeLookup,gameFile)
		elif i.isGym():
			WriteBadgeToRomMemory(i,addressData,gymOffsets,gameFile)

def ApplyGamePatches(gameFile, patches):
	for i in patches:
		for j in range(0,len(i['integer_values']['new'])):
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
def WriteRegularLocationToRomMemory(location,labelData,itemScriptLookup,romMap):
	if(not isinstance(location, Gym.Gym)):
		labelCodeB = "ckir_BEFORE"+("".join(location.TrueName.split())).upper().replace('.','_').replace("'","")+'0ITEMCODE'
		labelCodeB2 = "ckir_BEFORE"+("".join(location.TrueName.split())).upper().replace('.','_').replace("'","")+'0ITEMCODEB'
	else:
		labelCodeB = "ckir_BEFORE"+("".join(location.TrueName.split())).upper().replace('.','_').replace("'","")+'0BADGECODE'
		labelCodeB2 = "ckir_BEFORE"+("".join(location.TrueName.split())).upper().replace('.','_').replace("'","")+'0BADGECODEB'

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
		labelCodeBNPC = "ckir_BEFORE"+("".join(location.TrueName.split())).upper().replace('.','_').replace("'","")+'0NPCCODE'
		labelCodeBNPC2 = "ckir_BEFORE"+("".join(location.TrueName.split())).upper().replace('.','_').replace("'","")+'0NPCCODEB'
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
		labelCodeBNPC = "ckir_BEFORE" + ("".join(location.TrueName.split())).upper().replace('.', '_').replace("'","") + '0NPCCODE'
		labelCodeBNPC2 = "ckir_BEFORE" + ("".join(location.TrueName.split())).upper().replace('.', '_').replace("'","") + '0NPCCODEB'
		addressDataNPC = labelData[labelCodeBNPC]


		# need to extract the nibble out
		# print(list(map(int, addressDataNPC["integer_values"].split(' '))))
		# print(addressDataNPC["integer_values"].split(' '))
		flag_bytes = location.BerryFlag.to_bytes(2, 'little')
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


def WriteAideBallsToRomMemory(location,labelData,itemScriptLookup,romMap):
	labelCodeB = "ckir_BEFORE"+("".join(location.TrueName.split())).upper().replace('.','_').replace("'","")+'0ITEMCODE'
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
		endVal = 5
	elif(itemType == 'Rod'):
		commandVerbose = 177
		nextVal = 0
		endVal = 176
		nItemCode = 176
	if(itemType == 'Item'):
		romMap[addressData["address_range"]["begin"]+6] = nItemCode
		romMap[addressData["address_range"]["begin"]+12] = nItemCode
	else:
		romMap[addressData["address_range"]["begin"]+6] = 168
		romMap[addressData["address_range"]["begin"]+11] = commandVerbose
		romMap[addressData["address_range"]["begin"]+12] = nItemCode
		romMap[addressData["address_range"]["begin"]+13] = endVal

def WriteMachinePartToRomMemory(location,labelData,itemScriptLookup,romMap):
	labelCodeB = "ckir_BEFORE"+("".join(location.TrueName.split())).upper().replace('.','_').replace("'","")+'0ITEMCODE'
	labelCodeBNPC = "ckir_BEFORE"+("".join(location.TrueName.split())).upper().replace('.','_').replace("'","")+'0ITEMCODEB'

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
	
	if not location.OtherName is None:
		labelCodeB = "ckir_BEFORE"+("".join(location.OtherName.split())).upper().replace('.','_').replace("'","")+'0ITEMCODE'
		labelCodeBNPC = "ckir_BEFORE"+("".join(location.OtherName.split())).upper().replace('.','_').replace("'","")+'0ITEMCODEB'

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



def LabelAllLocations(locations):
	#codeLookup = Items.makeItemCodeDict()
	#textLookup = Items.makeItemTextDict()
	for i in locations:
		#TODO, LABELING FOR SPECIAL LOCATIONS
		if i.isItem() or i.Type == 'Dummy':
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
	codeSearch = re.findall(coderegexstr,filecode)[0]
	oldcode = codeSearch[0]
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

#currently only labels "regular" items
def LabelItemLocation(location):
	print("Labelling "+location.Name)
	#open the relevant file and get it as a string
	file = open("RandomizerRom/maps/"+location.FileName)
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
		codeSearch = re.findall(coderegexstr,filecode)[0]
		oldcode = codeSearch[0]
		#print(codeSearch)
	else:
		coderegexstr = re.escape(location.Code.replace("    ","\t")).replace("ITEMLINE",".+")
		oldcode = re.findall(coderegexstr,filecode)[0]

	#if this is an itemball, we need to find out what the command is because we're also going to need to find the line that actually
	if location.IsBall or location.IsBerry:
		#find the code on the line BEFORE the one we need to modify
		#fortunately, we have these lines already labeled, we need them to label something else
		commandregexstr = "(\w+):"
		commandSearch = re.findall(commandregexstr,location.Code)[0]
		npcRegex = ("[^\n]+")+commandSearch+",[^\n]+\n"
		npcSearch = re.findall(npcRegex,filecode)[0]
	labelCodeB = ".ckir_BEFORE"+("".join(location.Name.split())).upper().replace('.','_').replace("'","")+'0ITEMCODE::\n'
	labelCodeA = "\n.ckir_AFTER"+("".join(location.Name.split())).upper().replace('.','_').replace("'","")+'0ITEMCODE::\n'
	labelCodeBNPC = ".ckir_BEFORE"+("".join(location.Name.split())).upper().replace('.','_').replace("'","")+'0NPCCODE::\n'
	labelCodeANPC = ".ckir_AFTER"+("".join(location.Name.split())).upper().replace('.','_').replace("'","")+'0NPCCODE::\n'
	newCode = ""
	if not location.IsSpecial:
		newcode = oldcode.replace(codeSearch[1],labelCodeB+codeSearch[1]+labelCodeA)
		#switch spaces to tabs.....
		newcode = newcode.replace("    ","\t")
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
	#write the new file into the files for the randomizer rom
	newfilestream = open("RandomizerRom/maps/"+location.FileName,'w')
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
		file = open("RandomizerRom/maps/"+location.SecondaryFile)
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
			codeSearch = re.findall(coderegexstr,filecode)[0]
			oldcode = codeSearch[0]
			#print(codeSearch)
		else:
			coderegexstr = re.escape(location.SecondaryCode.replace("    ","\t")).replace("ITEMLINE",".+")
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
		newfilestream = open("RandomizerRom/maps/"+location.SecondaryFile,'w')
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