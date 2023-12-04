'''
Created on Jul 27, 2020

@author: christophe
'''

from clefsAndKeys.clefsAndKeysAnal import ClefsAndKeysAnalysis
from pitchAnalysis.scales import ScaleAnalysis
from harmonicAnalysis.cadenceAnalysis import Cadences 
from modalAnalysis import modes
from pitchAnalysis.pitchAnal import PitchAnalysis 
import os
from music21 import converter
from modalAnalysis.modes import ModalEnsemble
import rootAnalysis
from vectors import VectorAnalysis
   
#from networkx.classes.function import degree 
from builtins import isinstance 
from datetime import datetime
#from django.contrib.messages.api import success
from owlready2 import get_ontology, Thing, ObjectProperty, DataProperty
import types



 


''' Ontology methods'''


def unabbreviateTriple (triple):
    return [unabbreviateNode(triple[0]), unabbreviateNode(triple[1]),  unabbreviateNode(triple[2])]
        
def unabbreviateNode (tripleNode):
    if isinstance(tripleNode, int): 
        element1 = onto._unabbreviate(tripleNode)
    else: 
        element1 = tripleNode
    
    return element1
        

def getIndividualFromId (individual):
    return onto.search_one(hasId = individual.id)  


def addOntologyClass (superClass, subClassName):
    with onto:
        newClass = types.new_class(subClassName, (superClass,))
    
    return newClass 

def addOntologyDataProperty (propertyName, propertyRange):
    with onto:
        newProperty = types.new_class(propertyName, (DataProperty,))
        newProperty.range = propertyRange
        
        
    return newProperty


def addOntologyObjectProperty (propertyName, propertyRange):
    with onto:
        newProperty = types.new_class(propertyName, (ObjectProperty,))
        newProperty.range = propertyRange
            

 
''' analytical methods ''' 
        
''' part analysis '''

def createPartAnalysisInstance (work): 
    partAnalysisInstance = partAnalysisClass()
    partCollectionInstance = partCollectionClass()
    partAnalysisInstance.hasPartCollection.append(partCollectionInstance)
    partsAnal = ClefsAndKeysAnalysis(work)   
    partsClefsAndKeys = partsAnal.analyzedPartsDictionary
    partAnalysisInstance.versionInfo = partsAnal.__version__
    
    
    for analyzedPart in partsClefsAndKeys.values():
        analyzedPartInstance = partClass()
        analyzedPart.iri = analyzedPartInstance.iri
        analyzedPartInstance.hasClef.append(str(analyzedPart.clef))
        analyzedPartInstance.hasKey.append(str(analyzedPart.key))
        analyzedPartInstance.hasName.append(str(analyzedPart.partName))  
        analyzedPartInstance.hasAmbitusHigh.append(str(analyzedPart.ambitus[1]))
        analyzedPartInstance.hasAmbitusLow.append(str(analyzedPart.ambitus[0]))
        partCollectionInstance.hasPart.append(analyzedPartInstance)  
    return [partAnalysisInstance, partCollectionInstance, partsClefsAndKeys]     

''' scale analysis '''
def createScaleAnalysisInstance(work):
    scaleAnal = ScaleAnalysis(work)
    bestScale = scaleAnal.getBestDiatonicScale() 
    scaleAnalysisInstance = scaleAnalysisClass()
    bestScaleNames = [scale.name for scale in bestScale]
    scaleAnalysisInstance.hasBestDiatonicScale = bestScaleNames
    scaleAnalysisInstance.hasPartCollection.append(partCollectionInstance)
    
    for analyzedPart in partsClefsAndKeys.values(): 
        analyzedPartInstance = onto.search_one(iri = analyzedPart.iri)         
        partScaleAnalysis = ScaleAnalysis(analyzedPart.part.part)
        partBestScale = partScaleAnalysis.getBestDiatonicScale()
        analyzedPartInstance.hasBestDiatonicScale.append(str(partBestScale))   
    return [scaleAnalysisInstance, scaleAnal, bestScale]   


