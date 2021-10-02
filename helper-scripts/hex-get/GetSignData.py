import Process
import hexprocesspatch
import sys
import GetSignMapData

TEST_FILE_NAME=None


# Current issues / special cases
# Lake of Rage house is not a standard sign, does not find tile with 'jumptext'
# This could be mitigated by finding 'writetext'

# Celadon Mansion / Dept Store Floors are map clones with different ASM
# Therefore, they are not currently detected

# House's containing variables are not affected by this script by design
# May add in future depending on how they are processed, space, etc.
# Main instance of this is player's house


def convertTile(tile, tileset):
 tileset_simple=tileset.replace("TILESET_","")
 tileData = {('45',"JOHTO"):'1', \
 ('47',"JOHTO"):'2',
 ('8',"KANTO"):'1',
 ('56',"KANTO"):'77',
 ('79',"KANTO"):'7b',
 ('77',"JOHTO_MODERN"):'6',
 ('45',"JOHTO_MODERN"):'1',
 ('65',"JOHTO_MODERN"):'1',
 ('47',"JOHTO_MODERN"):'2',
 ('3c',"JOHTO_MODERN"):'2',
 ('3d',"JOHTO_MODERN"):'3f',
 ('78',"JOHTO_MODERN"):'49',
 ('15',"PARK"):'1',
 ('17',"PARK"):'1',
 ('2',"RADIO_TOWER"):'4',
 ('13',"RADIO_TOWER"):'1',
 
 ('25',"TRAIN_STATION"):'-1', #Contains TWO signs!
 ('21',"BATTLE_TOWER_OUTSIDE"):'1',
 ('33',"JOHTO_MODERN"):'-1', #Mart?
 ('78',"JOHTO"):'1',
 ('73',"KANTO"):'-1', #Not Used
 ('12',"KANTO"):'-1', #Gym Door??
 ('13',"FOREST"):'1',
 ('29', "HOUSE"): '3'
 }
 
 if (tile, tileset_simple) in tileData:
  return tileData[(tile,tileset_simple)]
 else:
  print("Unknown convert tile:",tile, tileset)

# Define Classes
class AddressSpace:
 start=None
 end=None
 name=None
 map=None
 commands=0
 originalTile=None
 newTile=None
 tileAddress=None
 
 def __init__(self, start, end, name, filename, commands):
  self.start = start
  self.end = end
  self.name = name
  self.commands = commands
  self.map = filename
  
 def setTileDetails(self, original, new, address):
  self.originalTile = int(str(original),16)
  self.newTile = int(str(new),16)
  self.tileAddress = address
  
 def formatAsJsonWithTile(self):
   json_format = "{{\"start\":{},\"end\":{},\"name\":\"{}\",\"map\":\"{}\",\"commands\":{},\"originalTile\":{}, \"newTile\":{}, \"tileAddress\":{}}}\n"
   js = json_format.format(self.start, self.end, self.name, 
    self.map, self.commands, self.originalTile, self.newTile, self.tileAddress)
   return js
  
 def formatAsJson(self):
    if self.originalTile is not None and self.newTile is not None and self.tileAddress is not None:
     return self.formatAsJsonWithTile()
    else:
     json_format = "{{\"start\":{},\"end\":{},\"name\":\"{}\",\"map\":\"{}\",\"commands\":{}}}\n"
     js = json_format.format(self.start, self.end, self.name, 
      self.map, self.commands)
    return js
 
class textOut:
 startLine=0
 filename=""
 label=""
 commands=0
 textLines=[]
 
 def __init__(self,label,filename,startLine):
   self.startLine=startLine
   self.filename=filename
   self.label = label
   self.textLines = []
   self.commands = 0

class ReplaceData:
 firstOld=None
 firstNew=None
 lastOld=None
 lastNew=None
 sedCommand=None
 label=None
 filename=None
 commands=None
 
import string
def ByteToGBCCharacterByte(charr):
    upper=string.ascii_uppercase
    lower=string.ascii_lowercase

    if charr in upper:
        return 128+upper.index(charr)
    elif charr in lower:
        return 160+lower.index(charr)
    elif charr == " ":
        return 127
    else:
        return 160

