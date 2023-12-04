'''
Created on Nov 2, 2022

@author: christophe
'''
from datetime import datetime 

''' used to create root individuals to be connected to a verticality in the Sherlock interface '''

if __name__ == '__main__':
    pass





import rootAnalysis, os, pitchCollections

from owlready2  import get_ontology, Thing, ObjectProperty, DataProperty, default_world
from music21 import converter

workDirectoryString = '/Users/christophe/Dropbox/HarmonisationsBach/Hugues/'
outputDirectoryString = '/Users/christophe/Documents/GitHub/tonalities-pilot/annotations/rootAnnotations.owl'

analystName = "Hugues Seress"
orcid = "0000-0001-9950-2657"

onto = get_ontology(outputDirectoryString).load()

 
 

for file in os.listdir(workDirectoryString):
    fileName = os.fsdecode(file)
    if fileName.endswith(".musicxml")== False: continue
    
    
    stats = os.stat(workDirectoryString + fileName)
   
    
 
    
    print ("Analyzing file " + fileName)
    
    

    workPath = workDirectoryString + fileName 
    work = converter.parse(workPath)
    
    
    
    ''' create pitch collection object '''
    
    ''' create PirtchCollectionSequencesObject '''
    pitchCollectionSequence = pitchCollections.PitchCollectionSequence(work)
    pitchCollectionSequence.setRootsFromPart("Root")
    
    
    ''' create individuals for all pitch colls '''
    for pitchColl in pitchCollectionSequence.explainedPitchCollectionList:
        if pitchColl.rootPitch == None: continue
        
        root = onto.rootAnnotation()
        
        root.hasAbsoluteOffset = pitchColl.offset
        root.hasAnalystName = analystName
        root.hasDateTime = datetime.fromtimestamp(stats.st_mtime)
        root.hasFileName = fileName
        root.hasMeasureNumber = pitchColl.measureNumber
        root.hasRelativeOffset = pitchColl.relativeOffset
        root.hasMeasureBeat = "beat-" + str(pitchColl.measureNumber) + "-" + str(pitchColl.relativeOffset)
        root.hasORCID = orcid
        root.hasPitch = pitchColl.rootPitch.name
        
        
    
onto.save(file = outputDirectoryString, format = "rdfxml")