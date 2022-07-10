# -*- coding: utf-8 -*-
''' Converts AOL GUID's to long integers and vice versa.

W = (W1 X 65536) + W2.

For example:
GID = 32-30
W=(32 X 65536)+30=2097182

For three part GIDs, such as 1-0-2240, the left most number is the highest byte (B1) of the four byte GID. The next number is the low byte (B2) of the hi word. The last number is the lo word (W2).

GID = 1-0-2240

B1=1
B2=0
W2=2240

W=(B1X256 + B2)X65536 + W2
W=(1X256+0)X65536 + 2240 = 16779456

'''

from gid_int import gid_to_int
from int_gid import int_to_gid


if __name__ == '__main__':
    print('')
    print('Enter GID to be converted to long integer (eg. 19-0-0, 32-30, 18 0 0, 1.0.27863) or,')
    print('enter a converted long integer to get a GID (eg. 3421567)')
    print('Notes:\tGID seperaters can be any of hyphen(-), period(.), camma(,) or a space( ).')
    print('\tLong integers must be 4 to 10 digits in length.')
    print('')

    if input_num := input('Convert: '):
        print('')
        # check input_num contains only numbers
        if input_num.isdigit():
            print('Converting integer to GID')
            print('Integer:', input_num)
            print('GID:', int_to_gid(input_num))

        elif [sep for sep in '-,. ' if sep in input_num]:
            print('Converting GID to integer')
            print('GID:', input_num)
            print('Integer:', gid_to_int(input_num))

        print('')
