'''
Created on Oct 18, 2021

@author: christophe
'''
import os, ontology
from datetime import datetime
from music21 import converter 

from clefsAndKeys.clefsAndKeysAnal import ClefsAndKeysAnalysis

if __name__ == '__main__':
    pass

now = datetime.now()
dt_string = now.strftime("%d%m%Y_%H%M")


workFolderString = '/Users/christophe/Documents/ontologies/works/'
analysisOntologyPath = 'file:///Users/christophe/Documents/ontologies/ontologies/analysisOntology.rdf'

modelPath = "file:///Users/christophe/Documents/ontologies/ontologies/Zarlino_1558_test.rdf" #"file:/Users/christophe/Documents/ontologies/ontologies/modalityTonality#"

workFolder = os.fsencode(workFolderString)

onto = ontology.AnalysisOntology(analysisOntologyPath)


''' import theoretical model '''


''' get data '''
dirList = os.listdir(workFolder)
analysisCounter = 1

for file in dirList:
    filename = os.fsdecode(file)
    if filename.endswith(".musicxml")== False: continue
    
    #if filename != "011.musicxml": continue
    print ("Analyzing file : " + str(filename) + " " + str(analysisCounter)) 
    work = converter.parse('%s%s' %(workFolderString, filename)) # forceSource= True 
    
    
     
    ''' metadata '''  
    
    onto.zarlinoModality(modelPath, work)
    
    onto.writeOntologyToFile("/Users/christophe/Documents/ontologies/ontologies/analysisOntologyCopy.rdf")
    
    
    #print (workClassInstance)



