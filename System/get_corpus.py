import json
import os
from tqdm import tqdm
import random
BASE_DIR = "NTSB_json/"
save_file='NTSB_Corpus.txt'
# Opening JSON file
lines= []

for filename in tqdm([x for x  in os.walk(BASE_DIR)][0][2]):
	f = open(BASE_DIR+filename)
	# returns JSON object as 
	# a dictionary
	data = json.load(f)
	relevant_data = [line['para_text'] for line in data if 'Analysis' in line['para_heading'] or 'Probable Cause and Findings' in line['para_heading'] or 'Factual Information' in line['para_heading']]
	lines.extend(' '.join(relevant_data).replace("The National Transportation Safety Board determines the probable cause(s) of this accident to be: ","").replace("\n"," ").replace(". ",".\n").split("\n"))
	# Closing file
	f.close()
print('Samples from dataset\n','\n'.join(random.sample(lines, 4)))
print("No of lines: ",len(lines))
with open(save_file, mode='wt', encoding='utf-8') as myfile:
    myfile.write('\n'.join([line.strip() for line in lines]))
print("Saved Corpus at ",save_file)
