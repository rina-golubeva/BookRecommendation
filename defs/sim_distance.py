def sim_distance(prefs, person1, person2):
    # get the list of shared items
    si = {}
    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item] = 1

    # if no ratings in common, return 0
    if len(si) == 0:
        return 0

    # add up the squares of all the differences
    sum_of_squares = sum([pow(prefs[person1][item] - prefs[person2][item], 2)
                          for item in prefs[person1] if item in prefs[person2]])
    return 1/(1 + sum_of_squares) # between (0, 1)
