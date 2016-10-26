from flask import Flask, render_template
import json


app = Flask(__name__)


@app.route("/")
def index():
	return render_template('index.html')

@app.route("/progress")
def progress():
	with open('static/data/dept_stats.json', 'r') as f:
		return render_template('progress.html', depts=json.loads(f.read()))

@app.route("/help")
def help():
    with open('static/data/concierge_list.json', 'r') as f:
        return render_template('help.html', contacts=json.loads(f.read()))

@app.route("/participate")
def participate():
	with open('static/data/survey_stats.json', 'r') as f:
		return render_template('participate.html', measures=json.loads(f.read()))

if __name__ == "__main__":
	app.run()