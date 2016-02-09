from customexceptions import custom_exceptions
from schemes import sss
from numbers import random, primes
import pytest

# TODO: some tests inspired by https://github.com/blockstack/secret-sharing/blob/master/unit_tests.py
secret = random.convert_bytestring_to_int('x\x02e\x9c\x9e\x16\xe9\xea\x15+\xbf]\xebx;o\xef\xc9X1c\xaepj\xebj\x12\xe3r\xcd\xeaM')  # An example key
alt_secret = random.convert_bytestring_to_int("c4bbcb1fbec99d65bf59d85c8cb62ee2db963f0fe106f483d9afa73bd4e39a8a")


def share_and_recover(num_players, reconstruction_threshold, secret, end):
    prime = primes.get_prime_by_batch([num_players, secret])

    shares = sss.share_secret(num_players, reconstruction_threshold, secret, prime)
    return sss.reconstruct_secret(shares[:end], prime)


def test_min_shares():
    num_players = 5
    reconstruction_threshold = 2
    end = 2

    recovered_secret = share_and_recover(num_players, reconstruction_threshold, secret, end)
    assert recovered_secret == secret


def test_max_shares():
    num_players = 5
    reconstruction_threshold = 2
    end = num_players

    recovered_secret = share_and_recover(num_players, reconstruction_threshold, secret, end)
    assert recovered_secret == secret


def test_secret_with_leading_zeroes():
    num_players = 5
    reconstruction_threshold = 2
    end = 2

    # Create secret
    trailing_zero_secret = random.convert_bytestring_to_int('\x00\x00e\x9c\x9e\x16\xe9\xea\x15+\xbf]\xebx;o\xef\xc9X1c\xaepj\xebj\x12\xe3r\xcd\xeaM')

    recovered_secret = share_and_recover(num_players, reconstruction_threshold, trailing_zero_secret, end)
    assert recovered_secret == trailing_zero_secret


def test_2_of_3_sharing():
    num_players = 3
    reconstruction_threshold = 2

    recovered_secret = share_and_recover(num_players, reconstruction_threshold, alt_secret, reconstruction_threshold)
    assert recovered_secret == alt_secret


def test_4_of_7_sharing():
    num_players = 7
    reconstruction_threshold = 4

    recovered_secret = share_and_recover(num_players, reconstruction_threshold, alt_secret, reconstruction_threshold)
    assert recovered_secret == alt_secret


def test_5_of_9_sharing():
    num_players = 9
    reconstruction_threshold = 5

    recovered_secret = share_and_recover(num_players, reconstruction_threshold, alt_secret, reconstruction_threshold)
    assert recovered_secret == alt_secret


def test_2_of_2_sharing():
    num_players = 2
    reconstruction_threshold = 2

    recovered_secret = share_and_recover(num_players, reconstruction_threshold, alt_secret, reconstruction_threshold)
    assert recovered_secret == alt_secret


def test_bad_configuration_threshold():
    num_players = 2
    reconstruction_threshold = 5
    sharing_prime = primes.get_prime_by_batch([num_players, secret])

    with pytest.raises(custom_exceptions.FatalConfigurationError):
        sss.share_secret(num_players, reconstruction_threshold, secret, sharing_prime)


def test_bad_configuration_prime_small_secret():
    num_players = 5
    reconstruction_threshold = 2
    sharing_prime = primes.get_prime_by_batch([num_players])  # prime = 7
    bad_secret = random.convert_bytestring_to_int('x\xFF\xFF')

    with pytest.raises(custom_exceptions.FatalConfigurationError):
        sss.share_secret(num_players, reconstruction_threshold, bad_secret, sharing_prime)


def test_bad_configuration_prime_small_num_players():
    bad_num_players = 40
    reconstruction_threshold = 2
    secret = 10
    sharing_prime = primes.get_prime_by_batch([secret])  # prime = 31

    with pytest.raises(custom_exceptions.FatalConfigurationError):
        sss.share_secret(bad_num_players, reconstruction_threshold, secret, sharing_prime)


def test_bad_configuration_prime_none():
    num_players = 2
    reconstruction_threshold = 5
    sharing_prime = None

    with pytest.raises(custom_exceptions.FatalConfigurationError):
        sss.share_secret(num_players, reconstruction_threshold, secret, sharing_prime)
