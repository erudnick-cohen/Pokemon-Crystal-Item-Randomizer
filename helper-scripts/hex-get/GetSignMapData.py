import Process
import re
import os

def getMapSize(file):
	attr_file = "../pokecrystal-speedchoice/data/maps/attributes.asm"
	file_entry = file.split("/")[-1].replace(".asm", "")
	command_attr = "grep 'map_attributes "+file_entry+",' "+attr_file
	attr_result = Process.create(command_attr)
	
	if len(attr_result[1]) > 0:
		print("ase",attr_result)
		return
		
	if len(attr_result[0]) == 0:
		print("asn",attr_result, command_attr)
		return
		
	#map_attributes NewBarkTown, NEW_BARK_TOWN, $05, WEST | EAST
	file_ref = attr_result[0][0].split(",")[1].strip()
		
	size_file = "../pokecrystal-speedchoice/constants/map_constants.asm"
	
	#map_const NEW_BARK_TOWN,                               10,  9 ;  4
	
	command = "grep 'map_const "+file_ref+",' "+size_file
	result = Process.create(command)
	
	if len(result[1]) > 0:
		print("mse",result)
		return
		
	if len(result[0]) == 0:
		print("msn",result)
		return
		
	result_detail = result[0][0].split(",")
	width = result_detail[1].strip()
	height = result_detail[2].split(";")[0].strip()
	
	return (width, height)
	

def getTilesetForMap(file):
	map_detail_file = "../pokecrystal-speedchoice/data/maps/maps.asm"
	file_entry = file.split("/")[-1].replace(".asm", "")
	
	tilesetLine = "grep 'map "+file_entry+", ' "+map_detail_file 
	result = Process.create(tilesetLine)
	
	if len(result[1]) > 0:
		print(result)
		return
		
	if len(result[0]) == 0:
		print(result)
		return
	
	return result[0][0].split(" ")[2].replace(",", "")

def loadBlkFile(blk_file):
	f = open(blk_file, "rb")
	
	bs = f.read(1)
	blk_data = []
	while bs != b"":	
		for b in bs:
			hex_rep = str(hex(int(str(b))))[2:]
			blk_data.append(hex_rep)
			bs = f.read(1)
	
	f.close()
	
	return blk_data
	
class MapDetail:
	blk_file=None
	width=None
	height=None
	sign_tile = None
	sign_pos = None
	tileset = None
	address = None
	label = None
	
	def __init__(self):
		self.address = None
	
	def printObj(self):
		print(self.label, self.blk_file, self.width, self.height,
		self.sign_tile, self.sign_pos, self.tileset, self.address)
	

def getAssociatedMapData(label_base, file):

	blk_file = file.replace("asm", "blk")
	
	# Currently, do not process files not found
	# Currently applies to DeptStore which uses a shared map 
	# for Goldenrod & Celadon
	if not os.path.isfile(blk_file):
		return None
	
	
	findViaTextLabel = "grep -B1 'jumptext "+label_base+"' "+file
	via_label = Process.create(findViaTextLabel)
	
	if len(via_label[1]) > 0:
		print("gamv:error")
		print(via_label)
		return
		
	if len(via_label[0]) == 0:
		print("gamv:0")
		print(via_label, findViaTextLabel)
		return
		
	label_call = via_label[0][0].replace(":","")


	findMapLocation = "grep 'BGEVENT_READ, "+label_call+"' "+file
	result = Process.create(findMapLocation)
	
	if len(result[1]) > 0:
		print("gamd:error")
		print(result)
		return
		
	if len(result[0]) == 0:
		print("gamd:0")
		print(result, findMapLocation)
		return
		
	splitDetails = re.split(" +",result[0][0])
	
	x_co = int(splitDetails[1].replace(",",""))
	y_co = int(splitDetails[2].replace(",",""))
	
	tileset_name = getTilesetForMap(file)	
	
	size = getMapSize(file)
	if size is None:
		print("Size not found")
		return
		
	width = int(size[0])
	height = int(size[1])	
	
	blk_file = file.replace("asm", "blk")
	
	blk_data = loadBlkFile(blk_file)
	#print("result_blk", len(blk_data),blk_data)
	
	if x_co % 2 == 0:
		x_blk = int(x_co/2)
	else:
		x_blk = int((x_co - 1)/2)
		
	if y_co % 2 == 0:
		y_blk = int(y_co/2)
	else:
		y_blk = int((y_co - 1)/2)
	
	blk_pos = (y_blk*width)+x_blk
	t_detail = blk_data[blk_pos]
	#print(t_detail, blk_pos, x_co, y_co, height, width, blk_data.index('45'))
	
	# At this stage, you have what the original tile was
	# Which can be determined from tileset and tile ID value (in t_detail)
	# Lookup table to determine what to move it to (same tile, no sign)
	
	# Now need to compile and work out the code-position
	
	#blk_d_file = open(blk_file, "r+b")
	#blk_d_file.seek(blk_pos)
	#blk_d_file.write(bytes(1))
	#blk_d_file.close()
	
	detail = MapDetail()
	detail.label = label_base
	detail.blk_file = blk_file
	detail.width = width
	detail.height = height
	detail.sign_tile = t_detail
	detail.sign_pos = blk_pos
	detail.tileset = tileset_name
	
	detail.printObj()
	
	return detail	




#dir = "../pokecrystal-speedchoice/maps"
#detail = getAssociatedMapData("NewBarkTownSign", dir+"/NewBarkTown.asm")
	