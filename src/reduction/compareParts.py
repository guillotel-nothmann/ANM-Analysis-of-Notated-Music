'''
Created on Aug 27, 2020

@author: christophe
'''

import re

from music21 import stream 

class CompareParts(object):
    '''
    This class is used to compare parts
    Show which parts are identical, show which parts are not
    '''


    def __init__(self, workStream):
        self.workStream = workStream
        
        self.cantusStreamsDictionary = {}
        self.altusStreamsDictionary = {}
        self.tenorStreamsDictionary = {}
        self.bassusStreamsDictionary = {}
        self.otherStreamsDictionary = {}
        
        self.structuralParts = {} ### this contains structured information aboput cantus, altus, tenor and bassus parts (and others)
        
        
        
        
    
        ''' loop over all parts and put them in corresponding dictionaries '''
        
        for part in self.workStream.recurse().getElementsByClass(stream.Part): 
            
            if re.search('cantus', part.partName, re.IGNORECASE):
                self.cantusStreamsDictionary[part.partName]=part
            
            elif re.search('altus', part.partName, re.IGNORECASE):
                self.altusStreamsDictionary[part.partName]=part  
            
            elif re.search('tenor', part.partName, re.IGNORECASE):
                self.tenorStreamsDictionary[part.partName]=part  
                
            elif re.search('bassus', part.partName, re.IGNORECASE):
                self.bassusStreamsDictionary[part.partName]=part  
                
            else:
                self.otherStreamsDictionary[part.partName]=part  
                
        print ("Cantus parts: " + str(len(self.cantusStreamsDictionary)))
        print ("Altus parts: " + str(len(self.altusStreamsDictionary)))
        print ("Tenor parts: " + str(len(self.tenorStreamsDictionary)))
        print ("Bassus parts: " + str(len(self.bassusStreamsDictionary)))
        
        for streamPart in self.otherStreamsDictionary:
            print ("Could not identify the following parts: " + streamPart.partName)
            
            
        ''' compare parts '''
        
        for unused_partKey, part in self.cantusStreamsDictionary.items():
            for measure in part.recurse().getElementsByClass(stream.Measure):
                self.addMeasure("Cantus", part.partName, measure)
                
        for unused_partKey, part in self.altusStreamsDictionary.items():
            for measure in part.recurse().getElementsByClass(stream.Measure):
                self.addMeasure("Altus", part.partName, measure)
        
        for unused_partKey, part in self.tenorStreamsDictionary.items():
            for measure in part.recurse().getElementsByClass(stream.Measure):
                self.addMeasure("Tenor", part.partName, measure)
                
        for unused_partKey, part in self.bassusStreamsDictionary.items():
            for measure in part.recurse().getElementsByClass(stream.Measure):
                self.addMeasure("Bassus", part.partName, measure)
                
                
        for unused_partKey, part in self.otherStreamsDictionary.items():
            for measure in part.recurse().getElementsByClass(stream.Measure):
                self.addMeasure("Other", part.partName, measure)
            
        
        ''' identify combinations '''
                
        for structuralPartKey, structuralPart in self.structuralParts.items():
            structuralPart.analyzeGroups()
        
        
        
    def addMeasure (self, structuralPartName, partName, measure):
        
        ''' check if structural part exist if yes get it, if not create it ''' 
        if  structuralPartName not in self.structuralParts:
            self.structuralParts[structuralPartName] = PartContainer(structuralPartName)
           
            
        structuralPart = self.structuralParts[structuralPartName]
        
        ''' check if measure container exists in part container, if not create it '''
        if measure.offset not in structuralPart.measures:
            structuralPart.measures[measure.offset] = MeasureContainer(structuralPartName, measure)     
        measureCont = structuralPart.measures [measure.offset] 
        
        ''' add measure to measure container ''' 
        measureCont.addMeasure (structuralPartName, partName, measure) 
        
        
    def show(self):
        
        measureString = "\t"
        structuralPart = self.structuralParts["Cantus"]
        
        for unused_key, measure in structuralPart.measures.items():
            measureString = measureString + str (measure.measureNumber) + " (" + str(measure.offset) + ")\t"
            
        print (measureString)
        
        
        for partName in ["Cantus", "Tenor", "Altus", "Bassus", "Other"]:
        
            if partName not in self.structuralParts: continue
            
            structuralPart = self.structuralParts[partName]
            
            
                
            
            for combination in structuralPart.combinationList:
                if len (combination.split(";"))<2: continue
                
                
                combinationString = combination + "\t"
                occurrenceCounter = 0
                for unused_key, measure in structuralPart.measures.items():
                    combinationBool = False
                    for unused_key2, groupCont in measure.partGroups.items():
                        if groupCont.presentationName == combination:
                            combinationString = combinationString + "X\t"
                            occurrenceCounter = occurrenceCounter + 1
                            combinationBool = True
                            break
                    if combinationBool == False: combinationString = combinationString + "\t"
                
                print (combinationString + "\t" + str(occurrenceCounter))
            
            
             
            
            
        
        
        
        
        
         
    

