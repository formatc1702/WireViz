#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List
from pathlib import Path
import re

awg_equiv_table = {
    '0.09': '28',
    '0.14': '26',
    '0.25': '24',
    '0.34': '22',
    '0.5': '21',
    '0.75': '20',
    '1': '18',
    '1.5': '16',
    '2.5': '14',
    '4': '12',
    '6': '10',
    '10': '8',
    '16': '6',
    '25': '4',
    '35': '2',
    '50': '1',
}

mm2_equiv_table = {v:k for k,v in awg_equiv_table.items()}

def awg_equiv(mm2):
    return awg_equiv_table.get(str(mm2), 'Unknown')

def mm2_equiv(awg):
    return mm2_equiv_table.get(str(awg), 'Unknown')


def expand(yaml_data):
    # yaml_data can be:
    # - a singleton (normally str or int)
    # - a list of str or int
    # if str is of the format '#-#', it is treated as a range (inclusive) and expanded
    output = []
    if not isinstance(yaml_data, list):
        yaml_data = [yaml_data]
    for e in yaml_data:
        e = str(e)
        if '-' in e:
            a, b = e.split('-', 1)
            try:
                a = int(a)
                b = int(b)
                if a < b:
                    for x in range(a, b + 1):
                        output.append(x)  # ascending range
                elif a > b:
                    for x in range(a, b - 1, -1):
                        output.append(x)  # descending range
                else:  # a == b
                    output.append(a)  # range of length 1
            except:
                output.append(e)  # '-' was not a delimiter between two ints, pass e through unchanged
        else:
            try:
                x = int(e)  # single int
            except Exception:
                x = e  # string
            output.append(x)
    return output


def int2tuple(inp):
    if isinstance(inp, tuple):
        output = inp
    else:
        output = (inp,)
    return output


def flatten2d(inp):
    return [[str(item) if not isinstance(item, List) else ', '.join(item) for item in row] for row in inp]


def tuplelist2tsv(inp, header=None):
    output = ''
    if header is not None:
        inp.insert(0, header)
    inp = flatten2d(inp)
    for row in inp:
        output = output + '\t'.join(str(remove_links(item)) for item in row) + '\n'
    return output


def remove_links(inp):
    return re.sub(r'<[aA] [^>]*>([^<]*)</[aA]>', r'\1', inp) if isinstance(inp, str) else inp


def clean_whitespace(inp):
    return ' '.join(inp.split()).replace(' ,', ',') if isinstance(inp, str) else inp


def open_file_read(filename):
    # TODO: Intelligently determine encoding
    return open(filename, 'r', encoding='UTF-8')

def open_file_write(filename):
    return open(filename, 'w', encoding='UTF-8')

def open_file_append(filename):
    return open(filename, 'a', encoding='UTF-8')

def aspect_ratio(image_src):
    try:
        from PIL import Image
        image = Image.open(image_src)
        if image.width > 0 and image.height > 0:
            return image.width / image.height
        print(f'aspect_ratio(): Invalid image size {image.width} x {image.height}')
    # ModuleNotFoundError and FileNotFoundError are the most expected, but all are handled equally.
    except Exception as error:
        print(f'aspect_ratio(): {type(error).__name__}: {error}')
    return 1 # Assume 1:1 when unable to read actual image size

def smart_file_resolve(filename, possible_paths):
    filename = Path(filename)
    if filename.is_absolute():
        if filename.exists():
            return filename
        else:
            raise Exception(f'{filename} does not exist.')
    else:  # search all possible paths in decreasing order of precedence
        possible_paths = [Path(path).resolve() for path in possible_paths]
        for possible_path in possible_paths:
            resolved_path = (possible_path / filename).resolve()
            if (resolved_path).exists():
                return resolved_path
        else:
            raise Exception(f'{filename} was not found in any of the following locations: \n' +
                            '\n'.join([str(x) for x in possible_paths]))
