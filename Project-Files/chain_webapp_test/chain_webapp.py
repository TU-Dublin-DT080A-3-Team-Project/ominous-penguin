#blockchain.py
import hashlib, json, requests
from time import time, localtime, asctime
from uuid import uuid4
from flask import Flask, jsonify, request, render_template, \
flash, redirect, url_for, make_response
from urllib.parse import urlparse

class Blockchain(object):
	def __init__(self):
		#Constructor - Create initial lists to store blockchain info
		self.chain = []
		self.current_records = []
		self.new_block(prev_hash=1, proof=100) #Create genesis block		
		self.nodes = set()#Will contain list of unique P2P net nodes
		
	def register_node(self, address):
		"""Add new node to P2P net, <str> address - address of node"""
		parsed_url = urlparse(address)
		self.nodes.add(parsed_url.netloc)
		
	def valid_chain(self, chain):
		"""Determine the authoritative blockchain - (Longest)
		<list> chain - Inputted blockchain"""
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
			if not self.valid_proof(last_block['proof'],block['proof']):
				return False
				
			last_block = block
			current_index += 1	
		return True
		
	def resolve_conflicts(self):
		"""Consensus Algorithm - Will replace current blockchain 
		with longest among connected network nodes."""
		
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
		"""Create new block in blockchain
		<int> proof - value given by PoW algorithm
		<str> prev_hash - Hash value of previous block, optional"""
		
		block = {
			'block': len(self.chain) + 1, #++ position in blockchain
			'timestamp': asctime(localtime(time())), #Stamp current time
			'records': self.current_records,
			'proof': proof,
			'prev_hash': prev_hash or self.hash(self.chain[-1])
		}
		
		#Reset current list of transactions
		self.current_records = []
		self.chain.append(block)
		return block
		
	def new_record(self, car_model, chassis_number, mileage):
		"""Creates new transaction for next subsequent block
		<str> car_model - Model (Make) of Car
		<str> chassis_number - Unique chass number of vehicle
		<int> mileage - mileage in km"""
		
		self.current_records.append({
			'car_model':car_model, 
			'chassis_number':chassis_number,
			'mileage':mileage,
		})
		#Return index of block the transaction will be added to i.e next
		return self.last_block['block'] + 1 #<int>
		
	@property #Shorthand GETTER, no need to assign self.chain to view
	def last_block(self):
		return self.chain[-1]
	
	@staticmethod #Doesn't require class instantiation to run
	def hash(block):
		"""Create a SHA256 hash from block
		<dict> block - See block format defined in new_block() """	
		#Order the dictionary so hashes remain consistent
		block_string = json.dumps(block, sort_keys=True).encode()
		return hashlib.sha256(block_string).hexdigest()
		
	def proof_of_work(self, last_proof):
		"""Simple Proof of Work Algorithm
		- Find a number p' such that hash(pp') contains 4 leading zeroes
		, where p is the previous p'
		- p is the previous proof, and p' is the new proof
		<int> last_proof - Proof of last block"""
		proof = 0
		while self.valid_proof(last_proof, proof) is False:
			proof += 1	
		return proof
		
	@staticmethod
	def valid_proof(last_proof, proof):
		"""Validate proof: hash(last_proof, proof) have 4 leading 0s?
		<int> last_proof - previous proof
		<int> proof - current proof"""
		guess = f'{last_proof}{proof}'.encode()
		guess_hash = hashlib.sha256(guess).hexdigest()
		return guess_hash[:4] == "0000"
#----------------------END-OF-CLASS-------------------------------------


#Instantiate Flask class and assign name of program
app = Flask(__name__)
app.secret_key = 'some_secret'

#Generate globally unique address for node
node_id = str(uuid4()).replace('-', '')

#Instantiate Blockchain
blockchain = Blockchain()


#--------------------WEB-PAGES------------------------------------------
@app.route("/")
def index():
	return render_template('index.html')

@app.route("/full_record")
def full_record():
	data = full_chain()
	return render_template('full_record.html',jsondata=json.dumps(data))
	
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or \
                request.form['password'] != 'secret':
            error = 'Invalid credentials!'
        else:
            return redirect(url_for('add_record'))
    return render_template('login.html', error=error)
    
@app.route('/add_record', methods=['GET', 'POST'])
def add_record():
	error = None
	if request.method == 'POST':
		if request.form['car_model'] == "" or \
		request.form['chassis_number'] == "" or \
		request.form['mileage'] == "":
			error = "Please Enter Required Details!"
		else:
			response = new_record(request.form['car_model'], \
			request.form['chassis_number'], request.form['mileage'])
			flash('Record Successfully Created!')
	return render_template('add_record.html', error=error)
	
@app.route('/add_block', methods=['GET'])
def add_block():
	data = create()
	return render_template('add_block.html',jsondata=json.dumps(data))

#-----------------------------------------------------------------------

#--------------------NODE-METHODS---------------------------------------
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
#-----------------------------------------------------------------------

#--------------BLOCKCHAIN-METHODS---------------------------------------
def create():
	#Run PoW to get next proof
	last_block = blockchain.last_block
	last_proof = last_block['proof']
	proof = blockchain.proof_of_work(last_proof)
	
	#Create new block by adding to chain
	prev_hash = blockchain.hash(last_block)
	block = blockchain.new_block(proof, prev_hash)
	
	response = {
		'message': "New Block Created!",
		'block': block['block'],
		'records': block['records'],
		'proof': block['proof'],
		'prev_hash': block['prev_hash']
	}
	return response
	
#Creating a new Record
def new_record(car_model, chass_num, mileage):
	i = blockchain.new_record(car_model, chass_num, mileage)
	response = {'message':f'Information added to block!'}
	return response
	
#Return the full blockchain
def full_chain():
	response = {
		'Vehicle Mileage Blockchain': blockchain.chain,
		'length': len(blockchain.chain)
	}
	return response
#-----------------------------------------------------------------------
	
if __name__ == '__main__':
	app.run()
