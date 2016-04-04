from robustsecretsharing import rss
from robustsecretsharing.schemes import authentication
from robustsecretsharing.crypto_tools import random
import pytest

secret = 'x\x02e\x9c\x9e\x16\xe9\xea\x15+\xbf]\xebx;o\xef\xc9X1c\xaepj\xebj\x12\xe3r\xcd\xeaM'  # An example key
alt_secret = 'c4bbcb1fbec99d65bf59d85c8cb62ee2db963f0fe106f483d9afa73bd4e39a8a'
PRIME = 2**13 - 1  # arbitary prime for generating random ids


def get_ids(num_players):
    '''
    Args:
        num_players, the number of players to generate ids for
    Returns:
        a list of random, unique ids
    '''
    ids = []
    for r in random.get_distinct_positive_random_ints_in_field(num_players, PRIME):
        ids.append(str(r))
    return ids


def get_shares_subset(players, reconstruction_threshold, secret, end):
    '''
    Args:
        players, a list of random, unique ids
        reconstruction_threshold, the threshold used for sharing
        secret, the value to be secret shared
        end, marks the number of shares to return
    Returns:
        a dictionary of length end that maps ids to json_string shares
    '''
    max_secret_length = len(secret)
    shares_map = rss.share_secret(players, reconstruction_threshold, max_secret_length, secret)
    return {player: shares_map[player] for player in shares_map.keys()[:end]}


def jsonify_dict(shares):
    '''
    Args:
        shares, a dictionary of players to unjsonified shares
    Returns:
        a dictionary of players to jsonified shares
    '''
    json_shares = {}
    for player in shares:
        json_shares[player] = rss._serialize_robust_share(shares[player]["share"], shares[player]["keys"], shares[player]["vectors"])
    return json_shares


def combine_testing_dictionaries(dictionary, subset):
    '''
    Args:
        dictionary, a base dictionary of shares
        subset, a partial dictionary of shares with keys that are subsets of those in dictionary
    Returns:
        a new full dictionary that has been corrupted according to the input
    '''
    shares = {}
    for player in dictionary:
        if player in subset:
            shares[player] = subset[player]
        else:
            shares[player] = dictionary[player]
    return shares


def share_and_recover(players, reconstruction_threshold, secret, end):
    '''
    Args:
        players, a list of unique player ids
        reconstruction_threshold, the threshold needed for secret reconstruction
        secret, the secret to be shared
        end, the number of shares to use in reconstruction
    Returns:
        the result of robust reconstruction
    '''
    max_secret_length = len(secret)
    shares_subset = get_shares_subset(players, reconstruction_threshold, secret, end)
    return rss.reconstruct_secret(len(players), reconstruction_threshold, max_secret_length, shares_subset)


def corrupt_share_and_recover(num_players, reconstruction_threshold, max_secret_length, shares_subset, num_corrupt):
    '''
    Args:
        num_players, the number of players that were shared across
        reconstruction_threshold, the threshold for reconstruction
        max_secret_length, the maximum length of the secret that was shared
        shares_subset, a dictionary of a subset of players to json robust shares
        num_corrupt, the number of players that will corrupt their shares
    Returns:
        the result of robust reconstruction
    '''
    corrupters = {player: rss._deserialize_robust_share(share) for player, share in shares_subset.items()[:num_corrupt]}

    # corrupt share data
    for player, share_dict in corrupters.items():
        share_dict["share"] /= 4

    shares = combine_testing_dictionaries(shares_subset, jsonify_dict(corrupters))
    return rss.reconstruct_secret(num_players, reconstruction_threshold, max_secret_length, shares)


def corrupt_vectors_and_recover(num_players, reconstruction_threshold, max_secret_length, shares_subset, num_corrupt, degree_of_corruption):
    '''
    Args:
        num_players, the number of players that were shared across
        reconstruction_threshold, the threshold for reconstruction
        max_secret_length, the maximum length of the secret that was shared
        shares_subset, a dictionary of a subset of players to json robust shares
        num_corrupt, the number of players that will corrupt their vectors
        degree_of_corruption, how many of their own vectors each corrupting player will corrupt
    Returns:
        the result of robust reconstruction
    '''
    corrupters = {player: rss._deserialize_robust_share(share) for player, share in shares_subset.items()[:num_corrupt]}
    verifiers = [player for player in shares_subset.keys()[:degree_of_corruption]]

    # corrupt vector data
    for player, share_dict in corrupters.items():
        for verifier in verifiers:
            share_dict["vectors"][verifier][0] /= 4
            share_dict["vectors"][verifier][1] /= 4

    shares = combine_testing_dictionaries(shares_subset, jsonify_dict(corrupters))
    return rss.reconstruct_secret(num_players, reconstruction_threshold, max_secret_length, shares)


