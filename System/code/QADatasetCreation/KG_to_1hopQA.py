from tqdm import tqdm
import openai
import os
import pandas as pd
import re
from time import sleep
KG = pd.read_csv("data/aviationKG/aviationKG.txt", sep='\t',
                 header=0, names=["head", "relation", "tail"], na_values=None)


def print_stats(KG):
    print(KG['head'].value_counts())
    print(KG['relation'].value_counts())
    print(KG['tail'].value_counts())
    print("#samples: ", len(KG))


remove_head = []
remove_relation = []
remove_tail = []
# Remove relation named type which had mostly Named_Individual and Accident_Number, and links
remove_relation.extend(["type", "http://purl.org/dc/elements/1.1/description",
                       "http://purl.org/dc/elements/1.1/source", "comment", "label", "subPropertyOf", "range", "domain", "seeAlso", "subClassOf", "defintion"])
# Remove reltation which occurs upto 5 times
rem_count = 5
for i in range(20):
    remove_relation.extend(list(KG['relation'].value_counts()[
                           KG['relation'].value_counts() <= rem_count].keys()))
    remove_tail.extend(["true", "false", "None"])
    
    # ^.*-.*-.*:.*:.*$
    remove_head.extend(list(KG['head'].value_counts()[
                       KG['head'].value_counts() <= rem_count].keys()))
    remove_tail.extend(list(KG['tail'].value_counts()[
                       KG['tail'].value_counts() <= rem_count].keys()))
    KG = KG[~KG['head'].isin(remove_head)]
    KG = KG[~KG['relation'].isin(remove_relation)]
    KG = KG[~KG['tail'].isin(remove_tail)]
# print_stats(KG)
# KG = KG[(KG['relation'] != "type") & (
#     KG['tail'] != "false") & (
#     KG['tail'] != "true") & (KG['tail'] != "1000")& (KG['tail'] != "None") & (KG['relation'] != "http://purl.org/dc/elements/1.1/description") & (KG['relation'] != "http://purl.org/dc/elements/1.1/source")]


# Check if the strings in the column are numbers
is_number = KG['tail'].apply(lambda x: bool(
    re.match(r'^-?\d+(?:\.\d+)?$', str(x))))

# Print the rows where the column contains a number
KG = KG[~is_number]
is_number = KG['tail'].apply(lambda x: bool(
    re.match(r'^.*-.*-.*:.*:.*', str(x))))

# Print the rows where the column contains a number
KG = KG[~is_number]
# print(KG[KG["relation"]=="hasRegisteredOwner"])
# KG = KG[~KG['tail'].str.isnumeric]

KG = KG.dropna()
KG = KG.drop_duplicates()
# print_stats(KG)
# print(KG[KG['relation'].isin(["subPropertyOf","range","domain"])])

# print(KG.head(100))
# print(KG[(KG['relation'] == "label")])
# print_stats(KG)
# print(KG)
# print(list(KG['tail'].value_counts()[KG['tail'].value_counts() <= 5].keys()))
# print(list(set(KG['relation'].to_list())))
# # Print the new dataframe
# print(df_filtered.head(15)

# # Print the shape of the dataframe
# print(df_filtered.shape)
# print(re.search("^.*-.*-.*:.*:.*$", '2001-08-02T12:05:00') )
openai.api_key = ""
relation_dict = {}
for index, triple in tqdm(KG.iterrows()):
    head, relation, tail = triple["head"], triple["relation"], triple["tail"]
    try:
        relation_dict[relation].append((head, relation, tail))
    except:
        relation_dict[relation] = []

questions = []
heads = []
relations = []
tails = []
templates = []
for key in tqdm(relation_dict.keys()):
    index = 0
    head, relation, tail = relation_dict[key][index]
    heads.append(head)
    relations.append(relation)
    tails.append(tail)
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Entity: "+head+"\tRelation: "+relation+"\n" +
                    "Convert the 'Entity' and 'Relation' to question. Keep Head in question and enclose in square brackets [ and ].\n Example: Entity: AccidentNumber_IAD05LA001 Relation: hasFederalAviationRegulation. Your response must be 'What is the Federal Aviation Regulation associated with [AccidentNumber_IAD05LA001]?'  Here Entity, AccidentNumber_IAD05LA001 is in [ and ] "}
            ]
        )
    # print(completion.choices[0])
    except:
        print("Exception. Retrying in 60 seconds!")
        sleep(60)
    questions.append(completion.choices[0]["message"]["content"])
    templates.append(questions[-1].replace("["+head+"]", "[HEAD]"))
    print(head, relation, questions[-1], templates[-1])
    details = {
        'head': heads,
        'relation': relations,
        'tail': tails,
        'question': questions,
        'template': templates,
    }

df = pd.DataFrame(details, columns=[
    'head', 'relation', 'tail','question','template'])
df.to_csv("data/AeroQA/1hop_template.csv",
            index=False)

'''
FIXED TEMLATES MANUALLY AND THEN...
'''

heads = []
relations = []
tails = []
questions = []
answers = []
templates_dict = {}
for index, row in pd.read_csv("data/AeroQA/1hop_template.csv").iterrows():
    head, relation, tail, question, template = row["head"],	row[
        "relation"], row["tail"], row["question"], row["template"]
    templates_dict[relation] = template
for index, triple in tqdm(KG.iterrows()):
    head, relation, tail = triple["head"], triple["relation"], triple["tail"]
    heads.append(head)
    relations.append(relation)
    questions.append(templates_dict[relation].replace("[HEAD]","["+head+"]"))
    answers.append(tail)
    tails.append(tail)
details = {
    'head': heads,
    'relation': relations,
    'tail': tails,
    'question': questions,
    'answer': answers,
}

df = pd.DataFrame(details, columns=[
    'head', 'relation', 'tail', 'question','answer'])
df.to_csv("data/AeroQA/1hop_with_head_relation_tail.csv",
          index=False)
details = {
    'answer': tails,
    'question': questions,
}
df = pd.DataFrame(details, columns=[
    'question', 'answer'])
df.to_csv("data/AeroQA/1hop.csv",
          index=False)
