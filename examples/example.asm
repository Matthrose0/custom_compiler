# Beispielprogramm fuer den Assembler (Syntax: siehe docs/isa.md)
# Ausfuehren: python assembler/assembler.py examples/example.asm example.bin

IMV x00 LO # 0 in LO laden
IMV x00 HI # 0 in HI laden
IMV 20 D  # 20 in D laden
IMV 42 A  # 42 in A laden
ADD D RAM  # A + D -> RAM @ #0000
MOV LO A   # LO byte nach A kopieren
MOV HI D   # HI byte nach D kopieren um platz für den jump pointer zu machen
IMV 13 LO # 13 in LO laden
IMV x00 HI # 0 in HI laden
INC A LO; JNC # A erhöhen und in LO speichern- kommenden teil überspringen wenn kein carry
MOV D A    # D nach A kopieren (wert von HI)
INC A HI     # A erhöhen und in HI speichern
IMV 99 RAM # 99 in RAM @ #0001 speichern
MOV RAM SPH # RAM wert in SPH zwischenspeichern
MOV LO A   # LO byte nach A kopieren
MOV HI D   # HI byte nach D kopieren um platz für den jump pointer zu machen
IMV 21 LO # 21 in LO laden
IMV x00 HI # HI nullen

DEC A LO; JNC # LO dekrementieren

MOV D A    # D nach A kopieren (wert von HI)
DEC A HI     # A dekrementieren und in HI speichern
MOV SPH A # wert aus SPH nach A kopieren
OR RAM OUT # A | RAM ausgeben in out
IMV 26 LO # endlosschleife
IMV x00 HI
JMP
