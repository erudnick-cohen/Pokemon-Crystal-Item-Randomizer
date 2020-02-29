import sys
import RandomizerGUI
import yaml
import json
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QFileDialog

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
		
	def selectRom(self):
		_translate = QtCore.QCoreApplication.translate
		file = QFileDialog.getOpenFileName()[0]
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
		yamlfile = open(settings['BasePatch'])
		yamltext = yamlfile.read()
		patches = json.loads(yamltext)
		modFileList = settings['DefaultModifiers']
		self.modList = []
		for i in modFileList:
			yamlfile = open(i)
			yamltext = yamlfile.read()
			self.modList.append(yaml.load(yamltext))
		self.updateModListView()
		self.CurentSettings.setText(_translate("MainWindow", settings['Name']))
		self.SettingsDescription.setText(_translate("MainWindow", settings['Description']))
		self.WildLevelScaling.setChecked(settings['WildLevelScalingDefault'])
		self.TrainerLevelScaling.setChecked(settings['TrainerLevelScalingDefault'])
		if('TrainerLevelBonus' in settings):
			self.TrainerLevelShiftBonus.setText(_translate("MainWindow", str(settings['TrainerLevelBonus'])))
		if('WildLevelBonus' in settings):
			self.WildLevelShiftBonus.setText(_translate("MainWindow", str(settings['WildLevelBonus'])))
		self.CurrentGoal.setText(_translate("MainWindow", settings['Goal']))

	
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