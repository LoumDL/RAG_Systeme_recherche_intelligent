import ollama
from bd_qdrant.vector_database import query_qdrant
from langdetect import detect


def llm(question: str):
    # Charger le client de la base de données

    resultats = query_qdrant(question)
    texte = resultats[0][1] if resultats else ""  # Vérifier si des résultats existent

    # Construire le prompt
    prompt_template = f"{texte}\n\n{question}" if texte else question  # Éviter un prompt vide

    # Interroger le modèle
    response = ollama.chat(
        model="deepseek-r1",
        messages=[
            {"role": "user", "content": f"Réponds en français: {prompt_template}"},
        ],
    )

    response_text = response["message"]["content"].strip() if "message" in response else ""

    # Filtrer les phrases en français
    french_text = []
    for sentence in response_text.split("\n"):
        sentence = sentence.strip()
        if sentence and len(sentence) > 3:  # Vérifier que la phrase n'est pas vide et a une longueur suffisante
            try:
                if detect(sentence) == "fr":  # Vérifier si la phrase est en français
                    french_text.append(sentence)
            except Exception as e:
                print(f"Erreur de détection de langue : {e}")  # Afficher l'erreur sans bloquer l'exécution

    return french_text


