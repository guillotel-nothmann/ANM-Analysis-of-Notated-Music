'''
Created on Mar 3, 2021

@author: christophe
'''
 
import os
from music21 import converter 
   
#from networkx.classes.function import degree  
from datetime import datetime
#from django.contrib.messages.api import success
from owlready2 import get_ontology, Thing, ObjectProperty, DataProperty
import types
import ontology

from dissonanceAnalysis import DissonanceAnalysis



if __name__ == '__main__':
    pass
now = datetime.now()
dt_string = now.strftime("%d%m%Y_%H%M")


directroyString = '/Users/christophe/Dropbox/Praetorius/Polyhymnia/Source/ontologyTest/'
ontologyName = '/Users/christophe/Dropbox/Praetorius/Polyhymnia/results/' + dt_string + '.rdf'
directory = os.fsencode(directroyString)

onto = ontology.AnalysisOntology()

''' get data '''
dirList = os.listdir(directory)
analysisCounter = 1

pitchCollSequ = onto.getPitchCollSequence("pYkeh6Bw")


dissonanceAnal=DissonanceAnalysis(pitchCollSequ)


print (pitchCollSequ)


for file in dirList:
    filename = os.fsdecode(file)
    if filename.endswith(".mei")== False: continue
    
    #if filename != "011.musicxml": continue
    print ("Analyzing file : " + str(filename) + " " + str(analysisCounter)) 
    work = converter.parse('%s%s' %(directroyString, filename), forceSource= True)  
    ''' metadata ''' 
    workClassInstance = onto.createWorkInstance(work)
    
    ''' pitch analysis '''
    pitchAnalysisInstance = onto.createPitchAnalysisInstance(work)
    workClassInstance.hasPitchAnalysis.append(pitchAnalysisInstance)
    #onto.addInstanceToTripleStore(workClassInstance)
    
    workList = onto.addInstanceToTripleStore(workClassInstance)
    
    
    