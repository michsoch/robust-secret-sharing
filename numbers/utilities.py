import codecs

prepend = '\x7E'


def convert_bytestring_to_int(bytestring):
    hex_string = codecs.encode(prepend + bytestring, 'hex')
    return int(hex_string, 16)


def convert_int_to_bytestring(int_val):
    hex_string = hex(int_val).lstrip('0x').rstrip('L')
    hex_len = len(hex_string)
    if hex_len % 2 is not 0:
        hex_string = hex_string.zfill(hex_len + 1)
    return codecs.decode(hex_string, 'hex').lstrip(prepend)
