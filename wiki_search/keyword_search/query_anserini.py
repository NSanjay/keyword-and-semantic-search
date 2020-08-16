from pyserini.search import SimpleSearcher


class KeywordSearchUtil:
    def __init__(self, index_file):
        self.searcher = SimpleSearcher(index_file)
        self.searcher.set_bm25(0.9, 0.4)
        self.searcher.set_rm3(10, 10, 0.5)

    def retrieve_top_k_hits(self, query, k=5000):
        hits = self.searcher.search(query, k)
        return hits
