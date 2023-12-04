'''
Created on Apr 5, 2022

@author: christophe
'''
from music21 import converter, expressions
import pitchCollections
from harmonicAnalysis import cadenceAnalysis

if __name__ == '__main__':
    pass

filePath = "/Users/christophe/Documents/Praetorius/Terpsichore/xml/016.musicxml"

''' parse file'''
work = converter.parse(filePath)

 



''' create pitch coll sequence '''
pitchCollectionSequence = pitchCollections.PitchCollectionSequence(work)

''' run cadence analysis '''
cadenceAnal = cadenceAnalysis.CadenceAnalysis(pitchCollectionSequence)


''' display results '''
pitchCollectionSequence.setAnnotationsToStream_Expressions()


work.write('musicxml', "/Users/christophe/Documents/Praetorius/Terpsichore/xmlWithCadences/016.musicxml")

