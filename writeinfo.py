# -*- coding: utf-8 -*-
from diseaseinfo import *
from annotation import *
import pymysql as pms
import os.path
from SPARQLWrapper import SPARQLWrapper, JSON

DBUSER = 'aw004'
DBPASS = 'mcca2018'
DBHOST = 'appserver-01.alunos.di.fc.ul.pt'

DISEASE_NUMBER = 100
ID_NUMBER = 15

def CreateConnection():
    con=pms.connect(host=DBHOST, user=DBUSER, passwd=DBPASS, db=DBUSER, autocommit=True, charset='utf8')
    return con

#replace mysql.server with "localhost" if you are running via your own server!
#server MySQL username MySQL pass Database name.

def DropTables(con):
    curs = con.cursor()
    curs.execute("DROP TABLE IF EXISTS Pictures;")
    curs.execute("DROP TABLE IF EXISTS Tweets;")
    curs.execute("DROP TABLE IF EXISTS Flickr;")
    curs.execute("DROP TABLE IF EXISTS Twitter;")
    curs.execute("DROP TABLE IF EXISTS Articles;")
    curs.execute("DROP TABLE IF EXISTS PubMed;")
    curs.execute("DROP TABLE IF EXISTS DBPedia;")
#    curs.execute("DROP TABLE IF EXISTS Metadata;")
#    curs.execute("DROP TABLE IF EXISTS DiseaseList;")
#    curs.execute("DROP TABLE IF EXISTS UniProt;")
    curs.execute("DROP TABLE IF EXISTS GeneInfo;")
    curs.execute("DROP TABLE IF EXISTS Diseases;")
    #curs.execute("DROP TABLE IF EXISTS Ontologies;")

def CreateTables(con):
    '''
    '''
    curs = con.cursor() 
#    curs.execute("CREATE TABLE DiseaseList(L_ID INT AUTO_INCREMENT, Name VARCHAR(250), Valid BIT, PRIMARY KEY(L_ID));")
    curs.execute("CREATE TABLE Diseases(D_ID INT AUTO_INCREMENT, Name VARCHAR(250), ArticlesNumber INT, PicsNumber INT, TweetsNumber INT, PRIMARY KEY(D_ID));")
    curs.execute("CREATE TABLE PubMed(A_ID INT, Title VARCHAR(300), Authors VARCHAR(1000), Abstract TEXT, Date DATE, TermCount TEXT, PRIMARY KEY (A_ID));")
    #Articles: considering that date can be order of publication 1,2,3... and Explicit can be 0 if user clicks Xremove publication and then multiplied to the sum of other parameters or something
    curs.execute("CREATE TABLE Articles(D_ID INT, A_ID INT, TF FLOAT, IDF FLOAT, TFIDF FLOAT, DiShIn FLOAT, Explicit FLOAT, Implicit FLOAT, Date INT, TOTAL FLOAT, FOREIGN KEY (D_ID) REFERENCES Diseases(D_ID) ON DELETE CASCADE ON UPDATE CASCADE, FOREIGN KEY (A_ID) REFERENCES PubMed(A_ID) ON DELETE CASCADE ON UPDATE CASCADE, PRIMARY KEY(D_ID, A_ID));")
    
    curs.execute("CREATE TABLE Flickr(F_ID INT AUTO_INCREMENT, F_URL VARCHAR(400), Tags TEXT, Date DATE, TermCount TEXT, PRIMARY KEY (F_ID));")
    curs.execute("CREATE TABLE Pictures(D_ID INT, F_ID INT, TF FLOAT, IDF FLOAT, TFIDF FLOAT, DiShIn FLOAT, Explicit FLOAT, Implicit FLOAT, Date INT, TOTAL FLOAT, FOREIGN KEY (D_ID) REFERENCES Diseases(D_ID) ON DELETE CASCADE ON UPDATE CASCADE, FOREIGN KEY (F_ID) REFERENCES Flickr(F_ID) ON DELETE CASCADE ON UPDATE CASCADE, PRIMARY KEY(D_ID, F_ID));")
    
    curs.execute("CREATE TABLE Twitter(T_ID INT AUTO_INCREMENT, T_URL VARCHAR(400), Tweet VARCHAR(300), PostDate DATE, TermCount TEXT, PRIMARY KEY (T_ID));")
    curs.execute("CREATE TABLE Tweets(D_ID INT, T_ID INT, TF FLOAT, IDF FLOAT, TFIDF FLOAT, DiShIn FLOAT, Explicit FLOAT, Implicit FLOAT, Date INT, TOTAL FLOAT, FOREIGN KEY (D_ID) REFERENCES Diseases(D_ID) ON DELETE CASCADE ON UPDATE CASCADE, FOREIGN KEY (T_ID) REFERENCES Twitter(T_ID) ON DELETE CASCADE ON UPDATE CASCADE, PRIMARY KEY(D_ID, T_ID));")
    
    #curs.execute("CREATE TABLE Metadata(DiseaseName VARCHAR(250), M_ID INT AUTO_INCREMENT, name VARCHAR (64), deathdate DATE, deathplace VARCHAR (128), wiki VARCHAR(400), field VARCHAR (64), PRIMARY KEY(M_ID));")
    curs.execute("CREATE TABLE DBPedia(D_ID INT, M_ID INT, PRIMARY KEY(D_ID, M_ID), FOREIGN KEY(D_ID) REFERENCES Diseases(D_ID), FOREIGN KEY(M_ID) REFERENCES Metadata(M_ID));")
    
