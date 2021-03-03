
''' used for key and clef extraction, and tonal types, for example in modal analysis'''
from music21 import clef, key, note, analysis
from modalAnalysis.modes import ModalPart
''' input is a parsed musical work'''
''' output is an object with dimensions for parts, clefs for parts etc. '''

class ClefsAndKeysAnalysis(object):



    def __init__(self, work):
        
        self.__version__ = "01082020"
        self.__author__="PolyMIR"
        self.work = work
        self.OverallAmbitus = None
        self.analyzedParts  = [] # contains all parts of the work
       
     
    
        ''' loop over parts and stor them in list '''
        for part in self.work.parts:
            self.analyzedParts.append(ClefsAndKeysForPart(part))
             
            
        
        self.analyzedPartsDictionary = {}
        for part in self.analyzedParts:
            modalPartInstance = ModalPart()
            modalPartInstance
            
            
            modalPartInstance.part = part #should be removed
            modalPartInstance.partName = part.partName
            modalPartInstance.clef = part.clef
            modalPartInstance.ambitus = part.ambitus
            modalPartInstance.key = part.key
            modalPartInstance.finalis = part.finalis
            
  
            
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
        
        

class ClefsAndKeysForPart (object):
    
    def __init__ (self, part):
        
        self.part = part
        self.clef = None
        self.ambitus = None
        self.key = None
        self.finalis = None
        self.partName = None
        
        
        ''' part name '''
        if hasattr(part , "partName"): self.partName = part.partName
        
        
        
        
        ''' get clef '''
        clefList = []
        for foundClef in part.flat.getElementsByClass(clef.Clef):
            clefList.append(foundClef)
        if len (clefList) >=1: self.clef = clefList[0]# use first clef only  
            
        
        ''' key signature '''
        keyList = []
        for foundKeySignature in part.flat.getElementsByClass(key.KeySignature):
            keyList.append(foundKeySignature.sharps)
        if len (keyList)>=1: self.key = keyList[0] # use first key only
            
        
        ''' ambitus '''    
        self.ambitus = analysis.discrete.Ambitus().getPitchSpan(part.flat)
        
        
        ''' get finalis '''
        noteList = []
        for foundNote in part.flat.getElementsByClass (note.Note):
            noteList.append(foundNote)
        if len(noteList) >= 1: self.finalis = noteList[-1]

        
    def show(self):
        print ("Part name: %s, Clef: %s%s, Ambitus: %s, Alterarion(s): %s, Finalis: %s." %(str(self.name), str(self.clef.sign), str(self.clef.line), str(self.ambitus), str(self.key.sharps), str(self.finalis.nameWithOctave)))
        
        
        
        
    
        
        
        
        
        
        
        
        
        
        
        
        

        