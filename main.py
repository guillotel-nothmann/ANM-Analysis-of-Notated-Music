'''
Created on Dec 14, 2019

@author: christophe
'''

if __name__ == '__main__':
    pass

''' imports '''
from music21 import converter
import logging, pitchCollections, dissonanceAnalysis

if __name__ == '__main__': pass  
 
''' configure logging '''
logging.basicConfig(level=logging.INFO)

''' get file '''
work = converter.parse('examples/1_Bransle_double.mei')
 
''' create PirtchCollectionSequencesObject '''
pitchCollectionSequences = pitchCollections.PitchCollectionSequences(work) 

''' dissonance analysis '''
dissonanceAnal = dissonanceAnalysis.DissonanceAnalysis(pitchCollectionSequences)
 
''' get analysis and print it in file '''
file = open('examples/1_Bransle_double.xml', "w")
xmlString = pitchCollectionSequences.getXMLRepresentation()
file.write(xmlString)
file.close