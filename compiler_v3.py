import os
import re
import yaml

macros = {}
alu_map = {}
alu_op_list = []
alu_op_pattern: str
single_op: list[str] = []
input_reg_map = {}
input_reg_map2 = {}
output_reg_map = {}
jmp_map = {}

class Utils:
    @staticmethod
    def open_file(file_name: str, mode: str = 'r') -> tuple[bool, str, any]:
        if os.path.exists(file_name):
            return True, file_name, open(file_name, mode)

        base_path = os.path.dirname(os.path.abspath(__file__))
        relative_path = os.path.join(base_path, file_name)

        if os.path.exists(relative_path):
            return True, str(relative_path), open(relative_path, mode)

        return False, "", None
    
    @staticmethod
    def log(msg: str, level: str):
        colors = {
            'OKCYAN': '\033[96m',
            'OKGREEN': '\033[92m',
            'WARNING': '\033[93m',
            'ERROR': '\033[91m',
            'ENDC': '\033[0m',
            'BOLD': '\033[1m',
            'UNDERLINE': '\033[4m'
        }
        print(f'{colors.get(level.upper(),'')}{level.upper()}: {msg}{colors['ENDC']}')
    
    @staticmethod
    def load_config(config_file: str):
        global macros, alu_map, alu_op_list, alu_op_pattern, single_op, input_reg_map, input_reg_map2, output_reg_map, jmp_map

        if config_file == None:
            config_file = 'config.yaml'
        f = Utils.open_file(config_file)[2]
        
        config = yaml.safe_load(f)
        instruction_maps = config.get('instruction_maps')

        macros = config.get('macros', {})
        alu_map = instruction_maps.get('alu_map', {})
        alu_op_list = sorted(alu_map.keys(), key=len, reverse=True)
        alu_op_pattern = '|'.join(re.escape(op) for op in alu_op_list)
        single_op = instruction_maps.get('single_op', {})
        single_op.sort(key=len, reverse=True)

        input_reg_map = instruction_maps.get('input_reg_map', {})
        input_reg_map2 = instruction_maps.get('input_reg_map2', {})
        output_reg_map = instruction_maps.get('saveAddress_map', {})
        jmp_map = instruction_maps.get('jump_map', {})


class Compiler:
    '''
    Manages the entire process from tokenizing, parsing ... to a bin file
    ''' 
    """ others
    # def number_check(self, str_num: str) -> bool:
    #     '''check for numeric value in 8bit region'''
    #     if str_num.strip().isdigit():
    #         num = int(str_num.strip())
    #         return num < 128 and num > -128

    # def parse_constant(self, line: str) -> None:
    #     '''Parse constant definition (e.g., 'DEFINE const_name=value')'''
    #     if line.upper().startswith('DEFINE'):
    #         name, value = line[6:].upper().split('=')
    #         if self.number_check(value):
    #             self.constants[name.strip()] = int(value.strip())

    # def compile(self, input_file: str, output_file: str) -> None:
        # '''
        # Compile assembly file to binary/hex output

        # compiling structures like functions, stack...
        # -> Tokenizer(create Tokens from input) -> Parser(create syntaxtree + rework tokens)
        # '''
        # success, path, f = Utils.open_file(input_file)
        # if not success:
        #     print(f'Could not open input file: {input_file}')
        #     return
        # # Determine output- and temp- file path
        # output_file = os.path.join(os.path.dirname(path), output_file)
        # temp_file = os.path.join(os.path.dirname(path), 'temp.txt')

        # tokenizer = Tokenizer(f,temp_file)
        # tokenizer.tokenize()

        
        # #write to output
        # try:
        #     with open(temp_file, 'w') as out:
        #         for line_num, line in enumerate(f, 1):
        #             self.current_line = line_num
        #             instruction = self.assemble_line(line.strip())
        #             if instruction:
        #                 out.write(f'{instruction}\n')
        #                 print(instruction)
        # finally:
        #     f.close()
    
    def __init__(self):
        self.structure:list = None

        self.structure_handler = StructureHandler()
        # self.tokenizer = Tokenizer()
        # self.writer = IntermediateFileWriter()
        # self.macro_handler = MacroHandler()
        # self.constants: Dict[str, int] = {}
    """
    
    def compile(self, input_file: str, output_file: str) -> None:
        """
        Compiles the input code into an intermediate file.
        
        Args:
            input_file (str): Path to the input code file.
            output_file (str): Path to the output intermediate file.
        """
        
        success, path, f = Utils.open_file(input_file)
        if not success:
            Utils.log(f'Could not open input file: {input_file}','error')
            return
        # Determine output- and temp- file path
        output_file = os.path.join(os.path.dirname(path), output_file)
        temp_file = os.path.join(os.path.dirname(path), 'temp.txt')

        # Filter first structures
        structured_code = StructureHandler.parse_code(f)
        #Utils.change_content(structured_code,)


