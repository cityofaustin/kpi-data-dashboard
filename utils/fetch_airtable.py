import requests
# import configparser
import json
import os
# import logger

# logging.getLogger()

# config = configparser.ConfigParser()
# config.read('secrets.txt')
# airtable_api_key = config['airtable']['api_key']

def get_survey_status():
    # config = configparser.ConfigParser()
    # config.read('secrets.txt')
    # airtable_api_key = config['airtable']['api_key']
    airtable_api_key = os.environ['AIRTABLE_API_KEY']
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
    print('wrote updated survey stats file.')

    # calculate dept-level stats for progress table
    dept_stats = {}
    for k,v in survey_stats.items():
        dept = k
        num_measures = len(v)
        verified = []
        for i in v:
            if i['status'] == 'verified':
                verified.append(1)
            num_verified = sum(verified)
    
        d = {dept: {'num_measures': num_measures, 'num_verified': num_verified, 'status': ''}}
        dept_stats.update(d)

    print(dept_stats)

    print(str(len(dept_stats)) + ' records added to new dept_stats object')

    for k,v in dept_stats.items():
        if v['num_verified'] == v['num_measures']:
            v['status'] = 'completed'
            print('another dept marked completed')
        elif v['num_verified'] > 0:
            v['status'] = 'in progress'
            print('another dept marked in progress')


    # write updated dept stats to json so it can get picked up by routes.py:
    with open('static/data/dept_stats.json', 'w') as outfile:
        json.dump(dept_stats, outfile, sort_keys=True, indent=4)
        print('dept stats written to json')


if __name__ == '__main__':
    get_survey_status()
