#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
from typing import List, Dict, Union
import re

from wireviz import __version__, APP_NAME, APP_URL, wv_colors
from wireviz.DataClasses import Metadata, Options
from wireviz.wv_helper import flatten2d, open_file_read, open_file_write, smart_file_resolve
from wireviz.wv_gv_html import html_line_breaks

def generate_html_output(filename: Union[str, Path], bom_list: List[List[str]], metadata: Metadata, options: Options):

    # load HTML template
    if 'name' in metadata.get('template',{}):
        # if relative path to template was provided, check directory of YAML file first, fall back to built-in template directory
        templatefile = smart_file_resolve(f'{metadata["template"]["name"]}.html', [Path(filename).parent, Path(__file__).parent / 'templates'])
    else:
        # fall back to built-in simple template if no template was provided
        templatefile = Path(__file__).parent / 'templates/simple.html'

    with open_file_read(templatefile) as file:
        html = file.read()

    # embed SVG diagram
    with open_file_read(f'{filename}.svg') as file:
        svgdata = file.read()
        svgdata = re.sub(
                  '^<[?]xml [^?>]*[?]>[^<]*<!DOCTYPE [^>]*>',
                  '<!-- XML and DOCTYPE declarations from SVG file removed -->',
                  svgdata, 1)
    html = html.replace('<!-- %diagram% -->', svgdata)

    # generate BOM table
    bom = flatten2d(bom_list)

    # generate BOM header (may be at the top or bottom of the table)
    bom_header_html = '  <tr>\n'
    for item in bom[0]:
        th_class = f'bom_col_{item.lower()}'
        bom_header_html = f'{bom_header_html}    <th class="{th_class}">{item}</th>\n'
    bom_header_html = f'{bom_header_html}  </tr>\n'

    # generate BOM contents
    bom_contents = []
    for row in bom[1:]:
        row_html = '  <tr>\n'
        for i, item in enumerate(row):
            td_class = f'bom_col_{bom[0][i].lower()}'
            row_html = f'{row_html}    <td class="{td_class}">{item}</td>\n'
        row_html = f'{row_html}  </tr>\n'
        bom_contents.append(row_html)

    bom_html = '<table>\n' + bom_header_html + ''.join(bom_contents) + '</table>\n'
    bom_html_reversed = '<table>\n' + ''.join(list(reversed(bom_contents))) + bom_header_html + '</table>\n'

    # insert BOM table
    html = html.replace('<!-- %bom% -->', bom_html)
    html = html.replace('<!-- %bom_reversed% -->', bom_html_reversed)

    # insert generator
    html = html.replace('<!-- %generator% -->', f'{APP_NAME} {__version__} - {APP_URL}')

    # insert other metadata
    if metadata:

        html = html.replace(f'"sheetsize_default"', '"{}"'.format(metadata.get('template',{}).get('sheetsize', ''))) # include quotes so no replacement happens within <style> definition

        # TODO: handle multi-page documents
        html = html.replace('<!-- %sheet_current% -->', '1')
        html = html.replace('<!-- %sheet_total% -->', '1')

        # fill out other generic metadata
        for item, contents in metadata.items():
            if isinstance(contents, (str, int, float)):
                html = html.replace(f'<!-- %{item}% -->', html_line_breaks(str(contents)))
            elif isinstance(contents, Dict):  # useful for authors, revisions
                for index, (category, entry) in enumerate(contents.items()):
                    if isinstance(entry, Dict):
                        html = html.replace(f'<!-- %{item}_{index+1}% -->', str(category))
                        for entry_key, entry_value in entry.items():
                            html = html.replace(f'<!-- %{item}_{index+1}_{entry_key}% -->', html_line_breaks(str(entry_value)))


    with open_file_write(f'{filename}.html') as file:
        file.write(html)
