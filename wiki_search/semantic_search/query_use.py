import numpy as np
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()

import tensorflow_hub as hub
import sentencepiece as spm
from absl import logging
logging.set_verbosity(logging.ERROR)


class SemanticSearchUtil:
    def __init__(self):
        self.graph = tf.Graph()
        with tf.Session(graph=self.graph) as sess:
            self.embed_module = hub.Module(
                "../../models/universal-sentence-encoder-lite_2")
            spm_path = sess.run(self.embed_module(signature="spm_path"))
            self.sp = spm.SentencePieceProcessor()
            self.sp.Load(spm_path)

    def rank_semantic(self, query, hits):
        # print(query)
        # print(hits)
        values, indices, dense_shape = self.process_to_IDs_in_sparse_format([query] + hits)
        with tf.Session(graph=self.graph) as sess:
            input_placeholder = tf.sparse_placeholder(tf.int64, shape=[None, None])
            encodings = self.embed_module(
                inputs=dict(
                    values=input_placeholder.values,
                    indices=input_placeholder.indices,
                    dense_shape=input_placeholder.dense_shape))

            sess.run([tf.global_variables_initializer(), tf.tables_initializer()])
            message_embeddings = sess.run(
                encodings,
                feed_dict={input_placeholder.values: values,
                           input_placeholder.indices: indices,
                           input_placeholder.dense_shape: dense_shape})

            message_embeddings = np.array(message_embeddings).tolist()

        query_embedding, hits_embeddings = message_embeddings[0], message_embeddings[1:]

        scores = np.inner(query_embedding, hits_embeddings)

        print(f"len of sentences:: {len(message_embeddings)} and len of hits:: {len(hits_embeddings)}"
              f"and len of scores:: {len(scores)}")
        # print(scores)
        return scores

    def process_to_IDs_in_sparse_format(self, sentences):

        ids = [self.sp.EncodeAsIds(x) for x in sentences]
        max_len = max(len(x) for x in ids)
        dense_shape = (len(ids), max_len)
        values = [item for sublist in ids for item in sublist]
        indices = [[row, col] for row in range(len(ids)) for col in range(len(ids[row]))]
        return (values, indices, dense_shape)
