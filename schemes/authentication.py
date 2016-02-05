# check vector generation
    # generate a prime pv > 2^k and assume s is in Z_pv
        # (see primes.py)
    # generate random values in Z_pv for tuples (b_i1, y_i1), ... ,(b_in, y_in)
        # the b_i values are not equal to zero
        # (see random.py)
    # compute c_ij = s_j + b_ij y_ij
    # (b_ij, c_ij) will be the check vector

# function to verify or reject based on given parameters
