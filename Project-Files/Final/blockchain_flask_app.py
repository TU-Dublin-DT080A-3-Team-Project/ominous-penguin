"""blockchain.py - webapp program for blockchain implementation
Imports described in project report
Database obtained from init_db.py"""

import hashlib, json, requests, sqlite3
from time import time, localtime, asctime
from flask import Flask, jsonify, request, render_template, \
flash, redirect, url_for, make_response, session

class Blockchain(object):
	"""Blockchain Class"""
	def __init__(self):
		#Constructor - Create initial lists to store blockchain info
		self.chain = [] #Stores entire blockchain
		self.current_records = [] #Temporary record storage
		self.new_block(prev_hash=1, proof=100) #Create genesis block		

	def new_block(self, proof, prev_hash=None):
		"""Create new block in blockchain
		<int> proof - value given by PoW algorithm
		<str> prev_hash - Hash value of previous block, 
		default value for genesis block overload"""
		
		block = {
			'block': len(self.chain) + 1, #++ position in blockchain
			'timestamp': asctime(localtime(time())), #Stamp current time
			'records': self.current_records,
			'proof': proof, #See proof_of_work()
			'prev_hash': prev_hash or self.hash(self.chain[-1])
		}
		
		#Reset current list of transactions & add to next block in chain
		self.current_records = []
		self.chain.append(block)
		return block #<dict>
		
	def new_record(self, car_model, chassis_number, mileage):
		"""Creates new record for next subsequent block
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
		return self.chain[-1] #<dict>
	
	@staticmethod #Doesn't require class instantiation to run
	def hash(block):
		"""Create a SHA256 hash from block
		<dict> block - See block format defined in new_block()
		Covert block to json string, then to bytes with encode()
		and hash it using SHA256, returning it as hex string with
		hexdigest()"""	
		#Order the dictionary so hashes remain consistent
		block_string = json.dumps(block, sort_keys=True).encode()
		return hashlib.sha256(block_string).hexdigest() #<str>
		
	def proof_of_work(self, last_proof):
		"""Simple Proof of Work Algorithm
		<int> last_proof - Proof of last block
		- y is the previous proof, and x is the new proof
		- Find number x such that hash(str(yx))contains 4 leading 0's"""
		
		proof = 0
		while self.valid_proof(last_proof, proof) is False:
			proof += 1 #++ until solution is found
		return proof #<int>
			
	@staticmethod
	def valid_proof(last_proof, proof):
		"""Validate proof: hash(last_proof, proof) have 4 leading 0s?
		<int> last_proof - previous proof
		<int> proof - current proof"""
		guess = f'{last_proof}{proof}'.encode() #str(yx) to bytes
		guess_hash = hashlib.sha256(guess).hexdigest()
		#check if guess hash starts with 0000
		return guess_hash[:4] == "0000" #<bool>
#----------------------END-OF-CLASS-------------------------------------

#--------------BLOCKCHAIN-METHODS---------------------------------------
def create():
	"""Perform PoW, add new block to chain, & return response"""
	#Run PoW to get next proof
	last_block = blockchain.last_block
	last_proof = last_block['proof']
	proof = blockchain.proof_of_work(last_proof)
	
	#Create new block by adding to chain
	prev_hash = blockchain.hash(last_block)
	block = blockchain.new_block(proof, prev_hash)
	
	response = { #return response to HTML client
		'message': "New Block Created!",
		'block': block['block'],
		'records': block['records'],
		'proof': block['proof'],
		'prev_hash': block['prev_hash']
	}
	return response #<dict>
	
def new_record(car_model, chass_num, mileage):
	"""Create new record & return message to client"""
	i = blockchain.new_record(car_model, chass_num, mileage)
	response = {'message':f'Information added to block!'}
	return response #<dict>
	
def full_chain():
	"""Return full blockchain"""
	response = {
		'Vehicle Mileage Blockchain': blockchain.chain,
		'Total Blocks': len(blockchain.chain)
	}
	return response #<dict>
#-----------------------------------------------------------------------

def db_conn():
	"""Establish connection to user database"""
	conn = sqlite3.connect('u_base.db')
	cur = conn.cursor() #create database cursor object
	return cur #<sqlite3.Cursor>

#Instantiate Flask class and assign name of program
app = Flask(__name__)
app.secret_key = '#Cq2v?g&xs+6yjR$' #required for flask login

#Instantiate Blockchain
blockchain = Blockchain()

#--------------------WEB-PAGES------------------------------------------
@app.route("/")
def index():
	"""Homepage"""
	return render_template('index.html')

@app.route("/full_record")
def full_record():
	"""Full Blockchain Page"""
	data = full_chain() #Convert this to JSON for display in HTML Page
	return render_template('full_record.html',jsondata=json.dumps(data))
	
@app.route('/login', methods=['GET', 'POST'])
def login():
	"""Login Page"""
	error = None #incorrect credentials result in error message
	if request.method == 'POST' and 'username' in request.form \
	and 'password' in request.form: #both user & pass fields required
		username = request.form['username']
		upassword = request.form['password']
		
		cursor = db_conn()
		
		#Try to match info with database
		cursor.execute \
		("SELECT * FROM users WHERE username = ? AND upassword = ?", \
		(username, upassword))
		account = cursor.fetchone()
		
		if account: #if account exists
			return redirect(url_for('add_record'))
		else: #back to login + display err msg
			error = "Incorrect Credentials!"
			return render_template('login.html', error=error)
	return render_template('login.html')
    
@app.route('/add_record', methods=['GET', 'POST'])
def add_record():
	"""Add record page"""
	error = None
	if request.method == 'POST':
		# If any fields are blank
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
	"""Add block page"""
	data = create() #Run create() blockchain method
	return render_template('add_block.html',jsondata=json.dumps(data))

#-----------------------------------------------------------------------
if __name__ == '__main__':
	app.run()
