'''
Created on Mar 25, 2020

@author: christophe
'''
from music21.tempo import MetronomeMark
 

if __name__ == '__main__':
    pass
import os
from music21 import converter, clef, meter, tempo

''' set paths '''
directoryName=os.path.dirname
rootDirectoryName = directoryName(directoryName(directoryName(__file__)))

workDirectoryString = '/Users/christophe/Documents/GitHub/BachChorals/krn/'
outputDirectoryString = '/Users/christophe/Documents/GitHub/BachChorals/xml/'


for file in os.listdir(workDirectoryString):
    fileName = os.fsdecode(file)
    if fileName.endswith(".krn")== False: continue 
    musicXMLFile = fileName.replace (".krn", ".musicxml")
    musicXMLFile = musicXMLFile.replace ("chor", "")
 
    work = converter.parse(workDirectoryString+ fileName, forceSource=True)
    
    
    ''' remove metronome marks '''
    metronomeMarkList = []
    
    for element in work.recurse(includeSelf=True): 
        if isinstance(element,tempo.MetronomeMark):
            metronomeMarkList.append(element)
    
    for metronomeMarkInstance in metronomeMarkList: 
        work.remove(metronomeMarkInstance, recurse=True)
    
    
    
    for part in work.parts:
        
        ''' change clef ''' 
        bestPartClef =  clef.bestClef(part, True, True)
        part.clef = bestPartClef
        
        ''' set time signatures '''
        partTimeSignatureList =[]
        for element in part.recurse(includeSelf=True): 
            if isinstance(element, meter.TimeSignature):
                partTimeSignatureList.append(element)
        part.timeSignature = partTimeSignatureList[0]
    

    
        ''' change part names '''    
        if part.id == "spine_1":
            part.partName = "Root"
            part.partAbbreviation = "R."
            
            
            
        
        if part.id == "spine_0":
            part.partName = "Bass"
            part.partAbbreviation = "B."
           
            
        if part.id == "spine_1":
            part.partName = "Tenor"
            part.partAbbreviation = "T."
        
        if part.id == "spine_2":
            part.partName = "Alto"
            part.partAbbreviation = "A."
        
        if part.id == "spine_3":
            part.partName = "Soprano"
            part.partAbbreviation = "S."
            
        
        ''' remove tempo indications '''
            
    
    
 
    
    
    work.write('musicxml', outputDirectoryString + musicXMLFile)