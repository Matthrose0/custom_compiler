# Befehlssatz (ISA)

Stand: Version 1.0, kann sich noch ändern. Die Tabellen mit allen Codes stehen in [`isa_plan.xlsx`](isa_plan.xlsx) (maßgeblich) und in [`../assembler/instructions.yaml`](../assembler/instructions.yaml) (vom Assembler verwendet). Hier steht nur das Konzept; Begriffe im [Glossar](glossar.md).

## Grundlagen

- Befehlswort 16 Bit (im ROM 2 Byte, Big-Endian), Datenpfad 8 Bit
- ROM: 16-Bit-Adresse; RAM: 8K × 8 Bit (13-Bit-Adresse)
- `HI:LO` ist die RAM-Adresse und das Sprungziel
- Stackpointer aus zwei Registern, `SPL` und `SPH`
- Flags: `Z`, `N`, `C`, `V`
- Jede Rechnung ist `A op B`: Operand `A` ist immer das Register `A`, `B` ist das per `src` gewählte zweite Register. `A` kann nicht als `B` gewählt werden (Code `000` = `D`).

## Bit-Layout

| Bits | 15–13 | 12 | 11–9 | 8 | 7 | 6–3 | 2–0 |
|---|---|---|---|---|---|---|---|
| Standard (`imm` = 0) | `jump` | `save` | Ziel / Aktion | 0 | `hold` | `alu` | `src` |
| Immediate (`imm` = 1) | `jump` | `save` | Ziel | 1 | Wert, Bits 7–0 | | |

- `save` = 1: Ergebnis wird in das Zielregister geschrieben; `save` = 0: Bits 11–9 sind eine Aktion
- `hold` = 1: Flags bleiben unverändert (kein Flag-Update); Assembler-Präfix `%`. Nicht zu verwechseln mit der Aktion `HOLD` (Takt anhalten).

## Befehle im Überblick

| Gruppe | Mnemonics |
|---|---|
| ALU | `CPY` `MOV` `SHR` `SHL` `AND` `OR` `XOR` `NOT` `ADD` `INC` `SUB` `DEC` `MIN` `MAX` (Codes `1110` / `1111` reserviert, geplant: `ADC`, `SBC`) |
| Sprung | `JZ` `JN` `JC` `JNZ` `JNN` `JNC` `JMP` (Ziel: `HI:LO`) |
| Ziel | `D` `LO` `HI` `RAM` `A` `SPL` `SPH` `OUT` |
| Quelle (`B`) | `D` `LO` `HI` `RAM` `IN` `SPL` `SPH` `FR` |
| Aktion | `NOP` `SYNC` `HOLD` `RESET` |

- `CPY` = `A`, `MOV` = `B`; `SHR` / `SHL` verschieben `A` arithmetisch; `NOT`, `INC`, `DEC` wirken nur auf `A`. Bei diesen Operationen mit einem Operanden wird `src` ignoriert, im Assembler steht dafür der Platzhalter `A`.
- Vergleich (`CMP`): `SUB` ohne Ziel, es zählen nur die Flags.
- `IN` liest über eine 3-Bit-Eingabeadresse: Tastatur (`000`), Timer low (`001`), Timer high (`011`); die übrigen Adressen sind frei.

## Assembler-Syntax

```
[%]OP [SRC] [DST][; SPRUNG]
IMV WERT DST[; SPRUNG]
JMP
NOP
```

- `#` beginnt einen Kommentar; Groß-/Kleinschreibung ist egal
- `OP src dst` rechnet `A op src` und schreibt nach `dst`
- `IMV`-Werte: dezimal `0`–`255`, hexadezimal `x1A`, binär `b101`; negative Zahlen übernimmt später der Compiler
- ein 16-Bit-Sprungziel entsteht aus zwei `IMV` (`LO`, `HI`), danach folgt der Sprung

```
ADD D RAM         # A + D -> RAM[HI:LO]
MOV LO A          # LO -> A
OR RAM OUT        # A | RAM -> serielle Ausgabe
%ADD D LO         # A + D -> LO, Flags bleiben erhalten (hold)
SUB D             # Vergleich: nur Flags, kein Ziel
```

## Noch nicht geklärt

- Flag-Auswertung bei Sprüngen: Flags des aktuellen oder des vorherigen Befehls?
- Woher die 3-Bit-Eingabeadresse bei `IN` kommt; Idee: niedrige 3 Bit von `LO`
- Bitbelegung des Flag-Registers `FR` (enthält laut Schaltung auch InputReady / OutputReady)
- Signed-Vergleiche: `V` ist vorhanden, aber alle 8 Sprungcodes sind belegt. Idee: im Compiler beide Werte mit `0x80` XOR-en und wie unsigned vergleichen.

Hardware-ToDos: siehe [hardware.md](hardware.md).
