from crypto_tools import serialization
import pytest


def test_pack_unpack_small():
    x = 4444
    y = 1010101010101010
    two_tup = (x, y)

    packed_string = serialization.pack_tuple(two_tup)
    unpacked_tup = serialization.unpack_tuple(packed_string)
    assert two_tup == unpacked_tup


def test_pack_unpack_large():
    x = 123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789
    y = 2468024680246802468024680246802468024680246802468024680246802468024680246802468024680
    two_tup = (x, y)

    packed_string = serialization.pack_tuple(two_tup)
    unpacked_tup = serialization.unpack_tuple(packed_string)
    assert two_tup == unpacked_tup


def test_encode_decode_standard():
    bytestring = 'x\x02e\x9c\x9e\x16\xe9\xea\x15+\xbf]\xebx;o\xef\xc9X1c\xaepj\xebj\x12\xe3r\xcd\xeaM'
    int_result = serialization.convert_bytestring_to_int(bytestring)
    assert serialization.convert_int_to_bytestring(int_result) == bytestring


def test_encode_decode_trailing_zero():
    bytestring = '\x00\x00e\x9c\x9e\x16\xe9\xea\x15+\xbf]\xebx;o\xef\xc9X1c\xaepj\xebj\x12\xe3r\xcd\xeaM'
    int_result = serialization.convert_bytestring_to_int(bytestring)
    assert serialization.convert_int_to_bytestring(int_result) == bytestring


def test_mutate_int():
    x = 4444
    y = 88888888
    two_tup = (x, y)

    packed_string = serialization.pack_tuple(two_tup)
    pieces = packed_string.split(",", 3)

    mid = len(pieces[2]) / 2
    mutated_string = pieces[0] + serialization.DELIM + pieces[1] + serialization.DELIM + pieces[2][:mid] + '333' + pieces[2][mid + 3:]

    unpacked_tup = serialization.unpack_tuple(mutated_string)
    assert unpacked_tup == (x, 88333888)


# error cases

def test_pack_unpack_input_not_ints():
    x = '4444'
    y = '10101Ol010101010'
    two_tup = (x, y)

    packed_string = serialization.pack_tuple(two_tup)

    with pytest.raises(ValueError):
        serialization.unpack_tuple(packed_string)


def test_pack_unpack_too_small():
    x = '4444'
    y = '1010101010101010'
    two_tup = (x, y)

    packed_string = serialization.pack_tuple(two_tup)[:-1]  # remove last character

    with pytest.raises(ValueError) as e_info:
        serialization.unpack_tuple(packed_string)
    assert serialization.UNPACK_ERROR_STRING in str(e_info)


def test_pack_unpack_too_large():
    x = '4444'
    y = '1010101010101010'
    two_tup = (x, y)

    packed_string = serialization.pack_tuple(two_tup) + '888'  # add characters

    with pytest.raises(ValueError) as e_info:
        serialization.unpack_tuple(packed_string)
    assert serialization.UNPACK_ERROR_STRING in str(e_info)


def test_pack_unpack_change_size():
    x = '4444'
    y = '1010101010101010'
    two_tup = (x, y)

    packed_string = serialization.pack_tuple(two_tup)
    pieces = packed_string.split(",", 3)

    with pytest.raises(ValueError) as e_info:
        serialization.unpack_tuple(str(5) + pieces[1] + pieces[2])
    assert serialization.UNPACK_ERROR_STRING in str(e_info)


def test_pack_unpack_out_not_ints():
    x = '4444'
    y = '1010101010101010'
    two_tup = (x, y)

    packed_string = serialization.pack_tuple(two_tup)[:-1] + 'A'  # replace last character with letter

    with pytest.raises(ValueError):
        serialization.unpack_tuple(packed_string)
