#!/usr/bin/env python

# NAME: Naz, Jake, Sida
# CLASS: CSC433
# Project: 03

from array import array
import sys
import time
import os

#maximum number of entry for files in the archive  and also for data blocks for the archive
MAX_ENTRY = 32

#maximum number of block for a single file archive entry
#a file cannot splan over multiple archiveentry
MAX_BLOCK_PER_FILE = 4

#maximum number of byte per datablock
MAX_BYTE_PER_DATABLOCK = 32

#maxium lenght for a file name
MAX_FILENAME = 8

#maximum number of characters used to store datablocks uses by a file
MAX_DIGIT_FOR_BLOCK = 2

#filesize will use a maximum of 3 digits
MAX_DIGIT_FOR_FILESIZE = 3

ARCHIVE_FILENAME = "archive.dat"

#datablock id starts at 1
class DataBlock:

     def __init__(self, id=0, data="Z" * MAX_BYTE_PER_DATABLOCK, ):

         self.id    = id
         self.data  = data

     def readFromArchive( self, id, line ):
         self.id   = id
         self.data = line

     def writeToArchive( self, file ):
         file.write( self.data.ljust( MAX_BYTE_PER_DATABLOCK ) ) 
         file.write("\n")

#an empty archiveentry has a filename = ""
#the block entries is equal to 0, when it is not in used
class ArchiveEntry:

     def __init__(self, filename = "", size=0, ):

         self.filename = filename
         self.size     = size
         
         self.datablocks   = [0] * (MAX_BLOCK_PER_FILE)

     def readFromArchive( self, line ):

         self.size     = int(line[:MAX_DIGIT_FOR_FILESIZE])
         self.filename = line[MAX_DIGIT_FOR_FILESIZE : MAX_DIGIT_FOR_FILESIZE + MAX_FILENAME].strip()
         self.datablocks = [int(line[i:i+2]) for i in range(MAX_DIGIT_FOR_FILESIZE + MAX_FILENAME,len(line),2)]
         
     def writeToArchive( self, file ):
         file.write( str(self.size).zfill( MAX_DIGIT_FOR_FILESIZE ) ) 
         file.write( self.filename.rjust( MAX_FILENAME ) ) 
         for idx in range(0, len( self.datablocks ) ) :
             file.write( str(self.datablocks[ idx ]).zfill( MAX_DIGIT_FOR_BLOCK ) )
         file.write("\n")

     def list( self ):
         print(self.filename.rjust( MAX_FILENAME )), 
         for idx in range(0, len( self.datablocks ) ) :
             print(str(self.datablocks[ idx ]).zfill( MAX_DIGIT_FOR_BLOCK )), 
         print("\n")

     def isEmpty( self ):
         return len(self.filename) == 0

