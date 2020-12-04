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

from openpyxl import Workbook   

import pandas as pd
#from networkx.classes.function import degree
import copy
from builtins import isinstance
from bs4 import element
from openpyxl.utils.datetime import to_excel
from datetime import datetime
#from django.contrib.messages.api import success
from owlready2 import get_ontology, Thing, ObjectProperty, DataProperty
import types



 


'''Create nested classes of modal-tonal markers'''

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
            

def getListFromDictionary(dataDictionary, dictionaryKey):
    
    if dictionaryKey not in dataDictionary:
        dataDictionary[dictionaryKey] = []

    
    return dataDictionary[dictionaryKey]
    

def getTotalFromList (dicList):
    ''' sum of all elements in list if list only contains numbers '''
    total = 0
    for element in dicList:
        if  isinstance (element, float) or isinstance(element, int):
            total = total + element
        else: return ""
        
    return total
            
        
    


if __name__ == '__main__':
    pass

now = datetime.now()
onto = get_ontology("http://modality-tonality.huma-num.fr/fr/analysis/praetorius1619.owl")

 


dt_string = now.strftime("%d%m%Y_%H%M")
''' folder '''
directroyString = '/Users/christophe/Dropbox/Praetorius/Polyhymnia/Source/ontologyTest/'
worksWithRootPath = "/Users/christophe/Dropbox/Praetorius/Polyhymnia/Source/ontologyTesWithRoot/"
workBookPath  = '/Users/christophe/Dropbox/Praetorius/Polyhymnia/results/' + dt_string + '.xlsx'
ontologyName = '/Users/christophe/Dropbox/Praetorius/Polyhymnia/results/' + dt_string + '.rdf'

#directroyString = '/Users/christophe/Documents/Praetorius/Musae Sioniae/xml/'
#worksWithRootPath = "/Users/christophe/Documents/Praetorius/Musae Sioniae/roots/"
#workBookPath  = '/Users/christophe/Documents/Praetorius/Musae Sioniae/' + dt_string + '.xlsx'
#ontologyName = '/Users/christophe/Documents/Praetorius/Musae Sioniae/' + dt_string + '.rdf'


''' add classes corpus, work'''
corpusAnalysisClass = addOntologyClass(Thing, "CoprusAnalysis")
workClass = addOntologyClass(corpusAnalysisClass, "Work")
modalPartClass = addOntologyClass(workClass, "ModalParts") 
vectorClass = addOntologyClass(workClass, "Vectors") 
rootsClass = addOntologyClass (workClass, "Roots")
inversionsClass = addOntologyClass (rootsClass, "Inversions")
bassScaleDegreeClass = addOntologyClass (workClass, "BassScaleDegree") 



''' add data properties '''
addOntologyDataProperty("hasFileName", [str])
addOntologyDataProperty("hasTitle", [str])
addOntologyDataProperty("hasComposer", [str])
addOntologyDataProperty("hasMeasureNumber", [int])
addOntologyDataProperty("hasWork", [str])

addOntologyDataProperty("hasOctaveDivision", [str])
addOntologyDataProperty("hasKey", [str])
addOntologyDataProperty("hasAmbitus", [str])
addOntologyDataProperty("hasFinalis", [str])
addOntologyDataProperty("hasStrongestPitches", [str])
addOntologyDataProperty("hasName", [str])
addOntologyDataProperty("hasOccurrence", [int])
addOntologyDataProperty("hasDuration", [float])
addOntologyDataProperty("hasAlteration", [str])
addOntologyDataProperty("hasHarmonization", [str])



''' add object properties '''
addOntologyObjectProperty("hasModalParts", modalPartClass) 
addOntologyObjectProperty("hasVectors", vectorClass) 
addOntologyObjectProperty("hasRoots", rootsClass) 
addOntologyObjectProperty("hasInversions", inversionsClass) 
addOntologyObjectProperty("hasBassScaleDegrees", bassScaleDegreeClass) 


#onto.save(file = ontologyName, format = "rdfxml")

directory = os.fsencode(directroyString)
modalEnsembleList = [] #  every item corresponds to one work
modalPartNameList = [] # every item corresponds to one part name




''' get data '''

dirList = os.listdir(directory)
analysisCounter = 1

