
-- Seleccionar top 5 artigos
SELECT p.Title, p.Abstract, p.Authors 
    	FROM Diseases d, Articles a, PubMed p 
    	WHERE d.Name=%disease AND d.D_ID=a.D_ID AND a.A_ID =p.A_ID AND a.Explicit>0
	ORDER BY a.TOTAL DESC
    	LIMIT 5;

-- Seleccionar top 5 doenças
SELECT f.F_URL, f.Tags 
   	FROM Diseases d, Pictures p, Flickr f 
   	WHERE d.Name=%disease AND d.D_ID=p.D_ID AND p.F_ID=f.F_ID AND p.Explicit>0
	ORDER BY p.TOTAL DESC
  	LIMIT 5;

-- Seleccionar top 5 tweets
SELECT tt.T_URL, tt.Tweet 
    	FROM Diseases d, Twitter tt, Tweets ee 
    	WHERE d.Name=%disease AND d.D_ID=ee.D_ID AND ee.T_ID=tt.T_ID AND ee.Explicit>0
	ORDER BY ee.TOTAL DESC
    	LIMIT 5;

-- Seleccionar metadata
   -- DBPedia
	-- wiki page + field
SELECT DISTINCT m.wiki,m.field 
	FROM Metadata m, DBPedia dbp, Diseases d 
	WHERE d.Name=%disease AND d.D_ID=dbp.D_ID AND dbp.M_ID=m.M_ID; 

	-- pessoas que morreram da doença (limite de 10)
	-- (Dá para fazer if para se for 0000-00-00 ficar 'unknown' ?)
SELECT m.name, m.deathdate, m.deathplace
	FROM Metadata m, DBPedia dbp, Diseases d 
	WHERE d.Name=%disease AND d.D_ID=dbp.D_ID AND dbp.M_ID=m.M_ID
	LIMIT 10;

-- UniProt (limite de 10)
SELECT u.GeneLabel, u.gene, u.NCBIgeneID
	FROM UniProt u, GeneInfo g, Diseases d
	WHERE d.Name=%disease, d.D_ID=g.D_ID, g.G_ID=u.G_ID
	LIMIT 10;


-- RECOMENDAÇÕES:
-- Selecionar top n related diseases:

-- Contar quantos artigos em comum entre duas doenças
SELECT d2.Name
	FROM Diseases d2, Articles a
	WHERE d2.Name!=%disease AND d2.D_ID=a.D_ID AND a.A_ID IN (
	-- Selecionar PMIDs para doença pesquisada
	SELECT a.A_ID
	FROM Diseases d1, Articles a
	WHERE d1.Name=%disease and d1.D_ID=a.D_ID)

	GROUP BY d2.Name
	ORDER BY COUNT(*) DESC
	LIMIT 10;


----------------------------------------------------------------------------

-- Valores de teste:	WHERE A_ID=29694442 AND D_ID=1;

-- Atualizar valores para artigo depois de click em artigo
UPDATE Articles SET Implicit=Implicit+10 	
	WHERE A_ID=$PMID AND D_ID=$disease;
    
UPDATE Articles SET TOTAL=Explicit*(0.375*TFIDF+0.1*DiShIn+0.5*Implicit+0.025*Date)
	WHERE A_ID=$PMID AND D_ID=$disease;

-- Atualizar valores para artigo depois de dislike
UPDATE Articles SET Explicit=0 	
	WHERE A_ID=$PMID AND D_ID=$disease;
    
UPDATE Articles SET TOTAL=Explicit*(0.375*TFIDF+0.1*DiShIn+0.5*Implicit+0.025*Date)
	WHERE A_ID=$PMID AND D_ID=$disease;


-- Atualizar valores para artigo depois de like
	
UPDATE Articles SET Explicit=POWER(Explicit+1, 4) -- Mudar fórmula conforme resultados no site	
	WHERE A_ID=$PMID AND D_ID=$disease;
    
UPDATE Articles SET TOTAL=Explicit*(0.375*TFIDF+0.1*DiShIn+0.5*Implicit+0.025*Date)
	WHERE A_ID=$PMID AND D_ID=$disease;

	

-- Atualizar valores para imagem depois de click em imagem
UPDATE Pictures SET Implicit=Implicit+10 	
	WHERE F_ID=$PMID AND D_ID=$disease;
    
UPDATE Pictures SET TOTAL=0.375*TFIDF+0.1*DiShIn+0.5*Implicit+0.025*Date
	WHERE F_ID=$PMID AND D_ID=$disease;


-- Atualizar valores para imagem depois de dislike
UPDATE Pictures SET Explicit=0 	
	WHERE F_ID=$PMID AND D_ID=$disease;
    
UPDATE Pictures SET TOTAL=Explicit*(0.375*TFIDF+0.1*DiShIn+0.5*Implicit+0.025*Date)
	WHERE F_ID=$PMID AND D_ID=$disease;


-- Atualizar valores para imagem depois de like
	
UPDATE Pictures SET Explicit=POWER(Explicit+1, 4) -- Mudar fórmula conforme resultados no site	
	WHERE F_ID=$PMID AND D_ID=$disease;
    
UPDATE Pictures SET TOTAL=Explicit*(0.375*TFIDF+0.1*DiShIn+0.5*Implicit+0.025*Date)
	WHERE F_ID=$PMID AND D_ID=$disease;



-- Atualizar valores para tweet depois de click em tweet
UPDATE Tweets SET Implicit=Implicit+10 	
	WHERE T_ID=$PMID AND D_ID=$disease;
    
UPDATE Tweets SET TOTAL=0.375*TFIDF+0.1*DiShIn+0.5*Implicit+0.025*Date
	WHERE T_ID=$PMID AND D_ID=$disease;


-- Atualizar valores para tweet depois de dislike
UPDATE Tweets SET Explicit=0 	
	WHERE T_ID=$PMID AND D_ID=$disease;
    
UPDATE Tweets SET TOTAL=Explicit*(0.375*TFIDF+0.1*DiShIn+0.5*Implicit+0.025*Date)
	WHERE T_ID=$PMID AND D_ID=$disease;


-- Atualizar valores para tweet depois de like
	
UPDATE Tweets SET Explicit=POWER(Explicit+1, 4) -- Mudar fórmula conforme resultados no site	
	WHERE T_ID=$PMID AND D_ID=$disease;
    
UPDATE Tweets SET TOTAL=Explicit*(0.375*TFIDF+0.1*DiShIn+0.5*Implicit+0.025*Date)
	WHERE T_ID=$PMID AND D_ID=$disease;


