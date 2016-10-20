import requests
import configparser
import json
import os
# import logger

# logging.getLogger()

config = configparser.ConfigParser()
config.read('secrets.txt')
airtable_api_key = config['airtable']['api_key']
form_id = config['typeform.com']['form_id']
typeform_api_key = config['typeform.com']['api_key']

def get_survey_status():
    config = configparser.ConfigParser()
    config.read('secrets.txt')
    airtable_api_key = config['airtable']['api_key']
    survey_status = {}
    groups = ['1', '2', '3']
    for i in groups:
        url = 'https://api.airtable.com/v0/apprncjzrsX5xkKCA/measures%20list?view=group' + i
        headers = {'authorization': airtable_api_key}
        r = requests.get(url, headers=headers, verify=False)
        j = r.json()
        for d in j['records']:
            x = {d['fields']['measure_id']: d['fields']['survey_status']}
            survey_status.update(x)

    # read in the previous measure_stats already published to airtable
    with open('static/data/survey_stats.json', 'r') as f:
        survey_stats = json.loads(f.read())

    # update the measure_stats with the most recent status
    for k,v in survey_stats.items():
    	for i in v:
    		i['status'] = survey_status[i['id']]

    # write the updated object back json for safe keeping and provision to routes.py
    with open('static/data/survey_stats.json', 'w') as outfile:
        json.dump(survey_stats, outfile, sort_keys=True, indent=4)


if __name__ == '__main__':
    get_survey_status()
