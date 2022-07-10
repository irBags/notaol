# -*- coding: utf-8 -*-
''' Converts AOL GID's to long integers.

W = (W1 * 65536) + W2.

For example:
GID = 32-30
W = (32 * 65536) + 30 = 2097182

For three part GIDs, such as 1-0-2240,
the left most number is the highest byte (B1) of the four byte GID.
The next number is the low byte (B2) of the hi word.
The last number is the lo word (W2).

GID = 1-0-2240

B1 = 1
B2 = 0
W2 = 2240

W = (B1 * 256 + B2) * 65536 + W2
W = (1 * 256 + 0) * 65536 + 2240 = 16779456

See int_gid.py for the reverse conversion.
'''
import re


def _conv_2(val1: int = 0, val2: int = 0) -> int:
    # sourcery skip: remove-unnecessary-cast
    try:
        # make sure val1 and val2 are integers
        val1 = int(val1)
        val2 = int(val2)
    except Exception as e:
        raise ValueError(e) from e
    # neither values can be larger than 65536
    if val1 > 65536 or val2 > 65536:
        raise ValueError('No value can be larger than 65536.')

    return int((val1 << 16) + val2)


def _conv_3(val1: int = 0, val2: int = 0, val3: int = 0) -> int:
    # sourcery skip: remove-unnecessary-cast

    try:
        # make sure val1, val2, and val3 are integers
        val1 = int(val1)
        val2 = int(val2)
        val3 = int(val3)
    except Exception as e:
        raise ValueError(e) from e
    if val1 > 65536 or val2 > 65536 or val3 > 65536:
        raise ValueError('No value can be larger than 65536.')

    return int((((val1 << 8) + val2) << 16) + val3)


def gid_to_int(input_num: str = '') -> int:
    # split the number at the hyphen(s)
    if [sep for sep in '-,. ' if sep in input_num]:
        input_num = re.split(r'[-,. ]', input_num)
    else:
        # raise ValueError(input_num, 'Value is not an FDO GID number.')
        return int(input_num)

    if len(input_num) == 2:
        # convert the two part number to a long integer
        num = _conv_2(input_num[0], input_num[1])
        return num
    elif len(input_num) == 3:
        # convert the three part number to a long integer
        num = _conv_3(input_num[0], input_num[1], input_num[2])
        return num

    return 0
