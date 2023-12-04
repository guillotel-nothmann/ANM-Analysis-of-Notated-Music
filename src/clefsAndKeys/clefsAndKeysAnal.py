
''' used for key and clef extraction, and tonal types, for example in modal analysis'''
from music21 import clef, key, note, analysis, meter
from modalAnalysis.modes import ModalPart
from music21.interval import Interval 
import string, random
''' input is a parsed musical work'''
''' output is an object with dimensions for parts, clefs for parts etc. '''

class ClefsAndKeysAnalysis(object):



    def __init__(self, work):
        
        self.work = work
        self.OverallAmbitus = None
        self.analyzedParts  = [] # contains all parts of the work
        self.idList = []
        
       
     
    
        ''' loop over parts and store them in list '''
        for part in self.work.parts:
            self.analyzedParts.append(ClefsAndKeysForPart(part))
             
            
        
        self.analyzedPartsDictionary = {}
        for part in self.analyzedParts:
            modalPartInstance = ModalPart()
            modalPartInstance
            
            
            modalPartInstance.part = part # remove ?
            modalPartInstance.partName = part.partName
            modalPartInstance.clef = part.clef
            modalPartInstance.ambitus = part.ambitus
            modalPartInstance.key = part.key
            modalPartInstance.finalis = part.finalis
            modalPartInstance.timeSignature = part.timeSignature
            
  
            
            self.analyzedPartsDictionary[part.partName] = modalPartInstance
            
        
        
    def getPartNames (self, returnParam = "string"):
        partsNameString = ""
        partList = []
        
        for part in self.analyzedParts:
            partName = "%s, " %(str(part.name))
            partsNameString = partsNameString + partName
            partList.append(partName[:-2])
            
        partsNameString = partsNameString[:-2]
        
        
        if returnParam == "string": 
            return partsNameString
        else: return partList

    
    def getClefs (self, returnParam = "string"):
        clefString = ""
        clefList = []
        for part in self.analyzedParts:
            clefName = "%s%s, " %(str(part.clef.sign), str(part.clef.line))
            clefString = clefString + clefName
            clefList.append(clefName[:-2])
        
        clefString = clefString[:-2]
        
        if returnParam == "string": 
            return clefString
        else: return clefList
        
      
    def getAmbitus (self, returnParam = "string"):
        ambitusString = ""
        ambitusList = []
        
        for part in self.analyzedParts:
            if len(part.part.pitches) ==0:continue
            ambitus  = "%s\t%s, " %(str(part.ambitus[0].nameWithOctave), str(part.ambitus[1].nameWithOctave))
            ambitusString = ambitusString + ambitus
            ambitusList.append(ambitus[:-2])
            
        ambitusString = ambitusString [:-2]
       
        if returnParam == "string": 
            return ambitusString
        else: return ambitusList
            
            
    def getFinalis (self, returnParam = "string"):
        finalisList = []
        finalisString = ""
        for part in self.analyzedParts:
            finalis = "%s, " %(part.finalis.nameWithOctave)   
            finalisString = finalisString +  finalis
            finalisList.append(finalis[:-2])
    
    
        finalisString = finalisString[:-2]
        
        if returnParam == "string": 
            return finalisString
        else: return finalisList  
        
    
    def getAlterations (self, returnParam = "string"):
        alterationString = ""
        alterationList = []
        for part in self.analyzedParts:
            alteration = "%s, " %str(part.key.sharps) 
            alterationString = alterationString + alteration
            alterationList.append(alteration[:-2])
            
        alterationString = alterationString[:-2]
        
        if returnParam == "string": 
            return alterationString
        else: return alterationList  
        
    
    def getPart (self, normalizedName):
        ''' used to retrieve one or more parts according to a normalized name (Cantus, Altus, Tenor, Bassus, Quintus, Sextus....)'''
        analyzedPartList = []
        
        for analyzedPart in self.analyzedParts:
            if analyzedPart.normalizedPartName == normalizedName : analyzedPartList.append(analyzedPart)
            
        return analyzedPartList
            
         
    def hasInitialNotes (self):
        ''' returns the initial note of each part '''
        
        initialToneList = []
        
        for part in self.analyzedParts:
            initialToneList.append(part.initialNote)
            
        return initialToneList
    
    def hasKeys (self):
        ''' returns the keys of each part '''
        keyList = []
        for part in self.analyzedParts:
            keyList.append(part.key)
        return keyList
    
    def hasSharps(self):
        ''' returns the accidentals for the whole work'''
        accidentList = []
        for part in self.analyzedParts:
            if part.key.sharps not in accidentList:
                accidentList.append(part.key.sharps)
        return accidentList
        
    
    def hasFinalis(self):
        finalToneList = []
        for part in self.analyzedParts:
            finalToneList.append(str.lower(part.finalis.nameWithOctave))
            
        return finalToneList
        
        
    
    def hasAmbitus(self, partName):
        ambitusList = []
        for part in self.getPart(partName): 
            ambitusList.append(part.ambitus)
                 
        return ambitusList
    
 
    
    def id_generator(self, size=6, chars=string.ascii_uppercase + string.digits):
        genId = None
        
        while genId==None or id in self.idList: 
            genId = ''.join(random.choice(chars) for _ in range(size))
        
        return genId
            
