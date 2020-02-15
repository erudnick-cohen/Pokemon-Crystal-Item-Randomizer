import shutil
import Items
import re
import os
import time
import yaml
import json
import copy
import mmap

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
	shutil.copytree("VanillaSpeedCrystal/pokecrystal-speedchoice","RandomizerRom")

def WriteWildLevelsToMemory(locationDict, distDict,addressData):
	f = open('crystal-speedchoice-v6.0.gbc','r+b')
	romMap = mmap.mmap(f.fileno(),0)
	surfDist = max(distDict['Surf'],distDict['Fog Badge'])
	#loop through locations
	for i in distDict:
		if i in locationDict:
			location = locationDict[i]
			if location.WildTableList is not None:
				for j in location.WildTableList:
					print('Writing '+j+" at "+location.Name)
					idTextB = "\nckir_BEFORE"+"".join(j.upper().replace("_","").split())+"0WILDGRASS"
					minLV = float('inf')
					#this is a hack to account for the fact that the larvitar in mt. silver are WAAAAYYYY to low level
					LVthresh = 0
					if "SILVERCAVEROOM" in location.Name:
						LVthresh = 40
					for k in range(5,len(addressData[idTextB]['integer_values']),2):
						minLV = min(addressData[idTextB]['integer_values'][k],max(minLV,LVthresh))
					for k in range(5,len(addressData[idTextB]['integer_values']),2):
						cLV = addressData[idTextB]['integer_values'][k]
						nLV = max(cLV-minLV+distDict[i], 2)
						romMap[addressData[idTextB]['address_range']['begin']+k] = nLV
	#loop through locations
	for i in distDict:
		if i in locationDict:
			location = locationDict[i]
			if location.WildTableList is not None:
				for j in location.WildTableList:
					print('Writing '+j+" at "+location.Name)
					idTextB = "\nckir_BEFORE"+"".join(j.upper().replace("_","").split())+"0WILDWATER"
					minLV = float('inf')
					for k in range(3,len(addressData[idTextB]['integer_values']),2):
						minLV = min(addressData[idTextB]['integer_values'][k],minLV)
					for k in range(3,len(addressData[idTextB]['integer_values']),2):
						cLV = addressData[idTextB]['integer_values'][k]
						nLV = max(cLV-minLV+max(surfDist,distDict[i]), 2)
						romMap[addressData[idTextB]['address_range']['begin']+k] = nLV
	#loop through locations
	#load up the swarm data
	yamlfile = open("Wild Data/swarmGrass.yaml")
	yamltext = yamlfile.read()
	wildData = yaml.load(yamltext)
	for i in distDict:
		if i in locationDict:
			location = locationDict[i]
			if location.WildTableList is not None:
				for j in location.WildTableList:
					print('Writing '+j+" at "+location.Name)
					idTextB = "\nckir_BEFORE"+"".join(j.upper().replace("_","").split())+"0WILDSWARM"
					minLV = float('inf')
					for k in range(5,len(addressData[idTextB]['integer_values']),2):
						minLV = min(addressData[idTextB]['integer_values'][k],minLV)
					for k in range(5,len(addressData[idTextB]['integer_values']),2):
						cLV = addressData[idTextB]['integer_values'][k]
						nLV = max(cLV-minLV+distDict[i], 2)
						romMap[addressData[idTextB]['address_range']['begin']+k] = nLV

def DirectWriteItemLocations(locations):
	codeLookup = Items.makeRawItemCodeDict()
	yamlfile = open("crystal-speedchoice-label-details.json")
	yamltext = yamlfile.read()
	addressLists = json.loads(yamltext)
	addressData = {}
	for i in addressLists:
		addressData[i['label'].split(".")[-1]] = i
	print(addressData)
	
	yamlfile = open("badgeData.yml")
	yamltext = yamlfile.read()
	gymOffsets = yaml.load(yamltext)
	f = open('crystal-speedchoice-v6.0.gbc','r+b')
	gameFile = mmap.mmap(f.fileno(),0)
	for i in locations:
		if i.isItem():
			if not i.IsSpecial:
				WriteRegularLocationToRomMemory(i,addressData,codeLookup,gameFile)
			else:
				if i.Name == "Elm Aide Pokeballs":
					WriteAideBallsToRomMemory(i,addressData,codeLookup,gameFile)
				if i.Name == "Dragons Den Dragon Fang":
					#this just happens to work, its in the same byte offset
					WriteRegularLocationToRomMemory(i,addressData,codeLookup,gameFile)
				if i.Name == "Hidden Machine Part":
					WriteMachinePartToRomMemory(i,addressData,codeLookup,gameFile)
		elif i.isGym():
			WriteBadgeToRomMemory(i,addressData,gymOffsets,gameFile)

