def topMatches(prefs, person, n = 5, similarity = sim_pearson):
    '''Return the best matches for person from the prefs dictionary.'''
    scores = [(round(similarity(prefs, person, other), 5), other)
              for other in prefs if other != person]
    # sort the list so the highest scores appear at the top
    scores.sort(reverse = True)
    return scores[0:n]
