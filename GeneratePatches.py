import json
import mmap
import shutil
import os

def makePatches():
	try:
		shutil.rmtree("Patches")
	except:
		print("No existing folder created, nothing to remove")
	os.mkdir("Patches")

	# Use rom map
	use_rom = True
	romMap = None
	if use_rom:
		romPath = "RandomizerRom/crystal-speedchoice.gbc"
		f = open(romPath, 'r+b')
		romMap = mmap.mmap(f.fileno(), 0)
	

	#load the json data so that we know what the addresses actually SHOULD be
	with open('crystal-speedchoice-label-details.json',encoding='utf-8') as f:
		addrText = f.read()
		addrData = json.loads(addrText)

	for root, dir, files in os.walk("Patches Base//"):
		for i in files:
			print("File: "+i)
			with open("Patches Base//"+i,encoding='utf-8') as f:
				patchText = f.read()
				patchData = json.loads(patchText)

			for j in patchData:
				#find the relevant address data
				count = 0
				comp_data = []
				for k in addrData:
					if 'label' in j:
						if j['label'] == k["label"]:
							actual_size = int(k["address_range"]["end"])-int(k["address_range"]["begin"])
							if len(j["integer_values"]["old"]) != actual_size or \
								len(j["integer_values"]["old"]) != len(j["integer_values"]["new"]):
								print("Patch is the wrong expected size:",j["description"])
								print("Patch is the wrong expected size vs:", k)

								raise Exception("Wrong size patch")

							j["address_range"]["begin"] = k["address_range"]["begin"]
							j["address_range"]["end"] = k["address_range"]["end"]

							comp_data = [ int(x) for x in romMap[k["address_range"]["begin"]:k["address_range"]["end"]] ]
							count += 1

				if "label" not in j:
					print("Unable to find label-",i, j )
				elif count != 1:
					print("Did not find label::", j["label"])
					raise Exception("Label not found")

				if len(j["integer_values"]["new"]) == len([ c for c in j["integer_values"]["new"] if c == 0])\
						and len(j["integer_values"]["old"]) == len([ c for c in j["integer_values"]["old"] if c == 0]):
					j["integer_values"]["new"] = comp_data

			# Old values should match rom data
			# This doesn't want the newly compiled rom WITH the patches in in particular?
			# Choatix: Note that my tests will fail this at present again...

			with open(r"Patches/"+i, 'w') as f:
				json.dump(patchData, f, indent=4)
			
if __name__ == "__main__":
	# execute only if run as a script
	makePatches()