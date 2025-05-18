// components/ConversationHistory.vue
<template>
  <div class="conversation-history">
    <div class="history-header">
      <h3>Historique des conversations</h3>
      <button 
        class="clear-history-btn" 
        v-if="conversations.length > 1"
        @click="confirmClearHistory"
      >
        <i class="fas fa-trash"></i>
      </button>
    </div>
    
    <div class="search-box">
      <input 
        type="text" 
        v-model="searchQuery" 
        placeholder="Rechercher une conversation..." 
        class="search-input"
      />
      <i class="fas fa-search search-icon"></i>
    </div>
    
    <div class="conversation-list">
      <div 
        v-for="conversation in filteredConversations" 
        :key="conversation.id"
        class="conversation-item"
        :class="{ 'active': conversation.id === currentConversationId }"
        @click="selectConversation(conversation.id)"
      >
        <div class="conversation-info">
          <div class="conversation-title">{{ conversation.title }}</div>
          <div class="conversation-date">{{ formatDate(conversation.lastUpdated) }}</div>
        </div>
        <div class="conversation-actions">
          <button 
            class="delete-btn" 
            @click.stop="confirmDeleteConversation(conversation.id)"
            title="Supprimer cette conversation"
          >
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>
      
      <div v-if="filteredConversations.length === 0" class="no-conversations">
        <p v-if="searchQuery">Aucune conversation ne correspond à votre recherche.</p>
        <p v-else>Aucune conversation disponible.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useConversationStore } from '~/store/conversationStore';

const conversationStore = useConversationStore();
const searchQuery = ref('');

// Propriétés calculées
const conversations = computed(() => conversationStore.allConversations);
const currentConversationId = computed(() => conversationStore.currentConversationId);

// Filtrer les conversations selon la recherche
const filteredConversations = computed(() => {
  if (!searchQuery.value) return conversations.value;
  
  const query = searchQuery.value.toLowerCase();
  return conversations.value.filter(conversation => 
    conversation.title.toLowerCase().includes(query) ||
    conversation.messages.some(msg => 
      msg.sender === 'user' && msg.text.toLowerCase().includes(query)
    )
  );
});

// Fonctions
const selectConversation = (conversationId) => {
  conversationStore.selectConversation(conversationId);
};

const confirmDeleteConversation = (conversationId) => {
  if (confirm('Êtes-vous sûr de vouloir supprimer cette conversation ?')) {
    conversationStore.deleteConversation(conversationId);
  }
};

const confirmClearHistory = () => {
  if (confirm('Êtes-vous sûr de vouloir supprimer toutes les conversations sauf la conversation actuelle ?')) {
    const currentId = currentConversationId.value;
    
    // Supprimer toutes les conversations sauf la courante
    conversations.value.forEach(conv => {
      if (conv.id !== currentId) {
        conversationStore.deleteConversation(conv.id);
      }
    });
  }
};

const formatDate = (dateString) => {
  const date = new Date(dateString);
  const now = new Date();
  const diff = now - date;
  
  // Moins d'une heure
  if (diff < 3600000) {
    const minutes = Math.floor(diff / 60000);
    return minutes <= 1 ? 'À l\'instant' : `Il y a ${minutes} min`;
  }
  
  // Aujourd'hui
  if (date.toDateString() === now.toDateString()) {
    return `Aujourd'hui ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`;
  }
  
  // Hier
  const yesterday = new Date(now);
  yesterday.setDate(now.getDate() - 1);
  if (date.toDateString() === yesterday.toDateString()) {
    return `Hier ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`;
  }
  
  // Cette semaine
  const weekDays = ['Dim', 'Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam'];
  if (diff < 604800000) { // 7 jours
    return `${weekDays[date.getDay()]} ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`;
  }
  
  // Plus ancien
  return `${date.getDate()}/${date.getMonth() + 1}/${date.getFullYear()}`;
};
</script>

<style scoped>
.conversation-history {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid #e0e0e0;
}

.history-header h3 {
  font-size: 16px;
  font-weight: 500;
  margin: 0;
}

.clear-history-btn {
  background: none;
  border: none;
  color: #5f6368;
  cursor: pointer;
  font-size: 14px;
  padding: 5px;
}

.clear-history-btn:hover {
  color: #ea4335;
}

.search-box {
  padding: 10px 15px;
  position: relative;
}

.search-input {
  width: 100%;
  padding: 8px 30px 8px 10px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 14px;
  outline: none;
}

.search-input:focus {
  border-color: #1a73e8;
}

.search-icon {
  position: absolute;
  right: 25px;
  top: 18px;
  color: #5f6368;
}

.conversation-list {
  flex: 1;
  overflow-y: auto;
}

.conversation-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  border-bottom: 1px solid #f1f3f4;
  cursor: pointer;
  transition: background-color 0.2s;
}

.conversation-item:hover {
  background-color: #f8f9fa;
}

.conversation-item.active {
  background-color: #e8f0fe;
}

.conversation-info {
  flex: 1;
  min-width: 0;
}

.conversation-title {
  font-size: 14px;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.conversation-date {
  font-size: 12px;
  color: #5f6368;
}

.conversation-actions {
  opacity: 0;
  transition: opacity 0.2s;
}

.conversation-item:hover .conversation-actions {
  opacity: 1;
}

.delete-btn {
  background: none;
  border: none;
  color: #5f6368;
  cursor: pointer;
  font-size: 14px;
  padding: 5px;
}

.delete-btn:hover {
  color: #ea4335;
}

.no-conversations {
  padding: 20px;
  text-align: center;
  color: #5f6368;
}
</style>
