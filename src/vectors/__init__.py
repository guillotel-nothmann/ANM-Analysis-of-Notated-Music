# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:         vectrors.py
# Purpose:      implement theory of harmonic vectors
# 
#
# Copyright:    Christophe Guillotel-Nothmann Copyright © 2017
#-------------------------------------------------------------------------------
 
from sre_parse import Pattern
import xml
from pitchCollections import PitchCollection
from idlelib.idle_test.test_configdialog import root
#from Cython.Shadow import struct
''' imports ''' 
from music21 import  stream, graph, note, chord, clef, interval, key
from music21.interval import Direction
from collections import OrderedDict
from _operator import and_
#from graphs import progressionScatterPlot
#import graphs
import copy, logging 

 

class VectorAnalysis(object):    
    
    def __init__(self, pitchCollSequence):
        
         
        self.chordSequenceList = []
        self.pitchCollSubList = [] ### the pitch coll sequences is slided according to end sections 
        self.pitchCollSequence = pitchCollSequence
        
        
        
        ''' slide pitch coll sequence in sections and compute chord sequences '''
        self.setPitchCollSubsequences()      
        
        for pitchCollSubList in self.pitchCollSubList:
            chordSequ = ChordSequence(pitchCollSubList)
            self.chordSequenceList.append(chordSequ)
        
        
        ''' compute vectors and set categories '''
        self.vectorList = self._computeVectors() 
     
        self.vectorPopulation = self._setVectorCategories('vectorInterval')
        self.longestPatterns = [] 
        

        
        
    
    
    
    def setPitchCollSubsequences (self):
        ''' build chord sequence '''
       
        self.pitchCollSubList.append([])
        
        for counter,  pitchColl in enumerate(self.pitchCollSequence.explainedPitchCollectionList): 
            
            ''' cut if general rest '''
            if pitchColl.rootPitch == None:  
                self.pitchCollSubList.append([]) 
                continue 
            
            self.pitchCollSubList[-1].append(pitchColl)
            
            ''' cut if sequence end '''
            if pitchColl.isSectionEnd == True and len (self.pitchCollSequence.explainedPitchCollectionList) != counter +1:
                self.pitchCollSubList.append([])  
    
    
    def getVectorDictionary (self, vectorCategory):
         
            
        categoryDictionary = {
            "name": vectorCategory.name,
            "occurrence": vectorCategory.occurrence,
            "subcategories": []
            }
        
        for subcategory in vectorCategory.subCategories:
            categoryDictionary["subcategories"].append (self.getVectorDictionary(subcategory))
            
        return categoryDictionary
            
     
    def getFlatVectorDictionary (self, vectorCategory, vectorDictionary = {}):
        
        categoryDictionary = {
            "name": vectorCategory.name,
            "occurrence": vectorCategory.occurrence
            }
        
        vectorDictionary [vectorCategory.name] = categoryDictionary
        
        for subcategory in vectorCategory.subCategories:
            self.getFlatVectorDictionary(subcategory, vectorDictionary)
            
            
            
            
        return vectorDictionary
             
        
    
    
    def show(self, representationType = "text", percents = False, threshold = 0):
        population = self.vectorPopulation
        ratio = 1
        
        if representationType == "text":
            logging.info (population.name + ': ' + str (population.occurrence))
            
            if percents == True:
                ratio = self.vectorPopulation.occurrence
            
            for vectorCategory in population.subCategories:
                logging.info ('\t' + str (vectorCategory.name) + ': ' + str(vectorCategory.occurrence/ratio))
                for interval in vectorCategory.subCategories:
                    logging.info  ('\t\t' + str(interval.name) + ': ' + str(interval.occurrence/ratio))
                    for intervalType in interval.subCategories:
                        logging.info  ('\t\t\t' + str (intervalType.name) + ': ' + str(intervalType.occurrence/ratio))
                        
        elif representationType == 'dict': # returns dictionary analysisObject 
            vectorDictionary = self.getFlatVectorDictionary(self.vectorPopulation)
            return vectorDictionary
            
            
        
        
        elif representationType == 'xml':
            ratio = population.occurrence
            xmlString = '<population name="%s" occurrence="%s" percentage="%s">' %(population.name, population.occurrence, round (population.occurrence/ratio, 4))
            
            for category in population.subCategories:
                xmlString = xmlString + '<category name="%s" occurrence="%s" percentage="%s">' %(category.name, category.occurrence, round(category.occurrence/ratio, 4))
                otherSubcategory = 0
                for subCategory in category.subCategories:
                    if subCategory.occurrence/ratio >= threshold:
                    
                        xmlString = xmlString + '<subcategory name="%s" occurrence="%s" percentage="%s">' %(subCategory.name, subCategory.occurrence, round (subCategory.occurrence/ratio, 4))
                        xmlString = xmlString + '</subcategory>'
                    else: otherSubcategory = otherSubcategory + subCategory.occurrence
                
                if otherSubcategory > 0:  xmlString = xmlString + '<subcategory name="%s" occurrence="%s" percentage="%s"></subcategory>' %("other", otherSubcategory, round (otherSubcategory/ratio, 4))
                        
                
                xmlString = xmlString + '</category>'
                
                
                
            xmlString = xmlString + "</population>"
            return xmlString
            
            
            
        elif representationType == 'simpleList':
            ratio = population.occurrence
            plus4 = population.getSubCategory(4)
            minus3 = population.getSubCategory(-3)
            plus2 = population.getSubCategory(2) 
            minus4 = population.getSubCategory(-4)
            plus3 = population.getSubCategory(3)
            minus2 = population.getSubCategory(-2)
            
            rootString = ""
            
            if plus4 != None: 
                rootString = rootString  + str (plus4.occurrence) 
            else: rootString = rootString + "\t"
                
            if minus3 != None: 
                rootString = rootString + "\t" + str (minus3.occurrence) 
            else: rootString = rootString + "\t"
                
            if plus2 != None: 
                rootString = rootString + "\t" + str (plus2.occurrence) 
            else: rootString = rootString + "\t"
            
            if minus4 != None: 
                rootString = rootString + "\t" + str (minus4.occurrence) 
            else: rootString = rootString + "\t"
            
            if plus3 != None: 
                rootString = rootString + "\t" + str (plus3.occurrence) 
            else: rootString = rootString + "\t"
            
            if minus2 != None: 
                rootString = rootString + "\t" + str (minus2.occurrence) 
            else: rootString = rootString + "\t" 
            return (rootString) 
        
        elif representationType == '2DTable':
            ratio = population.occurrence
            xmlString = "2DTable"
            
            
            ''' get all subsubCategories '''
            subcategoryNameList = []
         
            
            for category in population.subCategories:
                for subcategory in category.subCategories:
                    if subcategory.name not in subcategoryNameList: subcategoryNameList.append(subcategory.name)
                    
            subcategoryNameList.sort(reverse=False)
    
            
            for name in subcategoryNameList:
                xmlString = xmlString + "\t"  + name 
            
            
            for category in population.subCategories:
                xmlString = xmlString + '\r' +  str (category.name)  
                 
                
                
                for subCategoryName in subcategoryNameList:
                    subCategory = category.getSubCategory(subCategoryName)
                    
                    if subCategory == None:
                        xmlString = xmlString + "\t" + '-'  
                        
                    elif ((population.getOccurrenceRecursively(subCategoryName)) / population.occurrence) < threshold:
                        xmlString = xmlString + "\t" + '-'
                        
                    
                    else:
                        xmlString = xmlString + "\t" + str(subCategory.occurrence)
                    
                      
            
            return (xmlString)
        
        
