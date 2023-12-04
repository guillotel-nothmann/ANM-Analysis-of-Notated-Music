import rootAnalysis, os, pitchCollections
 

from music21 import converter 
from normalizeScore import ScoreNormalization


if __name__ == '__main__':
    pass
        
''' set paths '''
directoryName=os.path.dirname
rootDirectoryName = directoryName(directoryName(directoryName(__file__)))

#workDirectoryString = '/Users/christophe/Dropbox/WTBach/'
#outputDirectoryString = '/Users/christophe/Dropbox/HarmonisationsBach/analyseModèle/'

workDirectoryString = '/Users/christophe/Dropbox/exemplesZarlino/Analyses/musicXML/'
outputDirectoryString = '/Users/christophe/Dropbox/exemplesZarlino/Analyses/musicXML/normalizeds'

 
 

for file in os.listdir(workDirectoryString):
    fileName = os.fsdecode(file)
    if fileName.endswith(".mxl")== False: continue
     
    print ("Analyzing file " + fileName)

    workPath = workDirectoryString + fileName 
    work = converter.parse(workPath)
    
    scoreNorm = ScoreNormalization(work)
    
    work = scoreNorm.normalizePartNames()
    
    work = scoreNorm.addTimeSignaturesWhereNeeded()
    work = scoreNorm.resetMeasureOffsets()
    
    
    
    work.write('musicxml', outputDirectoryString + fileName)
    