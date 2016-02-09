class IllegalArgumentException(Exception):
    '''
    Indicates degenerate cases for parameters
    '''


class EntropyNotFound(Exception):
    '''
    Raised when a source of entropy cannot be found or
    when there is insufficient entropy
    '''


class FatalConfigurationError(Exception):
    '''
    Indicates that the desired configuration is not viable.
    This is used in the following cases -
        n or s (the secret) are too large to allow for a prime value to be selected for sharing
        t + 1 (the degree of the polynomial) is so large that we cannot select enough coefficients
            given the size of the secret and chosen prime
        t + 1 is greater than or equal to n
    '''
