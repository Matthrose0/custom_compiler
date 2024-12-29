import os
from typing import Dict, Optional


saveAddress_map = {
    'A'    : '00001',  # combinig addresses later
    'A2'   : '00010',
    'RAM'  : '00100',
    'B'    : '01000',
    'D'    : '10000',
}
jump_map = {
    'JLT' : '001',  # Jump if < 0
    'JEQ' : '010',  # Jump if = 0
    'JLE' : '011',  # Jump if <=0
    'JGT' : '100',  # Jump if > 0
    'JNE' : '101',  # Jump if !=0
    'JGE' : '110',  # Jump if >=0
    'JMP' : '111',  # Jump always
}
alu_map = {
    'NONE' : '0000',
    'NEG'  : '0001',
    'ADD'  : '0100',
    'SUB'  : '0110',
    'INC'  : '0101',
    'DEC'  : '0111',
    'AND'  : '1100',
    'OR'   : '1101',
    'XOR'  : '1110',
    'NOT'  : '1111',
    'SHL'  : '1000',
    'SHR'  : '1001',
    'MIN'  : '1010',
    'MAX'  : '0010',

    'MAX1' : '0011',
    'MIN1' : '1011',
}
single_op = {'NOT', 'NEG', 'INC', 'DEC', 'SHL', 'SHR', 'MIN1', 'MAX1'}
input_reg_map = {
    # first variable
    # first bit (from left to right) -> swap flag 
    # second bit -> select y
    # third bit -> select x
    'A'   : '000',
    'RAM' : '001',
    'B'   : '100',
    'D'   : '110',
}
input_reg_map2 = {
    # second variable
    'A'   : '000',
    'RAM' : '001',
    'B'   : '000',
    'D'   : '010',
}


def open_file(file_name: str, mode: str = 'r') -> tuple[bool, str, any]:
    """
    attempts to open a file, first directly, then as a relative path from the main program
    
    args:
        file_name: Name/path of the file
        
    returns:
        tuple: (success, file path, file handle or None)
    """
    # direct attempt to open the file
    if os.path.exists(file_name):
        return True, file_name, open(file_name, mode)
    
    # try relative path from the main program location
    base_path = os.path.dirname(os.path.abspath(__file__))
    relative_path = os.path.join(base_path, file_name)
    
    if os.path.exists(relative_path):
        return True, str(relative_path), open(relative_path, mode)
        
    return False, "", None
