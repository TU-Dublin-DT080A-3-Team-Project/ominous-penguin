"""	init_db.py - Use schema.sql to create initial db
	Create a simple database to demonstrate blockchain project"""
import sqlite3

connection = sqlite3.connect('u_base.db')
with open('schema.sql') as f:
	"""Open our created sql schema & execute for initial db structure"""
	connection.executescript(f.read())
	
cur = connection.cursor() #Cursor object for working in db
cur.execute("INSERT INTO users (username, upassword) VALUES (?, ?)",
			('admin', 'secret'))	
cur.execute("INSERT INTO users (username, upassword) VALUES (?, ?)",
			('user1', 'pass1'))
connection.commit() #apply changes
connection.close() #end connection
print("Database Successfully Created!")
