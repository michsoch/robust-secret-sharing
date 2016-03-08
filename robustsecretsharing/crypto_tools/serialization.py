import codecs

PREPEND = '*'


def _convert_hex_to_int(hex_string):
    '''
    Args:
        hex_string, any hex_string
    Returns:
        int_val, an integer value representing the hex_string
    '''
    return int(hex_string, 16)


def _convert_int_to_hex(int_val):
    '''
    Args:
        int_val, any integer
    Returns:
        hex_string, a hex_string of even length
    '''
    hex_string = format(int_val, 'x')
    if len(hex_string) % 2 is not 0:
        hex_string = '0' + hex_string
    return hex_string


def _convert_bytestring_to_hex(byte_string):
    '''
    Args:
        byte_string, any byte_string
    Returns:
        hex_string, a hex_string that can be passed to _convert_hex_to_bytestring
                    and will be larger by a byte than the value of the bytestring
    '''
    return codecs.encode(PREPEND + byte_string, 'hex')  # preserve leading zeros in the bytestring


def _convert_hex_to_bytestring(hex_string):
    '''
    Args:
        hex_string, the hex_string returned from _convert_bytestring_to_hex
    Returns:
        byte_string, the bytestring passed to _convert_bytestring_to_hex
    Raises:
        ValueError, cannot parse because bytestring is missing prepend value
    '''
    byte_string = codecs.decode(hex_string, 'hex')
    if byte_string.startswith(PREPEND):
        return codecs.decode(hex_string, 'hex')[len(PREPEND):]
    else:
        raise ValueError("cannot parse bytestring")


def convert_bytestring_to_int(byte_string):
    '''
    Args:
        byte_string, any bytestring value
    Returns:
        an integer that can be passed to convert_int_to_bytestring
    Note that this integer will be larger by a byte than the value of the bytestring
    '''
    hex_string = _convert_bytestring_to_hex(byte_string)
    return _convert_hex_to_int(hex_string)


def convert_int_to_bytestring(int_val):
    '''
    Args:
        int_val, an integer as returned by convert_bytestring_to_int
    Returns:
        the bytestring passed to convert_bytestring_to_int
    Raises:
        ValueError, resultant bytestring is not of the correct form
    '''
    hex_string = _convert_int_to_hex(int_val)
    return _convert_hex_to_bytestring(hex_string)