class Ambitus (object):
    
    def __init__ (self):
        
        self.hasPitchHigh = None
        self.hasPitchLow = None
        self.ambitusType = None
        self.normalizedAmbitusList = []         

class ClefsAndKeysForPart (object):
    
    def __init__ (self, part, ambitusToleranceSteps=5):
        
        self.part = part
        self.clef = None
        self.ambitus = None
        self.key = None
        self.finalis = None
        self.partName = None
        self.timeSignature = None
        self.normalizedPartName = None
        self.initialNote = None
        self.partNameDictionary = {
            "cant":"Cantus", 
            "super": "Cantus",
            "alt": "Altus", 
            "ten":"Tenor", 
            "bas":"Bassus", 
            "sixt": "Sixtus", 
            "quin":"Quintus"
        }
        
        
        ''' part name '''
        if hasattr(part , "partName"): 
            self.partName = part.partName
            
            
            for dicEntry in self.partNameDictionary:
                if dicEntry in str.lower(self.partName):
                    self.normalizedPartName = self.partNameDictionary[dicEntry]
                    break
            
        if self.normalizedPartName == None: self.normalizedPartName = "Other"
        
        
        
        
        ''' get clef '''
        clefList = []
        for foundClef in part.flat.getElementsByClass(clef.Clef):
            clefList.append(foundClef)
        if len (clefList) >=1: self.clef = clefList[0]# use first clef only  
            
        
        ''' key signature '''
        keyList = []
        for foundKeySignature in part.flat.getElementsByClass(key.KeySignature):
            keyList.append(foundKeySignature)
        if len (keyList)>=1: self.key = keyList[0] # use first key only
            
        ''' time signature '''
        timeSignatureList = []
        for foundTimeSignature in part.flat.getElementsByClass(meter.TimeSignature):
            timeSignatureList.append(foundTimeSignature)
        if len(timeSignatureList)>=1:self.timeSignature = timeSignatureList[0]
              
        
        
        ''' ambitus '''    
        self.ambitus = Ambitus()
        
        
        ambitus = analysis.discrete.Ambitus().getPitchSpan(part.flat)
        self.ambitus.hasPitchLow = ambitus[0]
        self.ambitus.hasPitchHigh = ambitus[1]
        
        ambitusInterval =  Interval(ambitus[0], ambitus[1])
        
        ''' check if ambitus exceeds octave '''
    
        
        if ambitusInterval.semitones > 12: self.ambitus.ambitusType = "expanded" 
        if ambitusInterval.semitones <=9: self.ambitus.ambitusType= "contracted"
        if ambitusInterval.semitones == 12: self.ambitus.ambitusType= "regular"
        
 
        
        
        diatonicPitchList = ["f", "c", "g", "d", "a", "e", "b"]
        octaveList = [0, 1, 2, 3, 4, 5]
        
        
        ''' generate modal octaves '''
        
        if self.ambitus.ambitusType != "regular":
            for diatonicPitch in diatonicPitchList:
                for octave in octaveList:
                    
                    lowerLimit = note.Note (diatonicPitch + str(octave))
                    upperLimit = note.Note(diatonicPitch + str(octave +1))
                    
                    ''' check intersections '''
                    
                    DifLow = Interval (noteStart=lowerLimit, noteEnd=ambitus[0])
                    DifHigh = Interval (noteStart=upperLimit, noteEnd=ambitus[1])
                    
                    
                    if abs(DifLow.chromatic.semitones) < ambitusToleranceSteps and abs(DifHigh.chromatic.semitones) < ambitusToleranceSteps:
                        self.ambitus.normalizedAmbitusList.append([lowerLimit, upperLimit])
                    elif DifLow.chromatic.semitones < 0 and DifHigh.chromatic.semitones > 0 : # " the modal octave is fully contained in the ambitus."
                        self.ambitus.normalizedAmbitusList.append([lowerLimit, upperLimit])
                    elif DifLow.chromatic.semitones > 0 and DifHigh.chromatic.semitones < 0 : #" the ambitus is fully contained in the modal octave "
                        self.ambitus.normalizedAmbitusList.append([lowerLimit, upperLimit]) 
            
        else:
            self.ambitus.normalizedAmbitusList.append([ambitus[0], ambitus[1]])
                
 
        
        ''' get initial tone and finalis '''
        noteList = []
        for foundNote in part.flat.getElementsByClass (note.Note):
            noteList.append(foundNote)
        if len(noteList) >= 1: 
            self.finalis = noteList[-1]
            self.initialNote = noteList[0]     
                
    
    def show(self):
        print ("Part name: %s, Clef: %s%s, Ambitus: %s, Alterarion(s): %s, Finalis: %s." %(str(self.name), str(self.clef.sign), str(self.clef.line), str(self.ambitus), str(self.key.sharps), str(self.finalis.nameWithOctave)))
        
        
        
   
        
        
        
        
        
        
        
        
        
        
        

        