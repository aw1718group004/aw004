# -*- coding: utf-8 -*-
##ALTER TABLE Diseases ADD Valid BIT;
## update diseases set Valid = 0 where D_ID=1;

import pymysql as pms
from prettytable import PrettyTable
import ast

DBUSER = 'aw004'
password = 'mcca2018'
DBHOST = 'appserver-01.alunos.di.fc.ul.pt'

DISEASE_NUMBER = 100
ID_NUMBER = 10

def CreateConnection():
    con=pms.connect(host=DBHOST, user=DBUSER, passwd=password, db=DBUSER, autocommit=True)
    return con


###########################################################################

def DiseaseStats():
    '''
    '''
    #Create connection
    con = CreateConnection()
    curs = con.cursor()
    #Create file
    stats_file = open('Statistics.txt', 'w')

    #Header
    stats_file.write(45*'#' + '\n')
    stats_file.write('#      DISEASES WEB CRAWLER STATISTICS      #\n')
    stats_file.write(45*'#' + '\n')

    #Nr of valid diseases in complete DBPedia List
    NrDisListed = curs.execute('SELECT COUNT(*) FROM DiseaseList GROUP BY DiseaseList.L_ID;')
    stats_file.write('Number of total valid + invalid in main list (source: DBPedia): ' + str(NrDisListed)+'\n')
    NrDisValid = curs.execute('SELECT COUNT(L_ID) FROM DiseaseList WHERE Valid=1 GROUP BY DiseaseList.L_ID;')
    stats_file.write('Number of valid diseases in main list (source: DBPedia): ' + str(NrDisValid)+'\n')

    #Nr of diseases
    NrDis = curs.execute('SELECT COUNT(D_ID) FROM Diseases GROUP BY Diseases.D_ID')
    stats_file.write('Number of diseases: ' + str(NrDis)+'\n')

    #Total number of articles listed for collected diseases
    NrArt = curs.execute('Select count(A_ID) From PubMed GROUP BY PubMed.A_ID;')
    stats_file.write('Total number of PubMed articles: ' + str(NrArt)+'\n')
    #Nr of average articles per disease
    avgArt = round(NrArt/NrDis)
    stats_file.write('Average of PubMed articles per total diseases: '+str(avgArt))

    #Total number of pics listed for collected diseases
    NrPics = curs.execute('Select count(F_ID) From Flickr GROUP BY Flickr.F_ID')
    stats_file.write('\nTotal number of pictures : ' + str(NrPics)+'\n')
    #Nr of average pictures per disease
    avgPics = round(NrPics/NrDis)
    stats_file.write('Average of Flickr pictures per total diseases: '+str(avgPics))

    #Total number of tweets listed for collected diseases
    NrTweets = curs.execute('Select count(T_ID) From Twitter GROUP BY Twitter.T_ID')
    stats_file.write('\nTotal number of Tweets: ' + str(NrTweets)+'\n')
    #Nr of average tweets per disease
    avgTweets = round(NrTweets/NrDis)
    stats_file.write('Average of tweets per total diseases: '+str(avgTweets))

    #DBPedia Data
    NrMeta = curs.execute('Select count( distinct(D_ID) ) From DBPedia GROUP BY DBPedia.D_ID')
    stats_file.write('\nDBPedia metadata available for ' + str(NrMeta)+' diseases.\n')
    #verificar que nao conta vazias


    #artigo com melhor score
    curs.execute('SELECT Name FROM Diseases WHERE D_ID = (SELECT D_ID FROM Articles ORDER BY Articles.`TOTAL` DESC LIMIT 1)')
    Bestarticle = curs.fetchone()
    stats_file.write('\nThe Disease with the best rated Article is: '+ str(Bestarticle[0])+'.')
    curs.execute('SELECT TOTAL FROM Articles ORDER BY Articles.`TOTAL` DESC LIMIT 1')
    Bestarticletotal = curs.fetchone()
    stats_file.write('\n -- With the total importance of: '+ str(Bestarticletotal[0])+'.')
    #tweet com melhor score
    curs.execute('SELECT Name FROM Diseases WHERE D_ID = (SELECT D_ID FROM Tweets ORDER BY Tweets.`TOTAL` DESC LIMIT 1)')
    BestTweet = curs.fetchone()
    stats_file.write('\nThe Disease with the best rated Tweet is: '+ str(BestTweet[0])+'.')
    curs.execute('SELECT TOTAL FROM Tweets ORDER BY Tweets.`TOTAL` DESC LIMIT 1')
    BestTweetTotal = curs.fetchone()
    stats_file.write('\n -- With the total importance of: '+ str(BestTweetTotal[0])+'.')
    #flick com melhor score
    curs.execute('SELECT Name FROM Diseases WHERE D_ID = (SELECT D_ID FROM Pictures ORDER BY Pictures.`TOTAL` DESC LIMIT 1)')
    BestPictures = curs.fetchone()
    stats_file.write('\nThe Disease with the best rated Picture is: '+ str(BestPictures[0]) + '.')
    curs.execute('SELECT TOTAL FROM Pictures ORDER BY Pictures.`TOTAL` DESC LIMIT 1')
    BestPicturesTotal = curs.fetchone()
    stats_file.write('\n -- With the total importance of: '+ str(BestPicturesTotal[0])+'.\n')


    #Doença com maior numero de artigos:
    curs.execute('SELECT Name FROM Diseases WHERE ArticlesNumber = (SELECT MAX(ArticlesNumber) FROM Diseases ORDER BY ArticlesNumber DESC LIMIT 1)')
    MoreArticles = curs.fetchone()
    stats_file.write('\nThe Disease with more articles is: '+ str(MoreArticles[0]) + '.')
    #Doença com menor numero de artigos:
    curs.execute('SELECT Name FROM Diseases WHERE ArticlesNumber = (SELECT MIN(ArticlesNumber) FROM Diseases ORDER BY ArticlesNumber DESC LIMIT 1)')
    LessArticles = curs.fetchone()
    stats_file.write('\nThe Disease with less articles is: '+ str(LessArticles[0]) + '.\n')


    #Doenças com maior número de Tweets:
    curs.execute('SELECT Name FROM Diseases WHERE TweetsNumber = (SELECT MAX(TweetsNumber) FROM Diseases ORDER BY TweetsNumber DESC LIMIT 1)')
    MoreTweets = curs.fetchone()
    stats_file.write('\nThe Disease with more Tweets is: '+ str(MoreTweets[0]) + '.')
    #Doenças com menor número de Tweets:
    curs.execute('SELECT Name FROM Diseases WHERE TweetsNumber = (SELECT MIN(TweetsNumber) FROM Diseases ORDER BY TweetsNumber DESC LIMIT 1)')
    LessTweets = curs.fetchone()
    stats_file.write('\nThe Disease with less Tweets is: '+ str(LessTweets[0]) + '.\n')


    #Doenças com maior número de Flickr:
    curs.execute('SELECT Name FROM Diseases WHERE PicsNumber = (SELECT MAX(PicsNumber) FROM Diseases ORDER BY PicsNumber DESC LIMIT 1)')
    MorePic = curs.fetchone()
    stats_file.write('\nThe Disease with more images is: '+ str(MorePic[0]) + '.')
    #Doenças com menor número de Flickr:
    curs.execute('SELECT Name FROM Diseases WHERE PicsNumber = (SELECT MIN(PicsNumber) FROM Diseases ORDER BY PicsNumber DESC LIMIT 1)')
    LessPic = curs.fetchone()
    stats_file.write('\nThe Disease with less images is: '+ str(LessPic[0]) + '.\n')


    #### Articles
    #Average of IDF in articles
    curs.execute('SELECT AVG(IDF) FROM Articles')
    IDFa= curs.fetchone()
    stats_file.write('\nThe average IDF of Articles is: '+ str(IDFa[0]) + '.')
    #Average of TF in articles
    curs.execute('SELECT AVG(TF) FROM Articles')
    TFa= curs.fetchone()
    stats_file.write('\nThe average TF of Articles is: '+ str(TFa[0]) + '.')
    #Average of TFIDF in articles
    curs.execute('SELECT AVG(TFIDF) FROM Articles')
    TFIDFa= curs.fetchone()
    stats_file.write('\nThe average TFIDF of Articles is: '+ str(TFIDFa[0]) + '.')
    #Average of DiShIn in articles
    curs.execute('SELECT AVG(DiShIn) FROM Articles')
    DiShina= curs.fetchone()
    stats_file.write('\nThe average DiShIn of Articles is: '+ str(DiShina[0]) + '.')
    # Max Total in articles
    curs.execute('SELECT MAx(Total) FROM Articles')
    totala = curs.fetchone()
    stats_file.write('\nThe best Total of Articles is: ' + str(totala[0]) + '.\n')

    ##### Pictures
    #Average of IDF in Pictures
    curs.execute('SELECT AVG(IDF) FROM Pictures')
    IDFp= curs.fetchone()
    stats_file.write('\nThe average IDF of Pictures is: '+ str(IDFp[0]) + '.')
    #Average of TF in Pictures
    curs.execute('SELECT AVG(TF) FROM Pictures')
    TFp= curs.fetchone()
    stats_file.write('\nThe average TF of Pictures is: '+ str(TFp[0]) + '.')
    #Average of TFIDF in Pictures
    curs.execute('SELECT AVG(TFIDF) FROM Pictures')
    TFIDFp= curs.fetchone()
    stats_file.write('\nThe average TFIDF of Pictures is: '+ str(TFIDFp[0]) + '.')
    #Average of DiShIn in Pictures
    curs.execute('SELECT AVG(DiShIn) FROM Pictures')
    DiShinp= curs.fetchone()
    stats_file.write('\nThe average DiShIn of Pictures is: '+ str(DiShinp[0]) + '.')
    # Max Total in pictures
    curs.execute('SELECT MAx(Total) FROM Pictures')
    totalp = curs.fetchone()
    stats_file.write('\nThe best Total of Pictures is: ' + str(totalp[0]) + '.\n')

    #### Tweets
    #Average of IDF in Tweets
    curs.execute('SELECT AVG(IDF) FROM Tweets')
    IDFt= curs.fetchone()
    stats_file.write('\nThe average IDF of Tweets is: '+ str(IDFt[0]) + '.')
    #Average of TF in Tweets
    curs.execute('SELECT AVG(TF) FROM Tweets')
    TFt= curs.fetchone()
    stats_file.write('\nThe average TF of Tweets is: '+ str(TFt[0]) + '.')
    #Average of TFIDF in Tweets
    curs.execute('SELECT AVG(TFIDF) FROM Tweets')
    TFIDFt= curs.fetchone()
    stats_file.write('\nThe average TFIDF of Tweets is: '+ str(TFIDFt[0]) + '.')
    #Average of DiShIn in Tweets
    curs.execute('SELECT AVG(DiShIn) FROM Tweets')
    DiShint= curs.fetchone()
    stats_file.write('\nThe average DiShIn of Tweets is: '+ str(DiShint[0]) + '.')
    # Max Total in Tweets
    curs.execute('SELECT MAx(Total) FROM Tweets')
    totalt = curs.fetchone()
    stats_file.write('\nThe best Total of Tweets is: ' + str(totalt[0]) + '.\n')



    # Exemplo
    stats_file.write('\n\n\n***Data example***\n')
    name = 'Asthma'
    name = name.lower()

    #get disease id
    curs.execute('SELECT D_ID FROM Diseases WHERE Name="{}";'.format(name))
    res = curs.fetchall()
    if res ==():
        print(name+' was deleted. Please update crawler.')
        stats_file.write('The example was deleted. Please update files.\n\n')
    else:
        stats_file.write('*Disease: '+name+'\n')
        d_id = res[0][0]

        #articles   PubMed(D_ID, A_ID, Title, Abstract)
        stats_file.write('\n*Articles available for '+name+':\n')
        curs.execute('SELECT COUNT(*) FROM PubMed p, Articles a WHERE a.D_ID="{}" and a.A_ID=p.A_ID;'.format(d_id))
        total = curs.fetchall()
        stats_file.write('Total: '+str(total[0][0])+' \n\n')
        curs.execute('SELECT p.A_ID, p.Title FROM PubMed p, Articles a WHERE a.D_ID="{}" and a.A_ID=p.A_ID;'.format(d_id))
        articles = curs.fetchall()
        x = PrettyTable(["PubMed ID", "Title"])
        x.align["PubMed ID"] = "c" # Left align PubMed ID
        x.align["Title"] = "l"
        x.border = False
        x.padding_width = 1 # One space between column edges and contents (default)

        for i in articles:
            content = [str(i[0]),str(i[1])]
            x.add_row(content)
        stats_file.write(str(x))

        #Um abstract
        stats_file.write('\n\n*Abstract for PubMed article '+str(articles[0][0])+':\n')
        curs.execute('SELECT Abstract FROM PubMed WHERE A_ID="{}";'.format(str(articles[0][0])))
        abstract = curs.fetchall()
        stats_file.write(abstract[0][0]+'\n')

        #Flickr pictures
        stats_file.write('\n*Flickr urls - pictures related to '+name+':\n')
        curs.execute('SELECT f.F_URL FROM Flickr f, Pictures p WHERE p.D_ID="{}" AND p.F_ID=f.F_ID;'.format(d_id))
        pictures = curs.fetchall()
        for i in pictures:
            stats_file.write(str(i[0])+'\n')

        #Tweets
        stats_file.write('\n*Twitter urls - tweets related to '+name+':\n')
        curs.execute('SELECT t.T_URL FROM Twitter t, Tweets s WHERE s.D_ID="{}" AND s.T_ID=t.T_ID;'.format(d_id))
        tweets = curs.fetchall()
        for i in tweets:
            stats_file.write(str(i[0])+'\n')

        #DBPedia Metadata
        stats_file.write('\n*Metadata related to '+name+':\n')
        #Field
        curs.execute('SELECT field FROM Metadata m, DBPedia d WHERE d.D_ID="{}" AND d.M_ID=m.M_ID;'.format(d_id))
        field = curs.fetchall()
        if field == ():
            field = 'unknown'
        else:
            field = field[0][0]
        stats_file.write('\n-Medical field: '+field+'\n')

        #wikipedia page
        stats_file.write('\n-Wikipedia page: ')
        curs.execute('SELECT distinct(m.wiki) FROM Metadata m, DBPedia d WHERE d.D_ID="{}" AND d.M_ID=m.M_ID GROUP BY m.wiki;'.format(d_id))
        wikipedia = curs.fetchall()
        if wikipedia ==():
            wikipedia = 'unknown'
        else:
            wikipedia = wikipedia[0][0]
        stats_file.write(str(wikipedia)+'\n\n')

        #Number of famous people who died from the disease
        deadpeople = curs.execute('SELECT COUNT(distinct(m.name)) FROM Metadata m, DBPedia d WHERE d.D_ID="{}" AND  d.M_ID=m.M_ID GROUP BY m.name;'.format(d_id))
        stats_file.write('-Number of famous people who died from '+name+': '+str(deadpeople)+'\n')
        #Deceased people info
        curs.execute('SELECT name, deathdate, deathplace FROM Metadata m, DBPedia d WHERE d.D_ID="{}" AND d.M_ID=m.M_ID;'.format(d_id))
        meta = curs.fetchall()
        x = PrettyTable(["Deceased Person", "Death date", "Death Place"])
        x.align["Deceased Person"] = "l" # Left align Deceased Person names
        x.padding_width = 1 # One space between column edges and contents (default)
        for i in meta:
            content = [str(i[0]),str(i[1]),str(i[2])]
            x.add_row(content)
        x.sortby = 'Death date'
        stats_file.write(str(x))
        stats_file.write('\n\n')

        #ANNOTATIONS; RANKS
        #Melhores artigos para o exemplo:
        stats_file.write('\nThe termcounts and ranks for the best 3 Articles related to Asthma: ' + '\n')
        curs.execute('SELECT A_ID, TF, IDF, TFIDF, DiShIn, Explicit, Implicit, Date, TOTAL FROM Articles where D_ID = "{}" ORDER BY TOTAL DESC LIMIT 3;'.format(d_id))
        art = curs.fetchall()
        x = PrettyTable(["Abstract title","TermCounts", "TF", "IDF", "TFIDF", "DiShIn", "Explicit", "Implicit", "Date", "Total"])
        x.align["Abstract title"] = "l"  # Left align 
        x.padding_width = 1  # One space between column edges and contents (default)
        for i in art:
            curs.execute('SELECT Title, TermCount FROM PubMed WHERE A_ID="{}";'.format(i[0]))
            title = curs.fetchall()
            content = [str(title[0][0]), str(title[0][1]), str(i[1]), str(i[2]), str(i[3]), str(i[4]), str(i[5]), str(i[6]), str(i[7]), str(i[8])]
            x.add_row(content)
        x.sortby = "Total"
        x.reversesort = True
        stats_file.write(str(x))
        stats_file.write('\n\n')
        
        #Melhores imagens para o exemplo:
        stats_file.write('\nThe termcounts and ranks for the best 3 Pictures related to Asthma: ' + '\n')
        curs.execute('SELECT F_ID, TF, IDF, TFIDF, DiShIn, Explicit, Implicit, Date, TOTAL FROM Pictures where D_ID = "{}" ORDER BY TOTAL DESC LIMIT 3;'.format(d_id))
        pic = curs.fetchall()
        x = PrettyTable(["ID","TermCounts", "TF", "IDF", "TFIDF", "DiShIn", "Explicit", "Implicit", "Date", "Total"])
        x.padding_width = 1  # One space between column edges and contents (default)
        for i in pic:
            curs.execute('SELECT TermCount FROM Flickr WHERE F_ID="{}";'.format(i[0]))
            title = curs.fetchall()
            content = [str(i[0]),str(title[0][0]), str(i[1]), str(i[2]), str(i[3]), str(i[4]), str(i[5]), str(i[6]), str(i[7]),str(i[8])]
            x.add_row(content)
        x.sortby = "Total"
        x.reversesort = True
        stats_file.write(str(x))
        stats_file.write('\n\n')
        
        #Melhores tweets para o exemplo:
        stats_file.write('\nThe termcounts and ranks for the best 3 Tweets related to Asthma: ' + '\n')
        curs.execute('SELECT T_ID, TF, IDF, TFIDF, DiShIn, Explicit, Implicit, Date, TOTAL FROM Tweets where D_ID = "{}" ORDER BY TOTAL DESC LIMIT 3;'.format(d_id))
        twe = curs.fetchall()
        x = PrettyTable(["ID", "TermCounts - Hashtags", "TF", "IDF", "TFIDF", "DiShIn", "Explicit", "Implicit", "Date", "Total"])
        x.padding_width = 1  # One space between column edges and contents (default)
        for i in twe:
            curs.execute('SELECT TermCount FROM Twitter WHERE T_ID="{}";'.format(i[0]))
            title = curs.fetchall()
            content = [ str(i[0]), str(title[0][0]), str(i[1]), str(i[2]), str(i[3]), str(i[4]), str(i[5]), str(i[6]), str(i[7]), str(i[8])]
            x.add_row(content)
        x.sortby = "Total"
        x.reversesort = True
        stats_file.write(str(x))
        stats_file.write('\n\n')
        stats_file.close()
        con.close()

DiseaseStats()