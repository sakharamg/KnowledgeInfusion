from colbert.data import Queries
from colbert.infra import Run, RunConfig, ColBERTConfig
from colbert import Searcher
import pandas as pd
from tqdm import tqdm
hops = ['1hop', '2hop', '3hop']
splits = ["train", "dev", "test"]
with Run().context(RunConfig(experiment='metaqa')):
    searcher = Searcher(index='wikimovies.nbits=2')
for hop in hops:
    for split in splits:
        questions = []
        answers = []
        contexts = []
        qas = open("../data/metaqa/"+hop+"/qa_"+split +
                   ".txt", 'r').read().splitlines()
        for qa in tqdm(qas, desc=hop+" and "+split):
            query = qa.split("\t")[0]
            ans = qa.split("\t")[1]
            results = searcher.search(query, k=5)
            top_k_passages = []
            for passage_id, passage_rank, passage_score in zip(*results):
                top_k_passages.append(searcher.collection[passage_id])
            context = ' '.join(top_k_passages).replace("\t", " ")
            questions.append(query)
            answers.append(ans)
            contexts.append(context)
        details = {
            'qid': [a for a in range(len(questions))],
            'question': questions,
            'answer': answers,
            'context': contexts,
        }

        # creating a Dataframe object with skipping
        # one column i.e skipping age column.
        df = pd.DataFrame(details, columns=[
                          'qid', 'question', 'answer', 'context'])
        df.to_csv("../data/metaqa/"+hop+"/qa_"+split+"_triples.tsv",
                  index=False, sep='\t', header=False)
