'''
Created on Dec 11, 2019

@author: christophe
'''
from music21 import stream, tree, note, chord, interval, converter, key, pitch
from music21.note import Note
import copy, string, random, os
from builtins import  list, isinstance
import manipulateDataset
from pitchCollections import PitchCollectionSequence
from tensorflow import keras
import numpy as np
from music21.chord import Chord


class CadenceAnalysis (object):
    
    def __init__(self, pitchCollectionSequence, analyzeWithModel = True):
        
        
        self.pitchCollectionSequence =  pitchCollectionSequence
        self.scoreTree = self.pitchCollectionSequence.scoreTree
        self.overallScore = None
        self.lowestScore = None
        self.highestScore = None
        self.rootDictionary = {}
        
        
        if analyzeWithModel == True: self.analyzeWithModel()
        
    def analyzeWithModel(self, modelPath = '/Users/Christophe/Desktop/dataset/cadenceModel.h5'): 
        observationDictionary = {0: "C_A", 1:"C_P", 2:"C_F", 
                                 3:"A_A", 4:"A_P", 5:"A_F", 
                                 6:"T_A", 7:"T_P", 8:"T_F", 
                                 9:"B_A", 10:"B_P", 11:"B_F",
                                 
                                 12:"PC_A", 13:"PC_P", 14:"PC_F", 
                                 15:"PA_A", 16:"PA_P", 17:"PA_F", 
                                 18:"PT_A", 19:"PT_P", 20:"PT_F", 
                                 21:"PB_A", 22:"PB_P", 23:"PB_F", 
                                 
                                 24:None
                                 }   
        
        ''' run model '''
       
        self.model = keras.models.load_model(modelPath)
        self.model.compile(optimizer="adam",  loss='sparse_categorical_crossentropy',metrics=['accuracy'])
        self.model.summary()
        
        scoreList = [] 
         
        for pitchCollection in self.pitchCollectionSequence.explainedPitchCollectionList:
            ''' loop over all analyzed pitches ''' 
            for analysedPitch in pitchCollection.analyzedPitchList:
                
            
                observationArray = np.array(self.pitchCollectionSequence.getObservationsForPitchIdChromatic(analysedPitch.id, 5, pitchCollection.offset))
                feature = np.array([observationArray])
                            
                ''' make prediction from observation list '''
                predictions = self.model.predict(feature)
                
                ''' get highest score identifiy index '''
                highestScore = max(predictions[0]) 
                for index in range (0, len(predictions[0])):
                    if predictions[0][index] == highestScore:
                        break
                    
                analysedPitch.pitchType = observationDictionary[index]
                analysedPitch.probability = highestScore
            
                scoreList.append(analysedPitch.probability)
                
                #print (str(analysedPitch.pitchType) + " " + str(pitchCollection.offset)+ " " + str(analysedPitch.part))
            
            
        scoreTotal = 0
        for score in scoreList:
            scoreTotal = scoreTotal + score
            
        scoreList.sort()
        self.overallScore = scoreTotal / len (scoreList)
        self.lowestScore = scoreList[0]
        self.highestScore = scoreList [-1]
          