''' cadence analysis '''
def createCadenceAnalysis(work):
    cadenceAn= Cadences(work, barLines= True)
    cadenceAnalysisInstance = cadenceAnalysisClass() 
    for cadenceKey, cadence in cadenceAn.cadencePointDictionary.items():
        cadenceInstance = cadenceClass()
        cadenceInstance.hasId = [str(cadenceKey)]
        cadenceInstance.hasOffset = [float(cadence["cadenceOffset"])]
        cadenceInstance.hasCadenceType = [str(cadence["cadenceType"])]
        cadenceInstance.hasCadenceSubType = [str(cadence["cadenceSubType"])]
        cadenceInstance.hasFinalScaleDegree = [str(cadence['cadenceDegree'])]
        cadenceInstance.hasFinalChord = [str(cadence['cadenceChord'])]
        cadenceInstance.hasFinalRoot = [str(cadence['cadenceRoot'])]
        cadenceAnalysisInstance.hasCadence.append(cadenceInstance)
        
    return cadenceAnalysisInstance

        
''' pitch collection sequence '''
def createAnalyzedPitchCollectionSequence (pitchCollSequence):
    analyzedPitchCollectionSequenceInstance = analyzedPitchCollectionSequenceClass()
    
    
    analyzedPitchCollectionSequenceInstance.hasId.append(pitchCollSequence.id)
    for pitchColl in pitchCollSequence.explainedPitchCollectionList:
        analyzedPitchCollectionSequenceInstance.hasAnalyzedPitchCollection.append(createAnalyzedPitchCollection(pitchColl))
    return analyzedPitchCollectionSequenceInstance


def createAnalyzedPitchCollection(pitchColl):
    analyzedPitchCollectionInstance = analyzedPitchCollectionClass()
    analyzedPitchCollectionInstance.hasId.append(id (pitchColl))
    analyzedPitchCollectionInstance.hasDuration.append( pitchColl.duration)
    analyzedPitchCollectionInstance.hasEndTime.append( pitchColl.endTime)
    analyzedPitchCollectionInstance.hasOffset.append( pitchColl.offset)
    analyzedPitchCollectionInstance.isSectionEnd.append(pitchColl.isSectionEnd)
    analyzedPitchCollectionInstance.hasRealBass.append(str(pitchColl.bass))
    
    for analyzedPitch in pitchColl.analyzedPitchList:
        analyzedPitchCollectionInstance.hasAnalyzedPitch.append(createAnalyzedPitch(analyzedPitch))
    
    return analyzedPitchCollectionInstance


def createAnalyzedPitch (analPitch):
    analyzedPitchInstance = analyzedPitchClass()
    analyzedPitchInstance.hasOffset.append(analPitch.offset)
    analyzedPitchInstance.hasId.append(analPitch.id)
    analyzedPitchInstance.hasName.append(analPitch.pitch.nameWithOctave)
    analyzedPitchInstance.hasPartName.append(analPitch.part.partName)
    analyzedPitchInstance.hasAttack.append(analPitch.attack)
    analyzedPitchInstance.hasDuration.append(analPitch.segmentQuarterLength)
    
    return analyzedPitchInstance
    

def updateAnalyzedPitchCollectionSequence (pitchCollSequence):
    for pitchColl in pitchCollSequence.explainedPitchCollectionList:
        updateAnalyzedPitchCollection(pitchColl)

def updateAnalyzedPitchCollection (pitchColl):
    analyzedPitchCollectionInstance = getIndividualFromId (pitchColl)
    analyzedPitchCollectionInstance.hasRootPitch.append(str(pitchColl.rootPitch))
    analyzedPitchCollectionInstance.hasContinuoSigns.append(str(pitchColl.continuoSigns))
    analyzedPitchCollectionInstance.hasRootScaleDegree.append(str(pitchColl.rootDegree)) 