for file in dirList:
    
    
    filename = os.fsdecode(file)
    if filename.endswith(".musicxml")== False: continue
    
    #if filename != "011.musicxml": continue

    print ("Analyzing file : " + str(filename) + " " + str(analysisCounter)) 
    
    
    work = converter.parse('%s%s' %(directroyString, filename))
    
    md = work.metadata.all()
    
    modalEnsembleInstance = ModalEnsemble()
    
   
    
    
    ''' check if file exists in directory '''
    try:
        workWithRoot  = converter.parse('%s%s' %(worksWithRootPath, filename))
        
    except FileNotFoundError:
            # doesn't exist
        print ("No root analysis file. Skipping this file ....")  
        continue      
    else:   
        rootStream = None
        for part in workWithRoot.parts:
            if part.partName == "Root":
                rootStream = part
                break
            
        if rootStream == None: 
            print ("No roots. Skipping this file ....")  
            continue  
        
    if work.duration.quarterLength != workWithRoot.duration.quarterLength:   
        print ("Works do not match... Skipping this file ....")  
    
    
 
    
 
    
   
    
    onto.save(file = ontologyName, format = "rdfxml")
    
    ''' general information '''
    'title, composer'
    modalEnsembleInstance.fileName = filename
    modalEnsembleInstance.title = work.metadata.title
    modalEnsembleInstance.composer = work.metadata.composer
    modalEnsembleInstance.measureNumber = work.finalBarline[0].measureNumber
    modalEnsembleInstance.work = work
    
    ''' scale Analysis '''
    scaleAnal = ScaleAnalysis(work)
    bestScale = scaleAnal.getBestDiatonicScale()
    bestScaleNames = [scale.name for scale in bestScale]
    bestScaleNames.sort()
    analysedPitches = scaleAnal.workAnalyzedPitches
    modalEnsembleInstance.bestScales = bestScaleNames
    modalEnsembleInstance.scaleAnal = scaleAnal
    
    
    '''parts, clefs and keys '''
    modalEnsembleInstance.modalParts = ClefsAndKeysAnalysis(work).analyzedPartsDictionary
    keyList = []
    ''' add modal part key to modal part list '''
    for modalPart in modalEnsembleInstance.modalParts:
        if modalEnsembleInstance.modalParts[modalPart].partName not in modalPartNameList: modalPartNameList.append(modalEnsembleInstance.modalParts[modalPart].partName)
    

    ''' cadence Analysis '''
    cadenceAn= Cadences(work, modalEnsembleInstance.modalParts, barLines= True)
    modalEnsembleInstance.setCadences(cadenceAn)
    
    
    ''' roots and vectors '''
    ''' set roots '''  
     
    scaleAnal.pitchCollectionSequences.setRootsFromStream(rootStream)  
    
    ''' analyze roots and inversions '''
    rootAnal = rootAnalysis.RootAnalysis(scaleAnal.pitchCollectionSequences)
    rootAnal.populateRootDictionary() 
    
    
    ''' reset final chord and chord root   '''
    modalEnsembleInstance.finalChordRoot = rootAnal.pitchCollectionSequence.explainedPitchCollectionList[-1].rootPitch.name
    modalEnsembleInstance.finalChord = [rootAnal.pitchCollectionSequence.explainedPitchCollectionList[-1].chord, None]
    rootAnal.pitchCollectionSequence.setRealbassScaleDegreeFromReferencePitch(bestScale[0], modalEnsembleInstance.finalChordRoot)
    rootAnal.pitchCollectionSequence.setRealBassDiatonicDegree(bestScale[0])
    
  
    continuoDict = rootAnal.pitchCollectionSequence.getContinuoDictionary() 
    rootAnal.pitchCollectionSequence.analyzeRealBassMovements() 
    
    modalEnsembleInstance.diatonicDegreesDictionary = rootAnal.pitchCollectionSequence.getDiatonicDegreesDictionary()
    modalEnsembleInstance.continuoSuccessionDictionary  = rootAnal.pitchCollectionSequence.continuoSuccessionDict
    modalEnsembleInstance.motionDictionary = rootAnal.pitchCollectionSequence.motionDictionary
    
    rootAnal.setRootDegreeFromReferencePitch(bestScale[0], modalEnsembleInstance.finalChordRoot) 

    ''' analyze vectors '''
    vectorAnal = VectorAnalysis(scaleAnal.pitchCollectionSequences)
    
    modalEnsembleInstance.continuoDictionary = continuoDict
 
    modalEnsembleInstance.rootAnalysis = rootAnal
    modalEnsembleInstance.vectorAnalysis = vectorAnal
  
    
    ''' pitch Analysis '''
    for modalPart in modalEnsembleInstance.modalParts.values():
        pitchAnal = PitchAnalysis(analysedPitches, hierarchyList=["pitch.nameWithOctave"], filterList=[["part.name", modalPart.partName]])    
        modalPart.strongestPitches = pitchAnal.getHighestScores(True)
        keyList.append(modalPart.key)
    modalEnsembleInstance.keys = keyList
    
    ''' identify mode '''
    modalAnal = modes.ModalAnalysis()
    modeList = []
    majorMinorThirdList = []
    
    if modalEnsembleInstance.finalChordRoot != None:
    
        for scale in bestScale:
            modeList.append (modalAnal.getModeFromFinalisAndDiatonicSystem(modalEnsembleInstance.finalChordRoot, scale))
            majorMinorThird = modalAnal.getmajorMinorThird()
        
            if majorMinorThird not in majorMinorThirdList: majorMinorThirdList.append(majorMinorThird)
        
        modeList.sort()
        majorMinorThirdList.sort()
        
        modalEnsembleInstance.modeName = modeList
        modalEnsembleInstance.majorMinorThird = majorMinorThirdList 
        for modalPart in modalEnsembleInstance.modalParts.values():
            modalPart.octaveDivision = modalAnal.getOctaveDivision(modalPart, modalEnsembleInstance.finalChordRoot) 
    
    modalEnsembleList.append(modalEnsembleInstance)
    analysisCounter = analysisCounter + 1
        
         