#         elif representationType == 'simpleGraph':
#             
#             DV4 = round (len(self.getSubSet(generic = 4))/ratio, 2)
#             DV3 = round (len(self.getSubSet(generic = -3))/ratio, 2)
#             DV2 = round (len(self.getSubSet(generic = 2))/ratio, 2)
#                       
#             SV4 = round (len(self.getSubSet(generic = -4))/ratio, 2)
#             SV3 = round (len(self.getSubSet(generic = 3))/ratio, 2)
#             SV2 = round (len(self.getSubSet(generic = -2))/ratio, 2)
#                       
#             graphs.SimpleVectorGraph((DV4, SV4), (DV3, SV3), (DV2, SV2)) 
#             
#         elif representationType == 'tonalProfile':
#             self.getProgressionScatter()
            
            
        
    def showLongestPatterns (self, representationType='xml'):
        
        xmlString = "<root>"
        for pattern in self.longestPatterns:
            noteStart = pattern.template[0].noteStart.name
            noteEnd = pattern.template[-1].noteEnd.name
            
            closed = noteStart == noteEnd
            
            
            xmlString = xmlString + '<pattern patternString="%s" length="%s" occurrence="%s" closed="%s">' %(pattern.patternString, pattern.length, pattern.occurrence, closed)
            for instance in pattern.instances:
                xmlString = xmlString + '<instance work="%s" startMeasure="%s" stopMeasure="%s"></instance>' %(instance[0].noteStart.editorial, instance[0].noteStart.measureNumber, instance[-1].noteEnd.measureNumber)
            
            xmlString = xmlString + "</pattern>"
            
        xmlString = xmlString + "</root>"
        return xmlString
            
            
    
    
    def setLongestPatterns (self, minimalPattern = 4, maximalPattern = 12, minimalOccurrence =2):
        
        ''' returns a list of recurrent longest vector patterns ''' 
        
        longestPatternList = []
        
        
        for length in range (minimalPattern, maximalPattern):
            print("... searching pattern lengths: " + str (length))
            ''' get different patterns with n lengths '''
            differentPatternList = self.getDifferentPatternsWithNLenght(length)
            
            
            ''' loop over different patterns and get their different instances '''
            for pattern in differentPatternList:
                if pattern == None: continue
                pattern.instances = self.getInstancesOfThisPattern(pattern)
                pattern.occurrence = len(pattern.instances)
          
                
                ''' if occurrence >= minimal occurrence, add to list '''
                if len (pattern.instances) >= minimalOccurrence:
                    longestPatternList.append(pattern) 
                
        ''' sort pattern list 1. according to length, 2. according to occurrence'''
        longestPatternList.sort(key=lambda x: x.occurrence, reverse=True) 
        longestPatternList.sort(key=lambda x: x.length, reverse=True)            
        
        if len(longestPatternList)==0: print ("No patterns to display...")  
        
        for pattern in longestPatternList:
            print ("harmonic pattern: %s, pattern length: %s pattern occurrence: %s" %(pattern.patternString, pattern.length, pattern.occurrence))            
        
        
        self.longestPatterns = longestPatternList
            
        
        
        
        
    def getDifferentPatternsWithNLenght(self, length):
        
        patternList = []
        
        ''' loop over vector list '''
        for vectorCounter in range (len(self.vectorList)):
            
            ''' get pattern starting at index with n length '''
            pattern = self.getPatternStartingAtIndex(vectorCounter, length)  
            if pattern == None: continue
            ''' check if pattern already in list, if not add it '''
            if self.patternInList(patternList, pattern) == False: patternList.append(pattern)
            
        return patternList
            
    def getInstancesOfThisPattern (self, pattern):
        
        patternInstances = []
        
        ''' check if element is pattern and that pattern length < then total list '''
        if not isinstance(pattern, HarmonicPattern): return []
        patternLength = pattern.length
        if patternLength >= len (self.vectorList): return []
        ''' loop over vector list and check subsequences '''
        for vectorCounter in range (len(self.vectorList)):
            patternB = self.getPatternStartingAtIndex(vectorCounter, patternLength)
            
            ''' if sequence corresponds to pattern append '''
            if self.patternsAreIdentical(pattern, patternB): 
                patternInstances.append(patternB.template)
                
        return patternInstances
                            
    
    def getPatternOccurrence (self, patternString):
        vectorList = patternString.split(';')
        patternLength = len (vectorList)
        patternInstances = []
        
        if not isinstance(vectorList, list): return []
        if len(vectorList) >= len (self.vectorList): return []
        
        ''' loop over vector list and check subsequences '''
        for vectorCounter in range (len(self.vectorList)):
            patternB = self.getPatternStartingAtIndex(vectorCounter, patternLength)
            
            ''' if sequence corresponds to pattern append '''
            if patternB == None: continue 
            if len (vectorList) != patternB.length : continue
            if patternString + ";" == patternB.patternString: patternInstances.append (patternB)
            
                
        return patternInstances
    
    
    def getOccurrencesOfThesePatterns (self, patternList=['4;4', '-3;4;-3;4']):
        
        for patternString in patternList:
            patternOccurrence = len (self.getPatternOccurrence(patternString))
            
            print ("Pattern %s \t occurrence: %s" %(patternString, patternOccurrence))
        
        
        
        
        
        
    
    
    
    
    def getPatternStartingAtIndex (self, index, length = 0):
        ''' returns vector pattern starting ad index '''
        ''' returns none if pattern out of range '''
        
        vectorList = []
        
        if index < 0 or index + length >= len (self.vectorList): return None
        
        for vectorCounter in range (index, index + length):
            ''' make sure that the pattern does not overlap two works '''
            if self.vectorList[vectorCounter].lastVector == True and vectorCounter in range (index, index + length -1): 
                return None
            
            vectorList.append(self.vectorList[vectorCounter])
    
                
        return HarmonicPattern(vectorList)
        
        
    def patternsAreIdentical (self, patternA, patternB):
        
        ''' make sure that both are lists and both patterns have same length'''
        if isinstance(patternA, HarmonicPattern) and isinstance(patternB, HarmonicPattern): 
            pass
        else: return False
        if patternA == None or patternB == None: 
            return False
        
        if len(patternA.template) != len(patternB.template): return False
        
        ''' TODO just compare both strings '''
      
        if patternA.patternString != patternB.patternString: return False
            
        return True
    
    def patternInList (self, patternList, pattern):
        
        for listPattern in patternList:
            if self.patternsAreIdentical(pattern, listPattern): return True
            
        return False
        
        
        
        
    
    
    
    def getSubSet (self, generic=None, bassProgression =None):
        vectorList = []
        
        
        for vector in self.vectorList:
            if generic != None:
                if vector.vector.generic.directed == generic:
                    vectorList.append(vector) 
            if bassProgression != None:
                if bassProgression[0].name == vector.noteStart.name and \
                bassProgression[1].name == vector.noteEnd.name:
                    vectorList.append(vector)
                           
                    
        return vectorList
    
    
        
    def getDistance (self):
        cycle5Dictionary = {'C-':-7, 'G-':-6, 'D-':-5, 'A-':-4, 'E-':-3, 'B-':-2, 'F':-1,'C':0 ,'G':1,'D':2, 'A':3, 'E':4, 'B':5, 'F#':6, 'C#':7, 'G#':8, 'D#':9, 'A#':10, 'E#':11}
        minDegreeStart = 11
        maxDegreeStart = -7
        
        for vector in self.vectorList:
            degreeStart = cycle5Dictionary[vector.noteStart.name]
            #logging.info (degreeStart)
            if degreeStart < minDegreeStart:
                minDegreeStart = degreeStart
            if degreeStart > maxDegreeStart:
                maxDegreeStart = degreeStart
                
            
                
        
        
        return maxDegreeStart-minDegreeStart  
        
        
        
    def getProgressionScatter(self):
        
        cycle5Dictionary = {-7:'c-', -6:'g-', -5:'d-', -4:'a-', -3:'e-', -2:'b-', -1:'f', 0:'c' , 1:'g', 2:'d', 3:'a', 4:'e', 5:'b', 6:'f#', 7:'c#', 8:'g#', 9:'d#', 10:'a#', 11:'e#'}
        yCoordinates = []
        xCoordinates = []
        tickLabels = tuple(cycle5Dictionary.values())
        values = [] 
        vectors = []
        
        ''' create x- y-coordinates and get values '''      
        for key1 in cycle5Dictionary.keys():
            for key2 in cycle5Dictionary.keys(): 
                yCoordinates.append(key1) 
                xCoordinates.append(key2) 
                
                note1 = note.Note(cycle5Dictionary[key1])
                note2 = note.Note(cycle5Dictionary[key2])
                subset = self.getSubSet(bassProgression= [note1, note2])
                
                if len(subset) == 0:
                    vectors.append(None)
                else: 
                    vectors.append(subset[0])
                        
                values.append(len (subset)) 
                
                
        ''' create plot '''
                
        #progressionScatterPlot(yCoordinates, xCoordinates, values, tickLabels, vectors)
    
    
   
    
    def _computeVectors (self):
    
        vectorList = []    
        
       
                    
        ''' loop over pitchcoll sequence '''
         
        for chordSequ in self.chordSequenceList:
             
    
            ''' get melodic intervals '''
            for analChordCounter in range(len(chordSequ.chordList)-1):
                
                 
                chord1 =  chordSequ.chordList[analChordCounter]
                chord2 =  chordSequ.chordList[analChordCounter+1]
                 
                 
                if chord1.rootPitch != None and chord2.rootPitch != None:
                     
                        vector = HarmonicVector(chord1, chord2)
                        vectorList.append(vector) 
             
            ''' separator in case of multiple works '''
            if len (vectorList) > 0: 
                vectorList[-1].lastVector = True
        
        return vectorList
    
    
    def _setVectorCategories (self,  structureType="vectorIntervalNature"):
      
        vectorPopulation = VectorCategory ("population")
       
        if structureType =='vectorIntervalNature':
        
            ''' VD / VS '''
            for vector in self.vectorList:
                vectorPopulation.addToSubCategory(vector, vector.category)
                vectorPopulation.vectorList.append(vector)
                vectorPopulation.setOccurence()
                
            
            ''' intervals '''
            vectorTypeCategories = vectorPopulation.subCategories
            for vectorTypeCategory in vectorTypeCategories:
                for vector in vectorTypeCategory.vectorList:
                    vectorTypeCategory.addToSubCategory (vector, vector.vector.generic.directed)  
                    
                    
            
            ''' interval's nature '''
            vectorTypeCategories = vectorPopulation.subCategories
            for vectorTypeCategory in vectorTypeCategories:
                for vectorIntervalCategroy in vectorTypeCategory.subCategories:
                    for vector in vectorIntervalCategroy.vectorList:
                        vectorIntervalCategroy.addToSubCategory(vector, vector.vector.specificName) 
                    
        
        if structureType == "vectorInterval":
            ''' VD / VS '''
            for vector in self.vectorList:
                vectorPopulation.addToSubCategory(vector, vector.category)
                vectorPopulation.vectorList.append(vector)
                vectorPopulation.setOccurence()
                
            
            ''' intervals '''
            vectorTypeCategories = vectorPopulation.subCategories
            for vectorTypeCategory in vectorTypeCategories:
                for vector in vectorTypeCategory.vectorList:
                    vectorTypeCategory.addToSubCategory (vector, vector.vector.generic.directed)  
        
        
        if structureType == 'intervalNatureChord':
            
            
            ''' interval '''
            for vector in self.vectorList:
                vectorPopulation.addToSubCategory(vector, vector.vector.generic.directed) #directedSimpleName
                vectorPopulation.vectorList.append(vector)
                vectorPopulation.setOccurence()
                
            
            ''' chords  '''
            
            vectorCategories = vectorPopulation.subCategories
            for vectorCategory in vectorCategories:
                for vector in vectorCategory.vectorList:
                    vectorCategory.addToSubCategory(vector, str(vector.chordProgression))
                    
        
        if structureType == 'interval':
            
            
            
            
            for vector in self.vectorList:
                vectorPopulation.addToSubCategory(vector, vector.vector.generic.directed) #directedSimpleName
                vectorPopulation.vectorList.append(vector)
                vectorPopulation.setOccurence()
            
                    
                
                    
                    
                    
        return vectorPopulation
                
        
    
    #def getVectorCategory (self, vectorCategory):
    #    vectorList =[] #

    #    if isinstance(vectorCategory, interval.Interval):
    #        for vector in self.vectorList: 
    #            if vector.vector == vectorCategory.generic.directed:
    #                vectorList.append(vector)
    #    
    #    return vectorList 
    
    
    def getAnnotatedFundamentalBass (self):
        for vector in self.vectorList:
            vector.getNote1().lyric = str(vector.getDirectionArrow()) + str(vector.getInterval())
        return self.stream
    
    
            
    