def GBCCharacterByteToByte(b):
    lower=string.ascii_lowercase
    upper=string.ascii_uppercase
    digits="0123456789"
    
    if b == 127:
     return " "
    elif b == 231:
     return "!"
    elif b == 232:
     return "."
    elif b == 117:
     return "…"
    elif b > 127 and b < 127+len(upper)+1:
     return upper[b-127-1]
    elif b > 159 and b < 159+len(lower)+1:
     return lower[b-159-1]
    elif b >= 246 and b < 256:
     return str(digits[b-246])
    elif b == 84:
     return '#' #May require special case for MON
    else:
     return None
        

start_dir="../pokecrystal-speedchoice/maps"
#debug_file="../pokecrystal-speedchoice/maps/Route34.asm"
debug_file=None

here="hex-get"
command="grep -rni -e \"trainertips[A-Za-z0-9]*text:\" -e \"sign[A-Za-z0-9]*text:\" " \
        "-e \"signpost[A-Za-z0-9]*text:\" -e \"SquareText:\" " \
        "-e \"NoticeText\" -e \"DescriptionText:\" -e \"Directory[A-Za-z0-9]*Text:\" " \
        + start_dir + " | grep -vi 'Signal' | grep -v 'Design' | \
        grep -vi 'unused' | grep -vi 'jumptext'"
#command="grep -rni -e \"text:\" -e \"_text\" -e \"text_\" " + start_dir
gitResetCommand = "cd ../pokecrystal-speedchoice; git reset --hard; " 
Process.create(gitResetCommand)

json_out_file="text.json"
out=open(json_out_file, "w")

letters_out_file="letters.txt"
letters=open(letters_out_file, "w")


full_results={}
print("Command=",command)
results = Process.create(command)
for line in results[0]: #The stdouts
 if TEST_FILE_NAME is not None and TEST_FILE_NAME not in line:
  continue
 
 line_data = line.split(":")
 file = line_data[0]
 lineNo = line_data[1]
 label = line_data[2]
 
 if debug_file is not None and file != debug_file:
  continue
  
 #print("try:", line)
 
 if len(line_data) <= 3:
  print("label", label, line_data, "not a label")
  continue  
 
 #print("d",file, lineNo, label)
 fobj = open(file)
 fdata = fobj.readlines()
 textDataEnded = False
 lineIt = int(lineNo) # Would add 1 but greps line number outputs starts at 1
 dataToProcess = [] 
 while not textDataEnded:
  if lineIt >= len(fdata):
   print("Big error with termination",file, lineNo, label)
   sys.exit(0)
  process = fdata[lineIt].strip()
  if len(process) == 0:
   dataToProcess.append((process,file,lineNo,label))
   lineIt += 1
   continue
  if process == "done":
   textDataEnded=True
  elif process == "text_end":
   textDataEnded=True
  elif "unused" in process:
   textDataEnded=True
  elif "endc" in process:
   textDataEnded=True
  elif "jumpstd" in process:
   textDataEnded=True
  else:
   dataToProcess.append((process,file,lineNo,label))
   lineIt += 1
 
 



 for i in dataToProcess:
  textData = i[0]
  sp = textData.split(" ")
  #print("sp=",sp)
  command = sp[0]
  if command == "jumpstd": #Skip references to standard messages (centres, marts, etc)
   print("Skip jumpstd",i)
   continue
  ix = textData.replace(command+" ", "")
  if textData == ix:
   data = ""
  data = ix.replace("\"","")
  dataLength = len(data)
  
  # Ignore signs with special variable calls in them!
  # May want to also expand this to have #MON, 
  # depending on functionality when imported
  if "<" in textData:
   print("Skip:", i)
   continue
  
  if not i[3] in full_results:
   t = textOut(i[3],i[1],i[2]) #label,filename,startLine)
   full_results[i[3]] = t
  exist = full_results[i[3]]
  exist.textLines.append(data)
  #print("added", data, exist.textLines)
  exist.commands +=1


#print(full_results)
import re
import string
import random

allLetters = []
allLetters.extend(list(string.ascii_uppercase))
allLetters.extend(list(string.ascii_lowercase))

allByteNumbers = range(0,255)
    
finished_text=False
finished_tile=False
lastStopped=None

signMapDetails = {}
signData = []
    
