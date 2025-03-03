import logging

# Configuration du logging pour écrire dans un fichier
logging.basicConfig(
    level=logging.INFO,
    filename='app.log',
    filemode='a',  # 'a' pour ajouter, 'w' pour écraser le fichier existant
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Ajouter un gestionnaire de console (optionnel)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)  # Afficher uniquement les avertissements et erreurs
console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logging.getLogger().addHandler(console_handler)

# Désactiver les logs de qdrant_client dans la console
#logging.getLogger('qdrant_client').setLevel(logging.CRITICAL)

# Exemple de log
logging.info("Ce message sera écrit dans le fichier app.log et non dans la console.")
logging.warning("Ce message apparaîtra dans la console et le fichier app.log.")
