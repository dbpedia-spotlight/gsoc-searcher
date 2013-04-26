
## Client Side

This is the source code for the little app we created that allows people to browse Google Summer of Code (GSoC) projects.

<p>If you are curious about how we implemented this app, feel free to check our <a href="https://github.com/dbpedia-spotlight/dbpedia-spotlight-gsoc">source code</a> as well.</p>

<ol>
<li>Type-ahead suggestion is done via <a href="http://enable-cors.org">CORS-enabled</a> Ajax queries to <a href="http://lookup.dbpedia.org/">DBpedia Lookup</a>. This API takes in some phrase and searches the <a href="http://dbpedia.org">DBpedia</a> knowledge base to find possible meanings for this phrase. Once you pick one of those meanings, we store its unique identifier (URI) from DBpedia. The client side javascript uses <a href="http://code.drewwilson.com/entry/autosuggest-jquery-plugin">AutoSuggest jQuery Plugin by Drew Wilson</a>.
<li>Suggestion of related concepts is done via <a href="http://wiki.dbpedia.org/Downloads37#wikipediapagelinks">DBpedia's wikiPageLinks</a> and using <a href="http://wiki.dbpedia.org/spotlight/isem2011">DBpedia Spotlight's notion of resource relatedness</a>. For each of the URIs you have selected in step 1, we find all concepts linked to them via DBpedia properties. We add to that any other concepts that are "topically similar" according to DBpedia Spotlight. The wikiPageLinks dataset was loaded into a <a href="http://virtuoso.openlinksw.com">Virtuoso triple store</a>, in order to provide the "expand" functionality.
<li>
<!--Retrieval of projects is done via a <a href="http://www.w3.org/TR/rdf-sparql-query/">SPARQL query</a> over annotated projects stored in our <a href="http://spotlight.dbpedia.org/sparql">SPARQL endpoint</a>.-->
Retrieval and ranking is done via queries over annotated projects stored in an <a href="http://www.elasticsearch.org">elasticsearch</a> server. Projects were annotated with <a href="http://wiki.dbpedia.org/spotlight/usersmanual">DBpedia Spotlight's Web Service</a>.
<li>Results are displayed by the <a href="http://datatables.net/">DataTables jQuery plugin</a>.
</ol>

<p>DBpedia and DBpedia Spotlight <a href="http://www.google-melange.com/gsoc/org/google/gsoc2013/dbpediaspotlight">has been selected as an organization</a> for GSoC2013. If you have <a href="http://wiki.dbpedia.org/gsoc2013/ideas">project ideas</a> involving DBpedia or DBpedia Spotlight, please let us know, for example through our <a href="https://lists.sourceforge.net/lists/listinfo/dbpedia-gsoc">discussion list at SourceForge.net</a>.</p>

## Server Side

This demo relies on three Web services.

### DBpedia Lookup

[DBpedia Lookup](http://lookup.dbpedia.org) returns tags in the DBpedia knowledge base that match some string. For example, the query below searches for everything containing Berlin:

     curl "http://lookup.dbpedia.org/api/search.asmx/KeywordSearch?QueryClass=place&QueryString=berlin"

### DBpedia Spotlight's rel8 ###

DBpedia Spotlight models DBpedia "tags" based on their distributional similarity. Therefore we can use their service to give us related tags.

Testing the deployed demo

     curl -H "application/json" "http://spotlight.dbpedia.org/related/?uri=Berlin"

Getting the code 

     https://github.com/dbpedia-spotlight/dbpedia-spotlight/wiki/Installation
    
Starting the server

     mvn scala:run -DmainClass="org.dbpedia.spotlight.web.rest.RelatedResources"

Using the server

     curl -H "application/json" "http://localhost:2222/related/?uri=Berlin"

### ElasticSearch server ###

We use an [ElasticSearch](http://www.elasticsearch.org/) server to query data about the GSoC projects.

Once you started an ElasticSearch server, you can index the data with the `index-gsoc-searcher-data.py` script. The input for it is the output of the `extract-gsoc-searcher-data.py` script.

Then you can check if your development is working by visiting

     http://localhost:9200/gsoc2013/d/_search?q=*:*

### Data extraction ###

The data that is indexed in the ElasticSearch server was created using the `extract-gsoc-searcher-data.py` script with the GSoC organizations listing in CSV which can be retrieved at http://www.google-melange.com/gsoc/accepted_orgs/google/gsoc2013.

