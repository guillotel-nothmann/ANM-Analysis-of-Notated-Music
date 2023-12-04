print("\n1. importer music21 et autres modules")
from music21 import converter, clef, key, meter, note , roman
from nltk import ngrams


print ("\n2. importer une partition")
partition = converter.parse("/Users/christophe/Documents/Praetorius/Terpsichore/xml/001.musicxml")


print ("\n3. Visualiser la partition")

partition.show(app="MuseScore 3") ### représentation dans MuseScore 3

 
print ("\n4. Identifier les parties et leurs propriétés")
for part in partition.parts:
    print (f"\t {part.partName} {part.partAbbreviation} {part.id} {part.duration}")
    
    
    for partClef in part.recurse().getElementsByClass(clef.Clef):
        print (f"\t Clé: {partClef} {partClef.measureNumber}")
        
    for partKey in part.recurse().getElementsByClass(key.Key):
        print (f"\t Armure: {partKey} {partKey.measureNumber}")
          
        
    print ("\n5. Identifier les ambitus")  
    ambitus = part.analyze("ambitus")   
    print (f"\t Ambitus: {ambitus.directedNiceName}, Note inférieure: {ambitus.noteStart}, Note supérieure: {ambitus.noteEnd}")
    

print ("\n6. Identifier toutes les classes de hauteurs et compter les sol3 (G4)")  
cantusPart = partition.parts["C."]
noteList = [] ### liste pour l'ensemble des notes
G4List = [] ### liste pour les sol4

for note in cantusPart.recurse().getElementsByClass (note.Note): #itérer
    noteList.append(note) # ajouter les notes à la liste
    
    if note.nameWithOctave == "G4":
        G4List.append(note)
        
print (f"Nombre de notes: {str(len(noteList))} Nombre de sol4: {str(len(G4List))} pourcentage sol4: {str(len(G4List)/len(noteList))}%")

cantusPart.plot('histogram', 'pitch')# histogramm de toutes les hauteurs

for note in G4List:
    print (f"Note sol3 à la mesure : {note.measureNumber} temps: {note.beat}")
    

print ("\n7. Identifier la formule G4-F#4-G4 au cantus et l'afficher en rouge dans la partition") 
triGrams = ngrams(noteList, 3) ### créer des trigrammes
patternList = [] ### créer une liste de patterns

for triGram in triGrams: ### analyser l'ensemble des trigrammes
    if triGram[0].nameWithOctave=="G4" and triGram[1].nameWithOctave=="F#4" and triGram[2].nameWithOctave== "G4":
        patternList.append (triGram)
        

for pattern in patternList: ### afficher les patterns
    print (f"Début du pattern: {pattern[0].measureNumber}, {pattern[0].beat} – fin du pattern: {pattern[2].measureNumber}, {pattern[2].beat} ")

    pattern[0].style.color="red"
    pattern[1].style.color="red"
    pattern[2].style.color="red"    
partition.show(app="MuseScore 3")


print ("\n8. Faire une réduction harmonique et l'afficher") 
reductionHarmonique = partition.chordify()
partition.insert(0, reductionHarmonique)
#partition.show(app="MuseScore 3")

for c in reductionHarmonique.recurse().getElementsByClass('Chord'):
    c.closedPosition(forceOctave=4, inPlace=True)
partition.show(app="MuseScore 3")

print ("\n9. Réaliser un chiffrage harmonique et l'afficher")
### identifier statistiquement la tonalité
tonalite = partition.analyze('Krumhansl')
 
### assigner un chiffrage
for c in reductionHarmonique.recurse().getElementsByClass('Chord'): ### itérer
    rn = roman.romanNumeralFromChord(c, tonalite) ### assigner un chiffre romain en raison d'une tonalité
    c.addLyric(str(rn.figure))
partition.show(app="MuseScore 3")
    
    
 
 

      
    






