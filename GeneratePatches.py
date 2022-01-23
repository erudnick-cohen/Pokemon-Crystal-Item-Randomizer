import json
import shutil
import os

def makePatches():
	try:
		shutil.rmtree("Patches")
	except:
		print("No existing folder created, nothing to remove")
	os.mkdir("Patches")
	

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
				addRange = []
				for k in addrData:
					if 'label' in j:
						if j['label'] == k["label"]:
							actual_size = int(k["address_range"]["end"])-int(k["address_range"]["begin"])
							if len(j["integer_values"]["old"]) != actual_size or \
								len(j["integer_values"]["old"]) != len(j["integer_values"]["new"]):
								print("Patch is the wrong expected size:",j["description"])

								raise Exception("Wrong size patch")

							j["address_range"]["begin"] = k["address_range"]["begin"]
							j["address_range"]["end"] = k["address_range"]["end"]
							count += 1

				if "label" not in j:
					print("Unable to find label-",i )
				elif count != 1:
					print("Did not find label::", j["label"])
					raise Exception("Label not found")





			with open(r"Patches/"+i, 'w') as f:
				json.dump(patchData, f)
			
if __name__ == "__main__":
	# execute only if run as a script
	makePatches()