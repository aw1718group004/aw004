# -*- coding: utf-8 -*-
from diseaseinfo import *
from writeinfo import *

''' Update diseases web crawler '''

Diseaselimit = None
# Max is 3563 valid diseases

while True:
    try:
        print("Updating...")    
                    
        UpdateCrawler(Diseaselimit, False) #True - faz annotations
        
        print("\nUpdate complete!") 
    except:
        print('Try again!')