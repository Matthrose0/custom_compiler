from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Union


# Tokenizer
class TokenType(Enum):
    
    KEYWORD = "KEYWORD"         # FUNC, MACRO, IF, ELIF, ... -> zu viel sonderlogik jedes mal notwendig
    
    IDENTIFIER = "IDENTIFIER"   # names of functions,...
    REGISTER = "REGISTER"       # A, D, SP, LO, HI, ...
    NUMBER = "NUMBER"
    STRING = "STRING"

    OPERATOR = "OPERATOR"       # +, -, *, /, <, >
    JUMP = "JUMP"               # JLT, JEQ, JLE, JGT, JNE, JGE
    
    COMMENT = "COMMENT"
    NEWLINE = "NEWLINE"
    INDENT = "INDENT"
    DEDENT = "DEDENT"
    EOF = "EOF"

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int







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
    
