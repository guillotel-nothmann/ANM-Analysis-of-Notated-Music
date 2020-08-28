'''
Created on Dec 11, 2019

@author: christophe
'''
from music21 import stream, tree, note, chord, interval
from music21.chord import Chord 
from music21.note import Note

class Cadences (object):
   
     
   
     

    def __init__(self, work, partDictionary):
        self.work = work
        self.scoreTree = tree.fromStream.asTimespans(self.work, flatten=True, classList=(note.Note, chord.Chord))
        self.finalVerticalities = []
        self.semiFlatWork = self.work.semiFlat
        self.flatWork= self.work.flat
        self.partDictionary = partDictionary
        
        self.chordMeasureList = []
        self.intermediaryChordList = []
        self.finalChord = None
        
        
        
        self.cantusFinalis = None
        self.bassusFinalis = None
        
        self.cadenceDegrees = []
        
        self.identifyCadences (barlines = True) 
        self.identifyDegrees ()
      
        
        
    def identifyCadences(self, barlines = False):
        from music21 import expressions
        ''' used to extract "final" chords in a work: the last verticality of a piece and all verticalies before double bars, repetitions, etc.'''
        measureEndOffsetList = [] 
        verticalityList = []
        chordMeasureList = [] 
        
        if barlines == True:
        
            ''' loop over eveyer measure and check bar '''
            ''' if double bar or final bar, our repetition, get offset of last verticality in measure'''
           
            
            for measure in self.semiFlatWork.recurse().getElementsByClass(stream.Measure):
                if measure.rightBarline == None: continue
                if measure.rightBarline.type in ["final", "double"]:
                    
                    ''' get every measure corresponding to this start offset '''
                    measuresAtOffset = []
                    
                    for measure2  in self.semiFlatWork.recurse().getElementsByClass(stream.Measure):
                        if measure2.offset == measure.offset:
                            measuresAtOffset.append(measure2) 
                            
                    ''' sort according to highest offset '''
                    measuresAtOffset.sort(key=lambda x: x.highestOffset, reverse=True)
                    
                    highestOffsetMeasure = measuresAtOffset [0]
                    
                    
                    if (highestOffsetMeasure.offset + highestOffsetMeasure.highestOffset) not in measureEndOffsetList: measureEndOffsetList.append(highestOffsetMeasure.offset + highestOffsetMeasure.highestOffset)
                    
            
        ''' loop over notes and identify fermatas '''
        intermediaryCadencesOffsets = []
        finalCadenceOffsets = []                 
                        
                    
        for elementNote in self.flatWork.recurse().getElementsByClass(note.Note):
            if len (elementNote.expressions) >= 1:
                
                for elementExpression in elementNote.expressions:
                    if elementExpression.name == "fermata":
                        if elementExpression.shape in ['angled', 'normal']:
                            measureEndOffsetList.append (elementNote.offset)
                            intermediaryCadencesOffsets.append(elementNote.offset)
                            
                        if elementExpression.shape in ['square']: # finalis
                            measureEndOffsetList.append (elementNote.offset)
                            finalCadenceOffsets.append(elementNote.offset)
                            
                        
             
        
                    
        measureEndOffsetList.sort()
        
        if barlines == True:
          
            
            for counter, measureEndOffset in enumerate(measureEndOffsetList):
                if counter + 1 < len(measureEndOffsetList):  intermediaryCadencesOffsets.append(measureEndOffset)
                else: finalCadenceOffsets.append(measureEndOffset)
                
            
        
        
        
        
        intermediaryCadencesOffsets.sort()
        finalCadenceOffsets.sort()
        
        intermediaryChordList = []
        finalChordList = []
         
        
        for measureEndOffset in measureEndOffsetList:
            verticality = self.scoreTree.getVerticalityAtOrBefore(measureEndOffset)
            verticalityList.append(verticality) 
            chordV = verticality.toChord() 
            chordMeasureList.append([chordV, verticality.measureNumber]) 
            
        for measureEndOffset in intermediaryCadencesOffsets:
            verticality = self.scoreTree.getVerticalityAtOrBefore(measureEndOffset)
            verticalityList.append(verticality) 
            chordV = verticality.toChord() 
            intermediaryChordList.append([chordV, verticality.measureNumber]) 
            
        for measureEndOffset in finalCadenceOffsets:
            verticality = self.scoreTree.getVerticalityAtOrBefore(measureEndOffset)
            verticalityList.append(verticality) 
            
            
            for part in self.work.recurse().getElementsByClass(stream.Part):
                
                modalPart = self.partDictionary[part.partName]
                element = part.flat.getElementAtOrBefore(measureEndOffset)
                if type(element) == Note: modalPart.finalis = element
                
                
                ### structural parts - this should be removed
                if part.name == "Cantus": 
                    self.cantusFinalis = part.flat.getElementAtOrBefore(measureEndOffset)
                    if type(self.cantusFinalis) == Note: self.cantusFinalis = self.cantusFinalis.pitch.nameWithOctave  
                if part.name == "Altus": 
                    self.altusFinalis = part.flat.getElementAtOrBefore(measureEndOffset)
                    if type(self.altusFinalis) == Note: self.altusFinalis = self.altusFinalis.pitch.nameWithOctave
                if part.name == "Tenor": 
                    self.tenorFinalis = part.flat.getElementAtOrBefore(measureEndOffset)
                    if type(self.tenorFinalis) == Note: self.tenorFinalis = self.tenorFinalis.pitch.nameWithOctave
                if part.name == "Quintus": 
                    self.quintusFinalis = part.flat.getElementAtOrBefore(measureEndOffset)
                    if type(self.quintusFinalis) == Note: self.quintusFinalis = self.quintusFinalis.pitch.nameWithOctave
                if part.name == "Bassus": 
                    self.bassusFinalis = part.flat.getElementAtOrBefore(measureEndOffset)
                    if type(self.bassusFinalis) == Note: self.bassusFinalis = self.bassusFinalis.pitch.nameWithOctave
                    
                    
                
                
                

            
            chordV = verticality.toChord() 
            finalChordList.append([chordV, verticality.measureNumber]) 
            
        
        self.chordMeasureList = chordMeasureList
        self.intermediaryChordList = intermediaryChordList
        
        if len (finalChordList) > 0:
            self.finalChord = finalChordList[0]  
        else:
            self.finalChord = None  
            
    
    def getIntermediaryCadences (self): 
        intermediaryCadences = []
        
        for cadencePoint in self.intermediaryChordList:
            intermediaryCadences.append(cadencePoint[0].pitchedCommonName)
            
        
        return intermediaryCadences
    
    
    def getFinalCadence (self):
        return self.finalChord
    
    def getDegrees (self, param = "succession"):
        
        if param == "succession":
            degreeString = ""
            for cDegree in self.cadenceDegrees:
                degreeString = degreeString + cDegree[0] + "-"
                
            degreeString = degreeString [:-1]
            return degreeString
        
        
        if param == "points":
            ''' points will be sorted according to occurrence'''
            
     
            cadencePointList = []
            cadencePointOccurrenceList = []
             
            for cDegree in self.cadenceDegrees:
                if cDegree[0] not in cadencePointList: cadencePointList.append(cDegree[0])
                
            for cPoint in cadencePointList:
                occurrence = 0
                for cDegree in self.cadenceDegrees:
                    if cDegree[0]== cPoint: occurrence = occurrence + 1
                    
                cadencePointOccurrenceList.append([cPoint, occurrence])
                
            
            cadencePointOccurrenceList.sort(key=lambda x: x[0], reverse = False) # sort on occurrence ?
            
            cadencePointList.clear()
            for cadencePoint in cadencePointOccurrenceList:
                cadencePointList.append(cadencePoint[0])
            return cadencePointList 
        return None
    
 
    
    def identifyDegrees(self):
        
        ''' check if cadences are identifies '''
        if len (self.chordMeasureList) == 0: return []
        
        stepDictionary = {}
        
        ''' associate final chord to I and and create dictionary of all other scale steps'''
        referenceStep = self.finalChord[0].root().step
        
        diatonicSteps = ["A", "B", "C", "D", "E", "F", "G"]
        referenceIndex = None
        
        
        
        for counter, diatonicStep in enumerate(diatonicSteps):
            if diatonicStep == referenceStep: referenceIndex = counter
                
        
        
        stepDictionary[diatonicSteps [referenceIndex]] = "I" 
        stepDictionary[ diatonicSteps [(referenceIndex + 1) % 7]] = "II"
        stepDictionary [diatonicSteps [(referenceIndex + 2) % 7]] = "III"
        stepDictionary [diatonicSteps [(referenceIndex + 3) % 7]] = "IV"
        stepDictionary [diatonicSteps [(referenceIndex + 4) % 7]] = "V"
        stepDictionary [diatonicSteps [(referenceIndex + 5) % 7]] = "VI"
        stepDictionary [diatonicSteps [(referenceIndex + 6) % 7]] = "VII"
       
        
        ''' loop over intermediaryChordList and identifiy scale steps '''
        cadenceDegrees = []
        
        for counter, chordMeasure in enumerate (self.chordMeasureList): 
            cadenceDegrees.append([stepDictionary.get(chordMeasure[0].root().step), chordMeasure[1]])
            
        
        
        self.cadenceDegrees = cadenceDegrees
        
        
        
           
        