# -*- coding: latin-1 -*-
"""
Original source code: https://github.com/chfoo/notaol/

Changes:
    - Added support for many more atoms
    - Added support for FDO criteria flags
    - Added support for FDO object type flags
    - Added support for FDO save register flags
    - code refactoring for better readability
"""
import io
import enum
import struct
import logging
import fdo.stream
import traceback

from gid_tools.gid_int import gid_to_int
#from gid_tools.int_gid import int_to_gid
from fdo.atomdatatype import AtomDataType
from fdo.datatype import DataType
from fdo.atomdef import Atom


_logger = logging.getLogger(__name__)


class AtomTypeComp(enum.IntEnum):
    no_comp = 0
    length_comp = 1
    data_comp = 2
    atom_noarg_comp = 3
    atom_comp = 4
    zero_comp = 5
    one_comp = 6
    extended = 7


class Criteria(enum.IntEnum):
    SELECTION = 1
    CLOSE = 2
    GAIN_FOCUS = 4
    LOSE_FOCUS = 5
    CANCEL = 6
    ENTER_FREE = 7
    ENTER_PAID = 8
    CREATE = 9
    SET_ONLINE = 10
    SET_OFFLINE = 11
    RESTORE = 12
    MINIMIZE = 14
    RESTORE_FROM_MAXIMIZE = 15
    RESTORE_FROM_MINIMIZE = 16
    TIMEOUT = 17
    SCREEN_NAME_CHANGED = 18
    MOVIE_OVER = 19
    DROP = 20
    URL_DROP = 21
    USER_DELETE = 22
    TOGGLE_UP = 23
    ACTIVATED = 24
    SEACTIVATED = 25
    POPUPMENU = 26
    DESTROYED = 27
    # basically 128-255 are assigned based on the FDO protocol
    # your form was created in? they have corosponding actions
    #ACTION_TOOL = range(127, 255)

    @classmethod
    def is_valid(cls, value):
        return value in Criteria.__members__.keys() or value in Criteria.__members__.values()

# redundant, still learning the class's so I'm leaving it here
criteria = {
    'SELECTION': 1,
    'CLOSE': 2,
    'GAIN_FOCUS': 4,
    'LOSE_FOCUS': 5,
    'CANCEL': 6,
    'ENTER_FREE': 7,
    'ENTER_PAID': 8,
    'CREATE': 9,
    'SET_ONLINE': 10,
    'SET_OFFLINE': 11,
    'RESTORE': 12,
    'MINIMIZE': 14,
    'RESTORE_FROM_MAXIMIZE': 15,
    'RESTORE_FROM_MINIMIZE': 16,
    'TIMEOUT': 17,
    'SCREEN_NAME_CHANGED': 18,
    'MOVIE_OVER': 19,
    'DROP': 20,
    'URL_DROP': 21,
    'USER_DELETE': 22,
    'TOGGLE_UP': 23,
    'ACTIVATED': 24,
    'SEACTIVATED': 25,
    'POPUPMENU': 26,
    'DESTROYED': 27,
    'SAVED': 28,
    'HAVE_MAIL': 128,
    'NO_MAIL': 129,
    'CHAT_UPDATE_COUNT': 130,
    'GIFVIEW_COMPLETE': 132,
    'Mip_Mail_Get_Status': 133,
    'Mip_Mail_Keep_As_New': 134,
    'Mip_Mail_Ignore': 135,
    'Mip_Mail_Read': 136,
    'Mip_Mail_Unsend': 137,
    'Mip_Mailsort_Update': 138,
    # basically 128-255 are assigned based on the FDO protocol
    'ACTION_TOOL': [128-255],
    # your form was created in? they have corosponding actions
}


class AlertType(enum.IntEnum):
    info = 1
    error = 2
    pop_info = 3
    pop_error = 4
    warning = 5
    pop_warning = 6

    @classmethod
    def is_valid(cls, value):
        return value in AlertType.__members__.keys() or value in AlertType.__members__.values()


class ObjType(enum.IntEnum):
    org_group =  0
    independent = 1
    ind_group = 1
    dms_list = 2
    sms_list = 3
    dss_list = 4
    sss_list = 5
    trigger = 6
    ornament = 7
    view = 8
    edit_view = 9
    boolean = 10
    selectable_boolean = 11
    range = 12
    select_range = 13
    tool_group = 17
    tab_group = 18
    tab_page = 19
    tree_control = 21 # AOL 2.5/3.0 do not know what this value is

    @classmethod
    def is_valid(cls, value):
        return value in ObjType.__members__.keys() or value in ObjType.__members__.values()


