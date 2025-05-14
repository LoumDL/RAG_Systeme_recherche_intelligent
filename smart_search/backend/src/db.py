from qdrant_client import models, QdrantClient
from sentence_transformers import SentenceTransformer
from pathlib import Path
import os
import logging
from datetime import datetime, timezone
from pymongo import MongoClient
from fastapi.encoders import jsonable_encoder
import redis
import json
import hashlib

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# =============================================
# Configuration Qdrant pour la recherche vectorielle
# =============================================
QDRANT_URL = "http://localhost:6333"
ENCODER_MODEL = "Alibaba-NLP/gte-Qwen2-1.5B-instruct"
COLLECTION_NAME = "smart_search"
VECTOR_SIZE = 1536  # Taille du vecteur attendu par le modèle

# Initialisation du client Qdrant et de l'encodeur
try:
    client = QdrantClient(url=QDRANT_URL)
    encoder = SentenceTransformer(ENCODER_MODEL, trust_remote_code=True)
    logger.info(f"Connexion établie avec Qdrant sur {QDRANT_URL}")
except Exception as e:
    logger.error(f"Erreur lors de l'initialisation de Qdrant ou de l'encodeur: {e}")
    # Ne pas arrêter l'application, mais définir les variables à None
    client = None
    encoder = None

def initialize_collection():
    """
    Initialise la collection Qdrant si elle n'existe pas.
    """
    if client is None:
        logger.error("Client Qdrant non initialisé, impossible de créer la collection")
        return False
        
    try:
        # Vérifier si la collection existe déjà
        collections = client.get_collections()
        collection_names = [collection.name for collection in collections.collections]
        
        if COLLECTION_NAME in collection_names:
            logger.info(f"Collection '{COLLECTION_NAME}' existe déjà.")
            return True
            
        # Créer la collection si elle n'existe pas
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=VECTOR_SIZE,
                distance=models.Distance.COSINE,
            ),
        )
        logger.info(f"Collection '{COLLECTION_NAME}' créée avec succès.")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la création de la collection: {e}")
        return False

def insert_documents_into_qdrant(documents):
    """
    Insère une liste de documents vectorisés dans la base de données Qdrant.
    
    Args:
        documents (list): Liste des documents sous forme de texte.
    
    Returns:
        bool: True si l'opération a réussi, False sinon.
    """
    if client is None or encoder is None:
        logger.error("Client Qdrant ou encodeur non initialisé, impossible d'insérer des documents")
        return False
        
    try:
        # Vérifier si la collection existe
        collections = client.get_collections()
        collection_names = [collection.name for collection in collections.collections]
        
        if COLLECTION_NAME not in collection_names:
            initialize_collection()
        
        # Compter les documents existants pour définir l'ID de départ
        count = client.count(collection_name=COLLECTION_NAME).count
        
        # Préparer les points à insérer
        points = []
        for idx, doc in enumerate(documents):
            # Encoder le document en vecteur
            try:
                vector = encoder.encode(str(doc)).tolist()
                
                # Créer le point
                point = models.PointStruct(
                    id=count + idx,
                    vector=vector,
                    payload={"text": doc, "timestamp": datetime.now(timezone.utc).isoformat()}
                )
                points.append(point)
            except Exception as e:
                logger.warning(f"Erreur lors de l'encodage du document {idx}: {e}")
                continue
        
        # Insérer les points par lots
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i+batch_size]
            client.upload_points(collection_name=COLLECTION_NAME, points=batch)
            logger.info(f"Lot {i//batch_size + 1} de {len(points)//batch_size + 1} inséré")
        
        logger.info(f"{len(points)} documents ont été indexés dans Qdrant.")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'insertion de documents dans Qdrant: {e}")
        return False

def query_qdrant(query_text, limit=3):
    """
    Recherche les documents similaires à la requête donnée en utilisant la similarité cosinus.
    
    Args:
        query_text (str): Texte de la requête.
        limit (int): Nombre de résultats à retourner (par défaut 3).
    
    Returns:
        list: Liste contenant le texte des documents les plus pertinents trouvés.
    """
    if client is None or encoder is None:
        logger.error("Client Qdrant ou encodeur non initialisé, impossible d'effectuer la recherche")
        return []
        
    try:
        # Encoder la requête
        query_vector = encoder.encode(query_text)
        
        # Rechercher dans Qdrant
        results = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector.tolist(),
            limit=limit
        )
        
        if not results:
            logger.warning(f"Aucun résultat trouvé pour la requête: {query_text[:50]}...")
            return []
            
        return [result.payload['text'] for result in results]
    except Exception as e:
        logger.error(f"Erreur lors de la recherche dans Qdrant: {e}")
        return []

# =============================================
# Configuration MongoDB pour l'historique
# =============================================
MONGODB_URI = "mongodb://localhost:27017"
DATABASE_NAME = "history_smart_search"

try:
    client_mongodb = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    # Vérifier la connexion
    client_mongodb.server_info()
    db = client_mongodb[DATABASE_NAME]
    logger.info(f"Connexion établie avec MongoDB sur {MONGODB_URI}")
