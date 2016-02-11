import codecs

PREPEND = '\x7E'


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
