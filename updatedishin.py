# -*- coding: utf-8 -*-

from writeinfo import *
from annotation import *


DBUSER = 'aw004'
DBPASS = 'mcca2018'
DBHOST = 'appserver-01.alunos.di.fc.ul.pt'


def CreateConnection():
    con=pms.connect(host=DBHOST, user=DBUSER, passwd=DBPASS, db=DBUSER, autocommit=True, charset='utf8')
    return con

def UpdateDishin(con):
    UpdateArticleDishin(con)
    UpdateFlickrDishin(con)
    UpdateTwitterDishin(con)
#    UpdateTotalArticles(con)
#    UpdateTotalPictures(con)
#    UpdateTotalTweets(con)
    print('\nUpdate Complete!')

con=CreateConnection()
UpdateDishin(con)

