from robustsecretsharing import rss
import pytest

secret = 'x\x02e\x9c\x9e\x16\xe9\xea\x15+\xbf]\xebx;o\xef\xc9X1c\xaepj\xebj\x12\xe3r\xcd\xeaM'  # An example key
alt_secret = 'c4bbcb1fbec99d65bf59d85c8cb62ee2db963f0fe106f483d9afa73bd4e39a8a'

# TODO: update these to also check authentication
###########################################################################################################


def share_and_recover(num_players, reconstruction_threshold, secret, end):
    max_secret_length = len(secret)
    shares = rss.share_secret(num_players, reconstruction_threshold, max_secret_length, secret)
    return rss.reconstruct_secret(num_players, reconstruction_threshold, max_secret_length, shares[:end])


def test_robust_min_shares():
    num_players = 5
    reconstruction_threshold = 2
    end = 2

    recovered_secret = share_and_recover(num_players, reconstruction_threshold, secret, end)
    assert recovered_secret == secret


def test_robust_max_shares():
    num_players = 5
    reconstruction_threshold = 2
    end = num_players

    recovered_secret = share_and_recover(num_players, reconstruction_threshold, secret, end)
    assert recovered_secret == secret


def test_robust_secret_with_leading_zeroes():
    num_players = 5
    reconstruction_threshold = 2
    end = 2

    # Create secret
    trailing_zero_secret = '\x00\x00e\x9c\x9e\x16\xe9\xea\x15+\xbf]\xebx;o\xef\xc9X1c\xaepj\xebj\x12\xe3r\xcd\xeaM'

    recovered_secret = share_and_recover(num_players, reconstruction_threshold, trailing_zero_secret, end)
    assert recovered_secret == trailing_zero_secret


def test_robust_many_players():
    num_players = 40
    reconstruction_threshold = 2

    secret = '\x0A'

    recovered_secret = share_and_recover(num_players, reconstruction_threshold, secret, reconstruction_threshold)
    assert recovered_secret == secret


def test_robust_2_of_3_sharing():
    num_players = 3
    reconstruction_threshold = 2

    recovered_secret = share_and_recover(num_players, reconstruction_threshold, alt_secret, reconstruction_threshold)
    assert recovered_secret == alt_secret


def test_robust_4_of_7_sharing():
    num_players = 7
    reconstruction_threshold = 4

    recovered_secret = share_and_recover(num_players, reconstruction_threshold, alt_secret, reconstruction_threshold)
    assert recovered_secret == alt_secret


def test_robust_5_of_9_sharing():
    num_players = 9
    reconstruction_threshold = 5

    recovered_secret = share_and_recover(num_players, reconstruction_threshold, alt_secret, reconstruction_threshold)
    assert recovered_secret == alt_secret


def test_robust_2_of_2_sharing():
    num_players = 2
    reconstruction_threshold = 2

    recovered_secret = share_and_recover(num_players, reconstruction_threshold, alt_secret, reconstruction_threshold)
    assert recovered_secret == alt_secret


def test_robust_bad_configuration_threshold():
    num_players = 2
    reconstruction_threshold = 5

    max_secret_length = len(secret)

    with pytest.raises(ValueError):
        rss.share_secret(num_players, reconstruction_threshold, max_secret_length, secret)


def test_robust_bad_configuration_prime_small_secret():
    num_players = 5
    reconstruction_threshold = 2

    bad_secret = '\xFF\xFF'
    max_secret_length = len(bad_secret) - 1

    with pytest.raises(ValueError):
        rss.share_secret(num_players, reconstruction_threshold, max_secret_length, bad_secret)


def test_robust_bad_configuration_prime_none():
    num_players = 2
    reconstruction_threshold = 5

    max_secret_length = len(secret)

    with pytest.raises(ValueError):
        rss.share_secret(num_players, reconstruction_threshold, max_secret_length, secret)

###########################################################################################################


#####################  >= k honest, <= k -1 dishonest ##################################

#####################  >= k honest, > k -1 dishonest ##################################

#####################  <= k honest, <= k -1 dishonest ##################################

#####################  <= k honest, > k -1 dishonest ##################################
