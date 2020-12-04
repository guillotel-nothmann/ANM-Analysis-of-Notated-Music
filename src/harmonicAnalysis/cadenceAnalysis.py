'''
Created on Dec 11, 2019

@author: christophe
'''
from music21 import stream, tree, note, chord, interval
from music21.chord import Chord 
from music21.note import Note
import copy, string, random


class CompareCadenceAnalyses(object):
    def __init__(self, workAuthList):
        self.workAuthList = workAuthList
        self.referenceStream = copy.deepcopy(workAuthList[0][0])
        
        self.compareStreams()
        
        
        
 
        
        
    
    def compareStreams (self):
        
         
            
        for referenceNote in self.referenceStream.flat.getElementsByClass([note.Note]): 
            interpretationDictionary = {}
            
            
            #
            '''loop over every analysis streams and get information '''
            for analysis in self.workAuthList:
                flatAnalysis = analysis[0].flat
                analysisNote = flatAnalysis.getElementAtOrBefore(referenceNote.offset, [note.Note]) 
                
                analysisNoteHasCadence = self.noteHasCadence(analysisNote)
                interpretationDictionary = self.addInterpretationToDictionary(analysisNoteHasCadence, analysis[1], interpretationDictionary)
                
                
            '''check if more then one interpretation, is so, highlight '''
                
            if len (interpretationDictionary) >1:
                referenceNote.style.color = 'red'
                referenceNote.lyric = self.getInterpretationString(interpretationDictionary)
                
                
    
    
    
    def addInterpretationToDictionary (self,interpretation, interpret, interpretationDictionary):
        if not str(interpretation) in interpretationDictionary: 
            interpretationDictionary[str(interpretation)] = []
        
        interpretationDictionary[str(interpretation)].append(interpret)
        
        return interpretationDictionary
    
    def getInterpretationString (self, interpretationDictionary):
        interpretationString = ""
        for element in interpretationDictionary:
            
            interpretationString = interpretationString + element + ": " + str (interpretationDictionary[element]) + "\n"
            
        return interpretationString
            
            
        
         
        
        
    
    def noteHasCadence (self, elementNote):
        for elementExpression in elementNote.expressions:
            if elementExpression.name == "fermata":
                if elementExpression.shape == 'normal':
                    return "normal"
                
                elif elementExpression.shape == 'angled':
                    return "angled"
                
                elif elementExpression.shape == 'square':
                    return "square"
                         
                         
    
        return None
        
                            
                            
    
    
    def removeCadenceIndications(self, workStream):
        ''' removes all fermates which could be interpreted as cadence indications '''
        
        streamWithoutCadences = copy.deepcopy(workStream)
        
        for elementNote in streamWithoutCadences.recurse().getElementsByClass(note.Note):
            if len (elementNote.expressions) >= 1:
                
                elementNote.expressions.clear()
        return streamWithoutCadences
        
        
        
        