def corrupt_keys_and_recover(num_players, reconstruction_threshold, max_secret_length, shares_subset, num_corrupt, degree_of_corruption):
    '''
    Args:
        num_players, the number of players that were shared across
        reconstruction_threshold, the threshold for reconstruction
        max_secret_length, the maximum length of the secret that was shared
        shares_subset, a dictionary of a subset of players to json robust shares
        num_corrupt, the number of players that will corrupt auth keys
        degree_of_corruption, how many of the keys each corrupting player will corrupt
    Returns:
        the result of robust reconstruction
    '''
    corrupters = {player: rss._deserialize_robust_share(share) for player, share in shares_subset.items()[:num_corrupt]}
    verifiers = [player for player in shares_subset.keys()[:degree_of_corruption]]

    # corrupt key data
    for player, share_dict in corrupters.items():
        for verifier in verifiers:
            share_dict["keys"][verifier] /= 4

    shares = combine_testing_dictionaries(shares_subset, jsonify_dict(corrupters))
    return rss.reconstruct_secret(num_players, reconstruction_threshold, max_secret_length, shares)


def collude_and_recover(num_players, reconstruction_threshold, max_secret_length, shares_subset, num_collude):
    '''
    Args:
        num_players, the number of players that were shared across
        reconstruction_threshold, the threshold for reconstruction
        max_secret_length, the maximum length of the secret that was shared
        shares_subset, a dictionary of a subset of players to json robust shares
        num_corrupt, the number of players that will collude
    Returns:
        the result of robust reconstruction
    '''
    max_secret_length = len(secret)

    colluders = {player: rss._deserialize_robust_share(share) for player, share in shares_subset.items()[:num_collude]}

    for player, player_dict in colluders.items():
        player_dict["share"] /= 2
        for verifier, verifier_dict in colluders.items():
            new_key, new_vector = authentication.generate_check_vector(player_dict["share"], max_secret_length)
            verifier_dict["keys"][player] = new_key
            player_dict["vectors"][verifier] = new_vector

    # assert that these players do in fact collude
    for verifier, verifier_dict in colluders.items():
        for player, player_dict in colluders.items():
            assert authentication.validate(verifier_dict["keys"][player], player_dict["vectors"][verifier],
                                           player_dict["share"], max_secret_length) is True

    shares = combine_testing_dictionaries(shares_subset, jsonify_dict(colluders))
    return rss.reconstruct_secret(num_players, reconstruction_threshold, max_secret_length, shares)


def verify_results(recovered_secret, original_secret, valid_players, honest_players, invalid_players, dishonest_players):
    '''
    Args:
        recovered_secret, the secret recovered by robust reconstruction
        original_secret, the original secret for comparison
        valid_players, a subset of players who had shares used in reconstruction
        honest_players, a subset of players constructed to be honest
        invalid_players, a subset of dishonest players
        dishonest_players, a subset of players constructed to be dishonest
    Returns:
        True if the results of reconstruction match the constructed test parameters and False otherwise
    '''
    return recovered_secret == original_secret and \
        sorted(valid_players) == sorted(honest_players) and \
        sorted(invalid_players) == sorted(dishonest_players)


def test_robust_min_shares():
    num_players = 5
    reconstruction_threshold = 3
    end = reconstruction_threshold

    players = get_ids(num_players)

    recovered_secret, valid_players, invalid_players = \
        share_and_recover(players, reconstruction_threshold, secret, end)
    verify_results(secret, recovered_secret, valid_players, players, invalid_players, [])


def test_robust_max_shares():
    num_players = 5
    reconstruction_threshold = 3
    end = num_players

    players = get_ids(num_players)

    recovered_secret, valid_players, invalid_players = \
        share_and_recover(players, reconstruction_threshold, secret, end)
    verify_results(secret, recovered_secret, valid_players, players, invalid_players, [])


def test_robust_secret_with_leading_zeroes():
    num_players = 5
    reconstruction_threshold = 3
    end = reconstruction_threshold

    players = get_ids(num_players)

    # Create secret
    trailing_zero_secret = '\x00\x00e\x9c\x9e\x16\xe9\xea\x15+\xbf]\xebx;o\xef\xc9X1c\xaepj\xebj\x12\xe3r\xcd\xeaM'

    recovered_secret, valid_players, invalid_players = \
        share_and_recover(players, reconstruction_threshold, trailing_zero_secret, end)
    verify_results(trailing_zero_secret, recovered_secret, valid_players, players, invalid_players, [])


def test_robust_many_players():
    num_players = 40
    reconstruction_threshold = 30

    players = get_ids(num_players)

    secret = '\x0A'

    recovered_secret, valid_players, invalid_players = \
        share_and_recover(players, reconstruction_threshold, secret, reconstruction_threshold)
    verify_results(secret, recovered_secret, valid_players, players, invalid_players, [])


