# -*- coding: utf-8 -*-

import urllib.request
from urllib.parse import quote
import json
from math import *
import ast #para passar string a dicionario
from collections import OrderedDict
from datetime import datetime
import subprocess
import ssm

def GetMer(text):
    '''
    Finds disease names in a given text using GetMER API.
    Requires: text as string. For PubMed articles ensure that it contains the title.
    Ensures: list where each element is a string with 3 comma separated values:
    start position, end position and disease name. If no disease found, returns 
    an empty list.
    '''
    #instalar awk: sudo apt-get install gawk
    #tirar premissões dos sh metendo-os em executaveis: chmod +x ./get_entities.sh e em todos os outros sh
    result = subprocess.getoutput('(cd MER; ./get_entities.sh "'+text+'" doid-simple )')
    #print(result)

    #remove last space, and separate values with commas and by line:  
    #and make sure it is all lowercase
    results = result.strip().replace('\t',',').lower().split('\n')  
    #print(results)
    
    if results == ['']:
        return []
    else:
        return results
    
#print(GetMer('Asthma is a disease, Cancer is life'))

def GetDOID(dname):
    '''
    Finds DOID by Human Disease Ontology.
    Requires: dname as string
    Ensures: the DOID.
    '''
    link = subprocess.getoutput("(cd MER; ./get_entities.sh '"+dname+"' doid-simple | ./link_entities.sh data/doid-simple.owl | sort | uniq)")
    a = link.split('\t')
    b = a[0].split('/')
    doid = b[-1]
    return doid
    
def GetPubTator(PMID): # for PubMed articles only !
    '''
    Finds disease names in an abstract from an article given its PMID resorting
    to PubTator.
    Requires: Article PMID as int.
    Ensures: list where each element is a string with 3 comma separated values:
    start position, end position and disease name. If no disease found, returns 
    an empty list.    
    '''
    url = 'https://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/RESTful/tmTool.cgi/Disease/'+str(PMID)+'/JSON/'
    
    with urllib.request.urlopen(url) as response:
        jsonStr = response.read().decode('utf-8')
    print('jsonStr:', jsonStr)
    j = json.loads(jsonStr)
#    print (j)
    
    results = []
    onts = {} #so we don't look up the same disease and waste time
    for data in j['denotations']:
        diseasecode = data['obj'][-7:]
        if diseasecode not in onts.keys():
            #and make sure it is all lowercase
            if GetOntName(diseasecode) != None:
                onts[diseasecode] = GetOntName(diseasecode).lower()  
            else:
                continue
        diseasename = onts[diseasecode]
        begin = data['span']['begin']
        end = data['span']['end']
#        print(diseasecode, begin, end)
        results.append(','.join([str(begin), str(end), diseasename]))
        
    return results

def GetBioPortal(text):
    '''
    Ensures: list where each element is a string with 3 comma separated values:
    start position, end position and disease name. If no disease found, returns 
    an empty list.
    '''
    text = quote(text)     #prepare encoding for url
    
    API_KEY = '2fcd5b1f-7cf8-4957-b936-bf9b905558e5'
    url = 'http://data.bioontology.org/annotator?text='+text+'&ontologies=PDO&apikeytoken='+API_KEY
#    print(url)
    opener = urllib.request.build_opener()
    opener.addheaders = [('Authorization', 'apikey token=' + API_KEY)]
    try:
        annotations = json.loads(opener.open(url).read())
    #    print(annotations)
        term_list = []
        for result in annotations:
            for annotation in result["annotations"]:
                #print(annotation)
    
                term = ",".join([str(annotation["from"]), str(annotation["to"]), annotation["text"].lower()])
                if term not in term_list:
                    term_list.append(term)
    except:
        term_list = []
                
#    print(term_list)
    return term_list

def GetOntName(diseasecode):
    '''
    Corresponds a disease name to a given MeSH code.
    Requires: disease code as string (format: D000000 where 0 can be any number)
    Ensures: name of the disease as a string.
    
    '''
    #https://hhs.github.io/meshrdf/sparql-and-uri-requests
    if diseasecode[0] == 'D':
        url = 'http://id.nlm.nih.gov/mesh/'+diseasecode+'.json'
        with urllib.request.urlopen(url) as response:
            jsonStr = response.read().decode('utf-8')
            
        data = json.loads(jsonStr)
    #    print (data)
        for j in data['@graph']: #just so we get over that list
    #        print(j)
    #        print(j['label']['@value'])
            return j['label']['@value']  #there is only one value anyway


