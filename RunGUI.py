import shutil
import sys

import FileOperations
import LoadLocationData
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

	def updateGUIFromSettings(self, settings):
		_translate = QtCore.QCoreApplication.translate

		self.updateModListView()
		self.CurentSettings.setText(_translate("MainWindow", settings['Name']))
		self.SettingsDescription.setText(_translate("MainWindow", settings['Description']))
		self.CurrentGoal.setText(_translate("MainWindow", settings['Goal']))
		if "SilverBadgeUnlockCount" in self.item_rando.settings:
			_translate = QtCore.QCoreApplication.translate
			self.BadgesNeeded.setText(_translate("MainWindow",
												 "Change # of badges\n to unlock Mt. Silver? \n(Currently " + str(
													 self.item_rando.settings["SilverBadgeUnlockCount"]) + ")"))
			QtGui.QGuiApplication.processEvents()
		else:
			self.BadgesNeeded.setText(_translate("MainWindow",
												 "Change # of badges\n to unlock Mt. Silver? \n(Currently " + str(
													 16) + ")"))

		if 'HintLevel' in self.item_rando.settings:
			self.HintButton.setText(_translate("MainWindow",
											   "Set Hints (LV: " + str(self.item_rando.settings['HintLevel']) + " N" + str(
												   self.item_rando.settings['nHints']) + ")"))
			QtGui.QGuiApplication.processEvents()
		else:
			self.HintButton.setText(_translate("MainWindow", "Set Hints (off)"))
			QtGui.QGuiApplication.processEvents()

		if "Plando" in self.item_rando.settings:
			self.TurnOffPlando.setEnabled(True)
		else:
			self.DeactivatePlando()

	def __init__(self, parent=None):
		super(RunWindow, self).__init__(parent)
		self.setupUi(self)
		self.item_rando = ItemRandomiser(GUI=self)

		_translate = QtCore.QCoreApplication.translate
		yamlfile = open('RandomizerConfig.yml',encoding='utf-8')
		yamltext = yaml.load(yamlfile,Loader=yaml.FullLoader)

		self.item_rando.loadSettings(yamltext['DefaultSettings'])
		self.updateGUIFromSettings(self.item_rando.settings)

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

		#self.PlandoMode = False
		#self.PlandoData = {}

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
				DisplayMessage('Please select previous install directory to import custom settings', "First Run", "INFO", self)
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


	def runGUIRandomiser(self, requiredMD5=None):
		_translate = QtCore.QCoreApplication.translate

		self.Randomize.setEnabled(False)
		self.Randomize.setText(_translate("MainWindow", "Randomizing"))

		gui_flags = {
			"RaceMode":self.RaceModeRadioButton.isChecked(),
			"Spoiler":self.SpoilerOutputRadioButton.isChecked()
					 }

		gui_seed = self.SeedInput.text()
		if gui_seed == "":
			gui_seed = None

		result = self.item_rando.runRandomizer(seed=gui_seed, in_file=self.romPath, run_flags=gui_flags, requiredMD5=None)

		self.Randomize.setEnabled(True)
		self.Randomize.setText(_translate("MainWindow", "Randomize Rom"))

	def pressRunRandomiser(self):
		self.runGUIRandomiser()

	def SetBadgeForSilver(self):
		(nBadge, ok2) = QInputDialog.getInt(self,"How many badges will Mt. Silver unlock with?","How many badges will Mt. Silver unlock with?")
		if nBadge <= 16 and ok2:
			if nBadge <= 0:
				message = "You must choose a number of badges greater than 1! Setting badge requirement to 1."
				DisplayMessage(message, None, "ERROR", self)
			self.item_rando.settings["SilverBadgeUnlockCount"] = nBadge
			_translate = QtCore.QCoreApplication.translate
			self.BadgesNeeded.setText(_translate("MainWindow", "Change # of badges\n to unlock Mt. Silver? \n(Currently "+str(nBadge)+")"))
			QtGui.QGuiApplication.processEvents()
		elif ok2:
			message = "There are only 16 badges in Pokemon Crystal! You can't require more, or your game will not be completable!"
			DisplayMessage(message, None, "ERROR", self)

	def AddBonusItem(self):
		(addedItem, ok1) = QInputDialog.getItem(self, "Select item you wish to add to the pool", "Select item you wish to add to the pool", self.itemsList, 0, False)
		if ok1:
			(nAdded, ok2) = QInputDialog.getInt(self,"Add how many?","Add how many?")
		if not ('BonusItems' in self.item_rando.settings):
			self.item_rando.settings['BonusItems'] = []
		if ok1 and ok2:
			for i in range(0,nAdded):
				self.item_rando.settings['BonusItems'].append(addedItem)

	def RemoveBonusItem(self):
		if 'BonusItems' in self.item_rando.settings and len(self.item_rando.settings['BonusItems']) > 0:
			self.item_rando.settings['BonusItems'] = []
			if ('BonusItems' in self.item_rando.settings):
				(addedItem, ok1) = QInputDialog.getItem(self, r"View/Remove Items in pool", "Select any item you wish to remove, or cancel to remove nothing",
														self.item_rando.settings['BonusItems'], 0, False)
			if ok1:
				(nAdded, ok2) = QInputDialog.getInt(self,"Remove how many?","Remove how many?")
			if not ('BonusItems' in self.item_rando.settings):
				self.item_rando.settings['BonusItems'] = []
			if ok1 and ok2:
				for i in range(0,nAdded):
					if addedItem in self.item_rando.settings['BonusItems']:
						self.item_rando.settings['BonusItems'].remove(addedItem)

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
			self.item_rando.loadSettings(file)
			self.updateGUIFromSettings(self.item_rando.settings)

	def loadPack(self):
		packfiles = QFileDialog.getOpenFileNames(directory = 'Packs')[0]
		if len(packfiles) > 0:
			currentModifierFiles = [obj["fileName"] for obj in self.item_rando.modList]
			modifiersToLoad = []
			for packfile in packfiles:
				yamlfile = open(packfile)
				yamltext = yamlfile.read()

				loadedYaml = yaml.load(yamltext, Loader=yaml.FullLoader)

				if 'Modifiers' in loadedYaml:
					self.item_rando.loadModifiers(loadedYaml['Modifiers'], reset=False)

			for mod in modifiersToLoad:
				if os.path.isfile(mod):
					yamlfile = open(mod)
					yamltext = yamlfile.read()
					loadedYaml = yaml.load(yamltext, Loader=yaml.FullLoader)
					self.item_rando.modList.append(loadedYaml)
					self.item_rando.modList[-1]['fileName'] = self.item_rando.makeFileNameSafe(mod)
				else:
					message = 'Pack Modifier not found:' + "\n" + mod
					DisplayMessage(message, None, "ERROR", self)



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
				currentModifierNames = [obj["Name"] for obj in self.item_rando.modList]

				if loadedYaml["Name"] in currentModifierNames:
					if len(modfiles) == 1:
						message = loadedYaml["Name"] + " is already loaded!"
						DisplayMessage(message, None, "ERROR", self)
					continue

				is_incompatible = False
				if "IncompatibleWith" in loadedYaml:
					for incomp in loadedYaml["IncompatibleWith"]:
						if incomp in currentModifierNames:
							is_incompatible = True
							message = loadedYaml["Name"] + "/" + incomp
							DisplayMessage(message, None, "ERROR", self)

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
					self.item_rando.modList.append(loadedYaml)
					self.item_rando.modList[-1]['fileName'] = self.item_rando.makeFileNameSafe(modfile)

					if "VariablesSet" in loadedYaml:
						for variable in loadedYaml["VariablesSet"]:
							variablesToSet.append(variable)


			if len(potentiallyMiss) > 0:
				currentModifierNames = [obj["Name"] for obj in self.item_rando.modList]
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
						self.item_rando.modList.append(missYaml)
						self.item_rando.modList[-1]['fileName'] = self.item_rando.makeFileNameSafe(miss)
					else:
						message = missYaml["Name"] + ":" + '/'.join(options)
						DisplayMessage(message, None, "ERROR", self)

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
			self.item_rando.modList.pop(row)
			self.updateModListView()

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

	def saveSettings(self):
		fName = QFileDialog.getSaveFileName(directory = 'Modes/Custom')[0]
		fName = self.item_rando.makeFileNameSafe(fName)
		if(fName != ''):
			filename = fName if fName.endswith(".yml") else fName + ".yml"
			self.item_rando.settings['DefaultModifiers'] = []
			for i in self.item_rando.modList:
				self.item_rando.settings['DefaultModifiers'].append(i['fileName'])

			if self.item_rando.PlandoMode:
				self.item_rando.settings["Plando"] = {}
				for key in self.item_rando.PlandoData.keys():
					self.item_rando.settings["Plando"][key] = self.PlandoData[key]

			if "ModeVariables" not in self.item_rando.settings:
				self.item_rando.settings["ModeVariables"] = {}
			for variable_name in self.modeVariables:
				self.item_rando.settings["ModeVariables"][variable_name] = self.modeVariables[variable_name]


			with open(filename, 'w',encoding='utf-8') as f:
				yaml.dump(self.item_rando.settings, f, default_flow_style=False)

			self.item_rando.loadSettings(filename)
			self.updateGUIFromSettings(self.item_rando.settings)
				
	def SetUpPlando(self):
		DisplayMessage('Select a log file (which need not specify every item allocation) to use as basis for plandomizer.\n'
					   ' NOTE: We are not reponsible for any lost friendships due to use of plandomizer mode',
					   'Plandomizer Mode',"INFO", self)
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
		self.item_rando.ResetPlando()
		self.TurnOffPlando.setEnabled(False)

	def updateModListView(self):
		self.modifierList.clear()
		for i in self.item_rando.modList:
			self.modifierList.addItem(i['Name'])

	def updateModifierDescription(self):
		_translate = QtCore.QCoreApplication.translate
		row = self.modifierList.currentRow()
		if(row != -1 and row < len(self.item_rando.modList)):
			self.ModifierDescription.setText(_translate("MainWindow", self.item_rando.modList[row]['Description']))
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
		DisplayMessage(
			'Select the mode which should be loaded by default when you open up the randomizer',
			'Choose default settings', "INFO", self)
		defaultFile = QFileDialog.getOpenFileName(directory = 'Modes')[0]
		if(defaultFile != ''):
			self.WriteRandomizerConfig(defaultFile)
		else:
			DisplayMessage("A file was not selected", None, "ERROR", self)

	def LoadRaceModeSettingsUI(self):
		success = QInputDialog.getText(self, "Race Mode", "Input Race Mode Here")
		if success[1]:
			inputString = success[0]
		else:
			return

		raceModeSettings = self.item_rando.LoadRaceModeSettings(raceString=inputString)

		seed = raceModeSettings[2]
		md5 = raceModeSettings[3]

		self.SpoilerOutputRadioButton.setChecked(False)
		self.RaceModeRadioButton.setChecked(False)
		self.NoOutputRadioButton.setChecked(True)

		self.SeedInput.setText(seed)
		if self.romPath is None or len(self.romPath) == 0:
			self.selectRom()
		self.runGUIRandomiser(requiredMD5=md5)
			
	def ProcessHintSettings(self):
		_translate = QtCore.QCoreApplication.translate
		(option, ok1) = QInputDialog.getItem(self,"What hint level should be used?","What hint level should be used?",['0. No Hints', '1. Gym Signs', '2. Max one per location', '3. More hints types', '4. Hint useless items','5. Many hints everywhere', '6. Hints might be more useless than on 4'])
		if ok1:
			(nHints, ok2) = QInputDialog.getInt(self,"How many different hints?","How many different hints?")
			if ok2 and int(option[0]) > 0:
				self.item_rando.settings['HintLevel'] = int(option[0])
				self.item_rando.settings['nHints'] = nHints
				self.HintButton.setText(_translate("MainWindow", "Set Hints (LV: "+str(self.item_rando.settings['HintLevel'])+" N"+str(self.item_rando.settings['nHints'])+")"))
				QtGui.QGuiApplication.processEvents()
		else:
			self.item_rando.settings['HintLevel'] = 0
			self.item_rando.settings['nHints'] = 0
			
			self.HintButton.setText(_translate("MainWindow", "Set Hints (off)"))
			QtGui.QGuiApplication.processEvents()

	def SetCurrentVariables(self):
		variablesToSet = []
		loadedVariableNames = []

		for variable in self.modeVariables.keys():
			variablesToSet.append({variable:self.modeVariables[variable]})
			loadedVariableNames.append(variable)


		for mod in self.item_rando.modList:
			if "VariablesSet" in mod:
				for variable in mod["VariablesSet"]:
					variableName = list(variable.keys())[0]
					if variableName not in loadedVariableNames:
						variablesToSet.append(variable)

		if len(variablesToSet) == 0:
			DisplayMessage(
				'No variables to set.',
				'Variables', "INFO", self)
		else:
			for variable in variablesToSet:
				self.PromptForVariable(variable)

		return


