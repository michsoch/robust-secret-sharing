# Implementation of the Rabin Ben-Or Robust Secret Sharing scheme

# generate shares of the secret s: (s_1, . . . , s_n)
    # (see sss.py)

# generate n^2 MAC keys k_{ij}
    # NaCl (?)

# generate n^2 MAC tags t_ij = MAC(k_ij, sj)
    # see paper or use NaCl MACs (?)

# give to player i the tuple (s_i, t_{ji}_j, k_{ij}_j)
    # the second index of the key and tag corresponds to the player index
    # that is, we give each player:
        # their share of the secret
        # n tags associated with this share
        # one key for for each provider
# ______________________________________________________________________________________________________________________________

# Shamir Secret Sharing with an honest dealer

# Refer to the corresponding section in the Rabin Ben-Or paper:
    # https://cs.umd.edu/~gasarch/TOPICS/secretsharing/rabinVSS.pdf

# guarantee: "When the secret is revealed we want that
    # all knights will agree on the same value and
    # that it will be the original secret the dealer shared."

# TODOS:
    # thinking of
    # https://github.com/blockstack/secret-sharing/blob/837f28b88958604866ac1707266d10539d740abf/secretsharing/primes.py
    # for primes but want to run it by Nadia
        # get the same prime for the same secret - is that bad?
        # can I just generate a massive number to pass in and get the prime that way for check vector?

    # thinking of _____ for random values

    # vet and / or write polynomial algorithms
        # https://github.com/blockstack/secret-sharing/blob/837f28b88958604866ac1707266d10539d740abf/secretsharing/polynomials.py
            # take egcd and mod_inverse (standard)
            # write random_polynomial and get_points (can compare after)
            # write modular_lagrange_interpolation based on (can compare after)
                # http://math.stackexchange.com/questions/621406/lagrange-interpolating-polynomial-using-modulo
                # http://www.artofproblemsolving.com/community/c1157h990758

    # input / output will be bytestring (TODO: chat with Doron to avoid mistakes of previous libraries)

        # fix a small prime ps > n such that s is in Z_ps (public)
        # Note that low ps sets an upper bound on s
        # large ps increases the likelihood that f(x) mod p = f(x)
    # sharing_prime = primes.get_prime([num_players, secret])

# parameters:
    # n: number of providers (n >= 2t + 1)
    # t: t players get no info, t + 1 can reconstruct
    # s: the secret
    # k is a security parameter
        # selected so that the probability of error is 2^(-k)
    # ps: a (potentially small) pubic prime used for defining polynomial coefficients
    # pv: a large, private prime used for check vectors

# sharing the secret (Phase 1) -
    # gather shares f(alpha_i)
        # (see sss.py)

    # for each f(alpha_i) generate a check vector
        # (see authentication.py)

    # disperse values to each player, Pi
        # f(alpha_i), the players share
        # y_i1, ..., y_in which the y_ij are the "tags" for Pi
        # (b1i, c_1i), ..., (bni, c_ni)
            # the (b_ji, c_ji) values are used by Pi to authenticate players Pj's tag

# recovering the secret (Phase 2) -
    # TODO: some thinking that needs to be done here
        # this algorithm assumes that all honest players should ultimately be able to agree on the secret
        # we only want the dealer in our case to determine the secret
        # fix: just make the checks below ourselves by requesting info rather than sending it out

    # TODO: how do we ultimately decide on the correct secret, as the dealer?
        # threat model (what can a malicious provider do?)
            # send back a corrupted share
            # send back an invalid tag for their own share
            # send a corrupted key for another provider

        # do we take majority vote or do we need t + 1 to make a vote?

        # what if we get a valid share and tag from a provider but they lie
            # about who else is honest?

    # TODO: is this something we can do for reed-solomon or is there a different solution in that case?

    # retrieve values from all players

    # calculate all pairs (f(alpha_i), y_ij), i != j

    # verify with all (b_ji, c_ji) that c_ji = f(alpha_j) + b_ji y_ji
        # accept or reject accordingly
        # (see authentication.py)

    # if pieces f(alpha_i1), ..., f(alpha_ir), r >= t + 1 are accepted for player Pi
    # then s can be calculated with these r shares
        # (see sss.py)