def ApplyGamePatches():
	f = open('crystal-speedchoice-v6.0.gbc','r+b')
	gameFile = mmap.mmap(f.fileno(),0)
	yamlfile = open("item-randomizer-patches-diff-speedchoice.json")
	yamltext = yamlfile.read()
	patches = json.loads(yamltext)
	for i in patches:
		for j in range(0,len(i['integer_values']['new'])):
			gameFile[i['address_range']['begin']+j] = i['integer_values']['new'][j]

def WriteBadgeToRomMemory(location,labelData,gymOffsets,romMap):
	labelCodeB = "ckir_BEFORE"+("".join(location.Name.split())).upper().replace('.','_').replace("'","")+'0BADGECODE'
	print('Writing '+labelCodeB)
	addressData = labelData[labelCodeB]
	romMap[addressData["address_range"]["begin"]+1] = location.badge.Code
	#borrowing this trick from goldenrules's key item randomizer
	nString = "It's\n"+location.badge.Name.upper()
	for i in range(0,len(nString)):
		#+1 to dodge the initial byte that isn't part of the text
		#note that this leaves the remaining text as "garbage", since we are terminating the string ourselves
		print(nString[i])
		nByte = str.encode(nString[i],'ascii')
		nByte = int.from_bytes(nByte,'big')-65+128
		if nString[i] == '\n':
			nByte = 79
		if nString[i] == "'":
			nByte = 224
		if nString[i] == " ":
			nByte = 127
		print(romMap[gymOffsets[location.Name]+i+1])
		print('to')
		print(nByte)
		romMap[gymOffsets[location.Name]+i+1] = nByte
		print('---')
	#add the done character to the end
	romMap[gymOffsets[location.Name]+len(nString)+1] = 87
	#then terminate the string
	romMap[gymOffsets[location.Name]+len(nString)+2] = 50
#STILL NEED TO WRITE THE REST OF THESE
def WriteRegularLocationToRomMemory(location,labelData,itemScriptLookup,romMap):
	labelCodeB = "ckir_BEFORE"+("".join(location.Name.split())).upper().replace('.','_').replace("'","")+'0ITEMCODE'
	print('Writing '+labelCodeB)
	addressData = labelData[labelCodeB]
	nItemCode = itemScriptLookup(location.item)
	if location.IsBall:
		romMap[addressData["address_range"]["begin"]] = nItemCode
	else:
		romMap[addressData["address_range"]["begin"]+1] = nItemCode
		
def WriteAideBallsToRomMemory(location,labelData,itemScriptLookup,romMap):
	labelCodeB = "ckir_BEFORE"+("".join(location.Name.split())).upper().replace('.','_').replace("'","")+'0ITEMCODE'
	print('Writing'+labelCodeB)
	addressData = labelData[labelCodeB]
	nItemCode = itemScriptLookup(location.item)
	romMap[addressData["address_range"]["begin"]+6] = nItemCode
	romMap[addressData["address_range"]["begin"]+12] = nItemCode

def WriteMachinePartToRomMemory(location,labelData,itemScriptLookup,romMap):
	labelCodeB = "ckir_BEFORE"+("".join(location.Name.split())).upper().replace('.','_').replace("'","")+'0ITEMCODE'
	print('Writing'+labelCodeB)
	addressData = labelData[labelCodeB]
	nItemCode = itemScriptLookup(location.item)
	romMap[addressData["address_range"]["begin"]+2] = nItemCode


