from flask import Flask, render_template
import json


app = Flask(__name__)

@app.route("/")
def index():
	with open('data/current_progress.json', 'r') as f:
		return render_template('index.html', depts=json.loads(f.read()))

@app.route("/about")
def about():
	return render_template('about.html')

@app.route("/find")
def find_page():
	return render_template('find.html')

if __name__ == "__main__":
	app.run(debug=True)