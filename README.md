This is the code for my 2013 Science Fair Project.

It was implemented in Python.

search_engine.py: contains search engine backbone, all others inherit from this file
search_engine_00.py: uses PageRank
search_engine_01.py: uses WordRank and PageRank, which was the combination that worked the best
search_engine_02.py: uses HITS
search_engine_03.py: uses WordRank and HITS

Beating Google: Development of the Web Page Ranking Algorithm WordRank in a Search Engine

Abstract

	Search engines rely on page ranking algorithms in order to return higher quality results to users. Some of the more widely used ranking algorithms, including HITS and Google’s PageRank, are dependent on a page’s popularity. However, this approach may not return relevant web pages when a user requires specific results instead of popular ones. This project is focused on the development of an algorithm named “WordRank” that will more effectively rank web pages so that a search engine can return more meaningful results, especially for specific queries. WordRank uses a web page’s content in order to assign ranks by taking in keywords from a user and using those keywords to assign scores to pages based on the number of times that word appears in the page’s content. WordRank was implemented in a Python search engine along with PageRank and HITS. A comparative analysis of PageRank, HITS, and WordRank was performed. It was found that when a combination of PageRank and WordRank was used in a 50:50 ratio, the quality scores and number of relevant links returned were overall the greatest. In addition, far superior results were returned when the combination was used on more specific keywords. Therefore, WordRank in conjunction with PageRank could potentially be used in a research search engine, which would benefit users who need high quality results to specialized queries.

Contact information:

Dennis Shim
hisroar@gmail.com