def GetAllMentions(text, pubmed=None):
    '''
    Retrieves all disease mentions from MER, PubTator and possibly Bioportal Annotator
    in the future from a given text.
    Requires: text as string (if from PubMed article ensure that it contains the title),
    and int pubmed that should only be provided if text is a PubMed article.
    Ensures: list with all disease mentions where each element is a string with
    3 comma separated values: start position, end position and disease name. 
    If no disease found, returns an empty list
    '''
#    print('doença:', text)
    mer = GetMer(text)
    if type(pubmed)==int:
        pubtator = GetPubTator(pubmed)
    else:
        pubtator = []
    bioportal = GetBioPortal(text)  
    #Sets are unordered collections of distinct objects
    allmentions = list(set(mer + pubtator + bioportal))
#    print(mer)
#    print('+++++++++++++++++++++++++++++++++++++++++')
#    print(pubtator)
#    print('+++++++++++++++++++++++++++++++++++++++++')
#    print(bioportal)
#    print('+++++++++++++++++++++++++++++++++++++++++')
#    print(len(mer),len(pubtator),len(allmentions))
#    print(allmentions)
#    print('+++++++++++++++++++++++++++++++++++++++++')
    return allmentions
   
#a = GetAllMentions('Asthma is a disease, Cancer is life')
#print(a)

def CountMentions(mentions):
    '''
    Counts how many times each disease was mentioned from a given list showing where 
    each word appears in a text.
    Requires: mentions - a list with all disease mentions where each element is a
    string with 3 comma separated values: start position, end position and disease name. 
    Ensures: a dictionary with disease names and correponding number of times it 
    appears on the text.
    '''
    counts = {}
    for item in mentions:
        if '/bin/sh' not in item and 'grep' not in item and 'awk: line' not in item:
            disease = item.split(',')[2] # item.split(',') -> [start, end, disease]
    #        print(disease)
            if disease in counts.keys():
                counts[disease] += 1
            else:
                counts[disease] = 1
#    print(counts)
    return counts
          
def CalcTF(mentionscount):
    '''
    Calculates TF for all diseases in a given text.
    Requires: mentionscount as a dictionary.
    Ensures: a dictionary with disease names and correponding term frequency
    (tf value) in the text provided.
    '''
#    mentions = GetAllMentions(text)
#    mentionscount = CountMentions(mentions) #agora j� guard�mos isto antes na base de dados
#    print(mentionscount)

    #Calculate tf for all diseases:
    tf_all = {}
    #t - term; d - document  
    #sum_ntd - sum of occurrences of all t's in d
    sum_ntd = sum(mentionscount.values())
#    print('sum_ntd = ', sum_ntd)

    for disease in mentionscount.keys():
  
        all_terms = disease.lower().split()
        ntd = mentionscount[disease.lower()]#ntd - number of occurrences of t in d 
        if len(all_terms) > 1:
            for t in all_terms:
#                print(t)
                if t in mentionscount.keys():
#                    print(mentionscount[t])
                    ntd += mentionscount[t]
        if sum_ntd != 0:
            tf = ntd/sum_ntd #calculate tf (term frequency)
            tf_all[disease] = tf
                       
    return tf_all
#print(CalcTF({'asthma':1, 'abdominal obesity':2, 'cancer':3}))
#print(CalcTF({'r':0}))

def CalcIDFPubMed(con): #falta testar
    '''
    Calculate IDF = log(total number of documents/number of documents for diseasename)
    -- PubMed table
    '''
    curs = con.cursor()
    curs.execute('SELECT COUNT(A_ID) FROM PubMed;')
    total_articles = curs.fetchone()
    curs.execute('SELECT D_ID FROM Diseases;')
    diseases = curs.fetchall()
    total_articles = total_articles[0]
    for d_id in diseases:
        nr_articles_disease = curs.execute('SELECT ArticlesNumber FROM Diseases WHERE D_ID="{}";'.format(d_id[0]))
        nr_articles_disease = curs.fetchone()
        nr_articles_disease = nr_articles_disease[0]
        if nr_articles_disease != 0:
            idf = log(total_articles/nr_articles_disease)
        else:
            idf = 0 
        curs.execute('UPDATE Articles set IDF="{}" where D_ID="{}";'\
                             .format(idf,d_id[0]))                
    return idf
  

