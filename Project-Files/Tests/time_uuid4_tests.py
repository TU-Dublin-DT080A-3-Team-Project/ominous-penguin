from uuid import uuid4
from time import time

print("UUID4 TEST\n--------------------------")
#Create 5 random values
for x in range(5):
	node_id = str(uuid4()).replace('-', '')
	print(f"Unique ID {x}", node_id)
	
print("\n\nTIME TEST\n---------------------------")
print(f"Timestamp: {time()}")

