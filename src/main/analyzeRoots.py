'''
Created on Mar 17, 2020

@author: christophe
'''
import rootAnalysis, os, pitchCollections
from music21 import converter
from tensorflow import keras
import tensorflow as tf

if __name__ == '__main__':
    pass
        
''' set paths '''
directoryName=os.path.dirname
rootDirectoryName = directoryName(directoryName(directoryName(__file__)))

#workDirectoryString = '/Users/christophe/Dropbox/WTBach/'
#outputDirectoryString = '/Users/christophe/Dropbox/HarmonisationsBach/analyseModèle/'

workDirectoryString = '/Users/christophe/Documents/GitHub/BachChorals//xmlToBeAnalyzed/'
outputDirectoryString = '/Users/christophe/Documents/GitHub/BachChorals/xmlWithRoot/'

modelPath = '/Users/christophe/Documents/GitHub/PolyMIR/models/rootModelBach_06052020.h5'
rootModel = keras.models.load_model(modelPath)
rootModel.compile(optimizer=tf.train.AdamOptimizer(), loss='sparse_categorical_crossentropy', metrics=['accuracy'])
rootModel.summary()



for file in os.listdir(workDirectoryString):
    fileName = os.fsdecode(file)
    if fileName.endswith(".musicxml")== False: continue
    
    print ("Analyzing file " + fileName)

    workPath = workDirectoryString + fileName 
    work = converter.parse(workPath)
    
    
    ''' create PirtchCollectionSequencesObject '''
    pitchCollectionSequences = pitchCollections.PitchCollectionSequences(work) 
    
    
    ''' add root information '''
    rootAnal = rootAnalysis.RootAnalysis(pitchCollectionSequences)
    rootAnal.analyzeWithModel(rootModel)
    rootAnal.modelScores()
    
    
    ''' add stream with roots to score '''
    bassStream = rootAnal.getFundamentalBass()
    work.insert(0, bassStream)
    work.write('musicxml', outputDirectoryString + fileName)
    
    ''' print everything to xml file '''
                 
        