from clefsAndKeys.clefsAndKeysAnal import ClefsAndKeysAnalysis
from pitchAnalysis.scales import ScaleAnalysis
from harmonicAnalysis.cadenceAnalysis import Cadences 
from modalAnalysis import modes
from pitchAnalysis.pitchAnal import PitchAnalysis 
import os
from music21 import converter, pitch
from modalAnalysis.modes import ModalEnsemble
import rootAnalysis
from vectors import VectorAnalysis
import random, string

from openpyxl import Workbook    
#from networkx.classes.function import degree
import copy
from builtins import isinstance, getattr, list
from bs4 import element 
from datetime import datetime
#from django.contrib.messages.api import success
from owlready2  import get_ontology, Thing, ObjectProperty, DataProperty, default_world
import types
from SPARQLWrapper import SPARQLWrapper, JSON, POST, BASIC
from pitchCollections import PitchCollectionSequence, PitchCollection, Pitch
from copy import deepcopy
from unittest.test.test_result import classDict



class AnalysisOntology ():
    def __init__(self, modelIRI): 
        self.ontoIRI = modelIRI
        self.onto = get_ontology(self.ontoIRI).load()
        
    
        
        #self.classesAndProperties()
        
        self.workClass = self.addOntologyClass(Thing, "Work")
        ''' work metadata '''
        self.addOntologyDataProperty("hasId", [str]) # metadata
        self.addOntologyDataProperty("hasXMLId", [str]) # metadata
        self.addOntologyDataProperty("hasFileName", [str]) # metadata
        self.addOntologyDataProperty("hasFilePath", [str]) # metadata
        self.addOntologyDataProperty("hasURL", [str]) # metadata
        self.addOntologyDataProperty("hasTitle", [str]) # metadata
        self.addOntologyDataProperty("hasComposer", [str]) # metadata
            
 
    def importOntology (self, ontologyPath):
        importedOntology = get_ontology(ontologyPath).load() 
        self.onto.imported_ontologies.append(importedOntology) 
    
    def zarlinoModality(self, ontologyPath, work):
        self.importOntology(ontologyPath)
        zarlinoOntology = self.onto.imported_ontologies[0]
        
        workClassInstance = self.createWorkInstance(work)
        
        ''' get all properties relevant for analysis '''
        
        propertyList = list(default_world.sparql("""
           SELECT ?s
        WHERE {
            ?s <http://data-iremus.huma-num.fr/ns/sherlock#musicAnnotationProperty> ?d . 
        }
    """))

        partsAnal = ClefsAndKeysAnalysis(work) 
        cadenceAnal = Cadences(work)
        
        propertiesModulesDictionary = {
            "cantusHasAmbitus": partsAnal,
            "altusHasAmbitus": partsAnal,
            "tenorHasAmbitus" : partsAnal,
            "bassusHasAmbitus": partsAnal,
            "hasFinalis": partsAnal,
            "hasInitialTone": partsAnal,
            "hasCadenceOn": cadenceAnal        
            }
    
        for counter, value in enumerate(propertyList):       
            propertyList[counter] = value[0]._name
        
        with self.onto.get_namespace("http://modality-tonality.huma-num.fr/analysisOntology#"):
            for predicate in propertyList: 
                for analyticalResult in getattr(propertiesModulesDictionary[predicate], predicate)(): 
                    getattr(workClassInstance, predicate).append(getattr(zarlinoOntology, analyticalResult)()) 
        print ("")
        
        
        
    
    
    def classesAndProperties(self):
        
        ''' analytical classes and properties created for part analysis, pitch analysis, etc. '''
        ''' add classes corpus, work'''
        #self.corpusAnalysisClass = self.addOntologyClass(Thing, "CorpusAnalysis")
        self.workClass = self.addOntologyClass(Thing, "Work")
        
        
        ''' folder '''
        #worksWithRootPath = "/Users/christophe/Dropbox/Praetorius/Polyhymnia/Source/ontologyTesWithRoot/"
        #self.workBookPath  = '/Users/christophe/Dropbox/Praetorius/Polyhymnia/results/' + self.dt_string + '.xlsx'

       
        
        ''' part analysis '''
        self.partAnalysisClass = self.addOntologyClass(self.workClass, "PartAnalysis")
        self.partCollectionClass = self.addOntologyClass(self.partAnalysisClass, "PartCollection")
        self.partClass = self.addOntologyClass(self.partCollectionClass, "Part")
        
        ''' scale analysis '''
        self.scaleAnalysisClass = self.addOntologyClass(self.workClass, "ScaleAnalysis")
        
        ''' cadences analysis '''
        self.cadenceAnalysisClass = self.addOntologyClass(self.workClass, "CadenceAnalysis")
        self.cadenceClass = self.addOntologyClass(self.cadenceAnalysisClass, "Cadence")
        
        ''' pitch analysis '''
        self.pitchAnalysisClass = self.addOntologyClass(self.workClass, "PitchAnalysis") 
        self.analyzedPitchCollectionSequenceClass = self.addOntologyClass(self.pitchAnalysisClass, "AnalyzedPitchCollectionSequence")
        self.analyzedPitchCollectionClass =  self.addOntologyClass(self.analyzedPitchCollectionSequenceClass, "AnalyzedPitchCollection")
        self.analyzedPitchClass = self.addOntologyClass(self.analyzedPitchCollectionClass, "AnalyzedPitch")
        self.pitchListClass = self.addOntologyClass(self.pitchAnalysisClass, "PitchList")
        
        ''' root analysis ''' 
        self.rootAndProgressionAnalysisClass  = self.addOntologyClass(self.workClass, "RootsAndProgressionsAnalysis") 
        self.rootAnalysisClass  = self.addOntologyClass(self.rootAndProgressionAnalysisClass, "RootAnalysis") 
        self.rootCollectionClass  = self.addOntologyClass(self.rootAnalysisClass, "RootCollection") 
        self.chordInversionClass = self.addOntologyClass(self.rootCollectionClass, "ChordInversion") 
        
        self.vectorAnalysisClass = self.addOntologyClass(self.rootAndProgressionAnalysisClass, "VectorAnalysis") 
        self.vectorCategoryClass = self.addOntologyClass(self.vectorAnalysisClass, "VectorCategory") 
        
        ''' real bass analysis '''
        self.realBassAnalysisClass = self.addOntologyClass(self.workClass, "RealBassAnalysis")
        self.bassScaleDegreeAnalysisClass = self.addOntologyClass(self.realBassAnalysisClass, "BassScaleDegreeAnalysis")
        self.bassScaleDegreeSuccessionAnalysisClass = self.addOntologyClass(self.realBassAnalysisClass, "BassScaleDegreeSuccessionAnalysis")
        
        self.bassScaleDegreeCollectionClass = self.addOntologyClass (self.bassScaleDegreeAnalysisClass, "BassScaleDegreeCollection") 
        self.harmonizationClass = self.addOntologyClass(self.bassScaleDegreeCollectionClass, "Harmonization")
        self.bassScaleDegreeSuccessionCollectionClass = self.addOntologyClass(self.bassScaleDegreeSuccessionAnalysisClass, "BassScaleDegreeSuccessionCollection")
        self.harmonizationSuccessionClass = self.addOntologyClass(self.bassScaleDegreeSuccessionCollectionClass, "HarmonizationSuccession")
        
        ''' modal - tonal analysis '''
        self.modalAnalysisClass = self.addOntologyClass(self.workClass, "ModalAnalysis")
        self.modalClassificationClass = self.addOntologyClass(self.modalAnalysisClass, "ModalClassification")
        
        #rootsClass = addOntologyClass (workClass, "Roots")
        #inversionsClass = addOntologyClass (rootsClass, "Inversions")
        
        ''' add data properties '''
        '''str '''
        
        self.addOntologyDataProperty("hasWork", [str])
        self.addOntologyDataProperty("hasBestDiatonicScale", [str]) # scale analysis 
        
        self.addOntologyDataProperty("hasName", [str])
        self.addOntologyDataProperty("hasAlteration", [str])
        self.addOntologyDataProperty("hasHarmonization", [str])
        
      
        
        
        
        ''' pitch analysis '''
        self.addOntologyDataProperty("hasStrongestPitches", [str])
        self.addOntologyDataProperty("isCategory", [str])
        self.addOntologyDataProperty("hasRootPitch", [str])
        self.addOntologyDataProperty("hasPartName", [str])
        self.addOntologyDataProperty("hasAttack", [str])
        self.addOntologyDataProperty("isSectionEnd", [str])
        self.addOntologyDataProperty("hasRealBass", [str])
        self.addOntologyDataProperty("hasContinuoSigns", [str])
        self.addOntologyDataProperty("hasEndTime", [float])
        self.addOntologyDataProperty("hasBeatStrength", [float])
        
        ''' cadence analysis'''
        self.addOntologyDataProperty("hasFinalScaleDegree", [str])
        self.addOntologyDataProperty("hasFinalChord", [str])
        self.addOntologyDataProperty("hasFinalRoot", [str])
        self.addOntologyDataProperty("hasCadenceType", [str]) # 
        self.addOntologyDataProperty("hasCadenceSubType", [str]) # 
        
        ''' root analysis '''
        self.addOntologyDataProperty("hasRoot", [str])
        self.addOntologyDataProperty("hasRootScaleDegree", [str])
        
        ''' real bass analysis '''
        self.addOntologyDataProperty("hasFirstScaleDegreeName", [str])
        self.addOntologyDataProperty("hasSecondScaleDegreeName", [str])
        self.addOntologyDataProperty("hasFirstHarmonizationName", [str])
        self.addOntologyDataProperty("hasSecondHarmonizationName", [str])
        
        ''' modal analysis '''
        self.addOntologyDataProperty("hasFinalis", [str])
        self.addOntologyDataProperty("hasThird", [str])
        self.addOntologyDataProperty("hasModalSystemName", [str])
        self.addOntologyDataProperty("hasOctaveDivision", [str])
        self.addOntologyDataProperty("hasKey", [str]) # 
        self.addOntologyDataProperty("hasClef", [str]) # 
        self.addOntologyDataProperty("hasAmbitusLow", [str])
        self.addOntologyDataProperty("hasAmbitusHigh", [str])
        #self.addOntologyDataProperty("hasModalAttribution", [str])
        self.addOntologyDataProperty("hasStrongestPitches", [str])
        
        ''' int '''
        self.addOntologyDataProperty("hasMeasureNumber", [int])
        self.addOntologyDataProperty("hasOccurrence", [int])
        self.addOntologyDataProperty("hasPartNumber", [int])
        
        ''' float '''
        self.addOntologyDataProperty("hasOffset", [float])
        self.addOntologyDataProperty("hasDuration", [float])
        
        ''' add object properties '''
        ''' pitch analysis '''
        self.addOntologyObjectProperty("hasPitchAnalysis", self.workClass) 
        self.addOntologyObjectProperty("hasSubCollection", self.pitchAnalysisClass) # pitch analyses can be nested
        self.addOntologyObjectProperty("hasAnalyzedPitchCollectionSequence", self.pitchAnalysisClass)
        self.addOntologyObjectProperty("hasAnalyzedPitchCollection", self.analyzedPitchCollectionSequenceClass)
        self.addOntologyObjectProperty("hasAnalyzedPitch", self.analyzedPitchCollectionClass)
        self.addOntologyObjectProperty("hasPitchList", self.pitchAnalysisClass)
        
        ''' part analysis '''
        self.addOntologyObjectProperty("hasPartAnalysis", self.workClass) 
        self.addOntologyObjectProperty("hasPartCollection", self.partAnalysisClass)
        self.addOntologyObjectProperty("hasPart", self.partCollectionClass) 
        
        ''' scale analysis '''
        self.addOntologyObjectProperty("hasScaleAnalysis", self.workClass) 
        self.addOntologyObjectProperty("hasScaleAnalysis", self.scaleAnalysisClass)  # scale analyses can be nested
        
        ''' cadence analysis '''
        self.addOntologyObjectProperty("hasCadenceAnalysis", self.workClass) 
        self.addOntologyObjectProperty("hasCadence", self.cadenceClass) 
        
        ''' root and progression analysis '''
        self.addOntologyObjectProperty("hasRootAndProgressionAnalysis", self.workClass)
        
        
        self.addOntologyObjectProperty("hasRootAnalysis", self.rootAndProgressionAnalysisClass)
        self.addOntologyObjectProperty("hasVectorAnalysis", self.rootAndProgressionAnalysisClass)
        
        self.addOntologyObjectProperty("hasRootCollection", self.rootAnalysisClass) 
        self.addOntologyObjectProperty("hasVectorCategory", self.vectorAnalysisClass) 
        
        self.addOntologyObjectProperty("hasVectorList", self.vectorAnalysisClass) 
        self.addOntologyObjectProperty("hasVectorSubCategory", self.vectorCategoryClass) 
        self.addOntologyObjectProperty("hasVectorList", self.vectorCategoryClass) 
        
        
        ''' real bass analysis '''
        self.addOntologyObjectProperty("hasRealBassAnalysis", self.workClass) 
        self.addOntologyObjectProperty("hasBassScaleDegreeAnalysis", self.realBassAnalysisClass) 
        self.addOntologyObjectProperty("hasBassScaleDegreeSuccessionAnalysis", self.realBassAnalysisClass)
        
        
        self.addOntologyObjectProperty("hasBassScaleDegrees", self.bassScaleDegreeAnalysisClass)
        self.addOntologyObjectProperty("hasBassScaleDegreeSuccessionCollections", self.bassScaleDegreeSuccessionAnalysisClass)  
        
        self.addOntologyObjectProperty("hasHarmonization", self.bassScaleDegreeCollectionClass) 
        self.addOntologyObjectProperty("hasHarmonizationSuccession", self.bassScaleDegreeSuccessionCollectionClass) 
        
        
        ''' modal analysis '''
        self.addOntologyObjectProperty("hasModalAnalysis", self.workClass)
        self.addOntologyObjectProperty("hasModalClassification", self.modalAnalysisClass)
        self.addOntologyObjectProperty("hasCadenceAnalysis", self.modalClassificationClass)
        self.addOntologyObjectProperty("hasPartCollection", self.modalClassificationClass)
        self.addOntologyObjectProperty("hasPart", self.partCollectionClass) 

        
    

    def generateId (self, length=8):
        ''' generate randomn id '''
        x = ''.join(random.choices(string.ascii_letters + string.digits, k=length)) 
        
        ''' make sure the id does not exist '''
        while self.individualNameExists(x):
            x = ''.join(random.choices(string.ascii_letters + string.digits, k=length)) 
        return x
    
    
    
    def getTriples(self, ontoInstance, recursion= True, tripleList=[]):
        
        
        
        tripleList = []
        for triple in self.onto.get_triples(ontoInstance.storid, None, None):
            unabbreviatedTriple = self.unabbreviateTriple(triple)
            if unabbreviatedTriple not in tripleList:  tripleList.append(unabbreviatedTriple)
            
            if recursion == True:
                if isinstance(triple[2], int) == False: continue 
                
                instanceObject = self.onto.search_one(iri = self.onto._unabbreviate(triple[2]))
                if instanceObject != None : 
                    for triple in  self.getTriples(instanceObject, True, tripleList):
                        if triple not in tripleList: tripleList.append(triple)
                         
            
        return tripleList 
    
    def unabbreviateTriple (self, triple):
        return [self.unabbreviateNode(triple[0]), self.unabbreviateNode(triple[1]),  self.unabbreviateNode(triple[2])]
            
    def unabbreviateNode (self, tripleNode):
        if isinstance(tripleNode, int): 
            element1 = self.onto._unabbreviate(tripleNode)
        else: 
            element1 = tripleNode
            
        if element1[0:4] == "http":  element1 = "<" + element1  + ">"
        
        return element1
            
    
    def getIndividualFromId (self, individualID):
        return self.onto.search_one(hasId = individualID)  
    
    
    def addOntologyClass (self, superClass, subClassName):
        with self.onto:
            newClass = types.new_class(subClassName, (superClass,))
        
        return newClass 
    
    def addOntologyDataProperty (self, propertyName, propertyRange):
        with self.onto:
            newProperty = types.new_class(propertyName, (DataProperty,))
            newProperty.range = propertyRange
        return newProperty
    
    
    def addOntologyObjectProperty (self, propertyName, propertyRange):
        with self.onto:
            newProperty = types.new_class(propertyName, (ObjectProperty,))
            newProperty.range = propertyRange
                
    
    ''' work, corpus '''
    def createWorkInstance (self, work, workURL = ""):
        workId = self.generateId()
        workClassInstance = self.workClass(workId)
        workClassInstance.hasComposer = [str(work.metadata.composer)] 
        workClassInstance.hasTitle = [str(work.metadata.title)] 
        workClassInstance.hasId = [workId]
        workClassInstance.hasURL = [workURL]
        workClassInstance.hasFileName = [str(work.filePath).split("/")[-1]] ## check this.
        workClassInstance.hasCopyright = work.metadata.copyright
        workClassInstance.hasDate = work.metadata.date
        workClassInstance.hasFileFormat =[work.fileFormat]
        #workClassInstance.hasFilePath = [work.filePath]
        workClassInstance.hasGenre = [work.filePath]
        workClassInstance.hasContext = [work.filePath]
        
        
        
        return workClassInstance
    
    
    ''' analytical methods '''         
    ''' pitch analysis '''
    

    
    
    
    ''' part analysis '''
    def createPartAnalysisInstance (self, work): 
        partAnalysisInstance = self.partAnalysisClass()
        partCollectionInstance = self.partCollectionClass()
        partAnalysisInstance.hasPartCollection.append(partCollectionInstance)
        partsAnal = ClefsAndKeysAnalysis(work)   
        partsClefsAndKeys = partsAnal.analyzedPartsDictionary
        partAnalysisInstance.versionInfo = partsAnal.__version__
        
        
        for analyzedPart in partsClefsAndKeys.values():
            analyzedPartInstance = self.partClass()
            analyzedPart.iri = analyzedPartInstance.iri
            analyzedPartInstance.hasClef.append(str(analyzedPart.clef))
            analyzedPartInstance.hasKey.append(str(analyzedPart.key))
            analyzedPartInstance.hasName.append(str(analyzedPart.partName))  
            analyzedPartInstance.hasAmbitusHigh.append(str(analyzedPart.ambitus[1]))
            analyzedPartInstance.hasAmbitusLow.append(str(analyzedPart.ambitus[0]))
            partCollectionInstance.hasPart.append(analyzedPartInstance)  
        return [partAnalysisInstance, partCollectionInstance, partsClefsAndKeys]     
    
    ''' scale analysis '''
    def createScaleAnalysisInstance(self, work):
        scaleAnal = ScaleAnalysis(work)
        bestScale = scaleAnal.getBestDiatonicScale() 
        scaleAnalysisInstance = self.scaleAnalysisClass()
        bestScaleNames = [scale.name for scale in bestScale]
        scaleAnalysisInstance.hasBestDiatonicScale = bestScaleNames
        scaleAnalysisInstance.hasPartCollection.append(self.partCollectionInstance)
        
        for analyzedPart in self.partsClefsAndKeys.values(): 
            analyzedPartInstance = self.onto.search_one(iri = analyzedPart.iri)         
            partScaleAnalysis = ScaleAnalysis(analyzedPart.part.part)
            partBestScale = partScaleAnalysis.getBestDiatonicScale()
            analyzedPartInstance.hasBestDiatonicScale.append(str(partBestScale))   
        return [scaleAnalysisInstance, scaleAnal, bestScale]   
    
    
    ''' cadence analysis '''
    def createCadenceAnalysis(self, work):
        cadenceAn= Cadences(work, barLines= True)
        cadenceAnalysisInstance = self.cadenceAnalysisClass() 
        for cadenceKey, cadence in cadenceAn.cadencePointDictionary.items():
            cadenceInstance = self.cadenceClass()
            cadenceInstance.hasId = [str(cadenceKey)]
            cadenceInstance.hasOffset = [float(cadence["cadenceOffset"])]
            cadenceInstance.hasCadenceType = [str(cadence["cadenceType"])]
            cadenceInstance.hasCadenceSubType = [str(cadence["cadenceSubType"])]
            cadenceInstance.hasFinalScaleDegree = [str(cadence['cadenceDegree'])]
            cadenceInstance.hasFinalChord = [str(cadence['cadenceChord'])]
            cadenceInstance.hasFinalRoot = [str(cadence['cadenceRoot'])]
            cadenceAnalysisInstance.hasCadence.append(cadenceInstance)
            
        return cadenceAnalysisInstance
    
            
    
    
    def getPitchCollSequence (self, pitchAnalysis):
        ''' given the pitch collection sequence id, this recreates the python object '''
        ''' get information relating to the sequence'''
        
        ''' get information relating to the pitch colls '''
        
        
        pitchCollSequence = PitchCollectionSequence()
        
        self.sparql = SPARQLWrapper("https://gdb.huma-num.fr:7200/repositories/IREMUS")
        self.sparql.setCredentials("iremus", "HhypDcv4c4hKjEm7JJ2FHzceGtLUyeLU")  
        sparqlQuery  = f"""
        PREFIX : <http://modality-tonality.huma-num.fr/fr/analysis.owl#>
        select ?analyzedPitchColl ?analyzedPitch ?hasAttack ?hasDuration ?hasId_analyzedPitch ?hasId_pitchColl ?hasRealBass ?hasName ?hasOffset ?hasPartName ?hasXMLId ?isSectionEnd ?hasBeatStrength where {{
        :{pitchAnalysis} :hasAnalyzedPitchCollectionSequence ?analyzedPitchCollSequence.
        ?analyzedPitchCollSequence :hasAnalyzedPitchCollection ?analyzedPitchColl.
        ?analyzedPitchColl :hasAnalyzedPitch ?analyzedPitch.
        ?analyzedPitchColl :hasEndTime ?hasEndTime.
        ?analyzedPitchColl :hasDuration ?hasDuration.
        ?analyzedPitchColl :hasId ?hasId_pitchColl.
        ?analyzedPitchColl :hasOffset ?hasOffset.
        ?analyzedPitchColl :isSectionEnd ?isSectionEnd.
        ?analyzedPitchColl :hasRealBass ?hasRealBass.
        ?analyzedPitchColl :hasBeatStrength ?hasBeatStrength.
        
        ?analyzedPitch :hasAttack ?hasAttack.
        ?analyzedPitch :hasId ?hasId_analyzedPitch.
        ?analyzedPitch :hasName ?hasName.
        ?analyzedPitch :hasPartName ?hasPartName.
        ?analyzedPitch :hasXMLId ?hasXMLId.
        }}"""
        
        self.sparql.setQuery(sparqlQuery)
        self.sparql.setReturnFormat(JSON)
        jsonIndividuals = self.sparql.query().convert()
        
        
        pitchCollIdList = []
        
        for element in jsonIndividuals["results"]["bindings"]:
            
            if element["analyzedPitchColl"]["value"] not in pitchCollIdList: 
                pitchCollIdList.append(element["analyzedPitchColl"]["value"])
                pitchColl = PitchCollection ()
                pitchColl.id = element["hasId_pitchColl"]["value"]
                pitchColl.isSectionEnd= bool(element["isSectionEnd"]["value"])
                pitchColl.duration= float (element["hasDuration"]["value"])
                pitchColl.offset= float (element["hasOffset"]["value"])
                pitchColl.bass = pitch.Pitch(element["hasRealBass"]["value"])
                pitchColl.beatStrength = float(element["hasBeatStrength"]["value"])
            
                ''' add it to pitch coll sequence '''
                pitchCollSequence.explainedPitchCollectionList.append(pitchColl)
            
            analyzedPitch = Pitch()
            analyzedPitch.attack = bool(element["hasAttack"]["value"])
            analyzedPitch.segmentQuarterLength = float(element["hasDuration"]["value"])
            analyzedPitch.id = element["hasId_analyzedPitch"]["value"]
            analyzedPitch.pitch = pitch.Pitch(element["hasName"]["value"])
            analyzedPitch.offset = float( element["hasOffset"]["value"])
            analyzedPitch.XMLId = element["hasXMLId"]["value"]
        
            ''' add it to pitch coll '''
      
            pitchCollSequence.addAnalyzedPitch(analyzedPitch)
            
        pitchCollSequence.updatePitchCollSequence()   
        return pitchCollSequence
        
    
    def createAnalyzedPitchCollectionSequenceInstance (self, pitchCollSequence):
        
        
        analyzedPitchCollectionSequenceInstance = self.analyzedPitchCollectionSequenceClass(self.generateId())
        
        
        #analyzedPitchCollectionSequenceInstance.hasId.append(pitchCollSequence.id)
        for pitchColl in pitchCollSequence.explainedPitchCollectionList:
            analyzedPitchCollectionSequenceInstance.hasAnalyzedPitchCollection.append(self.createAnalyzedPitchCollection(pitchColl))
        return analyzedPitchCollectionSequenceInstance
    
    
    def createAnalyzedPitchCollection(self, pitchColl):
        analyzedPitchCollectionInstance = self.analyzedPitchCollectionClass()
        analyzedPitchCollectionInstance.hasId.append(id (pitchColl))
        analyzedPitchCollectionInstance.hasDuration.append( pitchColl.duration)
        analyzedPitchCollectionInstance.hasEndTime.append( pitchColl.endTime)
        analyzedPitchCollectionInstance.hasOffset.append( pitchColl.offset)
        analyzedPitchCollectionInstance.isSectionEnd.append(pitchColl.isSectionEnd)
        analyzedPitchCollectionInstance.hasRealBass.append(str(pitchColl.bass))
        analyzedPitchCollectionInstance.hasBeatStrength.append(float(pitchColl.beatStrength))
        
        for analyzedPitch in pitchColl.analyzedPitchList:
            analyzedPitchCollectionInstance.hasAnalyzedPitch.append(self.createAnalyzedPitch(analyzedPitch))
        
        return analyzedPitchCollectionInstance
    
    
    def createAnalyzedPitch (self, analPitch):
        analyzedPitchInstance = self.analyzedPitchClass()
        analyzedPitchInstance.hasOffset.append(analPitch.offset)
        analyzedPitchInstance.hasXMLId.append(analPitch.id)
        analyzedPitchInstance.hasId.append(id(analPitch))
        analyzedPitchInstance.hasName.append(analPitch.pitch.nameWithOctave)
        analyzedPitchInstance.hasPartName.append(analPitch.part.partName)
        analyzedPitchInstance.hasAttack.append(analPitch.attack)
        analyzedPitchInstance.hasDuration.append(analPitch.segmentQuarterLength)
        
        return analyzedPitchInstance
        
    
    def updateAnalyzedPitchCollectionSequence (self, pitchCollSequence):
        for pitchColl in pitchCollSequence.explainedPitchCollectionList:
            self.updateAnalyzedPitchCollection(pitchColl)
    
    def updateAnalyzedPitchCollection (self, pitchColl):
        analyzedPitchCollectionInstance = self.getIndividualFromId (pitchColl.id)
        analyzedPitchCollectionInstance.hasRootPitch.append(str(pitchColl.rootPitch))
        analyzedPitchCollectionInstance.hasContinuoSigns.append(str(pitchColl.continuoSigns))
        analyzedPitchCollectionInstance.hasRootScaleDegree.append(str(pitchColl.rootDegree)) 
    
    ''' vector analysis '''
    def createVectorAnalysisInstance (self, vectorAnalysis): 
        ''' returns a vector category class '''
        vectorAnalysisInstance = self.vectorAnalysisClass()
        vectorCategoryInstance = self.createVectorSubCategoryInstances(vectorAnalysis.vectorPopulation)
        
        vectorAnalysisInstance.hasVectorCategory = [vectorCategoryInstance] 
        return vectorAnalysisInstance
                    
    def createVectorSubCategoryInstances (self, vectorCategory):
        vectorCategoryInstance = self.vectorCategoryClass()
        
        vectorCategoryInstance.hasName.append (str(vectorCategory.name))
        vectorCategoryInstance.hasOccurrence.append(vectorCategory.occurrence)
        
        for subCategory in vectorCategory.subCategories:
            subCategoryInstance = self.createVectorSubCategoryInstances (subCategory)
            vectorCategoryInstance.hasVectorSubCategory.append(subCategoryInstance)
            
        return vectorCategoryInstance
    
    
    ''' pitch analysis '''
    
    def createPitchAnalysisInstance (self, work):
        pitchAnId = self.generateId()
        pitchListId = self.generateId()
        
        ''' create pitchCollSequence and pitch analysis class '''
        pitchCollSequence = PitchCollectionSequence(work)
        pitchAnal = PitchAnalysis(pitchCollSequence.analyzedPitches, hierarchyList=["pitch.name"]) 
        
        ''' create corresponding ontology instances '''
        pitchCollSequenceInstance = self.createAnalyzedPitchCollectionSequenceInstance(pitchCollSequence) 
        pitchAnalysisInstance = self.pitchAnalysisClass(pitchAnId)
        
        
        ''' populate '''
        pitchAnalysisInstance.hasStrongestPitches.append(str(pitchAnal.getHighestScores(True)))
        pitchAnalysisInstance.hasAnalyzedPitchCollectionSequence.append(pitchCollSequenceInstance)         
        pitchAnalysisInstance.hasName.append(pitchAnal.attributeName)
        pitchAnalysisInstance.isCategory.append (pitchAnal.attributeValue)
        pitchAnalysisInstance.hasSubCollection = []
        pitchAnalysisInstance.hasOccurrence.append(len(pitchAnal.instanceList))
        
        pitchListInstance = self.pitchListClass(pitchListId)
        pitchAnalysisInstance.hasPitchList.append(pitchListInstance)
         
        for analPitch in pitchAnal.instanceList:
            analyzedPitchInstance =  self.getIndividualFromId(id(analPitch))
            pitchListInstance.hasAnalyzedPitch.append(analyzedPitchInstance) 
        #for subCollection in pitchAnal.subCollectionList:
        #    pitchAnalysisInstance.hasSubCollection.append(self.createPitchAnalysisInstance(subCollection))
            
        return pitchAnalysisInstance 
    
    
  
        
    
    
    
    
    
    def writeOntologyToFile (self, ontoName):
        self.onto.save(file = ontoName, format = "rdfxml")
        
    def getNamedIndividuals (self):
        individualsList = []
        self.sparql = SPARQLWrapper("https://gdb.huma-num.fr:7200/repositories/IREMUS")
        self.sparql.setCredentials("iremus", "HhypDcv4c4hKjEm7JJ2FHzceGtLUyeLU")  
        sparqlQuery  = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX : <http://modality-tonality.huma-num.fr/fr/analysis.owl#>
        select * where { 
        ?individual rdf:type owl:NamedIndividual .
        }"""
        
        self.sparql.setQuery(sparqlQuery)
        self.sparql.setReturnFormat(JSON)
        jsonIndividuals = self.sparql.query().convert()
        
        for element in jsonIndividuals["results"]["bindings"]:
            individualsList.append(element["individual"]["value"].split("#")[1])
        return individualsList
    
    def individualNameExists (self, individualName):
        self.sparql = SPARQLWrapper("https://gdb.huma-num.fr:7200/repositories/IREMUS")
        self.sparql.setCredentials("iremus", "HhypDcv4c4hKjEm7JJ2FHzceGtLUyeLU")  
        sparqlQuery  = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX : <http://modality-tonality.huma-num.fr/fr/analysis.owl#>
        select ?individual where {{ 
        ?individual rdf:type owl:NamedIndividual .
        FILTER (?individual = :{individualName})
        }}"""
        self.sparql.setQuery(sparqlQuery)
        self.sparql.setReturnFormat(JSON)
        jsonIndividuals = self.sparql.query().convert()
        
        for element in jsonIndividuals["results"]["bindings"]:
            return True
        return False
    
    
    def addInstanceToTripleStore(self, ontoInstance): 
        self.sparql = SPARQLWrapper("https://gdb.huma-num.fr:7200/repositories/IREMUS/statements")
        self.sparql.setCredentials("iremus", "HhypDcv4c4hKjEm7JJ2FHzceGtLUyeLU") 
        triples = self.getTriples(ontoInstance)
        triplesString = ""
         
        for triple in triples:
            triplesString = triplesString + f"{triple[0]} {triple[1]} {triple[2]}.\n"
        
        sparqlQuery = f"""INSERT {{ {triplesString} }}\n WHERE {{}}"""   
        self.sparql.setQuery(sparqlQuery)
        self.sparql.setMethod("POST")
        self.sparql.setReturnFormat(JSON)
        self.sparql.queryType = "INSERT"
        return self.sparql.query()
    
    def deleteInstanceFromTripleStore(self, instanceName): 
        self.sparql = SPARQLWrapper("https://gdb.huma-num.fr:7200/repositories/IREMUS/statements")
        self.sparql.setCredentials("iremus", "HhypDcv4c4hKjEm7JJ2FHzceGtLUyeLU") 
        
        sparqlQuery = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX : <http://modality-tonality.huma-num.fr/fr/analysis.owl#>
        DELETE WHERE {{ :{instanceName} ?p ?o }} 
        """   
        self.sparql.setQuery(sparqlQuery)
        self.sparql.setMethod("POST")
        self.sparql.setReturnFormat(JSON)
        self.sparql.queryType = "DELETE"
        return self.sparql.query()
    
    
    
    
    
    def getWorksFromTipleStore(self):
        self.sparql = SPARQLWrapper("https://gdb.huma-num.fr:7200/repositories/IREMUS")
        self.sparql.setCredentials("iremus", "HhypDcv4c4hKjEm7JJ2FHzceGtLUyeLU")  
        sparqlQuery  = """
        PREFIX : <http://modality-tonality.huma-num.fr/fr/analysis.owl#>
        PREFIX sesame: <http://www.openrdf.org/schema/sesame#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        select ?Work ?Composer ?Title ?Id{
        ?Work rdf:type :Work.
        ?Work :hasComposer ?Composer. 
        ?Work :hasTitle ?Title.
        ?Work :hasId ?Id.  
        }"""
        self.sparql.setQuery(sparqlQuery)
        self.sparql.setReturnFormat(JSON)
        jsonIndividuals = self.sparql.query().convert()
        
        return jsonIndividuals["results"]["bindings"]