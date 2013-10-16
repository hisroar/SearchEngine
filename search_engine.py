# Default Search Engine

from urllib import urlretrieve
from urllib2 import urlopen
from difflib import SequenceMatcher
from bs4 import BeautifulSoup
from random import random
from time import clock
from page import *
from subprocess import call
from collections import defaultdict
from Queue import Queue
import os
import sys
import argparse
import cPickle
#import requests


class SearchEngine:
    
    def __init__(self, link, time, match_threshold=0.65, import_name=None, page_stay=''):
        self.index = defaultdict(list)     # {<keyword> : [<list of urls that keyword was found in>]}
        self.ranks = {}                    # {<page> : <rank>}
        self.pages = {}                    # {<url> : [<list of outlinks>, <text of page>}
        self.page_stay = page_stay         # page to stay on (ie stay on USC's website only)
        #self.tocrawl = Queue()            # websites to crawl
        #tocrawl.put(link)
        self.tocrawl = [link]              # list of websites to crawl
        self.crawled = []                  # websites already crawled (don't crawl again)
        self.current_page = link
        self.thresh = match_threshold      # ratio for a word to 'match' (0 <= t <= 1)
        self.time = time                   # time to crawl
        if import_name:                    # import data from a previous crawl
            self.import_data(import_name)
        if time > 0:                       # don't re-sort if nothing added
            self.crawl_web(time)           # crawl the web
            self.compute_ranks()           # calculate the ranks
            self.sort_index()              # sort the index
            if import_name:                # save the crawled data
                self.save(import_name)
            else:
                x = raw_input('Save? [type save name if yes]: ')
                if x:
                    self.save(x)
    
    # Iterates throug the index and sorts each list of URLs
    def sort_index(self):
        print 'Sorting indices'
        for i in self.index:
            self.index[i] = self.sort_urls(self.index[i])
        print 'Done sorting'
    
#    def sort_urls(self, urls): # sort urls based upon rank using quicksort
#        if len(urls) <= 1:
#            return urls
#        pivot = urls.pop(int(random() * len(urls)))
#        low = []
#        high = []
#        pivot_rank = self.ranks[pivot]
#        for i in urls:
#            if self.ranks[i] <= pivot_rank:
#                low.append(i)
#            else:
#                high.append(i)
#        return self.sort_urls(high) + [pivot] + self.sort_urls(low)

    # Use python's sort function to sort each list of URLs by the ranks of the page
    def sort_urls(self, urls):
        return sorted(urls, key=lambda url: self.ranks[url], reverse=True)

    # Computes the ranks. In this case, assign each page a random number
    def compute_ranks(self): # returns ranks of the pages
        print 'Calculating ranks'
        for page in self.pages:
            self.ranks[page] = random()
        print 'Ranks finished'
        
    # Crawls the web for a certain period of time.
    def crawl_web(self, time):                                # returns index, graph of inlinks
        print 'Starting crawl'
        t = clock()                                           # initial time
        while self.tocrawl and clock() - t < time:            # loop when len(tocrawl) > 0 and deltatime > tFull
            url = self.tocrawl.pop(0)                         # take first page from tocrawl
            if url not in self.crawled:                       # check if page is not in crawled
                self.current_page = url
                html = self.get_text(url)                     # gets contents of page
                if html != '':
                    try:
                        soup = BeautifulSoup(html, 'lxml')    # parse with lxml (faster html parser)
                    except:                                   # parse with html5lib if lxml fails (more forgiving)
                        soup = BeautifulSoup(html, 'html5lib') 
                    try:
                        text = str(soup.get_text()).lower()   # convert from unicode
                    except:
                        text = soup.get_text().lower()        # keep as unicode
                    #try:
                    #    title = soup.title.string
                    #except:
                    #    pass #do nothing
                    outlinks = self.get_all_links(soup)       # get links on page
                    self.pages[url] = (tuple(outlinks), text) # creates new page object
                    self.add_page_to_index(url)               # adds page to index
                    self.union(self.tocrawl, outlinks)        # adds links on page to tocrawl
                    self.crawled.append(url)                  # add the url to crawled

        print 'Crawl finished'

    # Gets text of page from Internet using a PDF reader or urlopen
    def get_text(self, url): 
        f_name = url.split('/')[-1] # get file name
        try:
            if f_name.split('.')[-1] == 'pdf': # file type
                urlretrieve(url, os.getcwd() + '\\files\\' + f_name)
                call([os.getcwd() + '\\pdftotext.exe', os.getcwd() + '\\files\\' + f_name])
                return open(os.getcwd() + '\\files\\' + f_name.split('.')[0] + '.txt').read()
            else:
                return urlopen(url, None, 1).read()
        except:
            print 'bad link: ' + url    
            return ""
        
    # Iterates through the <a href=''> tags using BeautifulSoup to find the links
    def get_all_links(self, soup):
        links = []
        for link in soup.find_all('a'):
            linktemp = link.get('href')
            if linktemp: # can't have None
                try:
                    if str(linktemp)[-1] == '/': # strip the last slash
                        linktemp = linktemp[:-1]
                    parsed = self.parse_link(self.current_page, str(linktemp)) # parse the link
                    if str(linktemp).find('mailto') == -1: # don't grab emails
                        if self.page_stay: # add if the page is in page_stay
                            if self.page_stay in parsed:
                                links.append(parsed)
                        else: links.append(parsed)
                except:
                    pass # do nothing
        return links

    # Parses the link by removing #, or by appending to the link
    def parse_link(self, url, link):
        if '#' in link:
            return self.parse_link(url, link[:link.find('#')])
        if link.find('http') == 0:
            return link
        elif link[0:2] == '..':
            return self.parse_link(url[:url.rfind('/') + 1], link[3:])
        elif link[0] == '/':
            return url + link
        else:
            return url + '/' + link

    # Returns the union of two lists
    def union(self, a, b):
        for e in b:
            if e not in a:
                a.append(e)
    
    # Adds a whole page to the index
    def add_page_to_index(self, url):
        for keyword in self.pages[url][1].split():
            self.add_to_index(keyword, url)

    # Add a page to the list associated with a keyword
    def add_to_index(self, keyword, url):
        try:
            if url not in self.index[str(keyword)]:
                self.index[str(keyword)].append(url)
        except:
            if url not in self.index[keyword]:
                self.index[keyword].append(url)