#    curs.execute("CREATE TABLE UniProt(DiseaseName VARCHAR(250), G_ID INT AUTO_INCREMENT, GeneLabel VARCHAR(36), gene VARCHAR(400), NCBIgeneID INT, PRIMARY KEY(G_ID));")
    curs.execute("CREATE TABLE GeneInfo(D_ID INT, G_ID INT, PRIMARY KEY(D_ID, G_ID), FOREIGN KEY(D_ID) REFERENCES Diseases(D_ID), FOREIGN KEY(G_ID) REFERENCES UniProt(G_ID));")
    curs.execute("CREATE TABLE Ontologies(O_ID INT, Disease1 VARCHAR(250), Disease2 VARCHAR(250), DiShIn FLOAT, PRIMARY KEY(O_ID));")    
    
    #set coding as utf-8   
    curs.execute("ALTER TABLE UniProt CONVERT TO CHARACTER SET utf8;")
    curs.execute("ALTER TABLE GeneInfo CONVERT TO CHARACTER SET utf8;")
    curs.execute("ALTER TABLE Diseases CONVERT TO CHARACTER SET utf8;")
    curs.execute("ALTER TABLE Articles CONVERT TO CHARACTER SET utf8;")
    curs.execute("ALTER TABLE PubMed CONVERT TO CHARACTER SET utf8;")
    curs.execute("ALTER TABLE Flickr CONVERT TO CHARACTER SET utf8;")
    curs.execute("ALTER TABLE Twitter CONVERT TO CHARACTER SET utf8;")
    curs.execute("ALTER TABLE Metadata CONVERT TO CHARACTER SET utf8;")
    curs.execute("ALTER TABLE DBPedia CONVERT TO CHARACTER SET utf8;")
    curs.execute("ALTER TABLE DiseaseList CONVERT TO CHARACTER SET utf8;")
    curs.execute("ALTER TABLE Pictures CONVERT TO CHARACTER SET utf8;")
    curs.execute("ALTER TABLE Tweets CONVERT TO CHARACTER SET utf8;")
  #  curs.execute("ALTER TABLE Ontologies CONVERT TO CHARACTER SET utf8;")

def InsertDisease(con,name):
    '''
    Inserts a disease in the database
    Requires: A list with the diseases' names.
    Ensures: A table with the names of the diseases and respective ID's.
    '''
    curs = con.cursor()
    curs.execute('INSERT INTO Diseases(Name) VALUES ("{}");'.format(name))

