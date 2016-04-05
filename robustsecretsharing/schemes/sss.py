from robustsecretsharing.crypto_tools import random, polynomials, primes, serialization
from robustsecretsharing.schemes import pairing


def _verify_parameters(num_players, reconstruction_threshold, secret, prime):
    '''
    Args:
        see arguments to share_secret
    Returns:
        true if num_players, reconstruction_threshold, secret, and prime are validated
    '''
    return reconstruction_threshold <= num_players \
        and prime is not None \
        and secret < prime \
        and num_players < prime


def _share_secret_int(num_players, reconstruction_threshold, max_secret_length, secret):
    '''
    Args:
        num_players, the number of shares to be distributed
        reconstruction_threshold, the number of shares needed for reconstruction
            any collection of fewer shares will reveal no information about the secret
        max_secret_length, the maximum length of the secret represented as a bytestring (ie, len(secret))
        secret, an integer to be Shamir secret shared
    Returns:
        a list of tuples of (x, f(x)) values
    Raises:
        ValueError, the input parameters are invalid
    '''
    bitlength = max(num_players.bit_length(), max_secret_length * 8)
    prime = primes.get_prime_by_bitlength(bitlength)

    if not _verify_parameters(num_players, reconstruction_threshold, secret, prime):
        raise ValueError("invalid secret sharing parameters")

    # fix n distinct points, alpha_1,...,alpha_n in Z_ps  (public)
    alphas = [i for i in xrange(1, num_players + 1)]

    # choose at random t points, a_1,...,a_t in Z_ps (private)
    #   we will use the a_i values as our coefficients to define the polynomial f(x) = (a_t x^t) + ... + (a_1 x) + s
    coefficients = [secret] + random.get_distinct_positive_random_ints_in_field(reconstruction_threshold - 1, prime)

    # for values of i from 1 to n, calculate f(alpha_i)
    return polynomials.evaluate(coefficients, alphas, prime)


def share_secret(num_players, reconstruction_threshold, max_secret_length, secret):
    '''
    Args:
        num_players, the number of shares to be distributed
        reconstruction_threshold, the number of shares needed for reconstruction
            any collection of fewer shares will reveal no information about the secret
        max_secret_length, the maximum length of the secret represented as a bytestring (ie, len(secret))
        secret, a bytestring to be Shamir secret shared
    Returns:
        a list of strings, each representing an integer, that can be passed to reconstruct_secret
    Raises:
        ValueError, the input arguments fail validation
    '''
    secret_int = serialization.convert_bytestring_to_int(secret)
    points = _share_secret_int(num_players, reconstruction_threshold, max_secret_length + 1, secret_int)
    return [str(pairing.elegant_pair(*tup)) for tup in points]


def _reconstruct_secret_int(num_players, max_secret_length, shares):
    '''
    Args:
        num_players, the total number of players (can be greater than or equal to the number of shares)
        max_secret_length, the maximum length of the secret represented as a bytestring (ie, len(secret))
        shares, a list of tuples representing (x, f(x)) values
    Returns:
        if all shares are valid, the integer that was shared by _share_secret_int
        otherwise, no guarantees are made about the value of the integer returned
    '''
    bitlength = max(num_players.bit_length(), max_secret_length * 8)
    prime = primes.get_prime_by_bitlength(bitlength)
    return polynomials.interpolate(shares, prime)(0)


def reconstruct_secret(num_players, max_secret_length, shares):
    '''
    Args:
        num_players, the total number of players (can be greater than or equal to the number of shares)
        max_secret_length, the maximum length of the secret represented as a bytestring (ie, len(secret))
        shares, a list of strings - each representing an integer value
    Returns:
        if all shares are valid, the original secret as passed to share_authenticated_secret
        otherwise, no guarantees are made about the value of the bytestring returned
    '''
    points = [pairing.elegant_unpair(int(share)) for share in shares]
    secret_int = _reconstruct_secret_int(num_players, max_secret_length + 1, points)
    return serialization.convert_int_to_bytestring(secret_int)
