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
MAPPING = """{
  "d" : {
    "properties" : {
      "ideas" : {
        "type" : "string",
        "store" : "yes"
      },
      "linkId" : {
        "type" : "string",
        "store" : "yes"
      },
      "name" : {
        "type" : "string",
        "store" : "yes"
      },
      "tagged" : {
        "type" : "string",
        "store" : "yes"
      },
      "taggedString" : {
        "type" : "string",
        "store" : "yes"
      },
      "textTagged" : {
        "type" : "string",
        "store" : "yes"
      }
    }
  }
}"""


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

def iterOrgData(dataDir):
    d = {}  # group org data
    for fileName in [fn for fn in os.listdir(dataDir) if not fn.endswith(".text")]:
        fullPath = os.path.join(dataDir, fileName)
        with open(fullPath) as f:
            for line in f:
                key, prop, val = line.strip().split("\t")
                d.setdefault(key, []).append((prop, val))
    for k, vals in d.iteritems():
        yield k, vals

def wipeIndex(elasticSearchUrl):
    print "Wiping index %s" % elasticSearchUrl
    url = "%s/%s" % (elasticSearchUrl, INDEX_ID)
    try:
        print urllib2.urlopen(RequestWithMethod('DELETE', url)).read()
    except urllib2.HTTPError, err:
        if err.code != 404:
            raise  # none existed
    urllib2.urlopen(RequestWithMethod('PUT', url)).read()

def setMapping(elasticSearchUrl):
    url = "%s/%s/%s/_mapping" % (elasticSearchUrl, INDEX_ID, TYPE_ID)
    print urllib2.urlopen(RequestWithMethod('PUT', url, data=MAPPING)).read()

def indexOrgData(elasticSearchUrl, orgData):
    key, vals = orgData
    print "Indexing in %s: %s" % (elasticSearchUrl, key)
    url = "%s/%s/%s/%s" % (elasticSearchUrl, INDEX_ID, TYPE_ID, analyzeKey(key))
    data = '{' + ",".join(['"%s":"%s"' % (prop, val) for prop, val in vals]) + '}'
    answerJson = urllib2.urlopen(RequestWithMethod('PUT', url, data=data)).read()
    if not '"ok":true' in answerJson:
        print url, data
        print orgData, "failed indexation"
        sys.exit(1)

def flushIndex(elasticSearchUrl):
    url = "%s/_flush" % (elasticSearchUrl)
    print urllib2.urlopen(RequestWithMethod('POST', url)).read()

if __name__ == "__main__":
    dataDir = sys.argv[1]
    elasticSearchUrl = "http://localhost:9200"
    if len(sys.argv) == 3:
        elasticSearchUrl = re.sub("/$", "", sys.argv[2])

    wipeIndex(elasticSearchUrl)
    setMapping(elasticSearchUrl)

    for orgData in iterOrgData(dataDir):
        indexOrgData(elasticSearchUrl, orgData)

    flushIndex(elasticSearchUrl)

