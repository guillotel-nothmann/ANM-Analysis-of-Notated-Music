'''
Created on Nov 3, 2021

@author: christophe
'''

import os 
from harmonicAnalysis.cadenceAnalysis import Cadences 

'''PolyMIR'''
from pitchAnalysis.scales import ScaleAnalysis
import pitchCollections

from music21 import converter 
from copy import deepcopy
import pandas as pd



def getListFromDictionary(dataDictionary, dictionaryKey):
    
    if dictionaryKey not in dataDictionary:
        dataDictionary[dictionaryKey] = []
        
    return dataDictionary[dictionaryKey]

def getRowIndexForEntry (coll, rowname):
    for counter, element in enumerate(coll):
        if element == rowname: return counter
        
    return -1
    


if __name__ == '__main__':
    pass

workWithRootDirectoryString = '/Users/christophe/Documents/Praetorius/Terpsichore/Terpsichore/source/xmlWithCadences/'
workBookPath = '/Users/christophe/Documents/Praetorius/Terpsichore/Analyse/scaleDegrees.xlsx'

workDictionary = {"027.musicxml" : "['ionian']",
"091.musicxml" : "['ionian']",
"092.musicxml" : "['ionian']",
"093.musicxml" : "['ionian']",
"104.musicxml" : "['ionian']",
"106.musicxml" : "['ionian']",
"108.musicxml" : "['ionian']",
"111.musicxml" : "['ionian']",
"117.musicxml" : "['ionian']",
"131.musicxml" : "['ionian']",
"140.musicxml" : "['ionian']",
"141.musicxml" : "['ionian']",
"142.musicxml" : "['ionian']",
"143.musicxml" : "['ionian']",
"144.musicxml" : "['ionian']",
"145.musicxml" : "['ionian']",
"146.musicxml" : "['ionian']",
"147.musicxml" : "['ionian']",
"148.musicxml" : "['ionian']",
"296.musicxml" : "['ionian']",
"297.musicxml" : "['ionian']",
"300.musicxml" : "['ionian']",
"301.musicxml" : "['ionian']",
"359.musicxml" : "['ionian']",
"379.musicxml" : "['ionian']",
"404.musicxml" : "['ionian']",
"406.musicxml" : "['ionian']",
"408.musicxml" : "['ionian']",
"410.musicxml" : "['ionian']",
"411.musicxml" : "['ionian']",
"412.musicxml" : "['ionian']",
"415.musicxml" : "['ionian']",
"416.musicxml" : "['ionian']",
"418.musicxml" : "['ionian']",
"419.musicxml" : "['ionian']",
"424.musicxml" : "['ionian']",
"427.musicxml" : "['ionian']",
"430.musicxml" : "['ionian']",
"431.musicxml" : "['ionian']",
"435.musicxml" : "['ionian']",
"437.musicxml" : "['ionian']",
"438.musicxml" : "['ionian']",
"439.musicxml" : "['ionian']",
"441.musicxml" : "['ionian']",
"442.musicxml" : "['ionian']",
"444.musicxml" : "['ionian']",
"445.musicxml" : "['ionian']",
"462.musicxml" : "['ionian']",
"493.musicxml" : "['ionian']",
"510.musicxml" : "['ionian']",
"514.musicxml" : "['ionian']",
"528.musicxml" : "['ionian']",
"208.musicxml" : "['ionian']",
"436.musicxml" : "['ionian']"}


description = "Ionian on D"
 

corrputedFilesList = []
analyzedWorksList = []

overallContinuoDict = {}
overallDiatonicDict = {}
overallSuccessionDict = {}
bassPatternDictionary = {} # these are the actual bass progressions found in the works 
bassSubPatternList = [] # these are the subpatterns found in all pieces



