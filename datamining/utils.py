"""
data mining utility code...

the Apriori algorithm implemented here has received absolutely no consideration about efficiency or optimisation - it's fine for small jobs (i.e. finding a set of Mirnov channels to use from a set of a few hundred shots).
"""


def a_is_in_b(a,b):
    return False not in [i in b for i in a]

def get_frequent_itemsets(data, candidates, support_threshold,k):
    frequent_itemsets = []
    supports = []
    for candidate_i,candidate in enumerate(candidates):
        print '[ %d ] get frequent: candidate %d of %d' %(k,candidate_i+1,len(candidates))
        count = 0
        for item in data:
            if a_is_in_b(candidate, item):
                count +=1
        support = float(count)/len(data)
        if support >= support_threshold:
            frequent_itemsets.append(candidate)
            supports.append(support)
    return [frequent_itemsets,supports]
def get_subs(itemset):
    # return all n-1 subsets of a set of length 1
    return [itemset[:i]+itemset[i+1:] for i in range(len(itemset)-1)]
    

def prune(new_candidates, previous_frequent,k):
    pruned = []
    for candidate_i,candidate in enumerate(new_candidates):
        print '[ %d ] pruning: candidate %d of %d' %(k,candidate_i+1,len(new_candidates))
        for candidate_sub in get_subs(candidate):
            ok = False
            for prev in previous_frequent:
                if a_is_in_b(candidate_sub, prev):
                    ok = True
            if not ok:
                pruned.append(candidate)
    for i in pruned:
        new_candidates.remove(i)
    return new_candidates

def get_candidates(previous_frequent,k):
    output = []
    for fi,f in enumerate(previous_frequent[:-1]):
        for gj,g in enumerate(previous_frequent[fi+1:]):
            if f[:k-2] == g[:k-2]:
                tmp = f+[g[-1]]
                output.append(tmp)
    return prune(output, previous_frequent,k)
    
def apriori(data, support = 0.4):
    """
    A rather inefficient implementation of the Apriori algorithm
    """
    candidate_itemsets = {}
    frequent_itemsets = {}
    all_items = []
    for itemset in data:
        for item in itemset:
            if not item in all_items:
                all_items.append(item)
    k=1
    candidate_itemsets[str(k)] = [[i] for i in all_items]
    len_current_candidates = len(candidate_itemsets[str(k)])
    while len_current_candidates > 0:
        #print 'k = %d' %k
        [frequent_itemsets[str(k)],supports] = get_frequent_itemsets(data, candidate_itemsets[str(k)],support,k)
        k+=1
        candidate_itemsets[str(k)] = get_candidates(frequent_itemsets[str(k-1)],k)
        len_current_candidates = len(candidate_itemsets[str(k)])
    for j in range(len(frequent_itemsets[str(k-1)])):
        print frequent_itemsets[str(k-1)], supports[j]

