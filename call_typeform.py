import requests
import configparser
import json
import os

config = configparser.ConfigParser()
config.read('secrets.txt')
form_id = config['typeform.com']['form_id']
api_key = config['typeform.com']['api_key']

r = requests.get(
    'https://api.typeform.com/v1/form/'+form_id+'?key='+api_key)

with open('data/tmp/responses.tmp.json', 'w') as f:
	j = r.json()
	d = json.dumps(j)
	f.write(d)

os.rename('data/tmp/responses.tmp.json', 'data/tmp/responses.json')

if __name__ == "__main__":
	app.run(debug=True)