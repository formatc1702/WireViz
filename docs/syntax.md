# WireViz Syntax

## Main sections

```yaml
connectors:  # dictionary of all used connectors
  <str>   :    # unique connector designator/name
    ...          # connector attributes (see below)
  <str>   :
    ...
  ...

cables:      # dictionary of all used cables and wires
  <str>   :    # unique cable designator/name
    ...          # cable attributes (see below)
  <str>   :
    ...
  ...

connections:  # list of all connections to be made
              # between cables and connectors
  -
    ...         # connection set (see below)
  -
    ...
  ...

additional_bom_items:  # custom items to add to BOM
  - <bom-item>           # BOM item (see below)
  ...

```

## Connector attributes

```yaml
<str>   :  # unique connector designator/name
  # general information about a connector (all optional)
  type: <str>   
  subtype: <str>   
  color: <color>  # see below
  image: <image>  # see below
  notes: <str>   

  # product information (all optional)
  ignore_in_bom: <bool>  # if set to true the connector is not added to the BOM
  pn: <str>              # [internal] part number
  mpn: <str>             # manufacturer part number
  manufacturer: <str>    # manufacturer name
  additional_components: # additional components
    - <additional-component> # additional component (see below)

  # pinout information
  # at least one of the following must be specified
  pincount: <int>    # if omitted, is set to length of specified list(s)
  pins: <List>       # if omitted, is autofilled with [1, 2, ..., pincount]
  pinlabels: <List>  # if omitted, is autofilled with blanks

  # pin color marks (optional)
  pincolors: <List>  # list of colors to be assigned to the respective pins;
                     # if list length is lower than connector pinout,
                     # no color marks will be added to remaining pins

  # rendering information (all optional)
  bgcolor: <color>       # Background color of diagram connector box
  style: <style>         # may be set to simple for single pin connectors
  show_name: <bool>      # defaults to true for regular connectors,
                         # false for simple connectors
  show_pincount: <bool>  # defaults to true for regular connectors
                         # false for simple connectors
  hide_disconnected_pins: <bool>  # defaults to false

  # loops
  loops: <List>  # every list item is itself a list of exactly two pins
                 # on the connector that are to be shorted

  # auto-generation
  autogenerate: <bool>  # optional; defaults to false; see below

```

### Auto-generation of connectors

The `autogenerate: true` option is especially useful for very simple, recurring connectors such as crimp ferrules, splices, and others, where it would be a hassle to individually assign unique designators for every instance.

By default, when defining a connector, it will be generated once using the specified designator, and can be referenced multiple times, in different connection sets (see below).

If `autogenerate: true` is set, the connector will _not_ be generated at first. When defining the `connections` section (see below), every time the connector is mentioned, a new instance with an auto-incremented designator is generated and attached.

Since the auto-incremented and auto-assigned designator is not known to the user, one instance of the connector can not be referenced again outside the point of creation. The `autogenerate: true` option is therefore only useful for terminals with only one wire attached, or splices with exactly one wire going in, and one wire going out. If more wires are to be attached (e.g. for a three-way splice, or a crimp where multiple wires are joined), a separate connector with `autogenerate: false` and a user-defined, unique designator needs to be used.

## Cable attributes