ObjType = {
    'org_group': 0,
    'independent': 1,
    'ind_group': 1,
    'dms_list': 2,
    'sms_list': 3,
    'dss_list': 4,
    'sss_list': 5,
    'trigger': 6,
    'ornament': 7,
    'view': 8,
    'edit_view': 9,
    'boolean': 10,
    'selectable_boolean': 11,
    'range': 12,  # 12,
    'select_range': 13,  # 13,
    'tool_group': 17,  # 17,
    'tab_group': 18,  # 18,
    'tab_page': 19,  # 19,
    'tree_control': 21,  # 21, # AOL 2.5/3.0 do not know what this is
}


class Orientation(enum.IntEnum):
    # horizantal plane or vertical plane
    h = int('10000000', 2)
    v = int('01000000', 2)
    # horizontal orientations
    hc = int('00000000', 2)
    hl = int('00001000', 2)
    hr = int('00010000', 2)
    hf = int('00011000', 2)
    he = int('00100000', 2)
    #hn = int('00000000', 2)
    # vertical orientations
    vc = int('00000000', 2)
    vt = int('00000001', 2)
    vb = int('00000010', 2)
    vf = int('00000011', 2)
    ve = int('00000100', 2)
    #vn = int('00000000', 2)


class Position(enum.IntEnum):
    # string values
    top_left =  1
    top_center = 2
    top_right = 3
    center_left = 4
    center_center = 5
    center_right = 6
    bottom_left = 7
    bottom_center = 8
    bottom_right = 9

    @classmethod
    def is_valid(cls, value):
        return value in Position.__members__.keys() or value in Position.__members__.values()


class FrameType(enum.IntEnum):
    none = 0
    single_line_pop_in = 1
    single_line_pop_out = 2
    pop_in = 3
    pop_out = 4
    double_line = 5
    shadow = 6
    highlight = 7


class FontID(enum.IntEnum):
    arial = 0
    courier = 1
    times_roman = 2
    system = 3
    fixed_system = 4
    ms_serif = 5
    ms_sans_serif = 6
    small_fonts = 7
    courier_new = 8
    script = 9
    ms_mincho = 10
    ms_gothic = 11

    @classmethod
    def is_valid(cls, value):
        return value in FontID.__members__.keys() or value in FontID.__members__.values()


class SaveRegType(enum.IntEnum):
    A = 0
    B = 1
    C = 2
    D = 3

    @classmethod
    def is_valid(cls, value):
        return value in ['A', 'B', 'C', 'D', 1, 2, 3, 4, 5, 6, 7]
    # '1' = 0
    # '2' = 1
    # '3' = 2
    # '4' = 3
    # '5' = 4
    # '6' = 5
    # '7' = 6


saveRegType = {
    'A': 0,
    'B': 1,
    'C': 2,
    'D': 3,
    1: 0,
    2: 1,
    3: 2,
    4: 3,
    5: 4,
    6: 5,
    7: 6,
}


class TriggerStyle(enum.IntEnum):
    default = 0
    place = 1
    rectangle = 2
    group_state = 3
    picture = 4
    plain_picture = 5

    @classmethod
    def is_valid(cls, value):
        return value in TriggerStyle.__members__.keys() or value in TriggerStyle.__members__.values()


class YesNoBoolean(enum.IntEnum):
    yes = 1
    no = 0

    @classmethod
    def is_valid(cls, value):
        return value in YesNoBoolean.__members__.keys() or value in YesNoBoolean.__members__.values()


class DodType(enum.IntEnum):
    dod_raw = 0
    # dod_binary = 0
    dod_art = 1
    dod_form_art = 2
    dod_sound = 3

    @classmethod
    def is_valid(cls, value):
        return value in DodType.__members__.keys() or value in DodType.__members__.values()



def get_atom_type(num):
    # TODO: figure out what this means
    return num >> 5


def get_atom_value(num):
    # TODO: figure out what this means
    return num & 0x1f