class Cadences (object):
    def __init__(self, work, partDictionary = None, barLines = False, partName = "Bassus continuus"):
        self.work = work
        self.scoreTree = tree.fromStream.asTimespans(self.work, flatten=True, classList=(note.Note, chord.Chord))
        self.finalVerticalities = []
        self.semiFlatWork = self.work.semiFlat
        self.flatWork= self.work.flat
        self.partDictionary = partDictionary
         
        
        #self.chordMeasureList = []
        #self.intermediaryChordList = []
        #self.cantusFinalis = None
        #self.bassusFinalis = None
        
        self.cadencePointDictionary = {}
        
        #self.cadenceDegrees = []
        
        
 
        for part in work.parts:
            if part.partName == partName: self.cadencePart = part.flat

        
        if barLines == False:
            self.identifyCadencesFromAnnotations()
        else:
            self.identifyCadencesFromBarLines()    
        
        self.finalChord = self.getFinalChord()
        
        #self.identifyCadences (barlines = False) 
        self.identifyDegrees ()
        
        
    
    
    def id_generator(self, size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))
    
    def addCadenceToDictionary(self, cadenceType, cadenceSubType, cadenceOffset, cadenceDegree, cadenceChord, cadenceRoot):
        
        
        ''' generate cadence id used as key '''
        cadenceId = self.id_generator(6)
        while cadenceId in self.cadencePointDictionary:
            cadenceId = self.id_generator(6)
            
        dictionaryEntry = {
            "cadenceType": cadenceType, 
            "cadenceSubType" : cadenceSubType, 
            "cadenceOffset": cadenceOffset,
            "cadenceDegree": cadenceDegree,
            "cadenceChord": cadenceChord,
            "cadenceRoot": cadenceRoot
            
            }
        
        self.cadencePointDictionary[cadenceId] = dictionaryEntry
            
    def getCadenceAtOffset (self, offset):
        '''returns cadence at given offset '''
        
        for unused_key, element,  in self.cadencePointDictionary.items():
            if element["cadenceOffset"] == offset:
                return element
            
        return None 
           
            
    def getFinalChord(self):
        for unused_elementKey, element in self.cadencePointDictionary.items():
            if element["cadenceType"] == "final":
                return element["cadenceChord"]
        return None
                
    
    def getCadences (self, cadenceRoot = None, cadenceType = None, cadenceSubType= None):
        cadenceList = [] 
        
        for unused_elementKey, element in self.cadencePointDictionary.items():
            
            if cadenceRoot != None:
                if cadenceRoot != element["cadenceRoot"]: continue
                
            if cadenceType != None:
                if cadenceType != element ["cadenceType"]: continue
                
            if cadenceSubType != None:
                if cadenceSubType != element["cadenceSubType"]: continue
                
            cadenceList.append (element)
            
        return cadenceList 
                
            
                
             
   
    def identifyCadencesFromAnnotations (self):
        for elementNote in self.cadencePart.recurse().getElementsByClass(note.Note):
                if len (elementNote.expressions) >= 1:
                    
                    for elementExpression in elementNote.expressions:
                        if elementExpression.name == "fermata":
                            if elementExpression.shape in ['angled']:
                                cadenceType = "intermediary"
                                cadenceSubType = "angled"
                                
                            elif elementExpression.shape in ['normal']: 
                                cadenceType = "intermediary"
                                cadenceSubType = "normal"
                                
                            elif elementExpression.shape in ['square']: 
                                cadenceType = "final"
                                cadenceSubType = "square"
                            else:
                                cadenceType = "other"
                                cadenceSubType = "other"
                                
                            cadenceOffset = elementNote.offset                           
                            verticality = self.scoreTree.getVerticalityAtOrBefore(cadenceOffset)
                            cadenceChord = verticality.toChord() 
                            cadenceRoot = cadenceChord.root().name
                            
                            
                        self.addCadenceToDictionary(cadenceType, cadenceSubType, cadenceOffset, None, cadenceChord, cadenceRoot)
                                
                                
 
    def identifyCadencesFromBarLines(self): 
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
                highestMeasureOffset = highestOffsetMeasure.rightBarline.offset + highestOffsetMeasure.offset
                
                verticality = self.scoreTree.getVerticalityAtOrBefore(highestMeasureOffset) ## this will get the last verticality, even before offset
                
                
                
                cadenceOffset = verticality.offset
                
                ''' check if this offset is not in dictionary yet if not, add cadence '''
                
                if self.getCadenceAtOffset(cadenceOffset)!= None: continue
                
                if measure.rightBarline.type == "final" and highestMeasureOffset == self.semiFlatWork.highestOffset:
                    cadenceType = "final" 
                    cadenceSubType = None
                else:
                    cadenceType = "intermediary"
                    cadenceSubType = None
                
                 
                cadenceChord = verticality.toChord() 
                cadenceRoot = cadenceChord.root().name
                
                self.addCadenceToDictionary(cadenceType, cadenceSubType, cadenceOffset, None, cadenceChord, cadenceRoot)
                 
 
    
    def identifyDegrees(self):
        
        ''' check if cadences are identified '''
        if len (self.cadencePointDictionary) == 0: return []
        if self.finalChord == None: return []
        
        stepDictionary = {}
        
        ''' associate final chord to I and and create dictionary of all other scale steps'''
        referenceStep = self.finalChord.root().step
        
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
       
        
        ''' loop over cadence points and identifiy scale steps '''
        for unused_cadenceKey, cadenceElement in self.cadencePointDictionary.items():
            
            cadenceChord = cadenceElement["cadenceChord"]
            cadenceDegree = stepDictionary.get(cadenceChord.root().step)
            
            cadenceElement["cadenceDegree"] = cadenceDegree
             
        
        
        
           
        