triples = open("data/wikimovies/wikimovies.verb",'r').read().splitlines()
# import pandas library
import pandas as pd
  
# dictionary with list object in values
details = {
    'pid' : [int(float(a)) for a in range(len(triples))],
    'text' : [str(t) for t in triples],
}
  
# creating a Dataframe object with skipping 
# one column i.e skipping age column.
df = pd.DataFrame(details, columns = ['pid', 'text'])
df.to_csv("data/wikimovies/wikimovies.tsv",index=False,sep ='\t',header=False)