for file in os.listdir(workWithRootDirectoryString):
    fileName = os.fsdecode(file)
    if fileName.endswith(".musicxml")== False: continue
    
    if fileName not in workDictionary: continue
    
    
    print ("Analyzing file :" + fileName)
    scaleDegreeDictionary = {}
 
    
    workPath = workWithRootDirectoryString + fileName 
    workWithoutRoot = converter.parse(workPath)
    
    #workWithRoot = converter.parse(workPath)
    
    #''' get root stream '''
    #rootStream = None
    #for part in workWithRoot.parts:
    #    if part.partName == "Root":
    #        rootStream = part
    #    
    #if rootStream == None: 
    #    continue
    #    print (fileName + ": Cannot find root stream")
    #    corrputedFilesList.append(fileName)
    #    
    #    
    #workWithoutRoot = deepcopy(workWithRoot)
    #workWithoutRoot.remove(rootStream, recurse=True)
    
    ''' get best scale and reference pitch '''
    scaleAnal = ScaleAnalysis(workWithoutRoot)
    bestScale = scaleAnal.getBestDiatonicScale() 
    
    cadenceAnal = Cadences(workWithoutRoot, analysisMode="annotationsFermata")
    
    referencePitch = cadenceAnal.getFinalRoot()
    
    ''' create PitchCollectionSequencesObject  '''
    pitchCollectionSequence = scaleAnal.pitchCollectionSequence
    pitchCollectionSequence.setRealbassScaleDegreeFromReferencePitch(bestScale[0], referencePitch)
    
    pitchCollectionSequence.setRealBassDiatonicDegree(bestScale[0])
    continuoDict = pitchCollectionSequence.getContinuoDictionary()
    
    bassPatterns = pitchCollectionSequence.getRealBassPatterns()
    
    bassPatternDictionary[fileName] = bassPatterns
    
    for pattern in pitchCollectionSequence.getRealBassSubPatterns(bassPatterns, minLength=3):
        if not pattern in bassSubPatternList:
            bassSubPatternList.append(pattern)
    
    diatonicDict= pitchCollectionSequence.getDiatonicDegreesDictionary() 
    pitchCollectionSequence.analyzeRealBassMovements() 
    successionDict = pitchCollectionSequence.continuoSuccessionDict
    
    ''' add entries to overall dictionaries '''
    
    ''' 0. diatonic dic ''' 
    for element in diatonicDict:
        if element not in overallDiatonicDict: 
            overallDiatonicDict[element] = {}
            overallDiatonicDict[element]["name"] = diatonicDict[element]["name"]
            overallDiatonicDict[element]["occurrences"] = 0
            overallDiatonicDict[element]["duration"] = 0
            overallDiatonicDict[element]["harmonizations"] = {}
            
            
        overallDiatonicDict[element]["occurrences"] = overallDiatonicDict[element]["occurrences"] + len (diatonicDict[element]["pitchCollections"])
        overallDiatonicDict[element]["duration"] =  overallDiatonicDict[element]["duration"] + diatonicDict[element]["duration"]
        
        for harmElement in diatonicDict[element]["harmonizations"]:
            if harmElement not in overallDiatonicDict[element]["harmonizations"]:
                overallDiatonicDict[element]["harmonizations"][harmElement] = {}
                overallDiatonicDict[element]["harmonizations"][harmElement]["name"] = diatonicDict[element]["harmonizations"][harmElement]["name"]
                overallDiatonicDict[element]["harmonizations"][harmElement]["occurrences"] = 0
                overallDiatonicDict[element]["harmonizations"][harmElement]["duration"] = 0
            
            overallDiatonicDict[element]["harmonizations"][harmElement]["occurrences"] = overallDiatonicDict[element]["harmonizations"][harmElement]["occurrences"] + len (diatonicDict[element]["harmonizations"][harmElement]["pitchCollections"]) 
            overallDiatonicDict[element]["harmonizations"][harmElement]["duration"] = overallDiatonicDict[element]["harmonizations"][harmElement]["duration"] + diatonicDict[element]["harmonizations"][harmElement]["duration"]
    
    
    
    
    ''' 1. continuo dic '''
    for element in continuoDict:
        if element not in overallContinuoDict: 
            overallContinuoDict[element] = {}
            overallContinuoDict[element]["name"] = continuoDict[element]["name"]
            overallContinuoDict[element]["occurrences"] = 0
            overallContinuoDict[element]["duration"] = 0
            overallContinuoDict[element]["harmonizations"] = {}
            
            
        overallContinuoDict[element]["occurrences"] = overallContinuoDict[element]["occurrences"] + len (continuoDict[element]["pitchCollections"])
        overallContinuoDict[element]["duration"] =  overallContinuoDict[element]["duration"] + continuoDict[element]["duration"]
        
        for harmElement in continuoDict[element]["harmonizations"]:
            if harmElement not in overallContinuoDict[element]["harmonizations"]:
                overallContinuoDict[element]["harmonizations"][harmElement] = {}
                overallContinuoDict[element]["harmonizations"][harmElement]["name"] = continuoDict[element]["harmonizations"][harmElement]["name"]
                overallContinuoDict[element]["harmonizations"][harmElement]["occurrences"] = 0
                overallContinuoDict[element]["harmonizations"][harmElement]["duration"] = 0
            
            overallContinuoDict[element]["harmonizations"][harmElement]["occurrences"] = overallContinuoDict[element]["harmonizations"][harmElement]["occurrences"] + len (continuoDict[element]["harmonizations"][harmElement]["pitchCollections"]) 
            overallContinuoDict[element]["harmonizations"][harmElement]["duration"] = overallContinuoDict[element]["harmonizations"][harmElement]["duration"] + continuoDict[element]["harmonizations"][harmElement]["duration"]
    
    
    ''' 2. succession Dic '''
    
    for element in successionDict:
        if element not in overallSuccessionDict: 
            overallSuccessionDict[element] = {}
            overallSuccessionDict[element]["name"] = successionDict[element]["name"]
            overallSuccessionDict[element]["firstScaleDegreeName"] = successionDict[element]["firstScaleDegreeName"]
            overallSuccessionDict[element]["secondScaleDegreeName"] = successionDict[element]["secondScaleDegreeName"]
            overallSuccessionDict[element]["occurrences"] = 0 
            overallSuccessionDict[element]["harmonizations"] = {}
        
        overallSuccessionDict[element]["occurrences"] = overallSuccessionDict[element]["occurrences"] + len (successionDict[element]["pitchCollectionPairs"])
        
        for harmElement in successionDict[element]["harmonizations"]:
            if harmElement not in overallSuccessionDict[element]["harmonizations"]:
                overallSuccessionDict[element]["harmonizations"][harmElement] = {}
                overallSuccessionDict[element]["harmonizations"][harmElement]["name"] = successionDict[element]["harmonizations"][harmElement]["name"]
                overallSuccessionDict[element]["harmonizations"][harmElement]["firstHarmonizationName"] = successionDict[element]["harmonizations"][harmElement]["firstHarmonizationName"]
                overallSuccessionDict[element]["harmonizations"][harmElement]["secondHarmonizationName"] = successionDict[element]["harmonizations"][harmElement]["secondHarmonizationName"]
                overallSuccessionDict[element]["harmonizations"][harmElement]["occurrences"] = 0
                
            overallSuccessionDict[element]["harmonizations"][harmElement]["occurrences"] = overallSuccessionDict[element]["harmonizations"][harmElement]["occurrences"] + len(successionDict[element]["harmonizations"][harmElement]["pitchCollectionPairs"])
                
                
                

