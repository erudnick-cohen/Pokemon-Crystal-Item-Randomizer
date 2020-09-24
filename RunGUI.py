import sys
import RandomizerGUI
import time
import yaml
import json
import random
import string
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QFileDialog
import RunCustomRandomizationAssumedFill as RunCustomRandomization
from shutil import copyfile

class RunWindow(QtWidgets.QMainWindow, RandomizerGUI.Ui_MainWindow):
	def __init__(self, parent=None):
		super(RunWindow, self).__init__(parent)
		self.setupUi(self)
		_translate = QtCore.QCoreApplication.translate
		self.loadSettings('Modes/Standard.yml')
		self.modifierList.itemSelectionChanged.connect(self.updateModifierDescription)
		self.ChooseSettings.clicked.connect(self.selectLogicSettings)
		self.LoadModifier.clicked.connect(self.loadModifier)
		self.DeleteModifier.clicked.connect(self.deleteModifier)
		self.romPath = ''
		self.SelectRomFile.clicked.connect(self.selectRom)
		self.Randomize.setEnabled(False)
		self.Randomize.setText(_translate("MainWindow", "No Rom Loaded!"))
		self.Randomize.clicked.connect(self.runRandomizer)
		self.SaveSettings.clicked.connect(self.saveSettings)

	def runRandomizer(self):
		rngSeed = str(time.time())
		random.seed(rngSeed)
		rngSeed = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
		if(self.SeedInput.text() != ''):
			rngSeed = self.SeedInput.text()
		random.seed(rngSeed)
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
			QtWidgets.QMessageBox.about(self, 'Message', 'Please select the name for the file')
			validFileName = False
			while not validFileName:
				file = QFileDialog.getSaveFileName(directory = '.')[0]
				if file != '':
					validFileName = True
				else:
					QtWidgets.QMessageBox.about(self, 'ERROR', 'Please name and save the generated rom...')
			randomizedFileName = file
			copyfile(self.romPath, randomizedFileName+'.gbc')
			if('ProgressItems' in self.settings):
				result = RunCustomRandomization.randomizeRom(randomizedFileName+'.gbc',self.settings['Goal'], self.settings['FlagsSet'],patches, banList = self.settings['BannedLocations'], allowList = self.settings['AllowedLocations'], modifiers = self.modList,adjustTrainerLevels = False, adjustRegularWildLevels = False, adjustSpecialWildLevels = False, trainerLVBoost = tlv, wildLVBoost=wlv, requiredItems = self.settings['ProgressItems'])
			else:
				result = RunCustomRandomization.randomizeRom(randomizedFileName+'.gbc',self.settings['Goal'], self.settings['FlagsSet'],patches, banList = self.settings['BannedLocations'], allowList = self.settings['AllowedLocations'], modifiers = self.modList,adjustTrainerLevels = False, adjustRegularWildLevels = False, adjustSpecialWildLevels = False, trainerLVBoost = tlv, wildLVBoost=wlv)
			self.Randomize.setEnabled(True)
			if(self.OutputSpoiler.isChecked()):
				outputSpoiler = {}
				outputSpoiler['RNG Seed'] = rngSeed
				outputSpoiler['Solution'] = result[1]
				with open(randomizedFileName+'_SPOILER.txt', 'w') as f:
					yaml.dump(outputSpoiler, f, default_flow_style=False)
			self.Randomize.setText(_translate("MainWindow", "Randomize Rom"))
			QtWidgets.QMessageBox.about(self, 'Success', 'Sucessfully randomized rom')
			_translate = QtCore.QCoreApplication.translate



		except ValueError:
			error_dialog = QtWidgets.QErrorMessage()
			error_dialog.showMessage('Level bonus must be an integer')
			error_dialog.exec_()

		
	def selectRom(self):
		_translate = QtCore.QCoreApplication.translate
		file = QFileDialog.getOpenFileName(directory = '.')[0]
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

	def loadModifier(self):
		modfile = QFileDialog.getOpenFileName(directory = 'Modifiers')[0]
		if modfile != '':
			yamlfile = open(modfile)
			yamltext = yamlfile.read()
			self.modList.append(yaml.load(yamltext))
			self.modList[-1]['fileName'] = modfile
			self.updateModListView()

	def deleteModifier(self):
		row = self.modifierList.currentRow()
		if(row != -1):
			self.modifierList.setCurrentRow(-1)
			self.modList.pop(row)
			self.updateModListView()



	def loadSettings(self, settingsFile):
		_translate = QtCore.QCoreApplication.translate
		yamlfile = open(settingsFile)
		yamltext = yamlfile.read()
		settings = yaml.load(yamltext)
		self.settings = settings
		yamlfile = open(settings['BasePatch'])
		yamltext = yamlfile.read()
		patches = json.loads(yamltext)
		modFileList = settings['DefaultModifiers']
		self.modList = []
		for i in modFileList:
			yamlfile = open(i)
			yamltext = yamlfile.read()
			self.modList.append(yaml.load(yamltext))
			self.modList[-1]['fileName'] = i
		self.updateModListView()
		self.CurentSettings.setText(_translate("MainWindow", settings['Name']))
		self.SettingsDescription.setText(_translate("MainWindow", settings['Description']))
		self.CurrentGoal.setText(_translate("MainWindow", settings['Goal']))

	def saveSettings(self):
		fName = QFileDialog.getSaveFileName(directory = 'Modes')[0]
		if(fName != ''):
			self.settings['DefaultModifiers'] = []
			for i in self.modList:
				self.settings['DefaultModifiers'].append(i['fileName'])
			with open(fName+'.yml', 'w') as f:
				yaml.dump(self.settings, f, default_flow_style=False)

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
def main():
	app = QApplication(sys.argv)
	form = RunWindow()
	form.show()
	app.exec_()

if __name__ == '__main__':
	main()