def CalcIDFTweets(con): #falta testar
    '''
    Calculate IDF = log(total number of documents/number of documents for diseasename)
    -- Tweets table
    '''
    curs = con.cursor()
    curs.execute('SELECT COUNT(T_ID) FROM Twitter;')
    total_tweets = curs.fetchone()
    curs.execute('SELECT D_ID FROM Diseases;')
    diseases = curs.fetchall()
    total_tweets = total_tweets[0]
    for d_id in diseases:
        nr_tweets_disease = curs.execute('SELECT TweetsNumber FROM Diseases WHERE D_ID="{}";'.format(d_id[0]))
        nr_tweets_disease = curs.fetchone()
        nr_tweets_disease = nr_tweets_disease[0]
        if nr_tweets_disease != 0 and nr_tweets_disease != None:
            idf = log(total_tweets/nr_tweets_disease)
        else:
            idf = 0 
        curs.execute('UPDATE Tweets set IDF="{}" where D_ID="{}";'\
                             .format(idf,d_id[0]))                
    return idf



def CalcIDFFlickr(con): #falta testar
    '''
    Calculate IDF = log(total number of documents/number of documents for diseasename)
    -- Tweets table
    '''
    curs = con.cursor()
    curs.execute('SELECT COUNT(F_ID) FROM Flickr;')
    total_pics = curs.fetchone()
    curs.execute('SELECT D_ID FROM Diseases;')
    diseases = curs.fetchall()
    total_pics = total_pics[0]
    for d_id in diseases:
        nr_pics_disease = curs.execute('SELECT PicsNumber FROM Diseases WHERE D_ID="{}";'.format(d_id[0]))
        nr_pics_disease = curs.fetchone()
        nr_pics_disease = nr_pics_disease[0]
        if nr_pics_disease != 0:
            idf = log(total_pics/nr_pics_disease)
        else:
            idf = 0 
        curs.execute('UPDATE Pictures set IDF="{}" where D_ID="{}";'\
                             .format(idf,d_id[0]))                
    return idf


def CalcTFIDF(con, D_ID, Table_ID, tablename): #Est� a dar erro
    '''
    Calculates TFIDF = TF * IDF
    Requires: D_ID, the disease name in the table;
    Table_ID, the other primary key component; 
    tablename must be either Articles or Tweets or Pictures
    Ensures: The TFIDF = TF * IDF.
    '''    
    curs = con.cursor()
    #Select TF and IDF
    if tablename == 'Articles':
        curs.execute('SELECT TF, IDF FROM Articles WHERE D_ID="{}" AND A_ID="{}";'.format(D_ID, Table_ID))
    elif tablename == 'Tweets':
        curs.execute('SELECT TF, IDF FROM Tweets WHERE D_ID="{}" AND T_ID="{}";'.format(D_ID, Table_ID))
    elif tablename == 'Pictures':
        curs.execute('SELECT TF, IDF FROM Pictures WHERE D_ID="{}" AND F_ID="{}";'.format(D_ID, Table_ID))
        
    #Calculate TFIDF 
    TFandIDF = curs.fetchall()   
    TF = TFandIDF[0][0]
    IDF = TFandIDF[0][1]      
    TFIDF = TF * IDF    
    
    #insert TFIDF
    if tablename == 'Articles':
        curs.execute('UPDATE Articles set TFIDF="{}" where D_ID="{}" and A_ID="{}";'\
                             .format(TFIDF, D_ID, Table_ID))
    elif tablename == 'Tweets':
        curs.execute('UPDATE Tweets set TFIDF="{}" where D_ID="{}" and T_ID="{}";'\
        .format(TFIDF, D_ID, Table_ID))
    elif tablename == 'Pictures':
        curs.execute('UPDATE Pictures set TFIDF="{}" where D_ID="{}" and F_ID="{}";'\
        .format(TFIDF, D_ID, Table_ID))
    
    
    curs.execute('UPDATE Articles set TFIDF="{}" where D_ID="{}" and A_ID="{}";'\
                             .format(TFIDF,D_ID, Table_ID))
    
