what i've done so far: 

- created a gitignore
- installed and activated virtualenv
- installed flask
- created folder structure
- added templates and css
- deployed to heroku @ https://radiant-taiga-47405.herokuapp.com
- staged the json file that will hold the progress table data
- staged the json file that contains all the survey urls
- staged the json file that will be dim_measures
- built pages for index, find, and about
- downloaded flask wtf

parsing survey responses into survey file:
- get all potential question ids from json

parsing survey responses into progress json:


- grab records from json that have non-empty answer dict
- filter out records that aren't completed
- count num records per measure id
- grab most recent record per measure id
- count num records per dept
- compare with dept totals
- compute status
- write to json
