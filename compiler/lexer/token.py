from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Union, Dict

# =============================================================================
#  TOKEN_TYPE'S
# =============================================================================
class TOKEN_TYPE(Enum):
    # _____Structure___________________________________________________________
    COMMENT     = auto()
    NEWLINE     = auto()
    INDENT      = auto()
    DEDENT      = auto()
    EOF         = auto()

    # _____Literal_values______________________________________________________
    INT         = auto()
    FLOAT       = auto()
    STRING      = auto()
    CHAR        = auto()
    TRUE        = auto()    # for bool
    FALSE       = auto()
    NONE        = auto()    # for void pointer

    # _____Identifier__________________________________________________________
    IDENT       = auto()

    # _____Keywords____________________________________________________________
    # definitions
    FUNC        = auto()
    MACRO       = auto()
    PUB         = auto()
    CONST       = auto()

    # Module control
    IMPORT      = auto()
    AS          = auto()

    # Control flow
    IF          = auto()
    ELIF        = auto()
    ELSE        = auto()
    WHILE       = auto()
    REPEAT      = auto()
    FOR         = auto()
    IN          = auto()
    RETURN      = auto()
    BREAK       = auto()
    EXIT        = auto()    # stop program
    CONTINUE    = auto()
    PASS        = auto()

    # Types
    T_INT       = auto()
    T_FLOAT     = auto()
    T_STRING    = auto()
    T_CHAR      = auto()
    T_BOOL      = auto()
    T_VOID      = auto()

    # _____Operators___________________________________________________________
    # arithmetic
    ADD         = auto()    # +
    SUB         = auto()    # -
    MUL         = auto()    # *
    DIV         = auto()    # /
    INTDIV      = auto()    # //  int division
    MOD         = auto()    # % 
    POW         = auto()    # **
    INC         = auto()    # ++
    DEC         = auto()    # --

    # aliases for arithmatic
    PLUS        = ADD
    MINUS       = SUB
    STAR        = MUL
    SLASH       = DIV
    DOUBLESLASH = INTDIV
    PERCENT     = MOD
    DOUBLESTAR  = POW

    # bitwise
    BIT_AND     = auto()    # &
    BIT_OR      = auto()    # |
    BIT_XOR     = auto()    # ^
    BIT_NOT     = auto()    # ~
    LSHIFT      = auto()    # <<
    RSHIFT      = auto()    # >>

    # comparison
    LT          = auto()    # <
    LE          = auto()    # <=
    GT          = auto()    # >
    GE          = auto()    # >=
    EQ          = auto()    # ==
    NE          = auto()    # !=

    # logical
    AND         = auto()    # &&
    OR          = auto()    # ||
    NOT         = auto()    # !=
    
    
    # _____Assignments_________________________________________________________
    ASSIGN      = auto()    # =
    ADD_ASSIGN  = auto()    # +=
    SUB_ASSIGN  = auto()    # -=
    MUL_ASSIGN  = auto()    # *=
    POW_ASSIGN  = auto()    # **=
    DIV_ASSIGN  = auto()    # /=

    # aliases
    PLUS_ASSIGN = ADD_ASSIGN
    MINUS_ASSIGN= SUB_ASSIGN
    STAR_ASSIGN = MUL_ASSIGN
    SLASH_ASSIGN= DIV_ASSIGN

    # _____Delimiters__________________________________________________________
    # in no Kategorie group for now
    LPAREN      = auto()    # (
    RPAREN      = auto()    # )
    LBRACKET    = auto()    # [
    RBRACKET    = auto()    # ]
    LBRACE      = auto()    # {
    RBRACE      = auto()    # }
    COMMA       = auto()    # ,
    DOT         = auto()    # .
    COLON       = auto()    # :
    SEMICOLON   = auto()    # ;
    ARROW       = auto()    # ->   return type
    WALRUS      = auto()    # :=   (no functionality planned)
    AT          = auto()    # @    Decorator / matrix-multiplikation
 
    # Aliases
    OPEN_PAREN  = LPAREN
    CLOSE_PAREN = RPAREN
    OPEN_BRACK  = LBRACKET
    CLOSE_BRACK = RBRACKET
    OPEN_BRACE  = LBRACE
    CLOSE_BRACE = RBRACE

    # _____Errors______________________________________________________________
    ERROR       = auto()

    # _____ASM_commands_____________________________________________________
    # # Register
    # REG_A       = auto()
    # REG_D       = auto()
    # REG_LO      = auto()
    # REG_HI      = auto()
    # REG_FR      = auto()
    # REG_SPL     = auto()
    # REG_SPH     = auto()
    # REG_CARRY   = auto()

    # # Jump
    # JLT         = auto()
    # JEQ         = auto()
    # JGT         = auto()

    # JLE         = auto()
    # JNE         = auto()
    # JGE         = auto()

    # JMP         = auto()
    # JZ          = auto()
    # JNZ         = auto()

    # # actions
    # REFRESH     = auto()

    # # logical
    # XOR         = auto()
    # ...


