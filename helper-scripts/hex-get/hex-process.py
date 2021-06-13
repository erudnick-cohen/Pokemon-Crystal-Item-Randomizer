import sys
import hexget
import Process
#file1="crystal-speedchoice.gbc"
#file2="x.gbc"


file1="daily.gbc"
file2="daily-mod.gbc"

#file1="f1"
#file2="f2"

original=file1
f = open(original,"rb")

f_check = open(file2,"rb")

differences = hexget.processFiles(file1, file2)
#print("dif=",differences)
first_code_length=2
second_code_length=13

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

show_all_diff=True

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

processed=[]
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
   print("skipping", x)
   continue
  if x in processed:
   continue
  iterator += 1
  if iterator == 1:
   bytes_to_read=2
   hex_value = hex(x)
   f.seek(x)
   b = f.read(bytes_to_read)
   ints = printBytes(b, "int")
   hexes = printBytes(b,"hex")
   ph = "berry" #placeholder
   d1 = json1.format(item_label,x,x+bytes_to_read,ints,hexes)
   print(d1)
   for i in range(x, x+bytes_to_read):
    processed.append(i)
  elif iterator == 2:
   bytes_to_read=13
   hex_value = hex(x)
   f.seek(x)
   b = f.read(bytes_to_read)
   ints = printBytes(b, "int")
   hexes = printBytes(b,"hex")
   ph = "berry" #placeholder
   d1 = json1.format(npc_label,x,x+bytes_to_read,ints,hexes)
   print(d1)
   for i in range(x, x+bytes_to_read):
    processed.append(i)
# if iterator == 1:
 # continue
 #elif iterator == 3 or iterator==4:
  #print(hex(x))
  #f.seek(x)
  #b = f.read(first_code_length)
  #printBytes(b,"int")
  #printBytes(b,"hex")
  #print("\"begin\":",x,",\"end\":", x+first_code_length)
  #f_check.seek(x)
  #new = f_check.read(1)
  #print("changed to", new)
 #elif iterator == 2:
  #f.seek(x)
  #b = f.read(second_code_length)
  #print(x)
  #printBytes(b,"int")
  #printBytes(b, "hex")
 
