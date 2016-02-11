MERSENNE_PRIME_EXPONENTS = [2, 3, 5, 7, 13, 17, 19, 31, 61, 89, 107, 127, 521, 607, 1279,
                            2203, 2281, 3217, 4253, 4423]


def _mersenne_primes():
    '''
    Returns:
        all the mersenne primes with less than 5000 digits.
    '''
    primes = []

    for exp in MERSENNE_PRIME_EXPONENTS:
        prime = 2**exp - 1
        primes.append(prime)
    return primes


def get_prime_by_bitlength(bitlength):
    '''
    Returns:
        a prime with strictly more bits than the specified size
        or None if no such prime is found in hardcoded list
    Raises:
        ValueError, size is negative
        ValueError, could not find a sufficiently large prime
    '''
    if bitlength < 0:
        raise ValueError("invalid bit-length for prime selection")

    for exp in MERSENNE_PRIME_EXPONENTS:
        if exp > bitlength:
            return 2**exp - 1
    raise ValueError("could not return a sufficiently large prime")