def unserialize(last_protocol_id, data):
    index = 0

    while index < len(data):
        atom_protocol_add = 0
        atom_add = 0
        while (get_atom_type(data[index]) == AtomTypeComp.extended):
            atom_protocol_add += (data[index] & 0x18) << 2
            atom_add += (data[index] & 0x06) << 4
            index += 1

        atom_type = get_atom_type(data[index])

        match atom_type:
            case AtomTypeComp.no_comp:
                atom_protocol_id = get_atom_value(data[index])
                index += 1
                if index < len(data)+1:
                    atom_id = data[index]
                    index += 1
                if index <= len(data)+1:
                    # TODO: Getting index out of range errors here every now and then.
                    arg_length = data[index]
                    index += 1

                arg = data[index:index + arg_length]
                index += arg_length

            case AtomTypeComp.length_comp:
                atom_protocol_id = get_atom_value(data[index])
                index += 1
                atom_id = get_atom_value(data[index])
                arg_length = get_atom_type(data[index])
                index += 1
                arg = data[index:index + arg_length]
                index += arg_length

            case AtomTypeComp.data_comp:
                atom_protocol_id = get_atom_value(data[index])
                index += 1
                atom_id = get_atom_value(data[index])
                arg_length = 1
                arg = get_atom_type(data[index])
                index += 1

            case AtomTypeComp.atom_noarg_comp:
                atom_protocol_id = last_protocol_id
                atom_id = get_atom_value(data[index])
                index += 1
                arg_length = 0
                arg = None

            case AtomTypeComp.atom_comp:
                atom_protocol_id = last_protocol_id
                atom_id = get_atom_value(data[index])
                index += 1
                arg_length = data[index]
                index += 1
                arg = data[index:index + arg_length]
                index += arg_length

            case AtomTypeComp.zero_comp:
                atom_protocol_id = last_protocol_id
                atom_id = get_atom_value(data[index])
                index += 1
                arg_length = 1
                arg = 0

            case AtomTypeComp.one_comp:
                atom_protocol_id = last_protocol_id
                atom_id = get_atom_value(data[index])
                index += 1
                arg_length = 1
                arg = 1

        atom_protocol_id += atom_protocol_add
        atom_id += atom_add
        last_protocol_id = atom_protocol_id

        try:
            atom_def = Atom((atom_protocol_id, atom_id))
            data_type = getattr(AtomDataType, atom_def.name)
        except ValueError:
            atom_def = '(unknown atom)'
            data_type = None
            print(atom_protocol_id, atom_id, atom_def, arg_length, arg)

        if data_type == DataType.stream:
            atom_stream = fdo.stream.AtomStream()
            atom_stream.parse(arg)

        yield (atom_protocol_id, atom_id, atom_def, arg_length, arg)


