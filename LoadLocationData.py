import json
import os

import GenerateWarpData
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

	# TODO add to this function to deal with warp requirement chaining
	# Then pruning is done before the object creation below
	accepted_warps, removed_items = CheckLocationData(warpTSV, locationList)

	special_cases = GenerateWarpData.LoadSpecialCaseWarps()

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
			"FlagsSet": [],
			"ItemReqs": [],
			"Code": "",
			"Text": "",
			"Sublocations": None,
			"HasPKMN": "No",
			"ReachableReqs": None,
			"TrainerList": None
		}

		GenerateWarpData.handleSpecialCases(data, locationData, special_cases)


		darkWarpGroups = {"Silver Cave Room 1", "Whirl Island", "Rock Tunnel", "Dark Cave"}

		# For warps loaded in, modifiers must use Warpie in their description
		# For transitions, either/or is valid technically!



		if "No Flash" not in flags and\
				len(list(filter(lambda x: x in fromGroupName or x in toGroupName,darkWarpGroups))) > 0:
			locationData["FlagReqs"].append("Zephyr Badge")
			locationData["ItemReqs"].append("Flash")


			if "Fly Warps" in flags and "Delete Fly" not in flags:
				if "Storm Badge" not in locationData["FlagReqs"]:
					locationData["FlagReqs"].append("Storm Badge")
				if "Fly" not in locationData["ItemReqs"]:
					locationData["ItemReqs"].append("Fly")




		l = Location.Location(locationData)

		warpLocations.append(l)

	# TODO: Investigate methods to remove inaccessible warp locations
	# Closed loops, etc, and mark as impossible

	return warpLocations, removed_items


def ImpossibleWarpRecursion(accessible_groups, fullLocations, l, force=False):
	flags = []
	impossible = []
	dontChange = ["8 Badges", "Rocket Invasion", "All Badges", "Woke Snorlax",
				  "Most Map Access", "Elite Four"]

	for l_s in l.Sublocations:
		new_flags, new_impossible = ImpossibleWarpRecursion(accessible_groups, fullLocations, l_s,force)
		for flag in new_flags:
			flags.append(flag)
		for imp in new_impossible:
			if imp not in impossible:
				impossible.append(imp)

	if force or (l.WarpReqs is not None and len(l.WarpReqs) > 0 and l.WarpReqs[0] + WARP_OPTION not in accessible_groups and \
			"Unreachable" not in l.FlagReqs):
		l.FlagReqs.append("Unreachable")
		for flag in l.FlagsSet:
			flags.append(flag)
		print("Now Unreachable:", l.Name)
		if l.IsItem or (type(l) == Gym.Gym):
			impossible.append(l)

		# This risks infinite recursion due to things with the same name
		# As this is mostly a check for Gym objects
		# Some strange factors with badges cause issues, so if name is badge, don't recurse
		# TODO: Fix recursion issues with boat here due to inaccessibility loop!
		if not type(l) == Gym.Gym and "Port" not in l.Name and "Route 18" not in l.Name:
			forcedLocations = list(filter(lambda x: l.Name in x.LocationReqs, fullLocations))
			for location in forcedLocations:
				new_impossible = ImpossibleWarpRecursion(accessible_groups, fullLocations, location, force=True)
				for n_imp in new_impossible:
					if n_imp not in impossible:
						impossible.append(n_imp)


		for l_s in l.Sublocations:
			new_flags, new_impossible = ImpossibleWarpRecursion(accessible_groups, fullLocations, l_s, force=True)
			for flag in new_flags:
				if flag not in flags:
					flags.append(flag)
			for imp in new_impossible:
				if imp not in impossible:
					impossible.append(imp)

	return flags, impossible


def isValidWarpDesc(warpData):
	invalidWarps = ["x","X","null","NULL","", "Unused", "Pokemon Center Upstairs"]

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


def AddLocation(location, accessible, flattened, forbiddenFlags=None):
	if forbiddenFlags is None:
		forbiddenFlags = []
	accessible.append(location)
	otherPossibilities = list(filter(lambda x: x.Type == "Transition" and \
											   location in x.LocationReqs, flattened))
	for o in otherPossibilities:
		if HasForbiddenFlag(o, forbiddenFlags):
			continue

		if o.Name not in accessible:
			AddLocation(o.Name, accessible, flattened, forbiddenFlags)

def HasForbiddenFlag(location, forbiddenFlags):
	hasForbiddenFlag = False
	for f in forbiddenFlags:
		if f in location.FlagReqs:
			hasForbiddenFlag = True
			break

	return hasForbiddenFlag

