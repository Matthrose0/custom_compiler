# compiler

Gerüst des Compilers (Hochsprache → Assembler). Stand und Plan: [../docs/compiler-plan.md](../docs/compiler-plan.md).

| Pfad | Inhalt |
|---|---|
| `lexer/token.py` | Token-Typen, Schlüsselwörter, `Token`, `TokenStream` |
| `lexer/lexer.py` | Lexer: Quelltext → Tokenliste (Einrückung als `INDENT` / `DEDENT`, `LexerError`) |

`token.py` enthält außerdem Datentypen des früheren Struktur-Handlers (`Structure`, `Instruction`, …), die noch nicht in eigene Module verteilt sind.