''' vector analysis '''
def createVectorAnalysisInstance (vectorAnalysis): 
    ''' returns a vector category class '''
    vectorAnalysisInstance = vectorAnalysisClass()
    vectorCategoryInstance = createVectorSubCategoryInstances(vectorAnalysis.vectorPopulation)
    
    vectorAnalysisInstance.hasVectorCategory = [vectorCategoryInstance] 
    return vectorAnalysisInstance
                
def createVectorSubCategoryInstances (vectorCategory):
    vectorCategoryInstance = vectorCategoryClass()
    
    vectorCategoryInstance.hasName.append (str(vectorCategory.name))
    vectorCategoryInstance.hasOccurrence.append(vectorCategory.occurrence)
    
    for subCategory in vectorCategory.subCategories:
        subCategoryInstance = createVectorSubCategoryInstances (subCategory)
        vectorCategoryInstance.hasVectorSubCategory.append(subCategoryInstance)
        
    return vectorCategoryInstance


''' pitch analysis '''
def createPitchAnalysisInstance (pitchAnal):
    ''' returns a pitch analysis class ''' 
    
    pitchAnalysisInstance = pitchAnalysisClass()
    pitchAnalysisInstance.hasName.append(pitchAnal.attributeName)
    pitchAnalysisInstance.isCategory.append (pitchAnal.attributeValue)
    pitchAnalysisInstance.hasSubCollection = []
    pitchAnalysisInstance.hasOccurrence.append(len(pitchAnal.instanceList))
    pitchListInstance = pitchListClass()
    pitchAnalysisInstance.hasPitchList.append(pitchListInstance)
     
    for analPitch in pitchAnal.instanceList:
        analyzedPitchInstance =  getIndividualFromId(analPitch)
        pitchListInstance.hasAnalyzedPitch.append(analyzedPitchInstance) 
    for subCollection in pitchAnal.subCollectionList:
        pitchAnalysisInstance.hasSubCollection.append(createPitchAnalysisInstance(subCollection))
        
    return pitchAnalysisInstance 



if __name__ == '__main__':
    pass

now = datetime.now()
ontoIRI = "http://modality-tonality.huma-num.fr/ontology/analysis"
onto = get_ontology(ontoIRI)

 


dt_string = now.strftime("%d%m%Y_%H%M")
''' folder '''
directroyString = '/Users/christophe/Dropbox/Praetorius/Polyhymnia/Source/ontologyTest/'
#worksWithRootPath = "/Users/christophe/Dropbox/Praetorius/Polyhymnia/Source/ontologyTesWithRoot/"
workBookPath  = '/Users/christophe/Dropbox/Praetorius/Polyhymnia/results/' + dt_string + '.xlsx'
ontologyName = '/Users/christophe/Dropbox/Praetorius/Polyhymnia/results/' + dt_string + '.rdf'

#directroyString = '/Users/christophe/Documents/Praetorius/Musae Sioniae/xml/'
#worksWithRootPath = "/Users/christophe/Documents/Praetorius/Musae Sioniae/roots/"
#workBookPath  = '/Users/christophe/Documents/Praetorius/Musae Sioniae/' + dt_string + '.xlsx'
#ontologyName = '/Users/christophe/Documents/Praetorius/Musae Sioniae/' + dt_string + '.rdf'

''' add classes corpus, work'''
corpusAnalysisClass = addOntologyClass(Thing, "CorpusAnalysis")
workClass = addOntologyClass(corpusAnalysisClass, "Work")

''' part analysis '''
partAnalysisClass = addOntologyClass(workClass, "PartAnalysis")
partCollectionClass = addOntologyClass(partAnalysisClass, "PartCollection")
partClass = addOntologyClass(partCollectionClass, "Part")

''' scale analysis '''
scaleAnalysisClass = addOntologyClass(workClass, "ScaleAnalysis")

