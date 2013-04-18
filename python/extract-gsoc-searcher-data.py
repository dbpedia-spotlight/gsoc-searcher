import os.path
import csv
import codecs
import re
import urllib
import urllib2
import socket
import sys
from boilerpipe.extract import Extractor


csvInput = sys.argv[1]
DATA_DIR = "data"
CHUNKS_SIZE = 300

ns = "http://spotlight.dbpedia.org/gsoc/vocab#"
objectProperty = ns + "tagged"
textTaggedProperty = ns + "textTagged"
datatypeProperty = ns + "taggedString"
ideasHtmlProperty = ns + "ideas"
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


def getDataPath(fileName):
    if not os.path.isdir(DATA_DIR):
        os.mkdir(DATA_DIR)
    return os.path.join(DATA_DIR, fileName)

def save(path, content):
    with open(path, "a") as f:
        f.write(content + "\n")


def iterGsoc(csvFileName):
    """Generator for the parsed lines.
    """
    with open(csvFileName) as csvFile:
        for els in list(csv.reader(csvFile, delimiter=",", quotechar='"'))[1:]:
            key = els[0]
            name = els[1]
            linkId = els[2]
            tags = [t.replace("_", " ").strip() for t in els[3:-1][0].split(",")]
            ideasUrl = els[-1]

            if not key.strip() or not ideasUrl.strip():
                sys.stdout.write("** skipping %s %s\n" % (key, ideasUrl))
                continue

            yield (key, name, linkId, tags, ideasUrl)


def saveProperties(path, key, ideasUrl, name, linkId):
    """General properties.
    """
    save(path, serializer(key, ideasHtmlProperty, ideasUrl))
    save(path, serializer(key, nameProperty, name))
    save(path, serializer(key, linkIdProperty, linkId))

def saveTags(path, key, tags):
    """Tags as strings.
    """
    for tag in tags:
        if tag.strip():
            save(path, serializer(key, datatypeProperty, tag))

def _urisFromUrl(url, timeout=30, data=""):
    sys.stdout.write("  request: " + url[:120] + data[:30] + "...\n")
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

def saveDisambigTags(path, key, tags):
    """Disambiuated tags.
    """
    uris = []
    """
    if len(tags) == 1 and tags[0].strip() and tags[0].count(" ") < 3:
        query = urllib.quote(tags[0].strip())
        url = urlPrexfixLookup + query
        sys.stdout.write(url+"\n")
        contents = urllib2.urlopen(url).read()
        sys.stdout.write(contents+"\n")
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
        save(path, serializer(key, objectProperty, uri))

def _chunk(seq, size):
    return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))

def saveTextEntities(path, key, ideasUrl):
    """Disambiguated entities from the ideas page.
    """
    try:
        url = urlPrefixSpotlight + "&url=" + ideasUrl
        uris = _urisFromUrl(url)
    except (urllib2.HTTPError, socket.timeout) as e:
        sys.stdout.write("    produced %s\n" % e)
        textPath = path.replace(".tmp", "") + ".text"
        if os.path.isfile(textPath):
            sys.stdout.write("      reading text from disk\n")
            with codecs.open(textPath, "r", "utf-8") as textFile:
                text = textFile.read().encode("utf-8")
        else:
            sys.stdout.write("      will do boilerplate and chunking\n")
            sys.stdout.write("        getting %s\n" % ideasUrl)
            extractor = Extractor(extractor='ArticleExtractor', url=ideasUrl)
            text = extractor.getText().replace("\n", "  ").encode("utf-8")
            with open(textPath, "w") as textFile:
                textFile.write(text)

        uris = []
        for c in _chunk(re.split("\s+", text), CHUNKS_SIZE):
            postParams = urllib.urlencode({"text": " ".join(c)}) 
            try:
                uris.extend(_urisFromUrl(urlPrefixSpotlight, timeout=120, data=postParams))
            except socket.timeout:
                sys.stdout.write("    query for chunk timed out\n")

    for uri in uris:
        save(path, serializer(key, textTaggedProperty, uri))


if __name__ == "__main__":
    for key, name, linkId, tags, ideasUrl in iterGsoc(csvInput):
        sys.stdout.write(linkId + " " + ideasUrl)

        fileName = getDataPath(linkId)
        if os.path.exists(fileName):
            sys.stdout.write("   exists\n")
            continue
        sys.stdout.write("\n")

        tmpFileName = getDataPath(linkId + ".tmp")
        with open(tmpFileName, "w") as f:
            f.write("")

        saveProperties(tmpFileName, key, ideasUrl, name, linkId)
        saveTags(tmpFileName, key, tags)
        saveDisambigTags(tmpFileName, key, tags)
        saveTextEntities(tmpFileName, key, ideasUrl)

        os.rename(tmpFileName, fileName)

