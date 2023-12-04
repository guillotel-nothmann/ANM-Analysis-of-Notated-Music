''' imports ''' 
from music21.stream import Score
from music21.note import Note

class PitchAnalysisSimple ():
    def __init__(self, work):
        ''' this is a very basic class to extract pitch classes '''
        self.work = work
        self.pitchClassList = []
        
        
        for note in work.recurse().getElementsByClass(Note):
            if note.name not in self.pitchClassList:
                self.pitchClassList.append(note.name)
        
        
         
    


class PitchAnalysis ():
    
    def __init__(self, analyzedPitches, hierarchyList= ["pitch.step", "pitch.octave", "pitch.alter"],filterList=[]): 
        
        ''' possible hierarchy criteria: all attributes of an analysed pitch:  
         --- .part (part information)
         --- pitch.step (the pitch class WITHOUT alteration: A, B, etc.)
         --- pitch.name (the pitch class with alteration: B-)
         --- pitch.unicodeNameWithOctave (the pitch class Bb4)
         --- pitch.unicodeName (Bb)
         --- pitch.alter (the accidental used: -1, 0, etc.)
         --- pitch.octave (the pitch's octave : 2, 3, etc.)
         --- pitch.nameWithOctave (all information together: "B-4"
         
         etc.
          '''
        
        ''' filters  ? '''
        analysedPitchList = []
        
        if len(filterList) >0:
            for filterElement in filterList:
                for analysedPitch in analyzedPitches:
                    if "part." in filterElement[0]:
                        attributeValue = str (getattr(analysedPitch.part, filterElement[0].replace("part.", "")))
                    else:
                        attributeValue = str (getattr(analysedPitch, filterElement[0]))
                    
                    
                    if attributeValue== filterElement [1]: 
                        analysedPitchList.append(analysedPitch)
        else: analysedPitchList = analyzedPitches
            
        
        self.filterList = filterList
        self.hiearchyList = hierarchyList ### main and sub collections 
        self.instanceList = analysedPitchList 
        self.attributeName = "allPitches"
        self.attributeValue = ""        
        self.subCollectionList = []
        self.attributeValueDic = {}
        
        ''' create subCollections recursively '''
        self.setSubCollections(self, hierarchyList, 0)
        
        
        ''' get attribute values and store them in dictionary '''
        for attributeName in hierarchyList:
            self.attributeValueDic[attributeName]= self.getAttributeValues(attributeName)

    
    def getAttributeValues (self, attributeName):
        
        valueList = []
        
        for instance in self.instanceList:
            
            if "pitch." in attributeName:
                attributeValue = str (getattr(instance.pitch, attributeName.replace("pitch.", "")))
            
            elif "part." in attributeName:
                attributeValue = str (getattr(instance.part, attributeName.replace("part.", "")))
                
            
            else:
                attributeValue = str (getattr(instance, attributeName))
                
            if not attributeValue in valueList: valueList.append(attributeValue)
        return sorted (valueList)
                                         
            
    
    
    def getBasicInformation(self):
        infostring = ""
    
        ''' level 1 '''    
        
        ''' get sorted values '''
        for attributeValue1 in self.attributeValueDic[self.hiearchyList[0]]:
            subCollection = self.getSubCollectionByValue(attributeValue1) 
            infostring = infostring + '\t' + subCollection.getBasicInformation() + '\r'
            
            ''' level 2'''
            if len (self.hiearchyList) <= 1: continue 
            for attributeValue2 in self.attributeValueDic[self.hiearchyList[1]]:
                subSubCollection = subCollection.getSubCollectionByValue(attributeValue2)
                infostring = infostring + '\t\t' +  subSubCollection.getBasicInformation() + '\r' 
                
                ''' level 3'''
                if len (self.hiearchyList) <= 2: continue 
                for attributeValue3 in self.attributeValueDic[self.hiearchyList[2]]:
                    subSubSubCollection = subSubCollection.getSubCollectionByValue(attributeValue3)
                    infostring = infostring + '\t\t\t' + subSubSubCollection.getBasicInformation() + '\r' 
        print (infostring)
        
    
    
    def getHighestScores (self, duration=True):
        
        
     
        
        scoreList = []
        
        ''' extract scores at highest hierarchical level '''
        
        ''' level 1'''
        for attributeValue1 in self.attributeValueDic[self.hiearchyList[0]]:
             
            
           
            subCollection = self.getSubCollectionByValue(attributeValue1) 
            scoreList.append([attributeValue1, subCollection.getOccurrence(duration)])
            
        scoreList.sort(key=lambda x: x[1], reverse = True)    
            
        return scoreList#s[0:2]
            
            
    
    def buildChart (self, duration= True):
        valCounter = -1
        columnList = []
        
        'columnNames'
        columnNames = []
        rowNames = []
        
        
        ''' level 1'''
        for attributeValue1 in self.attributeValueDic[self.hiearchyList[0]]:
            valCounter = valCounter + 1
            column = [] 
            columnList.append(column)
            
           
            subCollection = self.getSubCollectionByValue(attributeValue1) 
            column.append(subCollection.getOccurrence(duration))
            columnNames.append(attributeValue1)
            if valCounter < 1: rowNames.append(attributeValue1)
            
            
            
            ''' level 2'''
            if len (self.hiearchyList) <= 1: continue 
            for attributeValue2 in self.attributeValueDic[self.hiearchyList[1]]:
                subSubCollection = subCollection.getSubCollectionByValue(attributeValue2)
                column.append(subSubCollection.getOccurrence(duration)) 
                if valCounter < 1: rowNames.append(attributeValue2)
                
                ''' level 3'''
                if len (self.hiearchyList) <= 2: continue 
                for attributeValue3 in self.attributeValueDic[self.hiearchyList[2]]:
                    subSubSubCollection = subSubCollection.getSubCollectionByValue(attributeValue3)
                    column.append(subSubSubCollection.getOccurrence(duration)) 
                    if valCounter < 1:rowNames.append(attributeValue3)
        
        ''' build table as string '''
        tableString = "\t"   
                     
        '1 columnNames '''
        for columnName in columnNames:
            tableString = tableString + columnName + "\t"
        tableString = tableString + "\r"    
        
        '2 rows'
        
        for rowCounter in range (0, len (columnList[0])): #how many rows ? 
            tableString = tableString + rowNames[rowCounter] + "\t"
            for column in columnList: #which column ?
                tableString = tableString + str (column[rowCounter]) + "\t"
            tableString = tableString + '\r'     
                
            
            
        print (tableString)         
        
        return columnList
        
    
    def getSubCollectionByName (self, analyzedPitch, attributeName, createNew = True):
        for subCollection in self.subCollectionList:
            
            if "pitch." in attributeName:
                if subCollection.attributeValue == str (getattr(analyzedPitch.pitch, attributeName.replace("pitch.", ""))):
                    return subCollection
            elif "part." in attributeName:
                if subCollection.attributeValue == str (getattr(analyzedPitch.part, attributeName.replace("part.", ""))):
                    return subCollection
                
            
            
            else:
                if subCollection.attributeValue == str (getattr(analyzedPitch, attributeName)):
                    return subCollection
        
        if createNew == True:
            newPitchSubCollection = pitchSubCollection(analyzedPitch, attributeName)
            self.subCollectionList.append(newPitchSubCollection)
        
        return newPitchSubCollection
    
    def getSubCollectionByValue (self, attributeValue):
        for subCollection in self.subCollectionList:
            if subCollection.attributeValue == attributeValue:
                return subCollection
            
        return pitchSubCollection() 
    
    def setSubCollections (self, subCollection, hierarchyList, hiearchyLevel):
        ''' used to set all subcategories recursively '''
        
        ''' check if subhiearchies, if so call recursively '''
        if hiearchyLevel +1 > len (hierarchyList): return
        
        ''' loop over instances in list '''
        for analyzedPitchCounter in  range (0, len (subCollection.instanceList)):
            analyzedPitch = subCollection.instanceList[analyzedPitchCounter]
            
            pitchSubCollection = subCollection.getSubCollectionByName(analyzedPitch, hierarchyList[hiearchyLevel])
            pitchSubCollection.add(analyzedPitch)

        for subCollection in subCollection.subCollectionList:
            self.setSubCollections(subCollection, hierarchyList, hiearchyLevel +1) 


