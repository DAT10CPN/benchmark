import os
import random
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

NAMESPACE = '{http://www.pnml.org/version-2009/grammar/pnml}'
ET.register_namespace('', 'http://www.pnml.org/version-2009/grammar/pnml')
INHIB_PERCENTAGE = 5
MCC_DIRECTORY = os.path.join(os.path.dirname(__file__), sys.argv[1])

if len(sys.argv) < 2:
    print("You did not give a path to the MCC directory")

models = [model for model in Path(MCC_DIRECTORY).rglob('*.pnml')]
num_models = len(models)
converted_models = 0


def findColorType(pid):
    for node in page.findall(f'{NAMESPACE}' + 'place'):
        if node.attrib['id'] == pid:
            type = node.find(f'{NAMESPACE}' + 'type')
            structure = type.find(f'{NAMESPACE}' + 'structure')
            usersort = structure.find(f'{NAMESPACE}' + 'usersort')
            return usersort.attrib['declaration']
    raise Exception("Colortype not found")


def findCardinality(arc):
    hlinscription = arc.find(f'{NAMESPACE}' + 'hlinscription')
    text = hlinscription.find(f'{NAMESPACE}' + 'text').text

    regex = r"[0-9](?=')"

    matches = re.finditer(regex, text, re.MULTILINE)

    total = 0
    for matchNum, match in enumerate(matches, start=1):
        total += int(match.group())

    if total <= 0:
        total = 1
    return str(total)


def usersortSubterm(colortype):
    # The subterm with the colortype
    usersortSubterm = ET.Element('subterm')
    all = ET.Element('all')
    usersort = ET.Element('usersort')
    usersort.set('declaration', colortype)
    all.append(usersort)
    usersortSubterm.append(all)

    return usersortSubterm


def cardinalitySubterm(cardinality):
    cardinalitySubterm = ET.Element('subterm')
    numberConstant = ET.Element('numberconstant')
    numberConstant.set('value', cardinality)
    positive = ET.Element('positive')
    numberConstant.append(positive)
    cardinalitySubterm.append(numberConstant)

    return cardinalitySubterm


def createHlinscription(colortype, cardinality):
    hlinscription = ET.Element('hlinscription')

    # Adds the text, i.e what it says on the arc
    text = ET.Element('text')
    text.text = f"{cardinality}'{colortype}"
    hlinscription.append(text)

    # Add the structure
    structure = ET.Element('structure')
    hlinscription.append(structure)
    numberOf = ET.Element('numberof')
    structure.append(numberOf)

    numberOf.append(cardinalitySubterm(cardinality))
    numberOf.append(usersortSubterm(colortype))

    return hlinscription


def createInscription(cardinality):
    inscription = ET.Element('inscription')
    text = ET.Element('text')
    text.text = cardinality
    inscription.append(text)
    return inscription


for model in models:
    if converted_models % 5 == 0:
        print(f"Converted models: {converted_models}/{num_models}")

    mytree = ET.parse(model)
    myroot = mytree.getroot()

    net = myroot.find(f'{NAMESPACE}' + 'net')
    page = net.find(f'{NAMESPACE}' + 'page')
    arcs = page.findall(f'{NAMESPACE}' + 'arc')
    transitions = page.findall(f'{NAMESPACE}' + 'transition')
    places = page.findall(f'{NAMESPACE}' + 'place')

    transition_ids = [transition.attrib.get('id') for transition in transitions]
    in_arcs = [arc for arc in arcs if arc.attrib.get('target') in transition_ids]
    num_arcs_to_create = round(len(in_arcs) * (INHIB_PERCENTAGE / 100.0))
    print(f"Creating {num_arcs_to_create} inhibitor arc. Candidates: {len(in_arcs)}")

    places_to_get_inhibitor_arc = random.sample(places, num_arcs_to_create)
    places_ids = [place.attrib.get('id') for place in places_to_get_inhibitor_arc]
    new_inhibitor_arcs = []

    tids_we_added_inhibs_to = []
    for place in places_to_get_inhibitor_arc:
        pid = place.attrib.get('id')

        added_an_inhib = False
        attempts = 0
        while not added_an_inhib:
            attempts = attempts + 1
            if attempts > 200:
                added_an_inhib = True
                break
            transition = random.sample(transitions, 1)[0]
            tid = transition.attrib.get('id')

            # Dont create arc to another transition that we just added an inhibitor to
            if tid in tids_we_added_inhibs_to:
                continue
            else:
                tids_we_added_inhibs_to.append(tid)

            # Dont create a new inhibitor arc between pair that already exists
            not_valid_transition = False
            for arc in arcs:
                source = arc.attrib.get('source')
                target = arc.attrib.get('target')
                if pid == source and tid == target:
                    not_valid_transition = True
                    break

            if not_valid_transition:
                continue

            added_an_inhib = True
            new_inhibitor_arcs.append((pid, tid))

    for arc in arcs:
        arc.set('type', 'normal')

    for new_inhibitor in new_inhibitor_arcs:
        arc = ET.Element('arc')
        colortype = findColorType(new_inhibitor[0])
        cardinality = random.sample(['1', '2'], 1)[0]
        hlinscription = createHlinscription(colortype, cardinality)
        inscription = createInscription(cardinality)
        arc.set('source', new_inhibitor[0])
        arc.set('target', new_inhibitor[1])
        arc.append(inscription)
        arc.append(hlinscription)
        arc.set('type', 'inhibitor')
        page.append(arc)

    """for arc in arcs:
        if arc in arcs_to_convert:
            arc.set('type', 'inhibitor')
            oldHlinscription = arc.find(f'{NAMESPACE}' + 'hlinscription')
            oldInscription = arc.find(f'{NAMESPACE}' + 'inscription')

            colortype = findColorType(arc)
            cardinality = findCardinality(arc)
            hlinscription = createHlinscription(colortype, cardinality)
            inscription = createInscription(cardinality)
            arc.remove(oldHlinscription)
            if oldInscription:
                arc.remove(oldInscription)
            arc.append(inscription)
            arc.append(hlinscription)
        else:
            arc.set('type', 'normal')"""

    tree = ET.ElementTree(myroot)
    with open(model, 'w') as f:
        # with open("inhib.pnml", 'w') as f:
        tree.write(f, xml_declaration=True, encoding='unicode')

    converted_models += 1

print("Done converting to inhibitor arcs")