''' print everything '''
dataDicIn = {description:list(workDictionary.keys())}
            
            
''' 0.1 scale degrees overall '''
dataDictionaryDiatonicDegrees = {
    "Scale degree" :[],
    "Occurrences": [],
    "Durations": []
    }        
    
for key in sorted (list(overallDiatonicDict.keys())):
    dataDictionaryDiatonicDegrees["Scale degree"].append(overallDiatonicDict[key]["name"])
    dataDictionaryDiatonicDegrees["Occurrences"].append(overallDiatonicDict[key]["occurrences"])
    dataDictionaryDiatonicDegrees["Durations"].append(overallDiatonicDict[key]["duration"])
  
''' 0.2 scale degrees with harmonization '''
harmonizationRows = []
harmonizationColls = []
for key in overallDiatonicDict:
    if not key in harmonizationColls: harmonizationColls.append(key)
    
    for harmKey in  overallDiatonicDict[key]["harmonizations"]:
        if not harmKey in harmonizationRows: harmonizationRows.append(harmKey)
harmonizationRows = sorted (harmonizationRows)
harmonizationColls = sorted (harmonizationColls)

dataDiatonicHarm = {"Harmonization": harmonizationRows}
for coll in harmonizationColls:
    if not coll in dataDiatonicHarm: dataDiatonicHarm[coll] = [0 for x in harmonizationRows]
    
