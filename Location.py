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
		print("Creating Location "+yamlTree["Name"])
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
		self.Type = yamlTree["Type"]
		self.item = None
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
			self.BerryFlag = yamlTree["BerryFlag"]
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
		self.Sublocations = [];
		if ("Sublocations" in yamlTree):
			if (yamlTree["Sublocations"] is not None):
				for i in yamlTree["Sublocations"]:
					self.Sublocations.append(Location(i))
		self.IsGym = False
		self.IsActuallyGym = False
	#determine if this location is reachable
	#reachable defined by requirements being present in state
	#and reachable reqs NOT present in state
	def isReachable(self, state):
		reachable = True
		for i in self.LocationReqs:
			reachable = reachable and state[i]
		for i in self.FlagReqs:
			reachable = reachable and state[i]
		for i in self.ItemReqs:
			reachable = reachable and state[i]
		for i in self.ReachableReqs:
			reachable = reachable and not state[i]
		return reachable
	
	#return the set of requirements for this location that still need to be met
	def requirementsNeeded(self,state):
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
		return reqList
	
	#returns the flags set by this location
	def getFlagList(self):
		return self.FlagsSet
	
	#returns if this is an item or not
	def isItem(self):
		return self.IsItem
	
	#return if this is a gym or not
	#Gym class overloads this to return true
	def isGym(self):
		return self.IsGym
	
	def applyBanList(self, banList, allowList):
		list = [];
		if((not (banList is None) and self.Name in banList) or (not (allowList is None) and self.Name not in allowList)):
			print('Banning '+self.Name)
			if(self.isItem()):
				self.IsItem = False
				self.Type = 'Map'
			else:
				#this means its a map location, so we need to just make it unreachable
				#unless its a gym, in which case nothing happens
				#note that this only functions for the BANLIST
				#for the allow list, it will still be available because that would be tedious and defeating the entire point of the allow list
				if(not self.isGym() and (not (banList is None) and self.Name in banList)):
					self.FlagReqs.append('Impossible')
		for i in self.Sublocations:
			 i.applyBanList(banList, allowList)

	def applyModifiers(self, modifierDict):
		list = [];
		if(self.Name in modifierDict):
			print('Modifying '+self.Name)
			for j in modifierDict[self.Name]:
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
		for i in self.Sublocations:
			 i.applyModifiers(modifierDict)
	
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
		if include:
			if self.NormalItem is not None and self.isItem():
				list.append(self.NormalItem)
			for i in self.Sublocations:
				list.extend(i.getTrashItemList(flags, labelling = labelling))
		#if this item isn't included, then don't use it as an item location
		elif not labelling and self.isItem():
			self.Type = 'Map'
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