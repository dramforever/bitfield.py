#!/usr/bin/env python

import sys
import json

def draw_field(field):
    if 'name' not in field:
        return '-' * field['len']
    elif field['len'] == 1:
        return 'x'
    else:
        mid = field['len'] - 2
        return f"<{'=' * mid}>"

def draw_through(field):
    if 'name' not in field:
        return ' ' * field['len']
    else:
        return (' ' * (field['len'] - 1)) + '|'

def draw_point(field):
    return (' ' * (field['len'] - 1)) + '\''

def describe_field(field, offset, value):
    desc_range = f"[{offset + field['len'] - 1}:{offset}]" if field['len'] > 1 else f'[{offset}]'
    if 'decode' in field:
        value = field['decode'].get(str(value), f'<0x{value:x}>')
    elif field['len'] == 1:
        value = str(value)
    else:
        value = hex(value)

    return f"{desc_range:7} {field['name']} = {value}"

def draw_value(fields, value):
    total_len = sum(f['len'] for f in fields)
    if value >= (1 << total_len):
        raise ValueError(f'Value {value} out of range ({total_len} bits)')

    lines = []

    hex_value = f'{value:x}'.rjust((total_len + 3) // 4, '0')
    hex_pad = (total_len - 1) % 4
    lines.append(f"0x{' ' * hex_pad}{(' '  * 3).join(hex_value)}")

    lines.append(f"0b{f'{value:b}'.rjust(total_len, '0')}")
    lines.append(f"  {''.join(draw_field(f) for f in fields)}")

    offset = 0

    for i in range(len(fields))[::-1]:
        f = fields[i]
        field_value = (value >> offset) & ((1 << f['len']) - 1)
        if 'name' in f:
            through = ''.join(draw_through(f) for f in fields[:i])
            point = draw_point(f)
            append = '-' * (offset + 1)
            lines.append(f'  {through}{point}{append} {describe_field(f, offset, field_value)}')

        offset += f['len']

    return lines

if len(sys.argv) != 3:
    print(f'Usage: {sys.argv[0]} <format.json> <value>')
else:
    _, format, value = sys.argv
    with open(format, 'rb') as f:
        fields = json.load(f)
    value = int(value, 0)
    print('\n'.join(draw_value(fields, value)))
