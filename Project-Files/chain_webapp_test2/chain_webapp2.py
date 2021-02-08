#blockchain.py
import hashlib, json, requests
from time import time, localtime, asctime
from uuid import uuid4
from flask import Flask, jsonify, request, render_template, \
flash, redirect, url_for, make_response, session
import sqlite3
from urllib.parse import urlparse

#-----------------BLOCKCHAIN-CLASS--------------------------------------
class Blockchain(object):
	def __init__(self):
		#Constructor - Create initial lists to store blockchain info
		self.chain = []
		self.current_records = []
		self.new_block(prev_hash=1, proof=100) #Create genesis block		

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

def db_conn():
	"""Establish connection to user database"""
	conn = sqlite3.connect('u_base.db')
	cur = conn.cursor()
	return cur

#Instantiate Flask class and assign name of program
app = Flask(__name__)
app.secret_key = '#Cq2v?g&xs+6yjR$' #required for sessions

#Instantiate Blockchain
blockchain = Blockchain()

#--------------------WEB-PAGES------------------------------------------
@app.route("/") #Homepage
def index():
	session.pop('username', None)
	return render_template('index.html')

@app.route("/full_record")
def full_record():
	data = full_chain()
	return render_template('full_record.html',jsondata=json.dumps(data))
	
@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		username = request.form['username']
		upassword = request.form['password']
		
		cursor = db_conn()
		
		cursor.execute("SELECT * FROM users WHERE username = ? AND upassword = ?", (username, upassword))
		account = cursor.fetchone()
		
		if account:
			session['loggedin'] = True
			session['id'] = account[0]
			session['username'] = account[1]
			return redirect(url_for('add_record'))
		else:
			error = "Incorrect Credentials!"
			return render_template('login.html', error=error)
	return render_template('login.html')
    
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
