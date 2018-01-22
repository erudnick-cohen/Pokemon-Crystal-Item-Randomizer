import shutil
import Items
import re
import os
import time

def ResetRom():
	try:
		shutil.rmtree("RandomizerRom")
	except:
		print("No existing folder created, nothing to remove")
	shutil.copytree("Game Files/pokecrystal","RandomizerRom")


def WriteLocationToRom(location, itemScriptLookup, itemTextLookup):
	print("Writing "+location.Name+" which contains "+location.item)
	
	#open the relevant file and get it as a string
	file = open("RandomizerRom/maps/"+location.FileName)
	filecode = file.read()
	
	#constuct new script that gives the new item
	#replace is technically deprecated, but this is more readable
	newcode = location.Code.replace("ITEMLINE",itemScriptLookup(location.item))
	#switch spaces to tabs.....
	newcode = newcode.replace("    ","\t")

	#find the code we need to replace
	coderegexstr = re.escape(location.Code.replace("    ","\t")).replace("ITEMLINE",".+")
	oldcode = re.findall(coderegexstr,filecode)[0]

	
	newtext = ""
	if location.Text is not None: 
		#construct a new script that updates text about the new item
		newtext = location.Text.replace("ITEMNAME",itemTextLookup(location.item))
		#switch spaces to tabs.....
		newtext = newtext.replace("    ","\t")
		
		#find the text we need to replace
		textregexstr = re.escape(location.Text.replace("    ","\t")).replace("ITEMNAME",".+")
		oldtext = re.findall(textregexstr,filecode)[0]
	else:
		oldtext = ""
	
	#make new file with the new text
	newfile = filecode.replace(oldcode,newcode).replace(oldtext,newtext)
	
	#write the new file into the files for the randomizer rom
	newfilestream = open("RandomizerRom/maps/"+location.FileName,'w')
	newfilestream.seek(0)
	newfilestream.write(newfile)
	newfilestream.truncate()
	newfilestream.flush()
	#os.fsync(newfilestream.fileno())
	newfilestream.close()

def WriteBadgeToRom(location):
	print("Writing "+location.Name+" which contains "+location.badge.Name)
	
	#open the relevant file and get it as a string
	file = open("RandomizerRom/maps/"+location.FileName)
	filecode = file.read()
	newfile = filecode
	#constuct new script that gives the new item
	#replace is technically deprecated, but this is more readable
	
	newcode = location.Code.replace("BADGELINE","ENGINE_"+location.badge.Name.replace(" ","").upper())
	#switch spaces to tabs.....
	newcode = newcode.replace("    ","\t")
	#find the code we need to replace
	coderegexstr = re.escape(location.Code.replace("    ","\t")).replace("BADGELINE",".+")
	oldcode = re.findall(coderegexstr,filecode)[0]
	newfile = filecode.replace(oldcode,newcode)
	#write the new file into the files for the randomizer rom
	newfilestream = open("RandomizerRom/maps/"+location.FileName,'w')
	newfilestream.seek(0)
	newfilestream.write(newfile)
	newfilestream.truncate()
	newfilestream.flush()
	#os.fsync(newfilestream.fileno())
	newfilestream.close()
	
	newtext = ""
	if location.Text is not None: 
		for i in location.Text:
			file = open("RandomizerRom/maps/"+i["File"])
			filecode = file.read()
			newfile = filecode
			#construct a new script that updates text about the new item
			newtext = i['Text'].replace("BADGENAME",location.badge.Name.upper())
			#switch spaces to tabs.....
			newtext = newtext.replace("    ","\t")
			#find the text we need to replace
			textregexstr = re.escape(i['Text'].replace("    ","\t")).replace("BADGENAME",".+")
			print(newtext)
			print(textregexstr)
			oldtext = re.findall(textregexstr,filecode)[0]
			newfile = newfile.replace(oldtext,newtext)
			newfilestream = open("RandomizerRom/maps/"+i["File"],'w')
			newfilestream.seek(0)
			newfilestream.write(newfile)
			newfilestream.truncate()
			newfilestream.flush()
			#os.fsync(newfilestream.fileno())
			newfilestream.close()
			
	
	#make new file with the new text
	newfile = filecode.replace(oldcode,newcode).replace(oldtext,newtext)
	
	#write the new file into the files for the randomizer rom
	newfilestream = open("RandomizerRom/maps/"+location.FileName,'w')
	newfilestream.seek(0)
	newfilestream.write(newfile)
	newfilestream.truncate()
	newfilestream.flush()
	#os.fsync(newfilestream.fileno())
	newfilestream.close()
	
	
def WriteItemLocations(locations):
	codeLookup = Items.makeItemCodeDict()
	textLookup = Items.makeItemTextDict()
	for i in locations:
		if i.isItem():
			WriteLocationToRom(i,codeLookup,textLookup)
		elif i.isGym():
			WriteBadgeToRom(i)