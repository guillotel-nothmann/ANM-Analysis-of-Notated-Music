 

import rootAnalysis, os
from music21 import converter, key
import logging, pitchCollections
import manipulateDataset


 
def getTranspositionIntervals (sharps=0, maxSharps=0): 
    
    
    if maxSharps == 4:
        keyTranspositionsDictionary = {
        4: ['p1',  'p4', '-M2',  'm3', '-M3', 'm2', '-a4', '-a1',  'd4'], 
        3:['-p4', 'p1', 'p4', '-M2', 'm3', '-M3', 'm2', '-a4', '-a1'], 
        2:['M2', '-p4', 'p1', 'p4', '-M2', 'm3', '-M3', 'm2', '-a4'],
        1:['-m3', 'M2', '-p4', 'p1', 'p4',  '-M2', 'm3', '-M3', 'm2'],
        0:['M3', '-m3', 'M2', '-p4',  'p1', 'p4', '-M2', 'm3', '-M3'],
        -1:['M3', '-m3', 'M2', '-p4', 'p1', 'p4', '-M2', 'm3', '-M3'],
        -2:['a4', '-m2', 'M3', '-m3', 'M2', '-p4', 'p1', 'p4', '-M2'],
        -3:['a1', 'a4',  '-m2',  'M3',  '-m3', 'M2', '-p4', 'p1', 'p4'],
        -4:['-d4', 'a1', 'a4', '-m2', 'M3', '-m3', 'M2', '-p4', 'p1']
        }
        return keyTranspositionsDictionary[sharps]    
        
    else : return ['p1']
        
    
    
    
    
     


if __name__ == '__main__':
    pass

directoryName=os.path.dirname
rootDirectoryName = directoryName(directoryName(directoryName(__file__)))

workDirectoryString = '/Users/christophe/Documents/GitHub/BachChorals/xml/'
rootDirectoryString = '/Users/christophe/Documents/GitHub/BachChorals/xmlWithRoot/'
observationPath = '/Users/christophe/Documents/GitHub/BachChorals/observations/'

#workDirectoryString = '/Users/christophe/Documents/GitHub/PraetoriusTerpsichore/xml/'
#rootDirectoryString = '/Users/christophe/Documents/GitHub/PraetoriusTerpsichore/xmlWithRoot/'
#observationPath = '/Users/christophe/Documents/GitHub/PraetoriusTerpsichore/observations/'

 
maxSharps = 4




corrputedFilesList = []

for file in os.listdir(rootDirectoryString):
    fileName = os.fsdecode(file)
    if fileName.endswith(".musicxml")== False: continue
    
    print ("Reading file " + fileName)

    
     
    ''' configure logging '''
    logging.basicConfig(level=logging.INFO)
    
    ''' get work and roots '''
    work = converter.parse(workDirectoryString + fileName)
    workWithRoot = converter.parse(rootDirectoryString + fileName)
    
    if work.quarterLength != workWithRoot.quarterLength:
        print (fileName + ": Work and roots do not match")
        corrputedFilesList.append(fileName)
        continue
        
    
    
    rootStream = None
    for part in workWithRoot.parts:
        if part.partName == "Root":
            rootStream = part
            break
        
        
    ''' get first key element '''
    keyElement = None
    for element in work.flat.getElementsByClass(key.KeySignature):
        keyElement = element
        break
    
    if keyElement == None:
        corrputedFilesList.append(fileName)
        break
    
    ''' generate transpositions '''
    transpositionList = getTranspositionIntervals(keyElement.sharps, maxSharps)
 
    for transposition in transpositionList:
        
        transposedWork = work.transpose(transposition)
        transposedRootStream = rootStream.transpose(transposition)
     
        ''' create PirtchCollectionSequencesObject '''
        pitchCollectionSequences = pitchCollections.PitchCollectionSequences(transposedWork) 
        
        
        ''' add root information '''
        rootAnal = rootAnalysis.RootAnalysis(pitchCollectionSequences)
        rootAnal.addRootInformation(transposedRootStream)
        
        
        rootAnal.setObservationData(observationPath)
        
    
manipDataSet = manipulateDataset.ManipulateDataSet(observationPath)
manipDataSet.createMainArrays()

print (str(corrputedFilesList))



