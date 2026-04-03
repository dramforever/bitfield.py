#!/usr/bin/env python

import sys
import json

CHARSET_ASCII = { 'vertical': '|', 'joint': '\'', 'horizontal': '-', 'start': '<', 'mid': '=', 'end': '>', 'single': 'x', 'gap': '-' }
CHARSET_UNICODE = { 'vertical': '│', 'joint': '╰', 'horizontal': '─', 'start': '└', 'mid': '─', 'end': '┤', 'single': '│', 'gap': ' ' }
charset = CHARSET_UNICODE

def draw_field(field):
    if 'name' not in field:
        return charset['gap'] * field['len']
    elif field['len'] == 1:
        return charset['single']
    else:
        mid = field['len'] - 2
        return f"{charset['start']}{charset['mid'] * mid}{charset['end']}"

def draw_through(field):
    if 'name' not in field:
        return ' ' * field['len']
    else:
        return (' ' * (field['len'] - 1)) + charset['vertical']

def draw_point(field):
    return (' ' * (field['len'] - 1)) + charset['joint']

def describe_field(field, offset, value):
    desc_range = f"[{offset + field['len'] - 1}:{offset}]" if field['len'] > 1 else f'[{offset}]'

    if field['len'] == 1:
        value_str = str(value)
    else:
        value_str = hex(value)

    if 'decode' in field:
        value_desc = f" ({field['decode'].get(str(value), '?')})"
    else:
        value_desc = ''

    return f"{desc_range:7} {field['name']} = {value_str}{value_desc}"

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
            append = charset['horizontal'] * (offset + 1)
            lines.append(f'  {through}{point}{append} {describe_field(f, offset, field_value)}')

        offset += f['len']

    return lines

def usage():
    print(f'Usage: {sys.argv[0]} [ -unicode | -ascii ] <format.json> <value>', file=sys.stderr)

def main():
    global charset

    if len(sys.argv) == 3:
        _, format, value = sys.argv
        flag = '-unicode'
    elif len(sys.argv) == 4:
        _, flag, format, value = sys.argv
    else:
        return usage()

    if flag == '-unicode':
        charset = CHARSET_UNICODE
    elif flag == '-ascii':
        charset = CHARSET_ASCII
    else:
        return usage()

    with open(format, 'rb') as f:
        fields = json.load(f)

    value = int(value, 0)
    print('\n'.join(draw_value(fields, value)))

if __name__ == '__main__':
    main()