def DisplayMessage(message, messageName, type="INFO", GUI=None):
	if GUI is not None:
		if type == "INFO":
			QtWidgets.QMessageBox.about(GUI, messageName, message)
		elif type == "ERROR":
			error_dialog = QtWidgets.QErrorMessage()
			error_dialog.showMessage(message)
			error_dialog.exec_()
	else:
		file = sys.stdout
		if type == "ERROR":
			file = sys.stderr

		print(message, file=file)

class ItemRandomiser():
	def __init__(self, GUI):
		self.GUI = GUI
		self.modeVariables = {}
		self.modList = []
		self.settings = {}
		return

	def ResetPlando(self):
		self.PlandoData = {}
		self.PlandoMode = False

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

		#yamlfile = open(settings['BasePatch'],encoding='utf-8')
		#yamltext = yamlfile.read()
		#patches = json.loads(yamltext)

		modFileList = settings['DefaultModifiers']
		self.loadModifiers(modFileList)

		if "ModeVariables" in self.settings:
			for variable in self.settings["ModeVariables"].keys():
				self.modeVariables[variable] = self.settings["ModeVariables"][variable]

		if "Plando" in self.settings:
			newSpoiler = OrderedDict()
			for key in self.settings["Plando"]:
				newSpoiler[key] = self.settings["Plando"][key]
			self.PlandoData = newSpoiler
			del self.settings['Plando']
			self.PlandoMode = True
		else:
			self.ResetPlando()


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
				message = 'Modifier not found:' + "\n" + i
				DisplayMessage(message, None, "ERROR", self.GUI)
	
	def checkForConflictingMods(self):
		conflicts = []
		seenMods = []
		repeatedMods = []
		modNames = [mod['Name'] for mod in self.modList]

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
						potentialConflicts.append(mod['Name'] + item)
					else:
						withoutRequired = True

				if not withoutRequired:
					conflicts.extend(potentialConflicts)

		if len(conflicts) > 0:
			message = "Mod config error with: " + ','.join(conflicts)
			DisplayMessage(message, None, "ERROR", self.GUI)
			return True

		if len(repeatedMods) > 0:
			message = "Mod repeated error with: " + ','.join([x["Name"] for x in repeatedMods])
			DisplayMessage(message, None, "ERROR", self.GUI)
			return True

		return False

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

		return hashlib.md5(new_hash.encode()).hexdigest()

	def yamlSortFunction(self, y):
		return y["Name"]

	def GetSettingsMD5(self):
		mods = self.modList.copy()
		mods.sort(key=self.yamlSortFunction)
		full_string = ";"
		for mod in mods:
			full_string += mod["Name"] + ";"

		return hashlib.md5(full_string.encode()).hexdigest()

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


	def LoadRaceModeSettings(self, raceString=None):
		inputString = raceString
		hex_bytes = bytes.fromhex(inputString)
		decompressed = zlib.decompress(hex_bytes)
		d_string = decompressed.decode("utf8")

		data = d_string.split("#")
		if len(data) != 4:
			raise Exception("Invalid race mode string")

		mode = data[0]
		mode_hash = data[1]
		#seed = data[2]
		#md5 = data[3]

		#race_string = seed["Mode"] + "#" + seed["ModeHash"] + "#" + seed["Seed"]

		self.loadSettings(mode)
		my_mode_hash = self.GetModeHash()

		if my_mode_hash != mode_hash:
			print("Mode hash does not match!")
			raise Exception("Mode doesn't match: ",mode)

		return data

	def GetRaceModeValue(self, seed):
		# Contains Mode, RNG Seed and ModeHash
		race_string = "#".join([seed["Mode"], seed["ModeHash"], seed["Seed"], seed["RomMD5"]])
		hexstring = zlib.compress(bytes(race_string, "utf8")).hex()
		#print(hexstring)
		return hexstring

	def runRandomizer(self, seed=None, out_dir=None, in_file=None, out_file=None, requiredMD5=None, run_flags=None):
		dataHash = LoadLocationData.GetDataHash()

		if run_flags is None:
			run_flags = {}

		if dataHash != Version.GetExpectedDataHash():
			print("dataHash = ", dataHash)
			message = "Map Data invalid. Try reinstalling. Continue at your own risk."
			DisplayMessage(message, None, "ERROR", self.GUI)

		conflict = self.checkForConflictingMods()
		if conflict:
			return

		os.environ['PYTHONHASHSEED'] = '0'  # this needs to be reproducible! so this can't be random!
		if seed is None:
			rngSeed = str(time.time())
			random.seed(rngSeed)
			rngSeed = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
		else:
			rngSeed = seed

		rngSeedBytes = rngSeed.encode('utf-8')
		rSeed = int(hashlib.md5(rngSeedBytes).hexdigest(), 16)
		print('numeric seed is: ' + str(rSeed))
		random.seed(rSeed)
		_translate = QtCore.QCoreApplication.translate
		yamlfile = open(self.settings['BasePatch'])
		yamltext = yamlfile.read()
		patches = json.loads(yamltext)
		modFileList = self.settings['DefaultModifiers']
		try:
			tlv = 0
			wlv = 0
			QtGui.QGuiApplication.processEvents()
			validFileName = False

			if out_file is not None:
				validFileName = True
				file = out_file

			base_dir = out_dir

			if base_dir is None:
				base_dir = ""

			if base_dir == "." or base_dir == "":
				for i in range(0, len(in_file.split("/")) - 1):
					if base_dir != "":
						base_dir += "/"
					base_dir += in_file.split("/")[i]


			exits = 0
			stop_after = 1
			while not validFileName:
				file = QFileDialog.getSaveFileName(directory=base_dir)[0]
				if file != '':
					validFileName = True
				else:
					DisplayMessage('Please name and save the generated rom...', "File",
								   "INFO", self.GUI)
					exits += 1
					if exits > stop_after:
						break
			randomizedFileName = file

			if not validFileName:
				DisplayMessage('3 Failed filenames, cancelling', "Error",
							   "INFO", self.GUI)
				return

			if not randomizedFileName.endswith(".gbc"):
				randomizedFileName += ".gbc"
			if 'HintLevel' in self.settings:
				HINT_LEVEL = self.settings['HintLevel']
				MAX_HINTS = self.settings['nHints']
			else:
				HINT_LEVEL = 0
				MAX_HINTS = 0
			HintOptions = RandomizeFunctions.ConvertHintLevelToFlags(HINT_LEVEL, MaxHints=MAX_HINTS)

			settings_md5 = self.GetSettingsMD5()
			#print(settings_md5)

			f = open(in_file, 'rb')
			romMD5 = str(hashlib.md5(f.read()).hexdigest())
			f.close()

			#print("reqMD5", requiredMD5)
			if requiredMD5 is not None:
				if romMD5 != requiredMD5:
					raise Exception("Invalid rom MD5")

			copyfile(in_file, randomizedFileName)
			with open('SAVEDSEEDLOG.log', 'a+') as f:
				f.write(rngSeed + "\n")

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
				DisplayMessage("Incorrect rom version provided!", None, "ERROR", self.GUI)
				raise Exception("Invalid ROM")

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

			isRaceMode = run_flags["RaceMode"] if "RaceMode" in run_flags else False
			isSpoilerOutput = run_flags["Spoiler"] if "Spoiler" in run_flags else False

			if isRaceMode or isSpoilerOutput:
				raceMode = {}
				raceMode['Seed'] = rngSeed
				raceMode["Mode"] = self.SettingsFilename
				raceMode["ModeHash"] = self.GetModeHash()
				raceMode["RomMD5"] = romMD5

				raceModeString = self.GetRaceModeValue(raceMode)

				if isRaceMode:
					self.LoadRaceModeSettings(raceString=raceModeString)

					#cb = QApplication.clipboard()
					#cb.setText(raceModeString, mode=cb.Clipboard)

					#DisplayMessage('Copied race output to clipboard', "Race Output",
					#			   "INFO", self.GUI)

					with open(randomizedFileName + '_SPOILER.txt', 'w') as f:
						f.write(raceModeString)

			if isSpoilerOutput:
				outputSpoiler = {}
				outputSpoiler['RNG Seed'] = rngSeed
				outputSpoiler['Solution'] = resultDict["Spoiler"]
				outputSpoiler['Useless Stuff'] = resultDict["Trash"]
				if "RandomizedExtra" in resultDict:
					outputSpoiler["Xtra Stuff"] = resultDict["RandomizedExtra"]

				if "UpgradedItems" in resultDict:
					outputSpoiler["Xtra Upgrades"] = resultDict["UpgradedItems"]

				outputSpoiler["CIR Version"] = Version.GetItemRandoVersion()
				outputSpoiler["Mode"] = self.settings['Name']
				outputSpoiler["ModifierHash"] = self.GetSettingsMD5()
				outputSpoiler["Modifiers"] = self.GetActiveModifiers()
				if hasWarning:
					outputSpoiler["Warnings"] = resultDict["Warnings"]

				if raceModeString is not None:
					outputSpoiler["Race"] = raceModeString

				with open(randomizedFileName + '_SPOILER.txt', 'w') as f:
					yaml.dump(outputSpoiler, f, default_flow_style=False)

			successMessage = "Successfully randomized rom"
			successBoxName = "Success"

			# TODO
			# Change warning handling and result to dictionary for easier readability and extension
			# Handle E4 not possible in the same way

			if hasWarning:
				successMessage = "Sucessfully generated rom with warnings"
				successBoxName = "Success..."

			DisplayMessage(successMessage, successBoxName,
						   "INFO", self.GUI)

			_translate = QtCore.QCoreApplication.translate
		except:
			message = ''.join(traceback.format_exc())
			DisplayMessage(message, None, "ERROR", self.GUI)


