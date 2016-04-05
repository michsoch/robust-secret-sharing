from robustsecretsharing.schemes import sss
import pytest

secret = 'x\x02e\x9c\x9e\x16\xe9\xea\x15+\xbf]\xebx;o\xef\xc9X1c\xaepj\xebj\x12\xe3r\xcd\xeaM'  # An example key
alt_secret = 'c4bbcb1fbec99d65bf59d85c8cb62ee2db963f0fe106f483d9afa73bd4e39a8a'


def share_and_recover(num_players, reconstruction_threshold, secret, end):
    max_secret_length = len(secret)
    shares = sss.share_secret(num_players, reconstruction_threshold, max_secret_length, secret)
    return sss.reconstruct_secret(num_players, max_secret_length, shares[:end])


def share_break_and_recover(num_players, reconstruction_threshold, secret, end, num_broken):
    max_secret_length = len(secret)
    shares = sss.share_secret(num_players, reconstruction_threshold, max_secret_length, secret)

    broken_shares = []
    for share in shares[:num_broken]:
        if share.startswith('1'):
            broken_shares.append('2' + share[1:])
        else:
            broken_shares.append('1' + share[1:])
    return sss.reconstruct_secret(num_players, max_secret_length, broken_shares + shares[:num_broken])


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


def test_secret_leading_zeroes():
    num_players = 5
    reconstruction_threshold = 2
    end = 2

    # Create secret
    leading_zero_secret = '\x00\x00e\x9c\x9e\x16\xe9\xea\x15+\xbf]\xebx;o\xef\xc9X1c\xaepj\xebj\x12\xe3r\xcd\xeaM'

    recovered_secret = share_and_recover(num_players, reconstruction_threshold, leading_zero_secret, end)
    assert recovered_secret == leading_zero_secret


def test_many_players():
    num_players = 40
    reconstruction_threshold = 2

    secret = '\x0A'

    recovered_secret = share_and_recover(num_players, reconstruction_threshold, secret, reconstruction_threshold)
    assert recovered_secret == secret


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


def test_int_share_recover():
    num_players = 5
    reconstruction_threshold = 3

    secret = 123456789
    max_secret_length = len(str(secret))
    shares = sss._share_secret_int(num_players, reconstruction_threshold, max_secret_length, secret)
    recovered_secret = sss._reconstruct_secret_int(num_players, max_secret_length, shares[:reconstruction_threshold])
    assert recovered_secret == secret


def test_int_players():
    num_players = 40
    reconstruction_threshold = 2

    secret = 10
    max_secret_length = len(str(secret))
    shares = sss._share_secret_int(num_players, reconstruction_threshold, max_secret_length, secret)
    recovered_secret = sss._reconstruct_secret_int(num_players, max_secret_length, shares[:reconstruction_threshold])
    assert recovered_secret == secret


def test_max_shares_some_bad():
    num_players = 9
    reconstruction_threshold = 5
    num_bad = 2

    with pytest.raises(ValueError):
        share_break_and_recover(num_players, reconstruction_threshold, secret, num_players, num_bad)


def test_min_shares_some_bad():
    num_players = 9
    reconstruction_threshold = 5
    num_bad = 2

    with pytest.raises(ValueError):
        share_break_and_recover(num_players, reconstruction_threshold, secret, reconstruction_threshold, num_bad)


def test_bad_configuration_threshold():
    num_players = 2
    reconstruction_threshold = 5

    max_secret_length = len(secret)

    with pytest.raises(ValueError):
        sss.share_secret(num_players, reconstruction_threshold, max_secret_length, secret)


def test_bad_configuration_prime_small_secret():
    num_players = 5
    reconstruction_threshold = 2

    bad_secret = '\xFF\xFF'
    max_secret_length = len(bad_secret) - 1

    with pytest.raises(ValueError):
        sss.share_secret(num_players, reconstruction_threshold, max_secret_length, bad_secret)


def test_bad_configuration_prime_none():
    num_players = 40
    reconstruction_threshold = 30

    with pytest.raises(ValueError):
        sss.share_secret(num_players, reconstruction_threshold, 5000, secret)
