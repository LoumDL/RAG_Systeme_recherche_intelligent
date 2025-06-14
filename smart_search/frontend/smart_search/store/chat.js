// store/chat.js - Utilisation de Pinia pour la gestion d'état
import { defineStore } from 'pinia';
import chatApi from '~/api/chat';

export const useChatStore = defineStore('chat', {
  state: () => ({
    conversations: [],
    currentConversationId: null,
    messages: [],
    isLoading: false,
    error: null
  }),
  
  getters: {
    currentConversation: (state) => {
      return state.conversations.find(conv => conv.id === state.currentConversationId) || null;
    },
    
    orderedMessages: (state) => {
      return [...state.messages].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
    }
  },
  
  actions: {
    async fetchConversations() {
      this.isLoading = true;
      this.error = null;
      
      try {
        const response = await chatApi.getConversationHistory();
        this.conversations = response.conversations;
        
        if (this.conversations.length > 0 && !this.currentConversationId) {
          this.currentConversationId = this.conversations[0].id;
          await this.fetchMessages(this.currentConversationId);
        }
      } catch (error) {
        this.error = error.message;
        console.error('Erreur lors de la récupération des conversations:', error);
      } finally {
        this.isLoading = false;
      }
    },
    
    async fetchMessages(conversationId) {
      this.isLoading = true;
      this.error = null;
      
      try {
        // Simulation pour la démo - Remplacer par un vrai appel API
        // const response = await chatApi.getMessages(conversationId);
        // this.messages = response.messages;
        
        // Pour la démo, on crée un message de bienvenue statique
        this.messages = [
          {
            id: '1',
            conversationId,
            sender: 'assistant',
            senderName: 'Assistant Hakili',
            text: "Bonjour! 👋 Je suis l'assistant virtuel de l'ISFAD. Comment puis-je vous aider aujourd'hui?\n\nVous pouvez me poser des questions sur nos cours, les détails de cours, ou d'autres questions.",
            timestamp: new Date().toISOString(),
            actions: [
              { type: 'extract', label: 'Texte réimprimable (à extraire)', icon: 'fas fa-copy' },
              { type: 'bookmark', label: 'Marquer ce dialogue', icon: 'fas fa-bookmark' },
              { type: 'share', label: 'Partager ce dialogue', icon: 'fas fa-share' }
            ]
          }
        ];
        
        this.currentConversationId = conversationId;
      } catch (error) {
        this.error = error.message;
        console.error('Erreur lors de la récupération des messages:', error);
      } finally {
        this.isLoading = false;
      }
    },
    
    async sendMessage(text) {
      if (!text.trim() || !this.currentConversationId) return;
      
      // Ajouter le message utilisateur localement immédiatement pour l'UX
      const userMessage = {
        id: `user-${Date.now()}`,
        conversationId: this.currentConversationId,
        sender: 'user',
        text,
        timestamp: new Date().toISOString()
      };
      
      this.messages.push(userMessage);
      this.isLoading = true;
      
      try {
        // Appel API - Remplacer par votre API réelle
        // const response = await chatApi.sendMessage(this.currentConversationId, text);
        
        // Pour la démo, simuler une réponse de l'assistant
        setTimeout(() => {
          const assistantMessage = {
            id: `assistant-${Date.now()}`,
            conversationId: this.currentConversationId,
            sender: 'assistant',
            senderName: 'Assistant Hakili',
            text: "Je peux vous aider pour le module de sensibilisation ISFAD-2022-001 à mettre avant le 15 juillet.\n\nLes informations principales sont sur les détails d'eic (header_footer). Pouvez-vous être plus spécifique ?",
            timestamp: new Date().toISOString(),
            actions: [
              { type: 'location', label: 'Accéder à l\'endroit décrit', icon: 'fas fa-map-pin' },
              { type: 'schedule', label: 'Programmer ce rappel', icon: 'fas fa-calendar' }
            ]
          };
          
          this.messages.push(assistantMessage);
          this.isLoading = false;
        }, 1000);
      } catch (error) {
        this.error = error.message;
        console.error('Erreur lors de l\'envoi du message:', error);
        this.isLoading = false;
      }
    },
    
    async createNewConversation() {
      this.isLoading = true;
      this.error = null;
      
      try {
        // Simulation pour la démo - Remplacer par un vrai appel API
        // const response = await chatApi.createNewConversation();
        // this.currentConversationId = response.conversationId;
        
        // Pour la démo, créer un ID statique
        const newConversationId = `conv-${Date.now()}`;
        const newConversation = {
          id: newConversationId,
          title: 'Nouvelle discussion',
          timestamp: new Date().toISOString()
        };
        
        this.conversations.unshift(newConversation);
        this.currentConversationId = newConversationId;
        this.messages = [
          {
            id: '1',
            conversationId: newConversationId,
            sender: 'assistant',
            senderName: 'Assistant Hakili',
            text: "Bonjour! 👋 Je suis l'assistant virtuel de l'ISFAD. Comment puis-je vous aider aujourd'hui?\n\nVous pouvez me poser des questions sur nos cours, les détails de cours, ou d'autres questions.",
            timestamp: new Date().toISOString(),
            actions: [
              { type: 'extract', label: 'Texte réimprimable (à extraire)', icon: 'fas fa-copy' },
              { type: 'bookmark', label: 'Marquer ce dialogue', icon: 'fas fa-bookmark' },
              { type: 'share', label: 'Partager ce dialogue', icon: 'fas fa-share' }
            ]
          }
        ];
      } catch (error) {
        this.error = error.message;
        console.error('Erreur lors de la création d\'une nouvelle conversation:', error);
      } finally {
        this.isLoading = false;
      }
    },
    
    handleAction(actionType, messageId) {
      // Implémenter les actions selon vos besoins
      switch (actionType) {
        case 'extract':
          console.log('Extraire le texte du message', messageId);
          // Logique d'extraction
          break;
        case 'bookmark':
          console.log('Marquer le message', messageId);
          // Logique de marquage
          break;
        case 'share':
          console.log('Partager le message', messageId);
          // Logique de partage
          break;
        case 'location':
          console.log('Accéder à l\'emplacement', messageId);
          // Logique de navigation
          break;
        case 'schedule':
          console.log('Programmer un rappel', messageId);
          // Logique de programmation
          break;
        default:
          console.log('Action non reconnue', actionType);
      }
    }
  }
});
