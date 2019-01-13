import gensim
from gensim import corpora
import pandas as pd
from nltk.corpus import stopwords
from nltk import FreqDist
from gensim import corpora, models, similarities
import logging
import os
import numpy as np
from gensim.models import Word2Vec
from annoy import AnnoyIndex


logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

stopwords = stopwords.words('english')

class Similarity(object):
    def __init__(self, data, num_topics = 10):
        self.WORD2VEC_LEN = 300
        self.num_topics = num_topics
        self.data = data
        self.tokenized_data = self._tokens()
        self.freqdist = FreqDist([x for y in self.tokenized_data for x in y])

    def _tokens(self):
      tokens = [[word for word in str(document).lower().split() if word not in stopwords]
                for document in self.data]
      return tokens

    def filter_tokens(self):
        """
            Filter tokens which have occured only once
        """
        return [[tk for tk in entry if self.freqdist[tk] > 1] for entry in self.tokenized_data]

    def build_dictionary(self):
        logging.info("In building dictionary")
        self.dictionary = corpora.Dictionary(self.tokenized_data)
        self.dictionary.save('similarity_dictionary.dict')

    def build_corpus(self):
        self.corpus = [self.dictionary.doc2bow(text) for text in self.tokenized_data]
        corpora.MmCorpus.serialize('similarity.mm', self.corpus)

    def build_lsi(self):
        logging.info("Building lsi model")
        self.lsi = models.LsiModel(self.corpus, id2word=self.dictionary, num_topics=self.num_topics)
        # self.lsi.print_topics(self.num_topics)
        self.index = similarities.MatrixSimilarity(self.lsi[self.corpus])
        self.index.save('similarity.index')
        random_samples = np.random.choice(self.data, 10)
        for t in random_samples:
            logging.info("Which of the recipes are more similar to  : {}".format(t))
            doc = t
            vec_bow = self.dictionary.doc2bow(doc.lower().split())
            vec_lsi = self.lsi[vec_bow]
            sims = self.index[vec_lsi]
            sims = sorted(enumerate(sims), key=lambda item: -item[1])
            cnt = 0
            tmp = set()
            tmp.add(t)
            for (x,y) in sims:
                if self.data[x] not in tmp:
                    logging.info(self.data[x])
                    tmp.add(self.data[x])
                if len(tmp) > 5:
                    break
            logging.info("*" * 10)

    def get_vector(self, data):
        data = str(data).lower()
        return np.max([self.w2v_model[x] for x in data.split() if self.w2v_model.vocab.has_key(x)], axis=0)

    def build_word2vec(self):
        self.w2v_model = Word2Vec(self.tokenized_data, size=self.WORD2VEC_LEN, window=5, negative=10)
        self.annoy_index = AnnoyIndex(self.WORD2VEC_LEN)
        for i, rname in enumerate(self.data):
            try:
                v = self.get_vector(rname.lower())
                self.annoy_index.add_item(i, v)
            except:
                pass
        self.annoy_index.build(50)

        names = np.random.choice(self.data, 10)
        for name in names:
            try:
                logging.info("*" * 50)
                logging.info("Source : {}".format(name))
                v = self.get_vector(name)
                res = self.annoy_index.get_nns_by_vector(v, 5, include_distances=True)
                logging.info(res)
                for i,rec in enumerate([self.data[x] for x in res[0]]):
                    logging.info("Recipe {} : {}, score: {}".format(i+1,rec, res[1][i]))
            except:
                pass

    def validate(self):
        names = np.random.choice(self.data, 20)
        for name in names:
            try:
                logging.info("-" * 50)
                logging.info("Which of the recipes are more similar to  : {}".format(name))
                v = self.get_vector(name)
                res = self.annoy_index.get_nns_by_vector(v, 5, include_distances=True)
                logging.info("************ Word2vec Engine **************")
                for i,rec in enumerate([self.data[x] for x in res[0]]):
                    # logging.info("Recipe {} : {}, score: {}".format(i+1,rec, res[1][i]))
                    logging.info("Recipe {} : {}".format(i+1,rec))
                logging.info("************ LSA Engine**************")

                doc = name
                vec_bow = self.dictionary.doc2bow(doc.lower().split())
                vec_lsi = self.lsi[vec_bow]
                sims = self.index[vec_lsi]
                sims = sorted(enumerate(sims), key=lambda item: -item[1])
                tmp = set()
                tmp.add(name)
                for (x,y) in sims:
                    if self.data[x] not in tmp and len(tmp) <= 5:
                        logging.info("Recipe {} : {}".format(i+1,self.data[x]))
                        tmp.add(self.data[x])

            except:
                pass


    def build_lda(self):
        logging.info("Building lda model")
        logging.info("*" * 50)
        lda = models.LdaModel(self.corpus_tfidf, id2word=self.dictionary, num_topics=self.num_topics)
        lda.print_topics(self.num_topics)
        logging.info("*" * 50)


    def build(self):
        logging.info("In build")
        self.build_dictionary()
        self.build_corpus()
        self.tfidf = models.TfidfModel(self.corpus)
        self.corpus_tfidf = self.tfidf[self.corpus]
        self.build_lsi()
        self.build_word2vec()
        # self.build_lda()
        self.validate()


if __name__ == "__main__":
    df = pd.read_csv('epi_r.csv')
    sim = Similarity(df.title.values, num_topics=100)
    sim.build()