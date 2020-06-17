'''
Created on Mar 27, 2020

@author: christophe
'''

### Thia is used to confront the labels with the model output and to highlight the wrong roots in the score

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


workDirectoryString = '/Users/christophe/Documents/GitHub/PraetoriusTerpsichore/xml/'
rootDirectoryString = '/Users/christophe/Documents/GitHub/PraetoriusTerpsichore/xmlWithRoot/'
observationPath = '/Users/christophe/Documents/GitHub/PraetoriusTerpsichore/observations/'
rootDirectoryStringCorr = '/Users/christophe/Documents/GitHub/PraetoriusTerpsichore/xmlWithRootCorr/'
modelPath = rootDirectoryName + '/models/rootModelPraetorius.h5'

corrputedFilesList = []

for file in os.listdir(rootDirectoryString):
    fileName = os.fsdecode(file)
    if fileName.endswith(".musicxml")== False: continue
   
    
    
     
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
        
    
     
    ''' create PirtchCollectionSequencesObject '''
    pitchCollectionSequences = pitchCollections.PitchCollectionSequences(work) 
    
    
    ''' confront root analysis with labels '''
    
    
    ''' add root information '''
    rootAnal = rootAnalysis.RootAnalysis(pitchCollectionSequences)
    rootAnal.confrontModelWithLabels(modelPath, rootStream)
    
    ''' add stream with roots to score '''
    bassStream = rootAnal.getFundamentalBass()
    work.insert(0, bassStream)
    work.write('musicxml', rootDirectoryStringCorr + fileName)
    
    
     

print (str(corrputedFilesList))
