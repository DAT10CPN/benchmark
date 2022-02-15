import os
import xml.etree.ElementTree as ET
from pathlib import Path

LOGGING = True


def main():
    NAMESPACE = '{http://www.pnml.org/version-2009/grammar/pnml}'
    ET.register_namespace('', 'http://www.pnml.org/version-2009/grammar/pnml')

    script_dir = os.path.dirname(__file__)
    MCC_DIRECTORY = os.path.join(script_dir, '..\\..\\..\\mcc2021-COL\\')

    graph_dir = os.path.join(script_dir, 'extracted\\')
    if not os.path.isdir(graph_dir):
        os.makedirs(graph_dir)
    for test_folder in os.listdir(MCC_DIRECTORY):
        if test_folder != 'SafeBus-COL-03':
            continue

        final_to_file = f""
        final_to_file = final_to_file + (f"Test: {test_folder}")
        if LOGGING:
            print(f"Test: {test_folder}")
        model_path = Path(os.path.join(MCC_DIRECTORY), f'{test_folder}\\model.pnml')
        mytree = ET.parse(model_path)
        myroot = mytree.getroot()
        net = myroot.find(f'{NAMESPACE}' + 'net')
        page = net.find(f'{NAMESPACE}' + 'page')

        # Find declarations
        declaration = net.findall(f'{NAMESPACE}' + 'declaration')
        structure = declaration[0].findall(f'{NAMESPACE}' + 'structure')
        declarations = structure[0].findall(f'{NAMESPACE}' + 'declarations')

        # ALL conditions on transitions
        final_to_file = final_to_file + "\n" + "-------GUARDS-------"
        if LOGGING:
            print("-------GUARDS-------")
        all_conditions_text = []
        transitions = page.findall(f'{NAMESPACE}' + 'transition')
        for transition in transitions:
            conditions = transition.findall(f'{NAMESPACE}' + 'condition')
            for condition in conditions:
                text = condition.findall(f'{NAMESPACE}' + 'text')

                all_conditions_text.append(text[0].text)

        if len(all_conditions_text) == 0:
            all_conditions_text = "No condition"

        for condition in all_conditions_text:
            final_to_file = final_to_file + "\n" + condition
            if LOGGING:
                print(condition)

        # Find all variables used
        final_to_file = final_to_file + "\n" + "-------VARIABLES-------"
        if LOGGING:
            print("-------VARIABLES-------")
        for variabledecl in declarations[0].findall(f'{NAMESPACE}' + 'variabledecl'):
            for usersort in variabledecl.findall(f'{NAMESPACE}' + 'usersort'):
                variable_declaration = f"Variable decl attrib: {variabledecl.attrib}, with declaration: {usersort.attrib}"
                final_to_file = final_to_file + "\n" + variable_declaration
                if LOGGING:
                    print(variable_declaration)

        # Find ranges of colors
        final_to_file = final_to_file + "\n" + "-------RANGES-------"
        if LOGGING:
            print("-------RANGES-------")
        for named_sort in declarations[0].findall(f'{NAMESPACE}' + 'namedsort'):
            min_range = None
            max_range = None
            for cyclicenumeration in named_sort.findall(f'{NAMESPACE}' + 'cyclicenumeration'):
                for feconstant in cyclicenumeration.findall(f'{NAMESPACE}' + 'feconstant'):
                    if min_range is None or int(feconstant.attrib['name']) < min_range:
                        min_range = int(feconstant.attrib['name'])
                    if max_range is None or int(feconstant.attrib['name']) > max_range:
                        max_range = int(feconstant.attrib['name'])
            if min_range is None and max_range is None:
                for finiteintrange in named_sort.findall(f'{NAMESPACE}' + 'finiteintrange'):
                    if len(finiteintrange) > 1:
                        print("Multiple finiteintranges")
                    min_range = finiteintrange.attrib['start']
                    max_range = finiteintrange.attrib['end']
            if min_range is None and max_range is None:
                for productsort in named_sort.findall(f'{NAMESPACE}' + 'productsort'):
                    product = []
                    for usersort in productsort.findall(f'{NAMESPACE}' + 'usersort'):
                        product.append(usersort.attrib['declaration'])
                    final_to_file = final_to_file + "\n" + f"Usersort {named_sort.attrib} has product: {product}"
                    if LOGGING:
                        print(f"Usersort {named_sort.attrib} has product: {product}")
            var_range = f"{named_sort.attrib['id']} has Range: [{str(min_range)},{str(max_range)}]"
            if str(min_range) is None and str(max_range) is None:
                final_to_file = final_to_file + "\n" + var_range
                if LOGGING:
                    print(var_range)
        final_to_file = final_to_file + "\n" + "-------ARCS-------"
        final_to_file = final_to_file + "\n" + "TODO"
        if LOGGING:
            print("-------ARCS-------")
            print("TODO")

        final_to_file = final_to_file + "\n" + "------------------------------------------------------------------"
        if LOGGING:
            print("------------------------------------------------------------------")

        with open(f"extracted/{test_folder}.txt", "w") as file:
            # Writing data to a file
            file.write(final_to_file)


if __name__ == "__main__":
    main()
