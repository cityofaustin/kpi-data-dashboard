import requests
import configparser
import json
import os

# call typeform and write repsonses to json

config = configparser.ConfigParser()
config.read('secrets.txt')
form_id = config['typeform.com']['form_id']
api_key = config['typeform.com']['api_key']
airtable_api_key = config['airtable']['api_key']

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

print(str(c) + ' responses identified and written to data/completed_responses.json')

# call airtable to fetch the survey tokens that have already been published 
# only 100 records will be allowed, need to fix

r_a = requests.get('https://api.airtable.com/v0/apprncjzrsX5xkKCA/responses', headers={'authorization': airtable_api_key})
j_a = r_a.json()
records = j_a['records']
t = []

for i in records:
    try:
        t.append(i['fields']['token'])
    except:
        pass
    
print(str(len(t)) + ' tokens already published to airtable.')
print(t)


# filter out records already published to airtable

responses_airtable = []
for i in responses_completed:
    if i['token'] not in t:
        responses_airtable.append(i)
print(str(len(responses_airtable)) + " responses to send to airtable")

# prep the responses to go to airtable by giving them more readable keys

answer_map = {'token': 'token', 'list_29849901_choice': 'Does your department collect and analyze the data needed for this measure?',
 'textfield_31433992': 'Where does the data come from?',
 'list_31434167_choice': 'Who collects the data?',
 'list_31434167_other': 'Other collector',
 'textfield_33594536': 'Name who collects the data?',
 'list_31434529_choice': 'What medium are the collectors using?',
 'list_31434529_other': 'Other medium',
 'list_31439434_choice': 'How often is the data gathered?',
 'list_31439434_other': 'Other freq',
 'list_29849202_choice': "When it's time to calculate the data (to produce the measure), what type of system is it stored in?",
 'list_29849202_other': 'Other system',
 'textfield_31440655': "What's the name of the data system?",
 'list_31441411_choice_40272190': 'calc w spreadsheet',
 'list_31441411_choice_40272191': 'calc w desktop database',
 'list_31441411_choice_40272189': 'calc w BI tools',
 'list_31441411_choice_40272192': 'calc w ETL process',
 'list_31441411_choice_40272193': "calc w good ol' pencil and paper",
 'list_31441411_choice_41493502': 'calc w trusty calculator',
 'list_31441411_choice_40272194': 'calc w I do it in my head. Seriously.',
 'list_31441411_choice_41493503': "calc w - don't know",
 'list_31441411_other': 'calc w other',
 'list_31441558_choice': 'Is the data for this measure published available to the public?',
 'list_31441558_other': 'Other published',
 'website_31441577': 'What is the URL where we can find the published data?',
 'textfield_31442505': 'responder name',
 'textfield_31442528': 'job title',
 'textfield_32615888': 'business unit',
 'email_31442534': 'responder email',
 'textarea_31444284': 'additional feedback',
 'm_name': 'm_name',
 'm_id': 'm_id',
 'dept': 'dept',
 'contact': 'concierge',
 'started': 'Start Date',
 'submitted': 'Submit Date',
 'network_id': 'Network ID'}

responses_prepped = []
for i in responses_airtable:
    z = dict((answer_map[key], value) for (key, value) in i.items())
    responses_prepped.append(z)

print(str(len(responses_prepped)) + ' records prepped for airtable')

# send those new responses to airtable

for i in responses_prepped:
    j_p = {'fields': i}
    payload = json.dumps(j_p)
    a_p = requests.post('https://api.airtable.com/v0/apprncjzrsX5xkKCA/responses', headers={'authorization': airtable_api_key, 'Content-type': 'application/json'}, data=payload)
    print(a_p)

# fetch updated measure status from airtable, api only returns 100 records max... so breaking this up into groups

r_s1 = requests.get('https://api.airtable.com/v0/apprncjzrsX5xkKCA/measures%20list?view=group1', headers={'authorization': airtable_api_key})
r_s2 = requests.get('https://api.airtable.com/v0/apprncjzrsX5xkKCA/measures%20list?view=group2', headers={'authorization': airtable_api_key})
r_s3 = requests.get('https://api.airtable.com/v0/apprncjzrsX5xkKCA/measures%20list?view=group3', headers={'authorization': airtable_api_key})
j1 = r_s1.json()
j2 = r_s2.json()
j3 = r_s3.json()

status_list = []

   # combine the responses from the 3 calls into one object

for i in j1['records']:
    status_list.append(i)

for l in j2['records']:
    status_list.append(l)
    
for p in j3['records']:
    status_list.append(p)

   # create a dict of measure ids with status for each

status = {}

for i in status_list:
    x = {i['fields']['measure_id']: i['fields']['measure_status']}
    status.update(x)

# bring in the last survey stats data snapshot:

with open('data/survey_stats.json', 'r') as infile:
    stats = json.load(infile)

# determine the completed survey counts per measure id:

counts = {}

for i in responses_completed:
    if i['m_id'] not in counts:
        counts.update({i['m_id']: {'submitted': 1, 'status': 'received'}})
    if i['m_id'] in counts:
        counts[i['m_id']]['submitted'] = counts[i['m_id']]['submitted'] + 1

# update the counts object with the measure status from airtable
for k,v in counts.items():
    v['status'] = status[k]

print(counts)

# update the survey stats object with the values from counts
for k,v in stats.items():
    for i in v:
        try:
            i['num_received'] = counts[i['id']]['submitted']
            i['status'] = counts[i['id']]['status']           
        except:
            pass

# write updated stats to json so it can get picked up by routes.py:

with open('data/survey_stats.json', 'w') as outfile:
    json.dump(stats, outfile, sort_keys=True, indent=4)

# calculate dept-level stats for progress table

dept_stats = {}
for k,v in stats.items():
    dept = k
    num_measures = len(v)
    verified = []
    for i in v:
        if i['status'] == 'verified':
            verified.append(1)

    num_verified = sum(verified)
	
    d = {dept: {'num_measures': num_measures, 'num_verified': num_verified, 'status': ''}}
    dept_stats.update(d)

for k,v in dept_stats.items():
	if v['num_verified'] == v['num_measures']:
		v['status'] = 'completed'
	elif v['num_verified'] > 0:
		v['status'] = 'in progress'


# write updated dept stats to json so it can get picked up by routes.py:
with open('data/dept_stats.json', 'w') as outfile:
    json.dump(dept_stats, outfile, sort_keys=True, indent=4)
    


