from robustsecretsharing.crypto_tools import serialization
from robustsecretsharing.schemes import authentication, sss, pairing
from collections import defaultdict
import json


class FatalReconstructionFailure(Exception):
    """
    Raised when reconstruction of the original secret cannot be guaranteed
    """


def _serialize_robust_share(share, keys, vectors):
    '''
    Args:
        share, an integer representation of a share
        keys, a dictionary of string player ids to integer keys
        vectors, a dictionary of string player ids to tuples of ints representing authentication vectors
    Returns:
        a serialized robust share string that encodes the arguments in a dictionary
        with keys: share, keys, and vectors
    '''
    return json.dumps({'share': share, 'keys': keys, 'vectors': vectors})


def _deserialize_robust_share(serialized_dump):
    '''
    Args:
        serialized_dump, a string created by _serialize_robust_share
    Returns:
        a dictionary of the arguments passed to _serialize_robust_share
        with keys (share, keys, vectors)
    Raises:
        ValueError
    '''
    return json.loads(serialized_dump)


def _make_robust_shares(shares_map, batch_keys, batch_vectors):
    '''
    Args:
        shares_map, a map of player ids to integer-valued shares
        batch_keys, a dictionary of player ids to
            dictionaries of player ids to associated integer keys
        batch_vectors, a dictionary of player ids to
            dictionaries of player ids to associated tuple vectors
    Returns:
        a dictionary of player ids to serialized robust shares containing
            a share
            a map of player ids to keys for the shares held by those players
            a map of player ids to vectors for this share
                that can be verified by keys held by those players
    '''
    robust_shares_map = {}
    for player, share in shares_map.items():
        keys_for_players = {other: batch_keys[other][player] for other in shares_map.keys()}
        robust_shares_map[player] = _serialize_robust_share(share, keys_for_players, batch_vectors[player])
    return robust_shares_map


def share_authenticated_secret(players, reconstruction_threshold, max_secret_length, secret):
    '''
    Args:
        players, a list of unique string ids for all players
        reconstruction_threshold, the number of shares needed for reconstruction
            any collection of fewer shares will reveal no information about the secret
        max_secret_length, the maximum length of the secret represented as a bytestring (ie, len(secret))
        secret, a bytestring to be Shamir secret shared
    Returns:
        a dictionary of ids (from the players argument) to robust secret shares, which consist of
            a share
            a map of player ids to keys for the shares held by those players
            a map of player ids to vectors for this share
                that can be verified by keys held by those players
    Raises:
        ValueError, the input parameters fail validation (see share_secret of schemes/sss.py)
    '''
    num_players = len(players)
    secret_int = serialization.convert_bytestring_to_int(secret)

    # generate shares of the secret s: ((x_1, s_1), . . . , (x_n, s_n))
    int_shares = [pairing.elegant_pair(*share) for share in
                  sss._share_secret_int(num_players,
                                        reconstruction_threshold,
                                        max_secret_length + 1,  # conversion to an integer adds one byte
                                        secret_int)]

    # assign shares to players
    shares_map = {player: share for (player, share) in zip(players, int_shares)}

    batch_keys, batch_vectors = defaultdict(dict), defaultdict(dict)
    for player in players:  # generate n MAC keys k_ij and vectors t_ij = MAC(k_ij, s_j) per share s_j
        keys, vectors = authentication.generate_batch(num_players, shares_map[player], max_secret_length + 1)
        for player_id, key, vector in zip(players, keys, vectors):
            batch_keys[player][player_id] = key
            batch_vectors[player][player_id] = vector

    return _make_robust_shares(shares_map, batch_keys, batch_vectors)


def _map_player_to_attributes(robust_shares_map, invalid_players):
    '''
    Create a dictionary from player to attribute value for "share", "keys", and "vectors" attributes
    If the robust share dictionary for a given player does not have all expected attributes,
    add that player to the invalid_players set.
    Args:
        robust_shares_map, a dictionary of string player ids to a dictionary with attributes
            "share", keys", and "vectors"
        invalid_players, a growing set of players whose shares cause structural errors
    Returns:
        a tuple of 3 dictionaries that each map string player ids to one of the attributes of robust_shares_map
        each of these dictionaries will have the same set of keys
    '''
    shares_map, keys_for_players, vectors_from_players = {}, {}, {}
    for player in robust_shares_map.keys():
        try:
            share = robust_shares_map[player]["share"]
            keys = robust_shares_map[player]["keys"]
            vectors = robust_shares_map[player]["vectors"]
        except KeyError:
            invalid_players.add(player)
        else:
            shares_map[player] = share
            keys_for_players[player] = keys
            vectors_from_players[player] = vectors
    return shares_map, keys_for_players, vectors_from_players


