import itertools

def P_B_wins(A,B):
    if (B<=1/2) and (A>B):
        return (B+A)/2
    if (B<=1/2) and (A<B):
        return (B-A)/2
    if (B>1/2) and (max(A,1-B,(B-A)/2)==1-B):
        return (B-A)/2
    if (B>1/2) and (max(A,1-B,(B-A)/2)==A):        
        return 1-(B+A)/2
    if (B>1/2) and (max(A,1-B,(B-A)/2)==(B-A)/2):  
        return 1-3/4*B-A/4
    if (B==A): return 0
    
def P_A_wins(A,B):
    if (B<=1/2) and (A>B):
        return (B-A)/2
    if (B<=1/2) and (A<B):
        return (B+A)/2
    if (B>1/2) and (max(A,1-B,(B-A)/2)==1-B):
        return (B-A)/2
    if (B>1/2) and (max(A,1-B,(B-A)/2)==A):        
        return (B-A)/2
    if (B>1/2) and (max(A,1-B,(B-A)/2)==(B-A)/2):  
        return A/2+(B+A)/4
    if (B==A): return 0
    
mesh_width = 1000
A_vals = [x/mesh_width for x in range(int(mesh_width/2)+1)]
B_vals = [x/mesh_width for x in range(int(mesh_width)+1)]
grid = list(itertools.product(A_vals, B_vals))

Tilde_B = []
for A in A_vals:
    val=[P_B_wins(A,B) for B in B_vals]
    max_val = max(val)
    max_index = [i for i, j in enumerate(val) if j == max_val]
    Tilde_B.append(B_vals[max_index[0]])

Tilde_A = [dict(A=a,P_A_wins=P_A_wins(a,b)) for a,b in zip(A_vals, Tilde_B)]
seq = [p['P_A_wins'] for p in Tilde_A]
max_seq=max(seq)
Tilde_A = list(filter(lambda x: x['P_A_wins']==max_seq, Tilde_A))
print(Tilde_A)

# [{'A': 0.25, 'P_A_wins': 0.37525}]