def txt_to_bin(input_file, output_file):
    try:
        # Datei lesen
        success, path, f = open_file(input_file)
        if not success: 
            print(f"Die Datei {input_file} wurde nicht gefunden.")

        # Nur die Zeichen '0' und '1' beibehalten
        bit_content = ''.join(char for char in f.read() if char in ['0', '1'])

        # Als Binärdatei speichern
        output_file = os.path.join(os.path.dirname(path), output_file)
        with open(output_file, 'wb') as outfile:
            # Konvertieren in Bytes
            byte_array = int(bit_content, 2).to_bytes((len(bit_content) + 7) // 8, byteorder='big')
            outfile.write(byte_array)

        print(f"Die Datei wurde erfolgreich von {input_file} zu {output_file} konvertiert.")
    except ValueError:
        print("Der Inhalt der Datei enthält keine gültigen Bits (nur '0' und '1' erlaubt).")
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")

class Compiler:
    def __init__(self):
        self.constants: Dict[str, int] = {}
        self.current_line = 0
    
    def number_check(self, str_num: str) -> bool:
        '''check for numeric value in 8bit region'''
        if str_num.strip().isdigit():
            num = int(str_num.strip())
            return num < 128 and num > -128

    def parse_constant(self, line: str) -> None:
        '''Parse constant definition (e.g., 'DEFINE const_name=value')'''
        if line.upper().startswith('DEFINE'):
            name, value = line[6:].upper().split('=')
            if self.number_check(value):
                self.constants[name.strip()] = int(value.strip())

    def parse_addr(self, destinations: str) -> str:
        '''Convert save addr'es to binary'''
        save_addr = '00000'
        dest_list = destinations.split(',')

        # Parse save addresses
        for s in dest_list:
            mapped_value = saveAddress_map.get(s.strip().upper(), '00000') # Default to '00000' if not found
            save_addr = format(int(save_addr, 2) | int(mapped_value, 2),'05b') # Combine binary values
        return save_addr
                    
    def parse_jump(self, jump_str: str) -> str:
        '''Convert jump instruction to binary'''
        return jump_map.get(jump_str.strip().upper(),'000')
    
    def parse_calc(self, instruction: str) -> tuple[str,str]: # tuple[instruction,mode]
        '''
        Parse instruction into ALU operation and register selection or get a constant.
        Handles single value operations and two-operand operations.
    
        Args:
            instruction: Assembly instruction string
        Returns:
            Binary string: {alu_op}{input_reg_flags} or {constant}
        
        error if instruction not valid
        '''
        
        if not instruction:
            return None, None
        
        parts = instruction.strip().upper().split()
        input_reg = '000'
        alu = '0000'
        

        # Pass-through (just register selection or constant)
        if len(parts) == 1:
            if parts[0] in input_reg_map:
                # middle part is Register
                return f'{alu}{input_reg_map[parts[0]]}','0'
            elif parts[0] in self.constants:
                # middle part is constant
                return f'{format(self.constants[parts[0]],'08b')}','1'
            elif self.number_check(parts[0]):
                # middle part is number
                return f'{format(int(parts[0]),'08b')}','1'

        # Single operand operations
        if len(parts) == 2:
            # Check both orders: "NOT A" and "A NOT"
            if parts[0] in single_op:
                alu = alu_map[parts[0]]
                input_reg = input_reg_map[parts[1]]
            elif parts[1] in single_op:
                alu = alu_map[parts[1]]
                input_reg = input_reg_map[parts[0]]
            return f'{alu}{input_reg}','0'

        if len(parts) == 3:
            # Find the operation and registers regardless of position
            op = None
            registers = []

            for part in parts:
                if part in alu_map:
                    op = part
                elif part in input_reg_map:
                    registers.append(part)

            if op and len(registers) == 2:
                alu = alu_map[op]
                
                # Combine register flags using bitwise OR
                reg1_flags = int(input_reg_map.get(registers[0], '000'), 2)
                reg2_flags = int(input_reg_map2.get(registers[1], '000'), 2)

                input_reg = format(reg1_flags | reg2_flags,'03b')

                return f'{alu}{input_reg}','0'

        return None, None

    def assemble_line(self, line: str) -> Optional[str]:
        '''
        Assemble single line into binary instruction
        Format: destination=calculation;jump
        to: mode[15],safe_addr[14-10], (data[7-0]) / jump[9-7], alu[6-3], input_register[2-0]
        '''
        try:
            if not line or line.isspace() or line.startswith(';'):
                return None

            if line.upper().startswith('DEFINE'):
                self.parse_constant(line)
                return None

            # Initialize instruction parts
            mode = '0'
            save_addr = '00000'  # No save by default
            jump = '000'      # No jump by default
            calculation = '0000000' # alu + input_register or data
            
            # Parse instruction parts
            if '=' in line:
                destinations, rest = line.split('=', 1)
                save_addr = self.parse_addr(destinations)
            else:
                # line contains no save
                rest = line
            
            if mode == '0':
                if ';' in rest:
                    # Parse jump
                    rest, jump_part = rest.split(';', 1)
                    jump = self.parse_jump(jump_part)
                elif len(rest.split()) == 1 and save_addr == '00000':
                    # test for only jmp
                    can_jump = self.parse_jump(rest)
                    if can_jump == '111':
                        jump = can_jump
                        rest = ''
            
            # middle part (alu and reg_select or Number)
            if len(rest.split()) <= 3 and  not rest.split() == []:
                calculation, mode = self.parse_calc(rest)
            
            # Combine all parts into 16-bit instruction
            if mode == '0':
                instruction = f'{mode}{save_addr}{jump}{calculation}'
            else:
                instruction = f'{mode}{save_addr}00{calculation}'
            return instruction
        except Exception as e:
            print(f'Error assembling line {self.current_line}: {e}')
            return None

    def compile(self, input_file: str, output_file: str) -> None:
        '''
        Compile assembly file to binary/hex output

        compiling structures like functions, stack...
        -> Tokenizer(create Tokens from input) -> Parser(create syntaxtree + rework tokens)
        '''
        success, path, f = open_file(input_file)
        if not success:
            print(f'Could not open input file: {input_file}')
            return
        # Determine output- and temp- file path
        output_file = os.path.join(os.path.dirname(path), output_file)

        #write to output
        try:
            with open(output_file, 'w') as out:
                for line_num, line in enumerate(f, 1):
                    self.current_line = line_num
                    instruction = self.assemble_line(line.strip())
                    if instruction:
                        out.write(f'{instruction}\n')
                        print(instruction)
        finally:
            f.close()

# Usage
if __name__ == '__main__':
    compiler = Compiler()
    compiler.compile('input.txt', 'binaer.txt')
    txt_to_bin('binaer.txt','output.bin')