def _assert_valid_share(share):
    '''
    Asserts valid structure for the given share
    Args:
        share, an integer share
    '''
    assert isinstance(share, (int, long))


def _assert_valid_keys(players, keys):
    '''
    Asserts valid structure for the given keys dictionary
    Args:
        players, a list of all current player ids
        keys, a given dictionary of player ids to keys
    '''
    assert isinstance(keys, dict)
    for target in players:
        assert target in keys.keys()
        assert isinstance(keys[target], (int, long))


def _assert_valid_vectors(players, vectors):
    '''
    Asserts valid structure for the given vectors dictionary
    Args:
        players, a list of all current player ids
        vectors, a given dictionary of player ids to vector tuples
    '''
    assert isinstance(vectors, dict)
    for target in players:
        assert target in vectors.keys()
        assert len(vectors[target]) == 2
        assert isinstance(vectors[target][0], (int, long))
        assert isinstance(vectors[target][1], (int, long))


def _validate_attributes(players, shares_map, keys_for_players, vectors_from_players, invalid_players):
    '''
    Will validate the structure of all shares, keys, and vectors and add violating players to the invalid_players list
    Args:
        players, a list of all current player ids
        shares_map, a map of string player ids to integer shares
        keys_for_players, a map of string players ids to keys associated with others players' shares
        vectors_from_players, a map of string players ids to vectors associated with those players shares
        invalid_players, a growing set of players who cause structural errors
    '''
    for player, share, keys, vectors in zip(players, shares_map.values(), keys_for_players.values(), vectors_from_players.values()):
        try:
            _assert_valid_share(share)
            _assert_valid_keys(players, keys)
            _assert_valid_vectors(players, vectors)
        except AssertionError:
            invalid_players.add(player)


def _clean_map(players, shares_map, keys_for_players, vectors_from_players, invalid_players):
    '''
    Args:
        players, a list of all current player ids
        shares_map, a map of string player ids to integer shares
        keys_for_players, a map of string players ids to keys associated with others players' shares
        vectors_from_players, a map of string players ids to vectors associated with those players shares
        invalid_players, the finalized set of players whose shares cause structural errors
    Removes all invalid_players from the keys of the three given mappings
    '''
    for player in players:
        if player in invalid_players:
            del shares_map[player]
            del keys_for_players[player]
            del vectors_from_players[player]


def _get_player_to_verifies_map(shares_map, keys_for_players, vectors_from_players, max_secret_length):
    '''
    Args:
        shares_map, a mapping of player string ids to integer shares
        keys_for_players, a mapping of player string ids to maps of keys to associate with other players
        vectors_from_players, a mapping of player string ids to maps of vectors associated with this player's share
        max_secret_length, the max length of the share if it were represented as a bytestring
    Returns:
        a mapping from player string id (verifier) to a tuple of players verified by the verifier
    '''
    verifies = defaultdict(list)
    for verifier in shares_map.keys():
        for player, share in shares_map.items():
            if authentication.validate(keys_for_players[verifier][player], vectors_from_players[player][verifier], share, max_secret_length + 1):
                verifies[verifier].append(player)
    # return a dictionary that can be inverted - the value is a tuple (hashable) and sorted (in preparation for equality checks)
    return {verifier: tuple(sorted(players)) for verifier, players in verifies.items()}


def _get_bytestring_secret(shares, num_players, max_secret_length):
    '''
    Args:
        shares, a list of paired integer shares (see schemes/pairing.py)
        num_players, the number of total players
        max_secret_length, the max length of the share if it were represented as a bytestring
    Returns:
        if all shares are valid, the original secret as passed to share_authenticated_secret
        otherwise, no guarantees are made about the value of the bytestring returned
    '''
    tuple_shares = [pairing.elegant_unpair(share) for share in shares]
    return serialization.convert_int_to_bytestring(sss._reconstruct_secret_int(num_players, max_secret_length + 1, tuple_shares))