def test_robust_2_of_3_sharing():
    num_players = 3
    reconstruction_threshold = 2

    players = get_ids(num_players)

    recovered_secret, valid_players, invalid_players = \
        share_and_recover(players, reconstruction_threshold, alt_secret, reconstruction_threshold)
    verify_results(secret, recovered_secret, valid_players, players, invalid_players, [])


def test_robust_4_of_7_sharing():
    num_players = 7
    reconstruction_threshold = 4

    players = get_ids(num_players)

    recovered_secret, valid_players, invalid_players = \
        share_and_recover(players, reconstruction_threshold, alt_secret, reconstruction_threshold)
    verify_results(secret, recovered_secret, valid_players, players, invalid_players, [])


def test_robust_5_of_9_sharing():
    num_players = 9
    reconstruction_threshold = 5

    players = get_ids(num_players)

    recovered_secret, valid_players, invalid_players = \
        share_and_recover(players, reconstruction_threshold, alt_secret, reconstruction_threshold)
    verify_results(alt_secret, recovered_secret, valid_players, players, invalid_players, [])


def test_robust_2_of_2_sharing():
    num_players = 2
    reconstruction_threshold = 2

    players = get_ids(num_players)

    recovered_secret, valid_players, invalid_players = \
        share_and_recover(players, reconstruction_threshold, alt_secret, reconstruction_threshold)
    verify_results(alt_secret, recovered_secret, valid_players, players, invalid_players, [])


def test_robust_bad_configuration_threshold():
    num_players = 2
    reconstruction_threshold = 5

    players = get_ids(num_players)

    max_secret_length = len(secret)

    with pytest.raises(ValueError):
        rss.share_secret(players, reconstruction_threshold, max_secret_length, secret)


def test_robust_bad_configuration_prime_small_secret():
    num_players = 5
    reconstruction_threshold = 2

    players = get_ids(num_players)

    bad_secret = '\xFF\xFF'
    max_secret_length = len(bad_secret) - 1

    with pytest.raises(ValueError):
        rss.share_secret(players, reconstruction_threshold, max_secret_length, bad_secret)


def test_robust_bad_configuration_prime_none():
    num_players = 40
    reconstruction_threshold = 30

    players = get_ids(num_players)

    with pytest.raises(ValueError):
        rss.share_secret(players, reconstruction_threshold, 5000, secret)


def test_honest_less_dishonest_greater_corrupt_share_failure():
    num_players = 8
    reconstruction_threshold = 4
    dishonest = 6
    end = num_players

    players = get_ids(num_players)
    shares_subset = get_shares_subset(players, reconstruction_threshold, secret, end)

    with pytest.raises(rss.FatalReconstructionFailure):
        corrupt_share_and_recover(num_players, reconstruction_threshold, len(secret), shares_subset, dishonest)


def test_honest_less_dishonest_greater_corrupt_some_vectors_failure():
    '''
    For some number of corrupt players (num_corrupt), corrupt a number of vectors held by those players (degree_of_corruption).
    This will cause all corrupt players to fail authentication by the players who hold keys associated with those corrupted vectors.

    Since there are greater than reconstruction_threshold - 1 such dishonest players
    and fewer than reconstruction honest players in this case, failure occurs.
    '''
    num_players = 20
    reconstruction_threshold = 10
    num_corrupt = reconstruction_threshold
    end = 15
    degree_of_corruption = num_players / 2

    players = get_ids(num_players)
    shares_subset = get_shares_subset(players, reconstruction_threshold, secret, end)

    with pytest.raises(rss.FatalReconstructionFailure):
        corrupt_vectors_and_recover(num_players, reconstruction_threshold, len(secret), shares_subset, num_corrupt, degree_of_corruption)


def test_honest_less_dishonest_greater_corrupt_some_keys_failure():
    '''
    For some number of corrupt players (num_corrupt), corrupt a number of keys held by those players (degree_of_corruption).
    This will cause all corrupt players to claim that the players associated with those keys lied about their share.

    Since there are greater than reconstruction_threshold - 1 such dishonest players
    and fewer than reconstruction honest players in this case, failure occurs.
    '''
    num_players = 20
    reconstruction_threshold = 10
    num_corrupt = reconstruction_threshold
    end = 15
    degree_of_corruption = num_players / 2

    players = get_ids(num_players)
    shares_subset = get_shares_subset(players, reconstruction_threshold, secret, end)

    with pytest.raises(rss.FatalReconstructionFailure):
        corrupt_keys_and_recover(num_players, reconstruction_threshold, len(secret), shares_subset, num_corrupt, degree_of_corruption)


