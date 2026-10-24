# custom_compiler

Assembler, Disassembler und (im Aufbau) Compiler für eine selbst entworfene 8-Bit-CPU mit 16-Bit-Befehlswort, dazu der Hardware-Entwurf in Logisim.

Das Projekt wurde zusammen mit einem Schulkameraden begonnen: Die Hardware (Logisim) stammt von ihm, der Software-Teil (Assembler, Compiler) ist hier weitergeführt.

## Stand

| Teil | Stand |
|---|---|
| Assembler / Disassembler | funktioniert; Assemblieren → Disassemblieren → Assemblieren ergibt dieselbe Binärdatei |
| Befehlssatz | Version 1.0, siehe [docs/isa.md](docs/isa.md) (Tabellen: [docs/isa_plan.xlsx](docs/isa_plan.xlsx)) |
| Compiler | Grundgerüst: Token-Definitionen und Lexer; Parser und weitere Stufen sind geplant ([docs/compiler-plan.md](docs/compiler-plan.md)) |
| Hardware | unfertiger Entwurf ([docs/hardware.md](docs/hardware.md)) |

## Benutzung

Python ≥ 3.9 (getestet mit 3.12), Abhängigkeit: PyYAML.

```bash
pip install -r requirements.txt

python assembler/assembler.py examples/example.asm example.bin      # assemblieren
python assembler/disassembler.py example.bin example_dis.asm        # zurück in Text
```

Syntax in Kurzform (Details in [docs/isa.md](docs/isa.md)):

```
IMV 20 D          # Wert 20 nach D
ADD D RAM         # A + D -> RAM[HI:LO]
INC A LO; JNC     # A + 1 -> LO, danach bedingter Sprung nach HI:LO
```

Lexer:

```python
from compiler.lexer.lexer import Lexer
tokens = Lexer("x = 1 + 2\n", "demo").tokenize()
```

## Struktur

```
assembler/    Assembler, Disassembler, instructions.yaml
compiler/     Compiler-Gerüst (bisher lexer/)
examples/     Beispielprogramm für den Assembler
hardware/     Logisim-Entwurf (aktuell + ältere Variante)
docs/         ISA, Hardware, Compiler-Plan, Sprachentwurf, Glossar, Historie, Skizzen
```

Dokumentation: [ISA](docs/isa.md) · [Hardware](docs/hardware.md) · [Compiler-Plan](docs/compiler-plan.md) · [Sprachentwurf](docs/language-draft.md) · [Glossar](docs/glossar.md) · [Historie](docs/history.md)

## Lizenz

[MIT](LICENSE) für Code und Dokumentation (Matthrose). Die Rechte am Hardware-Entwurf in `hardware/` liegen bei seinem Urheber, siehe [hardware/README.md](hardware/README.md).