''' Loop over modalEnsembleList ''' 
    
print ("Creating dictionary...")
    
#  Create json file

''' create root list '''
rootList = []
degreeList = []
diatonicDegreesList = []
raisedDegreesList = [] ## used for "diesis-rule" 
continuoList = []
continuoAList = []
continuoBList = []

for modalEnsembleCounter, modalEns in enumerate (modalEnsembleList): 
    
    for continuoSuccessionCounter, continuoSuccessionKey in modalEns.continuoSuccessionDictionary.items():
        continuoSuccession = continuoSuccessionCounter.split("=>")
        continuoNotationA = continuoSuccession[0]
        continuoNotationB = continuoSuccession[1]
    
        if not continuoNotationA in continuoAList : continuoAList.append(continuoNotationA)
        if not continuoNotationB in continuoBList : continuoBList.append(continuoNotationB)
    
    
    for continuoDictionaryKey, continuoDictionary in modalEns.continuoDictionary.items(): 
        if not continuoDictionaryKey in continuoList:
            continuoList.append(continuoDictionaryKey)
    
    
    rootDict = modalEns.rootAnalysis.rootDictionary
    
    for rootElementKey, rootElement in rootDict.items():
        if not rootElementKey in rootList:
            rootList.append(rootElementKey)
            
        if not rootElement["degree"] in degreeList: 
            degreeList.append(rootElement["degree"]) 
            
            
    for diatonicDegreeKey in modalEns.diatonicDegreesDictionary:
        if diatonicDegreeKey not in diatonicDegreesList: diatonicDegreesList.append(diatonicDegreeKey)
        
        if "#" in diatonicDegreeKey:
            if not diatonicDegreeKey in raisedDegreesList: raisedDegreesList.append(diatonicDegreeKey)
            
rootList.sort()
degreeList.sort()
diatonicDegreesList.sort()
raisedDegreesList.sort()
continuoList.sort()
continuoAList.sort()
continuoBList.sort()
        
successionTable = [[0 for x in range(len(continuoBList))] for y in range(len(continuoAList))] 
        
        


workNumber = len (modalEnsembleList)
# Create new workbook
wb = Workbook()
wb.save(workBookPath)
dataDictionary= {
    'File name': [],
    'Composer':[],
    'Title': [],
    'Measures': [],
    'Parts':[],
    
    'Best scales': [],
    'Keys': [],
    
    'Cadence Successions': [],
    'Cadence points': [],
    'Final chord':[],
    'Final chord root': [],
    
    'Modal attribution': [],
    'Major or minor third': []
    
    }