def GetDiShIn(dname1, dname2,con):
    sb_file = 'doid.db'
    curs = con.cursor()
    diseasenames = sorted([dname1,dname2]) # tem de estar por ordem alfabetica para par nao estar repetido na lista
    dname1=diseasenames[0]
    dname2=diseasenames[1]
    count = curs.execute('SELECT count(O_ID) FROM Ontologies WHERE Disease1="{}" and Disease2="{}";'.format(dname1, dname2))
    if count !=0: #count so pode ser 0 ou 1

        # Calculate the similarity 
        ssm.semantic_base(sb_file)
        name1 = GetDOID(dname1)
        name2 = GetDOID(dname2)
        # Similarity between terms
        e1 = ssm.get_id(name1)
        e2 = ssm.get_id(name2)
        
        if e1>0 and e2>0:
            ssm.intrinsic = True
                                        
            # ontology with multiple inheritance 
            ssm.mica = False
            ResDis = ssm.ssm_resnik (e1,e2)
            #print("Resnik \t DiShIn \t intrinsic \t"+ str(ResDis))
            
    #        print(str(ResDis))
        curs.execute('INSERT INTO Ontologies VALUES ("{}","{}", "{}" );'.format(dname1, dname2, str(ResDis)))
        return str(ResDis)
        
    else:
        ResDis = curs.execute('SELECT DiShIn FROM Ontologies WHERE Disease1="{}" and Disease2="{}";'.format(dname1, dname2))
        return ResDis[0][0]
    
    
    

#GetDiShIn('asthma', 'allergy',con)

def WriteTFPubMed(con, PMID, tf_all): 
    '''
    '''
    curs = con.cursor()
#    print(PMID, tf_all.keys())
    for disease in tf_all.keys():
#        print(disease, tf_all[disease])
#        print(disease, PMID)
        #1st check if disease exists in Diseases
        curs.execute('SELECT D_ID FROM Diseases WHERE Name="{}";'.format(disease))
        d_id = curs.fetchall()
        if len(d_id) != 0: #if it does: check if article is connected to disease
            d_id = d_id[0][0]
#            print('D_ID ', d_id)
            curs.execute('''SELECT a.D_ID, a.A_ID, a.TF FROM Articles a, Diseases d
                         WHERE d.Name="{}" and d.D_ID=a.D_ID and a.A_ID="{}";'''\
                         .format(disease, PMID))
            artdis = curs.fetchall()
            if len(artdis) == 0: #if it does not, add to articles table and add tf as well
                curs.execute('INSERT INTO Articles (D_ID, A_ID, TF, IDF, TFIDF, DiShIn, Explicit, Implicit, Date, TOTAL) VALUES ("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}");'.format(d_id,PMID,tf_all[disease],0,0,0,1,0,0,0))

                num_articles = curs.execute('SELECT COUNT(A_ID) FROM Articles WHERE D_ID="{}" GROUP BY A_ID;'.format(d_id))
#                print(num_articles)
                curs.execute('update Diseases set ArticlesNumber="{}" where D_ID={};'.format(num_articles,d_id))
            elif artdis[0][2] == None or artdis[0][2] == 0:   #else if it is null just add tf to articles 
#                print('null artdis')
#                print('tf to update:', tf_all[disease])
                curs.execute('UPDATE Articles set TF="{}" where D_ID="{}" and A_ID="{}";'\
                             .format(tf_all[disease],d_id,PMID))
                
            
            #otherwise the correct value should be there already
 

def UpdateTFPubMed(con):
    '''
    Update TF for each article related to each disease.
    '''
    curs = con.cursor()
    curs.execute('Select A_ID, Title, Abstract From PubMed;')
    res = curs.fetchall()
 #   print(res)
    for PMID in res:  
        text = ' '.join([PMID[1],PMID[2]])
        #print(text)
        curs.execute('SELECT TermCount From PubMed Where A_ID="{}";'.format(PMID[0]))
        termcount = curs.fetchall()
        #print(termcount)
        mentionscount = ast.literal_eval(termcount[0][0])
        
        
        #Select all diseases related to the article that are not in the dictionary and add them there
        # with a mention count of 0
        curs.execute('SELECT d.Name FROM Diseases d, Articles a WHERE a.A_ID="{}" and a.D_ID=d.D_ID;'.format(PMID[0]))
        disease_names = curs.fetchall()
        for d in disease_names[0]:
#            print (d)
            if d not in mentionscount.keys():
                mentionscount[d]=0
        
        tf_all = CalcTF(mentionscount)
#        print(tf_all)
#        print(tf_all)
        WriteTFPubMed(con, PMID[0], tf_all)
  
