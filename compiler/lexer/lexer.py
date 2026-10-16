from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Final, Any,Iterator
 
from compiler.lexer.token import TOKEN_TYPE as TT, Token, KEYWORDS
from compiler.errors.errors import LexerError, ErrorBag