class pitchSubCollection ():
    
    ''' used to build a subcollection of analyzed pitches    '''
    ''' a subCollection stores the attribute's name and value (i.e. the criterion used for constituting the collection ("pitch.step") and the value of this criterium ("-B"), an list of of all instances, and a further subCollectionContainer'''
    
    
    def __init__(self, analyzedPitch = None, attributeName = None):
        self.instanceList = []
        self.attributeName = attributeName
        self.attributeValue = None
        self.subCollectionList = []
         
        if analyzedPitch == None or attributeName == None: return
        
        if "pitch." in attributeName:
            self.attributeValue = str(getattr(analyzedPitch.pitch, attributeName.replace("pitch.", "")))
        elif "part." in attributeName:
            self.attributeValue = str(getattr(analyzedPitch.part, attributeName.replace("part.", "")))
        
        else:
            self.attributeValue = str(getattr(analyzedPitch, attributeName))
    
    def add(self, instance):
        
        self.instanceList.append(instance)
        
        
    def getBasicInformation(self):
        informationString = "%s: %s, occurence: %s, subCollections: %s" %(self.attributeName, self.attributeValue, len(self.instanceList), len(self.subCollectionList))
        
        return informationString
    
    
    
    
    
    def getOccurrence(self, boolDuration = False):
        
        if boolDuration == False:

            return len(self.instanceList)
        
        else:
            
            duration = 0
            for element in self.instanceList:
                duration = duration + element.segmentQuarterLength
                
            return duration

    
    
    def getSubCollectionByName (self, analyzedPitch, attributeName):
        
        for subCollection in self.subCollectionList:
            if "pitch." in attributeName:
                if subCollection.attributeValue == str (getattr(analyzedPitch.pitch, attributeName.replace("pitch.", ""))):
                    return subCollection
                
            else:
                if subCollection.attributeValue == str (getattr(analyzedPitch, attributeName)):
                    return subCollection
            
        
        newPitchSubCollection = pitchSubCollection(analyzedPitch, attributeName)
        self.subCollectionList.append(newPitchSubCollection)
        
        return newPitchSubCollection
    
    def getSubCollectionByValue (self, attributeValue):
        
        for subCollection in self.subCollectionList:
            if subCollection.attributeValue == attributeValue:
                return subCollection
            
        return pitchSubCollection() 
    