# =============================================================================
#  Keyword-mappings
#  -> in Lexer identify first as ident -> then check for keyword
# =============================================================================
KEYWORDS: Dict[str, TOKEN_TYPE] = {
    # definition
    "func": TOKEN_TYPE.FUNC,
    "macro": TOKEN_TYPE.MACRO,
    "pub": TOKEN_TYPE.PUB,
    "const": TOKEN_TYPE.CONST,

    # Module control
    "import": TOKEN_TYPE.IMPORT,
    "as": TOKEN_TYPE.AS,

    # control flow
    "if": TOKEN_TYPE.IF,
    "elif": TOKEN_TYPE.ELIF,
    "else": TOKEN_TYPE.ELSE,
    "while": TOKEN_TYPE.WHILE,
    "repeat": TOKEN_TYPE.REPEAT,
    "for": TOKEN_TYPE.FOR,
    "in": TOKEN_TYPE.IN,        #####
    "return": TOKEN_TYPE.RETURN,
    "break": TOKEN_TYPE.BREAK,
    "exit": TOKEN_TYPE.EXIT,
    "continue": TOKEN_TYPE.CONTINUE,
    "pass": TOKEN_TYPE.PASS,

    # types
    "int": TOKEN_TYPE.T_INT,
    "float": TOKEN_TYPE.T_FLOAT,
    "string": TOKEN_TYPE.T_STRING,
    "char": TOKEN_TYPE.T_CHAR,
    "bool": TOKEN_TYPE.T_BOOL,
    "void": TOKEN_TYPE.T_VOID,

    # literals which look like keywords
    "true": TOKEN_TYPE.TRUE,
    "false": TOKEN_TYPE.FALSE,
    "none": TOKEN_TYPE.NONE,
}

# =============================================================================
#  Kategories-Sets
# =============================================================================
TT = TOKEN_TYPE

STRUCTURALS: frozenset[TOKEN_TYPE] = frozenset({TT.COMMENT, TT.NEWLINE, TT.INDENT,
                                                TT.DEDENT, TT.EOF})
LITERSLS: frozenset[TOKEN_TYPE] = frozenset({TT.INT, TT.FLOAT, TT.STRING, 
                                             TT.CHAR, TT.TRUE, TT.FALSE, TT.NONE})

TYPE_KEYWORDS: frozenset[TOKEN_TYPE] = frozenset({TT.T_INT, TT.T_FLOAT, TT.T_STRING,
                                                  TT.T_CHAR, TT.T_BOOL, TT.T_VOID})
STRUCTURE_INITIATORS: frozenset[TOKEN_TYPE] = frozenset({TT.FUNC, TT.MACRO, TT.IF, TT.ELIF, 
                                                         TT.ELSE, TT.REPEAT, TT.WHILE, TT.FOR})
STRUCTURE_BREAKERS: frozenset[TOKEN_TYPE] = frozenset({TT.RETURN, TT.BREAK, TT.EXIT, 
                                                       TT.CONTINUE, TT.PASS})