class CreateCadenceObservations(object):
    ''' this class is used to make cadence observations used to train a neural network '''
    
    def __init__(self, dataPath, cadenceZone=False):
        
        self.dataPath = dataPath
        
        corruptedFileList = []
        
        
        ''' loop over individual works '''
        for file in os.listdir(dataPath):
            fileName = os.fsdecode(file)
            if fileName.endswith(".musicxml")== False: continue
            print ("Reading file " + fileName)
            
            
            ''' parse work '''
            work = converter.parse(dataPath + fileName)
            
            ''' generate transpositions to maximize training data '''
            keyElement = None
            for element in work.flat.getElementsByClass(key.KeySignature):
                keyElement = element
                break
            
            if keyElement == None:
                corruptedFileList.append(fileName)
                break
            
            transpositionList = self.getTranspositionIntervals(keyElement.sharps, 0)
            
            
            for transposition in transpositionList:
                
                ''' create pitch collection object for each transposition '''
                transposedWork = work.transpose(transposition)
                pitchCollSequence = PitchCollectionSequence(transposedWork)
                
                ''' create Cadences object for the stream '''        
                cadencesObj = Cadences(transposedWork, analysisMode = "voiceAnnotations")
                
                
                ''' add analytical information to pitch coll sequence : is part of cadence, cadence element '''
                
                ''' cadence zones '''
                if cadenceZone == False: 
                    for annotation in cadencesObj.annotationList:
                             
                        for element in annotation["elements"]:
                        
                            for analyzedElement in pitchCollSequence.getAnalyzedPitchCorrespondingToId(element.id):
                                analyzedElement.pitchType = annotation["content"]
                                
                else: 
                    for cadence in cadencesObj.cadenceList:
                        
                        ''' get pitchColls corresponding to offsets '''
                        pitchCollSubSet = pitchCollSequence.getPitchCollectionSubset(cadence.offsetList[0], cadence.offsetList[-1])
                        
                        for pitchColl in pitchCollSubSet:
                            for analyzedPitch in pitchColl.analyzedPitchList:
                                analyzedPitch.pitchType = "C"
            
                ''' set observations for this stream '''
                self.setObservationData(pitchCollSequence, cadenceZone)
        
        manipDataSet = manipulateDataset.ManipulateDataSet(dataPath)
        manipDataSet.createMainArrays()
        
        
    def setObservationData(self, pitchCollSequence, cadenceZone):
        if cadenceZone == True:
            observationDictionary = {"C": 0, None:1 }
            
        else:
            observationDictionary = {"C_A": 0, "C_P": 1, "C_F": 2, 
                                     "A_A": 3, "A_P": 4, "A_F": 5, 
                                     "T_A": 6, "T_P": 7, "T_F": 8, 
                                     "B_A": 9, "B_P":10, "B_F":11,
                                     
                                     "PC_A": 12, "PC_P": 13, "PC_F": 14, 
                                     "PA_A": 15, "PA_P": 16, "PA_F": 17, 
                                     "PT_A": 18, "PT_P": 19, "PT_F": 20, 
                                     "PB_A": 21, "PB_P":22, "PB_F":23, 
                                     None:24
                                     }
        
        
        pitchCollSequence.setPitchObservations(self.dataPath, observationDictionary)
        
     
    
    def getTranspositionIntervals (self, sharps=0, maxSharps=0): 
    
    
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
        
        
class Cadence (object):
    def __init__(self, annotation):
        
        self.cantusHasFinalis = []
        self.cantusHasPenultima = []
        self.cantusHasAntepenultima = []
        
        self.altusHasFinalis = []
        self.altusHasPenultima = []
        self.altusHasAntepenultima = []
        
        self.tenorHasFinalis = []
        self.tenorHasPenultima = []
        self.tenorHasAntepenultima = []
        
        self.bassusHasFinalis = []
        self.bassusHasPenultima = []
        self.bassusHasAntepenultima = []
        
        self.cantusTenorAntepenultima = []
        self.cantusTenorPenultima = []
        self.cantusTenorFinalis = []
        self.cantusBassusAntepenultima = []
        self.cantusBassusPenultima = []
        self.cantusBassusFinalis = [] 
        self.tenorBassusAntepenultima = []
        self.tenorBassusPenultima = []
        self.tenorBassusFinalis = []
        
        
        self.cantusAPDiminutions = []
        self.cantusPFDiminutions = []
        self.altusAPDiminutions = []
        self.altusPFDiminutions = []
        self.tenorAPDiminutions = []
        self.tenorPFDiminutions = []
        self.bassusAPDiminutions = []
        self.bassusPFDiminutions = []
        self.isPCadence = False
        self.hasDiminutions = False
        
        
        # used to store label information that describe the cadence functions for example for JRP
        self.labelList = []
        
        self.offsetList = []
        self.measureNumberList = []
        
        self.contentDictionary = {
            "C_A": self.cantusHasAntepenultima,
            "C_P": self.cantusHasPenultima,
            "C_F": self.cantusHasFinalis,
            "PC_A": self.cantusHasAntepenultima,
            "PC_P": self.cantusHasPenultima,
            "PC_F": self.cantusHasFinalis,
            
            "C": self.cantusHasFinalis, # Josquin annotation
            "c": self.cantusHasFinalis, # Josquin annotation
            "y": self.cantusHasFinalis, # Josquin annotation
            "d": self.cantusHasFinalis, # Josquin annotation
            

            
            
            "A_A": self.altusHasAntepenultima,
            "A_P": self.altusHasPenultima,
            "A_F": self.altusHasFinalis,
            "PA_A": self.altusHasAntepenultima,
            "PA_P": self.altusHasPenultima,
            "PA_F": self.altusHasFinalis,
            
            "A": self.altusHasFinalis, # Josquin annotation
            "w": self.altusHasFinalis, # Josquin annotation
            "g": self.altusHasFinalis, # Josquin annotation
            
            "T_A": self.tenorHasAntepenultima,
            "T_P": self.tenorHasPenultima,
            "T_F": self.tenorHasFinalis,
            "PT_A": self.tenorHasAntepenultima,
            "PT_P": self.tenorHasPenultima,
            "PT_F": self.tenorHasFinalis, 
            
            "T": self.tenorHasFinalis, #Josquin
            "t": self.tenorHasFinalis, #Josquin
            "z": self.tenorHasFinalis, #Josquin
            "e": self.tenorHasFinalis, #Josquin
            "et": self.tenorHasFinalis, #Josquin
             
            
            
            "B_A": self.bassusHasAntepenultima,
            "B_P": self.bassusHasPenultima,
            "B_F": self.bassusHasFinalis,
            "PB_A": self.bassusHasAntepenultima,
            "PB_P": self.bassusHasPenultima,
            "PB_F": self.bassusHasFinalis,
            
            "B":  self.bassusHasFinalis, # Josquin
            "b":  self.bassusHasFinalis, # Josquin
            "L": self.bassusHasFinalis, # Josquin
            "P": self.bassusHasFinalis, # Josquin 
            "u": self.bassusHasFinalis, # Josquin 
            "x": self.bassusHasFinalis, # Josquin 
            "f": self.bassusHasFinalis, # Josquin 
            "bf": self.bassusHasFinalis, # Josquin 
            
            
            "C_A_T_A": self.cantusTenorAntepenultima,
            "C_P_T_P": self.cantusTenorPenultima,
            "C_F_T_F": self.cantusTenorFinalis,
            "C_A_B_A": self.cantusBassusAntepenultima,
            "C_P_B_P": self.cantusBassusPenultima,
            "C_F_B_F": self.cantusBassusFinalis, 
            "T_A_B_A": self.tenorBassusAntepenultima,
            "T_P_B_P": self.tenorBassusPenultima,
            "T_F_B_F": self.tenorBassusFinalis,
            
            "PC_A_PT_A": self.cantusTenorAntepenultima,
            "PC_P_PT_P": self.cantusTenorPenultima,
            "PC_F_PT_F": self.cantusTenorFinalis,
            "PC_A_PB_A": self.cantusBassusAntepenultima,
            "PC_P_PB_P": self.cantusBassusPenultima,
            "PC_F_PB_F": self.cantusBassusFinalis, 
            "PT_A_PB_A": self.tenorBassusAntepenultima,
            "PT_P_PB_P": self.tenorBassusPenultima,
            "PT_F_PB_F": self.tenorBassusFinalis,
            
            
            "C_A_C_P": self.cantusAPDiminutions,
            "C_P_C_F": self.cantusPFDiminutions,
            "A_A_A_P": self.altusAPDiminutions,
            "A_P_A_F": self.altusPFDiminutions,
            "T_A_T_P": self.tenorAPDiminutions,
            "T_P_T_F": self.tenorPFDiminutions,
            "B_A_B_P": self.cantusAPDiminutions,
            "B_P_B_F": self.cantusPFDiminutions,
            
            "PC_A_PC_P": self.cantusAPDiminutions,
            "PC_P_PC_F": self.cantusPFDiminutions,
            "PA_A_PA_P": self.altusAPDiminutions,
            "PA_P_PA_F": self.altusPFDiminutions,
            "PT_A_PT_P": self.tenorAPDiminutions,
            "PT_P_PT_F": self.tenorPFDiminutions,
            "PB_A_PB_P": self.cantusAPDiminutions,
            "PB_P_PB_F": self.cantusPFDiminutions,
            
            
            
            
            }
        
        self.addAnnotation(annotation)
        
        
    
    def identvalProgressions (self):
        for pair in [["C_A", "T_A"],["C_P", "T_P"],["C_F", "T_F"], ["C_A", "B_A"],["C_P", "B_P"],["C_F", "B_F"], ["T_A", "B_A"], ["T_P", "B_P"], ["T_F", "B_F"]]:
            if len(self.contentDictionary[pair[0]])!= 0 and len(self.contentDictionary[pair[1]]) != 0:
                self.contentDictionary[pair[0]+ "_" + pair[1]].append(interval.Interval(self.contentDictionary[pair[0]][0], self.contentDictionary[pair[1]][0]))
 
    def diminutions (self):
        ''' cantus diminutions '''
        
        for pair in [["C_A", "C_P"],["C_P", "C_F"],["A_A", "A_P"],["A_P", "A_F"],["T_A", "T_P"],["T_P", "T_F"], ["B_A", "B_P"],["B_P", "B_F"]]:
            if len(self.contentDictionary[pair[0]])!=0 and len(self.contentDictionary[pair[1]]) !=0:
                constitutiveNoteA = self.contentDictionary[pair[0]][0]
                constitutiveNoteB = self.contentDictionary[pair[1]][0]
                
                if isinstance(constitutiveNoteA.activeSite,  stream.Stream):
                    streamPart=constitutiveNoteA.activeSite
                    
                    for noteElement in  streamPart.flat.getElementsByOffset(offsetStart=constitutiveNoteA.offset, offsetEnd=constitutiveNoteB.offset, includeEndBoundary=False, classList=[note.Note]):
                        if noteElement.offset == constitutiveNoteA.offset: continue
                        self.contentDictionary[pair[0] + "_" + pair[1]].append(noteElement)
                        self.hasDiminutions = True
                 
            
    def checkJosquinClasses (self, work):
        ''' these are the classes used in the Josquin cadence ontology '''
        self.simpleCadence = False
        self.formalCadence = False #OK
        self.plagalCadence = False #P
        self.phrygianCadence = False  #OK 
        self.otherCadence = False
        
        self.leapingContratenor = False # L
        self.bassizansEvadedByStepUp = False # b
        self.cantizansEvadedByFourthUp = False # c
        self.tenorizansEvadedByStepUp = False # t
        self.bassizansEvadedByThirdDown = False # u
        self.bassizansEvadedByDropout = False # x
        self.cantizansEvadedByDropout = False # y
        self.tenorizansEvadedByDroupout = False # z
        self.altizansEvadedByDropout = False # w
        self.cantizansEvadedByContinuation = False # d
        self.tenorizansEvadedByContinuation = False # e
        self.bassizansEvadedByContinuation = False # f
        self.altizansEvadedByContinuation = False # g
        
        
        for label in self.labelList:
            if label == "L": self.leapingContratenor = True
            elif label == "b": self.bassizansEvadedByStepUp = True
            elif label == "c": self.cantizansEvadedByFourthUp = True
            elif label == "t": self.tenorizansEvadedByStepUp = True
            elif label == "u": self.bassizansEvadedByThirdDown = True
            elif label == "x": self.bassizansEvadedByDropout = True
            elif label == "y": self.cantizansEvadedByDropout = True
            elif label == "z": self.tenorizansEvadedByDroupout = True
            elif label == "w": self.altizansEvadedByDropout = True
            elif label == "d": self.cantizansEvadedByContinuation = True 
            elif label == "e": self.tenorizansEvadedByContinuation = True 
            elif label == "f": self.bassizansEvadedByContinuation = True 
            elif label == "g": self.altizasEvadedByContinuation = True 
            
            elif label == "bf":
                self.bassizansEvadedByStepUp = True
                self.bassizansEvadedByContinuation = True
                
            elif label == "et":
                self.tenorizansEvadedByContinuation = True 
                self.tenorizansEvadedByStepUp = True
             
        
        
        ''' get part information '''
                    
        cantusFinalis = None
        cantusPenultima = None
        cantusAntePenultima = None
        
        tenorFinalis = None
        tenorPenultima = None # this has to be the cantus offset 
        tenorAntePenultima = None # 
        
        bassusFinalis = None
        bassusPenultima = None
        bassusAntePenultima = None
        
        if len (self.cantusHasFinalis) != 0 : 
            cantusFinalis = self.cantusHasFinalis[0] 
            cantusPenultima = self.getNoteBeforeInPart(work, cantusFinalis)
            cantusAntePenultima = self.getNoteBeforeInPart(work, cantusPenultima)
            
            if isinstance(cantusPenultima, Note): self.cantusHasPenultima.append(cantusPenultima)
            if isinstance(cantusAntePenultima, Note): self.cantusHasAntepenultima.append(cantusAntePenultima)
        
        if len (self.tenorHasFinalis) != 0 :  
            tenorFinalis = self.tenorHasFinalis[0]
            if cantusPenultima != None: # if cantus exists, use the cantus offset
                tenorPenultima = self.getNoteAtOffsetInPart(work, tenorFinalis, cantusPenultima.offset) 
                tenorAntePenultima = self.getNoteBeforeInPart(work, tenorPenultima, cantusPenultima.offset)
            else:
                tenorPenultima = self.getNoteBeforeInPart(work, tenorFinalis)
                tenorAntePenultima = self.getNoteBeforeInPart(work, tenorPenultima)
                
            if isinstance(tenorPenultima, Note): self.tenorHasPenultima.append(tenorPenultima)
            if isinstance(tenorAntePenultima, Note): self.tenorHasAntepenultima.append(tenorAntePenultima)
                
        
        if len (self.bassusHasFinalis) != 0:
            bassusFinalis = self.bassusHasFinalis[0]
            
            if cantusPenultima != None: # if cantus exists, use the cantus offset
                bassusPenultima = self.getNoteAtOffsetInPart(work, bassusFinalis, cantusPenultima.offset) 
            else:
                bassusPenultima = self.getNoteBeforeInPart(work, bassusFinalis)
                
            if cantusAntePenultima != None: # if cantus exists, use the cantus offset
                bassusAntePenultima = self.getNoteAtOffsetInPart(work, bassusPenultima, cantusAntePenultima.offset) 
            else:
                bassusAntePenultima = self.getNoteBeforeInPart(work, bassusPenultima)

            if isinstance(bassusPenultima, Note): self.bassusHasPenultima.append(bassusPenultima)
            if isinstance(bassusAntePenultima, Note): self.bassusHasAntepenultima.append(bassusAntePenultima)
                
         
      
        self.cantusLineExists = False
        self.tenorLineExists = False
        self.bassusLineExists = False
        self.altusLineExists = False
        
        if tenorAntePenultima!=None and tenorPenultima != None and tenorFinalis!=None:self.tenorLineExists = True
        if cantusAntePenultima!=None and cantusPenultima != None and cantusFinalis!=None:self.cantusLineExists = True
        if bassusAntePenultima!=None and bassusPenultima != None and bassusFinalis!=None:self.bassusLineExists = True
            
        # plagal cadence
        if "P" in self.labelList:
            noteList = []
            for part in work.parts:
                noteAtOffest = part.recurse().getElementAtOrBefore(bassusFinalis.offset, Note)
                if noteAtOffest != None:
                    noteList.append(noteAtOffest)
            chordAtOffset = Chord(noteList)
            if chordAtOffset.bass().nameWithOctave == bassusFinalis.nameWithOctave:  ### Marco !!!
                self.plagalCadence = True
        
        
        #phrygian cadence
        if self.tenorLineExists == True:
            tenorAF = interval.Interval(tenorPenultima, tenorFinalis)
            if tenorAF.directedSimpleName == "m-2":  
                self.phrygianCadence = True    
                
        # formal cadence
        if self.cantusLineExists:
            cantusAP = interval.Interval(cantusAntePenultima, cantusPenultima)
            cantusPF = interval.Interval(cantusPenultima, cantusFinalis)
            
            if cantusAP.directedSimpleName in ["m-2", "M-2"] and cantusPF.directedSimpleName in ["m2", "M2"]:    
                if self.tenorLineExists: 
                    TCAntepenultima = interval.Interval(tenorAntePenultima, cantusAntePenultima)
                    TCPenultima = interval.Interval(tenorPenultima, cantusPenultima)  
                    if TCAntepenultima.simpleName in ["m2", "M2", "m7", "M7"] and TCPenultima.simpleName in ["m6", "M6", "m3", "M3"]:
                        self.formalCadence = True
                                
                elif self.bassusLineExists:
                    BCAntepenultima = interval.Interval(bassusAntePenultima, cantusAntePenultima)
                    BCPenultima = interval.Interval(bassusPenultima, cantusPenultima) 
                    if BCAntepenultima.simpleName in ["p4", "M9", "m9"] and BCPenultima.simpleName in ["m3", "M3", "p8"]:
                        self.formalCadence = True
                        
                 
                            
            if self.formalCadence == False: 
                if self.tenorLineExists == True and self.cantusLineExists == True:
                    TCPenultima = interval.Interval(tenorPenultima, cantusPenultima) 
                    if TCPenultima.simpleName in ["m6", "M6", "m3", "M3"]:
                        self.simpleCadence = True # careful, careful
                        
                elif self.bassusLineExists == True and self.cantusLineExists == True:
                    BCPenultima = interval.Interval(bassusPenultima, cantusPenultima) 
                    if BCPenultima.simpleName in ["m3", "M3"]:
                        self.simpleCadence = True # careful, careful
                     
        if self.formalCadence==False and self.plagalCadence==False and self.phrygianCadence== False and self.simpleCadence==False:
            self.otherCadence=True
                    
        
            
    def getNoteBeforeInPart (self, work, noteInPart, offset=None):
        if  noteInPart != None:
            
            for part in  work.parts:
                identifiedNote = part.recurse().getElementById(noteInPart.id)
                if identifiedNote != None: 
                    if offset==None:
                        return part.recurse().getElementBeforeOffset(noteInPart.offset, classList=(Note)) 
                    else:
                        return part.recurse().getElementBeforeOffset(offset, classList=(Note))
        
        return None
                    
    def getNoteAtOffsetInPart (self, work, noteInPart, offset): 
        if  noteInPart != None:
            for part in  work.parts:
                identifiedNote = part.recurse().getElementById(noteInPart.id)
                if identifiedNote != None: 
                    return part.recurse().getElementAtOrBefore(offset, classList=(Note))        
                        
        # cantusPenultima
        # tenorPenultima
        
        # cantusAntepenultima
        # tenorAntepenultima 
        
        # tenor Antepenultima / tenorPenultima: unisono 
        # cantusAntepenultima  / cantusPenultima: -1
        
        # tenorAntepenultima / cantusAntepenultima = [2, 7]
        # tenorPenultima / cantusPenultima = [3, 6]
        
        # alternative bassus  
            
    

        
        

    
    def addAnnotation (self, annotation):
        
        
        if isinstance(annotation, list):
            for singleAnnotation in annotation:
                if singleAnnotation["content"][0]== "P": self.isPCadence = True
                
                if singleAnnotation["content"] in self.contentDictionary: 
                    for element in singleAnnotation["elements"]: 
                        self.contentDictionary[singleAnnotation["content"]].append(element) 
                        self.labelList.append(singleAnnotation["content"])
                if singleAnnotation["offset"] not in self.offsetList: self.offsetList.append(singleAnnotation["offset"])
                if singleAnnotation["measureNumber"] not in self.measureNumberList: self.measureNumberList.append(singleAnnotation["measureNumber"])
              
        
        else:
            if annotation["content"] in self.contentDictionary: 
                if annotation["content"][0]== "P": self.isPCadence = True
                for element in annotation["elements"]: 
                    self.contentDictionary[annotation["content"]].append(element)
                    self.labelList.append(annotation["content"])
                if annotation["offset"] not in self.offsetList: self.offsetList.append(annotation["offset"])
                if annotation["measureNumber"] not in self.measureNumberList: self.measureNumberList.append(annotation["measureNumber"])
                
                
              
        self.measureNumberList = sorted(self.measureNumberList)
        self.offsetList = sorted(self.offsetList)
        
        



