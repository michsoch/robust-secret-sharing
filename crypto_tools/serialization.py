import codecs
import struct

PREPEND = '*'
DELIM = ','

UNPACK_ERROR_STRING = "cannot parse packed tuple"


def pack_tuple(two_tup):
    '''
    Args:
        two_tup, a tuple of two integers
    Returns:
        a string that can be parsed by unpack_tuple
    Note that invalid parameters passed to this function will not be caught until the output is unpacked
    '''
    x_str = str(two_tup[0])
    y_str = str(two_tup[1])

    x_len_str = str(len(x_str))
    y_len_str = str(len(y_str))

    pack_fmt = "!" + x_len_str + "s" + y_len_str + "s"
    return x_len_str + "," + y_len_str + "," + struct.pack(pack_fmt, x_str, y_str)


def unpack_tuple(packed_string):
    '''
    Args:
        packed_string, the return value of pack_tuple()
    Returns:
        the tuple of two integers that had been passed to pack_tuple
    Raises:
        ValueError, mutations to the packed string render it invalid
        Note that if the packed string is corrupted but can still be parsed there will be no indication of error
    '''
    pieces = packed_string.split(",", 3)  # split into a max of 3 pieces

    if len(pieces) is not 3 or len(pieces[2]) is not int(pieces[0]) + int(pieces[1]):
        raise ValueError(UNPACK_ERROR_STRING)

    unpack_fmt = "!" + pieces[0] + "s" + pieces[1] + "s"
    str_tup = struct.unpack(unpack_fmt, pieces[2])
    return (int(str_tup[0]), int(str_tup[1]))


def convert_bytestring_to_int(bytestring):
    '''
    Args:
        bytestring, any bytestring value
    Returns:
        an integer that can be passed to convert_int_to_bytestring
    '''
    # use the prepend value to preserve leading zeros in the bytestring
    hex_string = codecs.encode(PREPEND + bytestring, 'hex')
    return int(hex_string, 16)


def convert_int_to_bytestring(int_val):
    '''
    Args:
        int_val, an integer as returned by convert_bytestring_to_int
    Returns:
        the bytestring passed to convert_bytestring_to_int
    '''
    # remove possible padding from long conversion and hex formatting
    hex_string = hex(int_val).lstrip('0x').rstrip('L')
    hex_len = len(hex_string)
    if hex_len % 2 is not 0:  # if the resultant length is odd, prepend with a zero
        hex_string = hex_string.zfill(hex_len + 1)

    # strip prepend value added in convert_bytestring_to_int
    return codecs.decode(hex_string, 'hex').lstrip(PREPEND)
