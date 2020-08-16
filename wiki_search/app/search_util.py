import sys
import os
import re

from collections import defaultdict

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from wiki_search.keyword_search.query_anserini import KeywordSearchUtil
from wiki_search.semantic_search.query_use import SemanticSearchUtil

import hunspell
import pandas as pd

class SearchUtil:
    def __init__(self):
        index_file = "../../indices/sample_collection_jsonl/"
        self.keyword_util = KeywordSearchUtil(index_file)
        self.semantic_util = SemanticSearchUtil()
        self.hobj = hunspell.HunSpell('/usr/share/hunspell/en_US.dic', '/usr/share/hunspell/en_US.aff')

    def retrieve_top_k_hits(self, query, k=5000):
        hits = self.keyword_util.retrieve_top_k_hits(query, k)
        keyword_dict = defaultdict(int)
        ids, paras, scores, titles = [], [], [], []

        def _filter_results():
            considered_paras = 0
            for doc in hits:
                a_split = doc.docid.split("[SEP]")
                url = a_split[-1]
                title = a_split[1]
                if (url not in keyword_dict and len(keyword_dict) < 10) or (keyword_dict[url] < 2):
                    if len(keyword_dict) >= 10:
                        continue

                    text = doc.raw.split("[SEP]")[1]
                    sentence_split = text.strip().split(".")
                    print(text)
                    sentence_split = [sentence for sentence in sentence_split if sentence.strip() != ""]

                    ids.extend([url] * len(sentence_split))
                    paras.extend(sentence_split)
                    scores.extend([doc.score] * len(sentence_split))
                    titles.extend([title] * len(sentence_split))

                    keyword_dict[url] += 1

                if considered_paras == 20:
                    break

                considered_paras += 1

        _filter_results()

        # print(paras)
        semantic_scores = self.semantic_util.rank_semantic(query, paras)

        assert len(ids) == len(paras) == len(titles) == len(scores) == len(semantic_scores), \
                                                                     f"lengths unequal::" \
                                                                     f"ids:: {len(ids)} - " \
                                                                     f"paras:: {len(paras)} - " \
                                                                     f"titles:: {len(titles)} - " \
                                                                     f"scores:: {len(scores)} - " \
                                                                     f"semantic_scores:: {len(semantic_scores)}"
        return_dict = dict()
        print("length of ids::", len(ids))
        for i in range(len(ids)):
            a_url = ids[i]
            if a_url not in return_dict or (scores[i] + semantic_scores[i] > return_dict[a_url][0]):
                return_dict[a_url] = (scores[i] + semantic_scores[i], titles[i], paras[i])

        ids_scores = sorted(return_dict.items(), key=lambda x: x[1][0], reverse=True)
        return ids_scores

    def _filter_results(self, hits):

        keyword_dict = defaultdict(int)
        ids, paras, scores, titles = [], [], [], []
        considered_paras = 0

        for doc in hits:
            a_split = doc.docid.split("[SEP]")
            url = a_split[-1]
            title = a_split[1]
            if (url not in keyword_dict and len(keyword_dict) < 10) or (keyword_dict[url] < 2):
                if len(keyword_dict) >= 10:
                    continue

                text = doc.raw.split("[SEP]")[1]
                sentence_split = text.split(".")

                ids.extend([url]*len(sentence_split))
                paras.extend(sentence_split)
                scores.extend([doc.score]*len(sentence_split))
                titles.extend([title]*len(sentence_split))

                keyword_dict[url] += 1

            if considered_paras == 20:
                break

            considered_paras += 1

        # ids, paras, scores = zip(*[entry] for url in keyword_dict for entry in keyword_dict[url])
        # ids, paras, scores = zip(*[(doc.docid, doc.raw) for doc in hits[:k]])
        paras = list(paras)
        semantic_scores = self.semantic_util.rank_semantic(query, paras)

        return_dict = dict()

        for i in range(len(ids)):
            url = ids[i]
            if url not in return_dict or ((scores[i] + semantic_scores[i]) > return_dict[url][0]):
                return_dict[url] = (scores[i] + semantic_scores[i], titles[i], paras[i])

        ids_scores = sorted(return_dict.items(), key=lambda x: x[1][0], reverse=True)

        return ids_scores

    def sanitise_query(self, query):
        query = re.sub(r'[\s]{2,}', " ", query)

        print("revised query::", query)
        actual_query = []
        for word in query.split():
            print(f"word:: {word}")
            if not self.hobj.spell(word):
                autocorrects = self.hobj.suggest(word)
                if not autocorrects:
                    return False, None
                actual_query.append(autocorrects[0])
            else:
                actual_query.append(word)

            print(f"actual_query:: {actual_query}")

        return True, " ".join(actual_query)
