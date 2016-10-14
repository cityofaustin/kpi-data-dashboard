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
	with open('data/survey_stats.json', 'r') as f:
		return render_template('find.html', measures=json.loads(f.read()))

if __name__ == "__main__":
	app.run(debug=True)