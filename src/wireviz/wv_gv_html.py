#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import List, Union
import re

from wireviz.DataClasses import Color
from wireviz.wv_colors import translate_color
from wireviz.wv_helper import remove_links

def nested_html_table(rows):
    # input: list, each item may be scalar or list
    # output: a parent table with one child table per parent item that is list, and one cell per parent item that is scalar
    # purpose: create the appearance of one table, where cell widths are independent between rows
    # attributes in any leading <tdX> inside a list are injected into to the preceeding <td> tag
    html = []
    html.append('<table border="0" cellspacing="0" cellpadding="0">')
    for row in rows:
        if isinstance(row, List):
            if len(row) > 0 and any(row):
                html.append(' <tr><td>')
                html.append('  <table border="0" cellspacing="0" cellpadding="3" cellborder="1"><tr>')
                for cell in row:
                    if cell is not None:
                        # Inject attributes to the preceeding <td> tag where needed
                        html.append(f'   <td balign="left">{cell}</td>'.replace('><tdX', ''))
                html.append('  </tr></table>')
                html.append(' </td></tr>')
        elif row is not None:
            html.append(' <tr><td>')
            html.append(f'  {row}')
            html.append(' </td></tr>')
    html.append('</table>')
    return html

def html_bgcolor(color: Color, _extra_attr: str = '') -> str:
    """Return <td> attributes prefix for bgcolor or '' if no color."""
    return f'<tdX bgcolor="{translate_color(color, "HEX")}"{_extra_attr}>' if color else ''

def html_colorbar(color: Color) -> str:
    """Return <tdX> attributes prefix for bgcolor and minimum width or None if no color."""
    return html_bgcolor(color, ' width="4"') if color else None

def html_image(image):
    from wireviz.DataClasses import Image
    if not image:
        return None
    # The leading attributes belong to the preceeding tag. See where used below.
    html = f'{html_size_attr(image)}><img scale="{image.scale}" src="{image.src}"/>'
    if image.fixedsize:
        # Close the preceeding tag and enclose the image cell in a table without
        # borders to avoid narrow borders when the fixed width < the node width.
        html = f'''>
    <table border="0" cellspacing="0" cellborder="0"><tr>
     <td{html}</td>
    </tr></table>
   '''
    return f'''<tdX{' sides="TLR"' if image.caption else ''}{html}'''

def html_caption(image):
    from wireviz.DataClasses import Image
    return f'<tdX sides="BLR">{html_line_breaks(image.caption)}' if image and image.caption else None

def html_size_attr(image):
    from wireviz.DataClasses import Image
    # Return Graphviz HTML attributes to specify minimum or fixed size of a TABLE or TD object
    return ((f' width="{image.width}"'   if image.width else '')
        +   (f' height="{image.height}"' if image.height else '')
        +   ( ' fixedsize="true"'        if image.fixedsize else '')) if image else ''

def html_line_breaks(inp):
    return remove_links(inp).replace('\n', '<br />') if isinstance(inp, str) else inp