def WriteArticleDishin(con, A_ID):
    '''
    '''
    import numpy as np
    print(';',end="")
    curs = con.cursor()
    curs.execute('SELECT TermCount From PubMed Where A_ID="{}";'.format(A_ID))
    termcount = curs.fetchall()
    mentionscount = ast.literal_eval(termcount[0][0])
    dnames = []
    for men in mentionscount:
        dnames.append(men)
    dnames = np.unique(dnames)
    dishins = []
    for dis in dnames:
        for dis2 in range (1,len(dnames)):
            if dis != dnames[dis2]:
                dishin = GetDiShIn(dis, dnames[dis2],con)
                dishins.append(dishin)
    dishins = [x for x in dishins if x is not None]
    if len(dishins) != 0:
        menor = dishins[0]
        for i in dishins:
            if i < menor:
               menor = i
    else:
        menor = 0
    curs.execute('UPDATE Articles set DiShIn="{}" WHERE A_ID="{}" ;'.format(menor, A_ID))

def UpdateArticleDishin(con):
    '''
    '''
    print('\nUpdating DiShIn in the Articles...')    
    curs = con.cursor()
    curs.execute('Select A_ID FROM PubMed;')
    res = curs.fetchall()
    for AID in res:
        AID = AID[0]
        WriteArticleDishin(con, AID)



def WriteTFFlickr(con, F_ID, tf_all):
    '''
    '''
    curs = con.cursor()

    for disease in tf_all.keys():
        curs.execute('SELECT D_ID FROM Diseases WHERE Name="{}";'.format(disease))
        d_id = curs.fetchall()
#        print(d_id)
        if len(d_id) != 0: #if it does: check if picture is connected to disease
            d_id = d_id[0][0]
     #       print('D_ID ', d_id)
            curs.execute('''SELECT p.D_ID, p.F_ID, p.TF FROM Pictures p, Diseases d
                         WHERE d.Name="{}" and d.D_ID=p.D_ID and p.F_ID="{}";'''\
                         .format(disease, F_ID))
            artdis = curs.fetchall()
#            print(artdis)
            if len(artdis) == 0: #if it is not, add to pics table and add tf as well
                curs.execute('INSERT INTO Pictures(D_ID, F_ID, TF, IDF, TFIDF, DiShIn, Explicit, Implicit, Date, TOTAL) VALUES ("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}");'\
                             .format(d_id,F_ID,tf_all[disease],0,0,0,1,0,0,0))
                num_pics = curs.execute('SELECT COUNT(F_ID) FROM Pictures WHERE D_ID="{}" GROUP BY F_ID;'.format(d_id))
       #         print(num_pics)
                curs.execute('update Diseases set Pictures="{}" where D_ID={};'.format(num_pics, d_id))
                  #update number of pics connected to the disease in table Diseases
            elif artdis[0][2] == None or artdis[0][2] == 0:   #else if it is null just add tf to articles 
#                print('null artdis')
#                print('tf flickr to update:', tf_all[disease])
                curs.execute('UPDATE Pictures set TF="{}" where D_ID="{}" and F_ID="{}";'\
                             .format(tf_all[disease],d_id,F_ID))
            #otherwise the correct value should be there already
            

def UpdateTFFlickr(con):
    '''
    Update TF for each picture related to each disease.
    '''
    curs = con.cursor()
    curs.execute('Select F_ID, Tags FROM Flickr;')
    res = curs.fetchall()
 #   print(res)
    for F_ID in res: 
        curs.execute('SELECT TermCount From Flickr Where F_ID="{}";'.format(F_ID[0]))
        termcount = curs.fetchall()
        mentionscount = ast.literal_eval(termcount[0][0])
       
        #Select all diseases related to the article that are not in the dictionary and add them there
        # with a mention count of 0
        curs.execute('SELECT d.Name FROM Diseases d, Pictures p WHERE p.F_ID="{}" and d.D_ID=p.D_ID;'.format(F_ID[0]))
        disease_names = curs.fetchall()
        for d in disease_names[0]:
            if d not in mentionscount.keys():
                mentionscount[d]=0
        
        
        tf_all = CalcTF(mentionscount)
#        print(F_ID[0])
#        print(tf_all)
        WriteTFFlickr(con, F_ID[0], tf_all)

