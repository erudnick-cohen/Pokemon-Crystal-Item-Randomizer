import re
import yaml
#open and parse the file
itemfile = open("ItemRawSearch.txt")
searchtxt = itemfile.read()
restring = 'Line [\d]+: 	(itemball|verbosegiveitem) ([a-zA-Z_]+)\n'
regex = re.compile(restring)
results = regex.findall(searchtxt)

#fill list of items in yaml format
itemlist = [];
for i in results:
	itemlist.append({'Name': i[1], 'GameName': i[1], 'output': i[0]+' '+i[1]})

stream = open('MostItems.yaml', 'w')
yaml.dump(itemlist, stream,default_flow_style=False)    # Write a YAML representation of data to 'document.yaml'.
print(yaml.dump(itemlist,default_flow_style=False))      # Output the document to the screen.