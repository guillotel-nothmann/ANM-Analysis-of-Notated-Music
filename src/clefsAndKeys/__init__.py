
''' used for key and clef extraction, and tonal types, for example in modal analysis'''
from clefsAndKeys.clefsAndKeysAnal import ClefsAndKeysAnalysis
from pitchAnalysis.scales import ScaleAnalysis

''' input is a parsed musical work'''
''' output is an object with dimensions for parts, clefs for parts etc. '''

from music21 import converter

if __name__ == '__main__':
    pass


    workPath = '/Users/christophe/Dropbox/Praetorius/source/Praetorius_Terpsichore/individuels/mei/001.mei'
    work = converter.parse(workPath)
    
    
    scaleAnal = ScaleAnalysis(work)    
    bestDiatonicScales = scaleAnal.getBestDiatonicScale()
    
    AndKAnal = ClefsAndKeysAnalysis(work)
     
    print (AndKAnal.getAlterations('list'))
    print (AndKAnal.getAmbitus('list'))
    print (AndKAnal.getClefs('list'))
    print (AndKAnal.getPartNames('list'))
    print (AndKAnal.getFinalis('list'))
    print (bestDiatonicScales)
    
   
