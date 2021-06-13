import os

def recurse(datafile_1,datafile_2,size,result):
 start = datafile_1.tell()
 value_1 = datafile_1.read(size)
 value_2 = datafile_2.read(size)
 #print("data=",value_1, "&", value_2)
 if value_1 == value_2:
  #print("equal")
  return
 if size == 1:
  #print("add", start)
  result.append(start)
  return

 datafile_1.seek(start)
 datafile_2.seek(start)

 first_size=int(size/2)
 second_size=int(size/2)
 if size % 2 != 0:
  first_size = first_size+1
 #print(first_size, second_size)
 recurse(datafile_1, datafile_2, first_size, result)
 datafile_1.seek(start+first_size)
 datafile_2.seek(start+first_size)
 recurse(datafile_1, datafile_2, second_size, result)
 #print(result)
 

def processFiles(file1, file2):
 filename_1=file1
 filename_2=file2

 size_1 = os.path.getsize(filename_1)
 size_2 = os.path.getsize(filename_2)

 if size_1 != size_2:
  print("Files are not the same size")
  exit(1)

 f1 = open(filename_1,"rb")
 f2 = open(filename_2,"rb")

 result = []
 recurse(f1, f2, size_1, result)

 return result