def _get_player_to_secret_map(verifies_map, shares_map, num_players, reconstruction_threshold, max_secret_length):
    '''
    Args:
        verifies_map, a mapping from player string id (verifier) to a tuple of players verified by the verifier
        shares_map, a mapping of player string ids to integer shares
        num_players, the total number of original shares (may be greater than or equal to len(verifies_map))
        reconstruction_threshold, the number of honest players required for secret reconstruction
        max_secret_length, the max length of the share if it were represented as a bytestring
    Returns:
        a mapping from player string ids to bytestring secrets
        that are reconstructed based on the shares verified by that player
    '''
    secret_map = {}
    for verifier, players in verifies_map.items():
        if len(players) >= reconstruction_threshold:
            secret_map[verifier] = _get_bytestring_secret([shares_map[player] for player in players], num_players, max_secret_length)
    return secret_map


def _invert_and_combine_by_value(original_dict):
    '''
    Args:
        original_dict, some dictionary of hashable keys to hashable values
    Returns:
        a reversed dictionary combined by value
    '''
    swapped = defaultdict(list)
    for key, value in original_dict.items():
        swapped[value].append(key)
    return swapped


def _vote(voting_blocks, reconstruction_threshold):
    '''
    Args:
        voting_blocks, a dictionary of reconstructed bytestring secrets to
            the list of players who reconstructed that secret from their authenticated shares
        reconstruction_threshold, the number of honest players required for reconstruction
    Returns:
        a list of all secrets that have votes from reconstruction_threshold number of players or more
    '''
    authorized = []
    for secret, verifiers in voting_blocks.items():
        if len(verifiers) >= reconstruction_threshold:
            authorized.append((secret, verifiers))
    return authorized


def reconstruct_authenticated_secret(num_players, reconstruction_threshold, max_secret_length, serialized_map):
    '''
    Args:
        num_players, the length of the list of players passed to share_authenticated_secret
        reconstruction_threshold, the number of shares needed for reconstruction
        max_secret_length, the maximum length of the secret represented as a bytestring (ie, len(secret))
        serialized_map, a map of valid player string ids to serialized robust share strings dispersed from share_authenticated_secret
    Returns:
        if the number of dishonest players was less than reconstruction_threshold,
        a successful return contains a tuple of
            the original bytestring that was shared by share_authenticated_secret
            a non-exhaustive list of players whose shares could be used for reconstruction of that secret
            a non-exhaustive list of dishonest players (specifically those whose shares caused structural errors)
    Raises:
        FatalReconstructionFailure, authenticated reconstruction could not be guaranteed
    '''
    invalid_players = set()
    robust_shares_map = {}
    for player, robust_share in serialized_map.items():
        try:
            robust_shares_map[player] = _deserialize_robust_share(robust_share)
        except ValueError:
            invalid_players.add(player)

    shares_map, keys_for_players, vectors_from_players = _map_player_to_attributes(robust_shares_map, invalid_players)
    players = shares_map.keys()
    _validate_attributes(players, shares_map, keys_for_players, vectors_from_players, invalid_players)

    # now that the set of invalid_players has been finalized, remove these players from the working dictionaries
    _clean_map(players, shares_map, keys_for_players, vectors_from_players, invalid_players)

    verifies_map = _get_player_to_verifies_map(shares_map, keys_for_players, vectors_from_players, max_secret_length)
    secret_map = _get_player_to_secret_map(verifies_map, shares_map, num_players, reconstruction_threshold, max_secret_length)
    voting_blocks = _invert_and_combine_by_value(secret_map)
    authorized = _vote(voting_blocks, reconstruction_threshold)

    if len(authorized) != 1:  # authenticated reconstruction cannot be guaranteed
        raise FatalReconstructionFailure

    secret, voting_players = authorized[0]  # authorized list is necessarily of length 1
    verified_players = {player for voter in voting_players for player in verifies_map[voter]}

    return secret, list(verified_players), list(invalid_players)


def reconstruct_unauthenticated_secret(num_players, max_secret_length, serialized_map):
    '''
    Args:
        num_players, the length of the list of players passed to share_authenticated_secret
        max_secret_length, the maximum length of the secret represented as a bytestring (ie, len(secret))
        serialized_map, a map of valid player string ids to serialized robust shares dispersed from share_authenticated_secret
    Returns:
        if all shares are valid, the original bytestring that was shared by share_authenticated_secret
        otherwise, no gaurentees are a
    '''
    shares = []
    for player, robust_share in serialized_map.items():
        try:
            share = _deserialize_robust_share(robust_share)["share"]
            _assert_valid_share(share)
        except (ValueError, KeyError, AssertionError):
            pass  # ignore players who cause structural share errors
        else:
            shares.append(share)

    return _get_bytestring_secret(shares, num_players, max_secret_length)
