# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:         reduction.py
# Purpose:      reduction object
# 
#
# Copyright:    Christophe Guillotel-Nothmann Copyright © 2017
#-------------------------------------------------------------------------------
from music21 import stream, note, chord, tree, clef, key, instrument
import copy, logging 
from music21.duration import GraceDuration
# from tkinter.constants import CURRENT
 
 

class addStringIds():
    def __init__(self, work):
        
        for element in work.flat:
            if element.id == id (element):
                element.id = 'id_' + str (id(element))
                #logging.info ('changed id ' + element.id)
                if isinstance(element, note.Note):
                    element.pitch.id = 'id_' + str (id(element.pitch))
            else:
                if isinstance(element, note.Note):
                    element.pitch.id = element.id
        
                       

class streamPreparation():        
    def __init__(self, work):
        self.work = work
        
    def getCorrectedStream (self):
        return self.work 
    
    def fillEmptyMeasures (self):
        ''' 1. create measure offset list [n, startOffset, endOffset]'''
        measureList = []
        ''' get list of all measures '''
        recurseIter = self.work.recurse()
        
        for el in recurseIter:
            if isinstance(el, stream.Measure):
      
        
                measureList.append(el)
        
        ''' put measures in dictionary '''
        measureDictionary = {}
        
        for measure in measureList:
            ''' get onset,  offset, measurenumber '''
            onset = measure.offset
            duration = measure.duration.quarterLength    
            offset = duration + onset
            number = measure.measureNumber
                        
            ''' check if measure number is in dictionary and get offsetList '''
            
            ''' if empty, add entry '''
            if not number in measureDictionary:
                measureDictionary [number] = [onset, offset, duration]
                
                ''' else: check if measureduration is the highest, if not, replace ''' 
            else:
                onsetOffsetDuration = measureDictionary[number]
                if onsetOffsetDuration [2] < duration:
                    measureDictionary [number] = [onset, offset, duration]
                    
        ''' 2. corret mesaures according to offsetList '''
        
        ''' loop over every measure element and fill up if necessary '''
                    
        for measure in measureList:
            number = measure.measureNumber
            ''' get dictionary entry '''
            onsetOffsetDuration =  measureDictionary[number]
            
            neededDuration = onsetOffsetDuration[2]
            actualDuration = measure.duration.quarterLength
            
            addDuration = neededDuration-actualDuration
            
            ''' if addDuration > 0 add it as silence '''
            
            if addDuration > 0 or onsetOffsetDuration[0] != measure.offset :
                
                rest = note.Rest()
                rest.duration.quarterLength = addDuration    
                measure.append(rest)
                measure.offset = onsetOffsetDuration[0]
            
         
        recurseIter = self.work.recurse()
        
        for el in recurseIter:
            if isinstance(el, stream.Stream):
                el.sort()   
        
               
                
class StreamAdditional():
    
    ''' convenience method to assign active sites '''
    def assignActiveSiteToStream(self, referenceStream, targetElement = None):
        for unused_element in referenceStream.recurse(): 
            pass
            

