# -*- coding: utf-8 -*-
from SPARQLWrapper import SPARQLWrapper, JSON

def GetDiseases():
    """
    Goes to DBPedia, search all diseases and puts in list.
    Requires: limit(int) - maximum number of diseases to be returned.
    Ensures: A list with a limit number of diseases, if set. Else it returns 
    a list of all diseases found.
    """
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")

    sparql.setQuery("""
    PREFIX dbo: <http://dbpedia.org/ontology/>

    SELECT ?diseasename ?personname ?deathdate ?deathplace ?dWiki ?field where {
            ?disease a dbo:Disease .
            ?person dbo:deathDate ?deathdate .
            ?disease dbp:field ?Medfield .
            ?person dbo:deathCause ?disease .
            ?person dbo:deathPlace ?deathPlace .
            ?disease prov:wasDerivedFrom ?dWiki .
            ?deathPlace rdfs:label ?deathplace FILTER (lang(?deathplace) = "en").
            ?disease rdfs:label ?diseasename FILTER (lang(?diseasename) = "en").
            ?person rdfs:label ?personname FILTER (lang(?personname) = "en").
            ?Medfield rdfs:label ?field FILTER (lang(?field) = "en")
            FILTER ((?deathdate > "1800-01-01"^^xsd:date) && (?deathdate < "1900-01-01"^^xsd:date)) .
            }
            """)

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    metList = []
    for data in results['results']['bindings']:
        metadata = {}
        metadata['disease'] = data['diseasename']['value']
        metadata['name'] = data['personname']['value']
        metadata['deathdate'] = data['deathdate']['value']
        metadata['deathplace'] = data['deathplace']['value']
        metadata['wiki'] = data['dWiki']['value']
        metadata['field'] = data['field']['value']
        metList.append(metadata)
    return metList

def writeMData(MList):
    output = open("metadata.txt", "w")
    for i in MList:
        for key, value in i.items():
            output.write('%s:%s\n' % (key, value))
    output.close()

def getData(fname):
    open_file = open(fname, "r")
    lista = open_file.readlines()
    i=0
    metadata = []
    while i < len(lista):
        nlista = []
        for item in lista[i:i+6]:
            nlista.append(item)
        metadata.append(nlista)
        i+=6
    disList = []
    meta = []
    for item in metadata:
        disease = item[0][8:-1]
        disList.append(disease)
        name = item[1][5:-1]
        meta.append(name)
        deathdate = item[2][10:-1]
        meta.append(deathdate)
        deathplace = item[3][11:-1]
        meta.append(deathplace)
        wiki = item[4][5:-1]
        meta.append(wiki)
        field = item[5][6:-1]
        meta.append(field)
    return (disList, meta)
