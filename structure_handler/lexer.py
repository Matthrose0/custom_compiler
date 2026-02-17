# for every token saves row and column
# has newline token and indent / dedent

from structure_handler.datatypes import *

from typing import List, Optional
import re
from utils import Utils




class Lexer:
    def __init__(self):
        pass

    def tokenize(self, s: str) -> list[str]:
        tokens = s.split()

        for token in tokens:
            if token.isdigit():
                pass