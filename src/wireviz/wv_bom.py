#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import List, Union
from collections import Counter

from wireviz.DataClasses import Connector, Cable
from wireviz.wv_gv_html import html_bgcolor_attr, html_line_breaks
from wireviz.wv_helper import clean_whitespace

def get_additional_component_table(harness, component: Union[Connector, Cable]) -> List[str]:
    rows = []
    if component.additional_components:
        rows.append(["Additional components"])
        for extra in component.additional_components:
            qty = extra.qty * component.get_qty_multiplier(extra.qty_multiplier)
            if harness.mini_bom_mode:
                id = get_bom_index(harness, extra.description, extra.unit, extra.manufacturer, extra.mpn, extra.pn)
                rows.append(component_table_entry(f'#{id} ({extra.type.rstrip()})', qty, extra.unit, extra.bgcolor))
            else:
                rows.append(component_table_entry(extra.description, qty, extra.unit, extra.bgcolor, extra.pn, extra.manufacturer, extra.mpn))
    return(rows)

def get_additional_component_bom(component: Union[Connector, Cable]) -> List[dict]:
    bom_entries = []
    for part in component.additional_components:
        qty = part.qty * component.get_qty_multiplier(part.qty_multiplier)
        bom_entries.append({
            'item': part.description,
            'qty': qty,
            'unit': part.unit,
            'manufacturer': part.manufacturer,
            'mpn': part.mpn,
            'pn': part.pn,
            'designators': component.name if component.show_name else None
        })
    return(bom_entries)

def generate_bom(harness):
    from wireviz.Harness import Harness  # Local import to avoid circular imports
    bom_entries = []
    # connectors
    for connector in harness.connectors.values():
        if not connector.ignore_in_bom:
            description = ('Connector'
                           + (f', {connector.type}' if connector.type else '')
                           + (f', {connector.subtype}' if connector.subtype else '')
                           + (f', {connector.pincount} pins' if connector.show_pincount else '')
                           + (f', {connector.color}' if connector.color else ''))
            bom_entries.append({
                'item': description, 'qty': 1, 'unit': None, 'designators': connector.name if connector.show_name else None,
                'manufacturer': connector.manufacturer, 'mpn': connector.mpn, 'pn': connector.pn
            })

        # add connectors aditional components to bom
        bom_entries.extend(get_additional_component_bom(connector))

    # cables
    # TODO: If category can have other non-empty values than 'bundle', maybe it should be part of item name?
    for cable in harness.cables.values():
        if not cable.ignore_in_bom:
            if cable.category != 'bundle':
                # process cable as a single entity
                description = ('Cable'
                               + (f', {cable.type}' if cable.type else '')
                               + (f', {cable.wirecount}')
                               + (f' x {cable.gauge} {cable.gauge_unit}' if cable.gauge else ' wires')
                               + (' shielded' if cable.shield else ''))
                bom_entries.append({
                    'item': description, 'qty': cable.length, 'unit': cable.length_unit, 'designators': cable.name if cable.show_name else None,
                    'manufacturer': cable.manufacturer, 'mpn': cable.mpn, 'pn': cable.pn
                })
            else:
                # add each wire from the bundle to the bom
                for index, color in enumerate(cable.colors):
                    description = ('Wire'
                                   + (f', {cable.type}' if cable.type else '')
                                   + (f', {cable.gauge} {cable.gauge_unit}' if cable.gauge else '')
                                   + (f', {color}' if color else ''))
                    bom_entries.append({
                        'item': description, 'qty': cable.length, 'unit': cable.length_unit, 'designators': cable.name if cable.show_name else None,
                        'manufacturer': index_if_list(cable.manufacturer, index),
                        'mpn': index_if_list(cable.mpn, index), 'pn': index_if_list(cable.pn, index)
                    })

        # add cable/bundles aditional components to bom
        bom_entries.extend(get_additional_component_bom(cable))

    for item in harness.additional_bom_items:
        bom_entries.append({
            'item': item.get('description', ''), 'qty': item.get('qty', 1), 'unit': item.get('unit'), 'designators': item.get('designators'),
            'manufacturer': item.get('manufacturer'), 'mpn': item.get('mpn'), 'pn': item.get('pn')
        })

    # remove line breaks if present and cleanup any resulting whitespace issues
    bom_entries = [{k: clean_whitespace(v) for k, v in entry.items()} for entry in bom_entries]

    # deduplicate bom
    bom = []
    bom_types_group = lambda bt: (bt['item'], bt['unit'], bt['manufacturer'], bt['mpn'], bt['pn'])
    for group in Counter([bom_types_group(v) for v in bom_entries]):
        group_entries = [v for v in bom_entries if bom_types_group(v) == group]
        designators = []
        for group_entry in group_entries:
            if group_entry.get('designators'):
                if isinstance(group_entry['designators'], List):
                    designators.extend(group_entry['designators'])
                else:
                    designators.append(group_entry['designators'])
        designators = list(dict.fromkeys(designators))  # remove duplicates
        designators.sort()
        total_qty = sum(entry['qty'] for entry in group_entries)
        bom.append({**group_entries[0], 'qty': round(total_qty, 3), 'designators': designators})

    bom = sorted(bom, key=lambda k: k['item'])  # sort list of dicts by their values (https://stackoverflow.com/a/73050)

    # add an incrementing id to each bom item
    bom = [{**entry, 'id': index} for index, entry in enumerate(bom, 1)]
    return bom

