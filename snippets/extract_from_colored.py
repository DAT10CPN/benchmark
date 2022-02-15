import os
import xml.etree.ElementTree as ET
from pathlib import Path


def main():
    NAMESPACE = '{http://www.pnml.org/version-2009/grammar/pnml}'
    ET.register_namespace('', 'http://www.pnml.org/version-2009/grammar/pnml')

    script_dir = os.path.dirname(__file__)
    MCC_DIRECTORY = os.path.join(script_dir, '..\\..\\..\\mcc2021-COL\\')

    for test_folder in os.listdir(MCC_DIRECTORY):

        if test_folder != 'TokenRing-COL-005':
            continue
        print("Test: ", test_folder)
        model_path = Path(os.path.join(MCC_DIRECTORY), f'{test_folder}\\model.pnml')
        mytree = ET.parse(model_path)
        myroot = mytree.getroot()
        net = myroot.find(f'{NAMESPACE}' + 'net')
        page = net.find(f'{NAMESPACE}' + 'page')

        # Find declarations
        declaration = net.findall(f'{NAMESPACE}' + 'declaration')
        structure = declaration[0].findall(f'{NAMESPACE}' + 'structure')
        declarations = structure[0].findall(f'{NAMESPACE}' + 'declarations')

        #ALL conditions on transitions
        print("-------CONDITIONS-------")
        all_conditions_text = []
        transitions = page.findall(f'{NAMESPACE}' + 'transition')
        for transition in transitions:
            conditions = transition.findall(f'{NAMESPACE}' + 'condition')
            for condition in conditions:
                text = condition.findall(f'{NAMESPACE}' + 'text')

                all_conditions_text.append(text[0].text)

        if len(all_conditions_text) == 0:
            all_conditions_text = "No condition"
        print(all_conditions_text)


        #Find all variables used
        print("-------VARIABLES-------:")
        for variabledecl in declarations[0].findall(f'{NAMESPACE}' + 'variabledecl'):
            print("Variable decl attrib: ", variabledecl.attrib)
            for usersort in variabledecl.findall(f'{NAMESPACE}' + 'usersort'):
                print("With declaration: ", usersort.attrib)



        #Find ranges of colors
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
                continue
            print(named_sort.attrib['id'] + " has Range: ")
            print("[" + str(min_range) + "," + str(max_range) + "]")
        print("------------------------------------------------------------------")


if __name__ == "__main__":
    main()
