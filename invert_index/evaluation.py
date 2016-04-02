from vsm import VSM
import operator
import timeit
import csv
import pandas as pd

vsm = VSM()
#evaluate models
def evaluate(model_name, query_list):
    #simple_vsm
    if model_name == "simple":
        start = timeit.default_timer()
        res_dict = vsm.simple_vector_space(query_list)
        stop = timeit.default_timer()
    elif model_name == "tfidf":
        start = timeit.default_timer()
        res_dict = vsm.tfidf_vector_space(query_list)
        stop = timeit.default_timer()
    elif model_name == "pln":
        start = timeit.default_timer()
        res_dict = vsm.pln_vector_space(query_list)
        stop = timeit.default_timer()
    elif model_name == "bm25":
        start = timeit.default_timer()
        res_dict = vsm.bm25_vector_space(query_list)
        stop = timeit.default_timer()
    else:
        print "no model named %s", model_name

    #sort res_dict by value
    res_dict = sorted(res_dict.items(), key = operator.itemgetter(1), reverse = True)
    return res_dict[0:20], stop - start

query_term = ['chair']
simple_dict, simple_time = evaluate("simple", query_term)
print "simple vsm:" + str(simple_time)
tfidf_dict, tfidf_time = evaluate("tfidf", query_term)
print "tfidf vsm:" + str(tfidf_time)
pln_dict, pln_time = evaluate("pln", query_term)
print "pln time:" + str(pln_time)
bm25_dict, bm25_time = evaluate("bm25", query_term)
print "bm25:" + str(bm25_time)
res = pd.DataFrame({'simple': simple_dict, 'tfidf': tfidf_dict, 'pln': pln_dict, 'bm25': bm25_dict})
res.to_csv("/home/wb/Documents/evaluation_data/e1.csv", sep = ",")











