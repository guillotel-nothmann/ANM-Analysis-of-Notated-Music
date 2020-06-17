'''
Created on Apr 8, 2020

@author: christophe
'''
from rootAnalysis import RootAnalysis

if __name__ == '__main__':
    pass


import rootAnalysis, os
from music21 import converter
import logging, pitchCollections
import manipulateDataset

if __name__ == '__main__':
    pass

directoryName=os.path.dirname
rootDirectoryName = directoryName(directoryName(directoryName(__file__)))

#workDirectoryString = '/Users/christophe/Documents/GitHub/PraetoriusTerpsichore/xml/'
#rootDirectoryString = '/Users/christophe/Documents/GitHub/PraetoriusTerpsichore/xmlWithRoot/'
#observationPath = rootDirectoryName + "/observations/rootObservationData"

minAnalysis = 2

workDirectoryStringComparison = '/Users/christophe/Dropbox/HarmonisationsBach/analyseComparaisons/'
workDirectoryStringModel = '/Users/christophe/Dropbox/HarmonisationsBach/analyseModèle/'
workDirectoryStringCraig = '/Users/christophe/Dropbox/HarmonisationsBach/Craig/'
workDirectoryStringMarc = '/Users/christophe/Dropbox/HarmonisationsBach/Marc/'
workDirectoryStringChristophe = '/Users/christophe/Dropbox/HarmonisationsBach/Christophe/'
workDirectoryStringNicolas = '/Users/christophe/Dropbox/HarmonisationsBach/Nicolas/'
workDirectoryStringAnneEmmanuelle = '/Users/christophe/Dropbox/HarmonisationsBach/Anne-Emmanuelle/'

workDirectoryNameList = [[workDirectoryStringMarc, "Marc"], [workDirectoryStringChristophe, "Christophe"], [workDirectoryStringNicolas, "Nicolas"], [workDirectoryStringAnneEmmanuelle, "Anne-Emmanuelle"], [workDirectoryStringCraig, "Craig"]]


corrputedFilesList = []

for file in os.listdir(workDirectoryStringModel):
    fileName = os.fsdecode(file)
    if fileName.endswith(".musicxml")== False: continue
    streamList = []
    
    for workDirectoryString in workDirectoryNameList:
    
        try:
            workStream = converter.parse(workDirectoryString[0] + fileName)
            for part in workStream.parts:
                if part.partName == "Root":
                    streamList.append([part, workDirectoryString[1][:2]]) 
        except: 
            continue

    
    if len (streamList) <= minAnalysis: continue
    
    ''' create reference analysis withouth root stream '''
    workStream = converter.parse(workDirectoryStringModel + fileName)
    for part in workStream.parts:
        if part.partName == "Root":  
            workStream.remove(part, recurse=True)
            
 
    '''compare streams and get annotated reference root stream '''
    referencerootStream = RootAnalysis.compareConcurrentRootAnalyses(streamList)
    
    if referencerootStream == None: 
        print("error " + fileName)
        continue
    
 
    workStream.insert(0, referencerootStream)
    workStream.write('musicxml', workDirectoryStringComparison + fileName)
    
    
    
    
    
             
            
    
    
        
        
    
    
    
   