class VectorCategory ():
    def __init__ (self, categoryName):
        self.name  = categoryName
        self.vectorList = []
        self.occurrence = None 
        self.subCategories = [] 
        
    def addToSubCategory(self, vector, subCategoryName):
        subCategory = self.getSubCategory (subCategoryName)
        if subCategory == None:
            subCategory = VectorCategory(subCategoryName)
            self.subCategories.append(subCategory)
        
        subCategory.vectorList.append(vector)
        subCategory.setOccurence()
        
        
    def setOccurence (self):
        self.occurrence = len (self.vectorList)
    
    
    def getSubCategory (self, subCategoryName):
        for category in self.subCategories:
            if category.name == subCategoryName:
                return category
        
        return None
    
    
    def getOccurrenceRecursively (self, categoryName):
        occurrence = 0
        
        for category in self.subCategories:
            if category.name == categoryName:
                occurrence = occurrence + category.occurrence
            
            if len (category.subCategories) != 0:
                occurrence = occurrence + category.getOccurrenceRecursively(categoryName)
                
        return occurrence
                
                
    
    
                
            
        
        
             
        
                 
            
class HarmonicVector (object):
    def __init__(self, chord1, chord2):
        
        
        ''' make sure imput is chord '''
        if isinstance(chord1, Chord) == False: return None
        if isinstance(chord2, Chord) == False: return None
        
        
      
        
        self.chord1 = chord1
        self.chord2 = chord2
        self.rootPitchStart = chord1.rootPitch
        self.rootPitchEnd = chord2.rootPitch
       
                          
        self.vector = self._setVector(interval.Interval(self.rootPitchStart, self.rootPitchEnd)) ## 
        self.category = self._setCategory()
        self.isSubstitution =  self._setIsPrincipal()==True
        self.direction = self.vector.diatonic.direction
        self.vectorString = self.vector.generic.directed 
        
        self.lastVector = False # last vector in work
         
        
    
    
    
    
    def _setVector (self, fbProgression):        
        ''' if interval > fourth then complementary '''
        if fbProgression.generic.directed > 4:
            ''' create complement interval '''
            intervalS = interval.Interval ("-"+fbProgression.complement.simpleName)
            
            return intervalS
        elif fbProgression.generic.directed < -4:
            return fbProgression.complement
            
            
        else:
            return fbProgression
    
    def _setCategory (self):
        if self.vector.generic.directed in [4, 2, -3]:
            return "dominant"
        elif self.vector.generic.directed in [-4, -2, 3]:
            return "subdominant"
    
    def _setIsPrincipal (self):
        if self.vector.generic.directed in [4, -4]:
            return True
        else: 
            return False
    
    def getNote1 (self):
        return self.noteStart
    
    def getNote2 (self):
        return self.noteEnd
    
    def getInterval (self):
        vector = self.vector.diatonic.directedSimpleName
        
        return vector
        
    def getDirectionArrow (self):
        arrow = ""
        if self.category == "dominant":
            arrow = "=>" 
        elif self.category == "subdominant":
            arrow = "<="
        
        return arrow
        
    
    
