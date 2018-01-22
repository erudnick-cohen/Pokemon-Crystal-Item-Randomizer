import Location
class Gym(Location.Location):
	def __init__(self,yamlTree):
		Location.Location.__init__(self,yamlTree)
		self.badge = None
		self.NormalBadge = yamlTree["NormalBadge"]
		self.Code = yamlTree["BadgeLine"]
	#return if this is a gym or not
	#This is the gym class
	def isGym(self):
		return True