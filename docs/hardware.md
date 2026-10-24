# Hardware

Entwurf in [`../hardware/computer.circ`](../hardware/computer.circ) (Logisim-evolution 3.9.0), noch unfertig. Befehlscodierung: [isa.md](isa.md). Urheberschaft: [../hardware/README.md](../hardware/README.md).

## Aufbau

```
ProgramCounter ──► ROM ──► DecoderUnit
      ▲                       │ selector, save/Ziel, alu, immediate
      │ Sprung (HI:LO)        ▼
      │                  RegisterBank ──► Operand A, B ──► ALU ──► Ergebnis ──► RegisterBank
      │                                                     │
      └──────────── ConditionUnit ◄──── Flags (Z, N, C, V) ◄┘
```

| Baugruppe | Aufgabe |
|---|---|
| `ProgramCounter` | 16 Bit, 4 × 74161; Sprung über `HI:LO` |
| ROM | 16-Bit-Adresse, 16-Bit-Befehl |
| `DecoderUnit` | zerlegt das Befehlswort in `jump`, `save`, `action`, `immediate`, `byte`, `alu`, `selector` |
| `RegisterBank` | `LO`, `HI`, `SPL`, `SPH`, `A`, `D` (6 × 74377), Auswahl über 74138, dazu RAM, Timer, serielle Ein-/Ausgabe |
| `synced_RAM` | 8K×8-SRAM (AS7C164A), 13-Bit-Adresse; Kommentare in der Schaltung zum Timing des Bausteins |
| `ALU` | 8 Bit, aus ICs (74244, 74240, 7486, 74138) und Addierer; Flags `Z`, `N`, `C`, `V`; der Immediate-Wert läuft durch die ALU |
| `ConditionUnit` | Flag-Register (74377), Sprungbedingung, zusätzlich InputReady / OutputReady |
| `KeyboardDriver` | Tastatureingang |
| `MatrixController_16p`, `DotMatrix` | Anzeige (eine Dot-Matrix) |
| `serialise_8`, `deserialise_8` / `_16` | serielle Ausgabe (`OUT`) und Eingabe (`IN`) |
| `hw_timer` | Timer (laut Schaltung ein 555-Monoflop) |

Hilfsschaltungen: `overflow`, `ic_tests`.

## ToDo

- **MIN / MAX** (`1100`, `1101`) sind in der ALU noch nicht gebaut, im Befehlssatz aber vorgesehen
- **ADC / SBC** (`1110`, `1111`): Carry-Eingang des Addierers fehlt noch

## Bauteile

Planwerte aus `isa_plan.xlsx` (Blatt „Parts“): 74377 Register (10), AS7C164A-15PCN RAM (2), 74240 (10), 74244 (10), 7486 XOR (3), 74161 Zähler (20), 74165 PISO (10), 74164 SIPO (10), BC 547C (500), außerdem 7420, 7402, 7427, 7410 und 74138.

## Skizzen und ältere Variante

- [Skizzen Blatt 1](images/hardware_plan_1.jpeg), [Blatt 2](images/hardware_plan_2.jpeg)
- `hardware/archive/computer_v0.circ`: älteres Befehlsformat (Mode-Bit 15, 4-Bit-Felder für Operanden und Bedingung, nur ein Stackpointer), Tabellen in `archive/isa_plan_v0.xlsx`; passt nicht zum Assembler