def runCLI(arguments):
	arg_error = False

	if "input" not in arguments:
		print("No --input or -i provided.", file=sys.stderr)
		arg_error = True

	if "output" not in arguments:
		print("No --output or -o provided.", file=sys.stderr)
		arg_error = True

	if "mode" not in arguments:
		print("No --mode or -m provided.", file=sys.stderr)
		arg_error = True

	if "race" in arguments and "log" in arguments:
		print("Cannot use race mode and spoiler log.", file=sys.stderr)
		arg_error = True

	use_seed = None
	if "seed" in arguments:
		use_seed = arguments["seed"]

	if "race" in arguments :
		if type(arguments["race"]) is not bool:
			race_mode = arguments["race"]
		else:
			race_mode = None
	else:
		race_mode = None

	if arg_error:
		return

	#app = QApplication(sys.argv)
	#form = RunWindow()

	# Need to load settings, etc.

	item_rando = ItemRandomiser(GUI=None)

	if race_mode is None:
		settingsFile = arguments["mode"]
		item_rando.loadSettings(settingsFile)
		rom_md5 = None
	else:
		data = item_rando.LoadRaceModeSettings(raceString=race_mode)
		use_seed = data[2]
		rom_md5 = data[3]


	flags = {"Spoiler" : "log" in arguments, "RaceMode": "race" in arguments}

	item_rando.runRandomizer(in_file=arguments["input"], out_file=arguments["output"],
							 seed=use_seed, run_flags=flags, requiredMD5=rom_md5)


	#form.romPath = arguments["input"]
	#form.runRandomizer(cli=True, outputFile=arguments["output"])

	if arg_error:
		return

def convertArgument(argument):
	if argument == "i":
		return "input"

	if argument == "o":
		return "output"

	if argument == "m":
		return "mode"

	if argument == "s":
		return "seed"

	if argument == "l":
		return "log"

	if argument == "r":
		return "race"

	return argument

def parseArguments():
	parsed_args = {}
	read_next_arg = 0
	for argument in sys.argv:

		if os.getcwd() in argument:
			continue

		if read_next_arg > 0 and argument.startswith("-"):
			arg_name = convertArgument(arg_name)
			parsed_args[arg_name] = True

		if argument.startswith("--"):
			arg_name = argument[2:]
			read_next_arg = 2
			pass
		elif argument.startswith("-"):
			arg_name = argument[1:]
			read_next_arg = 1
			pass
		elif read_next_arg > 0:
			if read_next_arg == 1:
				arg_name = convertArgument(arg_name)

			parsed_args[arg_name] = argument

			read_next_arg = 0
		else:
			parsed_args[argument] = True

	return parsed_args

def main():
	arguments = parseArguments()
	if "cli" in arguments:
		runCLI(arguments)
		return

	os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
	app = QApplication(sys.argv)
	form = RunWindow()
	form.show()
	app.exec_()

if __name__ == '__main__':
	main()
