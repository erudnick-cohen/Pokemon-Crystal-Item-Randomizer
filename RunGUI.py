import shutil
import sys

import FileOperations
import RandomizeFunctions
import RandomizerGUI
import time
import yaml
import json
import random
import string
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QInputDialog
import RunCustomRandomizationAssumedFill as RunCustomRandomization
from shutil import copyfile
from collections import OrderedDict
import traceback
import hashlib
import csv
import os
import zlib
import Version


class RunWindow(QtWidgets.QMainWindow, RandomizerGUI.Ui_MainWindow):
	def __init__(self, parent=None):
		super(RunWindow, self).__init__(parent)
		self.setupUi(self)
		_translate = QtCore.QCoreApplication.translate
		yamlfile = open('RandomizerConfig.yml',encoding='utf-8')
		yamltext = yaml.load(yamlfile,Loader=yaml.FullLoader)
		self.loadSettings(yamltext['DefaultSettings'])
		self.modifierList.itemSelectionChanged.connect(self.updateModifierDescription)
		self.ChooseSettings.clicked.connect(self.selectLogicSettings)
		self.LoadModifier.clicked.connect(self.loadModifier)
		self.LoadPack.clicked.connect(self.loadPack)
		self.DeleteModifier.clicked.connect(self.deleteModifier)
		self.romPath = ''
		self.defaultRomDirectory = "."
		if 'BaseRomInputDirectory' in yamltext:
			self.defaultRomDirectory = yamltext['BaseRomInputDirectory']
		self.defaultRomOutDirectory = "."
		self.defaultRom = None
		if 'BaseRomOutputDirectory' in yamltext:
			self.defaultRomOutDirectory = yamltext['BaseRomOutputDirectory']
		if 'BaseRom' in yamltext:
			self.defaultRom = yamltext['BaseRom']
		self.SelectRomFile.clicked.connect(self.selectRom)
		self.Randomize.setEnabled(False)
		self.Randomize.setText(_translate("MainWindow", "No Rom Loaded!"))
		self.Randomize.clicked.connect(self.pressRunRandomiser)
		self.SaveSettings.clicked.connect(self.saveSettings)
		self.PlandoMode = False
		self.PlandoData = {}
		self.LoadPlandoFile.clicked.connect(self.SetUpPlando)
		self.TurnOffPlando.clicked.connect(self.DeactivatePlando)
		self.DefaultSettings.clicked.connect(self.SelectDefaultSettings)
		self.LoadRaceMode.clicked.connect(self.LoadRaceModeSettingsUI)
		self.AddItem.clicked.connect(self.AddBonusItem)
		self.View_Items.clicked.connect(self.RemoveBonusItem)
		self.BadgesNeeded.clicked.connect(self.SetBadgeForSilver)
		self.HintButton.clicked.connect(self.ProcessHintSettings)
		self.modeVariables = {}
		self.setCurrentVariables.clicked.connect(self.SetCurrentVariables)
		self.version.setText(_translate("MainWindow", "Version "+Version.GetItemRandoVersion()))

		self.itemsList = []
		with open('AddItemValues.csv', newline='',encoding='utf-8-sig') as csvfile:
			reader = csv.reader(csvfile)
			for i in reader:
				if(len(i)>0):
					self.itemsList.append(i[0])
					#self.ItemList.addItem(i[0])

		if 'FirstRun' in yamltext:
			firstRunCheck = yamltext['FirstRun']
			if firstRunCheck:
				QtWidgets.QMessageBox.about(self, 'First Run',
											'Please select previous install directory to import custom settings')

				previous_dir = QFileDialog.getExistingDirectory()
				if previous_dir != "":
					self.importSettings(previous_dir)


				self.WriteRandomizerConfig(firstRun=False)

		if self.defaultRom is not None:
			isFullPath = os.path.isfile(self.defaultRom)
			if isFullPath:
				self.romPath = self.defaultRom
				self.Randomize.setEnabled(True)
				self.Randomize.setText(_translate("MainWindow", "Randomize Rom"))
			elif self.defaultRomDirectory is not None:
				romPath = self.defaultRomDirectory + "/" +self.defaultRom
				isEndPath = self.defaultRomDirectory is not None and \
							os.path.isfile(romPath)
				if isEndPath:
					self.romPath = romPath
					self.Randomize.setEnabled(True)
					self.Randomize.setText(_translate("MainWindow", "Randomize Rom"))

	def importSettings(self, oldDirectory):
		oldSettings = oldDirectory + "/RandomizerConfig.yml"
		config_exists = os.path.isfile(oldSettings)
		if config_exists:
			yamlfile = open(oldSettings, encoding='utf-8')
			yamltext = yaml.load(yamlfile, Loader=yaml.FullLoader)

			if "DefaultSettings" in yamltext["DefaultSettings"]:
				self.WriteRandomizerConfig(defaultFile=yamltext["DefaultSettings"])

		modeDirectory = oldDirectory + "/" + "Modes"
		if os.path.isdir(modeDirectory):
			oldModes = []
			newModes = []
			files = os.listdir(modeDirectory)
			for mode in files:
				if os.path.isfile(modeDirectory + "/" + mode):
					oldModes.append(mode)

			if os.path.isdir(modeDirectory + "/" + "Custom"):
				files = os.listdir(modeDirectory + "/Custom" )
				for mode in files:
					if os.path.isfile(modeDirectory + "/Custom/" + mode):
						oldModes.append("Custom/"+mode)

			release_modes = os.listdir("Modes")
			for mode in release_modes:
				if os.path.isfile("Modes" + "/" + mode):
					newModes.append(mode)

			if os.path.isdir("Modes" + "/" + "Custom"):
				files = os.listdir("Modes" + "/" + "Custom")
				for mode in files:
					if os.path.isfile("Modes" + "/Custom/" + mode):
						newModes.append("Custom/"+mode)

			additionalModes = [ mode for mode in
								[ old.replace("Custom/", "") for old in oldModes ]
								if mode not in
								[ new.replace("Custom/", "") for new in newModes ]]
			custom_modes = os.path.isdir("Modes/Custom")
			if not custom_modes:
				os.mkdir("Modes/Custom")

			for additionalMode in additionalModes:
				isCustom = os.path.isfile(modeDirectory + "/Custom/" + additionalMode)
				if isCustom:
					shutil.copy(modeDirectory + "/Custom/" + additionalMode, "Modes/Custom")
				else:
					shutil.copy(modeDirectory + "/" + additionalMode, "Modes/Custom")


	def pressRunRandomiser(self):
		self.runRandomizer()


	def runRandomizer(self, requiredMD5=None):

		dataHash = self.GetDataHash()

		if dataHash != Version.GetExpectedDataHash():
			message = "Map Data invalid. Try reinstalling."
			error_dialog = QtWidgets.QErrorMessage()
			error_dialog.showMessage(message)
			error_dialog.exec_()
			return


		conflicts = []
		seenMods = []
		repeatedMods = []
		modNames = [ mod['Name'] for mod in self.modList ]

		for mod in self.modList:
			if mod in seenMods:
				repeatedMods.append(mod)
			else:
				seenMods.append(mod)


			if 'IncompatibleWith' in mod:
				for item in mod['IncompatibleWith']:
					if item in modNames:
						conflicts.append(mod['Name'] + item)

			withoutRequired = False
			potentialConflicts = []
			if 'IncompatibleWithout' in mod:
				for item in mod['IncompatibleWithout']:
					if item not in modNames:
						potentialConflicts.append(mod['Name'] +  item)
					else:
						withoutRequired = True

				if not withoutRequired:
					conflicts.extend(potentialConflicts)


		if len(conflicts) > 0:
			message = "Mod config error with: "+ ','.join(conflicts)
			error_dialog = QtWidgets.QErrorMessage()
			error_dialog.showMessage('Incompatible modifiers found' + "\n" + message)
			error_dialog.exec_()
			return

		if len(repeatedMods) > 0:
			message = "Mod repeated error with: "+ ','.join([x["Name"] for x in repeatedMods])
			error_dialog = QtWidgets.QErrorMessage()
			error_dialog.showMessage('Incompatible modifiers found' + "\n" + message)
			error_dialog.exec_()
			return


		os.environ['PYTHONHASHSEED'] = '0'#this needs to be reproducible! so this can't be random!
		rngSeed = str(time.time())
		random.seed(rngSeed)
		rngSeed = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
		if(self.SeedInput.text() != ''):
			rngSeed = self.SeedInput.text()
		rngSeedBytes = rngSeed.encode('utf-8')

		rSeed = int(hashlib.md5(rngSeedBytes).hexdigest(),16)
		print('numeric seed is: '+str(rSeed))
		random.seed(rSeed)
		_translate = QtCore.QCoreApplication.translate
		yamlfile = open(self.settings['BasePatch'])
		yamltext = yamlfile.read()
		patches = json.loads(yamltext)
		modFileList = self.settings['DefaultModifiers']
		try:
			tlv = 0
			wlv = 0
			self.Randomize.setEnabled(False)
			self.Randomize.setText(_translate("MainWindow", "Randomizing"))
			QtGui.QGuiApplication.processEvents()
			#QtWidgets.QMessageBox.about(self, 'Message', 'Please select the name for the file. Make sure that you used a Speeedchoice V7.3 Rom as the base rom, or your game WILL crash.')
			validFileName = False


			base_dir = self.defaultRomOutDirectory
			if base_dir == ".":
				for i in range(0, len(self.romPath.split("/"))-1):
					if base_dir != "":
						base_dir+="/"
					base_dir += self.romPath.split("/")[i]

			exits = 0
			stop_after = 1
			while not validFileName:
				file = QFileDialog.getSaveFileName(directory = base_dir)[0]
				if file != '':
					validFileName = True
				else:
					QtWidgets.QMessageBox.about(self, 'ERROR', 'Please name and save the generated rom...')
					exits += 1
					if exits > stop_after:
						break
			randomizedFileName = file

			if not validFileName:
				QtWidgets.QMessageBox.about(self, 'ERROR', '3 Failed filenames, cancelling')
				return

			if not randomizedFileName.endswith(".gbc"):
				randomizedFileName+=".gbc"
			if 'HintLevel' in self.settings:
				HINT_LEVEL = self.settings['HintLevel']
				MAX_HINTS = self.settings['nHints']
			else:
				HINT_LEVEL = 0
				MAX_HINTS = 0
			HintOptions = RandomizeFunctions.ConvertHintLevelToFlags(HINT_LEVEL, MaxHints=MAX_HINTS)

			settings_md5 = self.GetSettingsMD5()
			print(settings_md5)

			f = open(self.romPath, 'rb')
			romMD5 = str(hashlib.md5(f.read()).hexdigest())
			f.close()

			print("reqMD5", requiredMD5)
			if requiredMD5 is not None:
				if romMD5 != requiredMD5:
					raise Exception("Invalid rom MD5")

			copyfile(self.romPath, randomizedFileName)
			with open('SAVEDSEEDLOG.log','a+') as f:
				f.write(rngSeed+"\n")

			# Fix issue with flags NOT resetting on running a second rom!
			# This will be appended to by modifiers, so ensure a copy is made, not the original!
			flagSettings = self.settings["FlagsSet"].copy()

			if "BannedLocations" in self.settings:
				bannedLocations = self.settings["BannedLocations"]
				if bannedLocations is not None:
					bannedLocations = bannedLocations.copy()

			if "AllowedLocations" in self.settings:
				allowedLocations = self.settings["AllowedLocations"]
				if allowedLocations is not None:
					allowedLocations = allowedLocations.copy()

			preventAdd = None
			if "PreventAddItems" in self.settings:
				preventAdd = self.settings["PreventAddItems"]
				if preventAdd is not None:
					preventAdd = preventAdd.copy()

			progressItems = self.settings["ProgressItems"].copy() if "ProgressItems" in self.settings else None

			coreProgress = self.settings["CoreProgress"].copy() if "CoreProgress" in self.settings else None
			bonusTrash = self.settings["BonusItems"].copy() if "BonusItems" in self.settings else None

			resultDict = RunCustomRandomization. \
				randomizeRom(randomizedFileName, self.settings['Goal'], rSeed, flagSettings, patches,
							 banList=bannedLocations, allowList=allowedLocations,
							 modifiers=self.modList, adjustTrainerLevels=False, adjustRegularWildLevels=False,
							 adjustSpecialWildLevels=False,
							 trainerLVBoost=tlv, wildLVBoost=wlv, requiredItems=progressItems,
							 coreProgress=coreProgress,
							 otherSettings=self.settings, plandoPlacements=self.PlandoData, hintConfig=HintOptions,
							 preventAddingItems=preventAdd, bonusTrash=bonusTrash, modeVariables=self.modeVariables)

			if resultDict is None:
				error_dialog = QtWidgets.QErrorMessage()
				error_dialog.showMessage("Incorrect rom version provided!")
				error_dialog.exec_()
				raise Exception("Invalid ROM")

			self.Randomize.setEnabled(True)

			hasWarning = False
			if "Warnings" in resultDict:
				warnings = resultDict["Warnings"]
				if "HasSilverLeaf" in warnings:
					HasSilverLeaf = warnings["HasSilverLeaf"]
					if HasSilverLeaf:
						hasWarning = True

				if "HasGoldLeaf" in warnings:
					HasGoldLeaf = warnings["HasGoldLeaf"]
					if HasGoldLeaf:
						hasWarning = True

				if "HasLeftoverTrash" in warnings:
					HasLeftoverTrash = warnings["HasLeftoverTrash"]
					if HasLeftoverTrash:
						hasWarning = True

				if "CantReachE4" in warnings:
					CantReachE4 = warnings["CantReachE4"]
					if CantReachE4:
						hasWarning = True

				if "NotAllPlaced" in warnings:
					NotAllPlaced = warnings["NotAllPlaced"]
					if NotAllPlaced:
						hasWarning = True

			raceModeString = None
			if self.RaceModeRadioButton.isChecked() or self.SpoilerOutputRadioButton.isChecked():
				raceMode = {}
				raceMode['Seed'] = rngSeed
				raceMode["Mode"] = self.SettingsFilename
				raceMode["ModeHash"] = self.GetModeHash()
				raceMode["RomMD5"] = romMD5

				raceModeString = self.GetRaceModeValue(raceMode)

				if self.RaceModeRadioButton.isChecked():
					self.LoadRaceModeSettings(raceString=raceModeString, start=False)

					cb = QApplication.clipboard()
					cb.setText(raceModeString, mode=cb.Clipboard)

					QtWidgets.QMessageBox.about(self, "Race Output", "Copied race output to clipboard")

					with open(randomizedFileName + '_SPOILER.txt', 'w') as f:
						f.write(raceModeString)

			if self.SpoilerOutputRadioButton.isChecked():
				outputSpoiler = {}
				outputSpoiler['RNG Seed'] = rngSeed
				outputSpoiler['Solution'] = resultDict["Spoiler"]
				outputSpoiler['Useless Stuff'] = resultDict["Trash"]
				if "RandomizedExtra" in resultDict:
					outputSpoiler["Xtra Stuff"] = resultDict["RandomizedExtra"]

				if "UpgradedItems" in resultDict:
					outputSpoiler["Xtra Upgrades"] = resultDict["UpgradedItems"]

				outputSpoiler["CIR Version"] = Version.GetItemRandoVersion()
				outputSpoiler["Mode"] = self.CurentSettings.text()
				outputSpoiler["ModifierHash"] = self.GetSettingsMD5()
				outputSpoiler["Modifiers"] = self.GetActiveModifiers()
				if hasWarning:
					outputSpoiler["Warnings"] = resultDict["Warnings"]

				if raceModeString is not None:
					outputSpoiler["Race"] = raceModeString

				with open(randomizedFileName+'_SPOILER.txt', 'w') as f:
					yaml.dump(outputSpoiler, f, default_flow_style=False)



			successMessage = "Successfully randomized rom"
			successBoxName = "Success"

			# TODO
			# Change warning handling and result to dictionary for easier readability and extension
			# Handle E4 not possible in the same way

			if hasWarning:
				successMessage = "Sucessfully generated rom with warnings"
				successBoxName = "Success..."


			self.Randomize.setText(_translate("MainWindow", "Randomize Rom"))
			QtWidgets.QMessageBox.about(self, successBoxName, successMessage)
			_translate = QtCore.QCoreApplication.translate
		except:
			error_dialog = QtWidgets.QErrorMessage()
			error_dialog.showMessage(''.join(traceback.format_exc()))
			error_dialog.exec_()


	def desireKey(self, key):
		if key == "Description":
			return False

		return True

	def AmendHash(self, value, h):
		if type(value) == str:
			h.append(value)
		elif type(value) == int:
			h.append(str(value))
		elif type(value) == list:
			for v in value:
				self.AmendHash(v, h)
		elif value is None:
			h.append("0")
		elif type(value) == bool:
			h.append(str(value))
		elif type(value) == float:
			h.append(str(value))
		elif type(value) == dict:
			for key in value.keys():
				if not self.desireKey(key):
					continue
				keyvalue = value[key]
				self.AmendHash(key, h)
				self.AmendHash(keyvalue, h)
		else:
			print("Unhandled type:", type(value))

	def GetDataHash(self):
		folders = ["Map Data", "Gym Data"]
		data = []
		for item in folders:
			newitems = os.listdir(item)
			for i in newitems:
				f = open(item+"/"+i)
				filedata = f.read()
				data.append(filedata)
				f.close()

		new_hash = str.join(";", data)
		return hashlib.md5(new_hash.encode()).hexdigest()



	def GetModeHash(self):
		value_to_hash = []
		self.AmendHash(Version.GetItemRandoVersion(), value_to_hash)
		self.AmendHash(Version.GetSupportedSpeedchoiceVersion(), value_to_hash)
		self.AmendHash(self.settings, value_to_hash)
		self.AmendHash(self.modList, value_to_hash)
		if self.PlandoMode:
			for value in self.PlandoData:
				self.AmendHash(value, value_to_hash)
		new_hash = str.join(";", value_to_hash)
		#print(new_hash)

		return hashlib.md5(new_hash.encode()).hexdigest()

	def GetRaceModeValue(self, seed):
		# Contains Mode, RNG Seed and ModeHash
		race_string = "#".join([seed["Mode"], seed["ModeHash"], seed["Seed"], seed["RomMD5"]])
		hexstring = zlib.compress(bytes(race_string, "utf8")).hex()
		#print(hexstring)
		return hexstring

	def SetBadgeForSilver(self):
		(nBadge, ok2) = QInputDialog.getInt(self,"How many badges will Mt. Silver unlock with?","How many badges will Mt. Silver unlock with?")
		if nBadge <= 16 and ok2:
			if nBadge <= 0:
				error_dialog = QtWidgets.QErrorMessage()
				error_dialog.showMessage("You must choose a number of badges greater than 1! Setting badge requirement to 1.")
				error_dialog.exec_()
				nBadge = 1
			self.settings["SilverBadgeUnlockCount"] = nBadge
			_translate = QtCore.QCoreApplication.translate
			self.BadgesNeeded.setText(_translate("MainWindow", "Change # of badges\n to unlock Mt. Silver? \n(Currently "+str(nBadge)+")"))
			QtGui.QGuiApplication.processEvents()
		elif ok2:
			error_dialog = QtWidgets.QErrorMessage()
			error_dialog.showMessage("There are only 16 badges in Pokemon Crystal! You can't require more, or your game will not be completable!")
			error_dialog.exec_()

	def AddBonusItem(self):
		(addedItem, ok1) = QInputDialog.getItem(self, "Select item you wish to add to the pool", "Select item you wish to add to the pool", self.itemsList, 0, False)
		if ok1:
			(nAdded, ok2) = QInputDialog.getInt(self,"Add how many?","Add how many?")
		if not ('BonusItems' in self.settings):
			self.settings['BonusItems'] = []
		if ok1 and ok2:
			for i in range(0,nAdded):
				self.settings['BonusItems'].append(addedItem)
		#print(self.settings)

	def RemoveBonusItem(self):
		if 'BonusItems' in self.settings and len(self.settings['BonusItems']) > 0:
			self.settings['BonusItems'] = []
			if ('BonusItems' in self.settings): 
				(addedItem, ok1) = QInputDialog.getItem(self, r"View/Remove Items in pool", "Select any item you wish to remove, or cancel to remove nothing", self.settings['BonusItems'], 0, False)
			if ok1:
				(nAdded, ok2) = QInputDialog.getInt(self,"Remove how many?","Remove how many?")
			if not ('BonusItems' in self.settings):
				self.settings['BonusItems'] = []
			if ok1 and ok2:
				for i in range(0,nAdded):
					if addedItem in self.settings['BonusItems']:
						self.settings['BonusItems'].remove(addedItem)
		#print(self.settings)


	def selectRom(self):
		_translate = QtCore.QCoreApplication.translate
		romDirectory = self.defaultRomDirectory
		file = QFileDialog.getOpenFileName(directory = romDirectory)[0]
		self.romPath = file
		if file != '':
			self.Randomize.setEnabled(True)
			self.Randomize.setText(_translate("MainWindow", "Randomize Rom"))
		else:
			self.Randomize.setEnabled(False)
			self.Randomize.setText(_translate("MainWindow", "No Rom Loaded!"))


	def selectLogicSettings(self):
		file = QFileDialog.getOpenFileName(directory = 'Modes')[0]
		if file != '':
			self.loadSettings(file)

	def loadPack(self):
		packfiles = QFileDialog.getOpenFileNames(directory = 'Packs')[0]
		if len(packfiles) > 0:
			currentModifierFiles = [obj["fileName"] for obj in self.modList]
			modifiersToLoad = []
			for packfile in packfiles:
				yamlfile = open(packfile)
				yamltext = yamlfile.read()

				loadedYaml = yaml.load(yamltext, Loader=yaml.FullLoader)

				if 'Modifiers' in loadedYaml:
					self.loadModifiers(loadedYaml['Modifiers'], reset=False)

			for mod in modifiersToLoad:
				if os.path.isfile(mod):
					yamlfile = open(mod)
					yamltext = yamlfile.read()
					loadedYaml = yaml.load(yamltext, Loader=yaml.FullLoader)
					self.modList.append(loadedYaml)
					self.modList[-1]['fileName'] = self.makeFileNameSafe(mod)
				else:
					error_dialog = QtWidgets.QErrorMessage()
					error_dialog.showMessage('Pack Modifier not found:' + "\n" + mod)
					error_dialog.exec_()



			self.updateModListView()

	def loadModifier(self):
		modfiles = QFileDialog.getOpenFileNames(directory = FileOperations.DEFAULT_MODIFIERS_DIRECTORY)[0]
		if len(modfiles) > 0:

			variablesToSet = []

			potentiallyMiss = {}

			for modfile in modfiles:
				yamlfile = open(modfile)
				yamltext = yamlfile.read()

				loadedYaml = yaml.load(yamltext, Loader=yaml.FullLoader)
				currentModifierNames = [obj["Name"] for obj in self.modList]

				if loadedYaml["Name"] in currentModifierNames:
					if len(modfiles) == 1:
						message = loadedYaml["Name"] + " is already loaded!"
						error_dialog = QtWidgets.QErrorMessage()
						error_dialog.showMessage(message)
						error_dialog.exec_()
					continue

				is_incompatible = False
				if "IncompatibleWith" in loadedYaml:
					for incomp in loadedYaml["IncompatibleWith"]:
						if incomp in currentModifierNames:
							is_incompatible = True
							message = loadedYaml["Name"] + "/" + incomp
							error_dialog = QtWidgets.QErrorMessage()
							error_dialog.showMessage('Invalid modifier chosen for selector:'+"\n"+message)
							error_dialog.exec_()

				if "IncompatibleWithout" in loadedYaml:
					options = loadedYaml["IncompatibleWithout"]
					optionFound = False
					for option in options:
						if option in currentModifierNames:
							optionFound = True
					if not optionFound:
						#TODO If loading multiple only show this message at the endpoint
						potentiallyMiss[modfile] = loadedYaml
						is_incompatible = True

				if not is_incompatible:
					self.modList.append(loadedYaml)
					self.modList[-1]['fileName'] = self.makeFileNameSafe(modfile)

					if "VariablesSet" in loadedYaml:
						for variable in loadedYaml["VariablesSet"]:
							variablesToSet.append(variable)


			if len(potentiallyMiss) > 0:
				currentModifierNames = [obj["Name"] for obj in self.modList]
				for miss in potentiallyMiss.keys():
					missYaml = potentiallyMiss[miss]
					is_incompatible = True

					options = missYaml["IncompatibleWithout"]
					found = False
					for option in options:
						if option in currentModifierNames:
							found = True

					if found:
						is_incompatible = False

					if not is_incompatible:
						self.modList.append(missYaml)
						self.modList[-1]['fileName'] = self.makeFileNameSafe(miss)
					else:
						message = missYaml["Name"] + ":" + '/'.join(options)
						print(message)
						error_dialog = QtWidgets.QErrorMessage()
						error_dialog.showMessage('Modifier chosen invalid without other:' + "\n" + message)
						error_dialog.exec_()

			if self.setNewVariables.isChecked():
				for variable in variablesToSet:
					self.PromptForVariable(variable)

			self.updateModListView()

	def PromptForVariable(self, variable):
		variableName = list(variable.keys())[0]
		variableDefault = variable[variableName]

		success = QInputDialog.getText(self, "Set variable", variableName + " (default is " + str(variableDefault) + ")")
		if success[1]:
			variableValue = success[0]
			if len(variableValue) != 0:
				self.modeVariables[variableName] = variableValue

		else:
			return



	def deleteModifier(self):
		row = self.modifierList.currentRow()
		if(row != -1):
			self.modifierList.setCurrentRow(-1)
			self.modList.pop(row)
			self.updateModListView()

	def makeFileNameSafe(self, mod):
		runningDirectory = os.getcwd().replace("\\", "/") + "/"

		sp = runningDirectory.split("/")
		root = sp[0]
		isAbsolute = False
		if root == "":
			if mod.startswith("/"):
				isAbsolute = True
		elif mod.startswith(root):
			isAbsolute = True

		if runningDirectory in mod:
			safeFile = mod.replace(runningDirectory, "")
			return safeFile
		elif isAbsolute:
			return None

		return mod

	def findFileWithinDirectory(self, name, directory):
		files = os.listdir(directory)
		for file in files:
			path_full = directory + "/" + file
			if os.path.isdir(path_full):
				found = self.findFileWithinDirectory(name, path_full)
				if found is not None:
					return found
			elif os.path.isfile(path_full):
				if name == file:
					return path_full

		return None


	def loadModifiers(self, modifiersList, reset=True):
		if reset:
			self.modList = []

		current = [x["fileName"] for x in self.modList]

		for i in modifiersList:
			fileToLoad = i
			if not os.path.isfile(i):
				filepart = i.split("/")[-1]
				fileToLoad = FileOperations.FindModifier(filepart)

			if fileToLoad is not None:
				if fileToLoad in current:
					continue
				yamlfile = open(fileToLoad)
				yamltext = yamlfile.read()
				self.modList.append(yaml.load(yamltext, Loader=yaml.FullLoader))
				self.modList[-1]['fileName'] = self.makeFileNameSafe(fileToLoad)
			else:
				error_dialog = QtWidgets.QErrorMessage()
				error_dialog.showMessage('Modifier not found:' + "\n" + i)
				error_dialog.exec_()


	def loadSettings(self, settingsFile):
		_translate = QtCore.QCoreApplication.translate

		self.SettingsFilename = self.makeFileNameSafe(settingsFile)
		if self.SettingsFilename is None:
			raise Exception("Must load correctly.")

		if not os.path.isfile(settingsFile):
			raise Exception("Mode file not found:", settingsFile)

		yamlfile = open(settingsFile,encoding='utf-8')
		yamltext = yamlfile.read()
		settings = yaml.load(yamltext, Loader=yaml.FullLoader)
		self.settings = settings
		yamlfile = open(settings['BasePatch'],encoding='utf-8')
		yamltext = yamlfile.read()
		patches = json.loads(yamltext)
		modFileList = settings['DefaultModifiers']
		self.loadModifiers(modFileList)
		self.updateModListView()
		self.CurentSettings.setText(_translate("MainWindow", settings['Name']))
		self.SettingsDescription.setText(_translate("MainWindow", settings['Description']))
		self.CurrentGoal.setText(_translate("MainWindow", settings['Goal']))
		if "SilverBadgeUnlockCount" in self.settings:
			_translate = QtCore.QCoreApplication.translate
			self.BadgesNeeded.setText(_translate("MainWindow", "Change # of badges\n to unlock Mt. Silver? \n(Currently "+str(self.settings["SilverBadgeUnlockCount"])+")"))
			QtGui.QGuiApplication.processEvents()
		else:
			self.BadgesNeeded.setText(_translate("MainWindow",
												 "Change # of badges\n to unlock Mt. Silver? \n(Currently " + str(16) + ")"))

		if 'HintLevel' in self.settings:
			self.HintButton.setText(_translate("MainWindow", "Set Hints (LV: "+str(self.settings['HintLevel'])+" N"+str(self.settings['nHints'])+")"))
			QtGui.QGuiApplication.processEvents()
		else:
			self.HintButton.setText(_translate("MainWindow", "Set Hints (off)"))
			QtGui.QGuiApplication.processEvents()

		if "Plando" in self.settings:
			newSpoiler = OrderedDict()
			for key in self.settings["Plando"]:
				newSpoiler[key] = self.settings["Plando"][key]
			self.PlandoData = newSpoiler
			del self.settings['Plando']
			self.PlandoMode = True
			self.TurnOffPlando.setEnabled(True)
		else:
			self.DeactivatePlando()

		if "ModeVariables" in self.settings:
			for variable in self.settings["ModeVariables"].keys():
				self.modeVariables[variable] = self.settings["ModeVariables"][variable]


			
	def saveSettings(self):
		fName = QFileDialog.getSaveFileName(directory = 'Modes/Custom')[0]
		fName = self.makeFileNameSafe(fName)
		if(fName != ''):
			filename = fName if fName.endswith(".yml") else fName + ".yml"
			self.settings['DefaultModifiers'] = []
			for i in self.modList:
				self.settings['DefaultModifiers'].append(i['fileName'])

			if self.PlandoMode:
				self.settings["Plando"] = {}
				for key in self.PlandoData.keys():
					self.settings["Plando"][key] = self.PlandoData[key]

			if "ModeVariables" not in self.settings:
				self.settings["ModeVariables"] = {}
			for variable_name in self.modeVariables:
				self.settings["ModeVariables"][variable_name] = self.modeVariables[variable_name]


			with open(filename, 'w',encoding='utf-8') as f:
				yaml.dump(self.settings, f, default_flow_style=False)

			self.loadSettings(filename)
				
	def SetUpPlando(self):
		QtWidgets.QMessageBox.about(self, 'Plandomizer Mode', 'Select a log file (which need not specify every item allocation) to use as basis for plandomizer.\n NOTE: We are not reponsible for any lost friendships due to use of plandomizer mode')
		file = QFileDialog.getOpenFileName(directory = '.')[0]
		if file != '':
			yamlfile = open(file)
			yamltext = yamlfile.read()
			spoiler = yaml.load(yamltext, Loader=yaml.FullLoader)
			newSpoiler = OrderedDict()

			if 'Solution' in spoiler:
				for i in sorted(spoiler['Solution'],reverse=True):
					print("Plando:",i)
					print(spoiler['Solution'][i])
					newSpoiler[spoiler['Solution'][i]] = i
				print(newSpoiler)
			if 'Useless Stuff' in spoiler:
				for i in spoiler['Useless Stuff']:
					iValue = spoiler['Useless Stuff'][i]
					itemSplit = iValue.split("->")
					if len(itemSplit) > 1:
						itemUse = itemSplit[0]
					else:
						itemUse = itemSplit[0]
					print("Plando-load", i, itemUse)
					newSpoiler[i] = itemUse
			self.PlandoData = newSpoiler
			self.PlandoMode = True
			self.TurnOffPlando.setEnabled(True)
			
	def DeactivatePlando(self):
		self.PlandoData = {}
		self.PlandoMode = False
		self.TurnOffPlando.setEnabled(False)

	def updateModListView(self):
		self.modifierList.clear()
		for i in self.modList:
			self.modifierList.addItem(i['Name'])

	def updateModifierDescription(self):
		_translate = QtCore.QCoreApplication.translate
		row = self.modifierList.currentRow()
		if(row != -1 and row < len(self.modList)):
			self.ModifierDescription.setText(_translate("MainWindow", self.modList[row]['Description']))
		else:
			self.ModifierDescription.setText(_translate("MainWindow", "No modifier selected!"))

	def WriteRandomizerConfig(self, defaultFile=None, firstRun=None):
		yamlfile = open('RandomizerConfig.yml')
		yamltext = yaml.load(yamlfile, Loader=yaml.FullLoader)

		if defaultFile is not None:
			yamltext['DefaultSettings'] = defaultFile

		if firstRun is not None:
			yamltext["FirstRun"] = firstRun

		with open('RandomizerConfig.yml', 'w', encoding='utf-8') as f:
			yaml.dump(yamltext, f, default_flow_style=False)
			
	def SelectDefaultSettings(self):
		QtWidgets.QMessageBox.about(self, 'Choose default settings', 'Select the mode which should be loaded by default when you open up the randomizer')
		defaultFile = QFileDialog.getOpenFileName(directory = 'Modes')[0]
		if(defaultFile != ''):
			self.WriteRandomizerConfig(defaultFile)
		else:
			error_dialog = QtWidgets.QErrorMessage()
			error_dialog.showMessage('A file was not selected!')
			error_dialog.exec_()

	def yamlSortFunction(self, y):
		return y["Name"]


	def GetSettingsMD5(self):
		mods = self.modList.copy()
		mods.sort(key=self.yamlSortFunction)
		full_string = ";"
		for mod in mods:
			full_string += mod["Name"] + ";"

		return hashlib.md5(full_string.encode()).hexdigest()

	def LoadRaceModeSettingsUI(self):
		self.LoadRaceModeSettings()

	def LoadRaceModeSettings(self, raceString=None, start=True):
		if raceString is None:
			success = QInputDialog.getText(self, "Race Mode", "Input Race Mode Here")
			if success[1]:
				inputString = success[0]
			else:
				return
		else:
			inputString = raceString

		hex_bytes = bytes.fromhex(inputString)
		decompressed = zlib.decompress(hex_bytes)
		d_string = decompressed.decode("utf8")

		data = d_string.split("#")
		if len(data) != 4:
			raise Exception("Invalid race mode string")

		mode = data[0]
		mode_hash = data[1]
		seed = data[2]
		md5 = data[3]

		print(mode)
		#race_string = seed["Mode"] + "#" + seed["ModeHash"] + "#" + seed["Seed"]

		self.loadSettings(mode)
		my_mode_hash = self.GetModeHash()

		if my_mode_hash != mode_hash:
			print("Mode hash does not match!")
			raise Exception("Mode doesn't match: ",mode)

		if start:
			self.SpoilerOutputRadioButton.setChecked(False)
			self.RaceModeRadioButton.setChecked(False)
			self.NoOutputRadioButton.setChecked(True)

			self.SeedInput.setText(seed)
			if self.romPath is None or len(self.romPath) == 0:
				self.selectRom()
			self.runRandomizer(requiredMD5=md5)

	def GetActiveModifiers(self, filenames=False):
		mods = self.modList.copy()
		mods.sort(key=self.yamlSortFunction)
		full_string = ";"
		for mod in mods:
			if filenames:
				fName = mod["fileName"]
			else:
				fName = mod["Name"]

			full_string += fName + ";"

		return full_string
			
	def ProcessHintSettings(self):
		_translate = QtCore.QCoreApplication.translate
		(option, ok1) = QInputDialog.getItem(self,"What hint level should be used?","What hint level should be used?",['0. No Hints', '1. Gym Signs', '2. Max one per location', '3. More hints types', '4. Hint useless items','5. Many hints everywhere', '6. Hints might be more useless than on 4'])
		if ok1:
			(nHints, ok2) = QInputDialog.getInt(self,"How many different hints?","How many different hints?")
			if ok2 and int(option[0]) > 0:
				self.settings['HintLevel'] = int(option[0])
				self.settings['nHints'] = nHints
				self.HintButton.setText(_translate("MainWindow", "Set Hints (LV: "+str(self.settings['HintLevel'])+" N"+str(self.settings['nHints'])+")"))
				QtGui.QGuiApplication.processEvents()
		else:
			self.settings['HintLevel'] = 0
			self.settings['nHints'] = 0
			
			self.HintButton.setText(_translate("MainWindow", "Set Hints (off)"))
			QtGui.QGuiApplication.processEvents()

	def SetCurrentVariables(self):
		variablesToSet = []
		loadedVariableNames = []

		for variable in self.modeVariables.keys():
			variablesToSet.append({variable:self.modeVariables[variable]})
			loadedVariableNames.append(variable)


		for mod in self.modList:
			if "VariablesSet" in mod:
				for variable in mod["VariablesSet"]:
					variableName = list(variable.keys())[0]
					if variableName not in loadedVariableNames:
						variablesToSet.append(variable)

		if len(variablesToSet) == 0:
			QtWidgets.QMessageBox.about(self, 'Message', 'No variables to set.')
		else:
			for variable in variablesToSet:
				self.PromptForVariable(variable)

		return

def main():
	os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
	app = QApplication(sys.argv)
	form = RunWindow()
	form.show()
	app.exec_()

if __name__ == '__main__':
	main()