for key in overallDiatonicDict:
    coll = getListFromDictionary(dataDiatonicHarm, key)
    
    for harmKey in overallDiatonicDict[key]["harmonizations"]:
        rowIndex = getRowIndexForEntry(dataDiatonicHarm["Harmonization"], harmKey)
        coll[rowIndex] = overallDiatonicDict[key]["harmonizations"][harmKey]["duration"]
            
            
            

''' 1.1 scale degrees overall '''
dataDictionaryScaleDegrees = {
    "Scale degree" :[],
    "Occurrences": [],
    "Durations": []
    }        
    
for key in sorted (list(overallContinuoDict.keys())):
    dataDictionaryScaleDegrees["Scale degree"].append(overallContinuoDict[key]["name"])
    dataDictionaryScaleDegrees["Occurrences"].append(overallContinuoDict[key]["occurrences"])
    dataDictionaryScaleDegrees["Durations"].append(overallContinuoDict[key]["duration"])
  
''' 1.2 scale degrees with harmonization '''
harmonizationRows = []
harmonizationColls = []
for key in overallContinuoDict:
    if not key in harmonizationColls: harmonizationColls.append(key)
    
    for harmKey in  overallContinuoDict[key]["harmonizations"]:
        if not harmKey in harmonizationRows: harmonizationRows.append(harmKey)
harmonizationRows = sorted (harmonizationRows)
harmonizationColls = sorted (harmonizationColls)

dataDegreesHarm = {"Harmonization": harmonizationRows}
for coll in harmonizationColls:
    if not coll in dataDegreesHarm: dataDegreesHarm[coll] = [0 for x in harmonizationRows]
    
for key in overallContinuoDict:
    coll = getListFromDictionary(dataDegreesHarm, key)
    
    for harmKey in overallContinuoDict[key]["harmonizations"]:
        rowIndex = getRowIndexForEntry(dataDegreesHarm["Harmonization"], harmKey)
        coll[rowIndex] = overallContinuoDict[key]["harmonizations"][harmKey]["duration"]
    

      
           
''' 2.1 scale degree successions (overall)'''
''' create colls (second scale degree name)'''  
dataDictionarySuccessions = {"First degree/ second degree": []} 
     
for simpleSuccession in sorted(list(overallSuccessionDict.keys()), key=lambda entry: entry.split("_")[-1]): 
    getListFromDictionary (dataDictionarySuccessions, overallSuccessionDict[simpleSuccession]["secondScaleDegreeName"])

''' populate colls '''
for simpleSuccession in sorted(list(overallSuccessionDict.keys())):
    
    ''' get row or create it '''
    rowIndex = getRowIndexForEntry(dataDictionarySuccessions["First degree/ second degree"], overallSuccessionDict[simpleSuccession]["firstScaleDegreeName"])
    if rowIndex == -1: 
        for coll in dataDictionarySuccessions: dataDictionarySuccessions[coll].append(0)
    
    
    ''' add actual value '''
    dataDictionarySuccessions["First degree/ second degree"][rowIndex] = overallSuccessionDict[simpleSuccession]["firstScaleDegreeName"]
    dataDictionarySuccessions[overallSuccessionDict[simpleSuccession]["secondScaleDegreeName"]][rowIndex] = overallSuccessionDict[simpleSuccession]["occurrences"]
    
