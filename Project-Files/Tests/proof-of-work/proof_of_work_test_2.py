from hashlib import sha384
from hashlib import blake2b

"""
Extention of previous test, in this case we are testing if 
hash begins with certain characters
"""

x, y = 8, 0
print("\n\nLooking for first SHA384 hash starting with ee...")
while sha384(f'{x*y}'.encode()).hexdigest()[:2] != "ee":
	print(f"Value when y = {y}\t"+ sha384(f'{x*y}'.encode()).hexdigest())
	y += 1
	
print("\n\n"+ sha384(f'{x*y}'.encode()).hexdigest())
print(f'The solution is y = {y}')



x, y = 8, 0
print("\n\nLooking for first BLAKE2B hash starting with ee...")
while blake2b(f'{x*y}'.encode()).hexdigest()[:2] != "ee":
	print(f"Value when y = {y}\t"+ blake2b(f'{x*y}'.encode()).hexdigest())
	y += 1
	
print("\n\n"+ blake2b(f'{x*y}'.encode()).hexdigest())
print(f'The solution is y = {y}')
