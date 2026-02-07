from structure_handler.datatypes import *

from typing import List, Optional
import re
from utils import Utils

class TreeBuilder:
    """
    Parses complex structures like functions, macros, loops, and conditions
    and organizes them into a tree-like format.
    
    The tree builder is resilient to indentation errors and will adjust indentation
    as needed to maintain proper tree structure. It removes comments and handles
    nested blocks correctly, returning a tree representation of the code structure.
    
    Supported structures:
        - FUNC NAME(ARGS): - Function definitions
        - MACRO NAME(ARGS): - Macro definitions  
        - IF(CONDITION): - Conditional blocks
        - ELIF(CONDITION): - Else-if blocks
        - ELSE: - Else blocks
        - REPEAT(NUMBER): - Repeat loops
        - while(CONDITION): - While loops
        - Function/macro calls: NAME(ARGS)
        - Regular instructions

    Example Input:
        - instructionA
        - instructionB
        - FUNC NAME(ARGS*):
        -     IF(REG1 VERGLEICHS_OP REG2):
        -         instructionC
        -         instructionD
        -     ELIF(Bedingung2):
        -         instructionE
        -     ELSE:
        -         instructionF
        - 
        - MACRO NAME(ARGS*):
        -     instructionG
        - NAME(ARGS*) # Function or macro call
        - REPEAT(NUMBER):
        -     instructionH
        - while(REG1 VERGLEICHS_OP REG2):
        -     instructionI
    """
    
    def __init__(self) -> None:
        """Initialize the TreeBuilder with empty structures list."""
        self.structures: List[StructureElement] = []
        self.last_structure_type: Optional[StructureType] = None

    @staticmethod
    def remove_comments(line: str) -> str:
        """
        Removes comments from a line of code

        Returns:
            Line with comments removed (everything after #)
        """
        return line.split("#", 1)[0]
    
    @staticmethod
    def _split_args(arg_str: str) -> List[str]:
        """
        Split argument string into individual arguments.
        
        Args:
            arg_str: Comma-separated argument string
            
        Returns:
            List of trimmed argument strings, empty list if no arguments
        """
        if not arg_str.strip(): return []
        return [a.strip() for a in arg_str.split(",") if a.strip()]
    
    def build_from_file(self, filepath: str) -> List[StructureElement]:
        """
        Build tree structure from a file.
        
        Args:
            filepath: Path to the file containing code to parse
            
        Returns:
            List of parsed structure elements
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            StructureParseError: If parsing fails
        """
        _, lines = Utils.open_file(filepath)
        return self.build(lines)
    
    def build(self, lines: List[str]) -> List[StructureElement]:
        """
        Parse the given code lines into structured blocks.
        
        This is the main entry point for parsing/ tree building. It preprocesses the lines
        to remove comments and calculate indentation, then builds a tree
        structure representing the code organization.
        
        Args:
            lines: List of code lines to parse
            
        Returns:
            List of parsed structure elements (Instructions and Structures)
            
        Raises:
            StructureParseError: If parsing fails due to invalid structure
        """
        if not lines: return []
        try:
            cleaned_lines = self._preprocess(lines)
            result = self._build_tree(cleaned_lines)
            self.structures = result
            return result
        except Exception as e:
            raise StructureParseError(f"Failed to parse structure in TreeBuilder: {str(e)}") from e

    def _preprocess(self, lines: List[str]) -> List[tuple[int, str, int]]:
        """
        Preprocess lines by removing comments and calculating indentation.
        
        Returns list of (indent_level, cleaned_line, original_line_number) tuples.
        """
        cleaned: List[tuple[int, str, int]] = []
        
        for line_num, line in enumerate(lines, 1):
            # Remove comments and trailing whitespace
            line = self.remove_comments(line).rstrip()
            
            if line:  # Skip empty lines
                indent = len(line) - len(line.lstrip())
                cleaned.append((indent, line.lstrip(), line_num))
            
        return cleaned
    
    def _build_tree(self, lines: List[tuple[int, str, int]]) -> List[StructureElement]:
        """
        Build the tree structure from preprocessed lines.
        
        Uses a stack to track nested structures and properly handle indentation.
        """
        stack: List[tuple[int, Structure]] = [] # Stack to track nested structures
        result: List[StructureElement] = []

        for indent, line, line_num in lines:
            try:
                self._process_line(indent, line, line_num, stack, result)
            except Exception as e:
                raise StructureParseError(f"Error processing line {line_num}: '{line}' - {str(e)}") from e
        
        # Close remaining structures
        while stack:
            self._pop_structure(stack, result)

        return result
    
    def _process_line(
        self,
        indent: int,
        line: str,
        line_num: int,
        stack: List[tuple[int, Structure]],
        result: List[StructureElement]
    ) -> None:
        """
        Process a single line and add it to the appropriate position in the tree.
        
        Handles indentation-based structure closing
        """
        elem: StructureElement = self._parse_line(line, line_num)
        # Pop structures with same or lower indentation
        while stack and indent <= stack[-1][0]:
            self._pop_structure(stack, result)
        
        if isinstance(elem, Instruction):
            # Add instruction to current structure or root level
            if stack:
                stack[-1][1].content.append(elem)
            else:
                result.append(elem)
        else:
            # Push new structure onto stack
            stack.append((indent, elem))

    def _pop_structure(
        self, stack: List[tuple[int, Structure]], result: List[StructureElement]
    ) -> None:
        """Pop a completed structure from stack and add to parent or result."""
        _, finished = stack.pop()
        if stack:
            stack[-1][1].content.append(finished)
        else:
            result.append(finished)
    
    def _parse_line(self, line: str, line_num: int) -> StructureElement:
        """
        Parse a single line into either a Structure or Instruction. 
        => equals node or leaf in the tree
        
        Tries to match against known structure patterns, falls back to Instruction.
        """
        # Try to match structure patterns
        for pattern, stype in STRUCTURE_PATTERNS.items():
            match = re.match(pattern, line, flags=re.IGNORECASE)
            if not match: continue

            structure = self._create_structure(stype, match, line_num)
            self.last_structure_type = structure.type
            return structure
        
        # If no structure pattern matches, treat as instruction
        return Instruction(line, line_num)

    def _create_structure(
        self, stype: StructureType, match: re.Match[str], line_num: int
    ) -> Structure:
        """
        Creates Structure-block from matchesd pattern
        no validation check for structures with multiple parts like elif needs if before
        """
        if stype in (FUNC, MACRO):
            name = match.group(2)
            args = self._split_args(match.group(3))
            return Structure(type=stype, name=name, args=args, line_number=line_num)
        elif stype in (IF, ELIF, WHILE, REPEAT):
            condition = match.group(2).strip()
            return Structure(type=stype, name=None, args=[condition], line_number=line_num)
        elif stype == ELSE:
            return Structure(type=stype, line_number=line_num)
        else:
            raise StructureParseError(f"Unhandled structure type: {stype} at line {line_num}")


    def display_structure(
        self, 
        structure: Optional[List[StructureElement]] = None, 
        level: int = 0,
        show_line_numbers: bool = False
    ) -> None:
        """
        Display the parsed structures in a readable tree format.
        
        Args:
            structure: Structure list to display (uses self.structures if None)
            level: Current indentation level for display
            show_line_numbers: Whether to show original line numbers
        """
        if structure is None:
            structure = self.structures
        
        indent = "  " * level
        for block in structure:
            line_part = f" [L{block.line_number}]" if show_line_numbers and block.line_number else ""
            if isinstance(block, Structure):
                name = f" {block.name}" if block.name else ""
                args = f"({', '.join(block.args)})" if block.args else ""
                print(f"{indent}{block.type}:{name}{args}{line_part}")
                if block.content: self.display_structure(block.content, level + 1)
            else: 
                print(f"{indent}INST: {block.inst}{line_part}")