except Exception as e:
    logger.error(f"Erreur lors de la connexion à MongoDB: {e}")
    client_mongodb = None
    db = None

def inserer_chat(donnee: dict):
    """
    Insère des données dans la collection MongoDB.
    
    Args:
        donnee (dict): Données à insérer.
    
    Returns:
        bool: True si l'opération a réussi, False sinon.
    """
    if db is None:
        logger.error("Connexion MongoDB non établie, impossible d'insérer des données")
        return False
        
    try:
        donnee = jsonable_encoder(donnee)
        result = db["history"].insert_one(donnee)
        logger.info(f"Données insérées avec succès. ID: {result.inserted_id}")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'insertion des données dans MongoDB: {e}")
        return False

def modeliserdonnee(question: str, reponse: str):
    """
    Modélise les données à insérer dans la base de données.
    
    Args:
        question (str): La question posée par l'utilisateur.
        reponse (str): La réponse générée par le modèle LLM.
    
    Returns:
        dict: Un dictionnaire contenant la question et la réponse.
    """
    return {
        "question": question,
        "reponse": reponse,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# =============================================
# Configuration Redis pour le cache et stockage
# =============================================
REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_CACHE_DB = 1
CACHE_TTL = 3600  # Durée de vie du cache en secondes (1 heure)

# Initialisation des connexions Redis
try:
    # Pool de connexion pour le stockage principal
    storage_pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    redis_storage = redis.Redis(connection_pool=storage_pool)
    
    # Pool de connexion pour le cache
    cache_pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_CACHE_DB)
    redis_cache = redis.Redis(connection_pool=cache_pool)
    
    # Vérifier la connexion
    if redis_storage.ping() and redis_cache.ping():
        logger.info(f"Connexion établie avec Redis sur {REDIS_HOST}:{REDIS_PORT}")
    else:
        raise Exception("Échec du ping Redis")
except Exception as e:
    logger.error(f"Erreur lors de la connexion à Redis: {e}")
    redis_storage = None
    redis_cache = None

def set_redis(eleve: dict):
    """
    Enregistre des données d'élève dans Redis.
    
    Args:
        eleve (dict): Données de l'élève à enregistrer.
    
    Returns:
        str: Clé générée pour les données enregistrées.
    """
    if redis_storage is None:
        logger.error("Connexion Redis non établie, impossible d'enregistrer les données")
        return None
        
    try:
        # Génération d'un nouvel ID
        compteur_key = "eleve:id"
        new_id = redis_storage.incr(compteur_key)
        cle = f"eleve:{new_id}"
        
        # Conversion des valeurs en chaînes de caractères pour Redis
        mapping = {k: str(v) for k, v in eleve.items()}
        
        # Enregistrement du hash
        redis_storage.hset(cle, mapping=mapping)
        logger.info(f"Données enregistrées dans Redis avec la clé: {cle}")
        return cle
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement des données dans Redis: {e}")
        return None

def get_redis(cle: str):
    """
    Récupère des données depuis Redis.
    
    Args:
        cle (str): Clé des données à récupérer.
    
    Returns:
        dict: Données récupérées.
    """
    if redis_storage is None:
        logger.error("Connexion Redis non établie, impossible de récupérer les données")
        return {}
        
    try:
        result = redis_storage.hgetall(cle)
        # Conversion des bytes en str pour compatibilité
        resultat = {k.decode('utf-8'): v.decode('utf-8') for k, v in result.items()}
        return resultat
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des données depuis Redis: {e}")
        return {}

# Fonctions de cache Redis
def get_cached_response(question: str):
    """
    Vérifie si une réponse existe dans le cache Redis.
    
    Args:
        question (str): La question à rechercher dans le cache.
        
    Returns:
        str or None: La réponse en cache si elle existe, None sinon.
    """
    if redis_cache is None:
        logger.error("Connexion Redis Cache non établie, impossible d'accéder au cache")
        return None
        
    try:
        # Générer une clé de cache basée sur le hash de la question
        question_hash = hashlib.md5(question.encode()).hexdigest()
        cache_key = f"cache:response:{question_hash}"
        
        # Récupérer depuis le cache
        cached = redis_cache.get(cache_key)
        if cached:
            logger.info(f"Réponse récupérée du cache pour: {question[:30]}...")
            return cached.decode('utf-8')
        return None
    except Exception as e:
        logger.error(f"Erreur lors de l'accès au cache Redis: {e}")
        return None

def set_cached_response(question: str, response: str):
    """
    Enregistre une réponse dans le cache Redis avec TTL.
    
    Args:
        question (str): La question comme clé de cache.
        response (str): La réponse à mettre en cache.
        
    Returns:
        bool: True si l'opération a réussi, False sinon.
    """
    if redis_cache is None:
        logger.error("Connexion Redis Cache non établie, impossible de mettre en cache")
        return False
        
    try:
        # Générer une clé de cache basée sur le hash de la question
        question_hash = hashlib.md5(question.encode()).hexdigest()
        cache_key = f"cache:response:{question_hash}"
        
        # Enregistrer dans le cache avec TTL
        redis_cache.setex(cache_key, CACHE_TTL, response)
        logger.info(f"Réponse mise en cache pour: {question[:30]}...")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement dans le cache Redis: {e}")
        return False

