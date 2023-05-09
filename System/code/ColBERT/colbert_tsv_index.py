from colbert.infra import Run, RunConfig, ColBERTConfig
from colbert import Indexer

if __name__ == '__main__':
    with Run().context(RunConfig(nranks=1, experiment="aviationqa")):

        config = ColBERTConfig(
            nbits=2,
            root="experiments",
        )
        indexer = Indexer(checkpoint="colbertv2.0", config=config)
        indexer.index(name="aviationkg.nbits=2",
                      collection="../data/aviationKG/aviationKG.tsv")
