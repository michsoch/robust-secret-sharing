from robustsecretsharing import rss
from robustsecretsharing.tests import test_authenticated_rss

secret = 'x\x02e\x9c\x9e\x16\xe9\xea\x15+\xbf]\xebx;o\xef\xc9X1c\xaepj\xebj\x12\xe3r\xcd\xeaM'  # An example key
alt_secret = 'c4bbcb1fbec99d65bf59d85c8cb62ee2db963f0fe106f483d9afa73bd4e39a8a'


def share_and_recover(num_players, reconstruction_threshold, secret, end):
    max_secret_length = len(secret)
    players = test_authenticated_rss.get_ids(num_players)
    robust_shares = rss.share_authenticated_secret(players, reconstruction_threshold, max_secret_length, secret)

    shares = {player: share for (player, share) in robust_shares.items()[:end]}
    return rss.reconstruct_unauthenticated_secret(num_players, max_secret_length, shares)


def corrupt_and_recover(robust_shares, num_players, end, num_corrupt):
    max_secret_length = len(secret)

    shares_subset = {player: share for (player, share) in robust_shares.items()[:end]}
    corrupters = {player: rss._deserialize_robust_share(share) for player, share in shares_subset.items()[:num_corrupt]}

    # corrupt share data
    for player, share_dict in corrupters.items():
        share_dict["share"] /= 4

    shares = test_authenticated_rss.combine_testing_dictionaries(shares_subset, test_authenticated_rss.jsonify_dict(corrupters))
    return rss.reconstruct_unauthenticated_secret(num_players, max_secret_length, shares)


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


def test_max_shares_some_bad():
    num_players = 9
    reconstruction_threshold = 5
    num_bad = 2

    max_secret_length = len(secret)
    players = test_authenticated_rss.get_ids(num_players)
    robust_shares = rss.share_authenticated_secret(players, reconstruction_threshold, max_secret_length, secret)

    result = corrupt_and_recover(robust_shares, num_players, num_players, num_bad)
    assert result is None or result != secret


def test_min_shares_some_bad():
    num_players = 9
    reconstruction_threshold = 5
    num_bad = 2

    max_secret_length = len(secret)
    players = test_authenticated_rss.get_ids(num_players)
    robust_shares = rss.share_authenticated_secret(players, reconstruction_threshold, max_secret_length, secret)

    result = corrupt_and_recover(robust_shares, num_players, num_players, num_bad)
    assert result is None or result != secret