''' cadences analysis '''
cadenceAnalysisClass = addOntologyClass(workClass, "CadenceAnalysis")
cadenceClass = addOntologyClass(cadenceAnalysisClass, "Cadence")

''' pitch analysis '''

pitchAnalysisClass = addOntologyClass(workClass, "PitchAnalysis") 
analyzedPitchCollectionSequenceClass = addOntologyClass(pitchAnalysisClass, "AnalyzedPitchCollectionSequence")
analyzedPitchCollectionClass =  addOntologyClass(analyzedPitchCollectionSequenceClass, "AnalyzedPitchCollection")
analyzedPitchClass = addOntologyClass(analyzedPitchCollectionClass, "AnalyzedPitch")
pitchListClass = addOntologyClass(pitchAnalysisClass, "PitchList")


''' root analysis ''' 
rootAndProgressionAnalysisClass  = addOntologyClass(workClass, "RootsAndProgressionsAnalysis") 
rootAnalysisClass  = addOntologyClass(rootAndProgressionAnalysisClass, "RootAnalysis") 
rootCollectionClass  = addOntologyClass(rootAnalysisClass, "RootCollection") 
chordInversionClass = addOntologyClass(rootCollectionClass, "ChordInversion") 

vectorAnalysisClass = addOntologyClass(rootAndProgressionAnalysisClass, "VectorAnalysis") 
vectorCategoryClass = addOntologyClass(vectorAnalysisClass, "VectorCategory") 


''' real bass analysis '''
realBassAnalysisClass = addOntologyClass(workClass, "RealBassAnalysis")
bassScaleDegreeAnalysisClass = addOntologyClass(realBassAnalysisClass, "BassScaleDegreeAnalysis")
bassScaleDegreeSuccessionAnalysisClass = addOntologyClass(realBassAnalysisClass, "BassScaleDegreeSuccessionAnalysis")

bassScaleDegreeCollectionClass = addOntologyClass (bassScaleDegreeAnalysisClass, "BassScaleDegreeCollection") 
harmonizationClass = addOntologyClass(bassScaleDegreeCollectionClass, "Harmonization")
bassScaleDegreeSuccessionCollectionClass = addOntologyClass(bassScaleDegreeSuccessionAnalysisClass, "BassScaleDegreeSuccessionCollection")
harmonizationSuccessionClass = addOntologyClass(bassScaleDegreeSuccessionCollectionClass, "HarmonizationSuccession")


''' modal - tonal analysis '''
modalAnalysisClass = addOntologyClass(workClass, "ModalAnalysis")
modalClassificationClass = addOntologyClass(modalAnalysisClass, "ModalClassification")


#rootsClass = addOntologyClass (workClass, "Roots")
#inversionsClass = addOntologyClass (rootsClass, "Inversions")



''' add data properties '''
'''str '''
addOntologyDataProperty("hasId", [str]) # metadata
addOntologyDataProperty("hasFileName", [str]) # metadata
addOntologyDataProperty("hasURL", [str]) # metadata
addOntologyDataProperty("hasTitle", [str]) # metadata
addOntologyDataProperty("hasComposer", [str]) # metadata
addOntologyDataProperty("hasWork", [str])
addOntologyDataProperty("hasBestDiatonicScale", [str]) # scale analysis 


addOntologyDataProperty("hasName", [str])
addOntologyDataProperty("hasAlteration", [str])
addOntologyDataProperty("hasHarmonization", [str])

''' pitch analysis '''
addOntologyDataProperty("hasStrongestPitches", [str])
addOntologyDataProperty("isCategory", [str])
addOntologyDataProperty("hasRootPitch", [str])
addOntologyDataProperty("hasPartName", [str])
addOntologyDataProperty("hasAttack", [str])
addOntologyDataProperty("isSectionEnd", [str])
addOntologyDataProperty("hasRealBass", [str])
addOntologyDataProperty("hasContinuoSigns", [str])
addOntologyDataProperty("hasEndTime", [float])
addOntologyDataProperty("hasBeatStrength", [float])

