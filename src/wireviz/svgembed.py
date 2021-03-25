#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import base64
from pathlib import Path
from typing import Union

mime_subtype_replacements = {'jpg': 'jpeg', 'tif': 'tiff'}

def embed_svg_images(svg_in: str, base_path: Union[str, Path] = Path.cwd()) -> str:
    # first, find any image references in SVG data, and cache the respective base64-encoded image
    images_b64 = {}  # cache of base64-encoded images
    re_xlink=re.compile(r'xlink:href="(?P<URL>.*?)"', re.IGNORECASE)
    for xlink in re_xlink.finditer(svg_in):
        imgurl = xlink.group('URL')
        if not imgurl in images_b64:  # only encode/cache every unique URL once
            imgurl_abs = (Path(base_path) / imgurl).resolve()
            images_b64[imgurl] = base64.b64encode(imgurl_abs.read_bytes()).decode('utf-8')
    # second, replace links with the base64-encoded data
    svg_out = svg_in
    for url, b64 in images_b64.items():
        svg_out = svg_out.replace(url, f'data:image/{get_mime_subtype(url)};base64, {b64}')

    return svg_out


def get_mime_subtype(filename: Union[str, Path]) -> str:
    mime_subtype = Path(filename).suffix.lstrip('.').lower()
    if mime_subtype in mime_subtype_replacements:
        mime_subtype = mime_subtype_replacements[mime_subtype]
    return mime_subtype


def embed_svg_images_file(filename_in: Union[str, Path], overwrite: bool = True) -> None:
    filename_in = Path(filename_in).resolve()
    filename_out = filename_in.with_suffix('.b64.svg')
    filename_out.write_text(embed_svg_images(filename_in.read_text(), filename_in.parent))
    if overwrite:
        filename_out.replace(filename_in)
