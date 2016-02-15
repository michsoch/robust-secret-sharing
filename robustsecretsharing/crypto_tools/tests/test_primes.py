import pytest
from robustsecretsharing.crypto_tools import primes


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


# error cases

def test_get_prime_by_bitlength_too_large_prime():
    secret_size = 4423
    with pytest.raises(ValueError):
        primes.get_prime_by_bitlength(secret_size)


def test_get_prime_by_bitlength_too_large():
    secret_size = 4444
    with pytest.raises(ValueError):
        primes.get_prime_by_bitlength(secret_size)


def test_get_prime_by_bitlength_negative():
    secret_size = -7
    with pytest.raises(ValueError):
        primes.get_prime_by_bitlength(secret_size)