def GetMetadata(con):
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
            ?person dbo:deathCause ?disease .
            ?disease rdfs:label ?diseasename FILTER (lang(?diseasename) = "en").
            ?person rdfs:label ?personname FILTER (lang(?personname) = "en").
            OPTIONAL {?person dbo:deathPlace ?deathPlace .
                     ?deathPlace rdfs:label ?deathplace FILTER (lang(?deathplace) = "en").}
            OPTIONAL {?disease dbp:field ?Medfield .
                      ?Medfield rdfs:label ?field FILTER (lang(?field) = "en").}
            OPTIONAL {?disease prov:wasDerivedFrom ?dWiki .}
            OPTIONAL {?person dbo:deathDate ?deathdate .
                      FILTER ((?deathdate > "1800-01-01"^^xsd:date) && (?deathdate < "2018-01-01"^^xsd:date)) .}
            }
            limit 10000
            """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    curs = con.cursor()
    for data in results['results']['bindings']:
        diseasename = data['diseasename']['value']
        name= data['personname']['value']
        if ("deathdate" in data):
            deathdate = data['deathdate']['value']
        else:
            deathdate = str(deathdate)
            deathdate = ""
        if ("deathplace" in data):
            deathplace = data['deathplace']['value'] 
        else:
            deathplace = ""
        if ("dWiki" in data):
            wiki = data['dWiki']['value'] 
        else:
            wiki = ""
        if ("field" in data):
            field = data['field']['value']
        else:
            field = ""
        name = str(name.encode('utf-8'))
        name = name.replace('"','')
        name = name.replace('\'','')
        name = name[1:]
        diseasename =  str(diseasename.encode('utf-8'))
        diseasename =  diseasename[2:-1]
        if deathdate != "":
            deathdate = str(deathdate.encode('utf-8'))
            deathdate = deathdate[2:-1]
        if deathplace != "":
            deathplace = str(deathplace.encode('utf-8'))
            deathplace = deathplace[2:-1]
        if wiki != "":
            wiki = str(wiki.encode('utf-8'))
            wiki = wiki[2:-1]
        if field != "":
            field = str(field.encode('utf-8'))
            field = field[2:-1]
        curs.execute('SELECT name FROM Metadata WHERE name="{}";'.format(name))
        res = curs.fetchall()
        if len(res) == 0:
            try:
                try:
                    curs.execute('INSERT INTO Metadata(DiseaseName, name, deathdate, deathplace, wiki, field) VALUES ("{}","{}","{}","{}","{}","{}");'.format(diseasename, name, deathdate, deathplace, wiki, field))
                except Exception as ex:
                    print(ex.value)
                    continue
            except:
                print('SQL error - check for \" and \' ')
                continue
        
def CreateDBPedia(con):
    '''
    Inserts metadata.
    Requires: con, a connection to access the database; mlista, list with the metadata related to a disease; dlista, list with the diseases' names.
    Ensures: A table with the names of the diseases and respective ID's.
    '''
    curs = con.cursor()
    curs.execute("DROP TABLE IF EXISTS DBPedia;")
    curs.execute("CREATE TABLE DBPedia AS SELECT D_ID, M_ID FROM Diseases, Metadata WHERE Diseases.Name = Metadata.DiseaseName;")
            
def CreateSortAlphabetically(con):
    '''
    Creates a table with the correspondency between the diseases' D_ID's and a new SA_ID ordered.
    Requires: con, a connection to access the database;
    Ensures: a table with the diseases' D_ID's ordered alphabetically and a new respective SA_ID.
    '''
    curs = con.cursor()
    curs.execute("DROP TABLE IF EXISTS SortAlphabeticalDis;")
    curs.execute("CREATE TABLE SortAlphabeticalDis (SA_ID INT AUTO_INCREMENT, D_ID INT, PRIMARY KEY(SA_ID)) AS SELECT d.D_ID FROM Diseases d ORDER BY d.Name ASC;")
     
def GetUniProt(con):
    '''
    SPARQL Query adapted from https://github.com/sebotic/SPARQL/blob/master/uniprot_sparql.md
    '''
    #weird url encoding requires extreme measures: % added to query to find new lines 
    query='\
    PREFIX up: <http://purl.uniprot.org/core/>%\
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>%\
    PREFIX wd: <http://www.wikidata.org/entity/>%\
    PREFIX p: <http://www.wikidata.org/prop/>%\
    PREFIX v: <http://www.wikidata.org/prop/statement/>%\
    PREFIX q: <http://www.wikidata.org/prop/qualifier/>%\
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>%\
    %\
    %\
    SELECT ?gene ?geneLabel ?wdncbi ?start ?stop ?disease_text WHERE {    %\
        SERVICE <https://query.wikidata.org/sparql> {    %\
    %\
            ?gene wdt:P351 ?wdncbi ;%\
                  wdt:P703 wd:Q15978631;%\
                  rdfs:label ?geneLabel ;%\
                  p:P644 ?geneLocStart ;%\
                  p:P645 ?geneLocStop ;%\
                  wdt:P688 ?wd_protein .%\
                  %\
            ?geneLocStart v:P644 ?start .%\
            ?geneLocStart q:P659 wd:Q20966585 . %\
                  %\
            ?geneLocStop v:P645 ?stop .%\
            ?geneLocStop q:P659 wd:Q20966585 . %\
     % \
            ?wd_protein wdt:P352 ?uniprot_id .%\
    %\
    %\
    		FILTER (LANG(?geneLabel) = "en") .%\
        }%\
        BIND(IRI(CONCAT("http://purl.uniprot.org/uniprot/", ?uniprot_id)) as ?protein)%\
            ?protein up:annotation ?annotation .%\
            ?annotation a up:Disease_Annotation .%\
            ?annotation up:disease ?disease_annotation .%\
            ?disease_annotation <http://www.w3.org/2004/02/skos/core#prefLabel> ?disease_text .%\
       %\
    }%\
      '             
    
   
    #fixing url
    query = quote(query).replace('%20', '+')
    query = query.replace('/', '%2f')
    query = query.replace('%3C', '<')
    query = query.replace('%3E', '>')
    query = query.replace('%7D', '}')
    query = query.replace('%7B','{')
    query = query.replace('%25','%0D%0A')
    url = "https://sparql.uniprot.org/sparql?query="
    url = url + query + '&format=srj'
    with urllib.request.urlopen(url) as response: 
            jsonStr = response.read().decode('utf-8')
            response = json.loads(jsonStr)
    
    
    curs = con.cursor()
    for data in response['results']['bindings']:
        geneLabel = data['geneLabel']['value']
        gene = data['gene']['value']
        wdncbi = data['wdncbi']['value']
        disease_text = data['disease_text']['value'].lower()
                
        try:
            curs.execute('INSERT INTO UniProt(DiseaseName, GeneLabel, gene, NCBIgeneID) VALUES ("{}","{}","{}","{}");'.format(disease_text, geneLabel, gene, wdncbi ))
        except Exception as ex:
            print(str(ex)) 
                   
def CreateGeneInfo(con):
    '''
    Inserts gene info metadata.
    Requires: con, a connection to access the database; 
    Ensures: A table with the names of the diseases and respective G_ID's.
    '''
    curs = con.cursor()
    curs.execute("DROP TABLE IF EXISTS GeneInfo;")
    curs.execute("CREATE TABLE GeneInfo AS SELECT D_ID, G_ID FROM Diseases, UniProt WHERE UniProt.DiseaseName like concat(Diseases.Name, '%');") 

def InsertPub(con,name):
    '''
    Inserts article information
    Requires: A list with the diseases' names.
    Ensures: A table with the names of the diseases and respective ID's.
    '''
    curs = con.cursor()
    curs.execute('SELECT D_ID FROM Diseases WHERE Name="{}";'.format(name))
    res = curs.fetchall()
    d_id = res[0][0]
    ids = GetIDs(name, ID_NUMBER)
    if ids != []:
        for item in ids:
            curs.execute('SELECT COUNT(A_ID) FROM Articles WHERE D_ID="{}";'.format(d_id))
            articles = curs.fetchone()
            num_articles = articles[0]
            if num_articles <10:
                title, abstr, date, authors = GetTitleAbst(item)
                if abstr != [] and title != [] and title !=None:
                    abstr = '\n'.join(abstr)
                    abstr = abstr.replace('"','')
                    title = title.replace('"','')
                    text = ' '.join([title,abstr])
                    mentions = GetAllMentions(text, item)
                    mentionscount = CountMentions(mentions)
                    
                    try: #assim tambem nao repete entradas... 
                        curs.execute('INSERT INTO PubMed(A_ID, Title, Authors, Abstract, Date, TermCount) VALUES ("{}","{}","{}","{}","{}","{}");'.format(item,title,authors,abstr,date, mentionscount))
                        curs.execute('INSERT INTO Articles (D_ID, A_ID, TF, IDF, TFIDF, DiShIn, Explicit, Implicit, Date, TOTAL) VALUES ("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}");'.format(d_id,item, 0,0,0,0,1,0,0,0))
        
                    except Exception as e:
                        if 'Duplicate entry' not in str(e): #se nao e um artigo que ja esta na db
                            num_articles = num_articles - 1
                        else:
                            try:
                                curs.execute('INSERT INTO Articles (D_ID, A_ID, TF, IDF, TFIDF, DiShIn, Explicit, Implicit, Date, TOTAL) VALUES ("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}");'.format(d_id,item, 0,0,0,0,1,0,0,0))
                            except:
                                pass
#                    WriteArticleDishin(con, item)
                else:
                    continue
            curs.execute('update Diseases set ArticlesNumber="{}" where D_ID="{}";'.format(num_articles,d_id))
    else:
        #curs.execute("INSERT INTO PubMed(D_ID, A_ID, Title) VALUES ('{}','{}','{}','{}');".format(d_id,item,title,abstr)) 
        curs.execute('update Diseases set ArticlesNumber=0 where D_ID="{}";'.format(d_id))

    
def InsertFlickr(con,name):
    '''
    Inserts picture information
    Requires: A list with the diseases' names.
    Ensures: A table with the names of the diseases and respective ID's.
    '''
    curs = con.cursor()
    curs.execute('SELECT D_ID FROM Diseases WHERE Name="{}";'.format(name))
    res = curs.fetchall()
    d_id = res[0][0]
    urls = GetImgs(name)
    if urls !=[]:
        for item in urls:
            try:
                tags = ', '.join(item[1])
                date = (item[2])
                mentions = GetAllMentions(tags)
                mentionscount = CountMentions(mentions)
                curs.execute('SELECT F_URL FROM Flickr WHERE F_URL="{}";'.format(item[0]))
                res = curs.fetchall()
                if len(res)==0:
                    curs.execute('INSERT INTO Flickr(F_URL, Tags, Date, TermCount) VALUES ("{}","{}","{}","{}");'.format(item[0], tags, date, mentionscount))
                curs.execute('SELECT F_ID FROM Flickr WHERE F_URL="{}";'.format(item[0]))
                r = curs.fetchall()
                num_id = r[0][0]
                curs.execute('INSERT INTO Pictures(D_ID, F_ID, TF, IDF, TFIDF, DiShIn, Explicit, Implicit, Date, TOTAL) VALUES ("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}","{}");'.format(d_id, num_id, 0,0,0,0,1,0,0,0))
    #            WriteFlickrDishin(con, num_id,  mentionscount)
            except Exception as ex:
                print(ex)
            
            curs.execute('SELECT COUNT(F_ID) FROM Pictures WHERE D_ID="{}";'.format(d_id))
            pictures = curs.fetchone()
            num_pics = pictures[0]
            curs.execute('update Diseases set PicsNumber="{}" where D_ID="{}";'.format(num_pics, d_id))
    else:
        curs.execute('SELECT COUNT(F_ID) FROM Pictures WHERE D_ID="{}";'.format(d_id))
        pictures = curs.fetchone()
        num_pics = pictures[0]
        curs.execute('update Diseases set PicsNumber="{}" where D_ID="{}";'.format(num_pics, d_id))

def InsertTweet(con, name):
    '''
    Inserts tweets
    Requires: A list with the diseases' names.
    Ensures: A table with the names of the diseases and respective ID's.
    '''
    curs = con.cursor()
    curs.execute('SELECT D_ID FROM Diseases WHERE Name="{}";'.format(name))
    res = curs.fetchall()
    d_id = res[0][0]
    try:
        tweets = GetTweets(name) #Too Many Requests returns
        for item in tweets:
            try:
                curs.execute('SELECT T_URL FROM Twitter WHERE T_URL="{}";'.format(item[0]))
                res = curs.fetchall()
                if len(res)==0:
                    item[1] = item[1].replace('\'','')
                    item[1] = item[1].replace('"','')
                    tweet_mentions = item[1].replace('#',' ') # so that it counts hashtags
                    
                    mentions = GetAllMentions(tweet_mentions)
                    mentionscount = CountMentions(mentions)
                    
                    curs.execute('INSERT INTO Twitter (T_URL, Tweet, PostDate, TermCount) VALUES ("{}","{}","{}","{}");'.format(item[0], item[1], item[2], mentionscount))
                curs.execute('SELECT T_ID FROM Twitter WHERE T_URL="{}";'.format(item[0]))
                r = curs.fetchall()
                num_id = r[0][0]
                curs.execute('INSERT INTO Tweets (D_ID, T_ID, TF, IDF, TFIDF, DiShIn, Explicit, Implicit, Date, TOTAL) VALUES ("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}");'.format(d_id, num_id, 0,0,0,0,1,0,0,0))
#                WriteTwitterDishin(con, num_id, mentionscount)
            except Exception as ex:
                print(ex)
        curs.execute('SELECT COUNT(T_ID) FROM Tweets WHERE D_ID="{}";'.format(d_id))
        tweets = curs.fetchone()
        num_tweets = tweets[0]
        curs.execute('update Diseases set TweetsNumber="{}" where D_ID="{}";'.format(num_tweets,d_id))
    except Exception as e:
        print("Tweet Error")
        try:
            if type(tweets)==list and len(tweets)==0:
                curs.execute('update Diseases set TweetsNumber=0 where D_ID="{}";'.format(d_id)) #else, leave it at NULL, no action required
        except Exception as ex:
            print(ex)
     
def UpdateDisease(con,name):
    '''
    It does things.
    Requires: the name of an awful disease.
    Ensures: not sure yet, some kind of update, if it works'''
    curs = con.cursor()
    curs.execute('SELECT D_ID, ArticlesNumber, PicsNumber, TweetsNumber FROM Diseases WHERE Name="{}";'.format(name))
    res = curs.fetchall()
       
    if len(res) == 0: 
        InsertDisease(con,name)
        InsertPub(con,name)
        InsertFlickr(con,name)
        InsertTweet(con,name)
        CreateDBPedia(con)
        CreateGeneInfo(con)
    else:
        d_id = res[0][0]
        articles = res[0][1]
        pics = res[0][2]
        tweets = res[0][3]
        #select count(a_id) from Diseases d LEFT OUTER JOIN PubMed p ON p.d_id = d.d_Id where (d.articles = 1 OR d.articles IS NULL) AND d.d_id = 1 GROUP BY p.d_id
        if articles==None or articles>0:
            count = curs.execute('SELECT count(a.A_ID) FROM Articles a WHERE a.D_ID="{}" GROUP BY a.A_ID;'.format(d_id))
            if count != articles:
                InsertPub(con,name)
            
            count = curs.execute('SELECT count(F_ID) FROM Pictures WHERE D_ID="{}" GROUP BY F_ID;'.format(d_id))
            if count != pics:
                InsertFlickr(con,name)
                
            count = curs.execute('SELECT count(T_ID) FROM Tweets WHERE D_ID="{}" GROUP BY T_ID;'.format(d_id))
            if count != tweets:
                print('updating tweets!')
                InsertTweet(con,name)
                
            count = curs.execute('SELECT count(D_ID) FROM DBPedia WHERE D_ID="{}";'.format(d_id))
            count = curs.fetchall()
            if count == 0:
                CreateDBPedia(con)
            count = curs.execute('SELECT count(D_ID) FROM GeneInfo WHERE D_ID="{}";'.format(d_id))
            count = curs.fetchall()
            if count == 0:
                CreateGeneInfo(con)

def UpdateCrawler(limit, annotations=False):
    '''
    Update our Disease web crawler.
    '''
    con = CreateConnection() 
    curs = con.cursor()   
    curs.execute('SELECT count(*) FROM DiseaseList;')
    num_diseases = curs.fetchall()
    if num_diseases[0][0]<10000:  # 10000 - numero de doencas na dbpedia
        DBPediaDiseases(con)
    curs.execute('SELECT count(*) FROM Metadata;')
    count = curs.fetchall()
    if count[0][0] == 0: 
        GetMetadata(con)  
    curs.execute('SELECT count(*) FROM UniProt;')
    count = curs.fetchall()
    if count[0][0] == 0: 
        GetUniProt(con) 
    diseases = GetDiseases(con,limit)
    for item in diseases:
        UpdateDisease(con,item)
        print('.', end='')
    if annotations==True:
        UpdateAnnotations(con)
        UpdateTotals(con)

def UpdateArticlesTFIDF(con):
    """
    Inserts on CalcTFIDF
    """
    curs = con.cursor()
    curs.execute('SELECT D_ID, A_ID FROM Articles;')
    articles = curs.fetchall()        
    for tuples in articles:
        CalcTFIDF(con, tuples[0], tuples[1], 'Articles')  

def UpdateTweetsTFIDF(con):
    """
    Inserts on CalcTFIDF
    """
    curs = con.cursor()
    curs.execute('SELECT D_ID, T_ID FROM Tweets;')
    tweets = curs.fetchall()        
    for tuples in tweets:
        CalcTFIDF(con, tuples[0], tuples[1], 'Tweets')  

def UpdatePicsTFIDF(con):
    """
    Inserts on CalcTFIDF
    """
    curs = con.cursor()
    curs.execute('SELECT D_ID, F_ID FROM Pictures;')
    pics = curs.fetchall()        
    for tuples in pics:
        CalcTFIDF(con, tuples[0], tuples[1], 'Pictures')
 
def UpdateAnnotations(con):    #Update annotations
    '''
    Updates annotations.
    Requires: con, an open connection to appserver.
    Ensures: Annotations are updated.
    '''
    print('\nChecking annotations...')    
    UpdateTFPubMed(con)
    UpdateTFFlickr(con)
    UpdateTFTwitter(con)
    CalcIDFPubMed(con)
    CalcIDFTweets(con)
    CalcIDFFlickr(con)
    UpdateArticlesTFIDF(con)
    UpdateTweetsTFIDF(con)
    UpdatePicsTFIDF(con)
    #UpdateDishin(con)
    OrdDateAllArticles(con)
    OrdDateAllTweets(con)
    OrdDateAllPictures(con)

def UpdateTotals(con):
    print('\nRecalculating totals...')
    UpdateTotalArticles(con)
    UpdateTotalPictures(con)
    UpdateTotalTweets(con)
