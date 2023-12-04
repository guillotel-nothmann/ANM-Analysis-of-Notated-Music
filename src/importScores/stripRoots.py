'''
Created on Nov 1, 2022

@author: christophe

used to import Bach chorals with roots and strip the root part '''

import os
from music21 import converter


if __name__ == '__main__':
    pass

workWithRootDirectoryString = '/Users/christophe/Dropbox/HarmonisationsBach/MEIWithoutRoots/'
workDirectoryString = '/Users/christophe/Dropbox/HarmonisationsBach/MusicXMLWithoutRoots/'


for file in os.listdir(workWithRootDirectoryString):
    fileName = os.fsdecode(file)
    if fileName.endswith(".mei")== False: continue
     
    print ("File " + fileName)

    workPath = workWithRootDirectoryString + fileName 
    work = converter.parse(workPath)
    

    
    
    
    for element in work.elements: 
        if not hasattr(element, "partName"): continue
        
        element.name = element.partName
        
        if element.partName == "Root":
            work.pop(work.elements.index(element))
            
    
    work.write('musicxml', workDirectoryString + fileName)
    
    
    