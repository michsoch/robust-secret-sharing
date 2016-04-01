from robustsecretsharing.crypto_tools import serialization
from robustsecretsharing.schemes import authentication, sss, pairing
from collections import defaultdict
import json


class FatalReconstructionFailure(Exception):
    """
    Raised when there are too few honest shares to allow for reconstruction of the secret
    """


def jsonify_robust_share(share, keys, vectors):
    '''
    Args:
        share, an integer representation of a share
        keys, a dictionary of string player ids to integer keys
        vectors, a dictionary of string player ids to tuples of ints representing authentication vectors
    Returns:
        a JSON string that encodes the arguments in a dictionary
        with keys: share, keys, and vectors
    '''
    return json.dumps({'share': share, 'keys': keys, 'vectors': vectors})


def unjsonify_robust_share(json_dump):
    '''
    Args:
        json_dump, a JSON string created by jsonify_robust_share
    Returns:
        a dictionary of the arguments passed to jsonify_robust_share
        with keys (share, keys, vectors)
    '''
    return json.loads(json_dump)


def make_robust_shares(shares_map, batch_keys, batch_vectors):
    '''
    Args:
        shares_map, a map of player ids to integer-valued shares
        batch_keys, a dictionary of player ids to
            dictionaries of player ids to associated integer keys
        batch_vectors, a dictionary of player ids to
            dictionaries of player ids to associated tuple vectors
    Returns:
        a dictionary of player ids to robust shares that are json strings containing
            a share
            a map of player ids to keys for the shares held by those players
            a map of player ids to vectors for this share
                that can be verified by keys held by those players
    '''
    robust_shares_map = {}
    for player, share in shares_map.items():
        keys_for_providers = {other: batch_keys[other][player] for other in shares_map.keys()}
        robust_shares_map[player] = jsonify_robust_share(share, keys_for_providers, batch_vectors[player])
    return robust_shares_map