```yaml
<str>   :  # unique cable designator/name
  # general information about a connector (all optional)
  category: <category>  # may be set to bundle;
                        # generates one BOM item for every wire in the bundle
                        # instead of a single item for the entire cable;
                        # renders with a dashed outline
  type: <str>   
  gauge: <int/float/str>  # allowed formats:
                          # <int/float> mm2  is understood
                          # <int> AWG        is understood
                          # <int/float>      is assumed to be mm2
                          # <str>            custom units and formats are allowed
                          #                  but unavailable for auto-conversion
  show_equiv: <bool>      # defaults to false; can auto-convert between mm2 and AWG
                          # and display the result when set to true
  length: <int/float>     # is assumed to be in meters
  shield: <bool/color>    # defaults to false
                          # setting to true will display the shield as a thin black line
                          # using a color (see below) will render the shield in that color
                          # using 's' as the wire number
  color: <color>  # see below
  image: <image>  # see below
  notes: <str>   

  # product information (all optional)
  ignore_in_bom: <bool>  # if set to true the cable or wires are not added to the BOM
  pn: <str>              # [internal] part number
  mpn: <str>             # manufacturer part number
  manufacturer: <str>    # manufacturer name
  additional_components: # additional components
    - <additional-component> # additional component (see below)

  # conductor information
  # the following combinations are permitted:
  # wirecount only          no color information is specified
  # colors only             wirecount is inferred from list length
  # wirecount + color_code  colors are auto-generated based on the specified
  #                         color code (see below) to match the wirecount
  # wirecount + colors      colors list is trimmed or repeated to match the wirecount
  wirecount: <int>
  colors: <List>     # list of colors (see below)
  color_code: <str>  # one of the supported cable color codes (see below)

  wirelabels: <List>  # optional; one label for each wire

  # rendering information (all optional)
  bgcolor: <color>          # Background color of diagram cable box
  show_name: <bool>         # defaults to true
  show_wirecount: <bool>    # defaults to true
  show_wirenumbers: <bool>  # defaults to true for cables; false for bundles

```

## Connection sets

A connection set is used to connect multiple components together. Multiple connections can be easily created in parallel within one connection set, by specifying a list of individual pins (for `connectors`) or wires (for `cables`) for every component along the way.

```yaml
connections:
  -                # Each list entry is a connection set
    - <component>    # Each connection set is itself a list of items
    - <component>    # Items must alternatingly belong to the connectors and cables sections
    -...

  - # example (single connection)
    - <connector>: <pin>   # attach one pin of the connector
    - <cable>:     <wire>  # attach one wire of the cable
    - <connector>          # for simple connectors, pin 1 is implicit
    - <cable>:     s       # for shielded wires, s attaches to the shield

  - # example (multiple parallel connections)
    - <connector>: [<pin>,  ..., <pin> ]  # attach multiple pins in parallel
    - <cable>:     [<wire>, ..., <wire>]  # attach multiple wires in parallel
    - <connector>                         # auto-generate a new connector for every parallel connection
    - <cable>:     [<wire>-<wire>]        # specify a range of wires to attach in parallel
    - [<connector>, ..., <connector>]     # specify multiple simple connectors to attach in parallel
                                          # these may be unique, auto-generated, or a mix of both

  ...    
```

- Each connection set is a list of components.
- The minimum number of items is two.
- The maximum number of items is unlimited.
- Items must alternatingly belong to the `connectors` and the `cables` sections.
- When a connection set defines multiple parallel connections, the number of specified `<pin>`s and `<wire>`s for each component in the set must match. When specifying only one designator, one is auto-generated for each connection of the set.
- `<pin>` may reference a pin's unique ID (as per the connector's `pins` attribute, auto-numbered from 1 by default) or its label (as per `pinlabels`).
- `<wire>` may reference a wire's number within a cable/bundle, its label (as per `wirelabels`) or, if unambiguous, its color.

### Single connections

#### Connectors

