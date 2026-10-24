# Sprachentwurf

Skizze der geplanten Hochsprache, nichts davon ist umgesetzt. Neuere Planung: [compiler-plan.md](compiler-plan.md).

## Grundregeln

- maximale Zeilenlänge 110 Zeichen
- keine String-Interpolation

## Syntax-Skizze

```
CONST NAME VALUE
LABEL L_NAME
FUNC NAME(ARGS*):
    IF(REG1 VERGLEICHS_OP REG2):
        ...
    ELIF(...):
        ...
    ELSE:
        ...
    return A

MACRO NAME(ARGS*):
    ...
NAME(ARGS*)                 # ruft Funktion oder Makro auf
REPEAT(NUMBER):
    ...
WHILE(REG1 VERGLEICHS_OP REG2):
    ...
```

Zuweisungen mit jeweils höchstens einer ALU-Operation pro Zeile:

```
A = D + RAM

A = D
A = A + RAM
```

## Notizen

- Zahlenformate: dezimal −128…+127, hexadezimal `0`…`0xff`, binär `0b…`
- Mehr als eine Operation pro Zeile braucht freie Arbeitsregister. Ist das Arbeitsregister `D` statt `A`, kann ein unbemerkter Fehler entstehen, weil `D` nicht jede Operation wie `A` ausführen kann.
- Auswertung von links nach rechts
- Bedingungen: `0` = false, `0xff` (−1) = true
- Makros und Funktionen können in eigenen Units liegen; manche Makros haben Anwendungsbedingungen (z. B. `return`)
- eingebaute Makros für Strukturen (Schleifen, Funktionen, Bedingungen)
- beim Ersetzen von Namen Leerzeichen auf beiden Seiten setzen, damit keine Wortteile ersetzt werden
- Struktur-Handler: nach der Zerlegung auf leere Strukturen prüfen (Warnung, dann entfernen)
- Idee: `wait`-Befehl als Makro, um Instruktionen abzuwarten
- Frage: zu vielen Makros eine „unsafe“-Variante, die das hohe Register ignoriert (Performance)
- bei Rechnungen mit Labels ist keine Vereinfachung möglich

Älterer Ablauf der Übersetzung:

1. Makro- und Funktionsdefinitionen trennen, alles als Baum aufteilen
2. Imports der höchsten Ebene auflösen
3. Strukturen von innen nach außen in höheres ASM umwandeln (mit Makros)
4. Imports von niedrigem ASM einbinden
5. Hauptparser wandelt höheres in niedriges ASM um
6. Assembler erzeugt die Binärdatei
