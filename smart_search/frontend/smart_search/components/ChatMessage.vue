// components/ChatMessage.vue
<template>
  <div class="message-container" :class="{ 'assistant-message': !isUser, 'user-message': isUser }">
    <div class="message-avatar" v-if="!isUser">
      <div class="avatar-circle">H</div>
    </div>
    <div class="message-content" :class="{ 'error-message': isError }">
      <div class="message-header" v-if="!isUser">
        <span class="message-sender">{{ senderName }}</span>
        <span class="processing-time" v-if="processingTime">
          {{ formatProcessingTime(processingTime) }}
        </span>
      </div>
      <div class="message-text formatted-content" v-html="formattedText"></div>
      <div class="message-actions" v-if="!isUser && actions && actions.length > 0">
        <button 
          v-for="(action, index) in actions" 
          :key="index" 
          class="action-btn"
          @click="$emit('action-clicked', action.type)"
        >
          <i :class="action.icon"></i> {{ action.label }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  text: {
    type: String,
    required: true
  },
  isUser: {
    type: Boolean,
    default: false
  },
  senderName: {
    type: String,
    default: 'Assistant Halki'
  },
  actions: {
    type: Array,
    default: () => []
  },
  isError: {
    type: Boolean,
    default: false
  },
  processingTime: {
    type: Number,
    default: null
  }
});

defineEmits(['action-clicked']);

// Fonction pour formater le texte sans dépendance externe
const formattedText = computed(() => {
  if (!props.text) return '';

  // Si c'est un message utilisateur, on conserve le formatage simple
  if (props.isUser) {
    return props.text.replace(/\n/g, '<br>');
  }
  
  // Pour les messages de l'assistant, on applique un formatage personnalisé
  let html = props.text;
  
  // Traiter les titres (h1 à h3)
  html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');
  html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
  html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
  
  // Traiter les listes à puces
  html = html.replace(/^- (.+)$/gm, '<li>$1</li>');
  html = html.replace(/<li>(.+)<\/li>(\s*)<li>/g, '<li>$1</li><ul><li>');
  html = html.replace(/<\/li>(\s*)$/g, '</li></ul>');

  // Traiter les paragraphes
  const paragraphs = html.split('\n\n');
  html = paragraphs.map(p => {
    if (!p.trim()) return '';
    if (p.match(/^<h[1-3]>|^<ul>|^<li>/)) return p; // Ne pas envelopper les titres et listes
    return `<p>${p}</p>`;
  }).join('\n');
  
  // Traiter le gras
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  
  // Traiter l'italique
  html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');
  
  // Traiter les séparateurs
  html = html.replace(/^---$/gm, '<hr>');
  
  // Remplacer les sauts de ligne simples par des <br> à l'intérieur des paragraphes
  html = html.replace(/<p>(.+?)\n(.+?)<\/p>/gs, (match, p1, p2) => {
    return `<p>${p1}<br>${p2}</p>`;
  });
  
  // Nettoyer et finaliser
  html = html.replace(/\n/g, ' ');
  
  return html;
});

// Formater le temps de traitement
const formatProcessingTime = (seconds) => {
  if (seconds < 0.01) return 'Instantané';
  if (seconds < 1) return `${Math.round(seconds * 1000)}ms`;
  return `${seconds.toFixed(2)}s`;
};
</script>

<style>
/* Styles pour le contenu formaté */
.formatted-content {
  line-height: 1.6;
}

.formatted-content h1 {
  font-size: 1.8em;
  margin: 1em 0 0.5em;
  padding-bottom: 0.3em;
  border-bottom: 1px solid #eaecef;
  color: #24292e;
}

.formatted-content h2 {
  font-size: 1.5em;
  margin: 1em 0 0.5em;
  padding-bottom: 0.2em;
  color: #0366d6;
}

.formatted-content h3 {
  font-size: 1.25em;
  margin: 1em 0 0.5em;
  color: #24292e;
}

.formatted-content p {
  margin: 0.7em 0;
}

.formatted-content ul, .formatted-content ol {
  margin: 0.7em 0;
  padding-left: 2em;
}

.formatted-content li {
  margin: 0.3em 0;
}

.formatted-content hr {
  height: 1px;
  padding: 0;
  margin: 1.5em 0;
  background-color: #e1e4e8;
  border: 0;
}

.formatted-content strong {
  font-weight: 600;
}

.formatted-content em {
  font-style: italic;
}

/* Styles spécifiques pour les messages */
.message-container {
  display: flex;
  margin-bottom: 20px;
  transition: all 0.3s ease;
}

.assistant-message {
  align-self: flex-start;
  max-width: 90%;
}

.user-message {
  align-self: flex-end;
  justify-content: flex-end;
  max-width: 80%;
}

.message-avatar {
  margin-right: 12px;
  align-self: flex-start;
}

.avatar-circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: #1a73e8;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
}

.message-content {
  background-color: white;
  padding: 16px 20px;
  border-radius: 8px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  transform-origin: left center;
  transition: transform 0.2s ease;
  position: relative;
}

.message-content:hover {
  transform: scale(1.01);
}

.user-message .message-content {
  background-color: #1a73e8;
  color: white;
  transform-origin: right center;
}

.error-message {
  background-color: #fdeded !important;
  border-left: 3px solid #ea4335;
  color: #5f6368 !important;
}

.message-header {
  margin-bottom: 10px;
  font-size: 14px;
  color: #5f6368;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #f1f3f4;
  padding-bottom: 8px;
}

.processing-time {
  font-size: 12px;
  color: #9aa0a6;
  font-weight: normal;
}

.user-message .message-header {
  color: rgba(255, 255, 255, 0.8);
}

.message-text {
  font-size: 14px;
  line-height: 1.5;
}

.message-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #f1f3f4;
  transition: opacity 0.2s ease;
  opacity: 0.8;
}

.message-content:hover .message-actions {
  opacity: 1;
}

.action-btn {
  padding: 6px 10px;
  background-color: #f1f3f4;
  border: none;
  border-radius: 16px;
  font-size: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: background-color 0.2s, transform 0.1s;
}

.action-btn:hover {
  background-color: #e8eaed;
  transform: translateY(-1px);
}

.action-btn:active {
  transform: translateY(0);
}

.action-btn i {
  margin-right: 6px;
  font-size: 12px;
}

/* Mobile Responsive Styles */
@media (max-width: 768px) {
  .message-container {
    max-width: 95%;
  }
  
  .message-avatar {
    margin-right: 8px;
  }
  
  .avatar-circle {
    width: 28px;
    height: 28px;
    font-size: 12px;
  }
  
  .message-content {
    padding: 12px 16px;
  }
  
  .message-actions {
    flex-direction: column;
    gap: 6px;
  }
  
  .action-btn {
    font-size: 11px;
    padding: 5px 8px;
  }
}
</style>
