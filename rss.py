# Implementation of the Rabin Ben-Or Robust Secret Sharing scheme

# generate shares of the secret s: (s_1, . . . , s_n)
    # see sss.py

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
