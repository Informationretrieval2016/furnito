import string
from invert_index import Invert_Index
import config
import json
import numpy as np
import pandas as pd
from file_reader import File_Reader
from file_writer import File_Writer

class VSM:
    def __init__(self):
        self.ii = Invert_Index()
        self.fr = File_Reader()
        self.fw = File_Writer()
        self.pl_path = config.posting_list_path
        self.pl = {}
        self.hash_dict = self.ii.posting_list()
        self.csv_path = config.vector_space_path
        #self.build_vector_space()

    def get_termid(self, query_list):
        '''
        @usage: according user query, find term id from dictionary
        @arg query_list: list of user query
        @return: list of term id, example user query for [chair, desk], return [24, 45]
        '''
        #step 1, find index of current user query
        term_id = []
        for query in query_list:
            try:
                term_id.append(self.hash_dict.keys()[self.hash_dict.values().index(query)])
            except:
                pass
        return term_id

    def get_docs(self, term_id):
        '''
        @usage: according to query index, get related documents
        @arg: term_id, id of user query terms
        @return: dict of document location, {24: [doc1, doc5, doc7], 45: [doc8, dic11, doc22]}
        '''
        with open(self.pl_path) as pl_file:
            self.pl = json.load(pl_file)
        term_location = {}
        for term in term_id:
            term_location[term] = self.pl[str(term)]
        return term_location

    def build_query_vector(self, term_id):
        '''
        @usage: build query vector
        @arg term_id: list of terms id
        @return: pandas data frame 1 row * n columns
        '''
        #build query vector
        #init a pandas data frame
        query_vector = pd.DataFrame(index = [1], columns = range(0, len(self.hash_dict)))
        query_vector = query_vector.fillna(0)
        for term in term_id:
            query_vector.xs(1, copy = False)[term_id] = 1
        query_vector = np.array(map(list, query_vector.values))
        return query_vector
    def build_vector_space(self):
        '''
        @usage: build simple vector space model
        @arg term_location: dict of term id and term docs, for example {1: [doc1, doc3]}
        @arg term_id: list of term id
        '''
        docs = self.fr.load_file_names()
        #init a dataframe, rows are docs, columns are terms
        df = pd.DataFrame(index = docs, columns = range(0, len(self.hash_dict)))
        df = df.fillna(0)
        for current_doc in docs:
            content = self.fr.read_file(current_doc)
            content = self.clean(content)
            #construct vector space
            for term in content.split():
                #get term_id by term
                try:
                    term_id = self.hash_dict.keys()[self.hash_dict.values().index(term)]
                    #add current dataframe
                    df.xs(current_doc, copy = False)[term_id] += 1
                except:
                    pass
        #insert a line into matrix indicate document frequency
        document_frequency = []
        for i in range(0, len(self.hash_dict)):
            #if current term >=1 means current term appear in doc
            temp_df = list(df.ix[:,i] >= 1)
            document_frequency.append(sum(temp_df))
        #write to dataframe
        df = pd.DataFrame(np.array([document_frequency]), columns = range(0, len(self.hash_dict))).append(df)
        df.to_csv(self.csv_path, sep = ',')

    def simple_vector_space(self, query_vector):
        '''
        @usage: compute score of ranking use simple vector space
        @arg query_vector: vector of user query
        @return: dict of score
        '''
        score_dict = {}
        term_id = self.get_termid(query_vector)
        term_location = self.get_docs(term_id)
        query_vector = self.build_query_vector(term_id)

        unique_locations = []
        #get unique documents
        for k in term_location:
            unique_locations.extend(term_location[k])
        unique_locations = list(set(unique_locations))
        #get these lines from vector space
        df = pd.read_csv(self.csv_path, header = None, encoding = "utf-8", skiprows = 2)
        df = df.loc[df[0].isin(unique_locations)]
        for index, row in df.iterrows():
            current_file = row[0]
            doc_vector = row[1:]
            doc_vector = np.array(doc_vector, dtype=pd.Series)
            score = np.sum(query_vector * doc_vector)
            score_dict[current_file] = score
        return score_dict

    def tfidf_vector_space(self, query_vector):
        '''
        @usage: compute score according to tf-idf
        @arg query_vector: list of user query
        @return: dict of final score
        '''
        score_dict = {}
        term_id = self.get_termid(query_vector)
        term_location = self.get_docs(term_id)
        query_vector = self.build_query_vector(term_id)
        unique_locations = []
        for k in term_location:
            unique_locations.extend(term_location[k])
            unique_locations = list(set(unique_locations))
        document_frequency = []
        #read df, first row is document frequency, other rows are term frequency
        df=pd.read_csv(self.csv_path, header = None, encoding="utf-8", skiprows=1)
        document_frequency = df.iloc[[0]]
        document_frequency = document_frequency.ix[:, document_frequency.columns!=0]
        document_frequency = np.array(map(list, document_frequency.values))
        idf = self.idf(document_frequency)
        df=df.loc[df[0].isin(unique_locations)]
        for index, row in df.iterrows():
            current_file = row[0]
            doc_vector = row[1:]
            doc_vector = np.array(doc_vector, pd.Series)
            doc_vector = doc_vector * idf
            score = np.sum(query_vector * doc_vector)
            score_dict[current_file] = score
        return score_dict


    def pln_vector_space(self, query_vector):
        '''
        @usage: compute pivot-length-normalization vector score
        @arg query_vector: vector of user query
        @return: score
        '''
        score_dict = {}
        term_id = self.get_termid(query_vector)
        term_location = self.get_docs(term_id)
        query_vector = self.build_query_vector(term_id)
        #init document length, for normalization doc length
        doc_length = self.fr.load_doc_length()
        avg_doc_length = sum(doc_length.values())/len(doc_length)
        #get doc locations
        unique_locations = []
        for k in term_location:
            unique_locations.extend(term_location[k])
        unique_locations = list(set(unique_locations))
        #read vector space
        df = pd.read_csv(self.csv_path, header = None, encoding="utf-8", skiprows=1)
        document_frequency = df.iloc[[0]]
        document_frequency = document_frequency.ix[:, document_frequency.columns!=0]
        document_frequency = np.array(map(list, document_frequency.values))
        idf = self.idf(document_frequency)
        df = df.loc[df[0].isin(unique_locations)]
        for index, row in df.iterrows():
            current_file = row[0]
            doc_vector = row[1:].tolist()
            doc_vector = np.array(doc_vector)
            doc_term = (np.log10(1 + np.log10(1 + doc_vector)))/(doc_length[current_file]/avg_doc_length)
            score = np.sum(query_vector * (doc_term*idf))
            score_dict[current_file] = score
        return score_dict


    def bm25_vector_space(self, user_query):
        '''
        @usage: use bm-25 model to build ranking system
        @arg user_query: list of user query
        @return: score
        '''
        score_dict = {}
        term_id = self.get_termid(user_query)
        term_location = self.get_docs(term_id)
        query_vector = self.build_query_vector(term_id)
        doc_length = self.fr.load_doc_length()
        avg_doc_length = sum(doc_length.values())/len(doc_length)
        #find overlap between user query and vector space
        unique_location = []
        for k in term_location:
            unique_location.extend(term_location[k])
        unique_location = list(set(unique_location))
        document_frequency = []
        #load df
        df = pd.read_csv(self.csv_path, header = None, encoding = 'utf-8', skiprows=1)
        document_frequency = df.iloc[[0]]
        document_frequency = document_frequency.ix[:,document_frequency.columns!=0]
        document_frequency = np.array(map(list,document_frequency.values))
        idf = self.idf(document_frequency)
        #filter df to files current user is retrieving
        df = df.loc[df[0].isin(unique_location)]
        for index, row in df.iterrows():
            current_file = row[0]
            doc_vector = row[1:].tolist()
            doc_vector = np.array(doc_vector)
            doc_term = ((10+1)*doc_vector)/(doc_vector+10 * (1-0.5+0.5*(doc_length[current_file]/avg_doc_length)))
            score = np.sum(query_vector * (doc_term * idf))
            score_dict[current_file] = score
        return score_dict

    def clean(self, content):
        '''
        @usage: clean content, remove
        @arg content: content of document
        @return: cleaned content
        '''
        punc = set(string.punctuation)
        content = ''.join([x for x in content if not x.isdigit()])
        content = ''.join([x for x in content if x not in punc])
        content = ''.join([x.lower() for x in content])
        content = ' '.join(content.split())

        return content

    def idf(self, document_frequency):
        '''
        @usage: compute inverse document frequency
        @arg document_frequency: frequency of terms appear in document
        @return: score of idf
        '''
        idf = np.log2(float(len(self.fr.load_file_names()) + 1)/document_frequency)
        return idf