#        for word in self.index:
#            if word == keyword:
#                if url not in self.index[word]:
#                    self.index[word].append(url)
#                return
#        # not found, add new keyword to index
#        try:
#            self.index[str(keyword)] = [url]
#        except:
#            self.index[keyword] = [url]
    
    # Lookup a keyword using the ranks; use: lookup(keyword)
    def lookup(self, keyword, to_print=True, print_times=10, exact_match=False, test=False):
        if exact_match:
            try:
                return self.index[keyword]
            except:
                print "No results for " + keyword
                return None
        elif test:
            links = []
            keyword = keyword.lower().split()[0]
            for i in self.index:
                if SequenceMatcher(None, keyword, i).ratio() > self.thresh:
                    self.union(links, self.index[i])
            links = self.sort_urls(links)
        else:
            links = []
            keyword = keyword.lower().split()[0]
            for i in self.index:
                if SequenceMatcher(None, keyword, i).ratio() > self.thresh:
                    links = self.merge(links, self.index[i])
        if to_print:
            self.print_lookup(links, print_times)
        else:
            return links

    # Merge two sorted lists of urls
    def merge(self, a, b):
        i, j = 0, 0
        x = []
        while i < len(a) and j < len(b):
            if a[i] == b[j]:
                x.append(a[i])
                i += 1
                j += 1
            elif self.ranks[a[i]] >= self.ranks[b[j]]:
                x.append(a[i])
                i += 1
            else:
                x.append(b[j])
                j += 1
        x += a[i:]
        x += b[j:]
        return x
            
    # Print the list returned by lookup
    def print_lookup(self, sorted_links, print_times):
        cont = 'y'
        i = 0
        links_len = len(sorted_links)
        while (cont == 'y' or cont == '') and i < links_len:
            print sorted_links[i]
            i += 1
            while i < links_len and i % 10 != 0:
                print sorted_links[i]
                i += 1
            if i < links_len:
                cont = raw_input('Display next 10 results? [y/n]: ')    

    # Save all the data using cPickle
    def save(self, name, dir_name=''):
        print 'Saving...'
        if dir_name == '': dir_name = name
        if not os.path.exists(os.getcwd() + '\\saves\\' + dir_name): os.makedirs(os.getcwd() + '\\saves\\' + dir_name)
        i = open(os.getcwd() + '\\saves\\' + dir_name + '\\' + name + '_index.PYTHON', 'wb')
        g = open(os.getcwd() + '\\saves\\' + dir_name + '\\' + name + '_graph.PYTHON', 'wb')
        tc = open(os.getcwd() + '\\saves\\' + dir_name + '\\' + name + '_tocrawl.PYTHON', 'wb')
        cd = open(os.getcwd() + '\\saves\\' + dir_name + '\\' + name + '_crawled.PYTHON', 'wb')
        r = open(os.getcwd() + '\\saves\\' + dir_name + '\\' + name + '_ranks.PYTHON', 'wb')
        cPickle.dump(self.index, i)
        cPickle.dump(self.pages, g)
        cPickle.dump(self.tocrawl, tc)
        cPickle.dump(self.crawled, cd)
        cPickle.dump(self.ranks, r)
        i.close()
        g.close()
        tc.close()
        cd.close()
        r.close()
        print 'Saved'
    
    # Import previously saved data
    def import_data(self, name, dir_name=''):
        if dir_name == '': dir_name = name
        print 'Loading...'
        i_in = open(os.getcwd() + '\\saves\\' + dir_name + '\\' + name + '_index.PYTHON', 'rb')
        g_in = open(os.getcwd() + '\\saves\\' + dir_name + '\\' + name + '_graph.PYTHON', 'rb')
        tc_in = open(os.getcwd() + '\\saves\\' + dir_name + '\\' + name + '_tocrawl.PYTHON', 'rb')
        cd_in = open(os.getcwd() + '\\saves\\' + dir_name + '\\' + name + '_crawled.PYTHON', 'rb')
        r_in = open(os.getcwd() + '\\saves\\' + dir_name + '\\' + name + '_ranks.PYTHON', 'rb')
        self.index = cPickle.load(i_in)
        self.pages = cPickle.load(g_in)
        self.tocrawl = cPickle.load(tc_in)
        self.crawled = cPickle.load(cd_in)
        self.ranks = cPickle.load(r_in)
        i_in.close()
        g_in.close()
        tc_in.close()
        cd_in.close()
        r_in.close()
        print 'Loaded'
        

#def main(argv=None):
#    try:
#        argv = sys.argv[1:]
#        x = SearchEngine(url, time, match_thresh)
#        x.save
    
    

def get_results(url, time, match_thresh=0.65, import_name='', page_stay = ''):
    while url != '' and url.find('http://') != 0:
        url = raw_input('Re-enter link: ')
    x = SearchEngine(url, time, match_thresh, import_name=import_name, page_stay=page_stay)
    return x 
    
# x.save('index_test', 'graph_test')
#if __name__ == '__main__':
#    sys.exit(main())