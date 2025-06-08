from utils import Utils, Config

class Assembler:
    '''
    Assembles assembly code to binary format (16-bit instructions)
    
    Instruction Format:
        {mode}{save_addr}{jump}{calculation/data}
        - mode[15]:                    0=instruction, 1=ROM value
        - save_addr[14-12]:            Target register for result
        - jump[11-8]:                  Jump condition
        - calculation[7-0]/data[7-0]:  immediate value OR ALU operation + input registers

    Assembly Format:
        destination=calculation;jump
        Examples:
        - "A = 5"              # Store value in register A
        - "D = Lo & D"         # Store result in registers B
        - "JMP"                # Unconditional jump
        - "A = B + C;JEQ"      # Add B and C, store in A, jump if zero
    '''
    def __init__(self):
        self.current_line = 0
        # Default binary values
        self.DEFAULT_MODE = '0'        # Instruction mode
        self.DEFAULT_SAVE = '000'      # No save address
        self.DEFAULT_JUMP = '0000'     # No jump
        self.DEFAULT_CALC = '00000000' # No operation

    def assemble(self, input) -> list[str]:
        '''
        Transform assembly code to binary. Accepts either a file object or list of strings

        Args:
            input: Either an opened file for reading or a list of strings
        Returns:
            list of 16-Bit instructions
        '''
        # Convert file to list of lines if needed
        if hasattr(input, 'readlines'):
            try:
                lines = input.readlines()
            except IOError as e:
                Utils.log(f"Reading file: {e}", 'error', True)
        elif isinstance(input, list):
            if not all(isinstance(line, str) for line in input):
                Utils.log("Assembler - Input list contains non-string elements", 'error', True)
            lines = input
        else:
            Utils.log("Assembler - Invalid input type, must be file object or list of strings", 'error', True)
        
        binary_instructions = []
        
        for self.current_line, line in enumerate(lines,start=1):
            # Skip comments and empty lines
            if line.strip() and not line.strip().startswith('#'):
                binary:str = self.assemble_line(line)
                if binary:
                    binary_instructions.append(binary)
                else:
                    Utils.log(f"Assembler - Error processing line {self.current_line}: '{line.strip()}'", 'error', False)
            
        return binary_instructions
    
    def assemble_line(self, line: str) -> str:
        '''
        Assembles a single line into a 16-bit binary instruction string
        '''
        if not line or line.isspace():
            return format(0,'016b')
        
        try:
            # Initialize with defaults
            mode = self.DEFAULT_MODE
            save_addr = self.DEFAULT_SAVE
            jump = self.DEFAULT_JUMP
            calculation = self.DEFAULT_CALC
            
            # Split line into components
            part_dest, part_calc, part_jump = Utils.split_instruction(line)
                
            # Parse components
            if part_dest:
                save_addr = self._parse_addr(part_dest)
                
            if part_jump:
                jump = self._parse_jump(part_jump)
                
            if part_calc:
                calculation, mode = self.parse_calc(part_calc)
                if calculation is None:
                    Utils.log(f"Assembler - Invalid calculation in line {self.current_line}: '{line.strip()}'", 'error')
                    return format(0,'016b')
            
            # Special case: standalone jump - (check for unconditional)
            elif jump != '1000':
                return format(0,'016b')
            
            # Combine into final instruction
            return f'{mode}{save_addr}{jump}{calculation}'
            
        except Exception as e:
            Utils.log(f"Assembler - codeline {self.current_line}: {e}\nCode: {line.strip()}", 'error', True)

    def parse_calc(self, instruction: str) -> tuple[str,str]:
        '''
        Parse instruction into ALU operation and register selection or a number (read from rom).
        Handles single value operations and two-operand operations.
    
        Args:
            instruction: Assembly instruction string without save and jmp
        Returns:
            Tuple of (binary_string, mode):
            - binary_string: {alu_op}{input_reg_flags} or {immediate_value}
            - mode: '0' for instruction, '1' for ROM value
        '''
        
        if not instruction:
            Utils.log(f"Assembler - Empty calculation at line {self.current_line}", 'warning')
            return None, None
        
        parts = instruction.strip().upper().split()
        
        # Handle different instruction formats
        match len(parts):
            case 1:
                return self._handle_single_operand(parts[0])
            case 2:
                return self._handle_unary_operation(parts)
            case 3:
                return self._handle_binary_operation(parts)
            case _:
                Utils.log(f"Assembler - calculation to long at line {self.current_line}: '{instruction.strip()}'", 'error')
                return None, None
    
    def _handle_single_operand(self, operand: str) -> tuple[str, str]:
        '''Handles single register or immediate value'''
        if operand in Config.output_reg_map:
            return f'0000{Config.input_reg_map[operand + (',D' if operand == 'A' else ',A')]}', '0'
        # returns bin line after checking for range
        return format(Utils.convert_num(operand, 0) & 0xFF,'08b'), '1'
    
    def _handle_unary_operation(self, parts: list[str]) -> tuple[str, str]:
        '''Handles unary operations like NOT'''
        op, reg = parts
        if op in Config.single_op and reg in Config.output_reg_map:
            return f'{Config.alu_map[op]}{Config.input_reg_map[reg + (',D' if reg == 'A' else ',A')]}', '0'
        Utils.log(f"Assembler - Invalid unary operation '{' '.join(parts)}' at line {self.current_line}", 'error', False)
        return None, None
    
    def _handle_binary_operation(self, parts: list[str]) -> tuple[str, str]:
        '''Handles binary operations for alu instruction'''
        # Find operation and registers
        op = next((p for p in parts if p in Config.alu_map), None)
        regs: list[str] = [r for r in parts if r in Config.output_reg_map]
        
        if op and len(regs) == 2:
            return f'{Config.alu_map[op]}{Config.input_reg_map(','.join(regs))}', '0'
        Utils.log(f"Assembler - Invalid binary operation '{' '.join(parts)}' at line {self.current_line}", 'error', False)
        return None, None

    def _parse_addr(self, destination: str) -> str:
        '''
        Converts save addresses to binary flags
        Only 1 addres is allowed
        '''
        destination = destination.strip().upper()
        if not destination in Config.output_reg_map:
            Utils.log(f"Assembler - Unknown register '{destination}' in line {self.current_line}",'warning')
            return self.DEFAULT_SAVE
        return Config.output_reg_map[destination]
    
    def _parse_jump(self, jump_str: str) -> str:
        '''Converts jump instruction to binary condition code'''
        jump = jump_str.strip().upper()
        if jump in Config.jmp_map:
            return Config.jmp_map[jump]
        Utils.log(f"Assembler - Unknown jump condition '{jump}' in line {self.current_line}",'warning')
        return self.DEFAULT_JUMP
