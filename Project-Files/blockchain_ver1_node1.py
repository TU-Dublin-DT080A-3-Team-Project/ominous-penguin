#blockchain.py
import hashlib, json, requests
from time import time
from uuid import uuid4
from flask import Flask, jsonify, request
from urllib.parse import urlparse

class Blockchain(object):
	def __init__(self):
		#Constructor - Create initial lists to store blockchain info
		self.chain = []
		self.current_transactions = []
		
		#Create genesis block
		self.new_block(prev_hash=1, proof=100)
		
		self.nodes = set()#Will contain list of unique P2P net nodes
		
	def register_node(self, address):
		"""
		Add new node to P2P net
		<str> address - address of node
		"""
		
		parsed_url = urlparse(address)
		self.nodes.add(parsed_url.netloc)
		
	def valid_chain(self, chain):
		"""
		Determine the authoritative blockchain - (Longest)
		<list> chain - Inputted blockchain
		"""
		
		last_block = chain[0]#Starting point in blockchain
		current_index = 1
		
		while current_index < len(chain):
			block = chain[current_index]
			print(f'{last_block}')
			print(f'{block}\n*************\n')
			
			#Check hash of the block
			if block['prev_hash'] != self.hash(last_block):
				return False
				
			#Check if PoW is correct
			if not self.valid_proof(last_block['proof'], block['proof']):
				return False
				
			last_block = block
			current_index += 1
			
		return True
		
		
	def resolve_conflicts(self):
		"""
		Consensus Algorithm - Will replace current blockchain 
		with longest among connected network nodes.
		"""
		
		neighbours = self.nodes
		new_chain = None
		
		#Don't consider chains shorter than local chain
		max_length = len(self.chain)
		
		#Download + Verify chains from all nodes in network
		for node in neighbours:
			response = requests.get(f'http://{node}/chain')
			
			if response.status_code == 200:
				length = response.json()['length']
				chain = response.json()['chain']
				
				#Check length and validity of chain
				if length > max_length and self.valid_chain(chain):
					max_length = length
					new_chain = chain
				
		#Replace local chain if valid chain exists
		if new_chain:
			self.chain = new_chain
			return True
							
		return False
		
		
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
		
	
	@staticmethod #Doesn't require class instantiation to run
	def hash(block):
		"""
		Create a SHA256 hash from block
		<dict> block - See block format defined in new_block() 
		"""
		
		#Order the dictionary so hashes remain consistent
		block_string = json.dumps(block, sort_keys=True).encode()
		return hashlib.sha256(block_string).hexdigest()
		
		
	def proof_of_work(self, last_proof):
		"""
		Simple Proof of Work Algorithm
		- Find a number p' such that hash(pp') contains 4 leading zeroes
		, where p is the previous p'
		- p is the previous proof, and p' is the new proof
		<int> last_proof - 
		"""
		
		proof = 0
		while self.valid_proof(last_proof, proof) is False:
			proof += 1
			
		return proof
		
		
	@staticmethod
	def valid_proof(last_proof, proof):
		"""
		Validate proof:does hash(last_proof, proof) have 4 leading 0s?
		<int> last_proof - previous proof
		<int> proof - current proof
		"""
		
		guess = f'{last_proof}{proof}'.encode()
		guess_hash = hashlib.sha256(guess).hexdigest()
		return guess_hash[:4] == "0000"

#----------------------END-OF-CLASS-------------------------------------


#Instantiate Flask class and assign name of program
app = Flask(__name__)

#Generate globally unique address for node
node_id = str(uuid4()).replace('-', '')

#Instantiate Blockchain
blockchain = Blockchain()


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
	values = request.get_json()
	
	nodes = values.get('nodes')
	if nodes is None:
		return "Error! Please supply a valid list of nodes", 400
		
	for node in nodes:
		blockchain.register_node(node)
		
	response = {
		'message': 'New nodes have been added!',
		'total_nodes': list(blockchain.nodes),
	}
	return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
	replaced = blockchain.resolve_conflicts()
	
	if replaced:
		response = {
			'message': 'Local Chain Was Replaced!',
			'new_chain': blockchain.chain
		}
	else:
		response = {
			'message': 'Local Chain Is The Authority!',
			'chain': blockchain.chain
		}
		
	return jsonify(response), 200


#Creating a new block
@app.route('/create', methods=['GET'])
def create():
	#Run PoW to get next proof
	last_block = blockchain.last_block
	last_proof = last_block['proof']
	proof = blockchain.proof_of_work(last_proof)
	
	#Reward for finding proof
	blockchain.new_transaction(
		sender = '0', #Rewarded by blockchain itself
		recipient = node_id,
		amount = 1,
	)
	
	#Create new block by adding to chain
	prev_hash = blockchain.hash(last_block)
	block = blockchain.new_block(proof, prev_hash)
	
	response = {
		'message': "New Block Created!",
		'index': block['index'],
		'transactions': block['transactions'],
		'proof': block['proof'],
		'prev_hash': block['prev_hash']
	}
	
	return jsonify(response), 200
	
	
#Adding a new transaction
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
	vals = request.get_json()
	
	#Check required fields are in POST data
	req = ['sender', 'recipient', 'amount']
	if not all(x in vals for x in req):
		return 'Missing Required Values!', 400
		
	#Create new transaction
	i = blockchain.new_transaction(vals['sender'], vals['recipient'],
	vals['amount'])
	
	response = {'message':f'Transaction added to block: {i}'}
	return jsonify(response), 201
	
	
#Return the full blockchain
@app.route('/chain', methods=['GET'])
def full_chain():
	response = {
		'chain': blockchain.chain,
		'length': len(blockchain.chain),
	}
	return jsonify(response), 200
	
	
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=6666)