''' occurrence sheet '''

for partName in modalPartNameList:
    dataDictionary[partName + " octave division"]= []
    dataDictionary[partName + " key"]= []
    dataDictionary[partName + " ambitus"]= []
    dataDictionary[partName + " finalis"]= []
    dataDictionary[partName + " strongest pitches"]= [] 

''' set data for modal ensemble '''
for modalEnsemble in modalEnsembleList :
    getListFromDictionary(dataDictionary, 'File name').append(modalEnsemble.fileName)
    getListFromDictionary(dataDictionary, 'Composer').append(modalEnsemble.composer)
    getListFromDictionary(dataDictionary, 'Title').append(modalEnsemble.title)
    getListFromDictionary(dataDictionary, 'Measures').append(modalEnsemble.measureNumber)
    getListFromDictionary(dataDictionary, 'Parts').append(len(modalEnsemble.modalParts))
    
    getListFromDictionary(dataDictionary, 'Best scales').append(modalEnsemble.bestScales)
    getListFromDictionary(dataDictionary, 'Keys').append(modalEnsemble.keys)
    getListFromDictionary(dataDictionary, 'Cadence Successions').append(modalEnsemble.cadenceSuccession)
    getListFromDictionary(dataDictionary, 'Cadence points').append(modalEnsemble.cadencePoints)
    getListFromDictionary(dataDictionary, 'Final chord').append(modalEnsemble.finalChord)
    getListFromDictionary(dataDictionary, 'Final chord root').append(modalEnsemble.finalChordRoot)
    getListFromDictionary(dataDictionary, 'Modal attribution').append(modalEnsemble.modeName)
    getListFromDictionary(dataDictionary, 'Major or minor third').append(modalEnsemble.majorMinorThird)
    
    
    
    ''' add information to ontology '''
    ''' add work instance '''
    workClassInstance = workClass()
    workClassInstance.hasFilename = [str(modalEnsemble.fileName)]
    workClassInstance.hasComposer = [str(modalEnsemble.composer)] 
    workClassInstance.hasTitle = [str(modalEnsemble.title)] 
    workClassInstance.hasMeasureNumber = [int(modalEnsemble.measureNumber)]
    workClassInstance.hasPartNumber = [int(len(modalEnsemble.modalParts))]
    
    workClassInstance.hasBestScales = modalEnsemble.bestScales
    workClassInstance.hasKeys = modalEnsemble.keys
    workClassInstance.hasCadenceSuccessions = [str(modalEnsemble.cadenceSuccession)]
    workClassInstance.hasCadencePoints = modalEnsemble.cadencePoints
    workClassInstance.hasFinalChord = [str(modalEnsemble.finalChord)]
    workClassInstance.hasFinalChordRoot = [str(modalEnsemble.finalChordRoot)]
    workClassInstance.hasModalAttribution =  modalEnsemble.modeName
    workClassInstance.isMajorMinorThirdMode = modalEnsemble.majorMinorThird
    workClassInstance.hasModalParts = []
    
    ''' fill individual parts '''
        
    for partName in modalPartNameList:
        if partName in modalEnsemble.modalParts:
            ''' ontology '''
            modalPartInstance = modalPartClass()
            modalPartInstance.hasName = [partName]
            modalPartInstance.hasOctaveDivision = [modalEnsemble.modalParts[partName].octaveDivision]
            modalPartInstance.hasKey = [str(modalEnsemble.modalParts[partName].key)]
            
            for element in modalEnsemble.modalParts[partName].ambitus:
                modalPartInstance.hasAmbitus.append(str(element))
                
            
        
            modalPartInstance.hasFinalis = [str(modalEnsemble.modalParts[partName].finalis)]
            modalPartInstance.hasStrongestPitches = [str(modalEnsemble.modalParts[partName].strongestPitches)]
            workClassInstance.hasModalParts.append(modalPartInstance)
            
            ''' dictionary '''
            getListFromDictionary(dataDictionary, partName + " octave division").append(modalEnsemble.modalParts[partName].octaveDivision) 
            getListFromDictionary(dataDictionary, partName + " key").append(modalEnsemble.modalParts[partName].key)
            getListFromDictionary(dataDictionary, partName + " ambitus").append(modalEnsemble.modalParts[partName].ambitus)
            getListFromDictionary(dataDictionary, partName + " finalis").append(modalEnsemble.modalParts[partName].finalis)
            getListFromDictionary(dataDictionary, partName + " strongest pitches").append(modalEnsemble.modalParts[partName].strongestPitches)
        
        else: 
            getListFromDictionary(dataDictionary, partName + " octave division").append("") 
            getListFromDictionary(dataDictionary, partName + " key").append("")
            getListFromDictionary(dataDictionary, partName + " ambitus").append("")
            getListFromDictionary(dataDictionary, partName + " finalis").append("")
            getListFromDictionary(dataDictionary, partName + " strongest pitches").append("") 

    ''' vectors... '''
            
    rootDict = modalEnsemble.rootAnalysis.rootDictionary
    vectorDict = modalEnsemble.vectorAnalysis.show('dict')
    continuoDict =  modalEnsemble.continuoDictionary 
    motionDict = modalEnsemble.motionDictionary
    totalVectors = 0 
    
    
   
    
    for vector in [4, -3, 2, -4, 3, -2]:
        dataList = getListFromDictionary(dataDictionary, vector)
        if vector in vectorDict:
            dataList.append (vectorDict[vector]["occurrence"]) 
            totalVectors = totalVectors + float(vectorDict[vector]["occurrence"])
            
            
            vectorInstance = vectorClass()
            vectorInstance.hasName = [str(vector)]
            vectorInstance.hasOccurrence = [int(vectorDict[vector]["occurrence"])]
            workClassInstance.hasVectors.append(vectorInstance)
            
        else:
            dataList.append(0)
            
    ''' add VD and VS sums '''
    dataListVD = getListFromDictionary(dataDictionary, "VD")
    dataListVS = getListFromDictionary(dataDictionary, "VS")
    dataListVD.append(vectorDict["dominant"]["occurrence"])
    dataListVS.append(vectorDict["subdominant"]["occurrence"]) 
    getListFromDictionary(dataDictionary, "Total vectors").append(totalVectors)
    
    
    dominantVectors = vectorClass()
    dominantVectors.hasName = ["DV"]
    dominantVectors.hasOccurence = [int(vectorDict["dominant"]["occurrence"])]
    
    subdominantVectors = vectorClass()
    subdominantVectors.hasName = ["SV"]
    subdominantVectors.hasOccurrence = [int(vectorDict["subdominant"]["occurrence"])]
    
    totalVec = vectorClass()
    totalVec.hasName = ["Total_vectors"]
    totalVec.hasOccurrence = [int(totalVectors)]
    
    
    workClassInstance.hasVectors.append(dominantVectors)
    workClassInstance.hasVectors.append(subdominantVectors)
    workClassInstance.hasVectors.append(totalVec)
    
    
    for aCounter, continuoA in enumerate(continuoAList):
        for bCounter, continuoB in enumerate(continuoBList):    
            continuoSuccession = continuoA + "=>" + continuoB     
            if continuoSuccession in  modalEnsemble.continuoSuccessionDictionary:
                if successionTable[aCounter][bCounter] == "": 
                    successionTable[aCounter][bCounter] = 0
                
                successionTable[aCounter][bCounter] =  successionTable[aCounter][bCounter] + len (modalEnsemble.continuoSuccessionDictionary[continuoSuccession])

     
    ''' diatonic degrees '''
    raisedDegrees_6 = 0
    raisedDegrees_ = 0
    for diatonicDegree in diatonicDegreesList:
        dataList = getListFromDictionary(dataDictionary, diatonicDegree + " (system degree)")
        if diatonicDegree in modalEnsemble.diatonicDegreesDictionary:
            diatonicDegreeValue = 0
            
            for element in modalEnsemble.diatonicDegreesDictionary[diatonicDegree]:
                diatonicDegreeValue = diatonicDegreeValue + element.duration
            
            
                
            dataList.append(diatonicDegreeValue) 
            if "#" in diatonicDegree and "_6" in diatonicDegree :  raisedDegrees_6 = raisedDegrees_6 +diatonicDegreeValue
            if "#" in diatonicDegree and diatonicDegree [-1] =="_":  raisedDegrees_ = raisedDegrees_ +diatonicDegreeValue
            
        else:
            dataList.append(0)
    dataList = getListFromDictionary(dataDictionary, "Raised degrees (system degree)_")
    dataList.append(raisedDegrees_)        
    
    dataList = getListFromDictionary(dataDictionary, "Raised degrees (system degree)_6")
    dataList.append(raisedDegrees_6)
            
    
    ''' roots  '''
    totalRoots  = 0
     
    for rootElement in rootList: 
        totalRoot = 0
        
        if rootElement in rootDict:
            rootInstance = rootsClass ()
            rootInstance.hasName = [str(rootElement)]
        for interv in ["P1", "m3", "M3", "p5", "d5"]:
            dataList = getListFromDictionary(dataDictionary, rootElement + "_" + interv)
            
            if rootElement in rootDict:
                rootEntry = rootDict[rootElement]
                
                
                
            
                if interv in rootEntry : 
                    inversionInstance = inversionsClass()
                    inversionInstance.hasName = [str(interv)]
                    inversionInstance.hasDuration = [float(rootEntry[interv])] 
                    
                    
                    rootInstance.hasInversions.append(inversionInstance)
                    
                    dataList.append (rootEntry[interv])
                    totalRoots = totalRoots + float (rootEntry[interv])
                    totalRoot = totalRoot + float (rootEntry[interv])
                else:
                    dataList.append(0)
            else:
                dataList.append(0)
            
         
        
        if rootElement in rootDict:
            rootInstance.hasDuration = [float(totalRoot)]
            workClassInstance.hasRoots.append(rootInstance)    

            
    
    getListFromDictionary(dataDictionary, "Total roots").append(totalRoots)
    
    
    ''' scale degrees '''
    totalScaleDegrees = 0
    for continuoElement in continuoList:
        dataList = getListFromDictionary(dataDictionary, continuoElement)
        if continuoElement in continuoDict:
            
            scaleDeg = str(continuoElement[0])
            splitContElement = continuoElement.split("_")
            harmonization = ""
            chromaticAlt = ""
            
            if len(splitContElement) == 2: harmonization = splitContElement[1]
            if len (splitContElement[0]) == 2:  chromaticAlt = splitContElement[0][1]
            
            bassScaleDegreeInstance = bassScaleDegreeClass()
            bassScaleDegreeInstance.hasName = [continuoElement]
            bassScaleDegreeInstance.hasChromaticAlteration = [chromaticAlt]
            bassScaleDegreeInstance.hasHarmonization = [harmonization]
            bassScaleDegreeInstance.hasOccurrence = [int(continuoDict[continuoElement])]
            
            
            if bassScaleDegreeInstance.hasOccurrence == 0:
                print()
          
            workClassInstance.hasBassScaleDegrees.append(bassScaleDegreeInstance)           
            dataList.append(continuoDict[continuoElement])
            totalScaleDegrees = totalScaleDegrees + float (continuoDict[continuoElement])
        else: dataList.append(0)
    getListFromDictionary(dataDictionary, "Total scale degrees").append(totalScaleDegrees)
        
    ''' scale degree motions '''
    
    for motionType in ["step_5=>5", "step_6=>6", "step_6<=>5", "leep_5=>5", "leep_6=>6", "leep_6<=>5", "+m2_6=>5", "+m2_other", "-m2_5=>6", "-m2_other"]:
        dataList = getListFromDictionary(dataDictionary, motionType)
        
        if motionType in motionDict:
            dataList.append(len (motionDict[motionType]))
        else: 
            dataList.append(0)
            
        
        
    
          
