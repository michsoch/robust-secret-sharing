from crypto_tools import random, polynomials


def _verify_parameters(num_players, reconstruction_threshold, secret, prime):
    '''
    Args:
        see arguments to share_secret
    Returns:
        true if num_players, reconstruction_threshold, secret, and prime are validated
    '''
    # TODO: chat about how this should be handled
    return reconstruction_threshold <= num_players \
        and prime is not None \
        and secret < prime \
        and num_players < prime


def share_secret(num_players, reconstruction_threshold, secret, prime):
    '''
    Args:
        num_players, the number of shares to be distributed
        reconstruction_threshold, the number of shares needed for reconstruction
            any collection of fewer shares will reveal no information about the secret
        secret, a bytestring to be Shamir secret shared
        prime, the prime value used to create a field for computations
    Returns:
        a list of tuple of (x, f(x)) values representing shares
            that can be used to reconstruct the secret via reconstruct_secret
    Raises:
        ValueError, the input arguments fail validation
    '''
    if not _verify_parameters(num_players, reconstruction_threshold, secret, prime):
        raise ValueError("invalid secret sharing parameters")

    # fix n distinct points, alpha_1,...,alpha_n in Z_ps  (public)
    alphas = [i for i in xrange(1, num_players + 1)]  # TODO: should these be picked arbitrarily to hide n?

    # choose at random t points, a_1,...,a_t in Z_ps (private)
    #   we will use the a_i values as our coefficients to define the polynomial f(x) = (a_t x^t) + ... + (a_1 x) + s
    coefficients = [secret] + random.get_distinct_random_ints_in_field(reconstruction_threshold - 1, prime)

    # for values of i from 1 to n, calculate f(alpha_i)
    return polynomials.evaluate(coefficients, alphas, prime)


def reconstruct_secret(shares, prime):
    '''
    Args:
       shares, a list of tuples of (x, f(x)) values from share_secret
       prime, the prime value used to create a field for computations
    Returns:
        an integer representation of the secret that was shared by share_secret
    '''
    return polynomials.interpolate(shares, prime)(0)