def test_honest_less_dishonest_equal_corrupt_share_failure():
    num_players = 20
    reconstruction_threshold = 10
    dishonest = reconstruction_threshold - 1
    end = 18  # only 9 left honest after 9 are corrupted

    players = get_ids(num_players)
    shares_subset = get_shares_subset(players, reconstruction_threshold, secret, end)

    with pytest.raises(rss.FatalReconstructionFailure):
        corrupt_share_and_recover(num_players, reconstruction_threshold, len(secret), shares_subset, dishonest)


def test_honest_less_dishonest_equal_corrupt_some_vectors_failure():
    '''
    For some number of corrupt players (num_corrupt), corrupt a number of vectors held by those players (degree_of_corruption).
    This will cause all corrupt players to fail authentication by the players who hold keys associated with those corrupted vectors.

    Since there are fewer than reconstruction honest players in this case, failure occurs.
    '''
    num_players = 20
    reconstruction_threshold = 7
    num_corrupt = reconstruction_threshold - 1
    end = 10   # 6 are dishonest so only 4 are left honest
    degree_of_corruption = num_players / 2

    players = get_ids(num_players)
    shares_subset = get_shares_subset(players, reconstruction_threshold, secret, end)

    with pytest.raises(rss.FatalReconstructionFailure):
        corrupt_vectors_and_recover(num_players, reconstruction_threshold, len(secret), shares_subset, num_corrupt, degree_of_corruption)


def test_honest_less_dishonest_less_corrupt_some_keys_failure():
    '''
    For some number of corrupt players (num_corrupt), corrupt a number of keys held by those players (degree_of_corruption).
    This will cause all corrupt players to claim that the players associated with those keys lied about their share.

    Since there are fewer than reconstruction honest players in this case, failure occurs.
    '''
    num_players = 20
    reconstruction_threshold = 7
    num_corrupt = 4
    end = 10
    degree_of_corruption = num_players / 2

    players = get_ids(num_players)
    shares_subset = get_shares_subset(players, reconstruction_threshold, secret, end)

    with pytest.raises(rss.FatalReconstructionFailure):
        corrupt_keys_and_recover(num_players, reconstruction_threshold, len(secret), shares_subset, num_corrupt, degree_of_corruption)


def test_all_honest():
    num_players = 5
    reconstruction_threshold = 2
    end = num_players

    players = get_ids(num_players)

    recovered_secret, authorized_players, invalid_players = \
        share_and_recover(players, reconstruction_threshold, secret, end)
    assert verify_results(recovered_secret, secret, authorized_players, players, invalid_players, []) is True


def test_honest_greater_dishonest_equal_corrupt_share():
    num_players = 20
    reconstruction_threshold = 7
    dishonest = reconstruction_threshold - 1
    end = num_players

    players = get_ids(num_players)
    shares_subset = get_shares_subset(players, reconstruction_threshold, secret, end)

    recovered_secret, authorized_players, invalid_players = \
        corrupt_share_and_recover(num_players, reconstruction_threshold, len(secret), shares_subset, dishonest)
    assert verify_results(recovered_secret, secret,
                          authorized_players, shares_subset.keys()[dishonest:],
                          invalid_players, []) is True


def test_honest_greater_dishonest_less_corrupt_share():
    num_players = 20
    reconstruction_threshold = 7
    dishonest = reconstruction_threshold - reconstruction_threshold / 2
    end = num_players

    players = get_ids(num_players)
    shares_subset = get_shares_subset(players, reconstruction_threshold, secret, end)

    recovered_secret, authorized_players, invalid_players = \
        corrupt_share_and_recover(num_players, reconstruction_threshold, len(secret), shares_subset, dishonest)
    assert verify_results(recovered_secret, secret,
                          authorized_players, shares_subset.keys()[dishonest:],
                          invalid_players, []) is True


def test_greater_honest_less_dishonest_corrupt_half_vectors():
    '''
    For some number of corrupt players (num_corrupt), corrupt a number of vectors held by those players (degree_of_corruption).
    This will cause all corrupt players to fail authentication by the players who hold keys associated with those corrupted vectors.

    In this case, 1 corrupt player attempts to cause problems by forcing honest players to disagree about the shares they authenticate.
    However, because there are fewer than reconstruction - 1 dishonest players and there are reconstruction_threshold honest players,
    the original secret can be recovered.
    '''
    reconstruction_threshold = 7
    num_corrupt = 1
    num_players = reconstruction_threshold + num_corrupt
    end = num_players
    degree_of_corruption = num_players / 2

    players = get_ids(num_players)
    shares_subset = get_shares_subset(players, reconstruction_threshold, secret, end)

    recovered_secret, authorized_players, invalid_players = \
        corrupt_vectors_and_recover(num_players, reconstruction_threshold, len(secret), shares_subset, num_corrupt, degree_of_corruption)
    assert verify_results(recovered_secret, secret,
                          authorized_players, shares_subset.keys(),
                          invalid_players, []) is True