while not finished_text:
    processLocations={}
    lastRound = True
    sedData = []
    indexProgression=0
    fine = True
    
    Process.create(gitResetCommand)
    #Process.create(d.sedCommandFirst)
    
    for label in full_results.keys():
     if lastStopped is not None:
      if indexProgression < lastStopped:
       indexProgression+=1
       continue
     indexProgression+=1
     
     data=full_results[label]
     labelLine = data.startLine
     #print("go", indexProgression, data.filename, labelLine, data.textLines)
     sed_command="sed -i '{}s/{}/{}/g' {}"
     lineDiffFirst=0
     lineDiffLast=0
     interestLines=[]
     lineDiff=0
     while lineDiff < len(data.textLines):
      lineDiff+=1
      if len(data.textLines[lineDiff-1]) != 0:
       if lineDiffFirst == 0:
        lineDiffFirst = lineDiff
       lineDiffLast = lineDiff
     lineNoFirst = int(labelLine)+lineDiffFirst
     lineNoLast = int(labelLine)+lineDiffLast

     firstChar = data.textLines[lineDiffFirst-1][0]
     lastChar = data.textLines[lineDiffLast-1][-1]
     
     first_options = []
     last_options = []
     
     map_detail = GetSignMapData.getAssociatedMapData(label, data.filename)
     signMapDetails[label] = map_detail
     
     random.seed(2) #Can be random, but debugging hard with random behaviour
     
     if firstChar in processLocations:
      alreadyLetters = processLocations[firstChar]
      first_options.extend(allLetters)
      first_options = [x for x in first_options if x not in alreadyLetters and x!=firstChar] 
      if len(first_options) > 0:
       charToFirst=random.choice(first_options)
       processLocations[firstChar].append(charToFirst)
      else:
       print("Unable to match up any furtherA:", firstChar, len(first_options), len(alreadyLetters))
       fine = False
     else:
      first_options.extend(allLetters)
      if firstChar in first_options:
       first_options.remove(firstChar)
      charToFirst = random.choice(first_options)
      processLocations[firstChar] = [charToFirst]
     
     if lastChar in processLocations:
      alreadyLetters = processLocations[lastChar]
      last_options.extend(allLetters)
      last_options = [x for x in last_options if x not in alreadyLetters and x!=lastChar and x!=charToFirst]
      if len(last_options) > 0:
       charToLast=random.choice(last_options)
       processLocations[lastChar].append(charToLast)
      else:
       print("Unable to match up any furtherB:", lastChar, len(last_options), len(alreadyLetters))
       fine = False
     else:
      last_options.extend(allLetters)
      if lastChar in last_options:
       last_options.remove(lastChar)
      if charToFirst in last_options:
       last_options.remove(charToFirst)
      charToLast = random.choice(last_options)
      processLocations[lastChar] = [charToLast]
      
     #if fine and map_detail is not None:
      #alreadyNumbers = processLocations[map_detail.sign_tile]
      #num_options = []
      #num_options.extend(allByteNumbers)
      #last_options = [x for x in num_options if x not in alreadyNumbers and x!=map_detail.sign_tile]
      #if len(num_options) > 0:
      # signTile=random.choice(num_options)
      # processLocations[map_detail.sign_tile].append(signTile)
      #else:
       #print("Unable to match up any furtherC:", lastChar, len(last_options), len(alreadyLetters))
       #fine = False
       
     if fine:
      firstCharEsc=re.escape("\""+firstChar)
      lastCharEsc=re.escape(lastChar+"\"")

      firstCharToEsc=re.escape("\""+charToFirst)
      lastCharToEsc=re.escape(charToLast+"\"")

      formatted_sed_first=sed_command.format(lineNoFirst,firstCharEsc,firstCharToEsc,data.filename)
      formatted_sed_last=sed_command.format(lineNoLast,lastCharEsc,lastCharToEsc,data.filename)  

      rd=ReplaceData()
      rd.firstOld = firstChar
      rd.firstNew = charToFirst
      rd.lastOld = lastChar
      rd.lastNew = charToLast
      rd.sedCommandFirst = formatted_sed_first
      rd.sedCommandLast = formatted_sed_last
      rd.filename = data.filename
      rd.label = data.label
      rd.commands = data.commands
      #print("add", rd.filename, rd.label)
      sedData.append(rd)
     
     else:
      print("Break, incomplete")
      fine = True
      lastStopped = indexProgression-1
      lastRound = False
      break
      

    if fine and len(sedData) == 0:
     break
     
    if lastRound:
     lastStopped = indexProgression 
      
    #print("Testing:", fine, lastRound, len(sedData), lastStopped)
    
    if fine:
     resultDetails = []
     #print("continue, do not process files yet")
     #continue
     
     for d in sedData:
      letterDebug = str(d.firstOld) + " " + str(d.firstNew) + " " + str(d.lastOld) + " " + str(d.lastNew) + " " + str(d.label+"\n")
      #print(letterDebug, d.sedCommandFirst, d.sedCommandLast)
      letters.write(letterDebug)
	  
      Process.create(d.sedCommandFirst)
      Process.create(d.sedCommandLast)
     
     
     
      
     make = "cd ../pokecrystal-speedchoice; make; cp crystal-speedchoice.gbc ../hex-get/sign.gbc"
     Process.create(make)
      
     changes = hexprocesspatch.processFile("base.gbc","sign.gbc")
     #input("Press to continue")
     firstInPair=True
     pairItem=None
     pairItemChange=None
     
     previous=None
     
     for change in changes:
      #print("Change=",change.oldBytes, change.newBytes, change.addressFrom, change.addressTo, len(change.oldBytes), len(change.newBytes))
      if len(change.oldBytes) == 1 and len(change.newBytes) == 1:
       originalChar = GBCCharacterByteToByte(change.oldBytes[0])
       newChar = GBCCharacterByteToByte(change.newBytes[0])
       #print("Change=",originalChar, newChar, change.addressFrom, change.addressTo)
       
       if newChar is None or originalChar is None:
        print("Error:Unknowns:", change.oldBytes[0], change.newBytes[0])
        #Unhandled characters so far
        firstInPair=True
        pairItem=None
        pairItemChange=None
        continue
        
       
       #print("lookup:", originalChar, newChar, change.oldBytes[0], change.newBytes[0])
       
       checkFirst = list(filter(lambda x: x.firstOld == originalChar and x.firstNew == newChar, sedData))
       checkLast = list(filter(lambda x: x.lastOld == originalChar and x.lastNew == newChar, sedData))
       
       if len(checkFirst) == 0 and len(checkLast) == 0:
        print("Error:Could not find accompyment")
       elif len(checkFirst) > 0 and len(checkLast) > 0:
        print("Error:Problem, found in first and last")
        continue
       elif len(checkFirst) == 0:
        if firstInPair:
         print("Error, should always match new")
         firstInPair=True
         pairItem=None
         pairItemChange=None
        else:
         if checkLast[0] == pairItem:
         #print(pairItem.filename, pairItem.label, pairItemChange.addressFrom, change.addressTo)
         #-1 to include the start of text command
         #+1 to iterate TO the next line that is not used
          addr = AddressSpace(pairItemChange.addressFrom-1, change.addressTo+1, pairItem.label, pairItem.filename, pairItem.commands)
          resultDetails.append(addr)           
         else:
          print("Error:Found items do not match as pair")
         
         firstInPair=True
         pairItem=None
         pairItemChange=None
         
       elif len(checkLast) == 0:
        if not firstInPair:
         print("Error:should always have no match!",previous, change.addressTo, originalChar, newChar)
         print("ErrorP2", checkFirst[0].firstNew, checkFirst[0].lastOld, checkFirst[0].lastNew, checkFirst[0].filename, checkFirst[0].label, change.oldBytes, change.newBytes, change.addressFrom, change.addressTo)
         print("Error cont:",pairItem.firstNew, pairItem.lastOld, pairItem.lastNew, pairItem.filename, pairItem.label, pairItemChange.oldBytes, pairItemChange.newBytes, pairItemChange.addressFrom, pairItemChange.addressTo, previous)
         firstInPair = True
        else:
         firstInPair=False
         pairItem=checkFirst[0]
         pairItemChange = change
         previous = str(originalChar) + "/" +  str(newChar)
         #print("Error:Reset first details.. previous:", ",at:", previous, change.addressTo, originalChar, newChar)
      elif len(change.oldBytes) !=1 or len(change.newBytes) !=1 :
       print("Error: Size change issue with:", change.addressTo, change.addressFrom)
       
     for detail in resultDetails:
      signData.append(detail)
        
     # Because we have to process other things first now, this will be moved to another function
     #json_format = "{{\"start\":{},\"end\":{},\"name\":\"{}\",\"map\":\"{}\",\"commands\":{}}}"
     #for detail in resultDetails:
      #js = json_format.format(detail.start, detail.end, detail.name, detail.map, detail.commands)
      #print(js)
      #out.write(js+"\n")
    
