from robustsecretsharing.schemes import authentication
import pytest


def test_check_vector_standard():
    message = 112358132134
    max_length = len(str(message))
    key, vector = authentication.generate_check_vector(message, max_length)
    assert authentication.validate(key, vector, message, max_length) is True


def test_check_vector_large():
    message = ('123456789012345678901234567890123456789012345678901234567890'
               '123456789012345678901234567890123456789012345678901234567890'
               '123456789012345678901234567890123456789012345678901234567890'
               '123456789012345678901234567890123456789012345678901234567890'
               '123456789012345678901234567890123456789012345678901234567890'
               '123456789012345678901234567890123456789012345678901234567890'
               '12345678901234567890')
    max_length = len(message)

    message = int(message)
    key, vector = authentication.generate_check_vector(message, max_length)
    assert authentication.validate(key, vector, message, max_length) is True


def test_check_vector_message_too_large():
    message = ('123456789012345678901234567890123456789012345678901234567890'
               '123456789012345678901234567890123456789012345678901234567890'
               '123456789012345678901234567890123456789012345678901234567890'
               '123456789012345678901234567890123456789012345678901234567890'
               '123456789012345678901234567890123456789012345678901234567890'
               '123456789012345678901234567890123456789012345678901234567890'
               '123456789012345678901234567890123456789012345678901234567890'
               '123456789012345678901234567890123456789012345678901234567890'
               '123456789012345678901234567890123456789012345678901234567890'
               '123456789012345678901234567890123456789012345678901234567890'
               '12345678901234567890')

    max_length = len(message)
    message = int(message)

    with pytest.raises(ValueError):
        authentication.generate_check_vector(message, max_length)


def test_check_vector_b():
    message = 112358132134
    max_length = len(str(message))

    for i in range(1000):
        key, vector = authentication.generate_check_vector(message, max_length)

        if (vector[0] == 0):  # verify that b is never zero for many cases
            assert False
        else:
            assert authentication.validate(key, vector, message, max_length) and vector[0] != 0


def test_generate_batch_validate_single():
    message = 112358132134
    max_length = len(str(message))
    num_macs = 55

    keys, vectors = authentication.generate_batch(num_macs, message, max_length)
    for key, vector in zip(keys, vectors):
        assert authentication.validate(key, vector, message, max_length) is True
