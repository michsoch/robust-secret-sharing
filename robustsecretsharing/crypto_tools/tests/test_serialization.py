from robustsecretsharing.crypto_tools import serialization
import pytest


def test_encode_decode_small():
    bytestring = '123'
    int_result = serialization.convert_bytestring_to_int(bytestring)
    assert serialization.convert_int_to_bytestring(int_result) == bytestring


def test_pack_unpack_large():
    bytestring = ('123456789012345678901234567890123456789012345678901234567890'
                  '123456789012345678901234567890123456789012345678901234567890'
                  '123456789012345678901234567890123456789012345678901234567890'
                  '123456789012345678901234567890123456789012345678901234567890'
                  '123456789012345678901234567890123456789012345678901234567890'
                  '123456789012345678901234567890123456789012345678901234567890'
                  '123456789012345678901234567890123456789012345678901234567890')
    int_result = serialization.convert_bytestring_to_int(bytestring)
    assert serialization.convert_int_to_bytestring(int_result) == bytestring


def test_encode_decode_standard():
    bytestring = 'x\x02e\x9c\x9e\x16\xe9\xea\x15+\xbf]\xebx;o\xef\xc9X1c\xaepj\xebj\x12\xe3r\xcd\xeaM'
    int_result = serialization.convert_bytestring_to_int(bytestring)
    assert serialization.convert_int_to_bytestring(int_result) == bytestring


def test_encode_decode_leading_zeros():
    bytestring = '\x00\x00e\x9c\x9e\x16\xe9\xea\x15+\xbf]\xebx;o\xef\xc9X1c\xaepj\xebj\x12\xe3r\xcd\xeaM'
    int_result = serialization.convert_bytestring_to_int(bytestring)
    assert serialization.convert_int_to_bytestring(int_result) == bytestring


def test_encode_decode_leading_star():
    bytestring = '**e\x9c\x9e\x16\xe9\xea\x15+\xbf]\xebx;o\xef\xc9X1c\xaepj\xebj\x12\xe3r\xcd\xeaM'
    int_result = serialization.convert_bytestring_to_int(bytestring)
    assert serialization.convert_int_to_bytestring(int_result) == bytestring


def test_encode_decode_trailing_zeros():
    bytestring = 'e\x9c\x9e\x16\xe9\xea\x15+\xbf]\xebx;o\xef\xc9X1c\xaepj\xebj\x12\xe3r\xcd\xeaM\x00\x00'
    int_result = serialization.convert_bytestring_to_int(bytestring)
    assert serialization.convert_int_to_bytestring(int_result) == bytestring


def test_small_mutation():
    bytestring = '\x00\x9c\x9e\x16\xe9'
    int_result = serialization.convert_bytestring_to_int(bytestring) + 100  # small relative to bytestring length
    assert serialization.convert_int_to_bytestring(int_result) != bytestring


def test_large_mutation():
    bytestring = '\x00\x9c\x9e\x16\xe9'
    int_result = serialization.convert_bytestring_to_int(bytestring) + 1000000000000000000  # large relative to bytestring length
    with pytest.raises(ValueError):
        serialization.convert_int_to_bytestring(int_result)
