import hashlib

import LoadLocationData
import RunCustomRandomizationAssumedFill as RunCustomRandomization
import yaml
import json
from shutil import copyfile

import Seed

romPath = 'testFullAccess.gbc'
copyfile(romPath, 'Hmmm'+romPath)

yamlfile = open("Modes/TMPlusKeyItems+.yml")
yamltext = yamlfile.read()
settings = yaml.load(yamltext, Loader=yaml.FullLoader)
yamlfile = open(settings['BasePatch'])
yamltext = yamlfile.read()
patches = json.loads(yamltext)
modFileList = settings['DefaultModifiers']
modList = []
#plandoPlacements = {"Hidden Machine Part" : "Radio Card", "Route 29 Potion" : "Squirtbottle", "Route 30 Berry Man" : "OLD_ROD", "Violet City Gym Badge": "Storm Badge", "Falkner TM" : "Fly", "Route 31 Pokeball" : "Cut", 'Goldenrod City Gym' : "Hive Badge", "Route 30 Antidote" : "Pass", 'Azalea Town Gym Badge': 'Fog Badge', 'Buena Item': "GOOD_ROD"}
#plandoPlacements = {'Celadon City Gym Badge':'Fog Badge' }
plandoPlacements = {}
#CoreProgress = ['Surf','Fog Badge', 'Pass', 'S S Ticket', 'Squirtbottle','Cut','Hive Badge']
for i in modFileList:
	yamlfile = open(i)
	yamltext = yamlfile.read()
	modList.append(yaml.load(yamltext, Loader=yaml.FullLoader))
seed = Seed.generateSeed()
res = RunCustomRandomization.randomizeRom('Hmmm'+romPath,settings['Goal'], seed,
										  flags = settings['FlagsSet'],
										  patchList=patches, banList = settings['BannedLocations'],
										  allowList = settings['AllowedLocations'],
										  modifiers = modList,
										  plandoPlacements = plandoPlacements,
										  otherSettings = settings)

locationList = res[7]
accessible = res[0]
#locationNames = list(map(lambda x: x.Name, locationList))
inaccessible = []
for location in locationList:
	permittedExclusion = False

	if location.Banned:
		permittedExclusion = True

	if 'Hidden Items' in location.FlagReqs and "Hidden Items" not in settings['FlagsSet']:
		permittedExclusion = True
	if 'Berry Trees' in location.FlagReqs and "Berry Trees" not in settings['FlagsSet']:
		permittedExclusion = True
	if 'Timed Events' in location.FlagReqs and "Timed Events" not in settings['FlagsSet']:
		permittedExclusion = True
	if 'Bug Catching Contest' in location.FlagReqs and 'Bug Catching Contest' not in settings['FlagsSet']:
		permittedExclusion = True
	if 'Phone Call Trainers' in location.FlagReqs and 'Phone Call Trainers' not in settings['FlagsSet']:
		permittedExclusion = True
	if 'Mon Locked Checks' in location.FlagReqs and 'Mon Locked Checks' not in settings['FlagsSet']:
		permittedExclusion = True
	if 'Pointless Checks' in location.FlagReqs and "Pointless Checks" not in settings['FlagsSet']:
		permittedExclusion = True
	if 'NPC Trash Can' in location.FlagReqs and "NPC Trash Can" not in settings['FlagsSet']:
		permittedExclusion = True
	if 'Warps' in location.FlagReqs and "Warps" not in settings["FlagsSet"]:
		permittedExclusion = True
	if 'Impossible' in location.LocationReqs \
		or 'Banned' in location.LocationReqs \
		or 'Unreachable' in location.LocationReqs:
		permittedExclusion = True


	if not permittedExclusion and location.Name not in accessible:
		inaccessible.append(location)

print(inaccessible)
