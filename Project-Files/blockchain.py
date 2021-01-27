#blockchain.py
import hashlib, json
from time import time


class Blockchain(object):	
	def __init__(self):
		#Constructor - Create initial lists to store blockchain info
		self.chain = []
		self.current_transactions = []
		
		#Create genesis block
		self.new_block(previous_hash=1, proof=100)
		
		
	def new_block(self, proof, prev_hash=None):
		"""
		Create new block in blockchain
		<int> proof - value given by PoW algorithm
		<str> prev_hash - Hash value of previous block, optional
		"""
		
		block = {
			'index': len(self.chain) + 1, #++ position in blockchain
			'timestamp': time(), #Stamp current time
			'transactions': self.current_transactions,
			'proof': proof,
			'prev_hash': prev_hash or self.hash(self.chain[-1])
		}
		
		#Reset current list of transactions
		self.current_transactions = []
		
		self.chain.append(block)
		return block
		
		
	def new_transaction(self, sender, recipient, amount):
		"""
		Creates new transaction for next subsequent block
		<str> sender - Address of Sender
		<str> recipient - Address of Recipient
		<int> amount - Transaction Amount
		"""
		
		self.current_transactions.append({
			'sender':sender, 
			'recipient':recipient,
			'amount':amount,
		})
		
		#Return index of block the transaction will be added to i.e next
		return self.last_block['index'] + 1 #<int>
		
		
	@property #Shorthand GETTER, no need to assign self.chain to view
	def last_block(self):
		return self.chain[-1]
		
	
	@staticmethod
	def hash(block):
		"""
		Create a SHA256 hash from block
		<dict> block - See block format defined in new_block() 
		"""
		
		#Order the dictionary so hashes remain consistent
		block_string = json.dumps(block, sort_keys=True).encode()
		return hashlib.sha256(block_string).hexdigest()