def clear_cache():
    """
    Efface toutes les entrées de cache.
    
    Returns:
        bool: True si l'opération a réussi, False sinon.
    """
    if redis_cache is None:
        logger.error("Connexion Redis Cache non établie, impossible de vider le cache")
        return False
        
    try:
        # Lister toutes les clés de cache
        cache_keys = redis_cache.keys("cache:response:*")
        
        if cache_keys:
            # Supprimer toutes les clés de cache
            redis_cache.delete(*cache_keys)
            logger.info(f"{len(cache_keys)} entrées supprimées du cache")
        else:
            logger.info("Aucune entrée de cache à supprimer")
            
        return True
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage du cache Redis: {e}")
        return False

# Fonction d'initialisation de la base de données
def load_the_database(chemin_dossier=None):
    """
    Charge les fichiers PDF, extrait leur contenu en Markdown, segmente le texte en chunks et les insère dans Qdrant.
    
    Args:
        chemin_dossier (str, optional): Chemin vers le dossier contenant les fichiers PDF.
        
    Returns:
        bool: True si l'opération a réussi, False sinon.
    """
    try:
        # Importer les modules nécessaires ici pour éviter les dépendances circulaires
        from .texte import extraction_markdown, markdown_file, Chunker
        
        # Utiliser le chemin par défaut si non spécifié
        if chemin_dossier is None:
            chemin_dossier = Path("/home/ubuntu/Hakili/RAG_Systeme_recherche_intelligent/smart_search/backend/data")
        else:
            chemin_dossier = Path(chemin_dossier)
            
        # Vérifier que le dossier existe
        if not chemin_dossier.exists() or not chemin_dossier.is_dir():
            logger.error(f"Le dossier {chemin_dossier} n'existe pas ou n'est pas un répertoire")
            return False
            
        # Rechercher les fichiers PDF
        fichiers_pdf = list(chemin_dossier.rglob("*.pdf"))
        
        if not fichiers_pdf:
            logger.warning("Aucun fichier PDF trouvé.")
            return False
            
        # Créer le dossier pour les fichiers Markdown
        dossier_markdown = Path("../markdown_files")
        dossier_markdown.mkdir(parents=True, exist_ok=True)
        
        # Traiter chaque fichier PDF
        success_count = 0
        for i, file_path in enumerate(fichiers_pdf):
            try:
                logger.info(f"Traitement du fichier {i+1}/{len(fichiers_pdf)}: {file_path.name}")
                
                # Extraire le contenu Markdown
                markdown = extraction_markdown(str(file_path))
                fichier_markdown = dossier_markdown / f"fichier{i}.md"
                markdown_file(markdown, fichier_markdown)
                
                if not fichier_markdown.exists():
                    logger.error(f"Erreur : {fichier_markdown} n'a pas été créé.")
                    continue
                    
                # Découper le texte en chunks et insérer dans Qdrant
                chunks = Chunker(str(fichier_markdown))
                if insert_documents_into_qdrant(chunks):
                    success_count += 1
                    
            except Exception as e:
                logger.error(f"Erreur lors du traitement du fichier {file_path.name}: {e}")
                continue
                
        logger.info(f"Traitement terminé. {success_count}/{len(fichiers_pdf)} fichiers traités avec succès.")
        return success_count > 0
        
    except ImportError as e:
        logger.error(f"Erreur d'importation des modules nécessaires: {e}")
        return False
    except Exception as e:
        logger.error(f"Erreur inattendue lors du chargement de la base de données: {e}")
        return False

# Fonction d'initialisation globale des bases de données
def initialize_databases():
    """
    Initialise toutes les bases de données et vérifie leur état.
    
    Returns:
        dict: État de chaque base de données (True si disponible, False sinon).
    """
    status = {
        "qdrant": False,
        "mongodb": False,
        "redis_storage": False,
        "redis_cache": False
    }
    
    # Vérifier Qdrant
    if client is not None and encoder is not None:
        status["qdrant"] = initialize_collection()
    
    # Vérifier MongoDB
    if db is not None:
        try:
            db.command('ping')
            status["mongodb"] = True
        except Exception:
            status["mongodb"] = False
    
    # Vérifier Redis pour le stockage
    if redis_storage is not None:
        try:
            status["redis_storage"] = redis_storage.ping()
        except Exception:
            status["redis_storage"] = False
    
    # Vérifier Redis pour le cache
    if redis_cache is not None:
        try:
            status["redis_cache"] = redis_cache.ping()
        except Exception:
            status["redis_cache"] = False
    
    # Afficher l'état
    for db_name, is_ok in status.items():
        if is_ok:
            logger.info(f"✅ {db_name} est disponible et initialisé")
        else:
            logger.error(f"❌ {db_name} n'est pas disponible")
    
    return status

if __name__ == "__main__":
    status = initialize_databases()
    
    # Charger la base de données seulement si Qdrant est disponible
    if status["qdrant"]:
        load_the_database()
        print("Database loaded successfully")
    else:
        print("Database initialization failed, check logs for details")