class PartContainer (object):  
    '''
    This class is a container for all measures of a structural part for one measure
    
    ''' 
    def __init__(self, partName):     
        self.partName = partName
        self.measures = {}  ### offset is key 
        self.maxGroups = 0
        self.minGroups = 100
        self.combinationList = []
        
        
    def analyzeGroups(self):
        for unused_keyMeasureCont,  measureCont in self.measures.items():
            if len (measureCont.partGroups) > self.maxGroups : self.maxGroups = len (measureCont.partGroups)
            if len (measureCont.partGroups) < self.minGroups : self.minGroups = len (measureCont.partGroups)
            
            for unused_keyGroupCont, groupCont in measureCont.partGroups.items():
                if groupCont.presentationName not in self.combinationList: self.combinationList.append(groupCont.presentationName) 
            
        self.combinationList.sort()
            
            
            
class MeasureContainer(object):
    '''
    This class is a container for one measure of a structural part 
    
    '''
    def __init__(self, structuralPartName, measure):
        self.partName =  structuralPartName
        self.offset = measure.offset
        self.measureNumber = measure.number
        self.partGroups = {}
        
        
    def addMeasure (self, structuralPartName, partName, measure):
        ''' 
        loops over every partGroup and checks if measure contents is identical with content of the corresponding group
        if so the measure is added, if not a new group is created 
        '''
        
        ''' measure has only silences do not take it into account '''
        noteList = []
        for element in measure.notes:
            noteList.append(element)
        
        if len (noteList) == 0:
            return     
        
        
        for unused_key, partGroup in self.partGroups.items():
            if partGroup.measureCorrespondsToModel(measure):
                partGroup.addMeasureToContainer(measure, partName)
                return 
        
        container = GroupContainer(measure, structuralPartName + "_" + str(len(self.partGroups))) 
        container.addMeasureToContainer(measure, partName)
        self.partGroups[container.groupIndex] = container 
        
class GroupContainer (object):
    ''' This class is a container for all identical parts within one measure '''
    def __init__(self, modelMeasure, groupIndex):
        self.groupIndex = groupIndex
        self.presentationName = None
        self.model = modelMeasure # the model which will be used for comparison
        self.modelNotesAndRestsList = []
        self.parts = {}
        self.partNameList = [] 
        
        for element in modelMeasure.notesAndRests:
            self.modelNotesAndRestsList.append(element)
        
    
    def measureCorrespondsToModel (self, measure):
        ''' compare measure with model '''
        ''' comparison based on durations and pitch classes (insensitive to octaves) of every note and rest element '''
        measureNotesAndRestsList = []
        
        for element in measure.notesAndRests:
            measureNotesAndRestsList.append(element)
        
        
        if len (self.modelNotesAndRestsList) != len (measureNotesAndRestsList): return False
        
        for counter, element in enumerate(self.modelNotesAndRestsList):
            if measureNotesAndRestsList[counter] != element: return False
            
        return True
        
        
        
        
    
    def addMeasureToContainer (self, measure, partName):
        self.parts[partName] = measure
        
        
        self.partNameList.append(partName)
            
        self.partNameList.sort()
        
        self.presentationName = "" 
        for partName in self.partNameList :
            self.presentationName = self.presentationName + partName + "; "
            
            
        
        self.presentationName = self.presentationName[:-2]
        
        
        

                 
            
                
        