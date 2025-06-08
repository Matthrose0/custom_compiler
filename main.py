#import os
from utils import Utils, Config
from translator import Translator
from structureHandler import StructureHandler

def main():
    success, path, code = Utils.open_file('input_Main.txt')
    if success:
        Config.load_config()

        # Determine output- and temp- file path
        #temp_file = os.path.join(os.path.dirname(path), 'temp.txt')

        #translator = Translator()

        # Test cases
        #print(translator.translate_lines(['LO=A+A+D-3-5+LO-M']))
        #print(translator.translate_lines(['LO=A^A']))
        #print(translator.translate_lines(['LO=A ^ A + A - D + 5']))
        #print(translator.translate_lines(['LO=!HI']))
        #print(translator.translate_lines(['JMP']))
        #print(translator.translate_lines(['LO=5;JGE']))
        #print(translator.translate_lines(['LABEL begini','JUMP_TO 0xff 0xff','D=begini']))
        #print(translator.translate_lines(['LABEL begini','JUMP_TO 0xff 0xff','D=begini']))


        handler = StructureHandler()
        handler.parse(code)
        print(handler.structures)
        handler.display_structure()
    else:
        print(f'Could not open input file: input.txt')

if __name__ == "__main__":
    main()
    print('___')
