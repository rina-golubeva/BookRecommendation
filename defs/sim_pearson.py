def sim_pearson(prefs, p1, p2):
    # get the list of shared items
    si = {}
    for item in prefs[p1]:
        if item in prefs[p2]:
            si[item] = 1

    # find the number of elements
    n = len(si)

    # if no ratings in common, return 0
    if len(si) == 0:
        return 0

    # add up all the preferences
    sum1 = sum([prefs[p1][item] for item in si])
    sum2 = sum([prefs[p2][item] for item in si])

    # sum up the squares
    sum1Sq = sum([pow(prefs[p1][item], 2) for item in si])
    sum2Sq = sum([pow(prefs[p2][item], 2) for item in si])

    # sum up the products
    pSum = sum([prefs[p1][item] * prefs[p2][item] for item in si])

    # calculate Pearson score
    num = pSum - (sum1 * sum2)/n
    den = sqrt((sum1Sq - pow(sum1, 2)/n) * (sum2Sq - pow(sum2, 2)/n))
    if den == 0:
        return 0
    else:
        return num/den # between(-1, 1)