class Reduction():  
    
    def __init__(self, work): 
        
        ''' create layer dictionary and append work'''  
        self.layerDictionary = []
        self.layerDescriptionList = []
        
        ''' add ids if no ideas '''
        addStringIds(work)  
        self.layerDictionary.append(work)
        self.layerDescriptionList.append("")
    
    def addLayer (self, layer = None):
        if layer == None :
            self.layerDictionary.append(copy.deepcopy(self.layerDictionary[-1]))
        else :
            self.layerDictionary.append(layer)
    
    
    
    #def removeCountrapuntalDissonances (self, types):   
    #    ''' add layer ''' 
    #    self.addLayer()
    #     
    #    dAnalysis =  DissonanceAnalysis(self.layerDictionary[-1])
    #    ''' loop over parts and remove contrapuntal passing tones and neighbor tones ''' 
    #    collectionList = dAnalysis.getDissonanceCollectionDictionary(types)
    #     
    #    
    #    currentLayer = self.layerDictionary[-1]
    #    for dissonanceKey in collectionList: 
    #        dissonanceCollection = collectionList[dissonanceKey] 
    #        dissonance = dissonanceCollection[0] 
    #        dissonantNote = dissonance.note2  
    #         
    #        ''' loop over notes and rests in main list ''' 
    #             
    #        ''' remove current note and expand precedent one '''   
    #    
    #        
    #        if dissonance.type in ['NT', 'PT', 'ET', 'ANT']:
    #            
    #            if dissonance.subType in ['n_a_n_sb']: 
    #                noteAfter = currentLayer.getElementById(dissonance.part2ID).recurse().getElementAfterElement(dissonantNote, ['Note', 'Rest']) 
    #                noteAfter.duration.quarterLength = noteAfter.duration.quarterLength + dissonance.quarterLength
    #                
    #                ''' change active site to current layer and change offset'''  
    #                StreamAdditional.assignActiveSiteToStream(self, currentLayer, noteAfter)
    #                noteAfter.offset = noteAfter.offset - dissonance.quarterLength
    #                 
    #                
    #            else:
    #                noteBefore = currentLayer.getElementById(dissonance.part2ID).recurse().getElementBeforeOffset(dissonantNote.offset, ['Note', 'Rest']) 
    #                noteBefore.duration.quarterLength  = noteBefore.duration.quarterLength  + dissonantNote.duration.quarterLength 
    #            currentLayer.remove(dissonantNote, recurse=True)
    #        
    #        
    #        if dissonance.type in ['SUS']:
    #            ''' dissonant note is independent '''
    #            noteBefore = currentLayer.getElementById(dissonance.part2ID).flat.getElementBeforeOffset(dissonantNote.offset, ['Note', 'Rest'])
    #            noteAfter = currentLayer.getElementById(dissonance.part2ID).flat.getElementAfterElement(dissonantNote, ['Note', 'Rest']) 
    #            noteAfter.duration.quarterLength = noteAfter.duration.quarterLength + dissonance.quarterLength
    #            
    #            ''' change active site to current layer and change offset'''  
    #            StreamAdditional.assignActiveSiteToStream(self, currentLayer, noteAfter)
    #            noteAfter.offset = noteAfter.offset - dissonance.quarterLength
    #            
    #            
    #            if dissonantNote.duration.quarterLength == dissonance.quarterLength: ## dissonance is independent and can be integrally removed 
    #                currentLayer.remove(dissonantNote, recurse=True)
    #                noteBefore.tie = None
    #            else: ##  dissonant note and consonant note before are the same - just one part can be removed 
    #                dissonantNote.duration.quarterLength = dissonantNote.duration.quarterLength - dissonance.quarterLength
    #            
    #         
    #            
    #           
    #        
    #        logging.info ("Removing dissonance: " + dissonance.getFullCounterpointDescription()  + ' at offset: ' 'Offset: ' + str (dissonance.note2.offset))
            
    
    #def removeNonChordTones (self, layerIndex = None):
    #    scoreTree = tree.fromStream.asTimespans(self.getLayer(), flatten=True, classList=(note.Note, chord.Chord)) 
    #    analysis.reduceChords.ChordReducer().removeNonChordTones(scoreTree)
    #    self.addLayer(tree.toStream.partwise(scoreTree, templateStream=self.getLayer()))
    #    
    #    
    #def removeNonHarmonicNotes (self, layerIndex = None):
    #    layerIndex = self._checkLayerIndex(layerIndex)
        
    #    ''' analyze stream '''
    #    chordAnal = chordAnalysis.ChordAnalysis(self.layerDictionary[layerIndex])
    #     
    #    ''' remove nhn '''
    #    nhnStream = chordAnal.removeNonHarmonicNotes()
    #    
    #    ''' get stream and add it to layer '''
    #    self.layerDictionary.append(nhnStream)
    #    
        
        
    def removeGraceNotes (self, layerIndex = None):
        ''' create new layer and loop over this layer ''' 
        
        layerIndex = self._checkLayerIndex(layerIndex)
        
        self.layerDictionary.append(copy.deepcopy(self.layerDictionary[layerIndex]))
        currentLayer = self.layerDictionary[-1]
    
        
        ''' loop over part and remove repetitions '''
        for part in currentLayer.getElementsByClass(stream.Part):
            flatPartNotes = part.flat.notesAndRests
            #logging.info ('Removing grace notes from part ' + str(flatPartNotes))
            
            ''' loop over notes and rests in main list '''
            for element in flatPartNotes:
                if isinstance(element.duration , GraceDuration):
                    currentLayer.remove(element, recurse=True)
                    

    
    
    def removeRepetitions (self, layerIndex = None):
        ''' create new layer and loop over this layer ''' 
        
        layerIndex = self._checkLayerIndex(layerIndex)
        
        self.layerDictionary.append(copy.deepcopy(self.layerDictionary[layerIndex]))
        currentLayer = self.layerDictionary[-1]
        
        
        ''' loop over part and remove repetitions '''
        for part in currentLayer.recurse().getElementsByClass(stream.Part):
            flatPartNotes = part.flat.notesAndRests
            #logging.info ('Removing repetitions from part ' + str(flatPartNotes))
            
            ''' loop over notes and rests in main list '''
            noteOrRestMainList = 0
            
            while noteOrRestMainList < len (flatPartNotes): 
                
                if flatPartNotes[noteOrRestMainList].isRest:
                    noteOrRestMainList +=1
                    continue
                else: 
                    note = flatPartNotes[noteOrRestMainList]
                    noteOrRestSecondaryList = noteOrRestMainList + 1
                'continue if note has tie'
                if note.tie is not None:
                    if note.tie.type == 'start':
                        noteOrRestMainList +=1
                        continue
                
                ''' loop over notes and rests in main list '''
                while noteOrRestSecondaryList <  len (flatPartNotes):
                    if flatPartNotes[noteOrRestSecondaryList].isRest:
                        break
                    else:
                        nextNote = flatPartNotes[noteOrRestSecondaryList]
               
                    if note.pitch == nextNote.pitch:
                        ''' get following duration and add it to the current duration '''
                        followingDuration = nextNote.duration.quarterLength
                        note.duration.quarterLength = note.duration.quarterLength + followingDuration 
                        logging.info ('Removed note at offset ' + str (nextNote.offset))  
                        currentLayer.remove(nextNote, recurse=True)
                        noteOrRestSecondaryList +=1
                    else: break
                    
                noteOrRestMainList = noteOrRestSecondaryList     
                        
    
        
    def verticalize (self):
        scoreTree = tree.fromStream.asTimespans(self.getLayer(), flatten=True, classList=(note.Note, chord.Chord))
        for verticalities in scoreTree.iterateVerticalitiesNwise(n=2):
            one, two = verticalities      
            
            pCollection1 = sorted(one.pitchSet)
            pCollection2 = sorted(two.pitchSet)
            
            ''' create pitch class collections and check if pitch classes are identical '''
            pcCollection1 = []
            pcCollection2 = []
            
            for pc  in pCollection1:
                if not pc.name in pcCollection1:
                    pcCollection1.append(pc.name)
            
            for pc  in pCollection2:
                if not pc.name in pcCollection2:
                    pcCollection2.append(pc.name)
                
            if sorted(pcCollection1) == sorted(pcCollection2):
                logging.info ("arpeggio") 
                ''' merge verticalities if their pitch classes are identical, i.e. create chords in voices ''' 
                horizontalities = scoreTree.unwrapVerticalities(verticalities)
                for unused_part, timespanList in horizontalities.items():
                    if len(timespanList) < 2:
                        continue
                    '''elif timespanList[0].pitches == timespanList[1].pitches:
                        continue'''
                    timespanListShort = []
                    [timespanListShort.append(item) for item in timespanList if item not in timespanListShort]
                     
                    logging.info (timespanList[0].part)
                    
                    ''' build chord from verticality one's offset onwards '''
                    sumChord = chord.Chord(timespanListShort[0].pitches + timespanListShort[1].pitches)
                    scoreTree.removeTimespanList(timespanList)
                    
                    if timespanListShort[0].offset == one.offset:
                        merged = timespanList[0].new(element=sumChord,endTime=timespanList[1].endTime)
                        scoreTree.insert(merged) 
                        
                    elif timespanListShort[0].offset < one.offset:
                        merged = timespanList[0].new(element=sumChord,offset= one.offset, endTime=timespanList[1].endTime) ### new chord (shorter than initial verticality one)
                        ''' shortened stimeStamp '''
                        shortTS = timespanList[0].new(endTime=one.offset)
                        scoreTree.insert(merged) 
                        scoreTree.insert(shortTS) 
                        
                        
                    logging.info ('Merged ' + str(one) + ' with ' + str(two))
            
        ''' convert back to stream and store it '''
        self.addLayer(tree.toStream.partwise(scoreTree, templateStream=self.getLayer()))
 
         
                
    
    
    def getLayer (self, layerIndex=-1): 
        return self.layerDictionary[self._checkLayerIndex(layerIndex)]      
    
    
    def mergeWithPreceding(self, element):
        ''' get element before element '''
        elementBefore = self.workReduction.recurse().getElementBeforeOffset(element.offset)
        
        ''' add duration to preceding element''' 
        elementBefore.duration.quaterLength = element.duration.quaterLength
        
        ''' remove element ''' 
        self.workReduction.remove(element, recuse=True)
        
    
                     
    def _checkLayerIndex (self, layerIndex):
        if layerIndex in range (-1, len (self.layerDictionary)-1):
            return layerIndex
        else: return -1             
            
        