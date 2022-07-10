# -*- coding: utf-8 -*-
''' Converts long integers to AOL GID's.
All numbers are long integers, no floats.

Two part GID integer conversion example:
int = 2097182
W = (2097182 / 65536)
X = (W * 65536)
Y = (2097182 - X)

GID = str(W) + "-" + str(Y)
or
GID = f'{W}-{Y}'



Three part GID integer conversion example:
int = 16779456
W = (16779456 / 65536)
X = (W / 256)
Y = (X * 256)
Z = (W - Y)
A = (W * 256 + Z) * 65536
B = (16779456 - A)

GID = str(X) + "-" + str(Z) + "-" + str(B)
or
GID = f'{X}-{Z}-{B}'

See gid_int.py for more information on how the long integers are calculated if
you find this confusing.
'''

def _do_three_part_gid(input_num: int = 0) -> str | None:
    # sourcery skip: remove-unnecessary-cast
    # if the length is between 8 and 10, convert it to a 3 part GID
    # convert the input_num to an integer
    input_num = int(input_num)
    # divide by 65536
    val1 = int(input_num >> 16)
    # divide val1 by 256
    val = int(val1 >> 8)
    # multiply val by 256
    v = int(val << 8)
    # subtract v from val1
    val2 = int(val1 - v)
    # put the value from val into val1
    val1 = val
    # multiply val1 by 256 add val2 then multiply by 65536
    v2 = int(((val1 << 8) + val2) << 16)
    # subtract the value from the input_num
    val3 = int(input_num - v2)
    # return a 3 part string GID
    return f'{val1}-{val2}-{val3}'


def int_to_gid(input_num: int = 0) -> str | int:
    # sourcery skip: remove-unnecessary-cast
    # check length of input_num to be equal to and between 4 and 7
    if len(str(input_num)) in range(4, 8):
        # if the length is between 4 and 7, convert it to a 2 part GID
        # convert the input_num to an integer if not already
        input_num = int(input_num)
        # divide by 65536 as long
        first_value = int(input_num >> 16)
        # multiply first_value by 65536
        v = int(first_value << 16)
        # subtract the value in v from that in input_num
        second_value = int(input_num - v)
        # return a 2 part string GID
        return f'{first_value}-{second_value}'

    elif len(str(input_num)) in range(8, 11):
        return _do_three_part_gid(input_num)
    else:
        # if the length is not between 4 and 10, return original value
        return input_num