OTHER_KEYWORDS: frozenset[TOKEN_TYPE] = frozenset({TT.PUB, TT.CONST, TT.IMPORT, TT.AS, TT.IN})


COMPARE_OPS: frozenset[TOKEN_TYPE] = frozenset({TT.EQ, TT.NE, TT.LT, TT.LE, TT.GT, TT.GE})
LOGIC_OPS: frozenset[TOKEN_TYPE] = frozenset({TT.AND, TT.OR, TT.NOT})#
BIT_OPS: frozenset[TOKEN_TYPE] = frozenset({TT.BIT_AND, TT.BIT_OR, TT.BIT_XOR, TT.BIT_NOT,
                                            TT.LSHIFT, TT.RSHIFT})
ARITHMATIC_OPS: frozenset[TOKEN_TYPE] = frozenset({TT.ADD, TT.SUB, TT.MUL, TT.DIV, TT.INTDIV,
                                                   TT.MOD, TT.POW, TT.INC, TT.DEC})

OPERATORS: frozenset[TOKEN_TYPE] = frozenset(COMPARE_OPS | LOGIC_OPS | BIT_OPS | ARITHMATIC_OPS)


ASSIGNMENTS: frozenset[TOKEN_TYPE] = frozenset({TT.ASSIGN, TT.ADD_ASSIGN, TT.SUB_ASSIGN, 
                                                TT.MUL_ASSIGN, TT.POW_ASSIGN, TT.DIV_ASSIGN})

OPENERS: frozenset[TOKEN_TYPE] = frozenset({TT.LPAREN, TT.LBRACKET, TT.LBRACE})
CLOSERS: frozenset[TOKEN_TYPE] = frozenset({TT.RPAREN, TT.RBRACKET, TT.RBRACE})

# =============================================================================
#  Token
# =============================================================================
@dataclass(frozen=True) 
class Token:
    """
    single Token. frozen=True 
    -> can't be changed after __init__ -> prevent changing in parser
    """
    type: TOKEN_TYPE
    value: str
    line: int
    col: int                    # start of token in line
    col_end: int                # end of token in line
    file: str = "<unknown>"
    
    @property
    def pos(self) -> str:#
        """
        get location of token for error messages. 
        Example: main.py: line:2, pos:12-14
        """
        return f"{self.file}: line: {self.line}, pos:{self.col}-{self.col_end}"

    def __repr__(self) -> str:
        return f"""Token(type={self.type}, value={self.value}, 
                   line={self.line}, col={self.col}, col_end={self.col_end}, file={self.file})"""
    
    # Kategory checks
    def is_structural(self) -> bool: return self.type in STRUCTURALS
    def is_literal(self) -> bool: return self.type in LITERSLS
    def is_type_keyword(self) -> bool: return self.type in TYPE_KEYWORDS
    def is_structure_initiator(self) -> bool: return self.type in STRUCTURE_INITIATORS
    def is_structure_breaker(self) -> bool: return self.type in STRUCTURE_BREAKERS
    def is_other_keyword(self) -> bool: return self.type in OTHER_KEYWORDS
    def is_operator(self) -> bool: return self.type in OPERATORS
    def is_assignment(self) -> bool: return self.type in ASSIGNMENTS
    def is_opener(self) -> bool: return self.type in OPENERS
    def is_closer(self) -> bool: return self.type in CLOSERS

    def is_type(self, *types: TOKEN_TYPE) -> bool:
        return self.type in types

