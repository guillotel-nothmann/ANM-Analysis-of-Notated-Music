'''
Created on Feb 7, 2020

@author: christophe
'''
from music21 import interval
from music21.note import Note, pitch    
from music21.interval import ChromaticInterval, Direction   
import ast

class ModalAnalysis(object):
    
 
        
    
    def getModeFromFinalisAndDiatonicSystem(self, finalis, diatonicScale):
        self.finalis= finalis
     
        
        ''' build diatonic scale '''
        self.diatonicScale = diatonicScale
        self.diatonicDegree = None
 
        self.twelveModeDictionary = { 
            1 : "ionian",
            2 : "dorian",
            3 : "phrygian",
            4 : "lydian",
            5 : "mixolydian",
            6 : "aeolian",
            7 : "locrian"
            }
        
        
        ''' identify scale degree '''
        
        for counter, pitch in enumerate (self.diatonicScale.pitches):
            if pitch.name == finalis: 
                self.diatonicDegree = counter + 1
                return self.twelveModeDictionary[self.diatonicDegree]
                
        return None
    
    def getmajorMinorThird (self):
        
        if self.diatonicDegree in [1,4, 5]: 
            self.majorMinorThird = "major"
            
        elif self.diatonicDegree in [2,3,6,7]:
            self.majorMinorThird = "minor"
            
        else: self.majorMinorThird = None
        
        return self.majorMinorThird
    
    
    def getOctaveDivision (self, modalPart, final, lowerExpansion = -1, upperExpansion = 1, lowerContraction = 1, upperContraction = -1):  
        
        # at this stage octaves do not matter. This should be changed for modal polyphony
        
        ''' authentic octave division '''
        authenticLowerHard = self.getAmbitusLimit(final, 0)
        authenticUpperHard = self.getAmbitusLimit(final, 0)
        
        authenticLowerExpansion = self.getAmbitusLimit(final, lowerExpansion) # 
        authenticlowerContraction = self.getAmbitusLimit(final, lowerContraction) #
        
        authenticUpperExpansion = self.getAmbitusLimit(final, upperExpansion)
        authenticUpperContraction = self.getAmbitusLimit(final, upperContraction)
        
        
        ''' plagal octave division '''
        plagalLowerHard = self.getAmbitusLimit(final, 0, "plagal")
        plagalUpperHard = self.getAmbitusLimit(final, 0, "plagal")
        
        plagalLowerExpansion = self.getAmbitusLimit(final, lowerExpansion, "plagal") # 
        plagallowerContraction = self.getAmbitusLimit(final, lowerContraction, "plagal") #
        
        plagalUpperExpansion = self.getAmbitusLimit(final, upperExpansion, "plagal")
        plagalUpperContraction = self.getAmbitusLimit(final, upperContraction, "plagal")
        
   
        
       
        
        
        self.octaveDivisionPartList = []
        
        if modalPart.ambitus== None: return ['None']
         
        ambitusLow = modalPart.ambitus[0]
        ambitusHigh = modalPart.ambitus[1]
        
        ''' check if ambitus exceeds octave '''
        ambitusExceedsOctave = False
        contractedAmbitus = False
        ambitusInterval = interval.Interval(ambitusLow, ambitusHigh)
        if ambitusInterval.semitones > 12: ambitusExceedsOctave = True
        if ambitusInterval.semitones <=9: contractedAmbitus = True
        
        
        lowerNoteIsAuthentic = False
        lowerNoteIsPlagal = False
        
        upperNoteIsAuthentic = False
        upperNoteIsPlagal = False
         
        
        if ambitusLow.step in authenticLowerHard: lowerNoteIsAuthentic=True
        if ambitusLow.step in authenticLowerExpansion: lowerNoteIsAuthentic=True
        if ambitusLow.step in authenticlowerContraction: lowerNoteIsAuthentic=True
        
        if ambitusLow.step in plagalLowerHard: lowerNoteIsPlagal=True
        if ambitusLow.step in plagalLowerExpansion: lowerNoteIsPlagal=True
        if ambitusLow.step in plagallowerContraction: lowerNoteIsPlagal=True
        
        if ambitusHigh.step in authenticUpperHard: upperNoteIsAuthentic= True
        if ambitusHigh.step in authenticUpperExpansion: upperNoteIsAuthentic= True
        if ambitusHigh.step in authenticUpperContraction: upperNoteIsAuthentic= True
        
        if ambitusHigh.step in plagalUpperHard: upperNoteIsPlagal= True
        if ambitusHigh.step in plagalUpperExpansion: upperNoteIsPlagal= True
        if ambitusHigh.step in plagalUpperContraction: upperNoteIsPlagal= True
        
        
        
        
        if lowerNoteIsAuthentic and upperNoteIsAuthentic: self.octaveDivisionPartList.append("authentic")
        elif lowerNoteIsPlagal and upperNoteIsPlagal: self.octaveDivisionPartList.append("plagal")
        elif lowerNoteIsAuthentic and ambitusExceedsOctave: self.octaveDivisionPartList.append("authentic_greater_than_octave")
        elif upperNoteIsPlagal and ambitusExceedsOctave: self.octaveDivisionPartList.append( "plagal_greater_than_octave")
        elif lowerNoteIsAuthentic and contractedAmbitus: self.octaveDivisionPartList.append( "authentic_smaller_than_octave")
        elif upperNoteIsPlagal and contractedAmbitus: self.octaveDivisionPartList.append( "plagal_smaller_than_octave")
        
        else: self.octaveDivisionPartList.append("undefined")
            
          
            
        return self.octaveDivisionPartList[0]
   
    
    
    
    def identifySpecificPitchesInSystem(self, bestScale, analysedPitches, pitchSystemList = [['G#', ''], ['A-', ''], ['C#', 'F diatonic'],['E-', 'C diatonic'],['B-', 'G diatonic'],['B-', 'D diatonic']]):
        
        identifiedPitchesInSystem = []
        for pitchSystem in pitchSystemList:
            pitch = pitchSystem[0]
            system = pitchSystem[1]
         
            
            if system == '' or system == bestScale[0].name:
                for analysedPitch in analysedPitches:
                    if analysedPitch.pitch.nameWithOctave == pitch: #.name if pitch class
                        identifiedPitchesInSystem.append(pitchSystem)
                        break
        
        if len (identifiedPitchesInSystem)== 0: identifiedPitchesInSystem= ""
            
        return identifiedPitchesInSystem
                    
                    
            
        
        
    def getAmbitusLimit (self, pitchString, liberty, param="authentic"):
        
        diatonicScalePitches = self.diatonicScale.pitches
        del diatonicScalePitches[-1]
        shift = 0
        
        if param == "plagal": shift = -3
    
    
    
        step = 1
        if liberty<0: step = -1
        
        'identify pitch index'
        index = None
        for counter, diatonicPitch in enumerate (diatonicScalePitches):
            if diatonicPitch.name == pitchString: 
                index = counter
                break
            
        if index == None: return 
        
        ''' create libertyList '''           
        libertyList = [index+shift]
        for libertyIndex in range (index, index + liberty, step):
            libertyList.append(libertyIndex+step + shift)
            
        
        ''' createPitchList '''
        pitchList = []
        
        for libertyIndex in libertyList:
            pitchList.append(diatonicScalePitches[libertyIndex%7].name)        
        
            
        return pitchList  



