// store/conversationStore.js
import { defineStore } from 'pinia';

export const useConversationStore = defineStore('conversation', {
  state: () => ({
    conversations: [],
    currentConversationId: null,
    isLoading: false,
    error: null
  }),
  
  getters: {
    currentConversation: (state) => {
      return state.conversations.find(c => c.id === state.currentConversationId) || null;
    },
    
    allConversations: (state) => {
      return state.conversations.sort((a, b) => new Date(b.lastUpdated) - new Date(a.lastUpdated));
    }
  },
  
  actions: {
    // Créer une nouvelle conversation
    createConversation(title = 'Nouvelle discussion') {
      const now = new Date().toISOString();
      const conversationId = `conv-${Date.now()}`;
      
      const newConversation = {
        id: conversationId,
        title,
        messages: [],
        created: now,
        lastUpdated: now
      };
      
      // Ajouter un message de bienvenue
      const welcomeMsg = {
        id: `msg-${Date.now()}`,
        sender: 'assistant',
        senderName: 'Assistant Hakili',
        text: "# Bienvenue sur l'Assistant Hakili\n\nJe suis l'assistant virtuel de l'ISFAD. Comment puis-je vous aider aujourd'hui?\n\nVous pouvez me poser des questions sur divers sujets. Je suis capable de structurer mes réponses de manière claire.",
        timestamp: now,
        actions: [
          { type: 'extract', label: 'Texte réimprimable (à extraire)', icon: 'fas fa-copy' },
          { type: 'bookmark', label: 'Marquer ce dialogue', icon: 'fas fa-bookmark' }
        ]
      };
      
      newConversation.messages.push(welcomeMsg);
      this.conversations.push(newConversation);
      this.currentConversationId = conversationId;
      
      // Sauvegarder dans le stockage local
      this.saveToLocalStorage();
      
      return conversationId;
    },
    
    // Sélectionner une conversation existante
    selectConversation(conversationId) {
      if (this.conversations.some(c => c.id === conversationId)) {
        this.currentConversationId = conversationId;
        return true;
      }
      return false;
    },
    
    // Ajouter un message à la conversation courante
    addMessage(message) {
      const conversation = this.conversations.find(c => c.id === this.currentConversationId);
      
      if (!conversation) return false;
      
      conversation.messages.push({
        ...message,
        id: message.id || `msg-${Date.now()}`
      });
      
      conversation.lastUpdated = new Date().toISOString();
      
      // Mettre à jour le titre si c'est le premier message utilisateur
      const userMessages = conversation.messages.filter(m => m.sender === 'user');
      if (userMessages.length === 1 && userMessages[0].text) {
        // Utilise les premiers mots du message utilisateur comme titre
        conversation.title = userMessages[0].text.substring(0, 30) + (userMessages[0].text.length > 30 ? '...' : '');
      }
      
      // Sauvegarder dans le stockage local
      this.saveToLocalStorage();
      
      return true;
    },
    
    // Supprimer une conversation
    deleteConversation(conversationId) {
      const index = this.conversations.findIndex(c => c.id === conversationId);
      
      if (index !== -1) {
        this.conversations.splice(index, 1);
        
        // Si la conversation supprimée était la courante, choisir une autre
        if (this.currentConversationId === conversationId) {
          this.currentConversationId = this.conversations.length > 0 ? this.conversations[0].id : null;
        }
        
        // Sauvegarder dans le stockage local
        this.saveToLocalStorage();
        
        return true;
      }
      
      return false;
    },
    
    // Charger les conversations depuis le stockage local
    loadFromLocalStorage() {
      try {
        const savedState = localStorage.getItem('halki-conversations');
        
        if (savedState) {
          const parsedState = JSON.parse(savedState);
          this.conversations = parsedState.conversations || [];
          this.currentConversationId = parsedState.currentConversationId;
          
          // Si pas de conversation active mais des conversations existent
          if (!this.currentConversationId && this.conversations.length > 0) {
            this.currentConversationId = this.conversations[0].id;
          }
          
          return true;
        }
      } catch (error) {
        console.error('Erreur lors du chargement des conversations:', error);
      }
      
      return false;
    },
    
    // Sauvegarder les conversations dans le stockage local
    saveToLocalStorage() {
      try {
        const stateToSave = {
          conversations: this.conversations,
          currentConversationId: this.currentConversationId
        };
        
        localStorage.setItem('halki-conversations', JSON.stringify(stateToSave));
        return true;
      } catch (error) {
        console.error('Erreur lors de la sauvegarde des conversations:', error);
        return false;
      }
    },
    
    // Synchroniser avec l'API (à implémenter ultérieurement)
    async syncWithApi() {
      // TODO: Implémenter la synchronisation avec l'API backend
      // Cette fonction pourrait envoyer les conversations au serveur
      // ou récupérer les conversations depuis le serveur
      console.log('Synchronisation avec l\'API non implémentée');
    }
  }
});
