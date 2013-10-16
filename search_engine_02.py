# HITS

import urllib2
from search_engine import *
from difflib import SequenceMatcher
from bs4 import BeautifulSoup
from random import random
from time import clock
from page import *

class SearchEngineHITS(SearchEngine):
    
    def __init__(self, link, time, match_threshold=0.65, numloops=10, import_name='', page_stay=''):
        
        SearchEngine.__init__(self, link, time, match_threshold=match_threshold, import_name=import_name, page_stay=page_stay)
        #self.compute_ranks(numloops)
        #SearchEngine.sort_index(self)

    # Compute the ranks of the pages
    def compute_ranks(self, numloops=10): # returns ranks of the pages
        print 'Calculating ranks'
        self.ranks = self.hits(numloops)
        print 'Ranks finished'
    
    # Compute the HITS scores
    def hits(self, numloops):
        len_pages = len(self.pages)
        authority = {}
        hub = {}
        
        # HITS
        
        # initialize scores to 1
        for page in self.pages: 
            authority[page] = 1.0
            hub[page] = 1.0
        
        for i in range(0, numloops):
            new_authority = {}
            new_hub = {}
            
            # authority score = hub score of page that links to the authority
            for page in authority:
                newrank = 0
                for i in hub:
                    if page in self.pages[i][0]:
                        newrank += hub[i]
                new_authority[page] = newrank
            authority = new_authority
            
            # divide by sum of squares of all authorities to normalize
            sumsq_authority = sum([i**2 for i in authority.values()]) ** 0.5
            for i in self.pages:
                authority[i] /= sumsq_authority

            
            # hub score = authority score of pages hub links to
            for page in hub:
                newrank = 0
                for i in self.pages[page][0]:
                    try: # not all pages have been crawled
                        newrank += authority[i]
                    except:
                        pass # do nothing
                new_hub[page] = newrank
            hub = new_hub   
            
            # divide by sum of squares of all hubs to normalize
            sumsq_hub = sum([i**2 for i in hub.values()]) ** 0.5
            for i in self.pages:
                hub[i] /= sumsq_authority
                
        
        both = {}
        for page in self.pages:
            both[page] = authority[page] + hub[page]
        return both

    # Save the data
    def save(self, name):
        SearchEngine.save(self, name + 'HITS', dir_name=name)
        
    # Import the data, and if HITS scores don't exists, calculate them
    def import_data(self, name):
        try:
            SearchEngine.import_data(self, name + 'HITS', dir_name=name)
        except:
            print 'No HITS file, importing default'
            SearchEngine.import_data(self, name, dir_name=name)
            if self.time == 0:
                self.compute_ranks()
                SearchEngine.sort_index(self)
                self.save(name)

def get_results(url, time, match_thresh=0.65, import_name=''):
    while url.find('http://') != 0:
        url = raw_input('Re-enter link: ')
    x = SearchEngineHITS(url, time, match_threshold=match_thresh, import_name=import_name)
    return x 
    
# x.save('index_test', 'graph_test')
