import os
import re
import yaml
import sys

class Config:
    functions = {}
    used_functions = {}
    macros = {}
    constants = {}
    alu_map = {}
    alu_op_list = []
    alu_op_pattern: str
    single_op: list[str] = []
    input_reg_map = {}
    output_reg_map = {}
    jmp_map = {}

    @staticmethod
    def load_config(config_file: str = 'config.yaml') -> None:
        success, path, f = Utils.open_file(config_file)
        if not success:
            raise FileNotFoundError(f"Configuration file '{config_file}' not found.")
        
        config = yaml.safe_load(f)
        instruction_maps = config.get('instruction_maps', {})

        Config.macros = config.get('macros', {})
        Config.alu_map = instruction_maps.get('alu_map', {})
        Config.alu_op_list = sorted(Config.alu_map.keys(), key=len, reverse=True)
        Config.alu_op_pattern = '|'.join(re.escape(op) for op in Config.alu_op_list)
        Config.single_op = instruction_maps.get('single_op', [])
        Config.single_op.sort(key=len, reverse=True)

        Config.input_reg_map = instruction_maps.get('input_reg_map', {})
        Config.output_reg_map = instruction_maps.get('saveAddress_map', {})
        Config.jmp_map = instruction_maps.get('jump_map', {})
    
    @staticmethod
    def load_dependencys(file_name: str):
        ...

class Utils:
    @staticmethod
    def open_file(file_name: str, mode: str = 'r') -> tuple[bool, str, list[str]]:
        if os.path.exists(file_name):
            return True, file_name, open(file_name, mode)

        base_path = os.path.dirname(os.path.abspath(__file__))
        relative_path = os.path.join(base_path, file_name)

        if os.path.exists(relative_path):
            return True, str(relative_path), open(relative_path, mode).readlines()

        return False, "", None
    
    @staticmethod
    def log(msg: str, level: str, exit_p: bool = False):
        colors = {
            'OKCYAN': '\033[96m',
            'OKGREEN': '\033[92m',
            'WARNING': '\033[93m',
            'ERROR': '\033[91m',
            'ENDC': '\033[0m',
            'BOLD': '\033[1m',
            'UNDERLINE': '\033[4m'
        }
       
        print(f'{colors.get(level.upper(), '')}{level.upper()}: {msg}{colors['ENDC']}')
        if exit_p and level.lower() == 'error':
            sys.exit(1)
    
    @staticmethod
    def txt_to_bin(input_file, output_file):
        try:
            success, path, f = Utils.open_file(input_file)
            if not success: 
                Utils.log_and_exit(f"File {input_file} not found.", 'error')
            
            bit_content = ''.join(char for char in f.read() if char in ['0', '1'])
            output_file = os.path.join(os.path.dirname(path), output_file)
            
            with open(output_file, 'wb') as outfile:
                byte_array = int(bit_content, 2).to_bytes((len(bit_content) + 7) // 8, byteorder='big')
                outfile.write(byte_array)
            
            Utils.log(f"Successfully converted {input_file} to {output_file}", 'okgreen')
        except ValueError:
            Utils.log_and_exit("Invalid bits in file (only '0' and '1' allowed)", 'error')
        except Exception as e:
            Utils.log_and_exit(f"Error occurred: {e}", 'error')
    
    @staticmethod
    def change_content(structure: list = None, func: callable = None) -> list:
        if func is None:
            return None
            # structure = self.structure

        for i, block in enumerate(structure):
            if isinstance(block, str):
                structure[i] = func(block)
            elif isinstance(block, dict):
                for j, item in enumerate(block["content"]):
                    if isinstance(item, str):
                        block["content"][j] = func(item)
                    elif isinstance(item, dict):
                        Utils.change_content([item], func)
        return structure
  
    @staticmethod
    def split_instruction(line: str) -> tuple:
        '''splits an assembly instruction'''
        jump = None
        dest = None
        calc = None
        line = line.strip()

        if line == 'JMP':
            return dest, calc, line

        instruction_parts = line.split(';', 1)
        if len(instruction_parts) > 1:
            jump = instruction_parts[1].strip()

        assignment = instruction_parts[0].split('=', 1)
        if len(assignment) > 1:
            dest = assignment[0].strip()
            calc = assignment[1].strip()
        else:
            calc = instruction_parts[0]

        return dest, calc, jump

    @staticmethod
    def convert_num(value: str, line: int = None) -> int:
        """Converts hex/bin to decimal within valid range"""
        value = Config.constants.get(value, value)
        n_range = '-128 <= num <= 127'

        try:
            if not value.lstrip('-').isdigit():
                n_range = '0 <= num <= 255'
            num = int(value, 0)
        except ValueError:
            raise ValueError(f"Invalid number format: '{value}' in line {line}")

        if eval(n_range):
            return num
        raise ValueError(f"Number out of range ({n_range}): '{value}' in line {line}")