def CycleWarps(warpLocations, flattened, forbiddenFlags=["Impossible"]):
	accessible_groups = ["New Bark" + WARP_OPTION, "Cherrygrove" + WARP_OPTION]
	accessible_warp_data = []

	while True:
		added_cycle = 0

		for warp in warpLocations:
			if not isValidWarpDesc(warp):
				continue

			start_groupless = warp["Start Warp Group"][1:-1]

			start = start_groupless + WARP_OPTION
			end = warp["End Warp Group"][1:-1] + WARP_OPTION

			if start in accessible_groups:
				# print("Add warp access:",start,end)

				if end not in accessible_groups:
					AddLocation(end, accessible_groups, flattened, forbiddenFlags)
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

					if HasForbiddenFlag(op, forbiddenFlags):
						continue

					for lreq in op.LocationReqs:
						if lreq in accessible_groups:
							if op.Name not in accessible_groups:
								# print("Add warp access2:", start,end)
								AddLocation(start, accessible_groups, flattened, forbiddenFlags)
								AddLocation(end, accessible_groups, flattened, forbiddenFlags)
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
									AddLocation(start, accessible_groups, flattened, forbiddenFlags)
									AddLocation(end, accessible_groups, flattened, forbiddenFlags)
									added_cycle += 2
								if warp not in accessible_warp_data:
									accessible_warp_data.append(warp)
									added_cycle += 1

							continue

		if added_cycle == 0:
			break

	return accessible_groups, accessible_warp_data

# May cause issues with transitions!
def purgeWarpBidirectional(warpLocations, locationList):
	# Load data to get transitions
	transitions = list(filter(lambda x: x.Type == "Transition", locationList))

	dupeSet = []
	warpsRemoved = []
	returnRemoved = []
	reverseSkip = []
	newWarp = True
	while newWarp:
		usages = {}
		newWarp = False
		warpBySourceAndDestination = {}
		# Count the warps leading OUT of each warp element

		for warpLocation in warpLocations:

			# If warp already removed, treat all other warps as if it doesn't exist
			if warpLocation in warpsRemoved:
				continue

			if warpLocation in returnRemoved:
				continue

			if warpLocation["Start Warp Group"] == warpLocation["End Warp Group"]:
				warpsRemoved.append(warpLocation)
				continue

			warp_key = warpLocation["Start Warp Group"]
			warp_end = warpLocation["End Warp Group"]
			if warp_key not in usages:
				usages[warp_key] = []

			if (warp_key,warp_end) not in warpBySourceAndDestination:
				warpBySourceAndDestination[(warp_key,warp_end)] = []

			usages[warp_key].append(warpLocation)
			warpBySourceAndDestination[(warp_key,warp_end)].append(warpLocation)

		# In theory, would we want to also remove transitions in the other direction to,
		# for the same reason?

		# Check for any warp reqs which have other location requirements
		# Currently the warp transition purging will fail on one-way transitions
		# As deems only one way to get there
		# For sensible transitions of this type, ensure an impossible route back
		# So this code does not purge, but also if a feature change is added later
		for warpTransition in transitions:
			transitionTo = warpTransition.Name
			transitionFrom = "("+warpTransition.LocationReqs[0]+")"

			# Since loading from normal loc list, remove the warp option
			warp_key = transitionFrom.replace(WARP_OPTION, "")

			if warp_key not in usages:
				usages[warp_key] = []

			usages[warp_key].append(warpTransition)


		duplicateRouting = list(filter(lambda x: len(x[1]) > 1, warpBySourceAndDestination.items()))

		if len(duplicateRouting) > 0:
			newWarp = True
			for dup in duplicateRouting:
				dup_count = len(dup[1])
				for i in range(1, dup_count):
					remove_dup = dup[1][i]
					warpsRemoved.append(remove_dup)
					dupeSet.append(remove_dup)

		else:
			singulars = list(filter(lambda x: len(x[1]) == 1, usages.items()))


			# TODO Work out what this code is doing?
			# This may just be looking at what is IN the list potentially about to remove
			inSingular = []
			for s in singulars:
				warpRemoveList = s[1]
				for w in warpRemoveList:
					inSingular.append(w)

			for s in singulars:
				warpRemoveList = s[1]
				for w in warpRemoveList:

					if isinstance(w, Location.Location):
						continue

					end_group = w["End Warp Group"]

					has_return = list(filter(lambda x: x["Start Warp Group"] == end_group and
								x["End Warp Group"] == s[0]

								and x not in warpsRemoved and x not in returnRemoved
								and x not in reverseSkip

								,warpLocations))

					# TODO Work out what is code is doing
					ignore_count = 0
					ignore_this_one = False
					for hr in has_return:
						if hr in inSingular:
							ignore_count += 1
							reverseSkip.append(hr)

					for warpTransition in transitions:
						transitionTo = "("+warpTransition.Name+")"
						# Since loading from normal loc list, remove the warp option
						warp_key = transitionTo.replace(WARP_OPTION, "")

						if w["Start Warp Group"] == warp_key:
							ignore_count += 1
							ignore_this_one = True

					if (len(has_return) - ignore_count) > 0:
						newWarp = True
						warpsRemoved.append(w)

					if not ignore_this_one:
						for w in has_return:
							returnRemoved.append(w)


	return warpsRemoved