''' add total line '''
for elementKey, element in dataDictionary.items():
    element.append(getTotalFromList(element))
        
        

    
#    ''' degrees  '''   
#     for degreeElement in degreeList: 
#         for interv in ["P1", "m3", "M3", "p5", "d5"]:
#             dataList = getListFromDictionary(dataDictionary, degreeElement + "_" + interv)
#             correspondingRoot = modalEnsemble.rootAnalysis.getRootCorrespondingToScaleDegree(degreeElement)
#             
#             if correspondingRoot != None:
#                  
#             
#                 if interv in correspondingRoot : 
#                     dataList.append (correspondingRoot[interv])
#                 else:
#                     dataList.append("")
#             else:
#                 dataList.append("")
            

''' percents sheet '''
    
percentsDataDictionary = copy.deepcopy(dataDictionary)

''' loop over file name column '''
fileNameList = percentsDataDictionary ["File name"]

for fileNameCounter, fileName in enumerate(fileNameList):
    ''' vectors ''' 
    totalVectorsList = percentsDataDictionary["Total vectors"]
    totalRootsList = percentsDataDictionary["Total roots"]
    totalScaleDegrees = percentsDataDictionary["Total scale degrees"]
    
    for vector in [4, -3, 2, -4, 3, -2]:
        vectorList = percentsDataDictionary[vector]
        vectorList[fileNameCounter] = vectorList[fileNameCounter]/totalVectorsList[fileNameCounter]
        
    totalVectorsList[fileNameCounter] = totalVectorsList[fileNameCounter] / totalVectorsList[fileNameCounter]
    
    ''' roots ''' 
    for routCounter, rootElement in enumerate(rootList): 
        for interv in ["P1", "m3", "M3", "p5", "d5"]:
            rootList_2 = percentsDataDictionary[rootElement + "_" + interv]
            rootList_2 [fileNameCounter] = rootList_2 [fileNameCounter]  / totalRootsList[fileNameCounter]
    totalRootsList[fileNameCounter] = totalRootsList[fileNameCounter] / totalRootsList[fileNameCounter]
          
    ''' degrees '''
    for degreesCounter, degreeElement in enumerate (continuoList):
        degreeList_2 = percentsDataDictionary[degreeElement]
        degreeList_2[fileNameCounter] = degreeList_2[fileNameCounter] / totalScaleDegrees[fileNameCounter]
    totalScaleDegrees[fileNameCounter] = totalScaleDegrees[fileNameCounter] / totalScaleDegrees[fileNameCounter]  
 
 