class Archive:

     def __init__( self ):
        self.archiveEntries = []
        self.dataEntries = []
        self.file = []

        self.archiveEntries = [ ArchiveEntry() for x in range(MAX_ENTRY)]
        self.dataEntries    = [ DataBlock() for x in range(MAX_ENTRY)]
     
     def writeToArchive( self ) :
     	
        archive = open( ARCHIVE_FILENAME, "w")

        for idx in range(0, MAX_ENTRY):
           self.archiveEntries[ idx ].writeToArchive( archive )

        for idx in range(0, MAX_ENTRY):
           self.dataEntries[ idx ].writeToArchive( archive )

        archive.close( )

     def readFromArchive( self ):
        archive = open( ARCHIVE_FILENAME, "r")

        count = 0
        datablockid = 1;
        for line in archive:
            line = line.rstrip('\n')
            if count < MAX_ENTRY: 
               self.archiveEntries[ count ].readFromArchive( line )
            else:
               self.dataEntries[ datablockid - 1 ].readFromArchive( datablockid, line )
               datablockid = datablockid + 1
            count = count + 1


     def list( self ):
     	#print(self.archiveEntries[0].isEmpty())
     	for idx in range(0, MAX_ENTRY):
     		print("entry :" + str(idx) )
     		if self.archiveEntries[ idx ].isEmpty():
                    print(" empty")
     		else :
                    self.archiveEntries[ idx ].list()
     	print("\n")
     
     def create( self ):
        self.writeToArchive();

     def addToArchive( self, filename ):
        count = 0
        while count < MAX_ENTRY and not self.archiveEntries[count].isEmpty():
            count+=1
        prev = 0
        if count > 0:
            prev = max(self.archiveEntries[count-1].datablocks)
        try:
            f = open(filename)
            txt = f.read().strip()
            size = os.stat(filename).st_size - 1
            if (fileSizeOk(filename) and fileNameOk(filename) and fileNameUnique(filename) and freeSpaceAvailable(filename) and checkMinimumDatablock(filename) and checkDatablockSize(size, prev)):
                archive = open( ARCHIVE_FILENAME, "w")
                new = ArchiveEntry(filename, size)
                for i in range(0, size//MAX_BYTE_PER_DATABLOCK+1):
                    new.datablocks[i] = prev+i+1
                    self.dataEntries[i+prev] = DataBlock(data = txt[MAX_BYTE_PER_DATABLOCK*i:MAX_BYTE_PER_DATABLOCK*(i+1)])
                self.archiveEntries[count] = new
        except IOError:
            print "No such file exists in the directory"
        
        
     def removeFromArchive( self, filename ):
        count = 0
        num = 0
        id = []
        while count < MAX_ENTRY:
            if self.archiveEntries[count].filename == filename:
                id = self.archiveEntries[count].datablocks
                for i in id:
                    if i !=0:
                        num += 1
                        self.dataEntries[i-1] = DataBlock()
                count+=1
                break
            count+=1
        if count == MAX_ENTRY:
            print("File doesn't exist!!!")
            return 0
        else:
            while count < MAX_ENTRY:
                if not self.archiveEntries[count].isEmpty():
                    for i in range(4):
                        if self.archiveEntries[count].datablocks[i] != 0:
                            self.archiveEntries[count].datablocks[i] -= num
                    self.archiveEntries[count-1] = self.archiveEntries[count]
                else:
                    self.archiveEntries[count-1] = ArchiveEntry()
                count+=1
            self.archiveEntries[count-1] = ArchiveEntry()
        start = max(id)
        while start < MAX_ENTRY and self.dataEntries[start].data != "Z" * MAX_BYTE_PER_DATABLOCK:
            self.dataEntries[start-num] = self.dataEntries[start]
            self.dataEntries[start] = DataBlock()
            start+=1


def fileSizeOk(filename):
    fileStat = os.stat(filename)
    if ( len(str(fileStat.st_size)) <= MAX_DIGIT_FOR_FILESIZE ):
        return True
    print('File size exceeds maximum size!!!')
    return False

def fileNameOk(filename):
    if (len(str(filename)) <= MAX_FILENAME):
        return True
    print('Filename exceeds maximum file name!!!')
    return False

def fileNameUnique(filename):
    f = open(ARCHIVE_FILENAME, 'r')
    listOfFileNames = []
    counter = 0
    for line in f:
        name = line[MAX_DIGIT_FOR_FILESIZE : MAX_DIGIT_FOR_FILESIZE + MAX_FILENAME]
        if not (name.strip() == ''):
            listOfFileNames.append(name.strip())
        counter += 1
        if (counter >= MAX_ENTRY):
            break
    if not (filename in listOfFileNames):
        return True
    print('File already exists in the archive!!!')
    return False

def freeSpaceAvailable(filename):
    fileSize = os.stat(filename).st_size
    f = open(ARCHIVE_FILENAME, 'r')
    listOfFileSizes = []
    counter = 0
    for line in f:
        size = int(line[:MAX_DIGIT_FOR_FILESIZE])
        listOfFileSizes.append(size)
        counter += 1
        if (counter >= MAX_ENTRY):
            break
    if ( (( 999 * counter ) - sum(listOfFileSizes)) > fileSize ):
        return True
    print('Free space not available in the archive!!!')
    return False

def checkMinimumDatablock(filename):
    f = open(filename, 'r')
    line = f.readline()
    if (len(line.strip()) <= MAX_BYTE_PER_DATABLOCK * MAX_BLOCK_PER_FILE - 1):
        return True
    print('File exceeds minimum set of datablock!!!')
    return False

def checkDatablockSize(size, prev):
    if size/MAX_BYTE_PER_DATABLOCK < MAX_BYTE_PER_DATABLOCK-prev:
        return True
    print('Datablock is full!!!')
    return False

def createArchive():
     print("Creating Archive")
     Archive().create()

def addToArchive():
     filename = sys.argv[ 2 ];
     print("Adding to Archive:" + filename)
     archive = Archive()
     archive.readFromArchive()
     archive.list()
     archive.addToArchive( filename )
     archive.writeToArchive();

def removeFromArchive():
     filename = sys.argv[ 2 ];
     print("Removing from Archive:" + filename)
     archive = Archive()
     archive.readFromArchive()
     archive.list()
     archive.removeFromArchive( filename )
     archive.writeToArchive();

def listArchive():
     filename = sys.argv[ 2 ];
     print("Removing from Archive:" + filename)
     archive = Archive()
     archive.readFromArchive()
     archive.list()

def listArchive():
     filename = sys.argv[ 2 ];
     print("Removing from Archive:" + filename)




command  = sys.argv[ 1 ] 

print('Processing command: ' + command)

if command == 'create' :
   createArchive()
elif command == 'add' :
   addToArchive()
elif command == 'remove' :
   removeFromArchive()
elif command == 'list' :
   listArchive()
else :
   print("Invalid command")


