import os
import Location
import Gym
import yaml
from collections import defaultdict

def readTSVFile(filename):
	file = open(filename)
	data = file.readlines()

	objs = []

	first_line = True
	for line in data:
		if first_line:
			field_names = line.strip().split("\t")
			first_line = False
		else:
			d = line.strip().split("\t")
			obj = {}
			iterator = 0

			for name in field_names:
				if iterator >= len(d):
					obj[name] = ""
				else:
					obj[name] = d[iterator]
				iterator += 1

			objs.append(obj)

	return objs


WARP_OPTION=" Warpie"

def LoadWarpData(locationList, flags):
	warpLocations = []

	# var
	# formattedString = String.format("%s\t(%s)\t->\t%s\t(%s)",
	# 								this.StartFriendlyName, this.StartGroupName,
	# 								this.EndFriendlyName, this.EndGroupName);

#Start Warp Name	Start Warp Group	->	End Warp Name	End Warp Group
	warpOutput = "Warp Data/warp-output.tsv"
	warpTSV = readTSVFile(warpOutput)

	accepted_warps = CheckLocationData(warpTSV, locationList)

	for data in accepted_warps:
		fromGroupName = data["Start Warp Group"][1:-1]
		toGroupName = data["End Warp Group"][1:-1]

		## TODO Unlock default test using only cherrygrove-based warps
		#if fromGroupName != "Cherrygove":
		#	continuemt

		locationData = {
			"Name": toGroupName+WARP_OPTION,
			"FileName": "",
			"Type": "Map",
			"WildTableList": None,
			"LocationReqs": [fromGroupName+WARP_OPTION],
			"FlagReqs": [],
			"FlagsSet": None,
			"ItemReqs": [],
			"Code": "",
			"Text": "",
			"Sublocations": None,
			"HasPKMN": "No",
			"ReachableReqs": None,
			"TrainerList": None
		}


		darkWarpGroups = {"Silver Cave Room 1", "Whirl Island", "Rock Tunnel", "Dark Cave"}



		if len(list(filter(lambda x: x in fromGroupName,darkWarpGroups))) > 0:
			locationData["FlagReqs"].append("Zephyr Badge")
			locationData["ItemReqs"].append("Flash")

			if "Fly Warps" in flags:
				locationData["FlagReqs"].append("Storm Badge")
				locationData["ItemReqs"].append("Fly")


		l = Location.Location(locationData)

		warpLocations.append(l)

	# TODO: Investigate methods to remove inaccessible warp locations
	# Closed loops, etc, and mark as impossible

	return warpLocations


def ImpossibleWarpRecursion(accessible_groups, l):
	dontChange = ["8 Badges", "Rocket Invasion", "All Badges", "Woke Snorlax",
				  "Most Map Access", "Elite Four"]

	for l_s in l.Sublocations:
		ImpossibleWarpRecursion(accessible_groups,l_s)

	if l.WarpReqs is not None and len(l.WarpReqs) > 0 and l.WarpReqs[0] + WARP_OPTION not in accessible_groups and \
			"Impossible" not in l.FlagReqs:
		l.FlagReqs.append("Impossible")
		print("Now impossible:", l.Name)


def isValidWarpDesc(warpData):
	invalidWarps = ["x","X","null","NULL","", "Unused"]

	oneWayWarpInvalidation = ["Drop Point", "Drop Point 2"]

	if warpData["End Warp Name"] in invalidWarps:
		return False

	warpGroup = warpData["End Warp Group"][1:-1]
	if warpGroup in invalidWarps:
		return False

	if warpData["Start Warp Name"] in invalidWarps :
		return False

	warpGroup = warpData["Start Warp Group"][1:-1]
	if warpGroup in invalidWarps:
		return False

	oneWay = list(filter(lambda x: warpData["Start Warp Name"].endswith(x), oneWayWarpInvalidation))
				#or warpData["End Warp Name"].endswith(x), oneWayWarpInvalidation))

	if len(oneWay) > 0:
		return False


	return True


def AddLocation(location, accessible, flattened):
	accessible.append(location)
	otherPossibilities = list(filter(lambda x: x.Type == "Transition" and \
											   location in x.LocationReqs, flattened))
	for o in otherPossibilities:
		if o.Name not in accessible:
			AddLocation(o.Name, accessible, flattened)



def CheckLocationData(warpLocations, locationList):
	# Currently ignores crossover logic
	# This is presently defined in Warp Data/WarpCrossoverData.yml
	# These should be usable as standard locations but not for marking as 'impossible'

	accessible_groups = ["New Bark"+WARP_OPTION,"Cherrygrove"+WARP_OPTION]
	accessible_warp_data = []

	flattened = FlattenLocationTree(locationList)

	while True:
		added_cycle = 0


		for warp in warpLocations:
			if not isValidWarpDesc(warp):
				continue

			start_groupless = warp["Start Warp Group"][1:-1]

			start = start_groupless + WARP_OPTION
			end = warp["End Warp Group"][1:-1] + WARP_OPTION

			if start in accessible_groups:
				#print("Add warp access:",start,end)


				if end not in accessible_groups:
					AddLocation(end, accessible_groups, flattened)
					added_cycle += 1

				if warp not in accessible_warp_data:
					accessible_warp_data.append(warp)
					added_cycle += 1


				# Add logic here to find all transitions from the currently added location



			else:
				otherPossibilities = list(filter(lambda x: \
					x.Name == start, flattened))

# TODO: Exclude any static flag requirements at this stage
# For example, Slowpoke Well transition only working on Spinner WHY
				for op in otherPossibilities:
					for lreq in op.LocationReqs:
						if lreq in accessible_groups:
							if op.Name not in accessible_groups:
								#print("Add warp access2:", start,end)
								AddLocation(start, accessible_groups, flattened)
								AddLocation(end, accessible_groups, flattened)
								added_cycle += 2
							if warp not in accessible_warp_data:
								accessible_warp_data.append(warp)
								added_cycle += 1

				withWarpReqs = list(filter(lambda x: \
													 start_groupless in x.WarpReqs, flattened))

				for w in withWarpReqs:
					name = w.Name
					withExactName = list(filter(lambda x: \
												   x.Name == name, flattened))

					# Exact name still needs to check for warp requirements
					if len(withExactName) > 1:
						nonWarpOption = False
						for wen in withExactName:
							if wen.WarpReqs is None or len(wen.WarpReqs) == 0:
								nonWarpOption = True


							if nonWarpOption and op.Name not in accessible_groups:
								# print("Add warp access2:", start,end)
								AddLocation(start, accessible_groups, flattened)
								AddLocation(end, accessible_groups, flattened)
								added_cycle += 2
							if warp not in accessible_warp_data:
								accessible_warp_data.append(warp)
								added_cycle += 1

						continue

		if added_cycle == 0:
			break

	for l in locationList:
		ImpossibleWarpRecursion(accessible_groups, l)




	return accessible_warp_data










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
						nLoc.applyWarpLogic(flags)
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
						nLoc.applyWarpLogic(flags)
					nLoc.applyBanList(banList,allowList)
					nLoc.applyModifiers(modifierDict)
					LocationList.append(nLoc)
				except Exception as inst:
					print("-----------")
					print("Failure in "+location["Name"])
					raise(inst)

	if "Warps" in flags:
		warpData = LoadWarpData(LocationList, flags)
		for warp in warpData:
			LocationList.append(warp)

	trashList = []
	for i in LocationList:
		trashList.extend(i.getTrashItemList(flags, labelling))
		
	#print('NameCounts')
	#print(LocCountDict)
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
		