''' root synthesis sheet '''
''' create specific root dictionary '''    
rootIntDictionary = {}

for rootElement in rootList: 
    rootIntDictionary[rootElement]=[]
    for interv in ["P1", "m3", "M3", "p5", "d5"]:
        rootIntDictionary[rootElement].append(dataDictionary[rootElement + "_" + interv][-1])
    
    
 
 
        
''' scale degrees synthesis sheet '''
scaleDegreeList = []
alterationList = []
for continuoSign in continuoList:
    splitContinuoSign = continuoSign.split("_")
    if not splitContinuoSign[1] in alterationList:
        alterationList.append(splitContinuoSign[1])
    if not splitContinuoSign[0] in scaleDegreeList:
        scaleDegreeList.append(splitContinuoSign[0])

continuoSignDict = {}
for scaleDegree in scaleDegreeList:
    for alterlation in alterationList:
        if not scaleDegree in continuoSignDict: 
            continuoSignDict[scaleDegree] = []
            
        if scaleDegree + "_" + alterlation in dataDictionary:
            continuoSignDict[scaleDegree].append(dataDictionary[scaleDegree + "_" + alterlation][-1])
        else: 
            continuoSignDict[scaleDegree].append(0)   
       
 
dfOccurrence = pd.DataFrame(data=dataDictionary)
dfPercents = pd.DataFrame(data=percentsDataDictionary)
dfRoots = pd.DataFrame(data=rootIntDictionary)
dfContinuo = pd.DataFrame(data=continuoSignDict)
dfContinuoSuccession = pd.DataFrame (successionTable,  columns=continuoBList, index=continuoAList)

 
                                            


writer = pd.ExcelWriter(workBookPath, engine='xlsxwriter')

dfOccurrence.to_excel(writer, sheet_name='Résultats généraux (o)')
dfPercents.to_excel(writer, sheet_name='Résultats généraux (p)')
dfRoots.to_excel(writer, sheet_name='Roots')
dfContinuo.to_excel(writer, sheet_name='Scale degrees')
dfContinuoSuccession.to_excel(writer, sheet_name='Degree successions')


writer.save()
onto.save(file = ontologyName, format = "rdfxml")

  

 

    

