import RunCustomRandomization
import yaml
import json

romPath = 'crystal-speedchoice-v6.0.gbc'
yamlfile = open("../Modes/TMPlusKeyItems.yml")
yamltext = yamlfile.read()
settings = yaml.load(yamltext, Loader=yaml.FullLoader)
yamlfile = open(settings['BasePatch'])
yamltext = yamlfile.read()
patches = json.loads(yamltext)
modFileList = settings['DefaultModifiers']
modList = []
for i in modFileList:
	yamlfile = open(i)
	yamltext = yamlfile.read()
	modList.append(yaml.load(yamltext, Loader=yaml.FullLoader))
RunCustomRandomization.randomizeRom(romPath,settings['Goal'], settings['FlagsSet'],patches, banList = settings['BannedLocations'], allowList = settings['AllowedLocations'], modifiers = modList)