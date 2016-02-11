from schemes import sss
from crypto_tools import serialization, primes
import pytest

secret = 'x\x02e\x9c\x9e\x16\xe9\xea\x15+\xbf]\xebx;o\xef\xc9X1c\xaepj\xebj\x12\xe3r\xcd\xeaM'  # An example key
alt_secret = 'c4bbcb1fbec99d65bf59d85c8cb62ee2db963f0fe106f483d9afa73bd4e39a8a'


def share_and_recover(num_players, reconstruction_threshold, secret, end):
    bitlength = max(num_players, secret).bit_length()
    prime = primes.get_prime_by_bitlength(bitlength)

    shares = sss.share_secret(num_players, reconstruction_threshold, secret, prime)

    # mimic network transfer
    serialized_shares = [serialization.pack_tuple(share) for share in shares]
    deserialized_shares = [serialization.unpack_tuple(share) for share in serialized_shares]

    return sss.reconstruct_secret(deserialized_shares[:end], prime)


def test_min_shares():
    num_players = 5
    reconstruction_threshold = 2
    end = 2

    secret_int = serialization.convert_bytestring_to_int(secret)

    recovered_secret = serialization.convert_int_to_bytestring(share_and_recover(num_players, reconstruction_threshold, secret_int, end))
    assert recovered_secret == secret


def test_max_shares():
    num_players = 5
    reconstruction_threshold = 2
    end = num_players

    secret_int = serialization.convert_bytestring_to_int(secret)

    recovered_secret = serialization.convert_int_to_bytestring(share_and_recover(num_players, reconstruction_threshold, secret_int, end))
    assert recovered_secret == secret


def test_secret_with_leading_zeroes():
    num_players = 5
    reconstruction_threshold = 2
    end = 2

    # Create secret
    trailing_zero_secret = '\x00\x00e\x9c\x9e\x16\xe9\xea\x15+\xbf]\xebx;o\xef\xc9X1c\xaepj\xebj\x12\xe3r\xcd\xeaM'
    trailing_zero_secret_int = serialization.convert_bytestring_to_int(trailing_zero_secret)

    recovered_secret = serialization.convert_int_to_bytestring(share_and_recover(num_players, reconstruction_threshold, trailing_zero_secret_int, end))
    assert recovered_secret == trailing_zero_secret


def test_2_of_3_sharing():
    num_players = 3
    reconstruction_threshold = 2

    alt_secret_int = serialization.convert_bytestring_to_int(alt_secret)

    recovered_secret = serialization.convert_int_to_bytestring(share_and_recover(num_players, reconstruction_threshold, alt_secret_int, reconstruction_threshold))
    assert recovered_secret == alt_secret


def test_4_of_7_sharing():
    num_players = 7
    reconstruction_threshold = 4

    alt_secret_int = serialization.convert_bytestring_to_int(alt_secret)

    recovered_secret = serialization.convert_int_to_bytestring(share_and_recover(num_players, reconstruction_threshold, alt_secret_int, reconstruction_threshold))
    assert recovered_secret == alt_secret


def test_5_of_9_sharing():
    num_players = 9
    reconstruction_threshold = 5

    alt_secret_int = serialization.convert_bytestring_to_int(alt_secret)

    recovered_secret = serialization.convert_int_to_bytestring(share_and_recover(num_players, reconstruction_threshold, alt_secret_int, reconstruction_threshold))
    assert recovered_secret == alt_secret


def test_2_of_2_sharing():
    num_players = 2
    reconstruction_threshold = 2

    alt_secret_int = serialization.convert_bytestring_to_int(alt_secret)

    recovered_secret = serialization.convert_int_to_bytestring(share_and_recover(num_players, reconstruction_threshold, alt_secret_int, reconstruction_threshold))
    assert recovered_secret == alt_secret


def test_bad_configuration_threshold():
    num_players = 2
    reconstruction_threshold = 5
    secret_int = serialization.convert_bytestring_to_int(secret)

    bitlength = max(num_players, secret_int).bit_length()
    sharing_prime = primes.get_prime_by_bitlength(bitlength)

    with pytest.raises(ValueError):
        sss.share_secret(num_players, reconstruction_threshold, secret_int, sharing_prime)


def test_bad_configuration_prime_small_secret():
    num_players = 5
    reconstruction_threshold = 2
    bad_secret_int = serialization.convert_bytestring_to_int('x\xFF\xFF')

    sharing_prime = 7

    with pytest.raises(ValueError):
        sss.share_secret(num_players, reconstruction_threshold, bad_secret_int, sharing_prime)


def test_bad_configuration_prime_small_num_players():
    bad_num_players = 40
    reconstruction_threshold = 2
    secret_int = 10

    sharing_prime = 31

    with pytest.raises(ValueError):
        sss.share_secret(bad_num_players, reconstruction_threshold, secret_int, sharing_prime)


def test_bad_configuration_prime_none():
    num_players = 2
    reconstruction_threshold = 5
    sharing_prime = None

    secret_int = serialization.convert_bytestring_to_int(secret)

    with pytest.raises(ValueError):
        sss.share_secret(num_players, reconstruction_threshold, secret_int, sharing_prime)
