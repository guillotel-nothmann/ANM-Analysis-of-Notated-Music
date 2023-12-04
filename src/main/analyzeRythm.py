'''
Created on Jul 4, 2021

@author: christophe
'''

from music21 import converter, interval, dynamics, articulations
from music21.tree.timespanTree import TimespanTree
from music21 import tree, note, chord 

if __name__ == '__main__':
    pass

workPath = '/Users/christophe/Documents/IReMus/équipeAnalyse/espace Interprétation/Psalms/SYMPHONY_OF_PSALMS_corr_III.musicxml'

work = converter.parse(workPath)
soundingPitchWork = work.toSoundingPitch() 
scoreTree = tree.fromStream.asTimespans(soundingPitchWork, flatten=True, classList=(note.Note, chord.Chord))

currentMeasure = 1

attacksPerUnitList = []
attacks= 0

''' create measure span dictionary '''
explorationWindow = 2


measureDict = {} #[measure, attaques, [classes de hauteurs], ]

filterInstGroup = []

woodFilter = ["Picc.", "Fl. 1 2", "Fl. 3 4", "Fl. 5", "Fl. 4", "Ob. 1 2", "Ob. 3 4", "E. Hn.", "Bsn. 1", "Bsn. 2 3", "Bsn. 3", "Cbsn."]
brassFilter = ["F Hn. 1 2", "F Hn. 3 4", "D Tpt.", "C Tpt. 1 2", "C Tpt. 2", "C Tpt. 3 4", "T. Tbn. 1 2", "T. Tbn.", "B. Tbn. 3", "Tba."]
percussionFilter = ["Timp.", "B. Dr."]
voiceFilter = ["S.", "A.", "T.", "B."]
pianoHarpFilter = ["Hrp.", "Pno. 1 2", "Pno. 2"]
stringFilter = ["Vc. Solo", "Vcs.", "Cb. Solo", "Cbs"]

instrumentDictionary = {
    "Picc.":0, "Fl. 1 2":0, "Fl. 3 4":0, "Fl. 5":0, "Fl. 4":0, "Ob. 1 2":0, "Ob. 3 4":0, "E. Hn.":0, "Bsn. 1":0, "Bsn. 2 3":0, "Bsn. 3":0, "Cbsn.":0,
    "F Hn. 1 2":1, "F Hn. 3 4":1, "D Tpt.":1, "C Tpt. 1 2":1, "C Tpt. 2":1, "C Tpt. 3 4":1, "T. Tbn. 1 2":1, "T. Tbn.":1, "B. Tbn. 3":1, "Tba.":1,
    "Timp.":2, "B. Dr.":2,
    "S.":3, "A.":3, "T.":3, "B.":3,
    "Hrp.":4, "Pno. 1 2":4, "Pno. 2":4,
    "Vc. Solo":5, "Vcs.":5, "Cb. Solo":5, "Cbs.":5
    }
 
 


for part in work.parts:
    print (part.partAbbreviation)


for verticality in scoreTree.iterateVerticalities():
    
    if verticality.measureNumber not in measureDict: measureDict[verticality.measureNumber]= [0, 0, [], 0, [], 0, 0,  0, 0, 0, 0, 0, 0] #7-12 are instrument families
    
    ''' attacks '''  #  all attacks, simultaneous or not 
    instrumentFamiliesAttacks = [0, 0, 0, 0, 0, 0] 
    totalAttacks = 0
    
    
    for element in verticality.startTimespans:
        if isinstance(element.element, chord.Chord):
            totalAttacks = totalAttacks + len(element.pitches)
            instrumentFamiliesAttacks[instrumentDictionary [element.part.partAbbreviation]] = instrumentFamiliesAttacks[instrumentDictionary [element.part.partAbbreviation]] + len(element.pitches)
            
            
            
            
        elif isinstance (element.element, note.Note):
            totalAttacks = totalAttacks + 1
            instrumentFamiliesAttacks[instrumentDictionary [element.part.partAbbreviation]] = instrumentFamiliesAttacks[instrumentDictionary [element.part.partAbbreviation]] + 1
            
         

    
    measureDict[verticality.measureNumber][0] = measureDict[verticality.measureNumber][0] + totalAttacks
    
    ''' verticalities ''' # verticalites all successive attacks 
    measureDict[verticality.measureNumber][1] = measureDict[verticality.measureNumber][1] + 1
    
    for counter, result in enumerate(instrumentFamiliesAttacks):
        measureDict[verticality.measureNumber][counter + 7] = measureDict[verticality.measureNumber][counter + 7] + result
        
    
    
    
    ''' pitch classes '''
    
    pitchClasses = measureDict[verticality.measureNumber][2]
    
    for pitchClass in verticality.pitchClassSet:
        
        
        if not pitchClass.name in pitchClasses: pitchClasses.append (pitchClass.name)
        
    ''' dissonances '''
    consonantIntervals = 0
    dissonantIntervals = 0
    
    for pitchA in verticality.pitchClassSet:
        for pitchB in verticality.pitchClassSet:
            if id(pitchA) == id(pitchB):continue
            inter = interval.Interval(pitchA, pitchB)
            
            if inter.chromatic.simpleUndirected in [0, 3, 4, 7, 8, 9]: # careful with the fourth 
                consonantIntervals = consonantIntervals + 1
            elif inter.chromatic.simpleUndirected in [1, 2, 6, 10, 11]:
                dissonantIntervals = dissonantIntervals + 1
            elif inter.chromatic.simpleUndirected in [5]: 
                continue
            
            else: 
                print ("Cannot assign interval")
            
    measureDict[verticality.measureNumber][3] = measureDict[verticality.measureNumber][3]+  dissonantIntervals

''' dynamics '''
for dynam in work.recurse().getElementsByClass(dynamics.Dynamic):
    if dynam.measureNumber == 70: continue
    if dynam._value not in measureDict[dynam.measureNumber][4]: measureDict[dynam.measureNumber][4].append(dynam._value)


''' articulations'''
for element in work.recurse().getElementsByClass([chord.Chord, note.Note]):
    if len (element.articulations) != 0:
        for articulation in element.articulations:
            if articulation.name == "accent" :
                measureDict[element.measureNumber][5] = measureDict[element.measureNumber][5] + 1
            
            elif articulation.name == "staccato" :
                measureDict[element.measureNumber][6] = measureDict[element.measureNumber][6] + 1
                
                 
print ("mesure" + "\t" + "attaques" + "\t" + "verticalités" + "\t" + "classes de hauteurs", "\t" + "dissonances" + "\t" + "dynamiques" + "\t" + "accent" + "\t" + "staccato" + "\t" + "attaques bois" + "\t" + "attaques cuivres" + "\t" + "attaques percu" + "\t" + "attaques voix" + "\t" + "attaques piano harpe"  + "\t" + "attaques cordes")    

for key, value in measureDict.items():
    print (str(key) + "\t" + str(value[0]) + "\t" + str (value[1]) + "\t" + str (sorted (value[2])) + "\t"  +  str (value[3]) + "\t" + str(value[4]) + "\t" + str(value[5]) + "\t" + str(value[6]) + "\t" + str(value[7])+  "\t" + str(value[8])  +"\t" + str(value[9])+ "\t" + str(value[10])+ "\t" + str(value[11])+ "\t" + str(value[12]))
    #print ( str (sorted (value[1])))

