# generate secret shares
    # fix a small prime ps > n, and assume that s is in Z_ps (public)
        # (see primes.py)

    # fix n distinct points, alpha_1,...,alpha_n in Z_ps  (public)
        # (see random.py)

    # choose at random t points, a_1,...,a_t in Z_ps (private)
        # (see random.py)

    # use the a values to define the polynomial f(x) = (a_t x^t) + ... + (a_1 x) + s
        # (see polynomials.py)

    # for values of i from 1 to n, calculate f(alpha_i)
        # (see polynomials.py)

    # return the f(alpha_i) values

# recover secret shares
    # (see polynomials.py)