''' 2.2. scale degree succession (with harm) '''
    
harmonizationRows = []
harmonizationColls = []
for key in overallSuccessionDict:
    for harmKey in overallSuccessionDict[key]["harmonizations"]:
        splitHarmKey = harmKey.split("=>")
    
        if not splitHarmKey[0] in harmonizationRows: harmonizationRows.append(splitHarmKey[0])
        if not splitHarmKey[1] in harmonizationColls: harmonizationColls.append(splitHarmKey[1])
    
harmonizationRows = sorted (harmonizationRows)
harmonizationColls = sorted (harmonizationColls)

dataHarmSuccession = {"Harm succession": harmonizationRows}
for coll in harmonizationColls:
    if not coll in dataHarmSuccession: dataHarmSuccession[coll] = [0 for x in harmonizationRows]
    
for key in overallSuccessionDict:
    for harmKey in overallSuccessionDict[key]["harmonizations"]:
        splitHarmKey = harmKey.split("=>")
        
        successionColl = getListFromDictionary(dataHarmSuccession, splitHarmKey[1])
        
        rowIndex = getRowIndexForEntry(dataHarmSuccession["Harm succession"], splitHarmKey[0])
        successionColl[rowIndex] = overallSuccessionDict[key]["harmonizations"][harmKey]["occurrences"]
        
        
    

''' 3 bass patterns '''
       
        
dataDicBassPatterns = {
    "Pattern": [], "Length": [], "Occurrence": [], "fileName": [], "mode": []}
for bassSubPattern in bassSubPatternList:
    occurrence = 0
    bassPatternLen = len (bassSubPattern)
    fileNameList = []
    modeList = []
    
    for fileName, bassPattern in bassPatternDictionary.items():
        bassPatternStr = str(bassPattern)
        
        
        
        
        if  bassPatternStr.count(str(bassSubPattern)[1:-1]) != 0:
            occurrence = occurrence +  bassPatternStr.count(str(bassSubPattern)[1:-1])
            if fileName not in fileNameList:
                fileNameList.append(fileName)
            
            if not workDictionary[fileName] in modeList:
                modeList.append(workDictionary[fileName])
        
    
    dataDicBassPatterns["Pattern"].append(str(bassSubPattern))
    dataDicBassPatterns["Length"].append(bassPatternLen)
    dataDicBassPatterns["Occurrence"].append(occurrence)
    dataDicBassPatterns["fileName"].append(fileNameList)
    dataDicBassPatterns["mode"].append(sorted (modeList))
    
   

writer = pd.ExcelWriter(workBookPath, engine='xlsxwriter')
pd.DataFrame(data=dataDicIn).to_excel(writer, sheet_name='Collection')
pd.DataFrame(data=dataDictionaryDiatonicDegrees).to_excel(writer, sheet_name='Diatonic degrees')
pd.DataFrame(data=dataDiatonicHarm).to_excel(writer, sheet_name='Diatonic degrees with harm.')
pd.DataFrame(data=dataDictionaryScaleDegrees).to_excel(writer, sheet_name='Modal degrees')
pd.DataFrame(data=dataDegreesHarm).to_excel(writer, sheet_name='Modal degrees with harm.')
pd.DataFrame(data=dataDictionarySuccessions).to_excel(writer, sheet_name='Modal progressions') 
pd.DataFrame(data=dataHarmSuccession).to_excel(writer, sheet_name='Modal progressions with harm.')   
pd.DataFrame(data=dataDicBassPatterns).to_excel(writer, sheet_name='Modal bass patterns with harm.')           


writer.save()         
            
        


    
    
    
    
    
    