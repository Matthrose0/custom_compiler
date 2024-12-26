import os

def open_file(file_name: str) -> tuple[bool, str, any]:
    """
    attempts to open a file, first directly, then as a relative path from the main program
    
    args:
        file_name: Name/path of the file
        
    returns:
        tuple: (success, file path, file handle or None)
    """
    # direct attempt to open the file
    if os.path.exists(file_name):
        return True, file_name, open(file_name, 'r')
    
    # try relative path from the main program location
    base_path = os.path.dirname(os.path.abspath(__file__))
    relative_path = os.path.join(base_path, file_name)
    
    if os.path.exists(relative_path):
        return True, str(relative_path), open(relative_path, 'r')
        
    return False, "", None
def assemble(s: str) -> list[str]:
    mode = 0
    tokens_adr = []
    tokens = []
    jmp = ""

    if "=" in s:
        tokens_adr, s = s.split('=', 1)
        tokens_adr = tokens_adr.split(',')
    else:
        tokens_adr = []
    
    if ";" in s:
        s, jmp = s.split(';', 1)
    
    tokens = s.split()

    for token in tokens:
        if token.isdigit():
            if jmp == '':
                mode = 1
            else:
                print('E: could not operate in different modes at the same time')
                return [None]
        #if token
        # adding other functions for Stack


    print(mode)
    print(tokens_adr)
    print(tokens)
    print(jmp)

   

def tokenize(s: str) -> list[str]:#not ready
    """
    transform high language to low language
    """
    tokens = s.split()

    for token in tokens:
        if token.isdigit():
            pass

    return tokens
def compile(input_file: str, output_file: str):
    """
    ...
    
    args:
        
        
    returns:
        ...
    """
    success, path, f = open_file(input_file)

    if not success:
        print("File not found")
        return

    assemble(f.readline())





compile('test.py','')

