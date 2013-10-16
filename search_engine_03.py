# HITS WORDRANK

import urllib2
from search_engine import *
from search_engine_02 import *
from difflib import SequenceMatcher
from bs4 import BeautifulSoup
from random import random
from time import clock
from page import *

class SearchEngineHITSWR(SearchEngineHITS):
    
    def __init__(self, link, time, word='', match_threshold=0.65, numloops=10, hits_ratio=0.5, import_name='', page_stay=''):
        self.keywords = word.lower().split() # words that are desired on a webpage
        self.word = word
        SearchEngineHITS.__init__(self, link, time, match_threshold=match_threshold, numloops=numloops, import_name=import_name, page_stay=page_stay)
        if word: # only sort if there is a word
            self.compute_ranks(numloops, hits_ratio)
            SearchEngineHITS.sort_index(self)

    def compute_ranks(self, numloops=10, hits_ratio=0.5): # returns ranks of the pages
        print 'Calculating ranks'
        self.ranks = self.hits(numloops)
        print 'Ranks finished'
    
    # Calculate the WordRank scores, and combine them with the HITS scores
    def wordrank(self, numloops, hits_ratio):
        len_pages = len(self.pages)
        wordrank = {}
        
        # HITS
        if len(self.__temp) == len(self.pages):
            hits = self.__temp
        else: hits = SearchEngineHITS.hits(numloops)
        
        # WordRank, ranking pages based upon relevancy to keyword(s)
        for page in self.pages:
            wordrank[page] = 0
        
        len_keywords = len(self.keywords)
        for keyword in self.keywords:
            for page in self.pages:
                text_split = self.pages[page][1].split()
                len_text = len(text_split)
                for word in text_split:
                    wordrank[page] += SequenceMatcher(None, keyword, word).ratio() / len_text / len_keywords / len_pages
        
        hitssum = sum(hits.values())
        wordsum = sum(wordrank.values())
        
        # forcing both totals to add to 1
        if hitssum > 0: # can't divide by 0
            for page in self.pages:
                hits[page] /= hitssum
        if wordsum > 0: # can't divide by 0
            for page in self.pages:
                wordrank[page] /= wordsum
        # equalize HITS and WordRank scores
        hits_wr = {}
        wr_scores = sorted(wordrank.values())
        hits_scores = sorted(hits.values())
        for i in range(len(wordrank)):
            hits_wr[wr_scores[i]] = hits_scores[i]
        for page in wordrank:
            wordrank[page] = hits_wr[wordrank[page]]
        # creating ranks using both PageRank and WordRank, using hits_ratio to determine the weight of each
        for page in self.pages:
            self.ranks[page] = hits_ratio * hits[page] + (1 - hits_ratio) * wordrank[page]
            
    # Save the data
    def save(self, name):
        SearchEngine.save(self, name + 'HITSWR', dir_name=name)
    
    # Import previous data
    def import_data(self, name):
        try:
            import cPickle
            hits = open(os.getcwd() + '\\saves\\' + name + '\\' + name + 'HITS_ranks.PYTHON', 'rb')
            self.__temp = cPickle.load(hits)
            SearchEngine.import_data(self, name + 'HITSWR', dir_name=name)
        except:
            print 'No HITSWR file, importing default'
            SearchEngine.import_data(self, name, dir_name=name)
            self.__temp = {}
            if self.time == 0:
                self.compute_ranks()
                SearchEngine.sort_index(self)
                self.save(name)

def get_results(url, time, match_thresh=0.65, import_name='', keywords=''):
    while url.find('http://') != 0:
        url = raw_input('Re-enter link: ')
    x = SearchEngineHITSWR(url, time, match_threshold=match_thresh, word=keywords, import_name=import_name)
    return x 
    
# x.save('index_test', 'graph_test')