def CheckLocationData(warpLocations, locationList):
	# Currently ignores crossover logic
	# This is presently defined in Warp Data/WarpCrossoverData.yml
	# These should be usable as standard locations but not for marking as 'impossible'

	flattened = FlattenLocationTree(locationList)
	accessible_groups, accessible_warp_data = CycleWarps(warpLocations, flattened)

	probably_impossible_flags = []
	actually_impossible_flags = []

	removed_warps = []

	for l in locationList:
		new_i_flags, r_warps = ImpossibleWarpRecursion(accessible_groups, locationList, l)
		for r_warp in r_warps:
			if r_warp not in removed_warps:
				removed_warps.append(r_warp)
		for i in new_i_flags:
			probably_impossible_flags.append(i)

	impossible_flags = False
	for flag in probably_impossible_flags:
		flagIsSet = list(filter(lambda x: flag in x.FlagsSet, locationList))
		flagIsSetImpossible = list(filter(lambda x: "Unreachable" in x.FlagReqs, flagIsSet))
		if len(flagIsSet) == len(flagIsSetImpossible):
			actually_impossible_flags.append(flag)
			impossible_flags = True


	if impossible_flags:
		accessible_groups, accessible_warp_data = CycleWarps(warpLocations, flattened,
															 forbiddenFlags=actually_impossible_flags)
	# if flags impossible, repeat
		for l in locationList:
			ignore, r_warps = ImpossibleWarpRecursion(accessible_groups, locationList,  l)
			for r_warp in r_warps:
				if r_warp not in removed_warps:
					removed_warps.append(r_warp)

	# TODO
	# This is still incomplete so disabled
	# Fixing and enabling this will speed up processing
	# As dead-end paths won't happen as often when processing them
	# However, at present it over-purges

	usePurge = True


	# For warp grouping purposes, have an additional check not to purge if the ONLY group that leads to that location
	# Should ALL be transitional options anyway

	if usePurge:
		toPurge = purgeWarpBidirectional(accessible_warp_data.copy(), flattened)
		print("Purge count==",len(toPurge))
		skip_purge = []
		for purge in toPurge:
			end_group = purge["End Warp Group"]
			other_end_group = len([ a for a in accessible_warp_data if a["End Warp Group"] == end_group])
			# Because the warps focus on START locations, double check the end groups here and ensure
			# Not to remove the last option from the list
			# For warp group processing, etc.
			if other_end_group <= 1:
				skip_purge.append(purge)
			else:
				accessible_warp_data.remove(purge)

	return accessible_warp_data,removed_warps










def LoadDataFromFolder(path, banList = None, allowList = None, modifierDict = {}, flags = [], labelling = False,
					   loadWarpData = True):
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
					nLoc.YmlFile = file
					nLoc.applyBanList(banList,allowList)
					nLoc.applyModifiers(modifierDict, flags)
					nLoc.applyBanList(banList,allowList)

					if "Warps" in flags:
						nLoc.applyWarpLogic(flags)
						#warpModifications = list(filter(lambda x: "Warpie" in x.Name, modifierDict))
						nLoc.applyModifiers(modifierDict, flags)


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
					nLoc.applyModifiers(modifierDict, flags)
					LocationList.append(nLoc)
				except Exception as inst:
					print("-----------")
					print("Failure in "+location["Name"])
					raise(inst)

	warp_removed_items = []
	if "Warps" in flags and loadWarpData:
		warpData, warp_removed_items = LoadWarpData(LocationList, flags)
		for warp in warpData:
			warp.applyModifiers(modifierDict, flags)
			warp.applyWarpLogic(flags)
			LocationList.append(warp)

	trashList = []
	for i in LocationList:
		trashList.extend(i.getTrashItemList(flags, labelling))
		
	#print('NameCounts')
	#print(LocCountDict)
	return (LocationList,trashList,warp_removed_items)
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
				j.SuperLocation = i.Name
				aList.append(j)
				done = False
		locations = aList
	return nList
		