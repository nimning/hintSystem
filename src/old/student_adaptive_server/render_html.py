#!/usr/bin/env python

import yaml
import re
import simplejson as json
import os
import sys
from markdown import markdown

# A textbox for storing answers to questions, parametrized by size
answerbox_template = "<input type=\"text\" class=\"answerbox\" size=\"%d\" value=\"\">"

# Load the yaml config file
with open('../config.yaml','r') as f:
    config = yaml.load(f)
problem_data_filename = os.path.join(config['Data path'],
    config['WebWork problem json relative path'])
server_html_path = config['Server configuration']['html file to serve']
# Load problem data from the given json file
with open(problem_data_filename,'r') as f:
    problem_data = json.load(f)

# Load client template html file, with a parameter for the html body
with open( "client_template.html" ,'r') as f:
    client_template = f.read()
client_template = open('client_template.html','r').read()

# Add part text and answerboxes to client template body
part_str = ''
for part in sorted(problem_data.keys()):
    part_info = problem_data[part]
    part = 'part%s'%part
    answer_box_str = answerbox_template%( len(str(part_info['answer'])) * 2)
    part_text = re.sub(r'\ +',' ',part_info['text'])
    part_text = markdown(part_text)%answer_box_str
    part_text = re.sub(r'\[\<code\>','$',part_text)
    part_text = re.sub(r'\<\/code\>\]','$',part_text)
    # Combine multiple spaces into one
    #part_str += "<div id=\"tip%s\" class=\"tip\" style=\"display:none;\"></div>"%part
    part_str += "<div id=\"%s\" class=\"%s\">\n%s\n</div>"% \
        (part, 
         'tip' if "is_clue" in part_info and part_info["is_clue"] else "part", 
         part_text)
part_str=part_str.replace('<ol>','')
part_str=part_str.replace('</ol>','')
# Print the newly rendered html file
with open(server_html_path,'w') as f:
    f.write(client_template%part_str)
