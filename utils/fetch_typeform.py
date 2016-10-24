import requests
import configparser
import json
import os
# import logger

# logging.getLogger()


def process_typeform_responses():
    # call typeform api and get all responses

    # form_id = os.environ['TYPEFORM_FORM_ID']
    # typeform_api_key = os.environ['TYPEFORM_API_KEY']
    # airtable_api_key = os.environ['AIRTABLE_API_KEY']

    config = configparser.ConfigParser()
    config.read('secrets.txt')
    form_id = config['typeform.com']['form_id']
    typeform_api_key = config['typeform.com']['api_key']
    airtable_api_key = config['airtable']['api_key']
    r = requests.get('https://api.typeform.com/v1/form/'+form_id+'?key='+typeform_api_key)
    d = r.json()
    all_responses = d['responses']
    
    # write to json for safe keeping
    with open('static/data/tmp/responses.tmp.json', 'w') as f:
        j = json.dumps(d)
        f.write(j)
    os.rename('static/data/tmp/responses.tmp.json', 'static/data/tmp/responses.json')
    
    print(str(len(d['responses'])) + ' responses fetched and written to /data/tmp/responses.json') # get logger to do this

    
    # process the responses we just got...

    # filter out responses that are incomplete or don't have a valid dept name
    dept_filter = ['Austin Energy', 'Animal Services', 'Austin Transportation', 'Aviation', 'Building Services', 'Office of the City Clerk', 'Austin Code', 'Austin Convention Center', 'Communication and Technology Management', 'Development Services', 'Economic Development', 'Emergency Medical Services', 'Fire', 'Fleet Services', 'Financial Services', 'Government Relations', 'Health and Human Services', 'Human Resources', 'Law', 'Austin Public Library', 'Labor Relations', 'Municipal Court', 'Management Services', 'Neighborhood Housing and Community Development', 'Office of the City Auditor', 'Office of the Medical Director', 'Office of Real Estate Services', 'Planning and Zoning', 'Communications and Public Information', 'Police', 'Parks and Recreation', 'Public Works', 'Small and Minority Business Resources', 'Austin Resource Recovery', 'Telecommunications and Regulatory Affairs', 'Watershed Protection', 'Austin Water']

    responses_completed = []
    c = -1
    for i in all_responses:
        if i['completed'] == '1' and i['hidden']['dept'] in dept_filter and len(i['answers']) != 0:
            w = {'token': i['token'], 'contact': i['hidden']['contact'], 'm_id': i['hidden']['m_id'], 'dept': i['hidden']['dept'], 'started': i['metadata']['date_land'], 'submitted': i['metadata']['date_submit'], 'network_id': i['metadata']['network_id']}
            for k,v in i['answers'].items():
                w.update({k: v})
            responses_completed.append(w)
        else:
            pass

    # write completed responses to json for safekeeping
    with open('static/data/completed_responses.json', 'w') as outfile:
        json.dump(responses_completed, outfile, sort_keys=True, indent=4)

    print(str(len(responses_completed)) + ' responses identified and written to data/completed_responses.json') # use logger for this

    # read in most recent list of tokens already published to airtable
    with open('static/data/published_tokens.json', 'r') as f:
        t = json.loads(f.read())

    print(str(len(t['tokens'])) + ' tokens already in airtable')

    responses_processed = []
    c = 0
    for i in responses_completed:
        if i['token'] not in t['tokens']:
            responses_processed.append(i)
            t['tokens'].append(i['token'])
            c = c+1

    print('discovered ' + str(c) + ' new tokens')

    print(str(len(responses_processed)) + " responses to send to airtable") # use logger for this


    # post the responses to airtable...

    # prep the responses to go to airtable by giving them more readable keys
    answer_map = {'token': 'token', 
    'list_29849901_choice': 'Does your department collect and analyze the data needed for this measure?', 
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

    responses_airtable = []
    for i in responses_processed:
        z = dict((answer_map[key], value) for (key, value) in i.items())
        responses_airtable.append(z)

    print(str(len(responses_airtable)) + ' records prepped for airtable') # use logger for this

    # send those new responses to airtable
    for i in responses_airtable:
        j = {'fields': i}
        payload = json.dumps(j)
        r = requests.post('https://api.airtable.com/v0/apprncjzrsX5xkKCA/responses', headers={'authorization': airtable_api_key, 'Content-type': 'application/json'}, data=payload)
        print(r) # need to add error handling here

    # update the token list if posts are successful
    with open('static/data/published_tokens.json', 'w') as outfile:
        json.dump(t, outfile, sort_keys=True, indent=4)

if __name__ == '__main__':
    process_typeform_responses()
    
