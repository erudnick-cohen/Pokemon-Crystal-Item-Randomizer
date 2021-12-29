import os
import Location
import Gym
import yaml
from collections import defaultdict

def LoadWarpData():
	warpLocations = []

	# var
	# formattedString = String.format("%s\t(%s)\t->\t%s\t(%s)",
	# 								this.StartFriendlyName, this.StartGroupName,
	# 								this.EndFriendlyName, this.EndGroupName);

	warpOutput = "warp-output.tsv"
	tsvFile = open(warpOutput)
	for line in tsvFile:
		data = line.strip().split("\t")
		fromGroupName = data[1][1:-1]
		toGroupName = data[4][1:-1]

		## TODO Unlock default test using only cherrygrove-based warps
		if fromGroupName != "Cherrygove":
			continue

		locationData = {
			"Name": toGroupName+" Warpie",
			"FileName": "",
			"Type": "Map",
			"WildTableList": None,
			"LocationReqs": [fromGroupName+" Warpie"],
			"FlagReqs": None,
			"FlagsSet": None,
			"ItemReqs": None,
			"Code": "",
			"Text": "",
			"Sublocations": None,
			"HasPKMN": "No",
			"ReachableReqs": None,
			"TrainerList": None
		}

		l = Location.Location(locationData)

		warpLocations.append(l)

	# TODO: Investigate methods to remove inaccessible warp locations
	# Closed loops, etc, and mark as impossible

	return warpLocations


def LoadDataFromFolder(path, banList = None, allowList = None, modifierDict = {}, flags = [], labelling = False):
	LocationList = []
	LocCountDict = defaultdict(lambda: 0)
	print("Creating Locations")
	for root, dir, files  in os.walk(path+"//Map Data"):
		for file in files:
			#print("File: "+file)
			entry = open(path+"//Map Data//"+file,'r',encoding='utf-8')
			try:
				yamlData = yaml.load(entry, Loader=yaml.FullLoader)
			except Exception as inst:
				raise(inst)
			#print("Locations in file are:")
			for location in yamlData["Location"]:
				#print(location["Name"])
				try:
					nLoc = Location.Location(location)
					if "Warps" in flags:
						nLoc.applyWarpLogic()
					nLoc.applyBanList(banList,allowList)
					nLoc.applyModifiers(modifierDict)
					LocationList.append(nLoc)
					LocCountDict[nLoc.Name] = LocCountDict[nLoc.Name]+1
				except Exception as inst:
					print("-----------")
					print("Failure in "+location["Name"])
					raise(inst)
	print("Creating Gyms")
	for groot, gdir, gfiles  in os.walk("Gym Data"):
		for gfile in gfiles:
			#print("File: "+gfile)
			entry = open(path+"//Gym Data//"+gfile,'r',encoding='utf-8')
			yamlData = yaml.load(entry,Loader=yaml.FullLoader)

			#print("Locations in file are:")
			for location in yamlData["Location"]:
				#print(location["Name"])
				try:
					nLoc = Gym.Gym(location)
					if "Warps" in flags:
						nLoc.applyWarpLogic()
					nLoc.applyBanList(banList,allowList)
					nLoc.applyModifiers(modifierDict)
					LocationList.append(nLoc)
				except Exception as inst:
					print("-----------")
					print("Failure in "+location["Name"])
					raise(inst)

	if "Warps" in flags:
		warpData = LoadWarpData()
		for warp in warpData:
			LocationList.append(warp)

	trashList = []
	for i in LocationList:
		trashList.extend(i.getTrashItemList(flags, labelling))
		
	print('NameCounts')
	print(LocCountDict)
	return (LocationList,trashList)
	
def FlattenLocationTree(locations):
	nList = []
	aList = []
	done = False
	while not done:
		done = True
		aList = []
		for i in locations:
			nList.append(i)
			#print('Flattened :'+i.Name)
			for j in i.Sublocations:
				aList.append(j)
				done = False
		locations = aList
	return nList
		