def test_greater_honest_equal_dishonest_corrupt_all_vectors():
    '''
    For some number of corrupt players (num_corrupt), corrupt a number of vectors held by those players (degree_of_corruption).
    This will cause all corrupt players to fail authentication by the players who hold keys associated with those corrupted vectors.

    Bceause there are only reconstruction - 1 dishonest players and there are reconstruction_threshold honest players,
    the original secret can be recovered.
    '''
    reconstruction_threshold = 7
    num_corrupt = reconstruction_threshold - 1
    num_players = reconstruction_threshold + num_corrupt
    end = num_players
    degree_of_corruption = num_players

    players = get_ids(num_players)
    shares_subset = get_shares_subset(players, reconstruction_threshold, secret, end)

    recovered_secret, authorized_players, invalid_players = \
        corrupt_vectors_and_recover(num_players, reconstruction_threshold, len(secret), shares_subset, num_corrupt, degree_of_corruption)
    assert verify_results(recovered_secret, secret,
                          authorized_players, shares_subset.keys()[num_corrupt:],
                          invalid_players, []) is True


def test_greater_honest_equal_dishonest_corrupt_many_vectors():
    '''
    For some number of corrupt players (num_corrupt), corrupt a number of vectors held by those players (degree_of_corruption).
    This will cause all corrupt players to fail authentication by the players who hold keys associated with those corrupted vectors.

    Bceause there are only reconstruction - 1 dishonest players and there are reconstruction_threshold honest players,
    the original secret can be recovered.
    '''
    reconstruction_threshold = 7
    num_corrupt = reconstruction_threshold - 1
    num_players = reconstruction_threshold + num_corrupt
    end = num_players
    degree_of_corruption = reconstruction_threshold

    players = get_ids(num_players)
    shares_subset = get_shares_subset(players, reconstruction_threshold, secret, end)

    recovered_secret, authorized_players, invalid_players = \
        corrupt_vectors_and_recover(num_players, reconstruction_threshold, len(secret), shares_subset, num_corrupt, degree_of_corruption)
    assert verify_results(recovered_secret, secret,
                          authorized_players, shares_subset.keys(),
                          invalid_players, []) is True


def test_greater_honest_equal_dishonest_corrupt_few_vectors():
    '''
    For some number of corrupt players (num_corrupt), corrupt a number of vectors held by those players (degree_of_corruption).
    This will cause all corrupt players to fail authentication by the players who hold keys associated with those corrupted vectors.

    Bceause there are only reconstruction - 1 dishonest players and there are reconstruction_threshold honest players,
    the original secret can be recovered.
    '''
    reconstruction_threshold = 7
    num_corrupt = reconstruction_threshold - 1
    num_players = reconstruction_threshold + num_corrupt
    end = num_players
    degree_of_corruption = reconstruction_threshold + 1

    players = get_ids(num_players)
    shares_subset = get_shares_subset(players, reconstruction_threshold, secret, end)

    recovered_secret, authorized_players, invalid_players = \
        corrupt_vectors_and_recover(num_players, reconstruction_threshold, len(secret), shares_subset, num_corrupt, degree_of_corruption)
    assert verify_results(recovered_secret, secret,
                          authorized_players, shares_subset.keys(),
                          invalid_players, []) is True


def test_greater_honest_equal_dishonest_corrupt_no_vectors():
    reconstruction_threshold = 7
    num_corrupt = reconstruction_threshold - 1
    num_players = reconstruction_threshold + num_corrupt
    end = num_players
    degree_of_corruption = 0  # should be equivalent to no corrruption

    players = get_ids(num_players)
    shares_subset = get_shares_subset(players, reconstruction_threshold, secret, end)

    recovered_secret, authorized_players, invalid_players = \
        corrupt_vectors_and_recover(num_players, reconstruction_threshold, len(secret), shares_subset, num_corrupt, degree_of_corruption)
    assert verify_results(recovered_secret, secret,
                          authorized_players, shares_subset.keys(),
                          invalid_players, []) is True


