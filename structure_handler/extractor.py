from structure_handler.datatypes import *
from typing import List


class ExtractorError(Exception):
    """Custom error class for Extractor-specific errors."""
    pass

class Extractor:
    def __init__(self) -> None:
        self.functions: dict[str, CallableStructureTupel] = {}
        self.macros: dict[str, CallableStructureTupel] = {}
        
        self.target_map = {
            FUNC: self.functions,
            MACRO: self.macros
        }
    
    def _raise_extraction_error(
        self, 
        structure: Structure, 
        reason: str
    ) -> None:
        """
        Raises a detailed ExtractorError with structure information.
        
        Args:
            structure: The Structure element that caused the error
            reason: Human-readable reason for the error
            
        Raises:
            ExtractorError: With detailed error message including line number
        """
        line_info = (f" at line {structure.line_number}" 
                    if structure.line_number is not None else "")
        type_info = f" (type: {structure.type})" if structure.type else ""
        
        error_msg = (f"Extraction failed{line_info}: {reason}. "
                    f"Structure{type_info} cannot be processed.\n{structure}")
        
        raise ExtractorError(error_msg)

    def extract(
        self, 
        tree_structure: List[StructureElement]
    ) -> tuple[
        List[StructureElement], 
        dict[str, CallableStructureTupel], 
        dict[str, CallableStructureTupel]
    ]:
        """
        Extracts functions and macros from the tree structure.
        
        Processes the tree structure recursively, removing all FUNC and MACRO
        type structures and storing them in separate dictionaries. Returns
        the cleaned tree structure along with the extracted callables.
        
        Modifys the tree_structure direct and returns the SAME object again.
        (so it wouldn't be necessary)
        
        Args:
            tree_structure: List of StructureElement objects to process
            
        Returns:
            Tuple containing:
            - Cleaned tree structure (functions/macros removed)
            - Dictionary of extracted functions
            - Dictionary of extracted macros
            
        Raises:
            ExtractorError: If a function/macro has no name or other issues
            TypeError: If tree_structure is not a list
        """
        # Reset dictionaries for fresh extraction
        self.functions.clear()
        self.macros.clear()
        
        # Process elements and remove functions/macros
        self._process_elements(tree_structure)
        
        return tree_structure, self.functions, self.macros

    
    def _process_elements(self, elements: List[StructureElement]) -> None:
        """
        Recursively processes elements, extracting functions and macros.
        
        Modifies the elements list in-place by removing extracted functions
        and macros. Processes nested structures recursively.
        
        Args:
            elements: List of StructureElement objects to process
            
        Raises:
            ExtractorError: If a function/macro structure has invalid data
        """
        # Process in reverse order to safely remove elements during iteration
        for i in range(len(elements) - 1, -1, -1):
            element = elements[i]
            if not isinstance(element, Structure): continue
            
            if element.type in self.target_map:
                self._extract_callable(element, elements, i)
                continue
            
            # Recursively process nested content
            if element.content:
                self._process_elements(element.content)

    def _extract_callable(
        self, 
        structure: Structure, 
        parent_list: List[StructureElement], 
        index: int
    ) -> None:
        """
        Extracts a single callable (function or macro) from the structure.
        
        Args:
            structure: The Structure element to extract
            parent_list: The parent list containing this structure
            index: Index of the structure in the parent list
            
        Raises:
            ExtractorError: If structure has no name or duplicate name exists
        """
        # Validate structure has a name
        if structure.name is None:
            self._raise_extraction_error(
                structure, 
                "function/macro must have a name"
            )
        
        # Get the appropriate storage dictionary
        target_dict = self.target_map[structure.type]
        
        # Check for duplicate names
        if structure.name in target_dict:
            self._raise_extraction_error(
                structure,
                f"duplicate {structure.type} name '{structure.name}'"
            )
        
        # child-check -> raise error when in deffinition is an other deffinition (deepcheck)
        self._check_for_nested_callables(structure.content, structure, [])
        
        # Store the callable structure
        target_dict[structure.name] = [ # type: ignore because structure.name is checked
            structure.args, 
            structure.content, 
            structure.line_number
        ]
        
        # Remove from parent structure
        parent_list.pop(index)
    

    def _check_for_nested_callables(
        self, 
        elements: List[StructureElement], 
        parent_callable: Structure,
        path: List[str]
    ) -> None:
        """
        Recursively checks elements for nested callable definitions.
        
        Args:
            elements: List of elements to check
            parent_callable: The parent callable structure being validated
            path: Current path through the structure (for error reporting)
            
        Raises:
            ExtractorError: If a nested callable definition is found
        """
        for element in elements:
            if not isinstance(element, Structure): continue
            
            # Build path for better error reporting
            current_path = path + [element.name or f"<{element.type}>"]
            
            # Check if this element is a callable definition
            if element.type in self.target_map:
                nested_name = element.name or "<unnamed>"
                path_str = " -> ".join(current_path)
                
                self._raise_extraction_error(
                    element,
                    f"nested {element.type} '{nested_name}' found inside "
                    f"{parent_callable.type} '{parent_callable.name}' "
                    f"at path: {path_str}"
                )
            
            # Recursively check nested content
            if element.content:
                self._check_for_nested_callables(
                    element.content, 
                    parent_callable, 
                    current_path
                )