class HarmonicPattern(object):
    
    def __init__(self, template):
        
        ''' check if template is list and not empty '''
        if isinstance(template, list) == False: 
            return None
        if len(template) == 0: 
            return None
        
        self.template = template
        self.length = len (template)
        self.occurrence = 0
        self.instances = []
        
        patternString = ""
        for vector in self.template:
            patternString = patternString + str (vector.vectorString) + ";"
            
        self.patternString = patternString
        
        
    def addInstance (self, instance):
        self.instance.append(instance)
        self.occurrence = len (self.instances)
        
         


class ChordStatistics ():
    
    def __init__(self, pitchCollSequenceList):
        
        self.chordList = []
        self.chordPopulation = ChordCategory ("dissonance population")
        
        if type(pitchCollSequenceList) is not list: pitchCollSequenceList = [pitchCollSequenceList]
        
        
        ''' loop over all pitchCollSequence lists '''
        for pitchCollSequence in pitchCollSequenceList:
             
             
            '''get chordified stream'''
            chordifiedStream = pitchCollSequence.getChordifiedStream()
            
            ''' loop over chords in stream '''
            flatStream = chordifiedStream.flat
            
            ''' main type roots, bass etc.  ''' 
            for elementChord in flatStream.getElementsByClass(chord.Chord):
                elementChord.removeRedundantPitchClasses()
                self.chordPopulation.chordList.append(elementChord) 
                
                name = elementChord.bass().name if elementChord.bass() != None else "None"
                self.chordPopulation.addToSubCategory(elementChord, name)
                
            self.chordPopulation.setOccurence()
            self.chordPopulation.subCategories.sort(key=lambda x: x.name, reverse=False)
                
                
            ''' subcategrories chord type '''
            rootCategories = self.chordPopulation.subCategories
            
            for rootCategory in rootCategories: # loop over them 
                for chordElement in rootCategory.chordList:
                    intervalList= chordElement.annotateIntervals(returnList = True, stripSpecifiers=False)
                    rootCategory.addToSubCategory(elementChord, sorted(intervalList, key=lambda char: char[1])) 
                
                rootCategory.subCategories.sort(key=lambda x: x.occurrence, reverse=False)
         
        
    
    def show(self, representationType = "text", percents = False, threshold = 0):
        population = self.chordPopulation
        ratio = 1
        
        if percents == True:
                ratio = population.occurrence
        
        if representationType == "text":
            logging.info (population.name + ': ' + str (population.occurrence))
            
            
            
            for category in population.subCategories:
                logging.info ('\t' + str (category.name) + ': ' + str(category.occurrence/ratio))
                for subCategory in category.subCategories:
                    logging.info  ('\t\t' + str(subCategory.name) + ': ' + str(subCategory.occurrence/ratio)) 
                    
                    
        elif representationType == 'xml':
            ratio = population.occurrence
            xmlString = '<population name="%s" occurrence="%s" percentage="%s">' %(population.name, population.occurrence, round (population.occurrence/ratio, 4))
            
            
            ''' roots, real bass etc. '''
            otherCategory = 0 
            for category in population.subCategories:
                
                if category.occurrence/ratio > threshold:
                    xmlString = xmlString + '<category name="%s" occurrence="%s" percentage="%s">' %(category.name, category.occurrence, round (category.occurrence/ratio, 4))
                    
                    otherSubCategory = 0 
                    for subcategory in category.subCategories :
                        if subcategory.occurrence/ratio > threshold:
                            xmlString = xmlString + '<subCategory name="%s" occurrence="%s" percentage="%s"></subCategory>' %(subcategory.name, subcategory.occurrence, round (subcategory.occurrence/ratio, 4))
                        else: otherSubCategory = otherSubCategory + subcategory.occurrence
                                    
                
                    
                    if otherSubCategory > 0:  
                        xmlString = xmlString + '<subCategory name="%s" occurrence="%s" percentage="%s"></category>' %("other", otherSubCategory, round (otherSubCategory/ratio, 4))
                        xmlString = xmlString + '</subCategory>'
                    xmlString = xmlString + '</category>'
                
                else: otherCategory = otherCategory + category.occurrence
                
            if otherCategory > 0:  
                xmlString = xmlString + '<category name="%s" occurrence="%s" percentage="%s"></category>' %("other", otherCategory, round (otherCategory/ratio, 4))
                xmlString = xmlString + '</category>'
  
            xmlString = xmlString + "</population>"
            
            print (xmlString)
            return (xmlString)



