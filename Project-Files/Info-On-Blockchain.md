# This file can be used to store any information relating to blockchains & cryptocurrency that we can use for our project report ###
Ensure sources are referenced etc...


## Format of single block within blockchain:
---
block = {

  'INDEX' - Positional index in blockchain
  
  'TIMESTAMP' - Timestamp allocated to transaction
  
  'TRANSACTION'{
  
    'SENDER' - Address of Sender
    
    'RECIPIENT' - Address of Recipient
    
    'AMOUNT' - Transaction Amount}
  
  'PROOF' - Produced by Proof of Work Algorithm
  
  'PREVIOUS-HASH' - Hash Value of previous block (Important for blockchain integrity)
  
}


## Genesis Block
When our Blockchain is instantiated we’ll need to seed it with a genesis block — a block with no predecessors

We’ll also need to add a “proof” to our genesis block which is the result of mining (or proof of work)
