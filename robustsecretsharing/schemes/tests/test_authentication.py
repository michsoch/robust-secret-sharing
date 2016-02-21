from robustsecretsharing.schemes import authentication
import pytest


def test_check_vector_standard():
    message = 112358132134
    max_length = len(str(message))
    key, vector = authentication.generate_check_vector(message, max_length)
    assert authentication.validate(key, vector, message, max_length)


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
    assert authentication.validate(key, vector, message, max_length)


def test_check_vector_too_large():
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
        assert authentication.validate(key, vector, message, max_length)


def test_generate_batch_validate_batch_all_valid():
    message = 112358132134
    max_length = len(str(message))
    num_macs = 55

    keys, vectors = authentication.generate_batch(num_macs, message, max_length)
    assert [True] * num_macs == authentication.validate_batch(keys, vectors, message, max_length)


def test_generate_batch_validate_batch_mix():
    message = 112358132134
    max_length = len(str(message))
    num_macs = 55

    keys, vectors = authentication.generate_batch(num_macs, message, max_length)
    midpoint = len(vectors) / 2
    valid_half = [vector for vector in vectors[:midpoint]]
    invalid_half = [(vector[0] - 1, vector[1]) for vector in vectors[midpoint:]]

    assert len(invalid_half) + len(valid_half) == len(vectors)
    vectors = valid_half + invalid_half

    assert ([True] * (num_macs / 2)) + ([False] * (num_macs - num_macs / 2)) == authentication.validate_batch(keys, vectors, message, max_length)


def test_generate_batch_validate_batch_all_invalid_vector():
    message = 112358132134
    max_length = len(str(message))
    num_macs = 55

    keys, vectors = authentication.generate_batch(num_macs, message, max_length)
    midpoint = len(vectors) / 2
    first_half = [(vector[0] - 1, vector[1]) for vector in vectors[:midpoint]]
    second_half = [(vector[0], vector[1] - 1) for vector in vectors[midpoint:]]

    assert len(first_half) + len(second_half) == len(vectors)
    vectors = first_half + second_half

    assert [False] * num_macs == authentication.validate_batch(keys, vectors, message, max_length)


def test_generate_batch_validate_batch_all_invalid_key():
    message = 112358132134
    max_length = len(str(message))
    num_macs = 55

    keys, vectors = authentication.generate_batch(num_macs, message, max_length)
    keys = [key - 1 for key in keys]  # corrupt all keys
    assert [False] * num_macs == authentication.validate_batch(keys, vectors, message, max_length)


def test_generate_batch_validate_batch_all_valid_multimessage():
    messages = [112358132134, 2468024680, 135791357913579, 4444]
    num_macs = 10

    all_keys = []
    all_vectors = []
    for message in messages:
        keys, vectors = authentication.generate_batch(num_macs, message, len(str(message)))
        all_keys += keys
        all_vectors += vectors

    i = 0
    for message in messages:
        assert [True] * num_macs == \
            authentication.validate_batch(all_keys[num_macs * i: num_macs * (i + 1)], all_vectors[num_macs * i: num_macs * (i + 1)], message, len(str(message)))
        i += 1


def test_generate_batch_validate_batch_mix_among_messages():
    messages = [112358132134, 2468024680, 7777777, 135791357913579, 4444, 731994]
    num_macs = 10

    all_keys = []
    all_vectors = []
    for message in messages:
            keys, vectors = authentication.generate_batch(num_macs, message, len(str(message)))
            midpoint = len(vectors) / 2
            valid_half = [vector for vector in vectors[:midpoint]]
            invalid_half = [(vector[0] - 1, vector[1]) for vector in vectors[midpoint:]]

            assert len(invalid_half) + len(valid_half) == len(vectors)
            vectors = valid_half + invalid_half

            all_keys += keys
            all_vectors += vectors

    i = 0
    for message in messages:
        assert ([True] * (num_macs / 2)) + ([False] * (num_macs - num_macs / 2)) == \
            authentication.validate_batch(all_keys[num_macs * i: num_macs * (i + 1)], all_vectors[num_macs * i: num_macs * (i + 1)], message, len(str(message)))
        i += 1


def test_generate_batch_validate_batch_mix_with_messages():
    messages = [112358132134, 2468024680, 7777777, 135791357913579, 4444, 731994]
    num_macs = 10

    all_keys = []
    all_vectors = []
    for i in range(len(messages)):
        message = messages[i]
        keys, vectors = authentication.generate_batch(num_macs, message, len(str(message)))
        if i % 2 == 0:  # invalidate every other message batch
            vectors = [(vector[0], vector[1] - 1) for vector in vectors]
        all_keys += keys
        all_vectors += vectors

    i = 0
    for message in messages:
        validated = authentication.validate_batch(all_keys[num_macs * i: num_macs * (i + 1)], all_vectors[num_macs * i: num_macs * (i + 1)], message, len(str(message)))
        if i % 2 == 0:
            assert [False] * num_macs == validated
        else:
            assert [True] * num_macs == validated
        i += 1


def test_generate_batch_validate_batch_all_invalid_vector_multimessage():
    messages = [112358132134, 2468024680, 7777777, 135791357913579, 4444, 731994]
    num_macs = 10

    all_keys = []
    all_vectors = []
    for i in range(len(messages)):
        message = messages[i]
        keys, vectors = authentication.generate_batch(num_macs, message, len(str(message)))
        vectors = [(vector[0], vector[1] - 1) for vector in vectors]
        all_keys += keys
        all_vectors += vectors

    i = 0
    for message in messages:
        validated = authentication.validate_batch(all_keys[num_macs * i: num_macs * (i + 1)], all_vectors[num_macs * i: num_macs * (i + 1)], message, len(str(message)))
        assert [False] * num_macs == validated
        i += 1


def test_generate_batch_validate_batch_all_invalid_key_multimessage():
    messages = [112358132134, 2468024680, 7777777, 135791357913579, 4444, 731994]
    num_macs = 10

    all_keys = []
    all_vectors = []
    for i in range(len(messages)):
        message = messages[i]
        keys, vectors = authentication.generate_batch(num_macs, message, len(str(message)))
        keys = [key - 1 for key in keys]
        all_keys += keys
        all_vectors += vectors

    i = 0
    for message in messages:
        validated = authentication.validate_batch(all_keys[num_macs * i: num_macs * (i + 1)], all_vectors[num_macs * i: num_macs * (i + 1)], message, len(str(message)))
        assert [False] * num_macs == validated
        i += 1