''' cadence analysis'''
addOntologyDataProperty("hasFinalScaleDegree", [str])
addOntologyDataProperty("hasFinalChord", [str])
addOntologyDataProperty("hasFinalRoot", [str])
addOntologyDataProperty("hasCadenceType", [str]) # 
addOntologyDataProperty("hasCadenceSubType", [str]) # 

''' root analysis '''
addOntologyDataProperty("hasRoot", [str])
addOntologyDataProperty("hasRootScaleDegree", [str])


''' real bass analysis '''
addOntologyDataProperty("hasFirstScaleDegreeName", [str])
addOntologyDataProperty("hasSecondScaleDegreeName", [str])
addOntologyDataProperty("hasFirstHarmonizationName", [str])
addOntologyDataProperty("hasSecondHarmonizationName", [str])

''' modal analysis '''
addOntologyDataProperty("hasFinalis", [str])
addOntologyDataProperty("hasThird", [str])
addOntologyDataProperty("hasModalSystemName", [str])
addOntologyDataProperty("hasOctaveDivision", [str])
addOntologyDataProperty("hasKey", [str]) # 
addOntologyDataProperty("hasClef", [str]) # 
addOntologyDataProperty("hasAmbitusLow", [str])
addOntologyDataProperty("hasAmbitusHigh", [str])
#addOntologyDataProperty("hasModalAttribution", [str])
addOntologyDataProperty("hasStrongestPitches", [str])


''' int '''
addOntologyDataProperty("hasMeasureNumber", [int])
addOntologyDataProperty("hasOccurrence", [int])
addOntologyDataProperty("hasPartNumber", [int])


''' float '''
addOntologyDataProperty("hasOffset", [float])
addOntologyDataProperty("hasDuration", [float])



''' add object properties '''

''' pitch analysis '''
addOntologyObjectProperty("hasPitchAnalysis", workClass) 
addOntologyObjectProperty("hasSubCollection", pitchAnalysisClass) # pitch analyses can be nested

addOntologyObjectProperty("hasAnalyzedPitchCollectionSequence", pitchAnalysisClass)
addOntologyObjectProperty("hasAnalyzedPitchCollection", analyzedPitchCollectionSequenceClass)
addOntologyObjectProperty("hasAnalyzedPitch", analyzedPitchCollectionClass)
addOntologyObjectProperty("hasPitchList", pitchAnalysisClass)





''' part analysis '''
addOntologyObjectProperty("hasPartAnalysis", workClass) 
addOntologyObjectProperty("hasPartCollection", partAnalysisClass)
addOntologyObjectProperty("hasPart", partCollectionClass) 


''' scale analysis '''
addOntologyObjectProperty("hasScaleAnalysis", workClass) 
addOntologyObjectProperty("hasScaleAnalysis", scaleAnalysisClass)  # scale analyses can be nested

''' cadence analysis '''
addOntologyObjectProperty("hasCadenceAnalysis", workClass) 
addOntologyObjectProperty("hasCadence", cadenceClass) 

''' root and progression analysis '''
addOntologyObjectProperty("hasRootAndProgressionAnalysis", workClass)


addOntologyObjectProperty("hasRootAnalysis", rootAndProgressionAnalysisClass)
addOntologyObjectProperty("hasVectorAnalysis", rootAndProgressionAnalysisClass)

addOntologyObjectProperty("hasRootCollection", rootAnalysisClass) 
addOntologyObjectProperty("hasVectorCategory", vectorAnalysisClass) 

addOntologyObjectProperty("hasVectorList", vectorAnalysisClass) 
addOntologyObjectProperty("hasVectorSubCategory", vectorCategoryClass) 
addOntologyObjectProperty("hasVectorList", vectorCategoryClass) 


