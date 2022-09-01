import json
import re
import shutil
import os

import RandomizeFunctions


def GetManualCode(labelName, lookups):
	#TrainerBugCatcherWade1.ckir_BEFORE_WADE

	labelFind = labelName.split(".ckir_")
	beforeLabel = ".ckir_"+labelFind[1]

	if beforeLabel not in lookups:
		#print("skip:", beforeLabel)
		return None

	betweenLines = lookups[beforeLabel]
	return betweenLines

def ExtractLabelledCode(file, result):

	text = open(file).read()
	regex = ".ckir_BEFORE_{0,}[A-Za-z0-9_]{1,}::(?:$|\n)"
	codeSearchBefore = re.findall(regex, text)

	regex = ".ckir_AFTER_{0,}[A-Za-z0-9_]{1,}::(?:$|\n)"
	codeSearchAfter = re.findall(regex, text)

	if len(codeSearchBefore) != len(codeSearchAfter):
		raise Exception("Invalid count")

	for before in codeSearchBefore:
		afterLine = before.replace("_BEFORE", "_AFTER").strip()
		found = [ x for x in codeSearchAfter if x.strip() == afterLine ]
		if len(found) != 1:
			raise Exception("Invalid result found")

		beforeIndex = text.index(before)
		afterIndex = text.index(afterLine)

		betweenText = text[beforeIndex+len(before):afterIndex-1]
		betweenLines = betweenText.split("\n")

		beforeClean = before.replace("::", "").strip()

		result[beforeClean] = betweenLines



def LoadManualCode(dir="Files with manual labels", result={}):
	entries = os.listdir(dir)
	for d in [ e for e in entries if os.path.isdir(dir+"/"+e)]:
		LoadManualCode(dir+"/"+d, result)

	for f in [ e for e in entries if not os.path.isdir(dir+"/"+e)]:
		print("Check:", f)
		ExtractLabelledCode(dir+"/"+f, result)

	return result


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

	lookups = LoadManualCode()

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

				labelName = j["label"]

				lines = GetManualCode(labelName, lookups)
				jumps = 0
				if lines is not None:
					for l in lines:
						# JR are less problematic and not detected in quite the same way
						# But if there is ever an issue with one of these in a new version
						# Consider changing this behaviour
						if (" ." in l or "ifequal" in l or "ifnotequal" in l) and "jr" not in l:
							print("checking label", j["label"],l)
							jumps += 1

				new_values = j["integer_values"]["new"]

				if jumps > 0:
					nullCount = [ x for x in new_values if x is None ]
					if len(nullCount) != jumps:
						raise Exception("Not handling JUMPS for +"+labelName+"!")

					iterator = 0
					while iterator < len(new_values):
						value = new_values[iterator]
						if type(value) != int:
							if value is None:
								print("problem...")
							# TODO Lookup the value in the label as refers to a label address
							usedLabels = [ x for x in addrData if x["label"].endswith(value) ]

							if len(usedLabels) == 0:
								raise Exception("Unable to find label " + value + " in sym file. ")
								iterator += 2
								continue

							addressFor = usedLabels[0]["address_range"]["begin"]
							jumpBytes = RandomizeFunctions.AddressToIntValues(addressFor)
							new_values[iterator] = jumpBytes[0]
							new_values[iterator + 1] = jumpBytes[1]
							iterator += 1

						iterator += 1

				for k in addrData:
					if 'label' in j:
						if j['label'] == k["label"]:
							actual_size = int(k["address_range"]["end"])-int(k["address_range"]["begin"])
							if len(j["integer_values"]["old"]) != actual_size or \
								len(j["integer_values"]["old"]) != len(new_values):
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