import csv
import config
from math import log
from vsm import VSM
import os
import numpy as np
from invert_index import Invert_Index

class BM25:
   def __init__(self):
     self.ii = Invert_Index()
     self.file_path = config.file_path
     self.hash_dict = self.ii.posting_list()
     self.vsm = VSM()
     self.doc_length = self.vsm.bm25_vector_space()
     self.avg_doc_length = self.vsm.bm25_vector_space()

   def readListFromCSV(self):
		with open('vector_space.csv', 'rb') as csvfile:
			spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
			spamreader.next()
			row = spamreader.next()
			# print row[0][2:].split(',')
			return row[0][2:].split(',')
   def run_query(self, query):
        query_result = dict()
        for term in query:
            if term in self.index:
             doc_dict = self.index[term] # retrieve index entry
             for docid, freq in doc_dict.iteritems(): #for each document and its word frequency
                score = score_BM25(n=len(doc_dict), f=freq, qf=1, r=0, N=len(self.doc_length), dl=self.doc_length.get_length(docid), avdl=self.avg_doc_length) # calculate score
                    if docid in query_result: #this document has already been scored once
                       query_result[docid] += score
                    else:
                       query_result[docid] = score
   k1 = 1.2
   k2 = 100
   b = 0.75
   R = 0.0

   def score_BM25(n, f, qf, r, N, dl, avdl):
    K = compute_K(dl, avdl)
    first = log( ( (r + 0.5) / (R - r + 0.5) ) / ( (n - r + 0.5) / (N - n - R + r + 0.5)) )
    second = ((k1 + 1) * f) / (K + f)
    third = ((k2+1) * qf) / (k2 + qf)
    return first * second * third

   def compute_K(dl, avdl):
    return k1 * ((1-b) + b * (float(dl)/float(avdl)))