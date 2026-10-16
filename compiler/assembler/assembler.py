from typing import List, Optional
import yaml
import os


class Assembler:
    """
    Assambles a asm file with following format into binary file.

    Format:
        [%]OPERATION [SRC] [DST/ACT][; JUMP_CONDITION]
        - % prefix: Sets status flag (affects bit 7 in the instruction)
        - OPERATION: ALU operation or special instruction
        - SRC: Source register or immediate value
        - DST: Destination register
        - ; JUMP_CONDITION: Optional jump condition after semicolon
        - -> immediate value when OPERATION is set to IMV

    Args:
        input_filename: Path to the assembly source file to process
        output_filename: Path where the binary output will be written
        instrruction_mappings_path: Path to YAML file containing instruction mappings

    Examples:
        - ADD D RAM; JNE
        - IMV x00 HI
        - JMP
        - NOP
    """

    def __init__(self, input_filename: str, output_filename: str, instrruction_mappings_path: str) -> None:
        self.input_filename: str = input_filename
        self.output_filename: str = output_filename
        self.lines: List[str] = []

        if not os.path.isfile(self.input_filename):
            raise FileNotFoundError(f"Input-file not found: '{self.input_filename}'")
        if not os.path.isfile(self.output_filename):
            raise FileNotFoundError(f"Output-file not found: '{self.output_filename}'")
        if not os.path.isfile(instrruction_mappings_path):
            raise FileNotFoundError(f"Configuration file not found: '{instrruction_mappings_path}'")

        with open(instrruction_mappings_path, "r") as f:
            try:
                self.MAPPINGS = yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML format in '{instrruction_mappings_path}': {e}")

        try:
            self.reg_map: dict[str, str] = self.MAPPINGS["registerSelect"]  # Bits 0-2
            self.alu_map: dict[str, str] = self.MAPPINGS["aluOperations"]  # Bits 3-6
            self.save_map: dict[str, str] = self.MAPPINGS["saveRegister"]  # Bits 9-12
            self.jmp_map: dict[str, str] = self.MAPPINGS["jumpConditions"]  # Bits 13-15
        except KeyError as e:
            raise KeyError(f"Missing mapping section in instruction_mappings: {e}")

    def run(self) -> None:
        """
        Execute the complete assembly process: 
            read source -> translate -> output binary.
        """
        self._read_file()
        self._process_lines()
        self._textToBin()

    def _read_file(self) -> None:
        """
        Reads and cleans the assembly source file.
        - Removes comments (everything after '#')
        - Strips whitespace from each line
        - Converts to uppercase for case-insensitive processing
        - Filters out completely empty lines to avoid processing errors
        """
        with open(self.input_filename, "r") as f:
            self.lines = [
                stripped for line in f 
                if (stripped := line.split("#", 1)[0].strip().upper())
            ]

    def _process_lines(self) -> None:
        """Convert each preprocessed assembly line into its binary representation."""
        for i, line in enumerate(self.lines):
            # Pass line number for better error reporting during translation
            self.lines[i] = self._translate_line(line, i)

    def _translate_line(self, line: str, lineNum: int) -> str:
        """
        Parse a single assembly line and convert it to binary instruction format.

        Args:
            line: The assembly instruction line to process
            lineNum: Line number for error reporting

        Returns:
            16-bit binary string representing the encoded instruction
        """
        if "%" in line:
            line = line.replace("%", "")
            status = True
        else:
            status = False

        if line.strip() == "JMP":
            return self._encode([], line.strip(), lineNum, status)
        elif line.strip() == "NOP":
            return 16*"0"

        # spliting parts
        instruction_parts = line.split(";", 1)
        jump = instruction_parts[1].strip() if len(instruction_parts) > 1 else None
        parts = instruction_parts[0].split()

        return self._encode(parts, jump, lineNum, status)

    def _encode(self, parts: List[str], jump: Optional[str], 
                lineNum: int, status: bool = False) -> str:
        """
        Encode instruction components into a 16-bit binary representation.

        The 16-bit instruction format is organized as follows:
        Bits 15-13: Jump conditions (3 bits)
        Bits 12-9:  Destination/Save register (4 bits)
        Bit 8:      Immediate Value mode (for Bits 0-7)
        Bit 7:      Status flag (0 = set flags, 1 = don't set flags)  Not used when Immediate
        Bits 6-3:   ALU operation  Not used when Immediate
        Bits 2-0:   Source register  Not used when Immediate

        Args:
            parts: List of instruction components [OPERATION, SRC, DST]
            jump: Optional jump condition string
            lineNum: Line number for error reporting
            status: Whether to set the status flag

        Returns:
            16-bit binary string representing the complete instruction
        """
        op: str = parts[0] if len(parts) > 0 else "CPY"
        src: str = parts[1] if len(parts) > 1 else "default"
        dst: str = parts[2] if len(parts) > 2 else "default"
        jmp: str = jump if jump else "default"
        value = None

        # Special handling for immediate value instructions
        if op == "IMV":
            value = parts[1] if len(parts) > 1 else None

        src_bin: str = self.reg_map.get(src, "None")
        alu_bin: str = self.alu_map.get(op, "None")
        dst_bin: str = self.save_map.get(dst, "None")
        jmp_bin: str = self.jmp_map.get(jmp, "None")

        # Construct the final 16-bit instruction
        if value:
            # Immediate value format: JMP(3) + DST(4) + Immediate->1 + VALUE(8)
            return jmp_bin + dst_bin + "1" + self._convert_num(value, lineNum)
        else:
            # Standard format: JMP(3) + DST(4) + !Immediate->0 + STATUS(1) + ALU(4) + SRC(3)
            return (
                jmp_bin + dst_bin + "0" + ("0" if status else "1") + alu_bin + src_bin
            )

    def _convert_num(self, value: str, line: int = -1) -> str:
        """
        Convert numeric values from various formats to 8-bit binary representation.

        Supports multiple input formats:
        - Hexadecimal: X1A (prefix X, then hex digits)
        - Binary: B10110 (prefix B, then binary digits)
        - Decimal: 26 (no prefix, decimal number)

        Args:
            value: String representation of the number to convert
            line: Line number for error reporting (default -1 if not specified)

        Returns:
            8-bit binary string (e.g., "00011010")

        Raises:
            ValueError: If the value format is invalid or out of 8-bit range (0-255)
        """
        base: int
        num_str: str

        # Determine number format based on prefix character
        if value.startswith("X"):
            base = 16
            num_str = value[1:]
        elif value.startswith("B"):
            base = 2
            num_str = value[1:]
        else:
            base = 10
            num_str = value

        try:
            num: int = int(num_str, base)
        except ValueError:
            raise ValueError(f"Invalid numeric value: '{value}' in line {line}")

        if not (0 <= num <= 255):
            raise ValueError(f"Value out of 8-bit range (0-255): '{value}' in line {line}")

        return format(num, "08b")

    def _textToBin(self) -> None:
        """
        Write the assembled binary instructions to the output file.

        Each 16-bit instruction is stored as 2 bytes in big-endian format.
        Big-endian is chosen for compatibility with many embedded processors
        and to make the binary file human-readable in hex editors.

        The output file format:
        - Each instruction: 2 bytes (16 bits)
        - Byte order: Big-endian (most significant byte first)
        - File size: 2 * number_of_instructions bytes
        """
        with open(self.output_filename, "wb") as f:
            for line in self.lines:
                value: int = int(line, 2)
                f.write(value.to_bytes(2, byteorder="big"))


# test
assembler = Assembler("input.txt", "output.bin", "compiler_v5/Assembler/instructions.yaml")
assembler.run()
