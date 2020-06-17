'''
Created on Apr 6, 2020

@author: christophe
'''
from vectors import VectorAnalysis
from music21 import converter
import os, pitchCollections
from astor.rtrip import convert
from copy import deepcopy

if __name__ == '__main__':
    pass

workWithRootDirectoryString = '/Users/christophe/Dropbox/Praetorius/source/xmlWithRoot/'
workDirectoryString = '/Users/christophe/Dropbox/Praetorius/source/xml/'

corrputedFilesList = []

for file in os.listdir(workWithRootDirectoryString):
    fileName = os.fsdecode(file)
    if fileName.endswith(".musicxml")== False: continue
    
  

    
    workPath = workWithRootDirectoryString + fileName 
    workWithoutRoot = converter.parse(workPath)
    
    
    ''' get root stream '''
    rootStream = None
    for part in workWithoutRoot.parts:
        if part.partName == "Root":
            rootStream = part
        
    if rootStream == None: 
        continue
        print (fileName + ": Cannot find root stream")
        corrputedFilesList.append(fileName)
        
        
    workWithRoot = deepcopy(workWithoutRoot)
    workWithoutRoot.remove(rootStream, recurse=True)
    
    if workWithoutRoot.duration.quarterLength != workWithRoot.duration.quarterLength:
        continue
        print (fileName + ": Offsets of root stream and other streams do not match")
        corrputedFilesList.append(fileName)
        
    
    ''' create PirtchCollectionSequencesObject and add root information '''
    pitchCollectionSequences = pitchCollections.PitchCollectionSequences(workWithoutRoot)
    pitchCollectionSequences.setRootsFromStream(rootStream)  
    
    vectorAnal = VectorAnalysis(pitchCollectionSequences)
    fileNumber = fileName.replace(".musicxml", "")
    vectorList = vectorAnal.show('simpleList')
    
    print (fileNumber + "\t" + vectorList)