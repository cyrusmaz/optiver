from copy import deepcopy
from itertools import permutations, groupby
from functools import reduce
from operator import add
from collections import Counter
from math import isclose
import json

# Given a path, calculate the probability of each player winning
# INPUT: 
#    path: a path of the form {'a':0.2, 'b': 0.5, 'c':0.8,... }
# OUTPUT: the payoff for each player, where payoff is defined 
#         as the probability of the player winning the game 
def payoff_calculator(path):
    sorted_keys=sorted(path, key=path.get)
    output=dict()
    for k in range(len(sorted_keys)):

        if k==0:
            lowbo=0
            upbo=(path[sorted_keys[k]]+path[sorted_keys[k+1]])/2
        elif k==len(sorted_keys)-1:
            lowbo=(path[sorted_keys[k-1]]+path[sorted_keys[k]])/2
            upbo=1
        else: 
            lowbo=(path[sorted_keys[k-1]]+path[sorted_keys[k]])/2
            upbo=(path[sorted_keys[k]]+path[sorted_keys[k+1]])/2
        output[sorted_keys[k]]=upbo-lowbo
    return output

# generate every possible sequence of choices by the first N-1 players 
# INPUTS: 
#   M: determines the choices for players are {i/(M+1) : i=0,1,...,M-1,M,M+1}
#   N: the number of players
# OUTPUT: all possible permutations of choices to play by the
#         first N-1 players
def play_generator(M, N):
    discretized = [x/(M) for x in range(0,M+1)]
    perms = list(permutations(discretized, N-1))
    output = []
    for perm in perms:
        processed_perm = {alphabet[i]:perm[i] for i in range(N-1)}
        output.append(processed_perm)
    return output 

### ALGORITHM 1:
# compute the optimal choice for the N-th player, given a sequence of choices by the first 
# N-1 players
# INPUTS: 
#   path: a path of N-1 plays by the first N-1 players, {'a':0.2, 'b': 0.5, ... }
# OUTPUT: a dictionary consisting of two key/value pairs: 
#   'path_group': a list of dicitonaries of paths that are equal to the input 
#                 path in the first N-1 plays, and have optimal plays by the Nth player
#   'payoff_group': a list of dictionaries of payoffs corresponding to the respective path 
#.                  in the path_group list
def optimal_path_calculator(path):
    letter = alphabet[len(path)]
    vals = list(path.values())
    vals.sort()
    intervals = []
    max_len = 0
    for i in range(len(vals)+1):
        if i==0: lobo=0
        else: lobo=vals[i-1]
            
        if i==(len(vals)): upbo=1
        else: upbo=vals[i]
            
        if not ((i==0) or (i==(len(vals)))):
            length=(upbo-lobo)/2
        elif ((i==0) or (i==(len(vals)))):
            length=upbo-lobo
        
        if i==0:
            lobo='zero'
        elif i==len(vals):
            upbo='one'    
                         
        intervals.append([lobo, upbo, length])
        if length>max_len: max_len=length
            
    intervals=list(filter(lambda x: isclose(x[2],max_len,abs_tol=r), intervals))
    
    path_list = []
    for interval in intervals:
        if interval[0]=='zero':
            path_list.append(min(vals)-e)
            
        elif interval[1]=='one':
            path_list.append(max(vals)+e)
        else: 
            path_list.append((interval[0] + interval[1])/2)
            
    path_group=[]
    payoff_group=[]
    for n in path_list:
        newdict = deepcopy(path)
        newdict[letter]=n
        path_group.append(newdict)
        payoff_group.append(payoff_calculator(newdict))
    
    return {'path_group':path_group, 'payoff_group':payoff_group}

# compute the average payoff for all paths in the group
def payoff_average_calculator(group):
    payoff_group = group['payoff_group']
    payoff_average = dict(reduce(add, map(Counter, payoff_group)))
    payoff_average = {k:v/len(payoff_group)  for k,v in payoff_average.items()}
    group['payoff_average'] = [payoff_average]*len(payoff_group)
    return group

# regroup path_space such that the first k-2 in each group are identical
def regroup(path_space, k):
    path_group_agg = []
    payoff_group_agg = []
    payoff_average_agg = []

    for e in path_space: 
        for path, payoff_group, payoff_average in zip(
            e['path_group'],
            e['payoff_group'],
            e['payoff_average']
            ):
            path_group_agg.append(path)
            payoff_group_agg.append(payoff_group)        
            payoff_average_agg.append(payoff_average)

    trip = zip(path_group_agg, payoff_group_agg, payoff_average_agg)
    l=alphabet[0:k-2]
    print('regrouping such that choices for ({}) in each group are equal'.format(l))
    regrouped_raw=[
        [*j] for i, j in 
            groupby(
                sorted(trip, key=lambda x: [x[0][i] for i in l]), 
                key=lambda x: [x[0][i] for i in l])
            ]

    regrouped = []
    for group in regrouped_raw: 
        path_group = []
        payoff_group = []
        payoff_average = []
        for path in group:
            path_group.append(path[0])
            payoff_group.append(path[1])        
            payoff_average.append(path[2])   
        d=dict(   path_group=path_group, 
                  payoff_group=payoff_group,
                  payoff_average=payoff_average)
        regrouped.append(d)
    return regrouped

