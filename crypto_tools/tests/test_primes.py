import pytest
from crypto_tools import primes
from customexceptions import custom_exceptions

# test by bitlength


def test_get_prime_by_bitlength_standard():
    secret_size = 61
    assert primes.get_prime_by_bitlength(secret_size) == 2**89 - 1


def test_get_prime_by_bitlength_prime():
    secret_size = 17
    assert primes.get_prime_by_bitlength(secret_size) == 2**19 - 1


def test_get_prime_by_bitlength_zero():
    secret_size = 0
    assert primes.get_prime_by_bitlength(secret_size) == 2**2 - 1


def test_get_prime_by_batch_equal_prime():
    secret_size = 521
    assert primes.get_prime_by_bitlength(secret_size) == 2**607 - 1


def test_get_prime_by_bitlength_very_large():
    secret_size = 4400
    assert primes.get_prime_by_bitlength(secret_size) == 2**4423 - 1


def test_get_prime_by_bitlength_too_large_prime():
    secret_size = 4423
    assert primes.get_prime_by_bitlength(secret_size) is None


def test_get_prime_by_bitlength_too_large():
    secret_size = 4444
    assert primes.get_prime_by_bitlength(secret_size) is None


def test_get_prime_by_bitlength_negative():
    secret_size = -7
    with pytest.raises(custom_exceptions.IllegalArgumentException):
        primes.get_prime_by_bitlength(secret_size)