class ModalMarkers (object): 
        
    def __init__(self):
        
        ''' load theoretical model '''
        self.modeList = []
        self.modalMarkerList= [] 
        self.loadTheoreticalModel()
        self.loadWorks()
        
        
    def cadenceDegrees (self):
        
        ''' extracts cadences in modes from txt data '''
        
        modeCadenceList = []
        for workModalMarkers in self.modalMarkerList:
            self.addModeToList(modeCadenceList, str(workModalMarkers.mode) + '_' + workModalMarkers.root, workModalMarkers.cadenceSuccessions.split("-"))
            
        
        
        
        for modeCadence in modeCadenceList:
            print (modeCadence)
            
            
            
            
    def addModeToList (self, modeCadenceList, modeFinalis, cadenceList):
        ''' used to add cadence occurrences (cadenceList) to different modes'''  
        
        ''' check if mode exists in modeCadenceList '''
        for modeCadence in modeCadenceList:
            if modeCadence [0] == modeFinalis:
                return self.addCadencesToThisMode(modeCadence, cadenceList)
        
        ''' if not add new entry '''
        
        return modeCadenceList.append(self.addCadencesToThisMode([modeFinalis, []], cadenceList))
                
        
                
                

    def addCadencesToThisMode (self, modeCadences, cadenceList):
        ''' add cadence occurrences (cadenceList) to this mode '''
        
        for cadence in cadenceList:
            cadenceOccurrence = self.addCadenceToThisMode(modeCadences[1], cadence)
            if  cadenceOccurrence != None: modeCadences[1].append(cadenceOccurrence)
            
        return modeCadences
            
              
            
        return modeCadences
        
    def addCadenceToThisMode (self, modeCadence, cadence):
        ''' either update cadence occurrence or create cadence '''
        for modeCadence in modeCadence:
            if modeCadence[0] == cadence:
                modeCadence[1] = modeCadence[1] + 1
                return  
        return [cadence, 1]
         
        
        
         
    
    
    def pitchIsHigherOrEquals (self, referencePitch, observedPitch, liberty=2):
        
        if referencePitch == "": 
            print ()
            
        if observedPitch == "":
            print ()
        
        libertyInterval = ChromaticInterval(liberty)
        libertyPitch = libertyInterval.transposePitch(pitch.Pitch(referencePitch))
            
        
       
        
        intervalRefOb =  interval.Interval (libertyPitch, pitch.Pitch(observedPitch))
        
        if intervalRefOb.direction == Direction.ASCENDING: 
            return True
        
        else: return False 
        
    
        
        
    def pitchIsLowerOrEquals (self, referencePitch, observedPitch, liberty=-2):
        
        libertyInterval = ChromaticInterval(liberty)
        libertyPitch = libertyInterval.transposePitch(pitch.Pitch(referencePitch))
            
        intervalRefOb =  interval.Interval (libertyPitch, pitch.Pitch(observedPitch))
        
        if intervalRefOb.direction == Direction.DESCENDING: 
            return True
        
        else: return False 
        
    
    def pitchesAreCompliantWithAmbitus (self, observedAmbitus, theoreticalAmbitus, liberty = [-2, 2]):
        observedAmbitusLow = observedAmbitus[0]
        observedAmbitusHigh = observedAmbitus[1]
        
        theoreticalAmbitusLow = theoreticalAmbitus[0]
        theoreticalAmbitusHigh = theoreticalAmbitus[1]
        
        ''' low note must be higher or equal theoretical low limit '''
        lowNoteBool = self.pitchIsHigherOrEquals(theoreticalAmbitusLow, observedAmbitusLow,  liberty[0])
        highNoteBool = self.pitchIsLowerOrEquals(theoreticalAmbitusHigh, observedAmbitusHigh, liberty[1])
        
        if lowNoteBool == True and highNoteBool == True: return True
        
        return False
        
        
    def pitchIsInList (self, observedPitch, theoreticalPitchList):
        if observedPitch in theoreticalPitchList: return True
        
        return False
        
    
    def modesAttribution (self):
        modesAttributionList = []
        ''' make stats on accepted unaccepted criteria '''
        observationOccurrenceList = []
         
        
        for workModalMarkers in self.modalMarkerList:
            modesAttributionList.append (self.modeAttribution(workModalMarkers))
            
        for attributionWork in modesAttributionList:
            number = attributionWork[1].workNumber
            name = attributionWork[0][0].name
            score = attributionWork[0][1]
            wrongs = attributionWork[0][2]
            rights = attributionWork[0][3]
            notMentionnedList = attributionWork[0][4]
            
            
            
            for wrong in wrongs: self.addEntryToList(observationOccurrenceList, wrong, 0)
            for right in rights: self.addEntryToList(observationOccurrenceList, right, 1)
            for notMentionned in notMentionnedList: self.addEntryToList(observationOccurrenceList, notMentionned, 2)
            
                
            
            print (str(number) + "\t" + str(name) + "\t" + str(score) + "\t" + str(wrongs) + "\t" + str(rights) + "\t" + str(notMentionnedList))
            
        
        for observation in observationOccurrenceList:
            string = ""
            for element in observation: string = string + str(element) + '\t' 
            print (string)
            
        
  
            
            
    
    def addEntryToList (self, observationList, entry, positiveNegative):
        for  element in  observationList:
            if element[0] == entry:
                element[1 + positiveNegative] = element[1 + positiveNegative] + 1
                return
        listElement = [entry, 0, 0, 0]
        listElement [1 + positiveNegative] = listElement [1 + positiveNegative] + 1
        
        observationList.append(listElement)
        return  
            
            
            
            
    def getModeModels (self, modeNameList, finalPitchClass, octaveDivision = "" ):
        modelList = []
        
        for modeName in modeNameList:
            for modeModel in self.modeList:
                if modeModel.modeName != modeName : continue
                if modeModel.finalisPitchClass != finalPitchClass: continue
                if octaveDivision != "":
                    if modeModel.octaveDivision != octaveDivision: continue
                    
                modelList.append(modeModel)
        
        return modelList
        
    
    def modeAttribution (self, workModalMarkers):
        
       
        ''' select models corresponding to mode '''
        
        
        #if workModalMarkers.workNumber == "005.musicxml":
        print (workModalMarkers.workNumber)
            
        
        restrictedModeList = self.getModeModels(workModalMarkers.mode, workModalMarkers.root)
        
        if len (restrictedModeList) == 0:
            return ([ModalEnsemble(), 0, [''], [''],['']],workModalMarkers)
       
        
        modelWorkMatchList = []
        for mode in restrictedModeList:
            positiveEvidence = 0
            negativeEvidence = 0
            totalEvidence = 0
            negativeEvidenceList = []
            positiveEvidenceList = []
            notMentionnedList = []
            
            
            
            ''' necessary conditions '''
            #if mode.bassusHasFinalis != workModalMarkers.bassusFinalis:
            #    continue
                 
        
            ''' finalis '''
            if mode.cantusHasFinalis == workModalMarkers.cantusFinalis:
                positiveEvidence = positiveEvidence + 1
                positiveEvidenceList.append("cantusHasFinalis")
            else: 
                negativeEvidence = negativeEvidence + 1
                negativeEvidenceList.append("cantusHasFinalis")
            
            totalEvidence = totalEvidence + 1
            
            if mode.bassusHasFinalis == workModalMarkers.bassusFinalis:
                positiveEvidenceList.append("bassusHasFinalis")
                positiveEvidence = positiveEvidence + 1
            else: 
                negativeEvidence = negativeEvidence + 1
                negativeEvidenceList.append("bassusHasFinalis")
            totalEvidence = totalEvidence + 1
            
        
            
            ''' ambitus '''
            theoreticalAmbitusCantus = mode.cantusHasAmbitus.split(";")
            theoreticalAmbitusAltus = mode.altusHasAmbitus.split(";")
            theoreticalAmbitusTenor = mode.tenorHasAmbitus.split(";")
            theoreticalAmbitusBassus = mode.bassusHasAmbitus.split(";")
            
             
            
            
            if self.pitchesAreCompliantWithAmbitus([workModalMarkers.lowestNoteCantus, workModalMarkers.highestNoteCantus], theoreticalAmbitusCantus):
                positiveEvidenceList.append("ambitusCantus")
                positiveEvidence = positiveEvidence + 1
            else: 
                negativeEvidence = negativeEvidence + 1
                negativeEvidenceList.append("ambitusCantus")
            totalEvidence = totalEvidence + 1 
            
            if self.pitchesAreCompliantWithAmbitus([workModalMarkers.lowestNoteAltus, workModalMarkers.highestNoteAltus], theoreticalAmbitusAltus):
                positiveEvidenceList.append("ambitusAltus")
                positiveEvidence = positiveEvidence + 1
            else: 
                negativeEvidence = negativeEvidence + 1
                negativeEvidenceList.append("ambitusAltus")
            totalEvidence = totalEvidence + 1  
            
            
            if workModalMarkers.highestNoteTenor != "" and workModalMarkers.lowestNoteTenor != "": 
                if self.pitchesAreCompliantWithAmbitus([workModalMarkers.lowestNoteTenor, workModalMarkers.highestNoteTenor], theoreticalAmbitusTenor):
                    positiveEvidenceList.append("ambitusTenor")
                    positiveEvidence = positiveEvidence + 1
                else: 
                    negativeEvidence = negativeEvidence + 1
                    negativeEvidenceList.append("ambitusTenor")
                totalEvidence = totalEvidence + 1     
            #else: notMentionnedList.append("ambitusTenor") 
            
            if self.pitchesAreCompliantWithAmbitus([workModalMarkers.lowestNoteBassus, workModalMarkers.highestNoteBassus], theoreticalAmbitusBassus):
                positiveEvidenceList.append("ambitusBassus")
                positiveEvidence = positiveEvidence + 1
            else: 
                negativeEvidence = negativeEvidence + 1
                negativeEvidenceList.append("ambitusBassus")
            totalEvidence = totalEvidence + 1        
            
            
            ''' pitch hierarchies - repercussio '''
            observedPitchList = []
            
            
            pitchOccurrenceList = ast.literal_eval(workModalMarkers.strongestPitchesCantus)
            
            for pitchOccurence in pitchOccurrenceList:
                observedPitchList.append(pitchOccurence[0])
                
            for observedPitch in observedPitchList:
                if self.pitchIsInList(observedPitch, mode.cantusHasRepercussio.split(";")):
                    positiveEvidenceList.append("Repercussio")
                    positiveEvidence = positiveEvidence + 1
                else: 
                    negativeEvidence = negativeEvidence + 1
                    negativeEvidenceList.append("Repercussio")
                totalEvidence = totalEvidence + 1
            
            ''' diatonia '''  
            if mode.isInSystema != "":
                isInSystem = ast.literal_eval(mode.isInSystema)
                systemList = ast.literal_eval(workModalMarkers.bestScale)
                if isInSystem[0] in systemList:
                    positiveEvidenceList.append("Systema")
                    positiveEvidence = positiveEvidence + 1
                else: 
                    negativeEvidence = negativeEvidence + 1
                    negativeEvidenceList.append("Systema")
                totalEvidence = totalEvidence + 1
            else: notMentionnedList.append("Systema") 
                    
            
            if mode.hasSystemAlteration:
                if mode.hasSystemAlteration == workModalMarkers.keyCantus:
                    positiveEvidenceList.append("Alterations")
                    positiveEvidence = positiveEvidence + 1
                else: 
                    negativeEvidence = negativeEvidence + 1
                    negativeEvidenceList.append("Alterations")
                totalEvidence = totalEvidence + 1
            else: notMentionnedList.append("Alterations") 
                    
            
            ''' clefs ''' 
            if mode.cantusHasClavisSignatura !="":
                clefList = mode.cantusHasClavisSignatura.split(";")
                if workModalMarkers.clefCantus in clefList:
                    positiveEvidenceList.append("cantusClef")
                    positiveEvidence = positiveEvidence + 1
                else: 
                    negativeEvidence = negativeEvidence + 1
                    negativeEvidenceList.append("cantusClef")
                totalEvidence = totalEvidence + 1
            else: notMentionnedList.append("cantusClef") 
            
            if mode.bassusHasClavisSignatura !="":
                clefList = mode.bassusHasClavisSignatura.split(";")
                if workModalMarkers.clefBassus in clefList:
                    positiveEvidenceList.append("bassusClef")
                    positiveEvidence = positiveEvidence + 1
                else: 
                    negativeEvidence = negativeEvidence + 1
                    negativeEvidenceList.append("bassusClef")
                totalEvidence = totalEvidence + 1    
            else: notMentionnedList.append("bassusClef")   
            
            if mode.tenorHasClavisSignatura !="":
                clefList = mode.tenorHasClavisSignatura.split(";")
                if workModalMarkers.clefTenor in clefList:
                    positiveEvidenceList.append("tenorClef")
                    positiveEvidence = positiveEvidence + 1
                else: 
                    negativeEvidence = negativeEvidence + 1
                    negativeEvidenceList.append("tenorClef")
                totalEvidence = totalEvidence + 1
            else: notMentionnedList.append("tenorClef")
             
            
            ''' compute score '''
                
            score = (positiveEvidence / totalEvidence) 
            
            modelWorkMatchList.append([mode, score, negativeEvidenceList, positiveEvidenceList, notMentionnedList])
        modelWorkMatchList.sort(key=lambda x: x[1], reverse=True)
        
       
            
        return (modelWorkMatchList[0], workModalMarkers) 
            
            
            
            
        
    def loadWorks(self):
        self.worklFile = open('/Users/christophe/Dropbox/Praetorius/Analyse/workData.txt', 'r', encoding="utf-8") 
        for counter, line in enumerate (self.worklFile):
            if counter == 0: continue
            workData = line.split("\t")
            modalMarker = ModalMarker(workData)
            self.modalMarkerList.append(modalMarker)
        
    def loadTheoreticalModel (self):
        
        self.modelFile = open('/Users/christophe/Dropbox/Praetorius/Analyse/theoreticalData.txt', 'r', encoding="utf-8")
        for counter, line in enumerate (self.modelFile):
            modeData = line.split("\t")
            if counter > 0:
                mode = ModalEnsemble()
                mode.name = modeData[0]
                mode.cantusHasOctaveDivision = modeData[1]
                mode.altusHasOctaveDivision =modeData[2]   
                mode.tenorHasOctaveDivision = modeData[3]
                mode.bassusHasOctaveDivision =modeData[4]
                mode.cantusHasClavisSignatura = modeData[5]
                mode.bassusHasClavisSignatura =modeData[6]
                mode.tenorHasClavisSignatura =modeData[7]
                mode.cantusHasAmbitus = modeData[8]
                mode.altusHasAmbitus = modeData[9]
                mode.tenorHasAmbitus = modeData[10]
                mode.bassusHasAmbitus = modeData[11]
                mode.cantusHasFinalis =modeData[12]
                mode.bassusHasFinalis = modeData[13]
                mode.cantusHasRepercussio = modeData[14]
                mode.isInSystema = modeData[15]
                mode.hasSystemAlteration = modeData[16]
                mode.isTransposition = modeData[17]
                mode.hasOctaveSpecies = modeData[18]
                mode.modeName = modeData[19]
                mode.finalisPitchClass = modeData[20]
                mode.octaveDivision = modeData[21]
                self.modeList.append(mode)
        self.modelFile.close()
        
        
