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
				addRange = []
				for k in addrData:
					if 'label' in j:
						if j['label'] == k["label"]:
							j["address_range"] = k["address_range"]
			with open(r"Patches/"+i, 'w') as f:
				json.dump(patchData, f)
			
if __name__ == "__main__":
	# execute only if run as a script
	makePatches()