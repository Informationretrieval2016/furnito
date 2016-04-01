import csv
import config
import os
import numpy as np
from invert_index import Invert_Index

class PBM:

	def __init__(self):
		self.ii = Invert_Index()
		self.file_path = config.file_path
		self.hash_dict = self.ii.posting_list()
	def readListFromCSV(self):
		with open('vector_space.csv', 'rb') as csvfile:
			spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
			spamreader.next()
			row = spamreader.next()
			# print row[0][2:].split(',')
			return row[0][2:].split(',')
	def get_termid(self, query_list):
		'''
		@usage: according user query, find term id from dictionary
		@arg query_list: list of user query
		@return: list of term id, example user query for [chair, desk], return [24, 45]
		'''
		term_id = []
		for query in query_list:
			try:
				term_id.append(self.hash_dict.keys()[self.hash_dict.values().index(query)])
			except:
				pass
		return term_id

	def file_count(self):
		return sum([len(files) for root,dirs,files in os.walk(self.file_path)]) / 2

	def get_score(self,query_list,total_file):
		scores = []
		term_id = self.get_termid(query_list)
		term_frequency = self.readListFromCSV()
		for i in term_id:
			scores.append((total_file - int(term_frequency[i]) + 0.5) / (int(term_frequency[i]) + 0.5))
		return scores
	def get_documents(self):
		'''
		#usage: get all file.
		#arg: the path where files are
		#return: a list of urls for all files
		'''
		FileList=[]
		FileNames=os.listdir(self.file_path)
		if (len(FileNames)>0):
			for fn in FileNames:
				fullfilename=os.path.join(self.file_path,fn)
				FileList.append(fullfilename)
		if (len(FileList)>0):
			FileList.sort()
		return FileList

	def log_prob(self, query_list,lam):
		pqd = []
		document_list = self.get_documents()
		collection = self.get_collection()
		for document in document_list:
			data = open(document).read().split(' ')
			score = 1.0
			for query in query_list:
				count = float(data.count(query))
				collection_count = float(collection.count(query))
				length = len(data)
				collection_length = len(collection)
				score = score + np.log(1 + ((1 - lam) / lam) * (count/length / (50 * collection_count / collection_length)))
			pqd.append(score)
		document_with_rank = zip(document_list,pqd)
		return sorted(document_with_rank, key=lambda s : s[1], reverse = True)

	def get_collection(self):
		collection = []
		document_list = self.get_documents()
		for document in document_list:
			collection.extend(open(document).read().split(' '))
		return collection

	def BIM_rank(self,query_list):
		ranks = []
		document_list = self.get_documents()
		for document in document_list:
			data = open(document).read().split(' ')
			x = list(set(query_list).intersection(set(data)))
			if len(x) == 0:
				ranks.append(1.0)
			else:
				scores = self.get_score(x,len(document_list))
				ranks.append(np.prod(scores))
			document_with_rank = zip(document_list,ranks)
		return sorted(document_with_rank, key=lambda s : s[1], reverse = True)

p = PBM()
ranks = p.log_prob(['chair'], 0.5)
