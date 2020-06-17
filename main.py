'''
Created on Dec 14, 2019

@author: christophe
'''
import rootAnalysis

if __name__ == '__main__':
    pass

''' imports '''
from music21 import converter
import logging, pitchCollections, dissonanceAnalysis

if __name__ == '__main__': pass  
 
''' configure logging '''
logging.basicConfig(level=logging.INFO)

''' get file '''
work = converter.parse('examples/787.mei')
 
''' create PirtchCollectionSequencesObject '''
pitchCollectionSequences = pitchCollections.PitchCollectionSequences(work) 

rootAnal = rootAnalysis.RootAnalysis(pitchCollectionSequences)
observationData = rootAnal.getObservationData()

#''' dissonance analysis '''
#dissonanceAnal = dissonanceAnalysis.DissonanceAnalysis(pitchCollectionSequences)
 
''' get analysis and print it in file '''
#file = open('examples/787.xml', "w")
#xmlString = pitchCollectionSequences.getXMLRepresentation() 
#file.write(xmlString)
#file.close