Process.create(gitResetCommand)

map_details = []

while not finished_tile:
 processTiles={}
 valueChanges=[]
 
 fine = True
 for tileKey in signMapDetails.keys():  
  #signTile = None
  tileValue = signMapDetails[tileKey]
  
  if tileValue is None:
   print("tileValue is None...", tileKey)
   continue
  
  blk_file = tileValue.blk_file
  
  if tileValue.sign_tile in processTiles:
   currentNos = processTiles[tileValue.sign_tile]
   alreadyNumbers=[]
   for x in currentNos:
    alreadyNumbers.append(x[0])   
   num_options = []
   num_options.extend(allByteNumbers)
   last_options = [x for x in num_options if x not in alreadyNumbers and x!=tileValue.sign_tile]
   if len(last_options) > 0:
     signTile=random.choice(last_options)
     processTiles[tileValue.sign_tile].append((signTile,tileValue))
   else:
     print("Unable to match up any furtherC:", lastChar, len(last_options), len(alreadyLetters))
     fine = False
     break
  else:
   first_nums = []
   first_nums.extend(allByteNumbers)
   first_nums = [x for x in first_nums if x != tileValue.sign_tile]
   signTile = random.choice(first_nums)
   processTiles[tileValue.sign_tile] = [(signTile,tileValue)]
     
  blk_d_file = open(blk_file, "r+b")
  blk_d_file.seek(tileValue.sign_pos)
  blk_d_file.write(bytes([signTile]))
  blk_d_file.close()
  
  
 print("process")
 make = "cd ../pokecrystal-speedchoice; make; cp crystal-speedchoice.gbc ../hex-get/sign.gbc"
 Process.create(make)
 
 #print(processTiles)
      
 changes = hexprocesspatch.processFile("base.gbc","sign.gbc")
 for change in changes:
  #if change.addressFrom != change.addressTo:
   # print("Error, single bytes only expected")
    #continue
    
  size = change.addressTo - change.addressFrom
    
  for i in range(0,size+1):
   converted_old = hex_rep = str(hex(int(str(change.oldBytes[i]))))[2:]
   converted_new = hex_rep = int(change.newBytes[i])
  
   options = processTiles[converted_old]
  
   results = list(filter(lambda x: x[0]==converted_new, options))
   if len(results) != 1:
    for x in results:
     print(x[0], x[1])
     x[1].printObj()
    print("issue finding matching result", results)
   else:
    map_data = results[0][1]
    if map_data.address is None:
     map_data.address = change.addressFrom
     map_data.printObj()
     map_details.append(map_data)
    else:
     print("Already replaced, bug in identification", map_data.address)
   
   

  #print(change.oldBytes, change.newBytes, change.addressFrom, change.addressTo)
 
 
 break
  
  
  