class ChordCategory ():
    def __init__ (self, categoryName):
        self.name  = categoryName
        self.chordList = []
        self.occurrence = None 
        self.subCategories = [] 
        
    def addToSubCategory(self, chord, subCategoryName):
        subCategory = self.getSubCategory (subCategoryName)
        if subCategory == None:
            subCategory = ChordCategory(subCategoryName)
            self.subCategories.append(subCategory)
        
        subCategory.chordList.append(chord)
        subCategory.setOccurence()
        
        
    def setOccurence (self):
        self.occurrence = len (self.chordList)
    
    
    def getSubCategory (self, subCategoryName):
        for category in self.subCategories:
            if category.name == subCategoryName:
                return category
        
        return None
    
    

class Chord():
    def __init__(self, pitchCollList):
        ''' this class is used to collection different pitchColls according to their root'''
        
        self.rootPitch = pitchCollList[0].rootPitch 
        self.pitchCollList = pitchCollList
        self.lowestOffset = pitchCollList[0].offset
        self.highestOffet = pitchCollList[-1].offset
        self.duration = 0
        
        for pitchColl in pitchCollList :
            self.duration = self.duration + pitchColl.duration 
       
       
 
class ChordSequence ():
    def __init__ (self, pitchCollSubList):
        ''' this class is used to gather information about succession of chords '''
        ''' it takes as input a pitchCollSequence. this collection in a chord sequence according to the pitchCOll roots '''
        self.pitchCollSubList = pitchCollSubList
        self.chordList = []
        
        rootChangeIndex = 0
        
        
        for pitchCollCounterOne in  range (len (self.pitchCollSubList)):
            if pitchCollCounterOne != rootChangeIndex: continue
            
            
            currentPitchColl = self.pitchCollSubList[pitchCollCounterOne]
            currentRoot = currentPitchColl.rootPitch
            pitchCollList = []
            
            for pitchCollCounterTwo in range (pitchCollCounterOne, len(self.pitchCollSubList)):
                followingPitchColl = self.pitchCollSubList[pitchCollCounterTwo]
                followingRoot = followingPitchColl.rootPitch
                
                if currentRoot == followingRoot:
                    pitchCollList.append(followingPitchColl)
                    if pitchCollCounterTwo == len(self.pitchCollSubList)-1: 
                        self.chordList.append(Chord(pitchCollList))
                    
                    
                else:
                    rootChangeIndex = pitchCollCounterTwo
                    self.chordList.append(Chord(pitchCollList))
                    
                    break
               
                
 