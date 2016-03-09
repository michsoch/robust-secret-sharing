from robustsecretsharing.crypto_tools import serialization
from robustsecretsharing.schemes import authentication, sss, pairing
import json


class FatalReconstructionFailure(Exception):
    """
    Raised when there are too few honest shares too allow for reconstruction of the secret
    """


def jsonify_robust_share(share, keys, vectors):
    return json.dumps({'share': share, 'keys': keys, 'vectors': vectors})


def unjsonify_robust_share(json_dump):
    json_dict = json.loads(json_dump)
    return json_dict['share'], json_dict['keys'], json_dict['vectors']


def make_robust_shares(int_shares, batch_keys, batch_vectors):
    robust_shares = []
    for share in int_shares:  # give to player i the tuple (s_i, t_{ji}_j, k_{ij}_j) over values of j
        player_keys = [batch_keys[s][len(robust_shares)] for s in int_shares]
        robust_shares.append(jsonify_robust_share(share, player_keys, batch_vectors[share]))
    return robust_shares


def share_secret(num_players, reconstruction_threshold, max_secret_length, secret):
    '''
    Args:
        num_players, the number of shares to be distributed
        reconstruction_threshold, the number of shares needed for reconstruction
            any collection of fewer shares will reveal no information about the secret
        max_secret_length, the maximum length of the secret represented as a bytestring (ie, len(secret))
        secret, an integer to be Shamir secret shared
    Returns:
        a list of bytestrings, each reprsenting a tuple of (x, f(x)) values TODO: also include the keys and macs
            these are the shares that can be used to reconstruct the secret via reconstruct_secret
    Raises:
        ValueError, the input parameters fail validation
    '''
    secret_int = serialization.convert_bytestring_to_int(secret)

    # generate shares of the secret s: ((x_1, s_1), . . . , (x_n, s_n))
    int_shares = [pairing.elegant_pair(*share) for share in sss._share_secret_int(num_players, reconstruction_threshold, max_secret_length + 1, secret_int)]

    batch_keys, batch_vectors = {}, {}  # TODO: is there a more pythonic way to to do this?
    for share in int_shares:  # generate n MAC keys k_ij and vectors t_ij = MAC(k_ij, s_j) per share s_j
        batch_keys[share], batch_vectors[share] = authentication.generate_batch(num_players, share, max_secret_length)

    return make_robust_shares(int_shares, batch_keys, batch_vectors)


def reconstruct_secret(num_players, reconstruction_threshold, max_secret_length, robust_shares):
    '''
    Args:
        num_players, the total number of players (can be greater than or equal to the number of shares)
        reconstruction_threshold, the number of shares needed for reconstruction
        max_secret_length, the maximum length of the secret represented as a bytestring (ie, len(secret))
        robust_shares, a list of JSON strings collected from share_secret

        Note: (TODO) - for now assume that len(shares) >= reconstruction_threshold
    Returns:
        result, a tuple of (secret, malicious_shares_list)
            secret: the bytestring that was shared by share_secret
            malicious_shares_list: the list of corrupt shares that fail authentication
    Raises:
        ValueError, share that were believed to be valid could not be parsed. Indicates some IllegalState.
        FatalReconstructionFailure, custom exception raised when the number of honest shares is less than reconstruction_threshold
    '''

    shares, share_keys, share_vectors = zip(*[unjsonify_robust_share(robust_share) for robust_share in robust_shares])

    tuple_shares = [pairing.elegant_unpair(share) for share in shares]
    return serialization.convert_int_to_bytestring(sss._reconstruct_secret_int(num_players, max_secret_length + 1, tuple_shares))

    # TODO: for now, just call sss reconstruction and see if we can pass the basic sharing tests

    # TODO: verify parameters

    # create a dictionary of number tags to each share (bytestring)

    # then create a dictionary of number tags to number tags that have been verified by that one

    # look for a t + 1 or great agreement
        # TODO: how to do this cleanly?
        #   for each number tag, add to list all the number tags that it authorizes
        # ex.
        #   dict = {1: [1, 2, 3], 2: [2, 3, 1], 3: [3, 2, 1], 4: [4, 5], 5: [4, 5]}

        #   then take that dictionary and convert the lists to tuples of sorted lists
        # ex.
        #   dict = {key: tuple(sorted(value)) for key, value in dict.items()}

        #   combine based on values
        # ex.
        #   groups = defaultdict(list)
        #   for key, value in dict.items():
        #       groups[value].append(key)

        #   look for lists of values that are greater than or equal to t + 1
        # ex.
        #   invalidated = []
        #   for key, value in groups.items():
        #       if len(value) >= reconstruction_threshold:
        #           authorized = key
        #       else:
        #           for k in key:
        #               invalidated.append(k)

    # take the number tags that were not in that agreement and make malicious_shares_list from their shares

    # take the number tags from that agreement to get back bytestring shares, and pass to sss.reconstruct_secret

    # then return bytestring (secret, malicious_shares_list)



# ______________________________________________________________________________________________________________________________


# ______________________________________________________________________________________________________________________________

# Shamir Secret Sharing with an honest dealer

# Refer to the corresponding section in the Rabin Ben-Or paper:
    # https://cs.umd.edu/~gasarch/TOPICS/secretsharing/rabinVSS.pdf

# guarantee: "When the secret is revealed we want that
    # all knights will agree on the same value and
    # that it will be the original secret the dealer shared."

# TODOS:
    # hard-code a massive prime for auth

# parameters:
    # n: number of providers (n >= 2t + 1)
    # t: t players get no info, t + 1 can reconstruct
    # s: the secret
    # k is a security parameter
        # selected so that the probability of error is 2^(-k)
    # ps: a (potentially small) pubic prime used for defining polynomial coefficients
    # pv: a large, private prime used for check vectors

# sharing the secret (Phase 1) -
    # gather shares f(alpha_i)
        # (see sss.py)

    # for each f(alpha_i) generate a check vector
        # (see authentication.py)

    # disperse values to each player, Pi
        # f(alpha_i), the players share
        # y_i1, ..., y_in which the y_ij are the "tags" for Pi
        # (b1i, c_1i), ..., (bni, c_ni)
            # the (b_ji, c_ji) values are used by Pi to authenticate players Pj's tag

# recovering the secret (Phase 2) -
    # fix: just make the checks below ourselves by requesting info rather than sending it out

    # goal: look for agreement across a subset of t + 1 of the shares

    # retrieve values from all players

    # calculate all pairs (f(alpha_i), y_ij), i != j

    # verify with all (b_ji, c_ji) that c_ji = f(alpha_j) + b_ji y_ji
        # accept or reject accordingly
        # (see authentication.py)

    # if pieces f(alpha_i1), ..., f(alpha_ir), r >= t + 1 are accepted for player Pi
    # then s can be calculated with these r shares
        # (see sss.py)