def test_greater_honest_equal_dishonest_corrupt_all_keys():
    '''
    For some number of corrupt players (num_corrupt), corrupt a number of keys held by those players (degree_of_corruption).
    This will cause all corrupt players to claim that the players associated with those keys lied about their share.

    Bceause there are only reconstruction - 1 dishonest players and there are reconstruction_threshold honest players,
    the original secret can be recovered.
    '''
    reconstruction_threshold = 7
    num_corrupt = reconstruction_threshold - 1
    num_players = reconstruction_threshold + num_corrupt
    end = num_players
    degree_of_corruption = num_players

    players = get_ids(num_players)
    shares_subset = get_shares_subset(players, reconstruction_threshold, secret, end)

    recovered_secret, authorized_players, invalid_players = \
        corrupt_keys_and_recover(num_players, reconstruction_threshold, len(secret), shares_subset, num_corrupt, degree_of_corruption)
    assert verify_results(recovered_secret, secret,
                          authorized_players, shares_subset.keys(),
                          invalid_players, []) is True


def test_greater_honest_equal_dishonest_corrupt_many_keys():
    '''
    For some number of corrupt players (num_corrupt), corrupt a number of keys held by those players (degree_of_corruption).
    This will cause all corrupt players to claim that the players associated with those keys lied about their share.

    Bceause there are only reconstruction - 1 dishonest players and there are reconstruction_threshold honest players,
    the original secret can be recovered.
    '''
    reconstruction_threshold = 7
    num_corrupt = reconstruction_threshold - 1
    num_players = reconstruction_threshold + num_corrupt
    end = num_players
    degree_of_corruption = num_players - reconstruction_threshold + 1

    players = get_ids(num_players)
    shares_subset = get_shares_subset(players, reconstruction_threshold, secret, end)

    recovered_secret, authorized_players, invalid_players = \
        corrupt_keys_and_recover(num_players, reconstruction_threshold, len(secret), shares_subset, num_corrupt, degree_of_corruption)
    assert verify_results(recovered_secret, secret,
                          authorized_players, shares_subset.keys(),
                          invalid_players, []) is True


def test_greater_honest_equal_dishonest_corrupt_few_keys():
    '''
    For some number of corrupt players (num_corrupt), corrupt a number of keys held by those players (degree_of_corruption).
    This will cause all corrupt players to claim that the players associated with those keys lied about their share.

    Bceause there are only reconstruction - 1 dishonest players and there are reconstruction_threshold honest players,
    the original secret can be recovered.
    '''
    reconstruction_threshold = 7
    num_corrupt = reconstruction_threshold - 1
    num_players = reconstruction_threshold + num_corrupt
    end = num_players
    degree_of_corruption = reconstruction_threshold + 1

    players = get_ids(num_players)
    shares_subset = get_shares_subset(players, reconstruction_threshold, secret, end)

    recovered_secret, authorized_players, invalid_players = \
        corrupt_keys_and_recover(num_players, reconstruction_threshold, len(secret), shares_subset, num_corrupt, degree_of_corruption)
    assert verify_results(recovered_secret, secret,
                          authorized_players, shares_subset.keys(),
                          invalid_players, []) is True


def test_greater_honest_equal_dishonest_corrupt_no_keys():
    reconstruction_threshold = 7
    num_corrupt = reconstruction_threshold - 1
    num_players = reconstruction_threshold + num_corrupt
    end = num_players
    degree_of_corruption = 0  # should be equivalent to no corruption

    players = get_ids(num_players)
    shares_subset = get_shares_subset(players, reconstruction_threshold, secret, end)

    recovered_secret, authorized_players, invalid_players = \
        corrupt_keys_and_recover(num_players, reconstruction_threshold, len(secret), shares_subset, num_corrupt, degree_of_corruption)
    assert verify_results(recovered_secret, secret,
                          authorized_players, shares_subset.keys(),
                          invalid_players, []) is True


def test_collusion():
    reconstruction_threshold = 7
    num_collude = reconstruction_threshold - 1
    num_players = reconstruction_threshold + num_collude
    end = num_players

    players = get_ids(num_players)
    shares_subset = get_shares_subset(players, reconstruction_threshold, secret, end)

    recovered_secret, authorized_players, invalid_players = \
        collude_and_recover(num_players, reconstruction_threshold, len(secret), shares_subset, num_collude)

    assert verify_results(recovered_secret, secret,
                          authorized_players, shares_subset.keys()[num_collude:],
                          invalid_players, []) is True


def test_json_bracket_parse_error():
    num_players = 8
    reconstruction_threshold = 4
    end = num_players
    num_broken = reconstruction_threshold - 1

    players = get_ids(num_players)
    shares_subset = get_shares_subset(players, reconstruction_threshold, secret, end)

    broken_shares = {}
    for player, share in shares_subset.items()[:num_broken]:
        broken_shares[player] = share[1:]  # remove opening JSON bracket

    shares = combine_testing_dictionaries(shares_subset, broken_shares)

    recovered_secret, authorized_players, invalid_players = \
        rss.reconstruct_secret(num_players, reconstruction_threshold, len(secret), shares)
    assert verify_results(recovered_secret, secret,
                          authorized_players, shares_subset.keys()[num_broken:],
                          invalid_players, shares_subset.keys()[:num_broken]) is True


