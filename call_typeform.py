import requests
import configparser
import json
import os

# call typeform and write repsonses to json

config = configparser.ConfigParser()
config.read('secrets.txt')
form_id = config['typeform.com']['form_id']
api_key = config['typeform.com']['api_key']

r = requests.get(
    'https://api.typeform.com/v1/form/'+form_id+'?key='+api_key)

with open('data/tmp/responses.tmp.json', 'w') as f:
	d = r.json()
	j = json.dumps(d)
	f.write(j)

os.rename('data/tmp/responses.tmp.json', 'data/tmp/responses.json')

print(str(len(d['responses'])) + ' responses fetched and written to /data/tmp/responses.json')

# filter out the incomplete responses and fake departments

dept_filter = ['Austin Energy', 'Animal Services', 'Austin Transportation', 'Aviation', 'Building Services', 'Office of the City Clerk', 'Austin Code', 'Austin Convention Center', 'Communication and Technology Management', 'Development Services', 'Economic Development', 'Emergency Medical Services', 'Fire', 'Fleet Services', 'Financial Services', 'Government Relations', 'Health and Human Services', 'Human Resources', 'Law', 'Austin Public Library', 'Labor Relations', 'Municipal Court', 'Management Services', 'Neighborhood Housing and Community Development', 'Office of the City Auditor', 'Office of the Medical Director', 'Office of Real Estate Services', 'Planning and Zoning', 'Communications and Public Information', 'Police', 'Parks and Recreation', 'Public Works', 'Small and Minority Business Resources', 'Austin Resource Recovery', 'Telecommunications and Regulatory Affairs', 'Watershed Protection', 'Austin Water']

  # grab all completed surveys from api data, filter out the ones that aren't from a valid dept name
responses_completed = []
c = -1
for i in d['responses']:
    if i['completed'] == '1' and i['hidden']['dept'] in dept_filter and len(i['answers']) != 0:
        w = {}
        c = c + 1
        w = {'token': i['token'], 'contact': i['hidden']['contact'], 'm_id': i['hidden']['m_id'], 'dept': i['hidden']['dept'], 'started': i['metadata']['date_land'], 'submitted': i['metadata']['date_submit'], 'network_id': i['metadata']['network_id']}
        for k,v in i['answers'].items():
            w.update({k: v})
        responses_completed.append(w)

  # write valid responses to json for safekeeping
with open('data/completed_responses.json', 'w') as outfile:
    json.dump(responses_completed, outfile, sort_keys=True, indent=4)

print(str(c) + ' valid responses identified and written to data/completed_responses.json')

# bring in the last survey stats data snapshot:

with open('data/survey_stats.json', 'r') as infile:
    stats = json.load(infile)

# determine the completed survey counts per measure id:

counts = {}
for i in responses_completed:
    if i['m_id'] not in counts:
        counts.update({i['m_id']: 1})
    if i['m_id'] in counts:
        counts[i['m_id']] = counts[i['m_id']] + 1

print(counts)

# update the stats object with the values from counts
for k,v in stats.items():
    for i in v:
        try:
            i['num_completed'] = counts[i['id']]
        except:
            pass

# write updated stats to json so it can get picked up by routes.py:

with open('data/survey_stats.json', 'w') as outfile:
    json.dump(stats, outfile, sort_keys=True, indent=4)