# for each group in path_space, discard every path that is suboptimal for player k-1
def optimize_groups(path_space, k):
    letter = alphabet[k-2]
    print('optimizing {}'.format(letter.upper()))
    optimized = []

    for i in range(len(path_space)):
        group = deepcopy(path_space[i])
        seq=[g[letter] for g in group['payoff_average']]
        max_pay = max(seq)
        filtered_group = list(filter(
            lambda x: isclose(x[2][letter],max_pay,abs_tol=r), 
            zip(group['path_group'], group['payoff_group'],group['payoff_average'])
            ))
        filtered_group = list(zip(*filtered_group))
        optimized.append(
            {'path_group': list(filtered_group[0]), 'payoff_group': list(filtered_group[1])})
    return optimized

# recursively carry out the while loop in Algorithm 1
def recursive_solver(path_space, k):
    print("k={}".format(k))
    path_space_withaverage = [payoff_average_calculator(o) for o in path_space]
    path_space_regrouped = regroup(path_space_withaverage, k)
    path_space_optimized_by_group = optimize_groups(path_space_regrouped, k)
    if k==2:
        return [payoff_average_calculator(o) for o in path_space_optimized_by_group]
    else: 
        k-=1
        return recursive_solver(path_space_optimized_by_group,k)

### ALGORITHM 2: 
# wrapper for recursive_solver 
def backwards_solver(M,N, question_1=False, write=False):
    print('M={}'.format(M))
    print('N={}'.format(N))
    path_space = play_generator(M,N)
    
    if question_1 is True:
        path_space = list(filter(lambda x: x['a']==0, path_space))
    else: 
        path_space = list(filter(lambda x: x['a']<=1/2, path_space))

    path_space = [optimal_path_calculator(play) for play in path_space]
    optimal_paths = recursive_solver(path_space,N)

    path_group=optimal_paths[0]['path_group']
    average_payoff = optimal_paths[0]['payoff_average'][0]

    if question_1 is False:
        A = list(set([x['a'] for x in path_group]))
        print('optimal choice(s) for A: {}'.format(A))
        print('average payoff: {}'.format(average_payoff))
        print('optimal paths: {}'.format(path_group))

    elif question_1 is True:
        B = list(set([x['b'] for x in path_group]))
        print('optimal choice(s) for B: {}'.format(B))
        print('average payoff: {}'.format(average_payoff))
        print('optimal paths: {}'.format(path_group))

    if write is True:
        with open('optimal_paths_M{}_N{}_r{}.txt'.format(M,N,r), 'w') as filehandle:
            json.dump(optimal_paths, filehandle)

########################################################################
# e: the minimum allowable epsilon
# r: absolute tolerance when comparing floating points
e = 1/100000
r = e/10
alphabet = ['a', 'b', 'c', 'd']
########################################################################
# QUESTION 3: Optimal choie for player A in four player setting.
backwards_solver(M=100, N=4,question_1=False, write=False)
# optimal choice(s) for A: [0.16]
# average payoff: 
#     {'a': 0.2875, 'd': 0.16999999999999998, 'c': 0.2549999999999999, 'b': 0.2875000000000001}
# optimal paths: [{'a': 0.16, 'b': 0.84, 'c': 0.5, 'd': 0.33}, 
#                 {'a': 0.16, 'b': 0.84, 'c': 0.5, 'd': 0.6699999999999999}]

# backwards_solver(M=127,N=4,question_1=False, write=False)
# optimal choice(s) for A: [0.16535433070866143]
# average payoff: 
     # {'a': 0.29035433070866146, 
     #  'c': 0.24999999999999992, 
     #  'd': 0.1692913385826772, 
     #  'b': 0.29035433070866146}
# optimal paths: [
#      {'a': 0.16535433070866143, 
#       'b': 0.8346456692913385, 
#       'c': 0.49606299212598426, 
#       'd': 0.6653543307086613}, 
#      {'a': 0.16535433070866143, 
#       'b': 0.8346456692913385, 
#       'c': 0.5039370078740157, 
#       'd': 0.3346456692913386}]

# backwards_solver(M=200,N=4,question_1=False, write=False)
# optimal choice(s) for A: [0.165]
# average payoff: {'a': 0.290625, 'd': 0.16749999999999998, 'c': 0.25125, 'b': 0.290625}
# optimal paths: [{'a': 0.165, 'b': 0.835, 'c': 0.5, 'd': 0.3325}, 
#                 {'a': 0.165, 'b': 0.835, 'c': 0.5, 'd': 0.6675}]

########################################################################
# QUESTION 1: Optimal choice for player B when A plays 0. 
# backwards_solver(M=100,N=3,question_1=True, write=False)
# optimal choice(s) for B: [0.67]
# average payoff: {'a': 0.1675, 'c': 0.3350000000000001, 'b': 0.49749999999999994}
# optimal paths: [{'a': 0.0, 'b': 0.67, 'c': 0.335}]

########################################################################
# QUESTION 2: Optimal choie for player A in three player setting.
# backwards_solver(M=100,N=3,question_1=False, write=False)
# optimal choice(s) for A: [0.25]
# average payoff: {'c': 0.24999666666666664, 'a': 0.3750016666666667, 'b': 0.3750016666666667}
# optimal paths: [{'a': 0.25, 'b': 0.75, 'c': 0.24999}, 
#                 {'a': 0.25, 'b': 0.75, 'c': 0.5}, 
#                 {'a': 0.25, 'b': 0.75, 'c': 0.75001}]