class StructureHandler:
    """
    Handles complex structures like functions, loops, and conditions
    first breakdown from input-code + removing comments
    """
    def __init__(self):
        self.structure = []
    
    def parse_code(self, file) -> list:
        """
        Parse the code and extract structural blocks
        -> only head controlled structures are allowed

        Args:
            file -- input-file which is already opened
        Return:
            self.structure:list -- result of parsing with:
                str, dict['type','header','content'] (block from structure)
        """
        stack = []  # Stack to maintain the hierarchy

        for line_num, line in enumerate(file, 1):
            line = self.remove_comments(line).strip().upper()
            if not line:    # Skip empty lines
                continue

            if "{" in line:
                # Begin new structure
                block = self.identify_structure(line)
                if block:
                    # Handle closing brace with elif/else on same line
                    if stack and (block['type'] == 'elif' or block['type'] == 'else'):
                        stack.pop()
                    
                    # Continue to handle opening structure
                    if stack:
                        stack[-1]["content"].append(block)
                    else:
                        self.structure.append(block)
                    stack.append(block)
                else:
                    Utils.log(f"Structures - in line {line_num}: unknown structure type\n  latest known structure: {stack[-1] if len(stack) != 0 else 'None'}",'error')
            elif "}" in line:
                # End highest structure
                if stack:
                    stack.pop()
                else:
                    Utils.log(f"Structures - in line {line_num}: closing brace, without matching opening brace",'error')
            else:
                # Line counts to current structure
                if stack:
                    stack[-1]["content"].append(line)
                else:
                    self.structure.append(line)

    def display_structure(self, structure:list=None, level=0) -> None:
        """
        Display the parsed structure for debugging purposes
        """
        if structure is None:
            structure = self.structure
        
        for block in structure:
            if isinstance(block, str): 
                print("  " * level + block)
                continue
            print("  " * level + f"{block['type']}: {block['header']}")
            for item in block["content"]:
                if isinstance(item, dict):
                    self.display_structure([item], level + 1)
                else:
                    print("  " * (level + 1) + item)
    
    def identify_structure(self, line: str) -> dict:
        """
        Identifys the structure and creates a block
        """
        patterns = {
            r'^DEF\s+\w+\s*\(.*\)\s*{': "function",
            r'^IF\s*\(.*\)\s*{': "if",
            r'^}\s*ELIF\s*\(.*\)\s*{': "elif",
            r'^}\s*ELSE\s*{': "else",
            r'^FOR\s*\(.*\)\s*{': "for",
            r'^WHILE\s*\(.*\)\s*{': "while",
            r'^REPEAT\s*\(.*\)\s*{': "repeat"
        }

        block_type = None
        block = None

        for pattern, result in patterns.items():
            if re.match(pattern, line):
                block_type = result
                break
        
        if block_type:
            block = {
                "type": block_type,
                "header": self.extract_header(line, block_type),
                "content": [],
            }
        return block
    
    def extract_header(self, line: str, block_type: str) -> str:
        """
        Extracts the header information based on the block type
        """
        line = line.replace("}", "").strip()
        if block_type == "function":
            match = re.match(r'^def\s+(\w+\s*\(.*\))\s*{', line)
            return match.group(1) if match else line
        elif block_type in {"if", "elif", "for", "while", "repeat"}:
            match = re.match(r'^\w+\s*\((.*)\)\s*{', line)
            return match.group(1) if match else line
        elif block_type == "else":
            return ""  # No header content for 'else'
        else:
            return line
    
    def remove_comments(self, line:str) -> str:
        '''
        removing comments from a line of code
        '''
        comment_index = line.find('#')
        if comment_index != -1:
            line = line[:comment_index].strip()
        return line


    '''other things to do:
    def handle_function(self, tokens: list[str]) -> list[str]:
        """
        Converts function tokens into assembly code.
        
        Args:
            tokens (list[str]): Tokens belonging to a function.
        
        Returns:
            list[str]: Assembly instructions.
        """
        # Implement function handling logic.
        return []

    def handle_loop(self, tokens: list[str]) -> list[str]:
        """
        Converts loop tokens into assembly code.
        
        Args:
            tokens (list[str]): Tokens belonging to a loop.
        
        Returns:
            list[str]: Assembly instructions.
        """
        # Implement loop handling logic.
        return []

    def handle_condition(self, tokens: list[str]) -> list[str]:
        """
        Converts conditional tokens into assembly code.
        
        Args:
            tokens (list[str]): Tokens belonging to a condition.
        
        Returns:
            list[str]: Assembly instructions.
        """
        # Implement condition handling logic.
        return []
    '''

# test Main
success, path, f = Utils.open_file('input_Main.txt')
if success:
    Utils.load_config(None)

    # Determine output- and temp- file path
    temp_file = os.path.join(os.path.dirname(path), 'temp.txt')

    compiler = Compiler()
    handler = StructureHandler()

    handler.parse_code(f)
    #with open(temp_file, 'w') as file:
    #    for line in assembler.assemble(f):
    #        file.write(line+'\n')


    # cont = Utils.change_content(handler.structure,lambda x : 'hi')
    # print(cont)
    handler.display_structure()

else: print(f'Could not open input file: {'input_Main.txt'}')