''' real bass analysis '''
addOntologyObjectProperty("hasRealBassAnalysis", workClass) 
addOntologyObjectProperty("hasBassScaleDegreeAnalysis", realBassAnalysisClass) 
addOntologyObjectProperty("hasBassScaleDegreeSuccessionAnalysis", realBassAnalysisClass)


addOntologyObjectProperty("hasBassScaleDegrees", bassScaleDegreeAnalysisClass)
addOntologyObjectProperty("hasBassScaleDegreeSuccessionCollections", bassScaleDegreeSuccessionAnalysisClass)  

addOntologyObjectProperty("hasHarmonization", bassScaleDegreeCollectionClass) 
addOntologyObjectProperty("hasHarmonizationSuccession", bassScaleDegreeSuccessionCollectionClass) 


''' modal analysis '''
addOntologyObjectProperty("hasModalAnalysis", workClass)
addOntologyObjectProperty("hasModalClassification", modalAnalysisClass)
addOntologyObjectProperty("hasCadenceAnalysis", modalClassificationClass)
addOntologyObjectProperty("hasPartCollection", modalClassificationClass)
addOntologyObjectProperty("hasPart", partCollectionClass) 






onto.save(file = ontologyName, format = "rdfxml")

directory = os.fsencode(directroyString)
modalEnsembleList = [] #  every item corresponds to one work
modalPartNameList = [] # every item corresponds to one part name




''' get data '''

dirList = os.listdir(directory)
analysisCounter = 1