- `- <designator>: <int/str>` attaches a pin of the connector, referring to a pin number (from the connector's `pins` attribute) or a pin label (from its `pinlabels` attribute), provided the label is unique.

- `- <designator>` is allowed for simple connectors, since they have only one pin to connect.
For connectors with `autogenerate: true`, a new instance, with auto-generated designator, is created.

#### Cables

- `<designator>: <wire>` attaches a specific wire of a cable, using its number.

### Multiple parallel connections

#### Connectors

- `- <designator>: [<pin>, ..., <pin>]`

  Each `<pin>` may be:

  - `<int/str>` to refer to a specific pin, using its number (from its `pins` attribute) or its label (from its `pinlabels` attribute, provided the label is unique for this connector)

  - `<int>-<int>` auto-expands to a range, e.g. `1-4` auto-expands to `1,2,3,4`; `9-7` will auto-expand to `9,8,7`.

  - Mixing types is allowed, e.g. `[<pin>, <pinlabel>, <pin>-<pin>, <pin>]`

- `- [<designator>, ..., <designator>]`

  Attaches multiple different single pin connectors, one per connection in the set.
  For connectors with `autogenerate: true`, a new instance, with auto-generated designator, is created with every mention.
  Auto-generated and non-autogenerated connectors may be mixed.

- `- <designator>`

  Attaches multiple instances of the same single pin connector, one per connectioin in the set.
  For connectors with `autogenerate: true`, a new instance, with auto-generated designator, is created for every connection in the set.
  Since only connectors with `pincount: 1` can be auto-generated, pin number 1 is implicit.

#### Cables

- `<designator>: [<wire>, ..., <wire>]`

  Each `<wire>` may be:

  - `<int>` to refer to a specific wire, using its number.
  - `<int>-<int>` auto-expands to a range.
  - `<str>` to refer to a wire's label or color, if unambiguous.


## BOM items and additional components

Connectors (both regular, and auto-generated), cables, and wires of a bundle are automatically added to the BOM,
unless the `ignore_in_bom` attribute is set to `true`.
Additional items can be added to the BOM as either part of a connector or cable or on their own.

Parts can be added to a connector or cable in the section `<additional-component>` which will also list them in the graph.

```yaml
-
  type: <str>  # type of additional component
  # all the following are optional:
  subtype: <str>  # additional description (only shown in bom)
  qty: <int/float>  # qty to add to the bom (defaults to 1)
  qty_multiplier: <str>  # multiplies qty by a feature of the parent component
                  # when used in a connector:
                  # pincount         number of pins of connector
                  # populated        number of populated positions in a connector
                  # when used in a cable:
                  # wirecount        number of wires of cable/bundle
                  # terminations     number of terminations on a cable/bundle
                  # length           length of cable/bundle
                  # total_length     sum of lengths of each wire in the bundle
  unit: <str>
  pn: <str>            # [internal] part number
  mpn: <str>           # manufacturer part number
  manufacturer: <str>  # manufacturer name  
```

Alternatively items can be added to just the BOM by putting them in the section `<bom-item>` above.

```yaml
-
  description: <str>              
  # all the following are optional:
  qty: <int/float>  # qty to add to the bom (defaults to 1)
  unit: <str>   
  designators: <List>
  pn: <str>            # [internal] part number
  mpn: <str>           # manufacturer part number
  manufacturer: <str>  # manufacturer name  
```

## Colors

Colors are defined via uppercase, two character strings.
Striped/banded wires can be specified by simply concatenating multiple colors, with no space inbetween, eg. `GNYE` for green-yellow.

The following colors are understood:

- `BK` ![##000000](https://via.placeholder.com/15/000000/000000?text=+) (black)
- `WH` ![##ffffff](https://via.placeholder.com/15/ffffff/000000?text=+) (white)
- `GY` ![##999999](https://via.placeholder.com/15/999999/000000?text=+) (grey)
- `PK` ![##ff66cc](https://via.placeholder.com/15/ff66cc/000000?text=+) (pink)
- `RD` ![##ff0000](https://via.placeholder.com/15/ff0000/000000?text=+) (red)
- `OG` ![##ff8000](https://via.placeholder.com/15/ff8000/000000?text=+) (orange)
- `YE` ![##ffff00](https://via.placeholder.com/15/ffff00/000000?text=+) (yellow)
- `OL` ![##708000](https://via.placeholder.com/15/708000/000000?text=+) (olive green)
- `GN` ![##00ff00](https://via.placeholder.com/15/00ff00/000000?text=+) (green)
- `TQ` ![##00ffff](https://via.placeholder.com/15/00ffff/000000?text=+) (turquoise)
- `LB` ![##a0dfff](https://via.placeholder.com/15/a0dfff/000000?text=+) (light blue)
- `BU` ![##0066ff](https://via.placeholder.com/15/0066ff/000000?text=+) (blue)
- `VT` ![##8000ff](https://via.placeholder.com/15/8000ff/000000?text=+) (violet)
- `BN` ![##895956](https://via.placeholder.com/15/895956/000000?text=+) (brown)
- `BG` ![##ceb673](https://via.placeholder.com/15/ceb673/000000?text=+) (beige)
- `IV` ![##f5f0d0](https://via.placeholder.com/15/f5f0d0/000000?text=+) (ivory)
- `SL` ![##708090](https://via.placeholder.com/15/708090/000000?text=+) (slate)
- `CU` ![##d6775e](https://via.placeholder.com/15/d6775e/000000?text=+) (copper)
- `SN` ![##aaaaaa](https://via.placeholder.com/15/aaaaaa/000000?text=+) (tin)
- `SR` ![##84878c](https://via.placeholder.com/15/84878c/000000?text=+) (silver)
- `GD` ![##ffcf80](https://via.placeholder.com/15/ffcf80/000000?text=+) (gold)

<!-- color list generated with a helper script: -->
<!-- https://gist.github.com/formatc1702/3c93fb4c5e392364899283f78672b952 -->

## Cable color codes

Supported color codes:

- `DIN` for [DIN 47100](https://en.wikipedia.org/wiki/DIN_47100)

  ![##ffffff](https://via.placeholder.com/15/ffffff/000000?text=+) ![##895956](https://via.placeholder.com/15/895956/000000?text=+) ![##00ff00](https://via.placeholder.com/15/00ff00/000000?text=+) ![##ffff00](https://via.placeholder.com/15/ffff00/000000?text=+) ![##999999](https://via.placeholder.com/15/999999/000000?text=+) ![##ff66cc](https://via.placeholder.com/15/ff66cc/000000?text=+) ![##0066ff](https://via.placeholder.com/15/0066ff/000000?text=+) ![##ff0000](https://via.placeholder.com/15/ff0000/000000?text=+) ![##000000](https://via.placeholder.com/15/000000/000000?text=+) ![##8000ff](https://via.placeholder.com/15/8000ff/000000?text=+) ...

- `IEC` for [IEC 60757](https://en.wikipedia.org/wiki/Electronic_color_code#Color_band_system) ("ROY G BIV")

  ![##895956](https://via.placeholder.com/15/895956/000000?text=+) ![##ff0000](https://via.placeholder.com/15/ff0000/000000?text=+) ![##ff8000](https://via.placeholder.com/15/ff8000/000000?text=+) ![##ffff00](https://via.placeholder.com/15/ffff00/000000?text=+) ![##00ff00](https://via.placeholder.com/15/00ff00/000000?text=+) ![##0066ff](https://via.placeholder.com/15/0066ff/000000?text=+) ![##8000ff](https://via.placeholder.com/15/8000ff/000000?text=+) ![##999999](https://via.placeholder.com/15/999999/000000?text=+) ![##ffffff](https://via.placeholder.com/15/ffffff/000000?text=+) ![##000000](https://via.placeholder.com/15/000000/000000?text=+) ...

- `TEL` and `TELALT`  for [25-pair color code](https://en.wikipedia.org/wiki/25-pair_color_code)
- `T568A` and `T568B` for [TIA/EIA-568](https://en.wikipedia.org/wiki/TIA/EIA-568#Wiring) (e.g. Ethernet)
- `BW` for alternating black and white


## Images

Both connectors and cables accept including an image with a caption within their respective nodes.

```yaml
image:
  src: <path>        # path to the image file
  # optional parameters:
  caption: <str>     # text to display below the image
  width: <int>       # range: 1~65535; unit: points
  height: <int>      # range: 1~65535; unit: points
  # if only one dimension (width/height) is specified, the image is scaled proportionally.
  # if both width and height are specified, the image is stretched to fit.
```

For more fine grained control over the image parameters, please see [`advanced_image_usage.md`](advanced_image_usage.md).


## Multiline strings

The following attributes accept multiline strings:
- `type`
- `subtype` (connectors only)
- `notes`
- `manufacturer`
- `mpn`
- `image.caption`

### Method 1

By using `|`, every following indented line is treated as a new line.

```yaml
attribute: |
  This is line 1.
  This is line 2.
```

### Method 2

By using double quoted strings, `\n` within the string is converted to a new line.

```yaml
attribute: "This is line 1.\nThis is line 2."
```

Plain (no quotes) or single quoted strings do not convert `\n`.

See [yaml-multiline.info](https://yaml-multiline.info/) for more information.

## Inheritance

[YAML anchors and references](https://blog.daemonl.com/2016/02/yaml.html) are useful for defining and referencing information that is used more than once in a file, e.g. when using defining multiple connectors of the same type or family. See [Demo 02](../examples/demo02.yml) for an example.
