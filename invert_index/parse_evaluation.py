import csv
import pandas as pd
# import nltk

class Parse_Evaluation:
	def __init__(self):
		self.fname = "/Users/wesleyquispel/Downloads/e1.csv"

	# def read_csv(self):
	# 	df = pd.read_csv(self.fname, skiprows = 1)
	# 	for column in df:
	# 		print column


	def read_csv(self):
		res = []
		res2 = []
		with open(self.fname, 'rb') as eval_csv:
			csv_reader = csv.reader(eval_csv, delimiter=',', quotechar = '"')
			for row in csv_reader:
				for item in row:
					item = item.split("'")[1:2]
					string = str(item).strip('[]')
					
					new_string = string.replace("/home/wb/Documents/furniture/", "")
					res.append(new_string)
		for filename in res:
			if filename == '':
				pass
			else:
				res2.append(filename)

		res2 = list(set(res2))
		return res2


pe = Parse_Evaluation()
pe.read_csv()