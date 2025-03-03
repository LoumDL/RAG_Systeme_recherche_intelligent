

# L’essor de l’IA générative et son impact sur l’éducation

L’essor de l’intelligence artificielle (IA) générative constitue une révolution majeure dans de nombreux domaines, y compris l’éducation.  
Ses applications se multiplient et apportent un soutien précieux aux étudiants en facilitant leurs recherches, la rédaction de documents et la résolution de problèmes complexes.  

Cependant, l’efficacité de ces outils dépend en grande partie de la qualité des requêtes formulées (*prompt*). Une question mal structurée ou imprécise peut entraîner des réponses longues, inexactes ou peu pertinentes, obligeant les étudiants à un tri manuel fastidieux.  

Dans cette perspective, nous explorerons les applications concrètes de l’IA générative en vue de concevoir un **système de recherche intelligent**.  
Ce dernier offrira des réponses précises, même en cas de formulation imprécise des questions.


## Objectif général  

Développer un **système de recherche intelligent** basé sur l’IA générative pour l’innovation pédagogique.  

## Objectifs spécifiques  

- Analyser des outils d’IA générative.  
- Concevoir un système de recherche capable d’interpréter les intentions des requêtes.  
- Développer un mécanisme d’indexation de plusieurs documents numériques.  
- Réaliser un moteur de recherche multiformat.  



## Methodologie nous allons d'abord implementer le systeme d'interpretation des intentions 

le projet est structure comme suit pour le moment  : 
 smart_search
    - backend
        - api
        - interpretation 
            - bd_qdrant
                - __init__.py
                -load_the_database.py : permet de charger la base 
                -vector_database.py : definit le client qdrant et la requete
            -model 
                -__init__.py
                - llm.py : definit le modele llm que nous allons utiliser 
            -traitement
            -__init__.py 
            - word_processing_function.py : de finit le traitement des documents ( extractions,          chunking, embeddingg)
            

## remarque : 

pour run notre api : 

   uvicorn main:app --reload 

 
