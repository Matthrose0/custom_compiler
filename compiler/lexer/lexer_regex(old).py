from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Final, Any,Iterator
 
from compiler.lexer.token import TOKEN_TYPE as TT, Token, KEYWORDS
from compiler.errors.errors import LexerError, ErrorBag


###### MEHRZEILIGE LEXER-FUNCTIONS ???? keine mehrzeiligen Kommentare, strings,...
# -> wie mach ich die?

# =================================================================================================
#  RULES for tokenization
#  Rules are in order of priority (komplex to simple cause they are matched first)
# =================================================================================================
_RULES: list[tuple[TT | None, re.Pattern[str]]] = [r for r in [                     # type: ignore
    (None, re.compile(r'[ \t]+')),                  # whitespaces
    (TT.COMMENT, re.compile(r'#[^\n]*')),

    # ____Literal_values___________________________________________________________________________
    (TT.STRING, re.compile(r'"(?:[^"\\\r\n]|\\.)*"')),  # "..." -> escaped chars are allowed
    (TT.STRING, re.compile(r"'(?:[^'\\]|\\.)*'")),  # '...'

    (TT.CHAR,   re.compile(r'\"[^\"]\"')),          # "a"
    (TT.CHAR,   re.compile(r'\'[^\']\'')),          # 'a'
    
    # float before int -> float has higher priority
    (TT.FLOAT,  re.compile(r'\d+\.\d+')),           # 1.2
    (TT.INT,    re.compile(r'\d+')),                # 1
    # true/false/None are matched with keywords
    
    # ____Multiple_character_Operators_____________________________________________________________
    (TT.INTDIV, re.compile(r'//')),                 # //
    (TT.POW,    re.compile(r'\*\*')),               # **
    (TT.INC,    re.compile(r'\+\+')),               # ++
    (TT.DEC,    re.compile(r'--')),                 # --

    # bitwise
    (TT.LSHIFT, re.compile(r'<<')),                 # <<
    (TT.RSHIFT, re.compile(r'>>')),                 # >>

    # comparison
    (TT.LE,     re.compile(r'<=')),                 # <=
    (TT.GE,     re.compile(r'>=')),                 # >=
    (TT.EQ,     re.compile(r'==')),                 # ==
    (TT.NE,     re.compile(r'!=')),                 # !=

    # logocal
    (TT.AND,    re.compile(r'&&')),                 # &&
    (TT.OR,     re.compile(r'\|\|')),               # ||
    (TT.NE,     re.compile(r'!=')),                 # !=

    # other
    (TT.ARROW,  re.compile(r'->')),                 # ->
    (TT.WALRUS, re.compile(r':=')),                 # :=
    
    # ____Assignments______________________________________________________________________________
    (TT.ADD_ASSIGN, re.compile(r'\+=')),            # +=
    (TT.SUB_ASSIGN, re.compile(r'-=')),             # -=
    (TT.POW_ASSIGN, re.compile(r'\*\*=')),          # **=
    (TT.MUL_ASSIGN, re.compile(r'\*=')),            # *=
    (TT.DIV_ASSIGN, re.compile(r'/=')),             # /=
    (TT.ASSIGN, re.compile(r'=')),                  # =

    # ____Single_character_Operators_______________________________________________________________
    (TT.ADD,    re.compile(r'\+')),                 # +
    (TT.MINUS,  re.compile(r'-')),                  # -
    (TT.MUL,    re.compile(r'\*')),                 # *
    (TT.DIV,    re.compile(r'/')),                  # /
    (TT.MOD,    re.compile(r'%')),                  # %

    # bitwise
    (TT.BIT_AND, re.compile(r'&')),                 # &
    (TT.BIT_OR, re.compile(r'\|')),                 # |
    (TT.BIT_XOR, re.compile(r'\^')),                # ^
    (TT.NOT,    re.compile(r'~')),                  # ~

    # comparison
    (TT.LT,     re.compile(r'<')),                  # <
    (TT.GT,     re.compile(r'>')),                  # >

    # ____Delimiters_______________________________________________________________________________
    (TT.LPAREN, re.compile(r'\(')),                 # (
    (TT.RPAREN, re.compile(r'\)')),                 # )
    (TT.LBRACKET, re.compile(r'\[')),               # [
    (TT.RBRACKET, re.compile(r'\]')),               # ]
    (TT.LBRACE, re.compile(r'\{')),                 # {
    (TT.RBRACE, re.compile(r'\}')),                 # }
    (TT.COMMA,  re.compile(r',')),                  # ,
    (TT.DOT,    re.compile(r'\.')),                 # .
    (TT.COLON,  re.compile(r':')),                  # :
    (TT.SEMICOLON, re.compile(r';')),               # ;
    (TT.AT,     re.compile(r'@')),                  # @
    
    

    # ____Identifiers______________________________________________________________________________
    (TT.IDENT,  re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*')),
    
    (TT.NEWLINE, re.compile(r'\n')),                # \n





] if r is not None]












# ══════════════════════════════════════════════════════════════════════════════
#  COMPILED REGEX PATTERNS
#  Used only inside number-scanning helpers to keep the char-by-char loop clean.
# ══════════════════════════════════════════════════════════════════════════════
 
_RE_DEC: Final = re.compile(r"[0-9]+")
_RE_HEX: Final = re.compile(r"[0-9a-fA-F]+")
_RE_BIN: Final = re.compile(r"[01]+")
 
 
# ══════════════════════════════════════════════════════════════════════════════
#  CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════
 
_WHITESPACE: Final[frozenset[str]] = frozenset({" ", "\t", "\r"})
 
_IDENT_START: Final[frozenset[str]] = frozenset(
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ_"
)
_IDENT_CONT: Final[frozenset[str]] = _IDENT_START | frozenset("0123456789")
 
# Characters whose token type is fixed — no lookahead required.
_SINGLE: Final[dict[str, TT]] = {
    "(": TT.LPAREN,   ")": TT.RPAREN,
    "[": TT.LBRACKET, "]": TT.RBRACKET,
    "{": TT.LBRACE,   "}": TT.RBRACE,
    ",": TT.COMMA,    ".": TT.DOT,
    ";": TT.SEMICOLON,"@": TT.AT,
    "^": TT.BIT_XOR,  "~": TT.BIT_NOT,
    "%": TT.MOD,
}
 
# Known escape sequences inside strings / char literals.
_ESCAPES: Final[dict[str, str]] = {
    "n": "\n", "t": "\t", "r": "\r",
    "\\": "\\", '"': '"', "'": "'",
    "0": "\0", "a": "\a", "b": "\b",
}
 
# Token types that suppress an extra NEWLINE immediately before them.
_NO_NEWLINE_BEFORE: Final[frozenset[TT]] = frozenset({
    TT.NEWLINE, TT.INDENT, TT.DEDENT, TT.COMMENT,
})

# =============================================================================
#  Lexer-Error
# =============================================================================
@dataclass
class LexerError(Exception):
    """Structured lexer error with source location and pretty-print method."""
 
    message:  str
    file:     str
    line:     int
    col:      int
    src_line: str = ""
 
    def pretty(self) -> str:
        pointer = " " * (self.col - 1) + "^"
        return (
            f"LexerError: {self.message}\n"
            f" --> {self.file}:{self.line}:{self.col}\n"
            f"  {self.line} | {self.src_line}\n"
            f"    | {pointer}"
        )
 
    def __str__(self) -> str:
        return self.pretty()

# =============================================================================
#  Lexer
# =============================================================================
class Lexer:
    """
    Tokenizes a single source-file into a flat list[Token].
 
    Usage:
        tokens = Lexer(source, file_path="main.xl").tokenize()
    """
    def __init__(self, source: str, file_path: str = "<input>") -> None:
        self._src:    str       = source
        self._file:   str       = file_path
        self._lines:  list[str] = source.splitlines()
        self._len:    int       = len(source)
 
        # current position
        self._pos:        int = 0   # byte index into _src
        self._line:       int = 1   # 1-based line number
        self._col:        int = 1   # 1-based column number
        self._line_start: int = 0   # _pos at start of current line
 
        # indentation tracking
        self._indent_stack:  list[int] = [0]
        self._at_line_start: bool      = True
 
        self._tokens: list[Token] = []

    def tokenize(self) -> list[Token]:
        """Scan the entire source and return the complete token list."""
        while not self._at_end():
            self._scan_next()
        self._flush_dedents()
        self._emit(TT.EOF, "", self._line, self._col)
        return self._tokens

    # ── Main dispatch ─────────────────────────────────────────────────────────
    def _scan_next(self) -> None:
        """Process one token (or whitespace/newline) at the current position."""
        if self._at_line_start:
            self._scan_indent()
            self._at_line_start = False
 
        if self._at_end():
            return
 
        ch = self._advance()
 
        if ch in _WHITESPACE:
            return
        if ch == "\n":
            self._handle_newline()
            return
        if ch == "#":
            self._scan_comment()
            return
        if ch == '"':
            self._scan_string_dquote()
            return
        if ch == "'":
            self._scan_squote()
            return
        if ch.isdigit():
            self._scan_number(ch)
            return
        if ch in _IDENT_START:
            self._scan_ident(ch)
            return
        self._scan_operator(ch)
 
    # ── Newline & Indentation ─────────────────────────────────────────────────
 
    def _handle_newline(self) -> None:
        """Emit NEWLINE (unless redundant) and enable indent scanning."""
        last = self._tokens[-1].type if self._tokens else None
        if last not in _NO_NEWLINE_BEFORE:
            self._emit(TT.NEWLINE, "\n", self._line - 1, self._col)
        self._at_line_start = True
 
    def _scan_indent(self) -> None:
        """
        Measure leading whitespace and emit INDENT / DEDENT tokens.
        Blank lines and comment-only lines are skipped entirely.
        """
        depth = 0
        while not self._at_end() and self._src[self._pos] in (" ", "\t"):
            depth += 1
            self._advance()
 
        # Blank line or comment-only line — don't change indent level.
        if self._at_end() or self._src[self._pos] in ("\n", "#"):
            return
 
        current = self._indent_stack[-1]
 
        if depth > current:
            self._indent_stack.append(depth)
            self._emit(TT.INDENT, "", self._line, 1)
            return
 
        if depth < current:
            self._pop_indents_to(depth)
 
    def _pop_indents_to(self, target: int) -> None:
        """Emit DEDENT tokens until the indent stack reaches `target`."""
        while self._indent_stack[-1] > target:
            self._indent_stack.pop()
            self._emit(TT.DEDENT, "", self._line, 1)
 
        if self._indent_stack[-1] != target:
            raise self._error(
                f"Indentation error: level {target} does not match "
                f"any open block (stack: {self._indent_stack})"
            )
 
    def _flush_dedents(self) -> None:
        """Close all remaining open indent blocks at end-of-file."""
        while self._indent_stack[-1] > 0:
            self._indent_stack.pop()
            self._emit(TT.DEDENT, "", self._line, self._col)
 
    # ── Comments ──────────────────────────────────────────────────────────────
 
    def _scan_comment(self) -> None:
        """Consume from '#' to end-of-line and emit a COMMENT token."""
        sc  = self._col - 1
        buf = "#"
        while not self._at_end() and self._peek() != "\n":
            buf += self._advance()
        self._emit(TT.COMMENT, buf, self._line, sc)
 
    # ── Strings ───────────────────────────────────────────────────────────────
 
    def _scan_string_dquote(self) -> None:
        """
        Double-quoted string: either a regular "..." or a multiline \"\"\"...\"\"\".
        Escape sequences are supported in both forms.
        """
        # Triple-quote check: first '"' already consumed, peek two more.
        if self._peek() == '"' and self._peek(1) == '"':
            self._advance()   # consume 2nd "
            self._advance()   # consume 3rd "
            self._scan_triple('"')
            return
        self._scan_single_line_string('"')
 
    def _scan_squote(self) -> None:
        """
        Single-quoted: either a char literal 'x' or a multiline '''...'''.
        Triple single-quote → STRING.  Single char / escape → CHAR.
        """
        if self._peek() == "'" and self._peek(1) == "'":
            self._advance()
            self._advance()
            self._scan_triple("'")
            return
        self._scan_char_literal()
 
    def _scan_single_line_string(self, quote: str) -> None:
        """Scan a regular single-line string delimited by `quote`."""
        open_line, open_col = self._line, self._col - 1
        buf: list[str] = []
 
        while not self._at_end():
            ch = self._advance()
 
            if ch == "\n":
                raise self._unclosed_string(open_line, open_col)
            if ch == "\\":
                buf.append(self._read_escape())
                continue
            if ch == quote:
                self._emit(TT.STRING, "".join(buf), self._line, open_col)
                return
            buf.append(ch)
 
        raise self._unclosed_string(open_line, open_col)
 
    def _scan_triple(self, quote: str) -> None:
        """
        Scan a triple-quoted multiline string (either \"\"\"...\"\"\" or '''...''').
        Ends at the matching triple-quote sequence.
        """
        open_line, open_col = self._line, self._col - 3
        buf: list[str] = []
 
        while not self._at_end():
            ch = self._advance()
 
            if ch == "\\":
                buf.append(self._read_escape())
                continue
            if ch == quote and self._peek() == quote and self._peek(1) == quote:
                self._advance()   # 2nd closing quote
                self._advance()   # 3rd closing quote
                self._emit(TT.STRING, "".join(buf), open_line, open_col)
                return
            buf.append(ch)
 
        raise LexerError(
            f"Unclosed triple-quoted string (opened at line {open_line})",
            self._file, open_line, open_col, self._get_src_line(open_line),
        )
 
    def _scan_char_literal(self) -> None:
        """
        Scan a char literal: 'x' or '\\n'.
        Exactly one character (or escape sequence) between the single quotes.
        """
        open_col = self._col - 1
 
        if self._at_end() or self._peek() == "\n":
            raise self._error("Empty character literal")
 
        value = self._read_escape() if self._peek() == "\\" else self._advance()
 
        if self._at_end() or self._peek() != "'":
            raise self._error(
                "Character literal must contain exactly one character"
            )
        self._advance()   # closing '
        self._emit(TT.CHAR, value, self._line, open_col)
 
    def _read_escape(self) -> str:
        """
        Consume one escape sequence; the leading backslash was already consumed.
        Supported:  \\n  \\t  \\r  \\\\  \\"  \\'  \\0  \\a  \\b  \\xHH  \\uHHHH
        """
        if self._at_end():
            raise self._error("Unexpected end of file in escape sequence")
 
        esc = self._advance()
 
        if esc in _ESCAPES:
            return _ESCAPES[esc]
        if esc == "x":
            return chr(int(self._read_hex_digits(2), 16))
        if esc == "u":
            return chr(int(self._read_hex_digits(4), 16))
 
        raise self._error(f"Unknown escape sequence '\\{esc}'")
 
    def _read_hex_digits(self, count: int) -> str:
        """Read exactly `count` hex digits; raise on unexpected char or EOF."""
        digits = ""
        for _ in range(count):
            if self._at_end() or self._peek() not in "0123456789abcdefABCDEF":
                raise self._error(f"Expected {count} hex digits, got {self._peek()!r}")
            digits += self._advance()
        return digits
 
    # ── Numbers ───────────────────────────────────────────────────────────────
 
    def _scan_number(self, first: str) -> None:
        """
        Dispatch to the right number scanner based on prefix.
        0x… → hex  |  0b… → binary  |  0o… → octal  |  else → decimal/float
        """
        sc = self._col - 1
 
        if first != "0" or self._at_end():
            self._scan_decimal(first, sc)
            return
 
        prefix = self._peek()
 
        if prefix in ("x", "X"):
            self._advance()
            self._scan_based_int("0x", _RE_HEX, sc)
        elif prefix in ("b", "B"):
            self._advance()
            self._scan_based_int("0b", _RE_BIN, sc)
        elif prefix in ("o", "O"):
            self._advance()
            self._scan_based_int("0o", _RE_OCT, sc)
        else:
            self._scan_decimal(first, sc)
 
    def _scan_based_int(
        self, prefix: str, pattern: re.Pattern[str], sc: int
    ) -> None:
        """Match `pattern` at the current position and emit an INT token."""
        m = pattern.match(self._src, self._pos)
        if not m:
            raise self._error(f"Expected digits after '{prefix}'")
        self._advance_by(len(m.group()))
        self._emit(TT.INT, prefix + m.group(), self._line, sc)
 
    def _scan_decimal(self, first: str, sc: int) -> None:
        """
        Scan a decimal INT or FLOAT, including scientific notation.
        Uses regex to collect digit runs; branching logic stays in Python.
        """
        # Integer part (first digit already consumed)
        rest = self._read_regex(_RE_DEC)
        buf  = first + rest
 
        has_frac = False
        has_exp  = False
 
        # Fractional part: only if '.' is followed by a digit
        if self._peek() == "." and self._peek(1).isdigit():
            has_frac = True
            buf += "." + self._advance()   # consume '.'
            buf += self._read_regex(_RE_DEC)
 
        # Exponent part: e  or  E  optionally followed by +/-
        if self._peek() in ("e", "E"):
            has_exp = True
            buf    += self._advance()   # e / E
            if self._peek() in ("+", "-"):
                buf += self._advance()
            exp_digits = self._read_regex(_RE_DEC)
            if not exp_digits:
                raise self._error("Expected digits after exponent marker")
            buf += exp_digits
 
        tt = TT.FLOAT if (has_frac or has_exp) else TT.INT
        self._emit(tt, buf, self._line, sc)
 
    # ── Identifiers & keywords ────────────────────────────────────────────────
 
    def _scan_ident(self, first: str) -> None:
        """
        Collect identifier characters, then look up the result in KEYWORDS.
        Keywords get their specific token type; everything else → IDENT.
        """
        sc  = self._col - 1
        buf = first
        while not self._at_end() and self._peek() in _IDENT_CONT:
            buf += self._advance()
        self._emit(KEYWORDS.get(buf, TT.IDENT), buf, self._line, sc)
 
    # ── Operators & delimiters ────────────────────────────────────────────────
 
    def _scan_operator(self, ch: str) -> None:
        """
        Emit operator / delimiter tokens.
        Characters in _SINGLE need no lookahead.
        Everything else is routed through _OP_DISPATCH (defined after the class).
        """
        sc = self._col - 1
 
        if ch in _SINGLE:
            self._emit(_SINGLE[ch], ch, self._line, sc)
            return
 
        handler = _OP_DISPATCH.get(ch)
        if handler is None:
            raise self._error(f"Unexpected character {ch!r}")
        handler(self, sc)
 
    # Individual operator methods — one method per leading character ───────────
 
    def _op_plus(self, sc: int) -> None:                  # +  +=  ++
        if self._match("+"):    self._emit(TT.INC,        "++", self._line, sc)
        elif self._match("="): self._emit(TT.ADD_ASSIGN,  "+=", self._line, sc)
        else:                   self._emit(TT.ADD,         "+",  self._line, sc)
 
    def _op_minus(self, sc: int) -> None:                 # -  -=  --  ->
        if self._match(">"):    self._emit(TT.ARROW,      "->", self._line, sc)
        elif self._match("-"): self._emit(TT.DEC,         "--", self._line, sc)
        elif self._match("="): self._emit(TT.SUB_ASSIGN,  "-=", self._line, sc)
        else:                   self._emit(TT.SUB,         "-",  self._line, sc)
 
    def _op_star(self, sc: int) -> None:                  # *  *=  **  **=
        if self._peek() != "*":
            tt = TT.MUL_ASSIGN if self._match("=") else TT.MUL
            self._emit(tt, "*=" if tt is TT.MUL_ASSIGN else "*", self._line, sc)
            return
        self._advance()   # consume second '*'
        tt  = TT.POW_ASSIGN if self._match("=") else TT.POW
        val = "**=" if tt is TT.POW_ASSIGN else "**"
        self._emit(tt, val, self._line, sc)
 
    def _op_slash(self, sc: int) -> None:                 # /  /=  //
        if self._match("/"):    self._emit(TT.INTDIV,     "//", self._line, sc)
        elif self._match("="): self._emit(TT.DIV_ASSIGN,  "/=", self._line, sc)
        else:                   self._emit(TT.DIV,         "/",  self._line, sc)
 
    def _op_eq(self, sc: int) -> None:                    # =  ==
        tt = TT.EQ if self._match("=") else TT.ASSIGN
        self._emit(tt, "==" if tt is TT.EQ else "=", self._line, sc)
 
    def _op_bang(self, sc: int) -> None:                  # !  !=
        tt = TT.NE if self._match("=") else TT.NOT
        self._emit(tt, "!=" if tt is TT.NE else "!", self._line, sc)
 
    def _op_lt(self, sc: int) -> None:                    # <  <=  <<
        if self._match("<"):    self._emit(TT.LSHIFT, "<<", self._line, sc)
        elif self._match("="): self._emit(TT.LE,      "<=", self._line, sc)
        else:                   self._emit(TT.LT,      "<",  self._line, sc)
 
    def _op_gt(self, sc: int) -> None:                    # >  >=  >>
        if self._match(">"):    self._emit(TT.RSHIFT, ">>", self._line, sc)
        elif self._match("="): self._emit(TT.GE,      ">=", self._line, sc)
        else:                   self._emit(TT.GT,      ">",  self._line, sc)
 
    def _op_amp(self, sc: int) -> None:                   # &  &&
        tt = TT.AND if self._match("&") else TT.BIT_AND
        self._emit(tt, "&&" if tt is TT.AND else "&", self._line, sc)
 
    def _op_pipe(self, sc: int) -> None:                  # |  ||
        tt = TT.OR if self._match("|") else TT.BIT_OR
        self._emit(tt, "||" if tt is TT.OR else "|", self._line, sc)
 
    def _op_colon(self, sc: int) -> None:                 # :  :=
        tt = TT.WALRUS if self._match("=") else TT.COLON
        self._emit(tt, ":=" if tt is TT.WALRUS else ":", self._line, sc)
 
    # ── Low-level helpers ─────────────────────────────────────────────────────
 
    def _at_end(self) -> bool:
        return self._pos >= self._len
 
    def _peek(self, offset: int = 0) -> str:
        """Return char at current + offset without consuming. '' if out of range."""
        idx = self._pos + offset
        return self._src[idx] if idx < self._len else ""
 
    def _advance(self) -> str:
        """Consume and return the current character, updating line/col tracking."""
        ch = self._src[self._pos]
        self._pos += 1
        if ch == "\n":
            self._line       += 1
            self._col         = 1
            self._line_start  = self._pos
        else:
            self._col += 1
        return ch
 
    def _advance_by(self, count: int) -> None:
        """Advance `count` characters (assumed non-newline, e.g. digit runs)."""
        self._pos += count
        self._col += count
 
    def _match(self, expected: str) -> bool:
        """Consume and return True only if the current char equals `expected`."""
        if self._at_end() or self._src[self._pos] != expected:
            return False
        self._advance()
        return True
 
    def _read_regex(self, pattern: re.Pattern[str]) -> str:
        """
        Try to match `pattern` at the current position.
        Advance by the match length and return the matched text ('' if no match).
        """
        m = pattern.match(self._src, self._pos)
        if not m:
            return ""
        self._advance_by(len(m.group()))
        return m.group()
 
    def _emit(self, tt: TT, value: str, line: int, col: int) -> None:
        """Append a Token to the output list."""
        self._tokens.append(Token(
            type    = tt,
            value   = value,
            line    = line,
            col     = col,
            col_end = col + len(value),
            file    = self._file,
        ))
 
    def _get_src_line(self, line_num: int) -> str:
        """Return the raw source text for `line_num` (1-based), or ''."""
        return self._lines[line_num - 1] if 1 <= line_num <= len(self._lines) else ""
 
    def _unclosed_string(self, open_line: int, open_col: int) -> LexerError:
        return LexerError(
            f"Unclosed string (opened at line {open_line})",
            self._file, open_line, open_col,
            self._get_src_line(open_line),
        )
 
    def _error(self, message: str) -> LexerError:
        return LexerError(
            message  = message,
            file     = self._file,
            line     = self._line,
            col      = self._col,
            src_line = self._get_src_line(self._line),
        )

# ══════════════════════════════════════════════════════════════════════════════
#  OPERATOR DISPATCH TABLE
#  Defined after Lexer so we can reference its bound methods directly.
#  Maps a leading character to the method that handles all its variants.
# ══════════════════════════════════════════════════════════════════════════════
 
_OpHandler = Callable[["Lexer", int], None]
 
_OP_DISPATCH: Final[dict[str, _OpHandler]] = {
    "+": Lexer._op_plus,
    "-": Lexer._op_minus,
    "*": Lexer._op_star,
    "/": Lexer._op_slash,
    "=": Lexer._op_eq,
    "!": Lexer._op_bang,
    "<": Lexer._op_lt,
    ">": Lexer._op_gt,
    "&": Lexer._op_amp,
    "|": Lexer._op_pipe,
    ":": Lexer._op_colon,
}



