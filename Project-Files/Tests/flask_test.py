from flask import Flask
app = Flask(__name__)

#route decorator denotes what URL triggers the function
@app.route('/') #root or 'homepage'
def hello_world():
	return '<h1>Hello World!</h1>'
	
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5555)

#After this search '127.0.0.1:6660' in web browser to view message