# =============================================================================
#  Token-Stream
# =============================================================================
class TokenStream:
    """
    Wrapper for tokenlist -> no indexes required from outside (parser)
    """
    _tokens: List[Token]
    _pos: int

    def __init__(self, tokens: list[Token]) -> None:
        if not tokens:
            raise ValueError("TokenStream requires at least one token.")
        if tokens[-1].type is not TT.EOF:
            raise ValueError("TokenStream requires a trailing EOF token.")
        self._tokens = tokens
        self._pos: int = 0
    
    def __len__(self): return len(self._tokens)
    def __getitem__(self, index: int): return self._tokens[index]
    def __iter__(self): return iter(self._tokens)
    def __repr__(self) -> str:
        remaining = len(self._tokens) - self._pos
        return f"TokenStream(pos={self._pos}, remaining={remaining})"

    # __state__________________________________________________________________
    @property
    def pos(self) -> int: return self._pos

    def peek(self, offset: int = 0) -> Token:
        """
        Returns the token at the given offset from the current position. 
        Returns EOF token if out of range.
        """
        idx = self._pos + offset
        return self._tokens[idx] if idx < len(self._tokens) and idx >= 0 else self._tokens[-1]
    
    def peek_type(self, offset: int = 0) -> TOKEN_TYPE:
        return self.peek(offset).type

    def is_eof(self) -> bool: return self.peek().type is TT.EOF
    
    # __manipulation___________________________________________________________
    def advance(self) -> Token:
        """Return current token and move forward."""
        tok = self.peek()
        if not self.is_eof():
            self._pos += 1
        return tok
    
    def expect(self, expected: TT) -> Token:
        """
        Consume and return current token if it matches expected.
        Raises SyntaxError with location info otherwise.
        """
        tok = self.peek()
        if tok.type is not expected:
            raise SyntaxError(
                f"Expected {expected.name}, got {tok.type.name} ({tok.value!r}) "
                f"at {tok.file or '<input>'}:{tok.line}:{tok.col}"
            )
        return self.advance()
    
    def restore(self, pos: int) -> None:
        if pos < 0 or pos > len(self._tokens):
            raise ValueError("Invalid token position for restore.")
        self._pos = pos
    

    






















# alter Müll
class StructureParseError(Exception):
    """Custom exception for structure parsing errors."""
    pass




StructureElement = Union["Structure", "Instruction"]

class StructureType(Enum):
    FUNC = "FUNC"
    MACRO = "MACRO"
    IF = "IF"
    ELIF = "ELIF"
    ELSE = "ELSE"
    REPEAT = "REPEAT"
    WHILE = "WHILE"
FUNC = StructureType.FUNC
MACRO = StructureType.MACRO
IF = StructureType.IF
ELIF = StructureType.ELIF
ELSE = StructureType.ELSE
REPEAT = StructureType.REPEAT
WHILE = StructureType.WHILE

STRUCTURE_PATTERNS = {
    # only for first erkennung in tree_builder
    r'^(FUNC)\s+(\w+)\s*\((.*?)\)\s*:$': FUNC,
    r'^(MACRO)\s+(\w+)\s*\((.*?)\)\s*:$': MACRO, 
    r'^(IF)\s*\((.*?)\)\s*:$': IF,
    r'^(ELIF)\s*\((.*?)\)\s*:$': ELIF,
    r'^(ELSE)\s*:$': ELSE,
    r'^(REPEAT)\s*\((.*?)\)\s*:$': REPEAT,
    r'^(WHILE)\s*\((.*?)\)\s*:$': WHILE
}

@dataclass
class Instruction:
    """
    Represents a single instruction line in the code.
    
    Attributes:
        inst: The instruction string content
        line_number: Optional original line number for debugging (added for better error reporting)
    """
    inst: str
    line_number: Optional[int]

@dataclass
class Structure:
    """
    Represents a structured block (function, loop, condition, etc.).
    
    Attributes:
        type: The structure type (FUNC, MACRO, IF, ELIF, ELSE, REPEAT, WHILE)
        name: Optional name for functions and macros
        args: Optional list of arguments/conditions
        content: List of nested structure elements
        line_number: Optional original line number for debugging
    """
    type: StructureType
    line_number: Optional[int] = None
    name: Optional[str] = None
    args: Optional[List[str]] = None
    content: List[StructureElement] = field(default_factory=list[StructureElement])

@dataclass
class CallableStructureTupel:
    """
    for macros/functions 
    name is the key for the tuple
    
    """
    line_number: Optional[int]
    args: Optional[List[str]] = None
    content: List[StructureElement] = field(default_factory=list[StructureElement])