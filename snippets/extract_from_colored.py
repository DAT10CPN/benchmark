import os
import xml.etree.ElementTree as ET
from pathlib import Path

LOGGING = False
TESTING = False
test_model = 'Sudoku-COL-AN16'


def main():
    NAMESPACE = '{http://www.pnml.org/version-2009/grammar/pnml}'
    ET.register_namespace('', 'http://www.pnml.org/version-2009/grammar/pnml')

    script_dir = os.path.dirname(__file__)
    MCC_DIRECTORY = os.path.join(script_dir, '..\\..\\mcc2021-COL\\')
    extracted_folder = '..\\static_data\\extracted\\'

    graph_dir = os.path.join(script_dir, extracted_folder)
    if not os.path.isdir(graph_dir):
        os.makedirs(graph_dir)

    all_guards = ""
    for test_folder in os.listdir(MCC_DIRECTORY):
        if TESTING:
            if test_folder != test_model:
                continue

        final_to_file = ""
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
        transitions = page.findall(f'{NAMESPACE}' + 'transition')
        arcs = page.findall(f'{NAMESPACE}' + 'arc')

        # Some stats
        final_to_file = final_to_file + (f"\nTransitions: {len(transitions)}")
        final_to_file = final_to_file + (f"\nArcs: {len(arcs)}")
        if LOGGING:
            print(f"Transitions: {len(transitions)}")
            print(f"Arcs: {len(arcs)}")

        named_sort_ids = []
        # Find ranges of colors
        final_to_file = final_to_file + "\n" + "-------SORTS-------"
        if LOGGING:
            print("-------SORTS-------")
        for named_sort in declarations[0].findall(f'{NAMESPACE}' + 'namedsort'):
            named_sort_ids.append(named_sort.attrib['id'])
            if named_sort.attrib['id'] == "dot":
                final_to_file = final_to_file + "\n" + f"Named sort: {named_sort.attrib}"
                if LOGGING:
                    print(f"Named sort: {named_sort.attrib}")

            min_range = None
            max_range = None
            for cyclicenumeration in named_sort.findall(f'{NAMESPACE}' + 'cyclicenumeration'):
                feconstants = cyclicenumeration.findall(f'{NAMESPACE}' + 'feconstant')
                if not feconstants[0].attrib['name'].isdigit():
                    values = []
                    for feconstant in feconstants:
                        values.append(feconstant.attrib['name'])

                    final_to_file = final_to_file + "\n" + f"Named sort: {named_sort.attrib} has values: {values}"
                    if LOGGING:
                        print(f"Named sort: {named_sort.attrib} has values: {values}")
                    continue

                for feconstant in feconstants:
                    if min_range is None or int(feconstant.attrib['name']) < min_range:
                        min_range = int(feconstant.attrib['name'])
                    if max_range is None or int(feconstant.attrib['name']) > max_range:
                        max_range = int(feconstant.attrib['name'])
                if not (min_range is None) and not (max_range is None):
                    final_to_file = final_to_file + "\n" + f"Named sort: {named_sort.attrib} has ranges: [{min_range},{max_range}]"
                    if LOGGING:
                        print(f"Named sort: {named_sort.attrib} has ranges: [{min_range},{max_range}]")
            if min_range is None and max_range is None:
                for finiteintrange in named_sort.findall(f'{NAMESPACE}' + 'finiteintrange'):
                    if len(finiteintrange) > 1:
                        print("Multiple finiteintranges")
                    min_range = finiteintrange.attrib['start']
                    max_range = finiteintrange.attrib['end']

                var_range = f"Usersort {named_sort.attrib} has Range: [{str(min_range)},{str(max_range)}]"
                if min_range and max_range:
                    final_to_file = final_to_file + "\n" + var_range
                    if LOGGING:
                        print(var_range)

            if min_range is None and max_range is None:
                for productsort in named_sort.findall(f'{NAMESPACE}' + 'productsort'):
                    product = []
                    for usersort in productsort.findall(f'{NAMESPACE}' + 'usersort'):
                        product.append(usersort.attrib['declaration'])
                    final_to_file = final_to_file + "\n" + f"Usersort {named_sort.attrib} is a product: {product}"
                    if LOGGING:
                        print(f"Usersort {named_sort.attrib} is a product: {product}")

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

        # ALL conditions on transitions
        final_to_file = final_to_file + "\n" + "-------GUARDS-------"
        if LOGGING:
            print("-------GUARDS-------")

        for transition in transitions:
            conditions = transition.findall(f'{NAMESPACE}' + 'condition')
            for condition in conditions:
                text = condition.find(f'{NAMESPACE}' + 'text').text

                if text == "":
                    text = "No guard"
                final_to_file = final_to_file + "\n" + text
                all_guards = all_guards + "\n" + text
                if LOGGING:
                    print(text)

        # ALL conditions on transitions
        final_to_file = final_to_file + "\n" + "-------TRANSITIONS-------"
        if LOGGING:
            print("-------TRANSITIONS-------")

        for transition in transitions:
            transition_id = transition.attrib['id']
            condition = transition.find(f'{NAMESPACE}' + 'condition')

            if condition:
                guard = condition.find(f'{NAMESPACE}' + 'text').text
                if guard == "":
                    guard = "No guard"
            else:
                guard = "No guard"

            arcs_descriptions = []
            for arc in arcs:
                hlinscription = arc.find(f'{NAMESPACE}' + 'hlinscription')
                text = hlinscription.find(f'{NAMESPACE}' + 'text').text
                if transition_id == arc.attrib['source']:
                    arcs_descriptions.append(f"Outgoing arc: {text}")
                if transition_id == arc.attrib['target']:
                    arcs_descriptions.append(f"Ingoing arc: {text}")

            final_to_file = final_to_file + "\n\n" + f"Transition '{transition_id}'"
            final_to_file = final_to_file + "\n" + f"Guard: {guard}"
            final_to_file = final_to_file + "\n" + "Arcs:"

            for arc in arcs_descriptions:
                final_to_file = final_to_file + "\n" + arc
            if LOGGING:
                print(f"\nTransition: '{transition_id}'")
                print(f"Guard: {guard}")
                print("Arcs:")
                for arc in arcs_descriptions:
                    print(arc)

        final_to_file = final_to_file + "\n" + "-------ARCS-------"
        if LOGGING:
            print("-------ARCS-------")
        for arc in arcs:
            hlinscription = arc.find(f'{NAMESPACE}' + 'hlinscription')
            text = hlinscription.find(f'{NAMESPACE}' + 'text').text
            final_to_file = final_to_file + "\n" + text
            if LOGGING:
                print(text)

        final_to_file = final_to_file + "\n" + "------------------------------------------------------------------"
        if LOGGING:
            print("------------------------------------------------------------------")

        with open(f"{extracted_folder}/{test_folder}.txt", "w") as file:
            # Writing data to a file
            file.write(final_to_file)

        with open(f"{extracted_folder}/_all_guards.txt", "w") as file:
            # Writing data to a file
            file.write(all_guards)


if __name__ == "__main__":
    main()
