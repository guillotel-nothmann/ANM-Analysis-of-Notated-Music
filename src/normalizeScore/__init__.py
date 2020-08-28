''' used to normalize a score and remove inconsistencies '''

from music21 import stream, meter, note
from progressbar.widgets import CurrentTime 
import copy 

class ScoreNormalization ():

    def __init__(self, inputScore):
        self.inputScore = inputScore
        self.outputScore = copy.deepcopy(inputScore)
        self.semiFlatOutputScore = self.outputScore.semiFlat
        
        
        self.timeSignatureDictionary = {
            24: '6/1', 
            12: '6/2',
            8: '4/2',
            }
        
       
        
         
    ''' TODO: check of all parts have same measure lengths  ? '''    
    
    
    
    def normalizePartNames (self):
        for part in self.semiFlatOutputScore.recurse().getElementsByClass(stream.Part):
            
            if part.name != "":
            
                part.name = part.partName
        return self.outputScore
            
        
    
    
    
    
    def addTimeSignaturesWhereNeeded (self):
        ''' used to add time signatures if time signature and effective measure length are incoherent '''
        currentOffset = 0
        
        
        ''' loop over every part '''
        for part in self.semiFlatOutputScore.recurse().getElementsByClass(stream.Part):
           
            ''' loop over every measure of semiflat score '''
            for partMeasure in part.recurse().getElementsByClass(stream.Measure): 
               
            
                currentOffset = partMeasure.offset
                currentTimeSignature = part.recurse().getElementAtOrBefore(currentOffset, meter.TimeSignature)
                 
                currentTimeSignatureQuarterLength = currentTimeSignature.numerator / currentTimeSignature.denominator
            
                
                duration = partMeasure.duration.quarterLength
                
                
                ''' special case : measure is emoty '''
                if self.measureHasNotes(partMeasure)== False:
                    duration = self.gethighestMeasureLength(partMeasure)
                    partMeasure.duration.quarterLength = duration
                    self.fillMeasureWithBreaks(partMeasure)
                    
                    print ("empty")
                
                #if self.measureHasNotes(partMeasure) == False:
                #    print ("empty measure")
                    
                
                '''  if current measure in quarter length duration does not correspond to current TS, add one....  '''
                if duration/4 != currentTimeSignatureQuarterLength:
                    bestTS = self.getBestTimeSigatureForMeasure(partMeasure)
                    #bestTS.setDisplay("")
                    if bestTS != None: partMeasure.timeSignature = bestTS
                    currentTimeSignature = bestTS
                    currentTimeSignatureQuarterLength = currentTimeSignature.numerator / currentTimeSignature.denominator
                    
        
        return self.outputScore
    
   
    def resetMeasureOffsets(self):
        
        
        
        
        ''' loop over every part '''
        for part in self.semiFlatOutputScore.recurse().getElementsByClass(stream.Part):
            currentOffset = 0
           
            ''' loop over every measure of semiflat score '''
            for partMeasure in part.recurse().getElementsByClass(stream.Measure): 
                partMeasure.offset = currentOffset
                
                currentOffset = partMeasure.duration.quarterLength
                
        return self.outputScore
                
    
    def gethighestMeasureLength (self, measure):
        ''' get all measures at this offset in stream and returns highest duration in quarter length '''
        highestDuration = 0
        
        measureNumber = measure.number
        
        for part in self.semiFlatOutputScore.recurse().getElementsByClass(stream.Part):
            for partMeasure in part.recurse().getElementsByClass(stream.Measure):
                if partMeasure.number == measureNumber:
            
             
                    if partMeasure.duration.quarterLength > highestDuration:
                        highestDuration = partMeasure.duration.quarterLength
                        break
                
        return highestDuration
    
    
    def fillMeasureWithBreaks (self, measure):
        quarterLengthDuration = measure.duration.quarterLength
        highestTime = measure.highestTime
        
        breakToAdd = quarterLengthDuration - highestTime
        if breakToAdd == 0: return
        
        
        
        if breakToAdd.is_integer():  
            restnote = note.Rest()
            restnote.duration.quarterLength = breakToAdd
            
            
            measure.insert(highestTime, restnote)
            
            
        else: print ("Cannot add silence to empty measure")
        
        
        
    
    
    def measureHasNotes(self, measure):
        
        for unused in measure.recurse().getElementsByClass(note.Note): 
            return True
        return False
        
        
        
    
    
    def getBestTimeSigatureForMeasure (self,partMeasure):
        currentMeasureDuration = partMeasure.duration.quarterLength 
        
        
        
        
        if currentMeasureDuration in self.timeSignatureDictionary:
            return meter.TimeSignature (self.timeSignatureDictionary[currentMeasureDuration])
             
        
        if currentMeasureDuration.is_integer():  
            return meter.TimeSignature (str(int (currentMeasureDuration)) + "/4")
        
        else: 
            print ("Cannot compute time signature !")
            return None
            
        
        