interface ApiResponse {
  reponse: string;
  status: string;
  processing_time: number;
}

class SmartSearchApi {
  private timeout: number = 600000; // 10 minutes
  private baseUrl: string = 'https://smartsearch.myfad.org'; // Votre API RAG directement

  async sendTextMessage(question: string): Promise<ApiResponse> {
    if (!question?.trim()) {
      throw new Error('La question ne peut pas être vide');
    }
    
    console.log('📤 Envoi DIRECT vers API RAG - TEXT...');
   
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);
   
    try {
      // ✅ APPEL DIRECT - Plus de proxy !
      const apiUrl = `${this.baseUrl}/smartsearch/text`;
      console.log('🎯 URL directe:', apiUrl);
      
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({ question: question.trim() }),
        signal: controller.signal,
      });
     
      clearTimeout(timeoutId);
     
      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Erreur API RAG TEXT:', response.status, errorText);
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }
     
      const data = await response.json();
      console.log('✅ Réponse TEXT reçue directement de l\'API RAG');
      console.log('⏱️ Temps de traitement:', data.processing_time, 's');
      return data;
     
    } catch (error: any) {
      clearTimeout(timeoutId);
     
      if (error.name === 'AbortError') {
        throw new Error('Timeout après 10 minutes');
      }
     
      // Erreurs CORS ou réseau
      if (error.message.includes('Failed to fetch') || error.message.includes('CORS')) {
        throw new Error('Erreur de connexion à l\'API RAG. Vérifiez la configuration CORS.');
      }
     
      console.error('💥 Erreur dans sendTextMessage:', error);
      throw new Error(`Erreur: ${error.message}`);
    }
  }

  async sendMultimodalMessage(prompt: string, file: File): Promise<ApiResponse> {
    if (!prompt?.trim()) {
      throw new Error('Le prompt ne peut pas être vide');
    }
    
    if (!file) {
      throw new Error('Le fichier est requis');
    }

    console.log('📤 Envoi DIRECT vers API RAG - MULTIMODAL...');
    console.log('📁 Fichier:', file.name, 'Taille:', file.size);
   
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);
   
    try {
      const formData = new FormData();
      formData.append('prompt', prompt.trim());
      formData.append('file', file);

      // ✅ APPEL DIRECT - Plus de proxy !
      const apiUrl = `${this.baseUrl}/smartsearch/multimodal`;
      console.log('🎯 URL directe:', apiUrl);

      const response = await fetch(apiUrl, {
        method: 'POST',
        body: formData, // Pas de Content-Type explicite pour FormData
        signal: controller.signal,
      });
     
      clearTimeout(timeoutId);
     
      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Erreur API RAG MULTIMODAL:', response.status, errorText);
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }
     
      const data = await response.json();
      console.log('✅ Réponse MULTIMODAL reçue directement de l\'API RAG');
      console.log('⏱️ Temps de traitement:', data.processing_time, 's');
      return data;
     
    } catch (error: any) {
      clearTimeout(timeoutId);
     
      if (error.name === 'AbortError') {
        throw new Error('Timeout après 10 minutes');
      }
     
      // Erreurs CORS ou réseau
      if (error.message.includes('Failed to fetch') || error.message.includes('CORS')) {
        throw new Error('Erreur de connexion à l\'API RAG. Vérifiez la configuration CORS.');
      }
     
      console.error('💥 Erreur dans sendMultimodalMessage:', error);
      throw new Error(`Erreur multimodal: ${error.message}`);
    }
  }

  async getConversationHistory(): Promise<{ conversations: any[] }> {
    return { conversations: [] };
  }

  async testConnection(): Promise<boolean> {
    try {
      console.log('🧪 Test de connexion directe à l\'API RAG...');
      
      const response = await fetch(`${this.baseUrl}/smartsearch/text`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: 'ping' }),
      });
      
      console.log('📡 Test connexion - Status:', response.status);
      return response.ok;
    } catch (error) {
      console.error('❌ Test de connexion échoué:', error);
      return false;
    }
  }
}

// Singleton pour éviter les instances multiples
let apiInstance: SmartSearchApi | null = null;

function getApiInstance(): SmartSearchApi {
  if (!apiInstance) {
    apiInstance = new SmartSearchApi();
  }
  return apiInstance;
}

// Export principal - APPELS DIRECTS vers l'API RAG
export default {
  async sendTextMessage(question: string): Promise<ApiResponse> {
    return getApiInstance().sendTextMessage(question);
  },
 
  async sendMultimodalMessage(prompt: string, file: File): Promise<ApiResponse> {
    return getApiInstance().sendMultimodalMessage(prompt, file);
  },
 
  async getConversationHistory(): Promise<{ conversations: any[] }> {
    return { conversations: [] };
  },
 
  async testConnection(): Promise<boolean> {
    return getApiInstance().testConnection();
  }
};