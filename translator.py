import re
from utils import Utils, Config

class Translator:
    """Translates high-level assembly into low-level assembly"""
    def __init__(self, output_file="intermediate.asm"):
        self.output_file = output_file
        self.current_line = -1
        self.label_counter = 0
        self.new_labels = []
        
        # Clear output file
        open(self.output_file, 'w').close()

        # Prepare tokenizer patterns
        self.token_patterns = [
            (f'(?:{Config.alu_op_pattern})', "<OPERATOR>"),
            (r'0[xX][0-9A-Fa-f]+|0[bB][01]+|\d+', "<NUMBER>"),
            (r'[a-zA-Z0-9_]+', "<IDENTIFIER>"),
        ]
        self.token_regex = re.compile("|".join(f"({pattern})" for pattern, _ in self.token_patterns))

    def translate_lines(self, lines):
        """Translates multiple lines + label management"""
        lines = [line.upper() for line in lines]
        
        # Process labels
        label_map = {}
        new_lines = []
        for line in lines:
            match = re.match(r'LABEL\s+(\w+)', line)
            if match:
                label = match.group(1)
                new_label = f"{label}_{self.label_counter}"
                self.label_counter += 1
                label_map[label] = new_label
                self.new_labels.append(new_label)
                new_lines.append('LABEL '+ new_label)
            else:
                new_lines.append(line)

        # Replace labels in lines
        for key, value in label_map.items():
            new_lines = [re.sub(rf'\b{re.escape(key)}\b', value, line) for line in new_lines]

        # Translate each line
        instructions = []
        for line in new_lines:
            self.current_line += 1
            translated = self._translate_line(line, self.current_line)
            if translated:
                instructions.extend(translated)
        return instructions
    
    def _translate_line(self, line, line_num):
        """Translates a single line"""
        line_parts = line.split()
        if not line_parts:
            return []
            
        # Handle macros
        if line_parts[0] in Config.macros:
            return self._expand_macro(line_parts[0], *line_parts[1:])
        
        # Handle constants
        if len(line_parts) == 3 and line_parts[0] == "CONST":
            num = Utils.convert_num(line_parts[2], line_num)
            if num != '0x0':
                Config.constants[line_parts[1]] = line_parts[2]
            return []
        
        # Handle labels
        if line.startswith('LABEL '):
            return [line]

        # Handle instructions
        save_addr, calculation, jmp = Utils.split_instruction(line)
        if save_addr is None and calculation is None and jmp == 'JMP': 
            return [jmp]
        return self.translate_calc_line(calculation, save_addr, jmp, line_num)
    
    def _expand_macro(self, macro_name, *args):
        """Processes a macro and replaces placeholders with arguments"""
        macro = Config.macros.get(macro_name)
        if not macro:
            raise ValueError(f"Macro '{macro_name}' not found")

        # Check if enough arguments are provided
        if len(args) < len(macro['params']):
            raise ValueError(f"Missing argument for macro '{macro_name}': expected {len(macro['params'])}, got {len(args)}")
            
        # Replace parameters
        body = macro['body']
        for i, key in enumerate(macro['params']):
            body = re.sub(rf'\b{re.escape(key)}\b', args[i], body)
        
        return self.translate_lines(body.splitlines())

    def translate_calc_line(self, calculation, save_addr=None, jmp=None, input_line=0):
        """Transforms a complex calculation into simple assembly instructions."""
        if not calculation:
            Utils.log(f'Empty expression in line {input_line}', 'error')
            return None
        
        # Tokenize and analyze
        tokens = self._tokenize(calculation)
        if not tokens:
            return None
        
        analysis = self._analyze_tokens(tokens, input_line)
        if not self._is_operation_possible(analysis):
            Utils.log(f'Cannot perform operation in line {input_line}: {calculation}', 'error')
            return None

        return self._generate_instructions(analysis, save_addr, jmp, input_line)
        
    def _tokenize(self, line):
        """Tokenizes an input line"""
        line = line.upper().strip()
        tokens = []

        for match in self.token_regex.finditer(line):
            token_value = None
            token_type = None

            # Find token type
            for group_index, (_, type_name) in enumerate(self.token_patterns, start=1):
                if match.group(group_index):
                    token_value = match.group(group_index)
                    token_type = type_name
                    break
            
            # Validate operator
            if token_type == "<OPERATOR>" and token_value not in Config.alu_op_list:
                Utils.log(f'Invalid operator found: {token_value}', 'error')
                return []
            
            tokens.append((token_value, token_type))
        
        return tokens
    
    def _analyze_tokens(self, tokens, line):
        """Analyzes tokens and optimizes constant expressions"""
        analysis = {
            'registers': {},
            'working_register': 'A',
            'constant': 0,
            'operations': [],
        }

        current_op = '+'  # Default operation
        for token, type_ in tokens:
            if type_ == '<OPERATOR>':
                current_op = token
            elif type_ == '<NUMBER>' or token in Config.constants:
                num = Utils.convert_num(token, line)
                if current_op in ('+', '-'):
                    analysis['constant'] = analysis['constant'] + num if current_op == '+' else analysis['constant'] - num
                else:
                    analysis['operations'].append(('constant', current_op, num))
            elif type_ == '<IDENTIFIER>' and token in Config.output_reg_map:
                if token in ('A', 'D'):
                    analysis['registers'][token] = analysis['registers'].get(token, 0) + 1
                analysis['operations'].append(('register', current_op, token))
            elif type_ == '<IDENTIFIER>' and token in self.new_labels:
                analysis['operations'].append(('label', current_op, token))
            else:
                Utils.log(f'Unknown IDENTIFIER in line {line}: {token}', 'error')
            
            if type_ != "<OPERATOR>":
                current_op = '+'  # Reset operator
        
        # Choose working register
        if 'A' in analysis['registers'] and analysis['registers']['A'] > 1:
            analysis['working_register'] = 'D'

        return analysis
    
    def _generate_instructions(self, analysis, save_addr, jmp, line):
        """Generates assembly instructions from analyzed expression"""
        instructions = []
        operations = analysis.get('operations', [])
        work_reg = analysis.get('working_register', 'A')
        second_reg = 'A' if work_reg == 'D' else 'D'
        constant = hex(analysis.get('constant', 0) & 0xFF)
        final_reg = f'{save_addr} = ' if save_addr else ''

        # Validate operations
        if not all(op_type in ('register', 'label') for op_type, _, _ in operations):
            Utils.log(f"Unhandled operation types in line {line}", 'error')
            return None
        
        # Handle different operation counts
        if len(operations) == 1:
            # Single operation
            _, first_op, value = operations[0]
            if first_op == '+':
                instructions.append(f"{final_reg}{value}")
            elif first_op in Config.single_op:
                instructions.append(f"{final_reg}{first_op} {value}")
            else:
                Utils.log(f"Unsupported operation in line {line}: {first_op}", 'error')
                return None
                
        elif len(operations) == 2:
            # Two operations
            (_, first_op, first_val), (_, second_op, second_val) = operations
            if first_op == '+':
                if first_val == second_val:
                    instructions.append(f"{work_reg} = {first_val}")
                    instructions.append(f"{final_reg}{work_reg} {second_op} {second_val}")
                else:
                    instructions.append(f"{final_reg}{first_val} {second_op} {second_val}")
            elif first_op in Config.single_op:
                instructions.append(f"{work_reg} = {first_op} {first_val}")
                instructions.append(f"{final_reg}{work_reg} {second_op} {second_val}")
            else:
                Utils.log(f"Unsupported operation in line {line}: {first_op}", 'error')
                return None
                
        elif len(operations) > 2:
            # Multiple operations
            _, first_op, first_val = operations[0]
            _, second_op, second_val = operations[1]

            # Initialize working register
            if first_op == '+':
                if first_val == second_val:
                    instructions.append(f"{work_reg} = {first_val}")
                    operations = operations[1:]
                elif first_val != work_reg:
                    instructions.append(f"{work_reg} = {first_val} {second_op} {second_val}")
                    operations = operations[2:]
            else:
                instructions.append(f"{work_reg} = {first_op} {first_val}")
                operations = operations[1:]

            # Process remaining operations
            for _, op, value in operations:
                if value == work_reg:
                    # Handle register conflicts
                    if op == '+' or op in Config.single_op:
                        instructions.append(f"{second_reg} = {op if op in Config.single_op else ''}{value}")
                        instructions.append(f"{work_reg} = {work_reg} {op} {second_reg}")
                    else:
                        Utils.log(f"Unsupported operation in line {line}: {op}", 'error')
                        return None
                else:
                    instructions.append(f"{work_reg} = {work_reg} {op} {value}")
            
            # Fix the last instruction
            instructions.pop(-1)
            instructions.append(f"{final_reg}{work_reg} {op} {value}")

        # Add constant if needed
        if constant != '0x0':
            if not instructions:
                instructions.append(f"{final_reg}{constant}")
            else:
                instructions.append(f"{second_reg} = {constant}")
                instructions.append(f"{final_reg}{work_reg} + {second_reg}")

        # Add jump if needed
        if jmp:
            instructions[-1] += f";{jmp}"

        return instructions

    def _is_operation_possible(self, analysis):
        """Checks if operation is possible without data loss"""
        reg_counts = analysis['registers']
        
        # Can't use both A and D more than once
        if 'A' in reg_counts and 'D' in reg_counts:
            return not (reg_counts['A'] > 1 and reg_counts['D'] > 1)
        return True