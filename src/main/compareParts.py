'''
Created on Aug 27, 2020

Show which parts are identical, show which parts are not within a stream
'''

import os
import pandas as pd

from music21 import converter
from reduction.compareParts import CompareParts

if __name__ == '__main__':
    pass

workDirectoryString = '/Users/christophe/Dropbox/Praetorius/Polyhymnia/Source/tests/'
workBookPath = '/Users/christophe/Dropbox/Praetorius/Polyhymnia/comparision.xlsx'

for file in os.listdir(workDirectoryString):
    fileName = os.fsdecode(file)
    if fileName.endswith(".musicxml")== False: continue
    

    
    workPath = workDirectoryString + fileName 
    workStream = converter.parse(workPath)
    
    
    partsComp = CompareParts(workStream)
    dataDictionary = partsComp.show()
    
 
    
    df = pd.DataFrame(data=dataDictionary)
    df.to_excel(workBookPath)  
    