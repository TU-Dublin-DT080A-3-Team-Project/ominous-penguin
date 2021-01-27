"""
Proof of work (PoW) is a form of cryptographic zero-knowledge proof in 
which one party (the prover) proves to others (the verifiers) that a 
certain amount of computational effort has been 
expended for some purpose. -https://en.wikipedia.org/wiki/Proof_of_work

We will use this PoW algorithm as part of creating new blocks on the
blockchain
"""

from hashlib import sha384
from hashlib import blake2b

x, y = 5, 0

"""Here we will brute-force what number y needs to equal for the 
generated hash to end in 0. The resulting hash value will always be 
the same using this number for y.
"""

#Test with BLAKE2B
print("Looking for first blake2b hash ending with f...")
while blake2b(f'{x*y}'.encode()).hexdigest()[-1] != "f":
	print(f"Value when y = {y}\t"+ blake2b(f'{x*y}'.encode()).hexdigest())
	y += 1
	
print("\n\n"+ blake2b(f'{x*y}'.encode()).hexdigest())
print(f'The solution is y = {y}')

#Test with SHA384
x, y = 5, 0
print("\n\nLooking for first SHA384 hash ending with f...")
while sha384(f'{x*y}'.encode()).hexdigest()[-1] != "f":
	print(f"Value when y = {y}\t"+ sha384(f'{x*y}'.encode()).hexdigest())
	y += 1
	
print("\n\n"+ sha384(f'{x*y}'.encode()).hexdigest())
print(f'The solution is y = {y}')
