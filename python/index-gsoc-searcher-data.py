"""
Requires an ElasticSearch server to be running.

python index-gsoc-search-data.py <dataDir> <elasticSearchUrl>
"""

import sys
import os
import urllib2
import re


INDEX_ID = "gsoc2013"
TYPE_ID = "d"


class RequestWithMethod(urllib2.Request):
    """Hack for forcing the method in a request - allows PUT and DELETE
    Ack: Eric S. Raymond
    http://benjamin.smedbergs.us/blog/2008-10-21/putting-and-deleteing-in-python-urllib2/#comment-430392
    """
    def __init__(self, method, *args, **kwargs):
        # This assignment works directly in older Python versions
        self._method = method
        urllib2.Request.__init__(self, *args, **kwargs)
    def get_method(self):
        # This method works in newer Pythons (2.6.5, possibly earlier).
        if self._method:
            return self._method
        elif self.has_data():
            return 'POST'
        else:
            return 'GET'

def analyzeKey(k):
    return k.replace("/", "_")

def iterDataPoints(dataDir):
    for fileName in [fn for fn in os.listdir(dataDir) if not fn.endswith(".text")]:
        fullPath = os.path.join(dataDir, fileName)
        with open(fullPath) as f:
            for line in f:
                url, prop, val = line.strip().split("\t")
                yield url, prop, val

def indexDataPoint(elasticSearchUrl, dataPoint):
    key, prop, val = dataPoint
    url = "%s/%s/%s/%s" % (elasticSearchUrl, INDEX_ID, TYPE_ID, analyzeKey(key))
    putJson = '{"%s":"%s"}' % (prop, val)
    print "Indexing in %s: %s" % (elasticSearchUrl, dataPoint)
    request = RequestWithMethod('PUT', url, data=putJson)
    answerJson = urllib2.urlopen(request).read()
    if not '"ok":true' in answerJson:
        print url, putJson
        print dataPoint, "failed indexation"
        sys.exit(1)


if __name__ == "__main__":
    dataDir = sys.argv[1]
    elasticSearchUrl = "http://localhost:9200"
    if len(sys.argv) == 3:
        elasticSearchUrl = re.sub("/$", "", sys.argv[2])

    for dataPoint in iterDataPoints(dataDir):
        indexDataPoint(elasticSearchUrl, dataPoint)