def WriteFlickrDishin(con, F_ID, termcount):
    '''
    '''
    import numpy as np
    print(':',end="")
    curs = con.cursor()
    if termcount != {}:
        termnames = []
        for term in termcount:
            termname = term.split(',')
            termname = termname[0]
            termnames.append(termname)
        termnames = np.unique(termnames)
        dishins = []
        for dis in termnames:
            for dis2 in range (1,len(termnames)):
                if dis != termnames[dis2]:
                    dishin = GetDiShIn(dis, termnames[dis2],con)
                    dishins.append(dishin)
        dishins = [x for x in dishins if x is not None]
        if len(dishins) != 0:
            menor = dishins[0]
            for i in dishins:
                if i < menor:
                   menor = i
        else:
            menor = 0
        
        curs.execute('UPDATE Pictures set DiShIn="{}" WHERE F_ID="{}" ;'.format(menor, F_ID))

def UpdateFlickrDishin(con):
    '''
    '''
    print('\nUpdating DiShIn in Flickr...')    
    curs = con.cursor()
    curs.execute('Select F_ID FROM Flickr;')
    res = curs.fetchall()
    for FID in res:
        curs.execute('SELECT TermCount From Flickr Where F_ID="{}";'.format(FID[0]))
        termcount = curs.fetchall()
        termcount = ast.literal_eval(termcount[0][0])
        WriteFlickrDishin(con, FID[0], termcount)        
        
def WriteTFTwitter(con, T_ID, tf_all):
    '''
    '''
    curs = con.cursor()
 
    for disease in tf_all.keys():
#        print(disease)
        #1st check if disease exists in Diseases
        curs.execute('SELECT D_ID FROM Diseases WHERE Name="{}";'.format(disease))
        d_id = curs.fetchall()
        if len(d_id) != 0: #if it does: check if tweet is connected to disease
            d_id = d_id[0][0]
#            print('D_ID ', d_id)
            curs.execute('''SELECT t.D_ID, t.T_ID, t.TF FROM Tweets t, Diseases d
                         WHERE d.Name="{}" and d.D_ID=t.D_ID and t.T_ID="{}";'''\
                         .format(disease, T_ID))
            artdis = curs.fetchall()
            if len(artdis) == 0: #if it is not, add to Tweets table and add tf as well
                curs.execute('INSERT INTO Tweets(D_ID, T_ID, TF, IDF, TFIDF, DiShIn, Explicit, Implicit, Date, TOTAL) VALUES ("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}");'\
                             .format(d_id,T_ID,tf_all[disease],0,0,0,1,0,0,0))
                             
                num_pics = curs.execute('SELECT COUNT(T_ID) FROM Tweets WHERE D_ID="{}" GROUP BY T_ID;'.format(d_id))
#                print(num_articles)
                curs.execute('update Diseases set TweetsNumber="{}" where D_ID={};'.format(num_pics, d_id))
                  #update number of tweets connected to the disease in table Diseases
            elif artdis[0][2] == None or artdis[0][2] == 0:   #else if it is null just add tf to articles 
#                print('null artdis')
                curs.execute('UPDATE Tweets set TF="{}" where D_ID="{}" and T_ID="{}";'\
                             .format(tf_all[disease],d_id,T_ID))
            #otherwise the correct value should be there already           


def UpdateTFTwitter(con):
    '''
    Update TF for each picture related to each disease.
    '''
    curs = con.cursor()
    curs.execute('Select T_ID, Tweet FROM Twitter;')
    res = curs.fetchall()
#    print(res)
    for T_ID in res:  
        curs.execute('SELECT TermCount From Twitter Where T_ID="{}";'.format(T_ID[0]))
        termcount = curs.fetchall()
        mentionscount = ast.literal_eval(termcount[0][0])
     #   print(mentionscount)
       
     
        #Select all diseases related to the article that are not in the dictionary and add them there
        # with a mention count of 0
        curs.execute('SELECT d.Name FROM Diseases d, Tweets t WHERE t.T_ID="{}" and d.D_ID=t.D_ID;'.format(T_ID[0]))
        disease_names = curs.fetchall()
        for d in disease_names[0]:
            if d not in mentionscount.keys():
#                print(d)
                mentionscount[d]=0 
   
     
        tf_all = CalcTF(mentionscount)

     #   print(tf_all)
        WriteTFTwitter(con, T_ID[0], tf_all)

def WriteTwitterDishin(con, T_ID, termcount):
    '''
    '''
    import numpy as np
    print('-',end="")
    curs = con.cursor()
    if termcount != {}:
        termnames = []
        for term in termcount:
            termname = term.split(',')
            termname = termname[0]
            termnames.append(termname)
        termnames = np.unique(termnames)
        dishins = []
        for dis in range (len(termnames)):
            for dis2 in range (dis,len(termnames)):
                if termnames[dis] != termnames[dis2]:
                    dishin = GetDiShIn(termnames[dis], termnames[dis2],con)
                    dishins.append(dishin)
        dishins = [x for x in dishins if x is not None]
        if len(dishins) != 0:
            menor = dishins[0]
            for i in dishins:
                if i < menor:
                   menor = i
        else:
            menor = 0
        curs.execute('UPDATE Tweets set DiShIn="{}" WHERE T_ID="{}" ;'.format(menor, T_ID))

