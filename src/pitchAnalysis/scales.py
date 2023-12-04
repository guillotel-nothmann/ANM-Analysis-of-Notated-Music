'''
Created on Dec 10, 2019

@author: christophe
'''
from music21 import scale, stream
import pitchCollections
from builtins import isinstance

class ScaleAnalysis(object):

    def __init__(self, workOrPitchCollectionSequence):
        self.pitchCollectionSequence = None
        ''' create analysis object and get analyzed pitch list'''
        
        if isinstance(workOrPitchCollectionSequence, stream.Stream): 
            self.pitchCollectionSequence = pitchCollections.PitchCollectionSequence(workOrPitchCollectionSequence)
        
        elif isinstance(workOrPitchCollectionSequence, pitchCollections.PitchCollectionSequence):
            self.pitchCollectionSequence = workOrPitchCollectionSequence
            
        
        if self.self.pitchCollectionSequence == None: return
        
        self.workAnalyzedPitches = self.pitchCollectionSequence.getAnalyzedPitches()
        
        
        
        ''' define chromatic steps  '''
        chromaticSteps = ['C-1', 'C1', 'C#1', 'D-1', 'D1', 'D#1', 'E-1', 'E1', 'E#1', 'F-1', 'F1', 'F#1', 'G-1', 'G1', 'G#1', 'A-1', 'A1', 'A#1', 'B-1', 'B1', 'B#1']
        
        
        ''' define  scales '''
        # octaves are only convention
        
        
        # diatonic scale
        
        
        ''' build diatonic scale on all chromatic pitches '''
        self.diatonicScaleList = []
        for refStep in chromaticSteps:
             
            self.diatonicScaleList.append(scale.DiatonicScale(refStep))

        ''' build pentatonic scale on all chromatic pitches'''
            
            
            
        ''' build zalzal scale on all chromatic ptiches '''
        print ('')    
    
 
                
    
    
    def buildScaleOn (self, refNote, scaleIntervals): 
        newNote = refNote
        noteList = [newNote]
        for interv in scaleIntervals:
            interv.noteStart =   newNote
            newNote = interv.noteEnd
            noteList.append(newNote)
            
        pitchList = [noteName.nameWithOctave for noteName in noteList] 
        builtScale = scale.ConcreteScale(pitches = pitchList)    
        
        return builtScale
    
    
    def getBestDiatonicScale (self):
        ''' loop over every scale ''' 
        scoreList = []
        
        for scale in self.diatonicScaleList:
            
            ''' get string list of pitch Colls '''
            pitchList = scale.getPitches()
            
            pitchCollList = [scalePitch.name for scalePitch in pitchList]
            
            'loop over every analyzed Pitch and test if this pitch is in scale'
            pitchesInScale = 0
            pitchesNotInScale = 0
            
            for analyzedPitch in self.workAnalyzedPitches:
                if analyzedPitch.pitch.name in pitchCollList:
                    pitchesInScale = pitchesInScale + 1
                else: 
                    pitchesNotInScale = pitchesNotInScale + 1
                    
            totalPitches = pitchesNotInScale + pitchesInScale
            scoreList.append(pitchesInScale / totalPitches)
            highestScore = max (scoreList)
            
        highestScoreList = []
        
        for counter, score in enumerate(scoreList) :
            if score == highestScore:
                highestScoreList.append(self.diatonicScaleList[counter])
                
                
                
                
        return highestScoreList
                
                 
            
            
                    
            
        
 
        
        