def get_bom_index(harness, item, unit, manufacturer, mpn, pn):
    # Remove linebreaks and clean whitespace of values in search
    target = tuple(clean_whitespace(v) for v in (item, unit, manufacturer, mpn, pn))
    for entry in harness.bom():
        if (entry['item'], entry['unit'], entry['manufacturer'], entry['mpn'], entry['pn']) == target:
            return entry['id']
    return None

def bom_list(bom):
    keys = ['id', 'item', 'qty', 'unit', 'designators'] # these BOM columns will always be included
    for fieldname in ['pn', 'manufacturer', 'mpn']: # these optional BOM columns will only be included if at least one BOM item actually uses them
        if any(entry.get(fieldname) for entry in bom):
            keys.append(fieldname)
    bom_list = []
    # list of staic bom header names,  headers not specified here are generated by capitilising the internal name
    bom_headings = {
        "pn": "P/N",
        "mpn": "MPN"
    }
    bom_list.append([(bom_headings[k] if k in bom_headings else k.capitalize()) for k in keys])  # create header row with keys
    for item in bom:
        item_list = [item.get(key, '') for key in keys]  # fill missing values with blanks
        item_list = [', '.join(subitem) if isinstance(subitem, List) else subitem for subitem in item_list]  # convert any lists into comma separated strings
        item_list = ['' if subitem is None else subitem for subitem in item_list]  # if a field is missing for some (but not all) BOM items
        bom_list.append(item_list)
    return bom_list

def component_table_entry(type, qty, unit=None, bgcolor=None, pn=None, manufacturer=None, mpn=None):
    output = f'{qty}'
    if unit:
        output += f' {unit}'
    output += f' x {type}'
    # print an extra line with part and manufacturer information if provided
    manufacturer_str = manufacturer_info_field(manufacturer, mpn)
    if pn or manufacturer_str:
        output += '<br/>'
        if pn:
            output += f'P/N: {pn}'
            if manufacturer_str:
                output += ', '
        if manufacturer_str:
            output += manufacturer_str
    output = html_line_breaks(output)
    # format the above output as left aligned text in a single visible cell
    # indent is set to two to match the indent in the generated html table
    return f'''<table border="0" cellspacing="0" cellpadding="3" cellborder="1"{html_bgcolor_attr(bgcolor)}><tr>
   <td align="left" balign="left">{output}</td>
  </tr></table>'''

def manufacturer_info_field(manufacturer, mpn):
    if manufacturer or mpn:
        return f'{manufacturer if manufacturer else "MPN"}{": " + str(mpn) if mpn else ""}'
    else:
        return None

# Return the value indexed if it is a list, or simply the value otherwise.
def index_if_list(value, index):
    return value[index] if isinstance(value, list) else value
