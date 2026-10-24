# Entwicklungsgeschichte

Das Projekt entstand in mehreren Anläufen. Die Hardware (Logisim) stammt von einem Schulkameraden, Assembler und Compiler sind der Software-Teil.

## Versionen

| Version | Inhalt |
|---|---|
| v1 | eine Datei (94 Zeilen): Datei lesen, einfacher Assembler, Tokenizer-Ansatz |
| v2 | eine Datei (289 Zeilen): Klasse `Compiler`, Text → Binärdatei |
| v3 | eine Datei (339 Zeilen): `Utils`, `Compiler`, `StructureHandler` |
| v4 | aufgeteilt in Module: `main`, `translator`, `structureHandler`, `utils`, `assembler`, `config.yaml` |
| v5 | Paket `structure_handler` (`extractor`, `tree_builder`, `datatypes`, `resolver`), eigener Ordner für Assembler / Disassembler |
| v6 | wie v5, mit erweiterten `datatypes` und Platzhaltern für Lexer und Parser |
| v7 | Paketstruktur `compiler/` mit den geplanten Stufen (lexer, parser, analyser, transformator, ir_generator, optimizer, asm_generator, assembler, errors), neue Token-Definitionen, handgeschriebener Lexer; die meisten Stufen noch leer |

Die Versionen sind als Tags `v1` bis `v7` abrufbar. Jede Version ist ein vollständiger Snapshot, der nachträglich als Commit angelegt wurde.

Der Stand auf `main` ist v7, aufgeräumt (siehe unten). Befehlsformat und Tabellen folgen `isa_plan.xlsx`; ältere Entwürfe liegen in `docs/archive/` und `hardware/archive/`.

## Änderungen beim Aufräumen von v7

Code

- `assembler/`
  - Aufruf über die Kommandozeile; der fest eingetragene Testlauf am Dateiende entfällt
  - Ausgabedatei muss nicht mehr vorher existieren
  - Parameter `instrruction_mappings_path` → `instruction_mappings_path`, Docstring `JNE` → `JNZ`
  - **Bit 7 (`hold`) wie im Plan:** `%` hält die Flags (kein Flag-Update), ohne `%` werden sie aktualisiert. Vorher war es umgekehrt, dadurch ändert sich die Binärausgabe gegenüber v7.
- `assembler/disassembler.py`
  - Dekorator `@NotImplementedError` entfernt
  - Quelle `000` wird als Platzhalter (`D`, bei Ein-Operand-Befehlen `A`) ausgegeben, damit die Ausgabe wieder dieselbe Binärdatei ergibt
- `assembler/instructions.yaml`: nur Kommentare ergänzt
- `compiler/lexer/lexer.py` ist die frühere Datei `lexer_regex(old).py` (der eigentliche Lexer); der nicht auflösbare Import `ErrorBag` entfällt. Die frühere `lexer.py` enthielt nur Imports.

Dateien

- `input.txt` → `examples/example.asm`
- `input_Main.txt`, `dok`, `compiler_v7/docs/basics.md` → `docs/language-draft.md`
- `plan_1.xlsx` → `docs/isa_plan.xlsx`, `plan.xlsx` → `docs/archive/isa_plan_v0.xlsx`
- `computer__2_.circ` → `hardware/computer.circ`, `computer__1_.circ` → `hardware/archive/computer_v0.circ`
- nicht übernommen: leere v7-Ordner und -Dateien, erzeugte Dateien (`output.*`, `intermediate.asm`, `temp.txt`, `binaer.txt`, `disassembled.txt`), eine nicht zum Projekt gehörende Testdatei, `__pycache__`, Editor-Erweiterungen