def test_json_list_parse_error():
    num_players = 8
    reconstruction_threshold = 4
    end = num_players
    num_broken = reconstruction_threshold - 1

    players = get_ids(num_players)
    shares_subset = get_shares_subset(players, reconstruction_threshold, secret, end)

    broken_shares = {}
    for player, share in shares_subset.items()[:num_broken]:
        list_index = share.index("[")
        broken_shares[player] = share[:list_index] + share[list_index + 1:]

    shares = combine_testing_dictionaries(shares_subset, broken_shares)

    recovered_secret, authorized_players, invalid_players = \
        rss.reconstruct_secret(num_players, reconstruction_threshold, len(secret), shares)
    assert verify_results(recovered_secret, secret,
                          authorized_players, shares_subset.keys()[num_broken:],
                          invalid_players, shares_subset.keys()[:num_broken]) is True


def test_json_key_error():
    num_players = 8
    reconstruction_threshold = 4
    end = num_players
    num_broken = reconstruction_threshold - 1

    players = get_ids(num_players)
    shares_subset = get_shares_subset(players, reconstruction_threshold, secret, end)

    broken_shares = {}
    for player, share in shares_subset.items()[:num_broken]:
        keys_index = share.index("keys")
        share = share[:keys_index] + "pown" + share[keys_index + len("keys"):]
        broken_shares[player] = share

    shares = combine_testing_dictionaries(shares_subset, broken_shares)

    recovered_secret, authorized_players, invalid_players = \
        rss.reconstruct_secret(num_players, reconstruction_threshold, len(secret), shares)
    assert verify_results(recovered_secret, secret,
                          authorized_players, shares_subset.keys()[num_broken:],
                          invalid_players, shares_subset.keys()[:num_broken]) is True


def test_json_parse_make_share_string():
    num_players = 8
    reconstruction_threshold = 4
    end = num_players
    num_broken = reconstruction_threshold - 1

    players = get_ids(num_players)
    shares_subset = get_shares_subset(players, reconstruction_threshold, secret, end)
    unjsonify_shares = {player: rss._deserialize_robust_share(share) for player, share in shares_subset.items()[:num_broken]}

    for player, share in unjsonify_shares.items():
        share["share"] = str(share["share"])

    shares = combine_testing_dictionaries(shares_subset, jsonify_dict(unjsonify_shares))

    recovered_secret, authorized_players, invalid_players = \
        rss.reconstruct_secret(num_players, reconstruction_threshold, len(secret), shares)
    assert verify_results(recovered_secret, secret,
                          authorized_players, shares_subset.keys()[num_broken:],
                          invalid_players, shares_subset.keys()[:num_broken]) is True


def test_json_parse_remove_vectors():
    num_players = 8
    reconstruction_threshold = 4
    end = num_players
    num_broken = reconstruction_threshold - 1

    players = get_ids(num_players)
    shares_subset = get_shares_subset(players, reconstruction_threshold, secret, end)
    unjsonify_shares = {player: rss._deserialize_robust_share(share) for player, share in shares_subset.items()[:num_broken]}

    for player, share in unjsonify_shares.items():
        for vector in share["vectors"].keys()[:num_players / 2]:
            del share["vectors"][vector]

    shares = combine_testing_dictionaries(shares_subset, jsonify_dict(unjsonify_shares))

    recovered_secret, authorized_players, invalid_players = \
        rss.reconstruct_secret(num_players, reconstruction_threshold, len(secret), shares)
    assert verify_results(recovered_secret, secret,
                          authorized_players, shares_subset.keys()[num_broken:],
                          invalid_players, shares_subset.keys()[:num_broken]) is True


def test_json_parse_remove_keys():
    num_players = 8
    reconstruction_threshold = 4
    end = num_players
    num_broken = reconstruction_threshold - 1

    players = get_ids(num_players)
    shares_subset = get_shares_subset(players, reconstruction_threshold, secret, end)
    unjsonify_shares = {player: rss._deserialize_robust_share(share) for player, share in shares_subset.items()[:num_broken]}

    for player, share in unjsonify_shares.items():
        for key in share["keys"].keys()[:num_players / 2]:
            del share["keys"][key]

    shares = combine_testing_dictionaries(shares_subset, jsonify_dict(unjsonify_shares))

    recovered_secret, authorized_players, invalid_players = \
        rss.reconstruct_secret(num_players, reconstruction_threshold, len(secret), shares)
    assert verify_results(recovered_secret, secret,
                          authorized_players, shares_subset.keys()[num_broken:],
                          invalid_players, shares_subset.keys()[:num_broken]) is True


