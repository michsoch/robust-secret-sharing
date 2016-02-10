from crypto_tools import utilities


def test_encode_decode_standard():
    bytestring = 'x\x02e\x9c\x9e\x16\xe9\xea\x15+\xbf]\xebx;o\xef\xc9X1c\xaepj\xebj\x12\xe3r\xcd\xeaM'
    int_result = utilities.convert_bytestring_to_int(bytestring)
    assert utilities.convert_int_to_bytestring(int_result) == bytestring


def test_encode_decode_trailing_zero():
    bytestring = '\x00\x00e\x9c\x9e\x16\xe9\xea\x15+\xbf]\xebx;o\xef\xc9X1c\xaepj\xebj\x12\xe3r\xcd\xeaM'
    int_result = utilities.convert_bytestring_to_int(bytestring)
    assert utilities.convert_int_to_bytestring(int_result) == bytestring