Process.create(gitResetCommand)
print("Check signdata", len(signData))
for sign in signData:
 possibleTiles = list(filter(lambda x: x.label == sign.name, map_details))
 
 hasSignIcon = True
 
 if len(possibleTiles) > 1:
  print("Error finding single tile reference:",sign.name)
  hasSignIcon = False
 
 if hasSignIcon and len(possibleTiles) == 0:
  print("No tiles found for",sign.name)
  hasSignIcon = False
  
 if hasSignIcon:
  address = possibleTiles[0].address
  if address is None:
   print("No address found for this sign")
   hasSignIcon = False
  
  
 if hasSignIcon:
  original_tile = possibleTiles[0].sign_tile
  replacement_tile = convertTile(original_tile, possibleTiles[0].tileset)
 
  if replacement_tile is None:
   print("Unknown conversion for", sign.name)
   hasSignIcon = False
  elif replacement_tile == '-1':
   print("Known tile exception for", sign.name)
   hasSignIcon = False
 
 if hasSignIcon:
  sign.setTileDetails(original_tile, replacement_tile, possibleTiles[0].address)
 
 
 json = sign.formatAsJson()
 #print("outputjson", json)
 out.write(json)
  
  
  

  
out.close()  
letters.close()  
#Process.create(gitResetCommand)
  
  
  