def share_secret(players, reconstruction_threshold, max_secret_length, secret):
    '''
    Args:
        players, a list of unique string ids for all players so that the length of this list is num_players
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
        ValueError, the input parameters fail validation
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

    batch_keys, batch_vectors = {}, {}
    for player in players:  # generate n MAC keys k_ij and vectors t_ij = MAC(k_ij, s_j) per share s_j
        keys, vectors = authentication.generate_batch(num_players, shares_map[player], max_secret_length + 1)
        batch_keys[player] = {player: key for (player, key) in zip(players, keys)}
        batch_vectors[player] = {player: vector for (player, vector) in zip(players, vectors)}

    return make_robust_shares(shares_map, batch_keys, batch_vectors)


def _make_map(robust_shares_map, dict_key, invalid_players):
    '''
    Args:
        robust_shares_map, a dictionary of string player ids to a dictionary with attributes
            "share", keys", and "vectors"
        dict_key, one of "share", keys", and "vectors"
        invalid_players, a growing list of players whose shares cause structural errors
    Returns:
        a dictionary of string player id to
        whichever of its attributes from robust_shares_map was specified by dict_key
    '''
    mapping = {}
    for player in robust_shares_map.keys():
        try:
            mapping[player] = robust_shares_map[player][dict_key]
        except KeyError:
            invalid_players.add(player)
    return mapping


def _validate_shares(shares_map, invalid_players):
    '''
    Args:
        shares_map, a map of string provider ids to integer shares
        invalid_players, a growing list of players who cause structural errors
    Will validate the structure of all shares and add violating players to the invalid_players list
    '''
    for player, share in shares_map.items():
        if not isinstance(share, (int, long)):
            invalid_players.add(player)


def _validate_vectors(vectors_from_providers, invalid_players):
    '''
    Args:
        vectors_from_providers, a map of string players ids to vectors associated with those players shares
        invalid_players, a growing list of players who cause structural errors
    Will validate the structure of all vectors and add violating players to the invalid_players list
    '''
    for player, vectors in vectors_from_providers.items():
        if not isinstance(vectors, dict):
            invalid_players.add(player)
            continue

        for target in vectors_from_providers.keys():
            try:
                integer_valued = isinstance(vectors[target][0], (int, long)) and isinstance(vectors[target][1], (int, long))
                if not (integer_valued and len(vectors[target]) == 2):
                    invalid_players.add(player)
            except (KeyError, IndexError):
                invalid_players.add(player)


def _validate_keys(keys_for_providers, invalid_players):
    '''
    Args:
        keys_for_providers, a map of string players ids to keys associated with others players' shares
        invalid_players, a growing list of players who cause structural errors
    Will validate the structure of all keys and add violating players to the invalid_players list
    '''
    for player, keys in keys_for_providers.items():
        if not isinstance(keys, dict):
            invalid_players.add(player)
            continue

        for target in keys_for_providers.keys():
            try:
                if not isinstance(keys[target], (int, long)):
                    invalid_players.add(player)
            except KeyError:
                invalid_players.add(player)


def _clean_map(mapping, invalid_players):
    '''
    Args:
        mapping, a map of string provider ids to some robust share attribute
        invalid_players, the list thus far of providers whose shares cause structural errors
    Removes from the keys of the provided mapping all invalid_players
    '''
    for player in mapping.keys():
        if player in invalid_players:
            del mapping[player]


def _get_player_to_verifies_map(shares_map, keys_for_providers, vectors_from_providers, max_secret_length):
    '''
    Args:
        shares_map, a mapping of player string ids to integer shares
        keys_for_providers, a mapping of player string ids to maps of keys to associate with other players
        vectors_from_providers, a mapping of player string ids to maps of vectors associated with this player's share
        max_secret_length, the max length of the share if it were represented as a bytestring
    Returns:
        a mapping from player string id (verifier) to a tuple of players verified by the verifier
    '''
    verifies = defaultdict(list)
    for verifier in shares_map.keys():
        for player, share in shares_map.items():
            if authentication.validate(keys_for_providers[verifier][player], vectors_from_providers[player][verifier], share, max_secret_length + 1):
                verifies[verifier].append(player)
    return {verifier: tuple(sorted(players)) for verifier, players in verifies.items()}


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
        if (len(players) >= reconstruction_threshold):
            tuple_shares = [pairing.elegant_unpair(share) for share in [shares_map[player] for player in players]]
            try:
                secret = serialization.convert_int_to_bytestring(sss._reconstruct_secret_int(num_players, max_secret_length + 1, tuple_shares))
            except ValueError:
                pass  # attempts by dishonest players to collude may cause a parse failure
            else:
                secret_map[verifier] = secret
    return secret_map


def _swap_and_combine_by_value(original_dict):
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


def reconstruct_secret(num_players, reconstruction_threshold, max_secret_length, json_map):
    '''
    Args:
        num_players, the total number of players (can be greater than or equal to the number of shares)
        reconstruction_threshold, the number of shares needed for reconstruction
        max_secret_length, the maximum length of the secret represented as a bytestring (ie, len(secret))
        json_map, a map of valid player string ids to JSON strings dispersed from share_secret
    Returns:
        if the number of dishonest players was less than reconstruction_threshold,
        a successful return contains a tuple of
            the original bytestring that was shared by share_secret
            a non-exhaustive list of providers whose shares could be used for reconstruction of that secret
            a non-exhaustive list of dishonest providers (specifically those whose shares caused structural errors)
    Raises:
        FatalReconstructionFailure, authenticated reconstruction could not be guaranteed
    '''
    invalid_players = set()
    robust_shares_map = {}
    for player, robust_share in json_map.items():
        try:
            robust_shares_map[player] = unjsonify_robust_share(robust_share)
        except ValueError:
            invalid_players.add(player)

    if (len(robust_shares_map) < reconstruction_threshold):
        raise FatalReconstructionFailure

    shares_map = _make_map(robust_shares_map, "share", invalid_players)
    keys_for_providers = _make_map(robust_shares_map, "keys", invalid_players)
    vectors_from_providers = _make_map(robust_shares_map, "vectors", invalid_players)

    _validate_shares(shares_map, invalid_players)
    _validate_keys(keys_for_providers, invalid_players)
    _validate_vectors(vectors_from_providers, invalid_players)

    _clean_map(shares_map, invalid_players)
    _clean_map(keys_for_providers, invalid_players)
    _clean_map(vectors_from_providers, invalid_players)

    verifies_map = _get_player_to_verifies_map(shares_map, keys_for_providers, vectors_from_providers, max_secret_length)
    secret_map = _get_player_to_secret_map(verifies_map, shares_map, num_players, reconstruction_threshold, max_secret_length)
    voting_blocks = _swap_and_combine_by_value(secret_map)
    authorized = _vote(voting_blocks, reconstruction_threshold)

    if len(authorized) != 1:  # authenticated reconstruction cannot be guaranteed
        raise FatalReconstructionFailure

    secret, voting_players = authorized[0]  # authorized list is necessarily of length 1
    verified_players = {player for voter in voting_players for player in verifies_map[voter]}

    return secret, list(verified_players), list(invalid_players)