def UpdateTwitterDishin(con):
    '''
    '''
    print('\nUpdating DiShIn in Twitter...')    
    curs = con.cursor()
    curs.execute('Select T_ID FROM Tweets;')
    res = curs.fetchall()
    for TID in res:
        curs.execute('SELECT TermCount From Twitter Where T_ID="{}";'.format(TID[0]))
        termcount = curs.fetchall()
        termcount = ast.literal_eval(termcount[0][0])
        WriteTwitterDishin(con, TID[0], termcount)

def UpdateTotalArticles(con):
    '''
    Update total for each article related to each disease.
    '''
    print('.',end="")
    curs = con.cursor()
    curs.execute('SELECT D_ID, A_ID, TFIDF, DiShIn, Explicit, Implicit, Date FROM Articles;')
    res = curs.fetchall()
    for a in res:
        tfidf = a[2]
        dishin = a[3]   
        explicit = a[4]
        implicit = a[5]
        date = a[6]
        total = explicit*(0.375*tfidf+0.1*dishin+0.5*implicit+0.025*date)
        curs.execute('UPDATE Articles SET TOTAL ="{}" WHERE D_ID="{}" AND A_ID="{}";'.format(total, a[0], a[1]))
        

def UpdateTotalTweets(con):
    '''
    Update total for each article related to each disease.
    '''
    print('.',end="")
    curs = con.cursor()
    curs.execute('SELECT D_ID, T_ID, TFIDF, DiShIn, Explicit, Implicit, Date FROM Tweets;')
    res = curs.fetchall()
    for a in res:
        tfidf = a[2]
        dishin = a[3]   
        explicit = a[4]
        implicit = a[5]
        date = a[6]
        total = explicit*(0.375*tfidf+0.1*dishin+0.5*implicit+0.025*date)
        curs.execute('UPDATE Tweets SET TOTAL ="{}" WHERE D_ID="{}" AND T_ID="{}";'.format(total, a[0], a[1]))


def UpdateTotalPictures(con):
    '''
    Update total for each article related to each disease.
    '''
    print('.',end="")
    curs = con.cursor()
    curs.execute('SELECT D_ID, F_ID, TFIDF, DiShIn, Explicit, Implicit, Date FROM Pictures;')
    res = curs.fetchall()
    for a in res:
        tfidf = a[2]
        dishin = a[3]   
        explicit = a[4]
        implicit = a[5]
        date = a[6]
#        print('date:', date)
        total = explicit*(0.375*tfidf+0.1*dishin+0.5*implicit+0.025*date)
        curs.execute('UPDATE Pictures SET TOTAL ="{}" WHERE D_ID="{}" AND F_ID="{}";'.format(total, a[0], a[1]))
  
#con = CreateConnection()
#UpdateTotalPictures(con)

def OrdDateArticles(con, diseaseID):
    '''
    Updates Date relevance for Articles.
    '''
    curs = con.cursor()
    
    
    curs.execute('SELECT a.A_ID, p.Date FROM Articles a, PubMed p WHERE a.D_ID="{}" and a.A_ID=p.A_ID;'.format(diseaseID))
    
    articdates = curs.fetchall()
    
    pubdates = {} # dicionario com indices e datas
    artics = []
    for articles in articdates:
        artics.append(articles[0])

    index = 0
    for article in articdates:
        pubdates[index] = article[1]
        index +=1
    pubs = list(pubdates.values())
    for i in range(len(pubs)):
        if pubs[i] == '0000-00-00':
            pubs[i] = '0001-01-01'
        if type(pubs[i]) == str:
            date = datetime.strptime(pubs[i], '%Y-%m-%d')
            pubs[i] = date
    orderedDates = sorted(pubdates.values()) #mais antigos primeiro para terem menos importancia
#    orderedDates = sorted(pubdates.values(), key=lambda d: map(int, d.split('-')))
#    print(orderedDates)
    orderedDates = OrderedDict.fromkeys(orderedDates).keys() #tirar valores repetidos
