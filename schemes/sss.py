from numbers import random, polynomials
from customexceptions import custom_exceptions


def verify_parameters(num_players, reconstruction_threshold, secret, sharing_prime):
    # TODO: chat about how this should be handled
    return reconstruction_threshold <= num_players and \
        sharing_prime is not None and \
        secret < sharing_prime and \
        num_players < sharing_prime


def share_secret(num_players, reconstruction_threshold, secret, sharing_prime):
    if (not verify_parameters(num_players, reconstruction_threshold, secret, sharing_prime)):
        raise custom_exceptions.FatalConfigurationError

    # fix n distinct points, alpha_1,...,alpha_n in Z_ps  (public)
    alpha = [i for i in range(1, num_players + 1)]  # TODO: should this be picked arbitrarily??

    # choose at random t points, a_1,...,a_t in Z_ps (private)
        # we will use the a values to define the polynomial f(x) = (a_t x^t) + ... + (a_1 x) + s
    coefficients = [secret] + random.get_distinct_random_ints_in_field(reconstruction_threshold - 1, sharing_prime)

    # for values of i from 1 to n, calculate f(alpha_i)
    return polynomials.evaluate(coefficients, alpha, sharing_prime)


def reconstruct_secret(shares, sharing_prime):
    return polynomials.interpolate(shares, sharing_prime)(0)