class ModalMarker (object):
    def __init__(self, dataList): 
        self.workNumber = dataList[0] 
        self.composer = dataList[1] 
        self.title = dataList[2]
        self.clefCantus = dataList[3]
        self.clefAltus = dataList[4]    
        self.clefTenor = dataList[5]  
        self.clefQuintus = dataList[6]
        self.clefSextus = dataList[7] 
        self.clefBassus = dataList[8] 
        self.parts = dataList[9] 
        self.keyCantus = dataList[10].replace("'", "") 
        self.keyAltus = dataList[11] 
        self.keyTenor = dataList[12]
        self.keyQuintus = dataList[13]  
        self.keySextus = dataList[14]
        self.keyBassus = dataList[15] 
        self.lowestNoteCantus = dataList[16]  
        self.highestNoteCantus = dataList[17]   
        self.lowestNoteAltus = dataList[18]    
        self.highestNoteAltus = dataList[19]    
        self.lowestNoteTenor = dataList[20]    
        self.highestNoteTenor = dataList[21]    
        self.lowestNoteQuintus = dataList[22]    
        self.highestNoteQuintus = dataList[23]    
        self.lowestNoteSextus = dataList[24]    
        self.highestNoteSextus = dataList[25]    
        self.lowestNoteBassus = dataList[26]    
        self.highestNoteBassus = dataList[27]    
        self.octaveDvsionCantus = dataList[28]    
        self.octaveDivsionAltus = dataList[29]    
        self.octaveDivsionTenor = dataList[30]    
        self.octaveDivsionQuintus = dataList[31]    
        self.octaveDivsionSextus = dataList[32]    
        self.octaveDivsionBassus = dataList[33]    
        self.octaveDivisions = dataList[34]    
        self.bestScale = dataList[35]    
        self.strongestPitchesCantus = dataList[36]    
        self.finalChord = dataList[37]    
        self.cantusFinalis = dataList[38]    
        self.bassusFinalis = dataList[39]    
        self.root = dataList[40]    
        self.mode =  ast.literal_eval(dataList[41])
        self.majorOrMinoThird = dataList[42]    
        self.cadencePoints = dataList[43]    
        self.cadenceDegrees = dataList[44]    
        self.cadenceSuccessions = dataList[45]    
        self.measures = dataList[46]    
        self.specificPitchesInSystem  = dataList[47]                              
            
