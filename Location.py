import LoadLocationData


class Tag:
	def __init__(self, treeItem=None, name=None):
		if treeItem is not None:
			self.Name = treeItem["Name"]
			if "SubTags" in treeItem:
				self.SubTags = treeItem["SubTags"]
			if self.SubTags is None:
				self.SubTags = []
		elif name is not None:
			self.Name = name
			self.SubTags = []


class Location:
	def __init__(self, yamlTree):
		#print("Creating Location "+yamlTree["Name"])
		self.Name = yamlTree["Name"]
		if "TrueName" in yamlTree:
			self.TrueName = yamlTree["TrueName"]
		else:
			self.TrueName = self.Name
		if "OtherName" in yamlTree:
			self.OtherName = yamlTree["OtherName"]
		else:
			self.OtherName = None
		self.FileName = yamlTree["FileName"]
		self.IsItem = yamlTree["Type"]=="Item"
		self.WasItem = False
		self.Type = yamlTree["Type"]
		self.item = None
		self.Handles = []
		self.SuperLocation = None
		self.YmlFile = None
		self.Dummy = yamlTree["Dummy"] if "Dummy" in yamlTree else False
		if self.Dummy:
			assert(self.TrueName != self.Name)

		if self.Type == "Shop":
			self.IsItem = True
			self.IsShop = True
			self.IsBargainShop = False
			self.IsVendingMachine = False
			self.IsPrize = False
			self.IsBuenaItem = False
		elif self.Type == "BargainShop":
			self.IsItem = True
			self.IsShop = True
			self.IsBargainShop = True
			self.IsVendingMachine = False
			self.IsPrize = False
			self.IsBuenaItem = False
		elif self.Type == "Buena":
			self.IsItem = True
			self.IsShop = True
			self.IsBargainShop = False
			self.IsVendingMachine = False
			self.IsPrize = False
			self.IsBuenaItem = True
		elif self.Type == "Vending Machine":
			self.IsItem = True
			self.IsShop = False
			self.IsBargainShop = False
			self.IsVendingMachine = True
			self.IsPrize = False
			self.IsBuenaItem = False
		elif self.Type == "Prize":
			self.IsItem = True
			self.IsShop = False
			self.IsBargainShop = False
			self.IsVendingMachine = False
			self.IsPrize = True
			self.IsBuenaItem = False
		else:
			self.IsShop = False
			self.IsBargainShop = False
			self.IsVendingMachine = False
			self.IsPrize = False
			self.IsBuenaItem = False


		if ( self.Type == "Vending Machine" or self.Type == "Prize") and "HardcodedName" in yamlTree:
			self.HardcodedName = yamlTree["HardcodedName"]
		else:
			self.HardcodedName = None

		#this is not in all the areas because I'm an idiot for not thinking of including it from the startswith
		#thus there is an if statement to handle all the things that don't have this
		if("NormalItem" in yamlTree):
			self.NormalItem = yamlTree["NormalItem"]
		else:
			self.NormalItem = None
		if("IsBall" in yamlTree):
			self.IsBall = yamlTree["IsBall"]
		else:
			self.IsBall = False
		if("IsSpecial" in yamlTree):
			self.IsSpecial = yamlTree["IsSpecial"]
		else:
			self.IsSpecial = False

		if("IsBerry" in yamlTree):
			self.IsBerry = yamlTree["IsBerry"]
			self.BerryFlag = self.Name.upper().replace(" ", "_")
			#self.BerryFlag = yamlTree["BerryFlag"]
		else:
			self.IsBerry = False
			self.BerryFlag = None

		if("HintName" in yamlTree):
			self.HintName = yamlTree["HintName"]
		else:
			self.HintName = self.Name

		self.Tags = []
		if "Tags" in yamlTree:
			for tag in yamlTree["Tags"]:
				self.Tags.append(Tag(treeItem=tag))

		if(isinstance(self.NormalItem,str)):
			self.NormalItem = self.NormalItem
		self.HasPKMN = yamlTree["HasPKMN"]
		self.WildTableList = yamlTree["WildTableList"]
		if self.WildTableList is None:
			self.WildTableList = []
		elif isinstance(self.WildTableList,str):
			self.WildTableList = [self.WildTableList]
		self.LocationReqs = yamlTree["LocationReqs"]
		if self.LocationReqs is None:
			self.LocationReqs = []
		elif isinstance(self.LocationReqs,str):
			self.LocationReqs = [self.LocationReqs]
		self.FlagReqs = yamlTree["FlagReqs"]
		if self.FlagReqs is None:
			self.FlagReqs = []
		elif isinstance(self.FlagReqs,str):
			self.FlagReqs = [self.FlagReqs]
		if("Hidden Items" in self.FlagReqs):
			self.IsHidden = True
			self.IsSpecial = True
		else:
			self.IsHidden = False
		self.ItemReqs = yamlTree["ItemReqs"]
		if self.ItemReqs is None:
			self.ItemReqs = []
		elif isinstance(self.ItemReqs,str):
			self.ItemReqs = [self.ItemReqs]
		self.FlagsSet = yamlTree["FlagsSet"]
		if self.FlagsSet is None:
			self.FlagsSet = []
		elif isinstance(self.FlagsSet,str):
			self.FlagsSet = [self.FlagsSet]
		self.ReachableReqs = yamlTree["ReachableReqs"]
		if self.ReachableReqs is None:
			self.ReachableReqs = []
		self.Code = yamlTree["Code"]
		if("SecondaryCode" in yamlTree):
			self.SecondaryCode = yamlTree["SecondaryCode"]
			self.SecondaryFile = yamlTree["SecondaryFile"]
		else:
			self.SecondaryCode = None
		self.Text = yamlTree["Text"]
		if ("TrainerList" in yamlTree):
			self.Trainers = yamlTree["TrainerList"]
		else:
			self.Trainers = None
		if self.Trainers is not None:
			self.AreaLevel = yamlTree["AREALV"]
		self.Sublocations = []
		if ("Sublocations" in yamlTree):
			if (yamlTree["Sublocations"] is not None):
				for i in yamlTree["Sublocations"]:
					self.Sublocations.append(Location(i))

		if "RecommendedFlagReqs" in yamlTree:
			self.RecommendedFlagReqs = yamlTree["RecommendedFlagReqs"]
		else:
			self.RecommendedFlagReqs = []
		if self.RecommendedFlagReqs is None:
			self.RecommendedFlagReqs = []
		elif isinstance(self.RecommendedFlagReqs, str):
			self.RecommendedFlagReqs = [self.RecommendedFlagReqs]

		if "RecommendedItemReqs" in yamlTree:
			self.RecommendedItemReqs = yamlTree["RecommendedItemReqs"]
		else:
			self.RecommendedItemReqs = []
		if self.RecommendedItemReqs is None:
			self.RecommendedItemReqs = []
		elif isinstance(self.RecommendedItemReqs, str):
			self.RecommendedItemReqs = [self.RecommendedItemReqs]

		if "RecommendedLocationReqs" in yamlTree:
			self.RecommendedLocationReqs = yamlTree["RecommendedLocationReqs"]
		else:
			self.RecommendedLocationReqs = []
		if self.RecommendedLocationReqs is None:
			self.RecommendedLocationReqs = []
		elif isinstance(self.RecommendedLocationReqs, str):
			self.RecommendedLocationReqs = [self.RecommendedLocationReqs]

		self.IsGym = False
		self.IsActuallyGym = False
		self.Banned = False

		if "WarpReqs" in yamlTree:
			self.WarpReqs = yamlTree["WarpReqs"]
			if self.WarpReqs is None:
				self.WarpReqs = []
			elif isinstance(self.WarpReqs, str):
				self.WarpReqs = [self.WarpReqs]
		else:
			self.WarpReqs = []

		if self.Type == "Transition":
			self.FlagReqs.append("Warps")


	#determine if this location is reachable
	#reachable defined by requirements being present in state
	#and reachable reqs NOT present in state
	def isReachable(self, state, recommended=None):
		if recommended is None:
			recommended = True
		reachable = True
		for i in self.LocationReqs:
			reachable = reachable and state[i]
		for i in self.FlagReqs:
			reachable = reachable and state[i]
		for i in self.ItemReqs:
			reachable = reachable and state[i]
		for i in self.ReachableReqs:
			reachable = reachable and not state[i]
		if recommended:
			for i in self.RecommendedItemReqs:
				reachable = reachable and state[i]
			for i in self.RecommendedLocationReqs:
				reachable = reachable and state[i]
			for i in self.RecommendedFlagReqs:
				reachable = reachable and state[i]
		return reachable
	
	#return the set of requirements for this location that still need to be met
	def requirementsNeeded(self,state, recommended=None):
		if recommended is None:
			recommended = True
		reqList = []
		for i in self.LocationReqs:
			if not state[i]:
				reqList.append(i)
		for i in self.FlagReqs:
			if not state[i]:
				reqList.append(i)
		for i in self.ItemReqs:
			if not state[i]:
				reqList.append(i)
		if recommended:
			for i in self.RecommendedLocationReqs:
				if not state[i]:
					reqList.append(i)
			for i in self.RecommendedItemReqs:
				if not state[i]:
					reqList.append(i)
			for i in self.RecommendedFlagReqs:
				if not state[i]:
					reqList.append(i)
		return reqList
	
	#returns the flags set by this location
	def getFlagList(self):
		return self.FlagsSet
	
	#returns if this is an item or not
	def isItem(self):
		return self.IsItem

	# returns if this is an item or not
	def wasItem(self):
		return self.WasItem
	
	#return if this is a gym or not
	#Gym class overloads this to return true
	def isGym(self):
		return self.IsGym
	
	def applyBanList(self, banList, allowList, flags=None, banned=False):
		list = [];
		if flags is None:
			flags = []
		# Some location to be banned from being used by default
		# Need to NOT run this on generation
		if banned or "Banned" in self.FlagReqs and "No Ban" not in flags:
			if self.IsItem:
				self.IsItem = False
				self.WasItem = True
				self.Type = 'Map'
				self.Banned = True
				# Maybe?
				if "Banned" in self.FlagReqs:
					self.FlagReqs.remove("Banned")

			for i in self.Sublocations:
				# What does this affect? Currently this over-bans all sublocations
				# but getting there should not be possible anyway
				i.applyBanList(banList, allowList, flags)

			return

		if((not (banList is None) and self.Name in banList) or (not (allowList is None) and self.Name not in allowList)):
			#print('Banning '+self.Name)
			if(self.isItem()):
				self.IsItem = False
				self.WasItem = True
				self.Type = 'Map'
				self.Banned = True
			else:
				#this means its a map location, so we need to just make it unreachable
				#unless its a gym, in which case nothing happens
				#note that this only functions for the BANLIST
				#for the allow list, it will still be available because that would be tedious and defeating the entire point of the allow list
				if(not self.isGym() and (not (banList is None) and self.Name in banList)):
					self.FlagReqs.append('Banned')
		for i in self.Sublocations:
			 i.applyBanList(banList, allowList, flags)


	# Finds any requirements for the location for potentially adding Fly Warp logic
	def hasBaseRequirement(self, inputFlags):
		notInputFlags = [x for x in self.FlagReqs if x not in inputFlags]
		hasItemReqs = [x for x in self.ItemReqs]

		hasRecommendFlag = [x for x in self.RecommendedFlagReqs if x not in inputFlags]
		hasRecommendedItem = [x for x in self.RecommendedItemReqs]

		totalLength = len(notInputFlags) + len(hasItemReqs) + len(hasRecommendedItem) + len(hasRecommendFlag)

		return totalLength != 0

	def applyWarpLogic(self, flags):
		# Remove standard requirements for warp randomisation
		# At definition, if the original requirements are still possible even in Warp Rando, then a fork must be made
		# e.g. Cianwood City can be warped to now, but can still be surfed from Olivine/Whirl Islands
		# This shall not add in location logic for flags or otherwise
		if len(self.WarpReqs) > 0:

			validWarpNames = {}
				#{"Cianwood"}

			dontChange = ["8 Badges", "Rocket Invasion", "All Badges", "Woke Snorlax",
						  "Most Map Access", "Elite Four"]

			newLoc = []
			for warp in self.WarpReqs:
				if warp in validWarpNames or len(validWarpNames) == 0:
					if warp in dontChange:
						newLoc.append(warp)
					else:
						newLoc.append(warp + LoadLocationData.WARP_OPTION)

			if len(newLoc) > 0:
				self.LocationReqs = newLoc



		if self.Type == "Transition" or self.Type == "Starting Warp":
			dontChange = ["8 Badges", "Rocket Invasion", "All Badges", "Woke Snorlax",
						  "Most Map Access", "Elite Four"]

			if self.Name not in dontChange:
				self.Name = self.Name + LoadLocationData.WARP_OPTION
			newReqs = []

			for x in self.LocationReqs:
				if x not in dontChange:
					newReqs.append(x + LoadLocationData.WARP_OPTION)
				else:
					newReqs.append(x)
			self.LocationReqs = newReqs

		if self.Type == "Transition" and self.hasBaseRequirement(flags):
			if "Fly Warps" in flags:
				if "Storm Badge" not in self.RecommendedFlagReqs:
					self.RecommendedFlagReqs.append("Storm Badge")
				if "Fly" not in self.RecommendedItemReqs:
					self.RecommendedItemReqs.append("Fly")

		if "Fly Warps" in flags:
			fly_first = self.hasBaseRequirement(flags)

			if fly_first:
				if "Storm Badge" not in self.RecommendedFlagReqs:
					self.RecommendedFlagReqs.append("Storm Badge")

				if "Fly" not in self.RecommendedItemReqs:
					self.RecommendedItemReqs.append("Fly")


		for i in self.Sublocations:
			i.applyWarpLogic(flags)

	def applyModifiers(self, modifierDict, flags, warpless=True):
		list = [];

		warpLessModiferName = self.Name
		if warpless and LoadLocationData.WARP_OPTION in warpLessModiferName:
			warpLessModiferName = warpLessModiferName.replace(LoadLocationData.WARP_OPTION, "")

		if(warpLessModiferName in modifierDict):
			#print('Modifying '+self.Name)
			for j in modifierDict[warpLessModiferName]:
				if 'NewItemReqs' in j:
					if not (j['NewItemReqs'] is None):
						self.ItemReqs = j['NewItemReqs']
					else:
						self.ItemReqs = self.ItemReqs
				if 'NewFlagReqs' in j:
					if not (j['NewFlagReqs'] is None):
						self.FlagReqs = j['NewFlagReqs']
					else:
						self.FlagReqs = self.FlagReqs
				if 'NewLocationReqs' in j:
					if not (j['NewLocationReqs'] is None):
						self.LocationReqs = j['NewLocationReqs']
					else:
						self.LocationReqs = self.LocationReqs
				if 'AddFlagReqs' in j:
					toAdd = j["AddFlagReqs"]
					for x in toAdd:
						if x not in self.FlagReqs:
							self.FlagReqs.append(x)
				if 'AddItemReqs' in j:
					toAdd = j["AddItemReqs"]
					for x in toAdd:
						if x not in self.ItemReqs:
							self.ItemReqs.append(x)
				if 'AddLocationReqs' in j:
					toAdd = j["AddLocationReqs"]
					for x in toAdd:
						if x not in self.LocationReqs:
							self.LocationReqs.append(x)
				if 'RemoveFlagReqs' in j:
					toRemove = j["RemoveFlagReqs"]
					for x in toRemove:
						if x in self.FlagReqs:
							self.FlagReqs.remove(x)
				if 'RemoveItemReqs' in j:
					toRemove = j["RemoveItemReqs"]
					for x in toRemove:
						if x in self.ItemReqs:
							self.ItemReqs.remove(x)
				if 'RemoveLocationReqs' in j:
					toRemove = j["RemoveLocationReqs"]
					for x in toRemove:
						if x in self.LocationReqs:
							self.LocationReqs.remove(x)
				if 'AddHandle' in j:
					toAdd = j["AddHandle"]
					for x in toAdd:
						if x not in self.Handles:
							self.Handles.append(x)
				if 'AddRecommendedFlagReqs' in j:
					toAdd = j["AddRecommendedFlagReqs"]
					for x in toAdd:
						if x not in self.RecommendedFlagReqs:
							self.RecommendedFlagReqs.append(x)
				if 'RemoveRecommendedFlagReqs' in j:
					toRemove = j["RemoveRecommendedFlagReqs"]
					for x in toRemove:
						if x in self.RecommendedFlagReqs:
							self.RecommendedFlagReqs.append(x)
				if 'AddRecommendedItemReqs' in j:
					toAdd = j["AddRecommendedItemReqs"]
					for x in toAdd:
						if x not in self.RecommendedItemReqs:
							self.RecommendedItemReqs.append(x)
				if 'RemoveRecommendedItemReqs' in j:
					toRemove = j["RemoveRecommendedItemReqs"]
					for x in toRemove:
						if x in self.RecommendedItemReqs:
							self.RecommendedItemReqs.append(x)

				if 'AddRecommendedLocationReqs' in j:
					toAdd = j["AddRecommendedLocationReqs"]
					for x in toAdd:
						if x not in self.RecommendedLocationReqs:
							self.RecommendedLocationReqs.append(x)
				if 'RemoveRecommendedLocationReqs' in j:
					toRemove = j["RemoveRecommendedLocationReqs"]
					for x in toRemove:
						if x in self.RecommendedLocationReqs:
							self.RecommendedLocationReqs.append(x)

		if "No Flash" in flags:
			if "Zephyr Badge" in self.FlagReqs and "Flash" in self.ItemReqs and \
					"Always Flash" not in self.FlagReqs:
				self.FlagReqs.remove("Zephyr Badge")
				self.ItemReqs.remove("Flash")
		if "Start With Bike" in flags:
			if "Bicycle" in self.ItemReqs:
				self.ItemReqs.remove("Bicycle")
			if "Bicycle" in self.RecommendedItemReqs:
				self.RecommendedItemReqs.remove("Bicycle")

		if "Delete Fly" in flags and ("Fly" in self.ItemReqs or "Fly" in self.RecommendedItemReqs):
			self.FlagReqs.append("Impossible")

		for i in self.Sublocations:
			 i.applyModifiers(modifierDict, flags)
	
	#get all trash items in this locations tree
	def getTrashItemList(self, flags,labelling = False):
		list = []
		include = True

		if 'Hidden Items' in self.FlagReqs and "Hidden Items" not in flags:
			include = False
		if 'Berry Trees' in self.FlagReqs and "Berry Trees" not in flags:
			include = False
		if 'Timed Events' in self.FlagReqs and "Timed Events" not in flags:
			include = False
		if 'Bug Catching Contest' in self.FlagReqs and 'Bug Catching Contest' not in flags:
			include = False
		if 'Phone Call Trainers' in self.FlagReqs and 'Phone Call Trainers' not in flags:
			include = False
		if 'Mon Locked Checks' in self.FlagReqs and 'Mon Locked Checks' not in flags:
			include = False
		if 'Pointless Checks' in self.FlagReqs and "Pointless Checks" not in flags:
			include = False
		if 'NPC Trash Can' in self.FlagReqs and "NPC Trash Can" not in flags:
			include = False
		if 'Shopsanity' in self.FlagReqs and "Shopsanity" not in flags:
			include = False
		if "Possible Sale" in self.FlagReqs and "Phone Call Trainers" not in flags:
			include = False
		if "Game Corner Access" in self.FlagReqs and "Game Corner Items" not in flags:
			include = False
		if "Buena Access" in self.FlagReqs and "Buena Items" not in flags:
			include = False
		if "Impossible" in self.FlagReqs:
			include = False
		if self.Dummy:
			include = False

		if include:
			if self.NormalItem is not None and self.isItem():
				list.append(self.NormalItem)
			for i in self.Sublocations:
				list.extend(i.getTrashItemList(flags, labelling = labelling))
		#if this item isn't included, then don't use it as an item location
		elif not labelling and self.isItem() and not self.Dummy:
			self.Type = 'Map'
			self.WasItem = True
			self.IsItem = False
		return list

	def UpdateTags(self):
		if self.IsBerry:
			self.Tags.append(Tag(name="Berry"))

		if self.IsHidden:
			self.Tags.append(Tag(name="Hidden"))

		#if self.IsBall:
		#	self.Tags.append(Tag(name="Ball"))

		if "Timed Events" in self.FlagReqs:
			self.Tags.append(Tag(name="Time"))

		if "Pure Evil Checks" in self.FlagReqs:
			self.Tags.append(Tag(name="Evil"))

	def isShop(self):
		return self.IsShop

	def isBargainShop(self):
		return self.IsBargainShop

	def isVendingMachine(self):
		return self.IsVendingMachine

	def isPrize(self):
		return self.IsPrize

	def isBuenaItem(self):
		return self.IsBuenaItem

	def isShopLike(self):
		return self.isShop() or self.isVendingMachine() or self.isPrize()