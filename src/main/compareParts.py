'''
Created on Aug 27, 2020

Show which parts are identical, show which parts are not within a stream
'''

import os
import pandas as pd

from music21 import converter, stream, note, chord, clef, meter
from reduction.compareParts import CompareParts
from music21.stream import Measure
from music21.instrument import Bass

 
    
    


def getListFromDictionary(dataDictionary, dictionaryKey):
    
    if dictionaryKey not in dataDictionary:
        dataDictionary[dictionaryKey] = []

    
    return dataDictionary[dictionaryKey]


if __name__ == '__main__':
    pass

workDirectoryString = '/Users/christophe/Dropbox/Praetorius/Polyhymnia/Source/normalized/'
workBookPath = '/Users/christophe/Dropbox/Praetorius/Polyhymnia/ambitus.xlsx'
scorePath = '/Users/christophe/Dropbox/Praetorius/Polyhymnia/ambitusScore.musicxml'

structuralPartsDictionary = {}

scoreStream = stream.Score() 

cantusStream = stream.Stream()
altusStream = stream.Stream()
tenorStream = stream.Stream()
bassusStream = stream.Stream()


cantusStream.name = "Cantus"
altusStream.name = "Altus"
tenorStream.name = "Tenor"
bassusStream.name = "Bassus"

cantusStream.append(meter.TimeSignature("4/4"))
altusStream.append(meter.TimeSignature("4/4"))

tenorStream.append(clef.Treble8vbClef())
tenorStream.append (meter.TimeSignature("4/4"))


bassusStream.append(clef.BassClef())
bassusStream.append(meter.TimeSignature("4/4"))

streamDictionary = {"Cantus": cantusStream, "Altus": altusStream, "Tenor": tenorStream, "Bassus": bassusStream}



for file in sorted(os.listdir(workDirectoryString)):
    fileName = os.fsdecode(file)
    if fileName.endswith(".musicxml")== False: continue
    
    print (fileName)

    
    workPath = workDirectoryString + fileName 
    workStream = converter.parse(workPath)
    
    
    partsComp = CompareParts(workStream, ignoreInst=False)
    #dataDictionary = partsComp.show()
    ambitusDictionary = partsComp.getAmbitusDictionary()
    getListFromDictionary(structuralPartsDictionary, "fileName").append(fileName)
    
    for partName in ["Cantus", "Altus", "Tenor", "Bassus"]:
        
        partStream = streamDictionary[partName]
        measureStream = measure = Measure()
        
        voiceHighStream = stream.Voice()
        voiceLowStream = stream.Voice()
        
        voiceHighStream.id = 0
        voiceLowStream.id = 1
        
        
        if partName in ambitusDictionary:
            ambitusLow = ambitusDictionary[partName]["low"] 
            ambitusHigh = ambitusDictionary[partName]["high"]
            interval = ambitusDictionary[partName]["interval"]
            
            if ambitusLow != None:
                noteAmbitusLow = note.Note(ambitusLow)
            else: 
                noteAmbitusLow = note.Rest()
                
            if ambitusHigh != None: 
                noteAmbitusHigh = note.Note(ambitusHigh)
            else:
                noteAmbitusHigh = note.Rest() 
            
        else:
            ambitusLow = ""
            ambitusHigh = ""
            interval = ""
            
            noteAmbitusLow = note.Rest()
            noteAmbitusHigh = note.Rest()
            
            
        noteAmbitusLow.duration.quarterLength = 4
        noteAmbitusHigh.duration.quarterLength = 4
            
        voiceLowStream.append(noteAmbitusLow)
        voiceHighStream.append(noteAmbitusHigh) 
        
        if partName == "Bassus":
            noteAmbitusHigh.lyric = fileName.replace(".musicxml", "")
        
       
        partStream.append(measureStream)
        
        measureStream.insert(measureStream.offset, voiceLowStream)
        measureStream.insert(measureStream.offset, voiceHighStream)
       
         
     
    
        getListFromDictionary(structuralPartsDictionary, partName + "_" + "low" ).append(ambitusLow)
        getListFromDictionary(structuralPartsDictionary, partName + "_" + "high" ).append(ambitusHigh)
        getListFromDictionary(structuralPartsDictionary, partName + "_" + "interval" ).append(interval)
    
    
for elementKey, element in   streamDictionary.items():
    scoreStream.insert(0, element)  


scoreStream.write("musicxml", scorePath)
 
    
    #df = pd.DataFrame(data=dataDictionary)
    #df.to_excel(workBookPath)  
    
df = pd.DataFrame(data=structuralPartsDictionary)
df.to_excel(workBookPath) 
    