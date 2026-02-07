import os
# import sys

class Config:
    @staticmethod
    def load_dependencys(file_name: str):
        ...

class Utils:
    @staticmethod
    def open_file(file_name: str, mode: str = 'r') -> tuple[str, list[str]]:
        # Try absolute or given path
        if os.path.exists(file_name):
            return file_name, open(file_name, mode).readlines()

        # Try relative to script path
        base_path = os.path.dirname(os.path.abspath(__file__))
        relative_path = os.path.join(base_path, file_name)

        if os.path.exists(relative_path):
            return str(relative_path), open(relative_path, mode).readlines()

        # Raise error if file not found
        raise FileNotFoundError(f"File '{file_name}' not found (tried absolute and relative path)")
    
    # @staticmethod
    # def log(msg: str, level: str, exit_p: bool = False):
    #     colors = {
    #         'OKCYAN': '\033[96m',
    #         'OKGREEN': '\033[92m',
    #         'WARNING': '\033[93m',
    #         'ERROR': '\033[91m',
    #         'ENDC': '\033[0m',
    #         'BOLD': '\033[1m',
    #         'UNDERLINE': '\033[4m'
    #     }
       
    #     print(f'{colors.get(level.upper(), '')}{level.upper()}: {msg}{colors['ENDC']}')
    #     if exit_p and level.lower() == 'error':
    #         sys.exit(1)
    
    # @staticmethod
    # def change_content(structure: list = None, func: callable = None) -> list:
    #     if func is None:
    #         return None
    #         # structure = self.structure

    #     for i, block in enumerate(structure):
    #         if isinstance(block, str):
    #             structure[i] = func(block)
    #         elif isinstance(block, dict):
    #             for j, item in enumerate(block["content"]):
    #                 if isinstance(item, str):
    #                     block["content"][j] = func(item)
    #                 elif isinstance(item, dict):
    #                     Utils.change_content([item], func)
    #     return structure
  
    # @staticmethod
    # def split_instruction(line: str) -> tuple:
    #     '''splits an assembly instruction'''
    #     jump = None
    #     dest = None
    #     calc = None
    #     line = line.strip()

    #     if line == 'JMP':
    #         return dest, calc, line

    #     instruction_parts = line.split(';', 1)
    #     if len(instruction_parts) > 1:
    #         jump = instruction_parts[1].strip()

    #     assignment = instruction_parts[0].split('=', 1)
    #     if len(assignment) > 1:
    #         dest = assignment[0].strip()
    #         calc = assignment[1].strip()
    #     else:
    #         calc = instruction_parts[0]

    #     return dest, calc, jump

    # @staticmethod
    # def convert_num(value: str, line: int = None) -> int:
    #     """Converts hex/bin to decimal within valid range"""
    #     value = Config.constants.get(value, value)
    #     n_range = '-128 <= num <= 127'

    #     try:
    #         if not value.lstrip('-').isdigit():
    #             n_range = '0 <= num <= 255'
    #         num = int(value, 0)
    #     except ValueError:
    #         raise ValueError(f"Invalid number format: '{value}' in line {line}")

    #     if eval(n_range):
    #         return num
    #     raise ValueError(f"Number out of range ({n_range}): '{value}' in line {line}")