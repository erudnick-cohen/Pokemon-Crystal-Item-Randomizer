import RunCustomRandomization
import yaml

romPath = 'crystal-speedchoice-v6.0.gbc'
yamlfile = open("Modes/TMPlusKeyItems.yml")
yamltext = yamlfile.read()
settings = yaml.load(yamltext)
RunCustomRandomization.randomizeRom(romPath,settings['Goal'], settings['FlagsSet'], banList = settings['BannedLocations'], allowList = settings['AllowedLocations'])