class Cadences (object):
    def __init__(self, work, analysisMode= "", partDictionary = None, partName = None):
        self.work = work
        self.scoreTree = tree.fromStream.asTimespans(self.work, flatten=True, classList=(note.Note, chord.Chord))
        self.finalVerticalities = []
        self.semiFlatWork = self.work.semiFlat
        self.flatWork= self.work.flat
        self.partDictionary = partDictionary
        self.cadenceParts = []
        self.cadenceList = []
       
         
        
        #self.chordMeasureList = []
        #self.intermediaryChordList = []
        #self.cantusFinalis = None
        #self.bassusFinalis = None
        
        self.cadencePointDictionary = {}
        
        #self.cadenceDegrees = []
        
        
 
        for part in work.parts: 
            if not partName == None:
                if part.partName == partName: self.cadenceParts.append(part.flat)
            else : self.cadenceParts.append(part.flat)

        
        if analysisMode == "annotationsFermata":
            self.identifyCadencesFromFermataAnnotations()
        elif analysisMode == "voiceAnnotations":
            self.identifyCadencesFromVoiceAnnotations()
        elif analysisMode =="josquinAnnotations":
            self.identifyCadencesFromJosquinAnnotations()
        elif analysisMode =="barLines":
                self.identifyCadencesFromBarLines() 
            
        
        
        self.finalChord = self.getFinalChord()
        
        #self.identifyCadences (barlines = False) 
        #self.identifyDegrees ()
        
    
    
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
            
    def getCadenceAtOffset (self, offset, tolerance= 8.0):
        '''returns cadence at given offset '''
        
        #for unused_key, element,  in self.cadencePointDictionary.items():
        #    if element["cadenceOffset"] == offset:
        #        return element
        #    
        #return None 
        
        for cadence in self.cadenceList:
            for cadenceOffset in cadence.offsetList:
                if cadenceOffset >=offset-tolerance and cadenceOffset<= offset+tolerance:
                    return cadence
                
        return None
                
        
           
            
    def getFinalChord(self):
        for unused_elementKey, element in self.cadencePointDictionary.items():
            if element["cadenceType"] == "final":
                return element["cadenceChord"]
        return None
    
    def getFinalRoot(self):
        for unused_elementKey, element in self.cadencePointDictionary.items():
            if element["cadenceType"] == "final":
                return element["cadenceRoot"]
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
                
            
    
    def getCadenceAnnotationsFromTextExpression(self): ### merge with function below
        ''' this uses the annotations stored in TextExpression ''' 
        ''' get  expression information and store it in dictionary '''
        
        self.annotationList = []
        for part in self.cadenceParts:
            for annotation in part.getElementsByClass('TextExpression'):   
                noteList = []
                for note in part.getElementsByOffset(annotation.offset, classList=[Note]):
                    noteList.append(note)
                self.annotationList.append({"content": annotation.content, "measureNumber": annotation.measureNumber, "offset": annotation.offset, "elements": noteList, "partName": part.partName})
        return self.annotationList
    
    def identifyCadencesFromJosquinAnnotations (self):
        ''' this uses the annotations stored in TextExpression ''' 
        
        ''' identify cadence regions ''' 
        
        ''' get all expression information and store it in dictionary '''
        
        self.annotationList = []
        for part in self.cadenceParts:
            for annotation in part.getElementsByClass('TextExpression'):
                if annotation.content in ["A", "B", "C", "L", "P", "T", "b", "c", "t", "u", "x", "y", "z", "d", "e", "f", "g", "bf", "et"]:
                    
                    noteList = []
                    for note in part.getElementsByOffset(annotation.offset, classList=[Note]):
                        noteList.append(note)
                    

                    self.annotationList.append({"content": annotation.content, "measureNumber": annotation.measureNumber, "offset": annotation.offset, "elements": noteList})
        
        for annotation in self.annotationList:
                 
                
         
            if self.getCadenceAtOffset(annotation["offset"])  == None: 
                self.cadenceList.append(Cadence(([annotation])))
            else:
                cadenceAtOffset = self.getCadenceAtOffset(annotation["offset"])
                cadenceAtOffset.addAnnotation(annotation) 
          
        self.cadenceList = sorted(self.cadenceList, key=lambda x: x.offsetList[0]) 
        
        for cadence in self.cadenceList:
            cadence.checkJosquinClasses(self.work)
        
         
      
      
      
    
    
    def identifyCadencesFromVoiceAnnotations (self):
        ''' this uses the annotations stored in expression '''
        ''' possible values: X_Y [X: "C", "A", "T", "B", Y: "A", "P", "F"] '''
        
        ''' identify cadence regions ''' 
        
        ''' get all expression information and store it in dictionary '''
        
        self.annotationList = []
        for part in self.cadenceParts:
            for annotation in part.getElementsByClass('TextExpression'):
                if annotation.content in ["C_A", "C_P", "C_F", "A_A", "A_P", "A_F", "T_A", "T_P", "T_F", "B_A", "B_P", "B_F",
                                          "PC_A", "PC_P", "PC_F", "PA_A", "PA_P", "PA_F", "PT_A", "PT_P", "PT_F", "PB_A", "PB_P", "PB_F"
                                          
                                          ]:
                    
                    noteList = []
                    for note in part.getElementsByOffset(annotation.offset, classList=[Note]):
                        noteList.append(note)
                    

                    self.annotationList.append({"content": annotation.content, "measureNumber": annotation.measureNumber, "offset": annotation.offset, "elements": noteList})
                
        
        ''' group annotations in cadences by starting backwards'''        
        for cadenceElement in ["_F", "_P", "_A"]:
        
            for annotation in self.annotationList:
                if not cadenceElement in annotation["content"]: continue
                
         
                if self.getCadenceAtOffset(annotation["offset"])  == None: 
                    self.cadenceList.append(Cadence(([annotation])))
                else:
                    cadenceAtOffset = self.getCadenceAtOffset(annotation["offset"])
                    cadenceAtOffset.addAnnotation(annotation) 
          
        self.cadenceList = sorted(self.cadenceList, key=lambda x: x.offsetList[0]) 
        
        for cadence in self.cadenceList:
            cadence.identvalProgressions() 
            cadence.diminutions()
        
                 
             
   
    def identifyCadencesFromFermataAnnotations (self):
        for cadencePart in self.cadenceParts:
        
            for elementNote in cadencePart.recurse().getElementsByClass(note.Note):
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
    
    def hasCadenceOn(self):
        cadencePointsList = []
        
        for unused_key, val  in self.cadencePointDictionary.items():
            cadencePitches = val["cadenceChord"].pitches
            for cadencePitch in cadencePitches:
                cadencePointsList.append(str.lower(cadencePitch.nameWithOctave))
                
        return cadencePointsList
                                       
                                
 
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
             
        
        
        
           
        