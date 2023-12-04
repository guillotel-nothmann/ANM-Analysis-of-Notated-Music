'''
Created on Oct 18, 2022

@author: christophe
'''

''' used to import a) a score and b) an excel folder with root information '''
''' the information is added to the score if possible (roots on an extra staff, dissonance patterns are linked to the note, etc.)'''


if __name__ == '__main__':
    pass


def getListFromDictionary(dataDictionary, dictionaryKey):
    
    if dictionaryKey not in dataDictionary:
        dataDictionary[dictionaryKey] = []
        
    return dataDictionary[dictionaryKey]
        

if __name__ == '__main__':
    pass

workWithRootDirectoryString = '/Users/christophe/Documents/Chostakovitch/noRoots/'
workDirectoryString = '/Users/christophe/Documents/Chostakovitch/roots/'
workBookPath = '/Users/christophe/Documents/Chostakovitch/rootsAndVectors_2.xlsx'


''' load score '''

''' load excel worksheet '''

''' get root information and add it to the score ''' 