def test_json_parse_make_vector_dict_string():
    num_players = 8
    reconstruction_threshold = 4
    end = num_players
    num_broken = reconstruction_threshold - 1

    players = get_ids(num_players)
    shares_subset = get_shares_subset(players, reconstruction_threshold, secret, end)
    unjsonify_shares = {player: rss._deserialize_robust_share(share) for player, share in shares_subset.items()[:num_broken]}

    for player, share in unjsonify_shares.items():
        share["vectors"] = str(share["vectors"])

    shares = combine_testing_dictionaries(shares_subset, jsonify_dict(unjsonify_shares))

    recovered_secret, authorized_players, invalid_players = \
        rss.reconstruct_secret(num_players, reconstruction_threshold, len(secret), shares)
    assert verify_results(recovered_secret, secret,
                          authorized_players, shares_subset.keys()[num_broken:],
                          invalid_players, shares_subset.keys()[:num_broken]) is True


def test_json_parse_make_some_vectors_string():
    num_players = 8
    reconstruction_threshold = 4
    end = num_players
    num_broken = reconstruction_threshold - 1

    players = get_ids(num_players)
    shares_subset = get_shares_subset(players, reconstruction_threshold, secret, end)
    unjsonify_shares = {player: rss._deserialize_robust_share(share) for player, share in shares_subset.items()[:num_broken]}

    for player, share in unjsonify_shares.items():
        for victim in share["vectors"].keys()[:num_players / 2]:
            share["vectors"][victim] = str(share["vectors"][victim])

    shares = combine_testing_dictionaries(shares_subset, jsonify_dict(unjsonify_shares))

    recovered_secret, authorized_players, invalid_players = \
        rss.reconstruct_secret(num_players, reconstruction_threshold, len(secret), shares)
    assert verify_results(recovered_secret, secret,
                          authorized_players, shares_subset.keys()[num_broken:],
                          invalid_players, shares_subset.keys()[:num_broken]) is True


def test_json_parse_make_key_dict_string():
    num_players = 8
    reconstruction_threshold = 4
    end = num_players
    num_broken = reconstruction_threshold - 1

    players = get_ids(num_players)
    shares_subset = get_shares_subset(players, reconstruction_threshold, secret, end)
    unjsonify_shares = {player: rss._deserialize_robust_share(share) for player, share in shares_subset.items()[:num_broken]}

    for player, share in unjsonify_shares.items():
        share["keys"] = str(share["keys"])

    shares = combine_testing_dictionaries(shares_subset, jsonify_dict(unjsonify_shares))

    recovered_secret, authorized_players, invalid_players = \
        rss.reconstruct_secret(num_players, reconstruction_threshold, len(secret), shares)
    assert verify_results(recovered_secret, secret,
                          authorized_players, shares_subset.keys()[num_broken:],
                          invalid_players, shares_subset.keys()[:num_broken]) is True


def test_various_parse_errors():
    reconstruction_threshold = 6
    num_broken = reconstruction_threshold - 1
    num_players = reconstruction_threshold + num_broken
    end = num_players

    players = get_ids(num_players)
    shares_subset = get_shares_subset(players, reconstruction_threshold, secret, end)

    unjsonify_shares = {player: rss._deserialize_robust_share(share) for player, share in shares_subset.items()}

    remove_vectors_player = players[0]
    remove_vectors_share = unjsonify_shares[remove_vectors_player]
    unjsonify_shares[remove_vectors_player]["vectors"] = {player: vector for player, vector in remove_vectors_share["vectors"].items()[:4]}

    remove_keys_player = players[1]
    remove_keys_share = unjsonify_shares[remove_keys_player]
    unjsonify_shares[remove_keys_player]["keys"] = {player: key for player, key in remove_keys_share["keys"].items()[:4]}

    make_share_string_player = players[2]
    unjsonify_shares[make_share_string_player]["share"] = str(unjsonify_shares[make_share_string_player]["share"])

    shares = jsonify_dict(unjsonify_shares)

    json_parse_player = players[3]
    shares[json_parse_player] = shares[json_parse_player][1:]  # remove starting bracket

    key_error_player = players[4]
    key_error_share = shares[key_error_player]
    keys_index = key_error_share.index("keys")
    shares[key_error_player] = key_error_share[:keys_index] + "pown" + key_error_share[keys_index + len("keys"):]

    recovered_secret, authorized_players, invalid_players = \
        rss.reconstruct_secret(num_players, reconstruction_threshold, len(secret), shares)
    dishonest_players = [remove_vectors_player, remove_keys_player, make_share_string_player, json_parse_player, key_error_player]
    assert verify_results(recovered_secret, secret,
                          authorized_players, list(set(players) - set(dishonest_players)),
                          invalid_players, dishonest_players) is True