def LabelAllLocations(locations):
	#codeLookup = Items.makeItemCodeDict()
	#textLookup = Items.makeItemTextDict()
	for i in locations:
		#TODO, LABELING FOR SPECIAL LOCATIONS
		if i.isItem():
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
	print(codeSearch)
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
	wildData = yaml.load(yamltext)
	for j in wildData:
		print('Writing '+j)
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
	wildData = yaml.load(yamltext)
	for j in wildData:
		print('Writing '+j)
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
	wildData = yaml.load(yamltext)
	for j in wildData:
		print('Writing '+j)
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
	print("Editing Special Pokemon")
	for root, dir, files  in os.walk("Special Pokemon Locations"):
		for file in files:
			print("File: "+file)
			entry = open("Special Pokemon Locations/"+file,'r')
			yamlData = yaml.load(entry)
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
				print(coderegexstr)
				codeSearch = re.findall(coderegexstr,filecode)[0]
				oldcode = codeSearch[0]
				newcode = oldcode.replace(codeSearch[1],idTextB+codeSearch[1]+idTextA)
				print(newcode)
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
		print('Labeling '+j)
		nCode = trainer['Code']
		idText = "."+"".join(j.upper().split())+"0TRAINER::\n\t"
		for k in range(0,len(trainer['Pokemon'])):
			print('Labeling mon '+str(k))
			pCode = trainer['Pokemon'][k]['Code']
			idTextPB = ".ckir_BEFORE"+"".join(j.upper().split())+"0TRAINER0MON"+str(k)+"::\n"
			idTextPA = "\n.ckir_AFTER"+"".join(j.upper().split())+"0TRAINER0MON"+str(k)+"::\n"

			nCode = nCode.replace("\t"+pCode,idTextPB+pCode+idTextPA,1)
		newfile = newfile.replace("\t"+trainer['Code'],idText+nCode,1)
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
	print(repr(re.escape(location.Code.replace("    ","\t"))))
	print(repr(location.Code.replace("    ","\t")))
	print(repr("\tITEMLINE"))
	print(repr("\tITEMLINE") in (repr(location.Code.replace("    ","\t"))))
	print("\tITEMLINE" in (location.Code.replace("    ","\t")))
	print(coderegexstr)
	codeSearch = None
	if not location.IsSpecial:
		codeSearch = re.findall(coderegexstr,filecode)[0]
		oldcode = codeSearch[0]
		print(codeSearch)
	else:
		coderegexstr = re.escape(location.Code.replace("    ","\t")).replace("ITEMLINE",".+")
		oldcode = re.findall(coderegexstr,filecode)[0]
	labelCodeB = ".ckir_BEFORE"+("".join(location.Name.split())).upper().replace('.','_').replace("'","")+'0ITEMCODE::\n'
	labelCodeA = "\n.ckir_AFTER"+("".join(location.Name.split())).upper().replace('.','_').replace("'","")+'0ITEMCODE::\n'
	newCode = ""
	if not location.IsSpecial:
		newcode = oldcode.replace(codeSearch[1],labelCodeB+codeSearch[1]+labelCodeA)
		#switch spaces to tabs.....
		newcode = newcode.replace("    ","\t")
	newtext = ""
	#TODO: Need to completely change how text works, we now need to actually track each string individually, no spanning across commands
	#For now, just not labeling text
	# if location.Text is not None: 
	# 	#construct a new script that updates text about the new item
	# 	newtext = ("".join(location.Name.split())).upper()+'0TEXT::\n'
	# 	#switch spaces to tabs.....
	# 	newtext = newtext.replace("    ","\t")
		
	# 	#find the text we need to replace
	# 	textregexstr = re.escape(location.Text.replace("    ","\t")).replace("ITEMNAME",".+")
	# 	oldtext = re.findall(textregexstr,filecode)[0]
	# else:
	# 	oldtext = ""
	
	#make new file with the new text (except no new text right now)
	#newfile = filecode.replace(oldcode,newcode+oldcode).replace(oldtext,newtext)
	if not location.IsSpecial:
		newfile = filecode.replace(oldcode,newcode)
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

def WriteLocationToRom(location, itemScriptLookup, itemTextLookup):
	print("Writing "+location.Name+" which contains "+location.item)
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
	print("Writing "+location.Name+" which contains "+location.badge.Name)
	
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
					print('Writing '+j+" at "+location.Name)
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
	wildData = yaml.load(yamltext)
	for i in distDict:
		if i in locationDict:
			location = locationDict[i]
			if location.WildTableList is not None:
				for j in location.WildTableList:
					print('Writing '+j+" at "+location.Name)
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
						print(areaData["Code"] in areaData["File"])
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
	wildData = yaml.load(yamltext)
	for i in distDict:
		if i in locationDict:
			location = locationDict[i]
			if location.WildTableList is not None:
				for j in location.WildTableList:
					print('Writing '+j+" at "+location.Name)
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
	wildData = yaml.load(yamltext)
	for i in distDict:
		if i in locationDict:
			location = locationDict[i]
			if location.WildTableList is not None:
				for j in location.WildTableList:
					if j.upper() in wildData:
						print('Writing '+j+" at "+location.Name)
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
	print("Editing Special Pokemon")
	for root, dir, files  in os.walk("Special Pokemon Locations"):
		for file in files:
			print("File: "+file)
			entry = open("Special Pokemon Locations/"+file,'r')
			yamlData = yaml.load(entry)
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