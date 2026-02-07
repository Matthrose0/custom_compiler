#from utils import Utils, Config
import structure_handler


if __name__ == "__main__":
    try:
        with open('input_Main.txt', 'r') as file:
            code = file.readlines()
    except FileNotFoundError:
        print("File 'input_Main.txt' not found")
        code=[]
    except Exception as e:
        print(f"Error: {e}")
        code=[]


    handler = structure_handler.run(code)