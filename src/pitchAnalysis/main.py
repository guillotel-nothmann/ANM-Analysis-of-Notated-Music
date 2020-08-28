from music21 import converter
import analysis
from pitchAnalysis import pitchAnal
from pitchAnalysis.pitchAnal import PitchAnalysis
 
 



if __name__ == '__main__':
    pass
 



    ''' get work '''
 
    
    work = converter.parse('/Users/christophe/Dropbox/Praetorius/source/Praetorius_Terpsichore/individuels/xml/001.xml')
    
    ''' create analysis object and get analyzed pitch list'''
    analysisObject = analysis.Analysis(work, False, False) #   adaptable frame,  hypotheses explored 
    workAnalyzedPitches = analysisObject.getAnalyzedPitches()
        
    
       
    
    
    
    pitchAnal = PitchAnalysis(workAnalyzedPitches, ["pitch.unicodeName"])
        
    pitchAnal.buildChart()