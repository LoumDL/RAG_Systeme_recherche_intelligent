// api/chat.ts - Service pour communiquer avec votre API

export default {
  // URL de base de l'API - récupérée depuis les variables d'environnement
  baseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  
  // Envoyer un message texte à l'API
  async sendTextMessage(question: string) {
    try {
      const response = await fetch(`${this.baseUrl}/smartsearch/text`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Erreur API: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Erreur lors de l\'envoi du message:', error);
      throw error;
    }
  },
  
  // Envoyer une requête multimodale (avec fichier)
  async sendMultimodalMessage(prompt: string, file: File) {
    try {
      const formData = new FormData();
      formData.append('prompt', prompt);
      formData.append('file', file);
      
      const response = await fetch(`${this.baseUrl}/smartsearch/multimodal`, {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Erreur API: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Erreur lors de l\'envoi du message multimodal:', error);
      throw error;
    }
  },
  
  // Récupérer l'historique des conversations (à implémenter si nécessaire)
  async getConversationHistory() {
    // Cette fonctionnalité n'est pas disponible dans l'API fournie
    // Vous pourriez implémenter un stockage local ou une nouvelle route API
    
    // Pour l'instant, on retourne un tableau vide
    return { conversations: [] };
  }
};
