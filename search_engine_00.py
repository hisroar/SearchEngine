# PAGERANK

import urllib2
from search_engine import *
from difflib import SequenceMatcher
from bs4 import BeautifulSoup
from random import random
from time import clock
from page import *

class SearchEnginePR(SearchEngine):
    
    def __init__(self, link, time, match_threshold=0.65, d=0.85, numloops=10, import_name='', page_stay=''):
        SearchEngine.__init__(self, link, time, match_threshold=match_threshold, import_name=import_name, page_stay=page_stay)
    
    # Compute the ranks of the pages
    def compute_ranks(self, d=0.85, numloops=10): # returns ranks of the pages
        print 'Calculating ranks'
        self.ranks = self.pagerank(d, numloops)
        print 'Ranks finished'
    
    # Compute the PageRank scores
    def pagerank(self, d, numloops):
        len_pages = len(self.pages)
        pagerank = {}
        
        # PageRank
        for page in self.pages: 
            pagerank[page] = 1.0 / len_pages
        
        for i in range(0, numloops):
            newranks = {}
            for page in pagerank:
                newrank = (1 - d) / len_pages # web surfer will not go to your page, so that surfer does not get stuck
                # sum of ranks of linked pages
                for i in pagerank:
                    if page in self.pages[i][0]:
                        newrank += d * pagerank[i] / len(self.pages[i][0])
                
                newranks[page] = newrank
            pagerank = newranks
        return pagerank
    
    # Save the data
    def save(self, name):
        SearchEngine.save(self, name + 'PR', dir_name=name)
    
    # Import the data, and if PageRank scores don't exists, calculate them
    def import_data(self, name):
        try:
            SearchEngine.import_data(self, name + 'PR', dir_name=name)
        except:
            print 'No PR file, importing default'
            SearchEngine.import_data(self, name, dir_name=name)
            if self.time == 0:
                self.compute_ranks()
                SearchEngine.sort_index(self)
                self.save(name)

def get_results(url='', time=0, match_thresh=0.65, import_name=''):
    x = SearchEnginePR(url, time, match_threshold=match_thresh, import_name=import_name)
    return x 
    
# x.save('index_test', 'graph_test')
