import numpy as np
import tensorflow as tf
import logging
import reduction
from tensorflow import keras
from music21.note import Note
from music21 import note, chord, stream, clef, key, pitch, interval
from music21.pitch import Pitch
from copy import deepcopy
from music21.interval import Interval


class RootAnalysis ():

    def __init__(self, pitchCollectionSequences, analyzeWithModel = True):
        self.pitchCollectionSequences = pitchCollectionSequences
        self.pitchCollectionSequence =  pitchCollectionSequences.pitchCollSequence
        self.scoreTree = self.pitchCollectionSequence.scoreTree
        self.overallScore = None
        self.lowestScore = None
        self.highestScore = None
        self.rootDictionary = {}
        
        
        if analyzeWithModel == True: self.analyzeWithModel()
      
        
  
    
        
    
    def populateRootDictionary (self):
        
        for pitchColl in self.pitchCollectionSequence.explainedPitchCollectionList:
            
            if pitchColl.rootPitch == None: continue
        
            ''' get corresponding root key'''
            rootEntry = self.getRootDictionaryEntry(pitchColl.rootPitch.name)
            
            ''' compute interval between root and real bass '''
            note1 = note.Note(pitchColl.rootPitch)
            note2 = note.Note (pitchColl.bass)
            
            note1.octave = 1
            note2.octave = 2
            
            note12Interval = Interval(note1, note2)
            
            ''' check if interval name exists in rootEntry if not add it '''
            rootEntry = self.getRootDictionaryEntry(pitchColl.rootPitch.name)
            
            rootEntry["occurrence"] = rootEntry["occurrence"]  + 1
            rootEntry["duration"] = rootEntry["duration"] + pitchColl.duration
            
            if note12Interval.simpleName in rootEntry:
                rootEntry[note12Interval.simpleName] = rootEntry[note12Interval.simpleName] + pitchColl.duration
            else:
                rootEntry[note12Interval.simpleName] = pitchColl.duration
    
 
    
    def getRootCorrespondingToScaleDegree (self, scaleDegree):
        
        for unused_elementKey, element in self.rootDictionary.items():
            if element["degree"] == scaleDegree: return element
            
        
        return None
    
    def setRootDegreeFromReferencePitch (self, scale, referencePitch):
        
        stepDictionary = {}
        
        ''' adds root degree e.g. romann numerals, given scale  and a reference pitch, '''
        
        if isinstance(referencePitch, str):
            rootPitch = pitch.Pitch(referencePitch)
        
        referenceStep = rootPitch
        
        diatonicSteps = [scalePitch.name for scalePitch in scale.pitches]
        referenceIndex = None
        
        for counter, diatonicStep in enumerate(diatonicSteps):
            if diatonicStep == referenceStep.name: referenceIndex = counter
                
        stepDictionary[diatonicSteps [referenceIndex]] = "I" 
        stepDictionary[ diatonicSteps [(referenceIndex + 1) % 7]] = "II"
        stepDictionary [diatonicSteps [(referenceIndex + 2) % 7]] = "III"
        stepDictionary [diatonicSteps [(referenceIndex + 3) % 7]] = "IV"
        stepDictionary [diatonicSteps [(referenceIndex + 4) % 7]] = "V"
        stepDictionary [diatonicSteps [(referenceIndex + 5) % 7]] = "VI"
        stepDictionary [diatonicSteps [(referenceIndex + 6) % 7]] = "VII"
        
        ''' add chromatic steps ''' 
        chomaticDictionary = {}
        
        for diatonicStepKey, diatonicStep in  stepDictionary.items():
            dimU = interval.Interval("d1")
            augU = interval.Interval("a1")
            
            dimU.noteStart = note.Note(diatonicStepKey)
            augU.noteStart = note.Note(diatonicStepKey)
        
            flatDegree = dimU.noteEnd 
            sharpDegree = augU.noteEnd
            
            chomaticDictionary[flatDegree.name] = diatonicStep + "-"
            chomaticDictionary[sharpDegree.name] = diatonicStep + "#"
            
            
            
        ''' add items to step dict ''' 
        for degreeKey, degree in  chomaticDictionary.items():
            stepDictionary[degreeKey]= degree 
        
         
        ''' set roman numerals accordingly in dic '''
        for rootKey, rootEntry in self.rootDictionary.items():
            
            rootPitch = pitch.Pitch(rootKey) 
            if rootPitch.name in stepDictionary: 
                rootEntry ["degree"] = stepDictionary[rootPitch.name]
                
            else:
                rootEntry ["degree"] =   "other"
        
        ''' add roman numerals to pitch collections '''
        for pitchCollection in self.pitchCollectionSequence.explainedPitchCollectionList:
            if pitchCollection.rootPitch == None:
                continue
            
            if pitchCollection.rootPitch.name in stepDictionary: 
                pitchCollection.rootDegree = stepDictionary[pitchCollection.rootPitch.name]
                
            else:
                pitchCollection.rootDegree = None
    
    
    def getRootDictionaryEntry (self, rootName):
         
        
        if rootName in self.rootDictionary:
            return self.rootDictionary[rootName]
        else:  
            dicEntry = {
                "occurrence": 0,
                "duration": 0,
                "root": rootName
                }  
            self.rootDictionary[rootName]= dicEntry
            return dicEntry
    
    
    def addRootInformation (self, rootStream):
        ''' this is used to add root information from individual stream to pitchCollectionSequence ''' 
        flatRootStream = rootStream.flat
        
        
        for pitchCollection in self.pitchCollectionSequence.explainedPitchCollectionList:
            pitchCollOffset = pitchCollection.verticality.offset
            
            noteAtOffset = flatRootStream.getElementAtOrBefore(pitchCollOffset, Note)
            
            if isinstance(noteAtOffset, note.Note):
            
                pitchCollection.rootPitch = noteAtOffset.pitch
            else:
                print ("Cannot add root information")
             
    def analyzeWithModel(self, modelPath = '/Users/christophe/Documents/GitHub/PolyMIR/models/rootModel16072020.h5'):
         
        #self.featuresPath = 'dissonanceNeuralNetwork/observations.npy' 
        #self.labelsPath = 'dissonanceNeuralNetwork/labels.npy'
         
        
        ### requires tensforflow 1.6
        ### keras==2.1.3 

        labelDict = {0:"C-", 1:"C", 2:"C#", 3:"D-", 4:"D", 5:"D#", 6:"E-", 7:"E", 8:"E#", 9:"F-", 10:"F", 11:"F#", 12:"G-", 13:"G", 14:"G#", 15:"A-", 16:"A", 17:"A#", 18:"B-", 19:"B", 20:"B#"}
            
        
        ''' run model '''
        #self.features = np.load(self.featuresPath)
        #self.labels = np.load(self.labelsPath)
        
        
        self.model = keras.models.load_model(modelPath)
        self.model.compile(optimizer="adam",  loss='sparse_categorical_crossentropy',metrics=['accuracy'])
        #rootModel.compile(optimizer=tf.train.AdamOptimizer(), loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        self.model.summary()
        
        
        scoreList = [] 
            
        
        
        for pitchCollection in self.pitchCollectionSequence.explainedPitchCollectionList:
            ''' loop over all analyzed pitches ''' 
            
            
            ''' check if collection is not empty '''
                
            ''' get observation list and put it in array '''                
            
            observationArray = np.array(self.pitchCollectionSequence.getObservationsForVerticality(pitchCollection.verticality, 5))
            feature = np.array([observationArray])
                        
            ''' make prediction from observation list '''
            predictions = self.model.predict(feature)
            
            ''' get highest score identifiy index '''
            highestScore = max(predictions[0]) 
            for index in range (0, len(predictions[0])):
                if predictions[0][index] == highestScore:
                    break
            
            #print ("offset: " + str(pitchCollection.verticality.offset) + " prediction: " + labelDict[index] + " score: " + str(highestScore))
            
            pitchCollection.rootPitch = Pitch(labelDict[index])
            pitchCollection.probability = highestScore
            
            scoreList.append(pitchCollection.probability)
            
            
        scoreTotal = 0
        for score in scoreList:
            scoreTotal = scoreTotal + score
            
        scoreList.sort()
        self.overallScore = scoreTotal / len (scoreList)
        self.lowestScore = scoreList[0]
        self.highestScore = scoreList [-1]
        
        
        
            
    
    @staticmethod
    def compareConcurrentRootAnalyses (analysisList):
        ''' this takes as input a list of concurrentAnalyses and gives as output a stream where equivalent roots are merged and different roots are identified '''
        
        ''' check that all streams have same length '''
        rootStream = analysisList[0][0]
        streamLength = rootStream.duration.quarterLength
        for analysis in analysisList:
            if analysis[0].duration.quarterLength != streamLength: return None
            
        ''' create reference root stream '''
        
        referenceStream = deepcopy(rootStream)
        
        
        
        ''' loop over reference stream check every note '''     
        flatRefStream = referenceStream.flat
           
        for referenceNote in flatRefStream.getElementsByClass([note.Note, note.Rest]):
            lyricString = ""
            heterogeneous=False
            #
            '''loop over other streams '''
            for analysis in analysisList:
                flatAnalysis = analysis[0].flat
                analysisNote = flatAnalysis.getElementAtOrBefore(referenceNote.offset, [note.Note, note.Rest]) 
                lyricString = lyricString + "\r" + analysis[1] + ":" + analysisNote.name
                
                if referenceNote.name != analysisNote.name: heterogeneous = True
                    
            if heterogeneous == True: 
                referenceNote.style.color = 'red'
                referenceNote.lyric = lyricString[1:]
                         
            
        return referenceStream
            
            
        
        
        
        
        
    
    
    def confrontModelWithLabels (self, modelPath, rootStream):
        ''' this is used to confont the labels with the model predictions '''
        
        self.modelPath = modelPath
        
        ''' run model '''
        #self.features = np.load(self.featuresPath)
        #self.labels = np.load(self.labelsPath)
        self.new_model = keras.models.load_model(modelPath)
        self.new_model.compile(optimizer=tf.train.AdamOptimizer(), loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        self.new_model.summary()
        
    
            
        
        
        for pitchCollection in self.pitchCollectionSequence.explainedPitchCollectionList:
            ''' loop over all analyzed pitches ''' 
                
            ''' get observation list and put it in array '''                
            
            observationArray = np.array(self.pitchCollectionSequence.getObservationsForVerticality(pitchCollection.verticality, 5))
            feature = np.array([observationArray])
                        
            ''' make prediction from observation list '''
            predictions = self.new_model.predict(feature)
            
            ''' get highest score identifiy index '''
            highestScore = max(predictions[0]) 
            for index in range (0, len(predictions[0])):
                if predictions[0][index] == highestScore:
                    break
            
            labelDict = {0:"C-", 1:"C", 2:"C#", 3:"D-", 4:"D", 5:"D#", 6:"E-", 7:"E", 8:"E#", 9:"F-", 10:"F", 11:"F#", 12:"G-", 13:"G", 14:"G#", 15:"A-", 16:"A", 17:"A#", 18:"B-", 19:"B", 20:"B#"}
            print ("offset: " + str(pitchCollection.verticality.offset) + " prediction: " + labelDict[index] + " score: " + str(highestScore))
            
            modelRootPitch = Pitch(labelDict[index])
            labelRootPitch = rootStream.flat.getElementAtOrBefore(pitchCollection.verticality.offset, [note.Note]).pitch
            
            pitchCollection.rootPitch = labelRootPitch
            
            if labelRootPitch.name != modelRootPitch.name: 
                labelRootPitch.color = "red"
                labelRootPitch.modelRoot = modelRootPitch.name
            
            
            pitchCollection.probability = highestScore
    
    
    
    def getFundamentalBass (self):
        ''' create stream  with part for FB'''     
        
        chordifiedStream =   self.scoreTree.source.chordify()
        recurseIter = chordifiedStream.recurse()
        

        for el in recurseIter:
            if isinstance(el, (chord.Chord, note.Note, note.Rest)):
                chordifiedStream.remove(el, recurse=True)
        
    
        
        measureList = list (chordifiedStream.recurse().getElementsByClass(stream.Measure))
        
       
        ''' loop over vertices and add notes '''
   
        

        for pitchColl in self.pitchCollectionSequence.explainedPitchCollectionList:
            if pitchColl.rootPitch != None:
                rootPitch = pitchColl.rootPitch
                rootPitch.octave = 3
                
                ''' create note according to duration of verticality '''
                
                
                 
                
                if rootPitch.name == None:
                    rootNote = note.Rest()
                else: rootNote = note.Note (rootPitch)
                rootNote.duration.quarterLength = pitchColl.duration
                
                
                if hasattr(rootPitch, "color"):
                    rootNote.style.color = rootPitch.color
                    rootNote.lyric = rootPitch.modelRoot
                    
              
            
            ''' check if measures: if so, get correct measure and insert '''
            
            measureCounter = 0
            for measureCounter in range (0, len (measureList)):
                
                if pitchColl.verticality.offset >= measureList[measureCounter].offset:
                    if len (measureList) - 1 == measureCounter: # last measure
                        measureList[measureCounter].insert(pitchColl.verticality.offset-measureList[measureCounter].offset, rootNote) 
                        break
                    else:
                        if pitchColl.verticality.offset <  measureList[measureCounter+ 1].offset : 
                            
                            ''' check if element exists in stream '''
                            elementExists = False
                            for eInStream in chordifiedStream.flat:
                                if eInStream is rootNote:
                                    elementExists = True
                                    logging.info("Cannot include following note: %s" %(rootNote))
                                    break
                            
                            if elementExists == False: 
                                #rootNote.editorial = self.name
                                measureList[measureCounter].insert(pitchColl.verticality.offset-measureList[measureCounter].offset, rootNote) 
                            break   
 
         
        chordifiedStream.id = "Root"
        chordifiedStream.partName = 'Root'
        chordifiedStream.name = "Root"
        chordifiedStream.partAbbreviation = 'R.'
        

        
        ''' change key(s) ''' 
        for clefElement in chordifiedStream.recurse().getElementsByClass(clef.Clef):
            chordifiedStream.recurse().replace(clefElement, clef.BassClef())
        
        for keyElement in chordifiedStream.recurse().getElementsByClass(key.Key):
            logging.info (keyElement.alteredPitches)
   

     
   
        ''' remove repetitions in stream '''
        
        #scoreStream = stream.Score ()
        #scoreStream.insert(0, chordifiedStream)
            
        #reductionStream = reduction.Reduction (scoreStream)
        #reductionStream.removeRepetitions()
        
     
        
        #partStream = reductionStream.getLayer().recurse().getElementsByClass(stream.Part)
        
        return chordifiedStream
    
        
    
    
    def modelScores(self):
        
        modelScores = "Overall score: " + str(self.overallScore) + " Highest score: " + str(self.highestScore) + " Lowest score: " + str(self.lowestScore)
        
        print (modelScores)
        return [self.overallScore, self.highestScore, self.lowestScore]

        
    
    def setObservationData(self, observationsDirectory):
        
         
        pitchCollectionSequence = self.pitchCollectionSequences.pitchCollSequence
        
        pitchCollectionSequence.setVerticalityObservations(observationsDirectory)