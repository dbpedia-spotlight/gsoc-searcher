## DBpedia links

Currently, this directory only contains links from DBpedia to various
datasets that describe either the projects which have participated in GSoC,
or the software that they produce.

### sourceforge-doap.nt

This contains links to the DOAP that Sourceforge provides for each project
it hosts. The data was extracted from Wikipedia, which uses a 'SourceForge'
template to generate external links for such projects.

For example, the article on [Apertium](http://en.wikipedia.org/wiki/Apertium) 
contains this usage of the template:

```
* {{SourceForge|apertium|Apertium}}
```

The first parameter is the name of the project, the second is the title to
display on the external link; the link to be generated is

```
http://sourceforge.net/api/project/name/$PARAM1/doap
```

### dbpedia-rdfohloh.nt

[RDFohloh](http://rdfohloh.wikier.org/about) is a live RDFizer of the API
provided by [Ohloh](http://www.ohloh.net/). RDFohloh is an Open Source
project, whose code may be downloaded from 
[the Google Code project](https://code.google.com/p/rdfohloh/).

The current links were manually created. Ohloh provides an API, but it is 
limited, and only allows searching for projects based on name, description, 
and tags, so query by homepage is not possible. 

### dbpedia-debian.nt

This is a set of links to Debian's [RDF Interface](http://wiki.debian.org/qa.debian.org/pts/RdfInterface)
which provides a description of each source package.

The full dataset is currently only available to Debian members, but it may
be possible to either run an RDF spider, or to re-generate the data from
the package database.