def serialize(file, atom_def, *args):
    arg_len: int = 0
    data: bytes = b''
    atom_type_id, atom_sub_id = atom_def

    try:
        if atom_type_id > 32 or atom_sub_id > 32:
            # Extended byte
            # byte_num = 0xe0
            # byte_num |= (atom_type_id & 0x60) >> 2
            # byte_num |= (atom_sub_id & 0x60) >> 4
            file.write(bytes([atom_type_id, atom_sub_id]))
        else:
            # file.write(bytes([byte_num]))
            file.write(bytes([atom_type_id & 0x1f, atom_sub_id & 0x1f]))

        for arg in args:
            data_type = getattr(AtomDataType, atom_def.name)

            match data_type:
                case DataType.dword:
                    # dword is 4 bytes long
                    # error trap arg for None
                    if arg is None: arg = 0
                    if isinstance(arg, str):
                        if DodType.is_valid(arg):
                            arg = DodType[arg]
                        else:
                            arg = gid_to_int(arg) or 0

                    if arg <= 255:
                        data = struct.pack('!B', arg)
                    else:
                        data = struct.pack('!I', arg)

                    arg_len = len(data)

                case DataType.vdword:
                    # the first argument should be A,B,C, or D string representing the save register to use, or
                    # 1,2,3,4 integer value representing the save register to use
                    if arg in saveRegType.keys():
                        data = struct.pack('!B', saveRegType[arg])
                        if len(args) > 1:
                            # second argument is an integer value - but there may not be a second argument
                            data += struct.pack('!I', args[1])
                        # data += struct.pack('!B', args[1])

                        arg_len = len(data)
                        assert len(data) == arg_len
                        file.write(bytes([arg_len]))

                        if arg_len:
                            file.write(data)
                        break

                case DataType.var:
                    # var datatype has only one argument.
                    if arg in saveRegType.keys():
                        data = struct.pack('!B', saveRegType[arg])
                        arg_len = len(data)

                case DataType.str:
                    # If not bytes, convert it to bytes
                    if isinstance(arg, str):
                        data = arg.encode('latin-1', 'replace')
                    elif isinstance(arg, int):
                        data = str(arg).encode('latin-1', 'replace')
                        # data = struct.pack('!B', arg)
                    else:
                        data = arg
                    arg_len = len(data)

                case DataType.word:
                    # word is 2 bytes long
                    # arguments can be streams or integer values
                    # check if argument is an integer value
                    if isinstance(arg, int):
                        data = struct.pack('!H', arg)
                        arg_len = len(data)
                    elif Atom[arg]:
                        arg_list = Atom[arg]
                        data = struct.pack(f'!{len(arg_list)}B', *arg_list)
                        arg_len = len(data)

                case DataType.bool:
                    if isinstance(arg, str) and YesNoBoolean.is_valid(arg):
                        data = struct.pack('!?', YesNoBoolean[arg])
                    else:
                        data = struct.pack('!?', arg)
                    arg_len = len(data)

                case DataType.orient:
                    orient_bits = 0
                    # check if arg is a string object
                    if isinstance(arg, str):
                        # loop over the string object 1 char at a time, add the values up
                        for i, char in enumerate(arg, start=0):
                            # horizontal justification bits
                            if i == 1: char = 'h' + char
                            # virtical justification bits
                            if i == 2: char = 'v' + char
                            if Orientation[char]:
                                orient_bits += Orientation[char]
                        data += struct.pack('!B', orient_bits)

                    else:
                        data = struct.pack('!B', arg)
                    arg_len = len(data)

                case DataType.crit:
                    # i had set crit to be 2 bytes awhile back in my testing and it "seemed" to work,
                    # however it is only supossed to be 1 bytes from 0-255 and that's it.
                    # this should fix some act_do_action issues
                    arg_len = 1
                    data = struct.pack('!B', arg)

                case DataType.token:
                    # 2 arguments always, first should be a token, the second can be an empty value
                    if isinstance(arg, (bytes, bytearray)):
                        data = arg
                        arg_len = len(data)
                    elif isinstance(arg, int):
                        data = struct.pack('!I', arg)
                        arg_len = len(data)
                    elif isinstance(arg, str):
                        data = arg.encode('latin-1', 'replace')
                        arg_len = len(data)

                case DataType.alert:
                    # async_alert puts the total length byte after the FDO
                    # class-protocol.
                    # [class-protocol][len][alert type][text]

                    # If not bytes, convert it to bytes
                    if isinstance(arg, str):
                        data += arg.encode('latin-1', 'replace')
                    elif isinstance(arg, int):
                        data += struct.pack('!B', arg)
                        continue
                    else:
                        data += arg
                    arg_len = len(data)

                case DataType.multi:
                    # Datatype.multi takes atoms as arguments; so we need to evaluate the atom passed
                    # This works perfect when viewing the data sent to the client with the Atomdebugger.
                    # However, if you misspell an atom it will error out (no shit!)
                    if Atom[arg]:
                        arg_list = Atom[arg]
                        data = struct.pack(f'!{len(arg_list)}B', *arg_list)
                        arg_len = len(data)

                case DataType.atom:
                    # Datatype.atom takes atoms as arguments; so we need to evaluate the atom passed
                    # This works perfect when viewing the data sent to the client with the Atomdebugger.
                    # However, if you misspell an atom it will error out (no shit!)
                    if Atom[arg]:
                        arg_list = Atom[arg]
                        data = struct.pack(f'!{len(arg_list)}B', *arg_list)
                        arg_len = len(data)

                case DataType.stream:
                    # The stream datatype is a collection of FDO atoms eg.:
                    #   uni_start_stream
                    #       async_online
                    #   uni_end_stream
                    # each atom can take arguments, the streams are usually the arguments
                    # of act_replace_select_action, act_replace_action, and the like.
                    # Start a bytes buffer to write to
                    buffer = io.BytesIO()
                    # serialize the stream data, write it to our buffer
                    for item in args:
                        atomdef = item[0]
                        argss = item[1:]
                        serialize(buffer, atomdef, *argss)
                    # get the bytes from the buffer, and the length of the bytes
                    data = buffer.getvalue()
                    arg_len = len(data)

                case DataType.gid:
                    # Check if arg is an integer or string
                    if isinstance(arg, int):
                        #data = struct.pack('!I', arg)
                        # check how many digits are in the integer
                        if len(str(arg)) in range(1, 4):
                            # 1 to 3 digits long
                            data = struct.pack('!B', arg)
                        if len(str(arg)) in range(5, 8):
                            # 5 to 7 digits long
                            data = struct.pack('!I', arg)
                            # strip the first byte from data
                            # this is required for 2 part GIDs (32-12345) or
                            # the GID will have a leading 0 when the client software
                            # parses the sent FDO stream. (0-32-12345)
                            data = data[1:]
                        arg_len = len(data)

                    elif isinstance(arg, str):
                        # convert string GID to long integer
                        num = gid_to_int(arg) or 0
                        data = struct.pack('!I', num)
                        if len(str(num)) in range(5, 8):
                            data = data[1:]
                        arg_len = len(data)

                    else:
                        # Unknown argument type, so do nothing.
                        _logger.warning(f"Unknown argument type for GID: {arg}")
                        arg_len = 0
                        data = b''

                case DataType.raw:
                    # not sure how to handle raw data type?
                    # I believe raw data is comma seperated bytes?
                    # Will probably have to check args for integer value (bytes) or strings and process accordingly
                    # if isinstance(arg, (bytes, bytearray, str)):
                    #     data = arg
                    #     arg_len = len(data)
                    #     break
                    if isinstance(arg, (bytes, bytearray, str)):
                        for byte in arg:
                            if isinstance(byte, str):
                                data += byte.encode('latin-1', 'replace')
                                continue
                            data += struct.pack('!B', byte)
                    else:
                        for argg in args:
                            data += struct.pack('!B', argg)

                    arg_len = len(data)

                case DataType.byte:
                    if not arg: continue
                    if isinstance(arg, str) and Position.is_valid(arg):
                        # check if arg is a string or a bytes object
                        data = struct.pack('!B', Position[arg])
                    elif isinstance(arg, str) and FontID.is_valid(arg):
                        # if this a font?
                        data = struct.pack('!B', FontID[arg])
                    else:
                        data = struct.pack('!B', arg)
                    arg_len = len(data)

                case DataType.bytelist:
                    # build the argument bytes
                    if isinstance(arg, str) and arg in FrameType:
                        # this is a frame type
                        data = struct.pack('!B', FrameType[arg])

                    else:
                        for dat in args:
                            if isinstance(dat, str):
                                dat = dat.encode('latin-1', 'replace')
                                data += struct.pack('!B', len(dat))
                                data += dat
                                continue
                            if dat > 255:
                                data += struct.pack('!H', dat)
                            else:
                                data += struct.pack('!B', dat)

                    arg_len = len(data)

                case DataType.objst:
                    # there should only ever be 2 arguments passed here,
                    # if more it will crash, but I don't care right now
                    if args[0] in ObjType.keys():
                        obj_type = struct.pack('!B', int(ObjType[args[0]]))
                    else:
                        obj_type = struct.pack('!B', int(args[0]))

                    if len(args) > 1:
                        data = args[1].encode('latin-1', 'replace')
                    data = obj_type + data

                    arg_len = len(data)
                    assert len(data) == arg_len
                    file.write(bytes([arg_len]))

                    if arg_len:
                        file.write(data)
                    break

                case DataType.vstring:
                    # vstring is used for FDO streams like var_string_set <A, "String">
                    # first argument will be either a single letter of: A,B,C,D or a number of: 0,1,2,3
                    if arg in saveRegType.keys():
                        data = struct.pack('!B', saveRegType[arg])
                        # second argument is a string of unknown length
                        data += args[1].encode('latin-1', 'replace')

                        arg_len = len(data)
                        assert len(data) == arg_len
                        file.write(bytes([arg_len]))

                        if arg_len:
                            file.write(data)
                        break

                case _:
                    raise Exception('unhandled data type {}'.format(data_type))


            assert len(data) == arg_len
            file.write(bytes([arg_len]))

            if arg_len:
                file.write(data)
            # we need to break out of the loop with a bytelist/raw/stream otherwise it mangles the FDO bytes
            if (data_type == DataType.bytelist
                or data_type == DataType.raw
                or data_type == DataType.stream
                # or data_type == DataType.alert
                ):
                break

        data_type = getattr(AtomDataType, atom_def.name)
        # any data type that is NOT of this list needs to have a zero byte value following it for the FDO to function
        if not args and (
            data_type != DataType.objst
            or data_type != DataType.gid
            or data_type != DataType.raw
            or data_type != DataType.str
            or data_type != DataType.dword
            or data_type != DataType.bytelist
            or data_type != DataType.var
            or data_type != DataType.orient
            or data_type != DataType.vdword
            or data_type != DataType.multi
            or data_type != DataType.atom
            or data_type != DataType.byte
            or data_type != DataType.alert
        ):
           file.write(b'\x00')

    except Exception as e:
        _logger.error(f"Error serializing stream data: {traceback.format_exc()}")


def unserialize_stream_id(data):
    # FIXME: this is bogus!
    stream_id = 0
    length = 0
    for index, byte_value in zip(range(len(data)), data):
        stream_id <<= 8
        stream_id |= byte_value
        length = index + 1
        if byte_value >= 0x10:
            break

    return (stream_id, data[:length])


def serialize_stream_id(num):
    # FIXME: this is bogus!
    assert num >= 0x10
    length = max(num.bit_length() // 8 + 1, 2)
    return num.to_bytes(length, 'big', signed=False)
