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

from openpyxl import Workbook   

import pandas as pd


'''Create nested classes of modal-tonal markers'''

def getListFromDictionary(dataDictionary, dictionaryKey):
    return dataDictionary[dictionaryKey]
    
    
    
    


if __name__ == '__main__':
    pass


''' folder '''
directroyString = '/Users/christophe/Dropbox/Praetorius/Polyhymnia/Source/xmlNUM_2/'
workBookPath  = '/Users/christophe/Dropbox/Praetorius/Polyhymnia/results_26082020.xlsx'
directory = os.fsencode(directroyString)
modalEnsembleList = [] #  every item corresponds to one work
modalPartNameList = [] # every item corresponds to one part name



''' get data '''

dirList = os.listdir(directory)

for file in dirList:
    
    
    filename = os.fsdecode(file)
    if filename.endswith(".musicxml")== False: continue
    
    if filename in ['046.musicxml',
                    '057.musicxml'
                        ]: continue

    print ("Analyzing file : " + str(filename)) 
    
    
    work = converter.parse('%s%s' %(directroyString, filename))
    modalEnsembleInstance = ModalEnsemble()
    
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
    cadenceAn= Cadences(work, modalEnsembleInstance.modalParts)
    modalEnsembleInstance.setCadences(cadenceAn)
  
    
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
        
         
''' Loop over modalEnsembleList ''' 
    
#  Create empty line
workNumber = len (modalEnsembleList)

# Create new workbook


wb = Workbook()
wb.save(workBookPath)
dataDictionary= {
    'File name': [],
    'Composer':[],
    'Title': [],
    'Measures': [],
    
    'Best scales': [],
    'Keys': [],
    
    'Cadence Successions': [],
    'Cadence points': [],
    'Final chord':[],
    'Final chord root': [],
    
    'Modal attribution': [],
    'Major or minor third': []
    
    }

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
    getListFromDictionary(dataDictionary, 'Best scales').append(modalEnsemble.bestScales)
    getListFromDictionary(dataDictionary, 'Keys').append(modalEnsemble.keys)
    getListFromDictionary(dataDictionary, 'Cadence Successions').append(modalEnsemble.cadenceSuccession)
    getListFromDictionary(dataDictionary, 'Cadence points').append(modalEnsemble.cadencePoints)
    getListFromDictionary(dataDictionary, 'Final chord').append(modalEnsemble.finalChord)
    getListFromDictionary(dataDictionary, 'Final chord root').append(modalEnsemble.finalChordRoot)
    getListFromDictionary(dataDictionary, 'Modal attribution').append(modalEnsemble.modeName)
    getListFromDictionary(dataDictionary, 'Major or minor third').append(modalEnsemble.majorMinorThird)
    
    
    ''' fill individual parts '''
        
    for partName in modalPartNameList:
        if partName in modalEnsemble.modalParts:
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
        
 
df = pd.DataFrame(data=dataDictionary)
df.to_excel(workBookPath)  

 

    

