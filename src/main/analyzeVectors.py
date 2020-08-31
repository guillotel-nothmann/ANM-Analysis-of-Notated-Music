'''
Created on Apr 6, 2020

@author: christophe
'''
from vectors import VectorAnalysis
from music21 import converter
from pitchAnalysis.scales import ScaleAnalysis
from openpyxl import Workbook   

import json
import pandas as pd

import os, pitchCollections 
from copy import deepcopy
import rootAnalysis



def getListFromDictionary(dataDictionary, dictionaryKey):
    
    if dictionaryKey not in dataDictionary:
        dataDictionary[dictionaryKey] = []
        
    return dataDictionary[dictionaryKey]
        

if __name__ == '__main__':
    pass

workWithRootDirectoryString = '/Users/christophe/Dropbox/Praetorius/Polyhymnia/Source/xmlWithRoot/testRoots/'
workDirectoryString = '/Users/christophe/Dropbox/Praetorius/Polyhymnia/Source/normalized/'
workBookPath = '/Users/christophe/Dropbox/Praetorius/Polyhymnia/rootsAndVectors.xlsx'


corrputedFilesList = []
analyzedWorksList = []

rootList = [] 


for file in os.listdir(workWithRootDirectoryString):
    fileName = os.fsdecode(file)
    if fileName.endswith(".musicxml")== False: continue
    
    
    print ("Analyzing file :" + fileName)
    rootDictionary = {}
    vectorDictionary = {} 
    
  

    
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
    
    ''' analyze roots and inversions '''
    rootAnal = rootAnalysis.RootAnalysis(pitchCollectionSequences)
    rootAnal.populateRootDictionary() 
     
    
    ''' analyze vectors '''
    vectorAnal = VectorAnalysis(pitchCollectionSequences)
    
    
    
    analyzedWorksList.append([fileName, deepcopy(rootAnal.rootDictionary), deepcopy (vectorAnal.show('dict'))])
    
''' populate work dictionaries '''

wb = Workbook()
wb.save(workBookPath)
dataDictionary= {
    'File name': [],
    }

 


for workDataCounter, workData in enumerate (analyzedWorksList): 
    rootDict = workData [1] 
    
    for rootElement in rootDict:
        if not rootElement in rootList:
            rootList.append(rootElement)
            
rootList.sort()



for workDataCounter, workData in enumerate (analyzedWorksList):
    fileName = workData [0]
    rootDict = workData [1]
    vectorDict = workData [2]
    
    
    dataDictionary["File name"].append(fileName)
    
    print (fileName)
    
      
    
    for vector in [4, -3, 2, -4, 3, -2]:
        dataList = getListFromDictionary(dataDictionary, vector)
        if vector in vectorDict:
            dataList.append (vectorDict[vector]["occurrence"]) 
            
        else:
            dataList.append("")
            
         
    for rootElement in rootList: 
        for interv in ["P1", "m3", "M3", "p5", "d5"]:
            dataList = getListFromDictionary(dataDictionary, rootElement + "_" + interv)
            
            if rootElement in rootDict:
                rootEntry = rootDict[rootElement]
            
                if interv in rootEntry : 
                    dataList.append (rootEntry[interv])
                else:
                    dataList.append("")
            else:
                dataList.append("")
             
         
           


         
            
df = pd.DataFrame(data=dataDictionary)
df.to_excel(workBookPath)  
       
        
    
    
    
