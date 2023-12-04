'''
Created on Mar 17, 2020

@author: christophe
'''
## keras: 2.4.3
## tensorflow: 2.3.0


import rootAnalysis, os, pitchCollections
 

from music21 import converter
from tensorflow import keras
import tensorflow as tf
from normalizeScore import ScoreNormalization


if __name__ == '__main__':
    pass
        
''' set paths '''
directoryName=os.path.dirname
rootDirectoryName = directoryName(directoryName(directoryName(__file__)))

#workDirectoryString = '/Users/christophe/Dropbox/WTBach/'
#outputDirectoryString = '/Users/christophe/Dropbox/HarmonisationsBach/analyseModèle/'

workDirectoryString = '/Users/christophe/Documents/Chostakovitch/'
outputDirectoryString = '/Users/christophe/Documents/Chostakovitch/roots/'

modelPath = '/Users/christophe/Documents/GitHub/PolyMIR/models/rootModel16072020.h5'
rootModel = keras.models.load_model(modelPath)
rootModel.compile(optimizer="adam",  loss='sparse_categorical_crossentropy',metrics=['accuracy'])
#rootModel.compile(optimizer=tf.train.AdamOptimizer(), loss='sparse_categorical_crossentropy', metrics=['accuracy'])
rootModel.summary()

 

for file in os.listdir(workDirectoryString):
    fileName = os.fsdecode(file)
    if fileName.endswith(".musicxml")== False: continue
    
    print ("Analyzing file " + fileName)

    workPath = workDirectoryString + fileName 
    
    work = converter.parse(workPath)
    
    #scoreNorm = ScoreNormalization(work)
    
    #work = scoreNorm.normalizePartNames()
 
    
    
    ''' create PirtchCollectionSequencesObject '''
    pitchCollectionSequence = pitchCollections.PitchCollectionSequence(work) 
    
    
    ''' add root information '''
    rootAnal = rootAnalysis.RootAnalysis(pitchCollectionSequence)
    #rootAnal.analyzeWithModel(rootModel)
    #rootAnal.modelScores()
    
    
    ''' add stream with roots to score '''
    bassStream = rootAnal.getFundamentalBass()
    work.insert(0, bassStream)
    work.write('musicxml', outputDirectoryString + fileName)
    
    ''' print everything to xml file '''
                 
        