#    print(orderedDates)
    relevance = {}
    rel = 1
    for date in orderedDates:
        for index in pubdates.keys():
            if pubdates[index] == date:

                relevance[artics[index]] = rel
                rel +=1
    
    for i in relevance.keys():
        curs.execute('UPDATE Articles SET Date="{}" WHERE A_ID="{}" AND D_ID="{}";'.format(relevance[i],i,diseaseID))

        
               
def OrdDateAllArticles(con):
    '''
    '''
    curs = con.cursor()
    curs.execute('SELECT D_ID from Diseases GROUP BY D_ID;')
    d_ids = curs.fetchall()
    d_ids = d_ids
#    print('article', d_ids)
    for dis in d_ids:
        OrdDateArticles(con, dis[0])
    
    
def OrdDateTweets(con, diseaseID):
    '''
    Updates Date relevance for Tweets.
    '''
    curs = con.cursor()
    
    
    curs.execute('SELECT a.T_ID, t.PostDate FROM Tweets a, Twitter t WHERE a.D_ID="{}" and a.T_ID=t.T_ID;'.format(diseaseID))
    
    tweetdates = curs.fetchall()
#    print(tweetdates)
    
    postdates = {} # dicionario com indices e datas
    tweets = []
    for articles in tweetdates:
        tweets.append(articles[0])
#    print(tweets)

    index = 0
    for t in tweetdates:
        postdates[index] = t[1]
        index +=1
#    print(postdates)
    tws = list(postdates.values())
    for i in range(len(tws)):
        if type(tws[i]) == str:            
            date = datetime.strptime(tws[i], '%Y-%m-%d')
            tws[i] = date

    orderedDates = sorted(postdates.values()) #mais antigos primeiro para terem menos importancia

#    print(orderedDates)
    orderedDates = OrderedDict.fromkeys(orderedDates).keys() #tirar valores repetidos
#    print(orderedDates)
    relevance = {}
    rel = 1
    for date in orderedDates:
        for index in postdates.keys():
            if postdates[index] == date:

                relevance[tweets[index]] = rel
                rel +=1
    
    for i in relevance.keys():
        curs.execute('UPDATE Tweets SET Date="{}" WHERE T_ID="{}" AND D_ID="{}";'.format(relevance[i],i,diseaseID))
        
#    print(relevance)
        
        
def OrdDateAllTweets(con):
    '''
    '''
    curs = con.cursor()
    curs.execute('SELECT D_ID from Diseases;')
    d_ids = curs.fetchall()
    d_ids = d_ids
#    print ('tweet',d_ids)
    for dis in d_ids:
        OrdDateTweets(con, dis[0])
        
def OrdDatePictures(con, diseaseID):
    '''
    Updates Date relevance for Pictures.
    '''
    curs = con.cursor()
    
    
    curs.execute('SELECT p.F_ID, f.Date FROM Pictures p, Flickr f WHERE p.D_ID="{}" and p.F_ID=f.F_ID;'.format(diseaseID))
    
    picdates = curs.fetchall()
#    print(tweetdates)
    
    dates = {} # dicionario com indices e datas
    pics = []
    for pic in picdates:
        pics.append(pic[0])
#    print(tweets)

    index = 0
    for t in picdates:
        dates[index] = t[1]
        index +=1
#    print(postdates)
    pictures = list(dates.values())
    for i in range(len(pictures)):
        if type(pictures[i]) == str:            
            date = datetime.strptime(pictures[i], '%Y-%m-%d')
            pictures[i] = date

    orderedDates = sorted(dates.values()) #mais antigos primeiro para terem menos importancia

#    print(orderedDates)
    orderedDates = OrderedDict.fromkeys(orderedDates).keys() #tirar valores repetidos
#    print(orderedDates)
    relevance = {}
    rel = 1
    for date in orderedDates:
        for index in dates.keys():
            if dates[index] == date:

                relevance[pics[index]] = rel
                rel +=1
    
    for i in relevance.keys():
        curs.execute('UPDATE Pictures SET Date="{}" WHERE F_ID="{}" AND D_ID="{}";'.format(relevance[i],i,diseaseID))
        
#    print(relevance)
        
def OrdDateAllPictures(con):
    '''
    '''
    curs = con.cursor()
    curs.execute('SELECT D_ID from Diseases;')
    d_ids = curs.fetchall()
    d_ids = d_ids
#    print ('tweet',d_ids)
    for dis in d_ids:
        OrdDatePictures(con, dis[0]) 
