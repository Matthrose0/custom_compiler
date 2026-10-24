from typing import List, Dict
import argparse
import os
import sys

import yaml

DEFAULT_CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "instructions.yaml")

class Disassembler:
    """
    Disassembles a binary file back to assembly format.
    
    Reads binary instructions and converts them back to the original assembly format:
        [%]OPERATION [SRC] [DST/ACT][; JUMP_CONDITION]
    
    The 16-bit instruction format is organized as follows:
        Bits 15-13: Jump conditions (3 bits)
        Bits 12-9:  Destination/Save register (4 bits)
        Bit 8:      Immediate Value mode (for Bits 0-7)
        Bit 7:      hold (0 = flags are updated, 1 = flags are held)  Not used when Immediate
        Bits 6-3:   ALU operation  Not used when Immediate
        Bits 2-0:   Source register  Not used when Immediate  

    Args:
        input_filename: Path to the binary file to disassemble
        output_filename: Path where the assembly output will be written
        instruction_mappings_path: Path to YAML file containing instruction mappings
    """
    
    # ALU operations that use only operand A (the source field is ignored)
    _UNARY_OPS = {'CPY', 'SHR', 'SHL', 'NOT', 'INC', 'DEC'}

    def __init__(self, input_filename: str, output_filename: str, instruction_mappings_path: str) -> None:
        self.input_filename: str = input_filename
        self.output_filename: str = output_filename
        self.instructions: List[str] = []

        if not os.path.isfile(self.input_filename):
            raise FileNotFoundError(f"Input-file not found: '{self.input_filename}'")
        if not os.path.isfile(instruction_mappings_path):
            raise FileNotFoundError(f"Configuration file not found: '{instruction_mappings_path}'")

        with open(instruction_mappings_path, "r") as f:
            try:
                self.MAPPINGS = yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML format in '{instruction_mappings_path}': {e}")

        # Create reverse mappings for disassembly
        try:
            self._reverse_mappings()
        except KeyError as e:
            raise KeyError(f"Missing mapping section in instruction_mappings: {e}")

    def _reverse_mappings(self) -> None:
        """Create reverse mappings from binary values to keywords."""
        self.reg_map: Dict[str, str] = self._reverse_mapping(self.MAPPINGS['registerSelect'])
        self.alu_map: Dict[str, str] = self._reverse_mapping(self.MAPPINGS['aluOperations'])
        self.save_map: Dict[str, str] = self._reverse_mapping(self.MAPPINGS['saveRegister'])
        self.jmp_map: Dict[str, str] = self._reverse_mapping(self.MAPPINGS['jumpConditions'])

    def _reverse_mapping(self, mapping: Dict[str, str]) -> Dict[str, str]:
        """Create reverse mapping from binary values to keywords."""
        reversed_map: Dict[str, str] = {}
        for key, value in mapping.items():
            # Use the first occurrence for duplicates (prefer main names over aliases)
            if value not in reversed_map:
                reversed_map[value] = key
        return reversed_map

    def run(self) -> None:
        """
        Execute the complete disassembly process:
            read binary -> decode -> output assembly.
        """
        self._read_binary()
        self._disassemble()

    def _read_binary(self) -> None:
        """
        Read the binary file and convert to list of 16-bit binary strings.
        Assumes big-endian format as used by the assembler.
        """
        with open(self.input_filename, 'rb') as f:
            data = f.read()
            
        if len(data) % 2 != 0:
            raise ValueError(f"Invalid binary file: odd number of bytes ({len(data)})")

        self.instructions.clear() # for safe when more than one call
        for i in range(0, len(data), 2):
            value = (data[i] << 8) | data[i + 1]
            bin_str = format(value, '016b')
            self.instructions.append(bin_str)

    def _disassemble(self) -> None:
        """Disassemble all binary instructions and write to output file."""
        assembly_lines: List[str] = []
        
        for instruction in self.instructions:
            assembly_line = self._decode_instruction(instruction)
            assembly_lines.append(assembly_line)
        
        # Write to output file
        with open(self.output_filename, 'w') as f:
            for line in assembly_lines:
                f.write(line + '\n')

    def _decode_instruction(self, binary_str: str) -> str:
        """
        Decode a 16-bit binary instruction back to assembly format.
        [%]OPERATION [SRC] [DST][; JUMP_CONDITION]
        
        Args:
            binary_str: 16-bit binary string
            
        Returns:
            Assembly instruction string
        """
        # Extract main components
        jmp_code = self._get_part(self.jmp_map, binary_str[0:3] ) # Bits 15-13
        dst_code = self._get_part(self.save_map, binary_str[3:7]) # Bits 12-9
        is_immediate = binary_str[7] == '1' # Bit 8
        
        # Build instruction based on type
        if is_immediate:
            return self._build_immediate_instruction(binary_str[8:16], dst_code, jmp_code)
        return self._build_standard_instruction(binary_str[8:16], dst_code, jmp_code)

    def _get_part(self, mapping: Dict[str, str], bits: str) -> str:
        """Get part from mapping, return empty string for 'default'."""
        result = mapping.get(bits, 'UNKNOWN')
        return '' if result == 'default' else result

    def _build_immediate_instruction(self, value_bits: str, dst: str, jmp: str) -> str:
        """Build IMV instruction string."""
        hex_value = f"x{(int(value_bits, 2)):02X}"
        parts = ['IMV', hex_value]
        if dst: 
            parts.append(dst)

        return self._add_jump_condition(parts, jmp)
    
    def _convert_to_appropriate_format(self, value: int) -> str:
        """
        Not Used -> implement using 
            value = int(value_bits, 2)
            hex_value = self._convert_to_appropriate_format(value)
        instead of
            hex_value = f"x{(int(value_bits, 2)):02X}"
        for smart hex conversion.
        """
        if value == 0:
            return "x00"  # Always use hex for 0
        elif value <= 15 and value % 4 == 0:  # Small multiples of 4
            return f"x{value:02X}"
        elif value % 16 == 0:  # Multiples of 16
            return f"x{value:02X}"
        else:
            return str(value)  # Use decimal for irregular values

    def _build_standard_instruction(self, remaining_bits: str, dst: str, jmp: str) -> str:
        """Build standard instruction string."""
        hold_flag = remaining_bits[0] == '1'
        alu_code = self.alu_map.get(remaining_bits[1:5], 'UNKNOWN')
        src_code = self._get_part(self.reg_map, remaining_bits[5:8])
        
        # Handle special cases
        if alu_code == 'CPY' and not src_code and not dst:
            return 'JMP' if jmp == 'JMP' else 'NOP'

        # Source 000 is omitted by the reverse mapping ('default'); keep a placeholder
        # so that SRC/DST stay in place when the output is assembled again.
        if not src_code and dst:
            src_code = 'A' if alu_code in self._UNARY_OPS else 'D'
        
        # Build instruction parts
        alu_with_status = f"{'%' if hold_flag else ''}{alu_code or 'CPY'}"
        parts = [p for p in [alu_with_status, src_code, dst] if p]
        return self._add_jump_condition(parts, jmp)

    def _add_jump_condition(self, parts: List[str], jmp: str) -> str:
        """Add jump condition to instruction if needed."""
        # no check for standalone jump needed 
        # -> because of early return in _build_standard_instruction
        instruction = ' '.join(parts)
        if jmp: instruction += f'; {jmp}'
            
        return instruction


def main() -> None:
    parser = argparse.ArgumentParser(description="Disassembles a binary file back to assembly.")
    parser.add_argument("input", help="binary input file")
    parser.add_argument("output", help="assembly output file")
    parser.add_argument("-c", "--config", default=DEFAULT_CONFIG,
                        help="instruction mappings (default: instructions.yaml next to this script)")
    args = parser.parse_args()
    try:
        Disassembler(args.input, args.output, args.config).run()
    except (FileNotFoundError, ValueError, KeyError) as e:
        sys.exit(f"Error: {e}")


if __name__ == "__main__":
    main()
