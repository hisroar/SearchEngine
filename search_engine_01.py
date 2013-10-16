# PAGERANK WORDRANK

import urllib2
from search_engine import *
from search_engine_00 import *
from difflib import SequenceMatcher
from bs4 import BeautifulSoup
from random import random
from time import clock
from page import *

class SearchEnginePRWR(SearchEnginePR):
    
    def __init__(self, link, time, word='', match_threshold=0.65, d=0.85, numloops=10, pr_ratio=0.5, import_name='', page_stay=''):
        self.keywords = word.lower().split() # words that are desired on a webpage
        self.word = word
        self.wr = {} # WordRank scores
        self.pr = {} # PageRank scores
        self.pr_ratio = pr_ratio # weight of the PageRank scores (default 0.5)
        self.m_t = match_threshold # match threshold to have a matching word
        SearchEnginePR.__init__(self, link, time, match_threshold=match_threshold, import_name=import_name, page_stay=page_stay)
        if word: # only sort if there is a word
            self.compute_ranks(d=d, numloops=numloops, pr_ratio=pr_ratio)
            self.sort_index()
    
    # Compute the ranks of the pages
    def compute_ranks(self, d=0.85, numloops=10, pr_ratio=0.5): # returns ranks of the pages
        print 'Calculating ranks'
        if len(self.pr) == len(self.pages): # only compute PageRank if there are no scores
            self.wordrank(pr_ratio)
        else:
            self.pr = SearchEnginePR.pagerank(self, d, numloops)
            self.wordrank(pr_ratio)
        print 'Ranks finished'
    
    # Recalculate ranks only if necessary
    def change_ranks(self, d=0.85, numloops=10, pr_ratio=None):
        if pr_ratio == None: pr_ratio = self.pr_ratio
        if pr_ratio != self.pr_ratio:
            for page in self.pages:
                self.ranks[page] = pr_ratio * self.pr[page] + (1 - pr_ratio) * self.wr[page]
        elif numloops != 10 or d != 0.85:
            self.pr = SearchEnginePR.pagerank(self, d, numloops)
            self.wordrank(pr_ratio)
        self.sort_index()
    
    # Calculate the WordRank scores, and combine them with the PageRank scores
    def wordrank(self, pr_ratio):
        len_pages = len(self.pages)
        
        # WordRank, ranking pages based upon relevancy to keyword(s)
        for page in self.pages:
            self.wr[page] = 0
        
        len_keywords = len(self.keywords)
        for keyword in self.keywords:
            for page in self.pages:
                text_split = self.pages[page][1].split()
                len_text = len(text_split)
                for word in text_split:
                    rat_temp = SequenceMatcher(None, keyword, word).ratio()
                    if rat_temp > self.m_t:
                        self.wr[page] += rat_temp / len_text / len_keywords / len_pages
        
        pagesum = sum(self.pr.values())
        wordsum = sum(self.wr.values())
        
        # forcing both totals to add to 1
        if pagesum > 0: # can't divide by 0
            for page in self.pages:
                self.pr[page] /= pagesum
        if wordsum > 0: # can't divide by 0
            for page in self.pages:
                self.wr[page] /= wordsum
        # equalize PageRank and WordRank scores
        pr_wr = {}
        wr_scores = sorted(self.wr.values())
        pr_scores = sorted(self.pr.values())
        for i in range(len(self.wr)):
            pr_wr[wr_scores[i]] = pr_scores[i]
        for page in self.wr:
            self.wr[page] = pr_wr[self.wr[page]]
        # creating ranks using both PageRank and WordRank, using pr_ratio to determine the weight of each
        for page in self.pages:
            self.ranks[page] = pr_ratio * self.pr[page] + (1 - pr_ratio) * self.wr[page]
    
    # Save the data
    def save(self, name):
        SearchEngine.save(self, name + 'PRWR_' + self.word, dir_name=name)
        
    # Import previous data
    def import_data(self, name):
        try:
            SearchEnginePR.import_data(self, name)
            self.pr = self.ranks
        except IOError:
            print 'No PR file, importing default'
            SearchEngine.import_data(self, name, dir_name=name)

def get_results(url, time, keywords='', match_thresh=0.65, import_name=''):
    while url.find('http://') != 0:
        url = raw_input('Re-enter link: ')
    x = SearchEnginePRWR(url, time, match_threshold=match_thresh, word=keywords, import_name=import_name)
    return x 
    
# x.save('index_test', 'graph_test')
