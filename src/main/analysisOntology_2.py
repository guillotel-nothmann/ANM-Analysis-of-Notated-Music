'''
Created on Mar 3, 2021

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
import ontology



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
    workClassInstance = onto.workClass()
    workClassInstance.hasFileName = [str(filename)]
    workClassInstance.hasComposer = [str(work.metadata.composer)] 
    workClassInstance.hasTitle = [str(work.metadata.title)] 
    workClassInstance.hasMeasureNumber = [int(work.finalBarline[0].measureNumber)]
    
    
    onto.addInstanceToTripleStore(workClassInstance)
    
    
    