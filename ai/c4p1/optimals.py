def optimal(col):
    """ return the 6x7 array of the optimal game for the 0th or 1st turn\n
    col is either the opponent's first move 0-6, or -1 if we're going first """
    if col == -1: # go first win optimal
        return [[2,2,1,1,2,2,2],[1,1,2,2,1,1,1],[2,2,1,1,2,2,2],[1,1,2,2,1,2,1],[2,2,1,1,1,1,1],[1,1,2,1,2,0,2]]
    if col == 3: # go second lose optimally
        return [[2,2,1,1,2,2,2],[1,1,2,2,1,1,1],[2,2,1,1,2,2,2],[1,1,2,2,1,2,1],[2,2,1,1,1,0,1],[1,1,2,1,2,0,2]]
    if col == 0 or col == 6: # go second win bc opp bad
        reg = [[1,1,1,2,1,2,1],[2,2,2,1,1,1,2],[1,1,2,2,2,1,1],[2,2,1,1,1,2,2],[1,1,1,2,0,1,2],[2,2,2,2,0,2,1]]
        return reg if col == 0 else [i[::-1] for i in reg]
    if col == 1 or col == 5:
        reg = [[1,1,2,1,1,1,2],[1,2,1,2,2,2,1],[2,2,2,1,1,2,2],[2,1,1,2,2,1,1],[1,1,2,1,1,1,2],[2,1,2,2,2,2,1]]
        return reg if col == 1 else [i[::-1] for i in reg]
    if col == 2 or col == 4:
        reg = [[1,2,1,1,1,2,2],[1,2,1,2,2,1,1],[2,2,2,1,1,1,2],[1,1,1,2,2,2,1],[1,2,2,1,1,1,2],[2,2,1,1,2,2,2]]
        return reg if col == 2 else [i[::-1] for i in reg]