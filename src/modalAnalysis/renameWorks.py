'''
Created on Feb 18, 2020

@author: christophe
'''

import xml.etree.ElementTree as ET

if __name__ == '__main__':
    pass

''' loop over text file '''
textFilePath =  '/Users/christophe/Documents/GitHub/PraetoriusTerpsichore/fileNamesComposers.txt'
xmlFilePath = '/Users/christophe/Documents/GitHub/PraetoriusTerpsichore/xml/'
newXMLFilPath = '/Users/christophe/Documents/GitHub/PraetoriusTerpsichore/tests/'


with open(textFilePath, encoding="utf-8") as file_in:
    lines = []
    for line in file_in:
        
        ''' get file name and select file accordingly '''
        fileName, composer = line.split("\t")
        
        ''' parse file '''
        tree = ET.parse(xmlFilePath + fileName)  
        root = tree.getroot()
        ''' check if creator @ type composer exists, if so change value according to composer, if not add information ''' 
        hasCreator = False
        
        
        for creator in root.findall("./identification/creator"):
            hasCreator = True
            creator.text = composer
            tree.write (newXMLFilPath + fileName)
        
        if hasCreator == True: continue
        "... if not add information"
        
        for indentification in root.findall ("identification"):
            new=ET.Element('creator')
            new.text= composer
            new.set("type", "composer")
            indentification.insert(0,new)
            tree.write (newXMLFilPath + fileName)



''' add composer name to file '''

