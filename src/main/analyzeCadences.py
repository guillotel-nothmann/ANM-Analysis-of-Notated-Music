'''
Created on Nov 3, 2020

@author: christophe

used to analyse cadences in a work or a group of works
cadences are identifed with fermatas in the score 

'''

import os
import pandas as pd
from music21 import converter
from harmonicAnalysis import cadenceAnalysis
from datetime import datetime

if __name__ == '__main__':
    pass


cadenceAnalList = []
now = datetime.now()
dt_string = now.strftime("%d%m%Y_%H%M")

''' set paths '''
directoryName=os.path.dirname
rootDirectoryName = directoryName(directoryName(directoryName(__file__)))
 

workDirectoryString = '/Users/christophe/Dropbox/Praetorius/Polyhymnia/Source/normalizedWithCadences/test/'
outputDirectoryString = '/Users/christophe/Dropbox/Praetorius/Polyhymnia/Source/normalizedWithCadences/results/' + dt_string + '.xlsx'

''' read files and store cadence analyses in list '''
for file in os.listdir(workDirectoryString):
    fileName = os.fsdecode(file)
    if fileName.endswith(".musicxml")== False: continue
    streamList = []
    
    print (fileName)
    workStream = converter.parse(workDirectoryString + fileName)
    
    
    ''' cadence analysis '''
    cadenceAnalList.append(cadenceAnalysis.Cadences(workStream))
    

''' organize results '''
    
# 2D: cadence types versus root steps
 
subTypeList = ["normal", "square", "angled"] ## lines
rootList = []## cols

tableDict = {"cadences": ["normal", "square", "angled"]}

for cadenceAnal in cadenceAnalList: ###
    for elementKey, element in cadenceAnal.cadencePointDictionary.items(): 
        if element["cadenceRoot"] not in rootList: 
            rootList.append(element["cadenceRoot"])
            tableDict [element["cadenceRoot"]] =  [0, 0, 0]
    
rootList.sort()

for cadenceAnal in cadenceAnalList:
    for root in rootList:
        for counter, subtype in enumerate(subTypeList):
            tableDict[root][counter] = tableDict[root][counter] +  len (cadenceAnal.getCadences(cadenceRoot = root, cadenceType = None, cadenceSubType= subtype))
            
            
            
            
dfOccurrence = pd.DataFrame(data=tableDict)
 
 
                                            


writer = pd.ExcelWriter(outputDirectoryString, engine='xlsxwriter')

dfOccurrence.to_excel(writer, sheet_name='Cadences')
 
writer.save()
 
    
    
    

     
    
    
    
    
    
    
    
    


