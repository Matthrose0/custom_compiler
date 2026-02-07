from structure_handler.tree_builder import TreeBuilder
from structure_handler.extractor import Extractor
from structure_handler.resolver import Resolver

def run(raw_text: list[str]) -> tuple[dict[str, list[str]], dict[str, list[str]], list[str]]:
    treeBuilder = TreeBuilder()
    
    tree = treeBuilder.build(raw_text)

    

    tree, functions, macros = Extractor().extract(tree)

    print(functions,"\n", macros)

    treeBuilder.display_structure(tree)

    Resolver().resolve(tree)
    for structure_dict in [functions, macros]:
        for callableStructureTupel in structure_dict.values():
            Resolver().resolve(callableStructureTupel.content)
    
    
    
    treeBuilder.display_structure(tree)
    print(functions,"\n", macros)


    
    # parsed_structures = handler.parse(code)
    # 
    # print("Parsed structures:")
    # for i, struct in enumerate(parsed_structures):
        # print(f"{i}: {struct}")
    # 
    # print("\nStructure tree:")
    # handler.display_structure(parsed_structures)

    return {},{},[]


