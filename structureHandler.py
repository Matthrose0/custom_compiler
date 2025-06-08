from dataclasses import dataclass, field
from typing import List, Optional
import re
from utils import Utils

@dataclass
class Structure:
    type: str
    name: Optional[str] = None # for named structures
    args: Optional[List[str]] = None
    content:  Optional[List["Structure"]] = None #field(default_factory=list)

class StructureHandler:
    """
    Parses complex structures like functions, macros, loops, and conditions
    -> organizes it into a tree-like format
    First breakdown from input code + removing comments
    """
    STRUCTURE_PATTERNS = {
        r'^(FUNC)\s+(\w+)\((.*?)\):$': "FUNC",
        r'^(MACRO)\s+(\w+)\((.*?)\):$': "MACRO",
        r'^(IF)\((.*?)\):$': "IF",
        r'^(ELIF)\((.*?)\):$': "ELIF",
        r'^(ELSE):$': "ELSE",
        r'^(REPEAT)\((.*?)\):$': "REPEAT",
        r'^(while)\((.*?)\):$': "WHILE"
    }
    
    def __init__(self):
        self.structures: List[Structure] = []
    
    def parse(self, lines: List[str]) -> List[Structure]:
        """Parses the given assembly lines into structured blocks"""
        stack = []
        indent_levels = []
        last_structure_type = None
        
        for line_num, line in enumerate(lines, 1):
            raw_line = line
            line = self.remove_comments(line).rstrip()
            if not line:
                continue
            
            # handle indents
            indent_level = len(raw_line) - len(raw_line.lstrip())
            while indent_levels and indent_levels[-1] >= indent_level:
                indent_levels.pop()
                stack.pop()

            current_structure = self._parse_structure_line(line, line_num, last_structure_type)
            
            
            
            if current_structure == None:
                code_structure = Structure(type="CODE", name=line)
                if stack and indent_level > indent_levels[-1]:
                    stack[-1].content.append(code_structure)
                else:
                    self.structures.append(code_structure)

                ####
                if stack and indent_level > indent_levels[-1]:
                    stack[-1].content.append(structure)
                else:
                    self.structures.append(structure)
                stack.append(structure)
                indent_levels.append(indent_level)
                last_structure = structure
                matched = True
                break
            
            
        
        return self.structures

    def _parse_structure_line(self, line: str, line_num: int, last_structure_type: Optional[str]) -> Optional[Structure]:
        """Parses a single line and returns a Structure if matched"""
        for pattern, struct_type in self.STRUCTURE_PATTERNS.items():
            match = re.match(pattern, line)
            if not match: continue

            name = match.group(2) if len(match.groups()) > 1 else None
            args = match.group(3).split(',') if len(match.groups()) > 2 and match.group(3) else []

            if struct_type in {"ELIF", "ELSE"} and (last_structure_type not in {"IF", "ELIF"}):
                Utils.log(f"Structures - in line {line_num}: {struct_type} without matching IF or ELIF", 'error')
                return None

            return Structure(type=struct_type, name=name, args=args)
        return Structure(type="CODE", name=line)

    def display_structure(self, structure: List[Structure] = None, level = 0) -> None:
        """Display the parsed structure for debugging purposes"""
        if structure is None:
            structure = self.structures

        for block in structure:
            if isinstance(block, str):
                print("  " * level + block)
            else:
                print("  " * level + f"{block.type}: {block.name} {block.args if block.args else ''}")
                self.display_structure(block.content, level + 1)
    
    def remove_comments(self, line: str) -> str:
        """Removes comments from a line of code"""
        return re.split(r'\s*#', line, maxsplit=1)[0].strip()