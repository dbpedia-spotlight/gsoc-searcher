import csv
import re
import urllib
import urllib2
import sys
from boilerpipe.extract import Extractor


csvInput = sys.argv[1]

ns = "http://spotlight.dbpedia.org/gsoc/vocab#"
objectProperty = ns + "tagged"
textTaggedProperty = ns + "textTagged"
datatypeProperty = ns + "taggedString"
keyProperty = ns + "key"
nameProperty = ns + "name"
linkIdProperty = ns + "linkId"

#urlPrexfixLookup = "http://lookup.dbpedia.org/api/search.asmx/KeywordSearch?QueryString="
#urlPrefixSpotlight = "http://spotlight.dbpedia.org/rest/annotate?disambiguator=Document&support=-1&confidence=-1"
urlPrefixSpotlight = "http://spotlight.sztaki.hu:2222/rest/annotate?"


def ntLiterals(s, p, o):
    return "<"+s+"> <"+p+'> "'+o+'"@en .'

def ntObject(s, p, o):
    return "<"+s+"> <"+p+"> <"+o+"> ."

def tsvFields(s, p, o):
    return s + "\t" + p.replace(ns, "") + "\t" + o


serializer = tsvFields

def iterGsoc(csvFileName):
    """Generator for the parsed lines.
    """
    skippedFirst = False
    with open(csvFileName) as csvFile:
        for els in csv.reader(csvFile, delimiter=",", quotechar='"'):
            if not skippedFirst:
                skippedFirst = True
                continue

            key = els[0]
            name = els[1]
            linkId = els[2]
            tags = [t.replace("_", " ").strip() for t in els[3:-1][0].split(",")]
            ideasUrl = els[-1]

            yield (key, name, linkId, tags, ideasUrl)


def printProperties(ideasUrl, key, name, linkId):
    """General properties.
    """
    print serializer(ideasUrl, keyProperty, key)
    print serializer(ideasUrl, nameProperty, name)
    print serializer(ideasUrl, linkIdProperty, linkId)

def printTags(tags):
    """Tags as strings.
    """
    for tag in tags:
        if tag.strip():
            print serializer(ideasUrl, datatypeProperty, tag)

def _urisFromUrl(url, timeout=10, data=None):
    sys.stderr.write("  request: "+url[:120]+"\n")
    """
    req = urllib2.urlopen(ideasHtml)
    encoding = getEncoding(req)
    contents = unicode(req.read(), encoding)
    """

    acceptJson = {"Accept": "application/json"}
    if data:
        request = urllib2.Request(url, headers=acceptJson, data=data)
    else:
        request = urllib2.Request(url, headers=acceptJson)
    contents = urllib2.urlopen(request, timeout=timeout).read()
    return re.findall('"@URI": "(.*?)",', contents)

def printDisambigTags(tags):
    """Disambiuated tags.
    """
    uris = []
    """
    if len(tags) == 1 and tags[0].strip() and tags[0].count(" ") < 3:
        query = urllib.quote(tags[0].strip())
        url = urlPrexfixLookup + query
        sys.stderr.write(url+"\n")
        contents = urllib2.urlopen(url).read()
        sys.stderr.write(contents+"\n")
        m = re.search('<ArrayOfResult.*<URI>(.*?)</URI>,', contents)
        if m:
            uris = [m.group(0)]
    else:
    """
    if tags[0].strip():
        #query = urllib.quote("[[" + "]], [[".join(tags) + "]]")
        query = urllib.quote("; ".join(tags))
        url = urlPrefixSpotlight + "&text=" + query
        uris = _urisFromUrl(url)

    for uri in uris:
        print serializer(ideasUrl, objectProperty, uri)

def printTextEntities(ideasUrl):
    """Disambiguated entities from the ideas page.
    """
    url = urlPrefixSpotlight + "&url=" + ideasUrl
    try:
        uris = _urisFromUrl(url)
    except urllib2.HTTPError:
        sys.stderr.write("404!!!!!!!!!!!!!!!!!!\n")
        extractor = Extractor(extractor='ArticleExtractor', url=ideasUrl)
        text = urllib.quote_plus(extractor.getText().replace("\n", "  ").encode("utf-8"))
        postParams = urllib.urlencode({"text": text}) 
        uris = _urisFromUrl(urlPrefixSpotlight, timeout=30, data=postParams)
    for uri in uris:
        print serializer(ideasUrl, textTaggedProperty, uri)


if __name__ == "__main__":
    for key, name, linkId, tags, ideasUrl in iterGsoc(csvInput):
        sys.stderr.write(ideasUrl + "\n")
        printProperties(ideasUrl, key, name, linkId)
        printTags(tags)
        printDisambigTags(tags)
        printTextEntities(ideasUrl)



