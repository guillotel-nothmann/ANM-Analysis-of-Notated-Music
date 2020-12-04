'''
Created on Nov 2, 2020

@author: christophe
'''

import os, copy
from music21 import converter
from harmonicAnalysis.cadenceAnalysis import CompareCadenceAnalyses

if __name__ == '__main__':
    pass

directoryName=os.path.dirname
rootDirectoryName = directoryName(directoryName(directoryName(__file__)))


minAnalysis = 1

 
workDirectoryStringChristophe = '/Users/christophe/Dropbox/Praetorius/Polyhymnia/Source/normalizedWithCadences/christophe/' 
workDirectoryStringAnneEmmanuelle = '/Users/christophe/Dropbox/Praetorius/Polyhymnia/Source/normalizedWithCadences/anne-emmanuelle/'
workDirectoryStringComparison = "/Users/christophe/Dropbox/Praetorius/Polyhymnia/Source/normalizedWithCadences/compare"


workDirectoryNameList = [[workDirectoryStringChristophe, "Christophe"], [workDirectoryStringAnneEmmanuelle, "Anne-Emmanuelle"]]


corrputedFilesList = []

for file in os.listdir(workDirectoryStringChristophe):
    fileName = os.fsdecode(file)
    if fileName.endswith(".musicxml")== False: continue
    streamList = []
    
    print (fileName)
    
    for workDirectoryString in workDirectoryNameList:
    
        try:
            workStream = converter.parse(workDirectoryString[0] + fileName)
            for part in workStream.parts:
                if part.partName == "Bassus continuus":
                    streamList.append([part, workDirectoryString[1][:2]]) 
        except: 
            continue

    
    if len (streamList) <= minAnalysis: continue
    
    print ("Comparing files " + fileName) 
 
    '''compare streams and get annotated reference root stream '''
    analysisComp = CompareCadenceAnalyses(streamList)
    
    refStream = analysisComp.referenceStream
    
    if refStream == None: 
        print("error " + fileName)
        continue
    
    '''create ref analysis ''' 
    
    refAnalysis = copy.deepcopy(workStream)
    for part in refAnalysis.parts:
        if part.partName == "Bassus continuus":
            refAnalysis.remove(part, recurse=True)
            break
    
    
 
    refAnalysis.insert(0, refStream)
    refAnalysis.write('musicxml', workDirectoryStringComparison + fileName)
    