# Glossar

Abkürzungen und Fachbegriffe, die im Projekt vorkommen. Codes und Tabellen: [isa.md](isa.md).

## Befehlssatz und Assembler

| Begriff | Bedeutung |
|---|---|
| ISA | Instruction Set Architecture: Befehlssatz einer CPU samt Codierung |
| Opcode | Teil des Befehlswortes, der die Operation festlegt (hier das Feld `alu`) |
| Operand | Wert oder Register, mit dem ein Befehl rechnet |
| Immediate (`IMV`) | Wert, der direkt im Befehlswort steht (8 Bit) |
| Mnemonic | Kurzname eines Befehls (`ADD`, `JMP`) |
| Label | Name einer Programmstelle, Sprungziel |
| Assembler / Disassembler | Assembler-Text → Maschinencode / Maschinencode → Assembler-Text |
| Big-Endian | höherwertiges Byte zuerst |
| `CMP` | Compare: Vergleich durch Subtraktion ohne Ziel, nur die Flags zählen |
| `ADC` / `SBC` | Add / Subtract with Carry: Addition bzw. Subtraktion mit Übertrag, für 16-Bit-Rechnung aus zwei 8-Bit-Schritten (reserviert, Hardware fehlt) |
| `SHL` / `SHR` | Schieben nach links / rechts (arithmetisch: ASHL / ASHR, Vorzeichen bleibt beim Rechtsschieben erhalten) |
| `hold` / `%` | Bit 7 im Befehlswort: Flags nicht aktualisieren; im Assembler das Präfix `%` |
| Aktion | Befehl ohne Zielregister: `NOP`, `SYNC`, `HOLD`, `RESET` |
| `SYNC` | Aktion zum Synchronisieren der Bildschirmausgabe (Plan: `SCREEN_SYNC`) |
| `HOLD` | Aktion: Takt anhalten (Plan: `HOLD_CLOCK`); nicht dasselbe wie das Bit `hold` |

## Register und Speicher

| Begriff | Bedeutung |
|---|---|
| `A` | Akkumulator, erster Operand jeder ALU-Operation |
| `D` | Datenregister |
| `LO`, `HI` | Low- und High-Byte; `HI:LO` ist RAM-Adresse und Sprungziel |
| `SP`, `SPL`, `SPH` | Stackpointer (Position im Stack), Low- und High-Teil |
| `FR` | Flag-Register: Flags und Statusbits der Ein-/Ausgabe |
| `IN` / `OUT` | Eingabequelle (Tastatur, Timer) / serielle Ausgabe |
| PC | Program Counter: Adresse des nächsten Befehls |
| ROM / RAM | Programmspeicher / Datenspeicher (hier 8K × 8 Bit, SRAM) |
| Stack / Heap | Stapelspeicher für Rücksprünge und lokale Daten / Bereich für dynamisch angeforderte Daten |
| Flag | Statusbit nach einer ALU-Operation |
| `Z`, `N`, `C`, `V` | Zero (Ergebnis 0), Negative (höchstes Bit 1), Carry (Übertrag), Overflow (Vorzeichenüberlauf, Ergebnis passt nicht in −128…127) |
| Signed / unsigned | mit / ohne Vorzeichen gelesene Zahl |
| Zweierkomplement | übliche Darstellung negativer ganzer Zahlen |

## Hardware

| Begriff | Bedeutung |
|---|---|
| ALU | Arithmetic Logic Unit, Rechenwerk |
| Decoder | zerlegt das Befehlswort in Steuerfelder |
| Logisim(-evolution) | Programm zum Entwerfen und Simulieren digitaler Schaltungen (`.circ`) |
| TTL / 74xx | Familie von Standard-Logikbausteinen |
| 74377 | 8-Bit-Register mit Freigabe |
| 74240 / 74244 | Tri-State-Inverter / -Buffer |
| 74161 | 4-Bit-Zähler |
| 74138 | Decoder 3 zu 8 |
| 74164 / 74165 | Schieberegister SIPO / PISO |
| SIPO / PISO | Serial-In-Parallel-Out / Parallel-In-Serial-Out |
| Tri-State | Ausgang mit drittem Zustand „hochohmig“, vom Bus getrennt |
| Bus | gemeinsame Datenleitung mehrerer Bausteine |
| 555 / Monoflop | Timer-Baustein / Schaltung, die nach einem Impuls genau einen Puls erzeugt |
| Takt (Clock) | Signal, das den Ablauf der CPU steuert |

## Compiler

| Begriff | Bedeutung |
|---|---|
| Lexer / Token | zerlegt Text in Tokens / kleinste Einheit des Quelltextes (Schlüsselwort, Zahl, Operator) |
| Parser | erzeugt aus Tokens einen Syntaxbaum |
| Recursive Descent | Parser-Verfahren: eine Funktion pro Grammatikregel, die sich rekursiv aufruft |
| AST | Abstract Syntax Tree, Baumdarstellung des Programms |
| Symboltabelle / Scope | Verzeichnis aller Namen mit Typ / Gültigkeitsbereich eines Namens |
| Makro | Textbaustein, der beim Übersetzen durch Befehle ersetzt wird |
| IR / TAC | Intermediate Representation, Zwischendarstellung / Three-Address Code: höchstens drei Adressen je Zeile |
| Konstantenfaltung | Rechnen mit Konstanten schon beim Übersetzen |
| Linker / Merger | führt mehrere Teile zu einem Programm zusammen |
| Debug-Dump | optionale Ausgabe eines Zwischenstands zur Fehlersuche |