for file in dirList:
    
    
    filename = os.fsdecode(file)
    if filename.endswith(".mei")== False: continue
    
    #if filename != "011.musicxml": continue

    print ("Analyzing file : " + str(filename) + " " + str(analysisCounter)) 
    
    
    work = converter.parse('%s%s' %(directroyString, filename), forceSource= True)
    
    md = work.metadata.all()
    
    modalEnsembleInstance = ModalEnsemble()
    modalEnsembleInstance.work = work
    
   
    
    ''' metadata '''
    workClassInstance = workClass()
    workClassInstance.hasFileName = [str(filename)]
    workClassInstance.hasComposer = [str(work.metadata.composer)] 
    workClassInstance.hasTitle = [str(work.metadata.title)] 
    workClassInstance.hasMeasureNumber = [int(work.finalBarline[0].measureNumber)]
    
    ''' part analysis '''
    partAnalInstList = createPartAnalysisInstance(work)  
    partCollectionInstance = partAnalInstList[1]
    partsClefsAndKeys = partAnalInstList[2]
    workClassInstance.hasPartAnalysis.append(partAnalInstList[0])


    ''' scale Analysis '''
    scaleAnalysisRes = createScaleAnalysisInstance(work)
    scaleAnalysisInstance = scaleAnalysisRes [0]
    scaleAnal = scaleAnalysisRes [1]
    bestScale = scaleAnalysisRes [2]
    workClassInstance.hasScaleAnalysis.append(scaleAnalysisInstance)
    
    
    ''' pitch Analysis '''
    analysedPitches = scaleAnal.workAnalyzedPitches  
    pitchAnal = PitchAnalysis(analysedPitches, hierarchyList=["pitch.name"]) 
    pitchCollSequenceInstance = createAnalyzedPitchCollectionSequence(scaleAnal.pitchCollectionSequence) 
    pitchAnalysisInstanceWork = createPitchAnalysisInstance(pitchAnal)
    pitchAnalysisInstanceWork.hasStrongestPitches.append(str(pitchAnal.getHighestScores(True)))
    pitchAnalysisInstanceWork.hasAnalyzedPitchCollectionSequence.append(pitchCollSequenceInstance) 
    workClassInstance.hasPitchAnalysis.append(pitchAnalysisInstanceWork)
    
    for analyzedPart in partsClefsAndKeys.values():
        analyzedPartInstance = onto.search_one(iri = analyzedPart.iri)  
        pitchAnal = PitchAnalysis(analysedPitches, hierarchyList=["pitch.name"], filterList=[["part.partName", analyzedPart.partName]])    
        pitchAnalysisInstance = createPitchAnalysisInstance(pitchAnal)
        pitchAnalysisInstance.hasStrongestPitches.append(str(pitchAnal.getHighestScores(True)))
        analyzedPartInstance.hasPitchAnalysis.append(pitchAnalysisInstance)
        

    ''' cadence analysis '''
    cadenceAnalysisInstance = createCadenceAnalysis(work)
    workClassInstance.hasCadenceAnalysis.append(cadenceAnalysisInstance)
        
     
    
    ''' root and progression analysis ''' 
    #scaleAnal.pitchCollectionSequences.setRootsFromStream(rootStream)  
    
    rootAnal = rootAnalysis.RootAnalysis(scaleAnal.pitchCollectionSequence)
    referencePitch = rootAnal.pitchCollectionSequence.explainedPitchCollectionList[-1].rootPitch.name # careful, careful !!!
    rootAnal.populateRootDictionary() 
    rootAnal.setRootDegreeFromReferencePitch(bestScale[0], referencePitch) # this may lead to inconsistencies between cadence analysis and root analysis
    rootAndProgressionAnalysisInstance = rootAndProgressionAnalysisClass() 
    workClassInstance.hasRootAndProgressionAnalysis = [rootAndProgressionAnalysisInstance]
    
    rootAnalysisInstance = rootAnalysisClass()    
    for rootCollectionKey, rootCollection in rootAnal.rootDictionary.items():
        rootCollectionInstance = rootCollectionClass()
        rootCollectionInstance.hasOccurrence = [rootCollection['occurrence']] 
        rootCollectionInstance.hasDuration = [rootCollection['duration']] 
        rootCollectionInstance.hasRoot = [rootCollection['root']] ### this should be deduced from final cadence ?
        rootCollectionInstance.hasRootScaleDegree = [rootCollection['degree']] 
        
        # inversions
        rootAnalysisInstance.hasRootCollection.append(rootCollectionInstance)
    rootAndProgressionAnalysisInstance.hasRootAnalysis.append(rootAnalysisInstance) 
   
    
    ''' vector analysis '''
    vectorAnal = VectorAnalysis(scaleAnal.pitchCollectionSequence)
    vectorAnalysisInstance = createVectorAnalysisInstance(vectorAnal)
    rootAndProgressionAnalysisInstance.hasVectorAnalysis.append(vectorAnalysisInstance)

 
    ''' real bass analysis   '''
    realBassAnalysisInstance = realBassAnalysisClass()
    workClassInstance.hasRealBassAnalysis.append(realBassAnalysisInstance) 

    rootAnal.pitchCollectionSequence.setRealbassScaleDegreeFromReferencePitch(bestScale[0], referencePitch)
    rootAnal.pitchCollectionSequence.setRealBassDiatonicDegree(bestScale[0])
    continuoDict = rootAnal.pitchCollectionSequence.getDiatonicDegreesDictionary() 
    rootAnal.pitchCollectionSequence.analyzeRealBassMovements() 
    successionDict = rootAnal.pitchCollectionSequence.continuoSuccessionDict

    bassScaleDegreeAnalysisInstance = bassScaleDegreeAnalysisClass()
    realBassAnalysisInstance.hasBassScaleDegreeAnalysis.append(bassScaleDegreeAnalysisInstance)
    for realBassKey, realBassEntry in continuoDict.items():
        bassScaleDegreeInstance = bassScaleDegreeCollectionClass()
        bassScaleDegreeInstance.hasName = [realBassEntry["name"]]
        bassScaleDegreeInstance.hasDuration = [realBassEntry["duration"]]
        bassScaleDegreeInstance.hasHarmonization = []
        
        for harmonizationKey, harmonization in realBassEntry["harmonizations"].items():
            harmonizationInstance = harmonizationClass()
            harmonizationInstance.hasName = [harmonization["name"]]
            harmonizationInstance.hasDuration = [harmonization["duration"]]
            
            bassScaleDegreeInstance.hasHarmonization.append(harmonizationInstance) 
        bassScaleDegreeAnalysisInstance.hasBassScaleDegrees.append(bassScaleDegreeInstance)
    
     
    
    bassScaleDegreeSuccessionAnalysisInstance = bassScaleDegreeSuccessionAnalysisClass()
    realBassAnalysisInstance.hasBassScaleDegreeSuccessionAnalysis.append(bassScaleDegreeSuccessionAnalysisInstance)
    
    for successionKey, successionEntry in successionDict.items():
        bassScaleDegreeSuccessionCollectionInstance = bassScaleDegreeSuccessionCollectionClass()
        bassScaleDegreeSuccessionCollectionInstance.hasName = [successionEntry["name"]]
        bassScaleDegreeSuccessionCollectionInstance.hasFirstScaleDegreeName = [successionEntry["firstScaleDegreeName"]]
        bassScaleDegreeSuccessionCollectionInstance.hasSecondScaleDegreeName = [successionEntry["secondScaleDegreeName"]]
        
        for harmonizationKey, harmonizationsEntry in successionEntry["harmonizations"].items() :
            harmonizationSuccessionInstance = harmonizationSuccessionClass()
            harmonizationSuccessionInstance.hasName = [harmonizationsEntry["name"]]
            harmonizationSuccessionInstance.hasFirstHarmonizationName = [harmonizationsEntry["firstHarmonizationName"]]
            harmonizationSuccessionInstance.hasSecondHarmonizationName = [harmonizationsEntry["secondHarmonizationName"]]
            bassScaleDegreeSuccessionCollectionInstance.hasHarmonizationSuccession.append(harmonizationSuccessionInstance)
        bassScaleDegreeSuccessionAnalysisInstance.hasBassScaleDegreeSuccessionCollections.append(bassScaleDegreeSuccessionCollectionInstance)   
 
    #modalEnsembleInstance.motionDictionary = rootAnal.pitchCollectionSequence.motionDictionary
    

        
    
    ''' modal analysis '''
    modalAnalysisInstance = modalAnalysisClass()
    workClassInstance.hasModalAnalysis.append(modalAnalysisInstance)
    modalAnal = modes.ModalAnalysis()
    for scale in bestScale:
        modalClassificationInstance = modalClassificationClass()
        modalClassificationInstance.hasModalSystemName.append("Glarean")
        modalClassificationInstance.hasName.append(modalAnal.getModeFromFinalisAndDiatonicSystem(referencePitch, scale))
        modalClassificationInstance.hasFinalis.append(referencePitch)
        modalClassificationInstance.hasBestDiatonicScale.append(str(scale))
        modalClassificationInstance.hasThird.append(modalAnal.getmajorMinorThird()) 
        modalClassificationInstance.hasCadenceAnalysis.append(cadenceAnalysisInstance)        
        #modalClassificationInstance.hasOctaveDivision.append("")
        modalAnalysisInstance.hasModalClassification.append(modalClassificationInstance)
        modalClassificationInstance.hasPartCollection.append(partCollectionInstance)
        for analyzedPart in partsClefsAndKeys.values():
            analyzedPartInstance = onto.search_one(iri = analyzedPart.iri)          
            analyzedPartInstance.hasOctaveDivision.append(modalAnal.getOctaveDivision(analyzedPart, referencePitch))  
            analyzedPartInstance.hasFinalis.append(analyzedPart.finalis.nameWithOctave) 
 

           
    
    ''' update pitch collection sequence '''
    updateAnalyzedPitchCollectionSequence(scaleAnal.pitchCollectionSequence)
    
    
    
    #for triple in onto.get_triples(scaleAnalysisInstance.storid, None, None):
    #    print (unabbreviateTriple(triple))

    
    


onto.save(file = ontologyName, format = "rdfxml")

  

 

    