class ModalEnsemble(object): 
    ''' this class is used to gather all modal information about a piece '''
    
    def __init__(self):
        
        self.fileName = ""
        self.work = ""
        self.title = ""
        self.composer = ""
        self.measureNumber =""
        self.name=""
        
        ''' all analyzed pitches'''
        self.analysedPitches = ""
        
        ''' scale and system'''
        self.clefsAndKeys = ""
        self.scaleAnal =""
        self.bestScales =""
        
        ''' system, diatonia '''
        self.system = "" ### this should be a list of all 
        self.keys = "" ### this sould be a key list 
        self.isTransposition = ""
        self.octaveSpecies = ""  
        self.finalisPitchClass = ""
       
        
        
        ''' cadences '''
        self.cadences = ""
        self.intermediaryCadences = ""  
        self.cadenceSuccession = ""
        self.cadencePoints = ""
        self.finalChord =""
        self.finalChordRoot =""
        
        ''' mode '''
        self.modeName= "" 
        self.majorMinorThird = ""
        self.octaveDivision = ""
        self.modalParts = {} 
        
        self.vectors = None
         
        
        
        
        
        ''' the following information should be an extraction of modal parts above '''
        self.cantusHasOctaveDivision = ""
        self.altusHasOctaveDivision =""    
        self.tenorHasOctaveDivision = ""
        self.bassusHasOctaveDivision = "" 
        
        self.cantusHasClavisSignatura = ""
        self.bassusHasClavisSignatura = "" 
        self.tenorHasClavisSignatura = ""
        
        self.cantusHasAmbitus = ""
        self.altusHasAmbitus = "" 
        self.tenorHasAmbitus = ""
        self.bassusHasAmbitus = ""
        
        self.cantusHasFinalis = ""
        self.bassusHasFinalis = ""
        
        self.cantusHasRepercussio = "" 
        
        
    def setCadences(self, cadenceAnal):
        self.cadences = cadenceAnal
        self.intermediaryCadences = self.cadences.getCadences(None, "intermediary", None)
        self.finalCadence = self.cadences.getCadences (None, "final", None)
        if len (self.finalCadence) != 0: 
            self.finalChordRoot = self.finalCadence[0]["cadenceChord"]
            self.rootPitch = self.finalCadence[0]["cadenceRoot"]
        else:
            self.finalChordRoot = None
            self.rootPitch = None
        
        self.cadenceSuccession = None #self.cadences.getDegrees("succession")
        self.cadencePoints = None #self.cadences.getDegrees("points")
    
         
        

class ModalPart(object): 
    def __init__(self):
        
        self.partName=""
        self.part = "" # this could be the stream
        
        self.octaveDivision = ""
        self.octaveSpecies = "" 
        self.clef = ""
        self.ambitus = ""
        
        self.finalis = ""
        
        self.strongestPitches = "" 
        self.system = "" 
        self.key = "" 
        self.isTransposition = "" 
        self.modeName= ""
        self.finalisPitchClass = ""
        self.structuralPart = ""
    
         
        
        
        
    
 
                

             
        
        
        
        