import os
import Location
import Gym
import yaml
from collections import defaultdict

def LoadDataFromFolder(path, banList = None, allowList = None, modifierDict = {}, flags = [], labelling = False):
	LocationList = []
	LocCountDict = defaultdict(lambda: 0)
	print("Creating Locations")
	for root, dir, files  in os.walk(path+"//Map Data"):
		for file in files:
			print("File: "+file)
			entry = open(path+"//Map Data//"+file,'r',encoding='utf-8')
			try:
				yamlData = yaml.load(entry, Loader=yaml.FullLoader)
			except Exception as inst:
				raise(inst)
			print("Locations in file are:")
			for location in yamlData["Location"]:
				print(location["Name"])
				try:
					nLoc =Location.Location(location)
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
			print("File: "+gfile)
			entry = open(path+"//Gym Data//"+gfile,'r',encoding='utf-8')
			yamlData = yaml.load(entry,Loader=yaml.FullLoader)

			print("Locations in file are:")
			for location in yamlData["Location"]:
				print(location["Name"])
				try:
					nLoc = Gym.Gym(location)
					nLoc.applyBanList(banList,allowList)
					nLoc.applyModifiers(modifierDict)
					LocationList.append(nLoc)
				except Exception as inst:
					print("-----------")
					print("Failure in "+location["Name"])
					raise(inst)

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
			print('Flattened :'+i.Name)
			for j in i.Sublocations:
				aList.append(j)
				done = False
		locations = aList
	return nList
		