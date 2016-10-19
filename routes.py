from flask import Flask, render_template
import requests
import json


app = Flask(__name__)


@app.route("/")
def index():
	return render_template('index.html')

@app.route("/progress")
def progress():
	with open('data/dept_stats.json', 'r') as f:
		return render_template('progress.html', depts=json.loads(f.read()))

@app.route("/help")
def help():
	return render_template('help.html')

@app.route("/participate")
def participate():
	with open('data/survey_stats.json', 'r') as f:
		return render_template('participate.html', measures=json.loads(f.read()))
	

if __name__ == "__main__":
	app.run()