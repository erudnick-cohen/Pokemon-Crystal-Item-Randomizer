import sys
import hexget
import Process

default_file1="base.gbc"
default_file2="sign.gbc"

def printBytes(bs,type):
 return_string=""
 for b in bs:
  if type == "hex":
   hex_rep = str(hex(int(str(b))))[2:]
   hex_rep = "$"+ hex_rep +" "
   return_string+=hex_rep
  elif type == "int":
   int_rep =  str(int(str(b)))+" "
   return_string+=int_rep

 return return_string[0:-1]


class DiffResult:
 oldBytes=[]
 newBytes=[]
 addressFrom=None
 addressTo=None
 
 def __init__(self,old,new,From,To):
  self.oldBytes=old
  self.newBytes=new
  self.addressFrom=From
  self.addressTo=To

def processFile(file1,file2,shouldPrint=False):
	original=file1
	f = open(original,"rb")

	f_check = open(file2,"rb")

	differences = hexget.processFiles(file1, file2)

	show_all_diff=False

	checksum=[334,335,336,337,338]

	itemout, err = Process.create("cd ../pokecrystal-speedchoice; git diff | grep + | grep itemball | awk '{print $3'}")
	locationout, err = Process.create("cd ../pokecrystal-speedchoice; git diff | grep maps/ | grep +++ | awk '{print $2}'")

	location_name="location_buffer"
	item_name="item_buffer"
	#location_name = locationout[0].split("/")[-1].replace(".asm","")
	#item_name = itemout[0].lower().capitalize()

	#print(item_name, location_name)

	json1="{{\"label\":\"{}\"," \
	"\"address_range\":{{\"begin\":{},\"end\":{}}}," \
	"\"integer_values\":\"{}\", \"hex_values\":\"{}\"}}"

	label_item = "{}{}.ckir_BEFORE{}{}0ITEMCODE"
	label_npc = "{}_MapEvents.ckir_BEFORE{}{}0NPCCODE"

	item_label = label_item.format(location_name, item_name, location_name.upper(), item_name.upper())
	npc_label = label_npc.format(location_name, location_name.upper(), item_name.upper())

	processed={}
	ranges={}

	iterator=0
	for x in differences:

	 if show_all_diff:
	  f_check.seek(x)
	  f.seek(x)
	  old_byte = f.read(1)
	  new_byte = f_check.read(1)
	  old=printBytes(old_byte, "hex")
	  new=printBytes(new_byte, "hex")
	  print(old, new, x, hex(x))
	 
	 else:
	  if x in checksum:
	   #print("skipping", x)
	   continue

	 if x-1 in ranges:
	  range_start = ranges[x-1]
	  del ranges[x-1]
	  ranges[x] = range_start
	 else:
	  ranges[x] = x

	#print(ranges)
	
	diffResults = []


	json_patch="{{\"integer_values\": {{ \"old\": [{}], \"new\": [{}] }},"\
	 "\"address_range\": {{ \"begin\": {}, \"end\": {} }}}},"
	for range_end in ranges.keys():
	 range_start = ranges[range_end]
	 f.seek(range_start)
	 f_check.seek(range_start)
	 byte_size = range_end-range_start + 1
	 by_old = f.read(byte_size)
	 by_new = f_check.read(byte_size)
	 
	 ints_old = printBytes(by_old, "int").replace(" ",",")
	 ints_new = printBytes(by_new, "int").replace(" ",",")
	 j = json_patch.format(ints_old, ints_new, range_start, range_end+1)
	 
	 dR = DiffResult(by_old, by_new, range_start, range_end)
	 diffResults.append(dR)
	 if shouldPrint:
	  print(j)
	return diffResults
	 
if __name__ == "main":
 processFile(default_file1, default_file2, print=true)
