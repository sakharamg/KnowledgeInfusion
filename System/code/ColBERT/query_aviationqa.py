from colbert.data import Queries
from colbert.infra import Run, RunConfig, ColBERTConfig
from colbert import Searcher
import pandas as pd
from tqdm import tqdm
splits = ["train", "dev", "test"]
with Run().context(RunConfig(experiment='aviationqa')):
    searcher = Searcher(index='aviationkg.nbits=2')
for split in splits:
    questions = []
    answers = []
    contexts = []
    qas = pd.read_csv("../data/aviationqa/"+split + ".csv")
    for i in tqdm(range(len(qas)), desc=split):
        query, ans = qas.loc[i, "Question"], qas.loc[i, "Answer"]
        results = searcher.search(query, k=5)
        top_k_passages = []
        for passage_id, passage_rank, passage_score in zip(*results):
            top_k_passages.append(searcher.collection[passage_id])
        context = '. '.join(top_k_passages).replace("\t", " ")
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
    df.to_csv("../data/aviationqa/"+split+"_triples.tsv",
              index=False, sep='\t', header=False)
