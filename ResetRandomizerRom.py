import shutil

def ResetRom():
	try:
		shutil.rmtree("RandomizerRom")
	except:
		print("No existing folder created, nothing to remove")
	shutil.copytree("Game Files/pokecrystal","RandomizerRom")