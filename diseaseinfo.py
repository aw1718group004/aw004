#-*- coding: utf-8 -*-
import urllib.request
from urllib.parse import quote
import xml.etree.ElementTree as ET
from SPARQLWrapper import SPARQLWrapper, JSON
from TwitterSearch import *
from annotation import *


# example in: https://rdflib.github.io/sparqlwrapper/
# needs to be installed with
# pip3 install SPARQLWrapper

def DBPediaDiseases(con):
    """
    Goes to DBPedia, search all diseases and puts in list.
    Requires: limit(int) - maximum number of diseases to be returned.
    Ensures: A file with a list with a limit number of diseases, if set. Else it returns 
    a list of all diseases found.
    """
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")

    sparql.setQuery("""
    PREFIX dbo: <http://dbpedia.org/ontology/> 
    SELECT ?name where {
            ?name a dbo:Disease . 
            }
        """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    curs = con.cursor() 
    for disease in results['results']['bindings']:
        uri = disease['name']['value']
        name = uri[28:] # http://dbpedia.org/resource/ has 28 characters        
        name = name.replace('_',' ').lower()
        curs.execute('SELECT L_ID FROM DiseaseList WHERE Name="{}";'.format(name))
        res = curs.fetchall()
        if len(res) == 0: 
            validity = GetAllMentions(name)
            if len(validity) != 0:
                curs.execute('INSERT INTO DiseaseList(Name, Valid) VALUES ("{}",1);'.format(name))
            else:
                curs.execute('INSERT INTO DiseaseList(Name, Valid) VALUES ("{}",0);'.format(name))

def GetDiseases(con,limit=None): #max 10000 diseases in dbpedia
    """
    Finds limit of diseases from dbpedia list in Diseases-dbpedia.txt - not anymore (now db)
    """
    diseaseNames = []
    curs = con.cursor()
    d_id = 1
    diseases = 0
    if limit != None:
        while diseases < limit:
            curs.execute( 'SELECT Name FROM DiseaseList WHERE L_ID="{}" AND Valid=1;'.format(d_id))
            name = curs.fetchall()
            if len(name)!=0:
                diseaseNames.append(name[0][0])
                diseases = diseases + 1
            d_id = d_id + 1
    else: #sem limite, o maximo é 10000
        curs.execute( 'SELECT Name FROM DiseaseList WHERE Valid=1;' )
        name = curs.fetchall()
        for disease_name in name:
            diseaseNames.append(disease_name[0])
    print('Disease list is ready!')
    return diseaseNames

def GetIDs(name, limit): #GUARDAR EM TABELA
    """
    Requires: A disease name. 
    Ensures: A list of Articles Id's, related to the disease.
    """
    #getting things out of a URL: https://docs.python.org/3/howto/urllib2.html
    try:
        with urllib.request.urlopen('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term='+quote(name)+'&retmax='+str(limit)) as response: #retmax = nº de Id's que se pretende
            xml = response.read().decode('utf-8')
    except Exception as e:
        print(e)
        return []
    root = ET.fromstring(xml)

    idlist = []
    for id in root.iter('Id'):
        idlist.append(id.text)
    return (idlist)

def GetTitleAbst(id):
    """
    Requires: a list of Articles' Id's.
    Ensures: returns a tuple with a string and a list.
    """    
    with urllib.request.urlopen('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id='+str(id)+'&retmode=text&rettype=xml') as response: 
        xml = response.read().decode('utf-8')
    root = ET.fromstring(xml)
    titulo = ""
    for title in root.iter('ArticleTitle'):    
        titulo = title.text
    lastnames = []
    inits = []
    for name in root.iter('LastName'):
        if name.text != None:
            lastnames.append(name.text)
        else:
            lastnames.append('')
    for initials in root.iter('Initials'):
        if name.text != None:
            inits.append(initials.text)
        else:
            inits.append('')
    authors = ''
    if len(lastnames) > len(inits):
        for i in range(len(lastnames) - len(inits)):
            inits.append('')
    for i in range(len(lastnames)):
        if  lastnames[i] != '' and i == (len(lastnames)-1):
            authors = authors + lastnames[i] + ' ' + inits[i] # we don't need the comma
        elif lastnames[i] != '':
            authors = authors + lastnames[i] + ' ' + inits[i] + ', '
    parag = []        
    for abstract in root.iter('Abstract'):
        for paragraph in root.iter('AbstractText'):
            if paragraph.text != None:
                parag.append(paragraph.text)
    monthDict= {'jan':'01', 'feb':'02', 'mar':'03', 'apr':'04', 'may':'05', 'jun':'06',\
                'jul':'07', 'aug':'08', 'sep':'09', 'oct':'10', 'nov':'11', 'dec':'12'}     
    #year-month-day
    try:
        month = root.find('.//PubmedArticle/MedlineCitation/Article/Journal/JournalIssue/PubDate/Month').text
        if month == '00':
            month = 'jan'
    except:
        month = 'jan' #if we don't know the month, just suppose it is january    
    try:
        year = root.find('.//PubmedArticle/MedlineCitation/Article/Journal/JournalIssue/PubDate/Year').text
        if year == '0000':
            year = '0001'
    except:
        year = '0001'
    if month.lower() in monthDict.keys():
        month_nr = monthDict[month.lower()]
        date_pub = '-'.join([year, month_nr, '01']) #01 for day because we don't have a day of publication
    else:
        date_pub = '0001-01-01'
    
    return titulo, parag, date_pub, authors

def GetImgs(name):
    '''
    Flickr Search.
    From: http://joequery.me/code/flickr-api-image-search-python/
    '''
    with urllib.request.urlopen('https://api.flickr.com/services/rest/?method=flickr.photos.search&api_key=36956e3fe91cfeda5c05cf74dc9b1e84&text='+quote(name)+'&per_page=10&privacy_filter=1') as response: 
        xml = response.read()
    root = ET.fromstring(xml)
    listurl = []
    for photo in root.iter('photo'):
        id = photo.get('id')
        secret = photo.get('secret')
        server = photo.get('server')
        farm = photo.get('farm')       
        listurl.append([id,'https://farm'+farm+'.staticflickr.com/'+server+'/'+id+'_'+secret+'_q.jpg'])
    urltags = []    
    for url in listurl[:10]:
        try:
            with urllib.request.urlopen('https://api.flickr.com/services/rest/?method=flickr.photos.getInfo&api_key=36956e3fe91cfeda5c05cf74dc9b1e84&photo_id='\
            +str(url[0])+'&privacy_filter=1') as response:
                xml = response.read()
            root = ET.fromstring(xml)
            datelist = []
            for content in root.iter('dates'):
                date = content.get('taken')
                urldate = date[:10]
            listtags = []
            for content in root.iter('tag'):
                for i in root.iter('tag'):
                    tag = i.get('raw')
                    listtags.append(tag.replace('#','').lower())
            urltags.append([url[1],listtags,urldate])  #lista com url e lista de tags
        except:
            urltags.append([url[1],[],'0001-01-01'])
    return(urltags)

def GetTweets(name):
    '''
    Search for tweets related to the disease.
    Ensures: a list of lists [[url, tweet_text]]
    
    If Too Many Requests Error, returns TwitterSearchException class object.
    '''
    try:
        tso = TwitterSearchOrder() # create a TwitterSearchOrder object
        tso.set_keywords([name]) # define all words we would like to have a look for
        tso.set_language('en') 
        tso.set_include_entities(False) # don't give us all those entity information
        ts = TwitterSearch(consumer_key = 'JQ1WqJue1UK73qtvnk50HWze7',
                           consumer_secret = 'QUHd4IZiPEveucrJpQAkpgLVMdwGfOBL2W0zuQUp5aaDxCBHGW',
                           access_token = '975712055113256960-Axj6e2031N1qd0OlqrcyeTCB09ue6rM',
                           access_token_secret = 'CnlJlHDVqYouqkxmMyUyaz1SGlenrDhRXsPdOGg74GZUs')
        listturl = []
        for tweet in ts.search_tweets_iterable(tso):
            id = tweet['id']
            date = tweet['created_at']
            month = date[4:7]
            day = date[8:10]
            year = date[-4:]
            monthDict= {'Jan':'01', 'Feb':'02', 'Mar':'03', 'Apr':'04', 'May':'05', 'Jun':'06',\
                'Jul':'07', 'Aug':'08', 'Sep':'09', 'Oct':'10', 'Nov':'11', 'Dec':'12'}        
            #year-month-day
            month_nr = monthDict[month]
            date_pub = '-'.join([year, month_nr, day]) #01 for day because we don't have a day of publication  
            id = str(id)
            tweet_text = tweet['text']
            listturl.append(['http://twitter.com/'+id+'/status/'+id, tweet_text, date_pub])
        new_listurl = []
        for i in listturl[:10]:
            new_listurl.append(i)
        return new_listurl
    except Exception as e:
        print(e)
        