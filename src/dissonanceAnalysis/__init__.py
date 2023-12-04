
import numpy as np
import tensorflow as tf
from tensorflow import keras


### requires tensforflow 1.6 (unsure => check)
### keras==2.1.3  (unsure => check)

class DissonanceAnalysis ():

    def __init__(self, pitchCollSequence):
        
        
        self.algorithmId = "dissonanceAnalysis03042021"
        self.pitchCollSequence = pitchCollSequence
        #self.featuresPath = 'dissonanceNeuralNetwork/observations.npy' 
        #self.labelsPath = 'dissonanceNeuralNetwork/labels.npy'
        self.modelPath = '/Users/christophe/Documents/GitHub/PolyMIR/models/dissonanceModel.h5'
        
        ''' run model '''
        #self.features = np.load(self.featuresPath)
        #self.labels = np.load(self.labelsPath)
        self.new_model = keras.models.load_model(self.modelPath)
        self.new_model.compile(optimizer="adam",  loss='sparse_categorical_crossentropy',metrics=['accuracy'])
        self.new_model.summary()
        
        #unused_loss, acc = self.new_model.evaluate(self.features, self.labels)
        #print("Restored model, accuracy: {:5.2f}%".format(100 * acc))
    
        self.analyzeWithModel()
        
    
    
    
    def analyzeWithModel (self):
        
        ''' loop over all analyzed pitches '''
  
        
        for pitchCollection in self.pitchCollSequence.explainedPitchCollectionList:
            ''' loop over all analyzed pitches '''
            for analyzedPitch in pitchCollection.analyzedPitchList:
                
                ''' get observation list and put it in array '''                
                
                observationArray = np.array(self.pitchCollSequence.getObservationsForPitchId(analyzedPitch.id, 5, pitchCollection.offset))
                feature = np.array([observationArray])
                            
                ''' make prediction from observation list '''
                predictions = self.new_model.predict(feature)
                
                ''' get highest score identifiy index '''
                highestScore = max(predictions[0]) 
                for index in range (0, len(predictions[0])):
                    if predictions[0][index] == highestScore:
                        break
                
                labelDict = {0:"CN", 1:"PN", 2:"NN", 3:"AN", 4:"SU", 5:"AP", 6:"PE", 7:"EN"}
                print ("prediction: " + labelDict[index] + " score: " + str(highestScore))
                
                analyzedPitch.pitchType = labelDict[index]
                analyzedPitch.probability = highestScore
