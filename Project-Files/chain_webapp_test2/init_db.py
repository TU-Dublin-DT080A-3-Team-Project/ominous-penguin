#init_db.py - Use schema.sql to create initial db
import sqlite3

connection = sqlite3.connect('u_base.db')

with open('schema.sql') as f:
	connection.executescript(f.read())
	
cur = connection.cursor()

cur.execute("INSERT INTO users (username, upassword) VALUES (?, ?)",
			('admin', 'secret')
			)
				
cur.execute("INSERT INTO users (username, upassword) VALUES (?, ?)",
			('user1', 'pass1')
			)

connection.commit()
connection.close()
