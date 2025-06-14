<template>
  <div class="message-container" :class="{ 'user-message': isUser, 'assistant-message': !isUser }">
    <!-- Avatar -->
    <div class="avatar-circle" v-if="!isUser">
      {{ senderName?.charAt(0) || 'H' }}
    </div>
    <div class="avatar-circle user-avatar" v-else>
      <i class="fas fa-user"></i>
    </div>

    <!-- Message Content -->
    <div class="message-content">
      <!-- Sender Info -->
      <div class="message-header" v-if="!isUser">
        <span class="sender-name">{{ senderName }}</span>
        <span class="timestamp" v-if="processingTime">{{ processingTime }}</span>
      </div>

      <!-- Message Text -->
      <div class="message-text" :class="{ 'error-message': isError }">
        <!-- Rendu markdown pour les messages non-utilisateur -->
        <div v-if="!isUser" v-html="renderedMarkdown" class="markdown-content"></div>
        <!-- Texte simple pour les messages utilisateur -->
        <div v-else class="user-text">{{ text }}</div>
      </div>

      <!-- Actions -->
      <div class="message-actions" v-if="actions && actions.length > 0 && !isUser">
        <button 
          v-for="action in actions" 
          :key="action.type"
          @click="$emit('action-clicked', action.type)"
          class="action-btn"
          :title="action.label"
        >
          <i :class="action.icon"></i>
          {{ action.label }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

// Props
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
    default: 'Assistant'
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
    type: String,
    default: ''
  }
});

// Events
defineEmits(['action-clicked']);

// Fonction avancée pour convertir le markdown en HTML proprement
const parseMarkdown = (text) => {
  if (!text) return '';
  
  let html = text;
  
  // Nettoyer le texte d'abord
  html = html.trim();
  
  // Supprimer les ### isolés qui ne sont pas des titres
  html = html.replace(/\s###\s/g, ' ');
  html = html.replace(/^###\s*$/gm, '');
  
  // Conversion des titres (ordre important : du plus spécifique au plus général)
  html = html.replace(/^#### (.*$)/gm, '<h4 class="markdown-h4">$1</h4>');
  html = html.replace(/^### (.*$)/gm, '<h3 class="markdown-h3">$1</h3>');
  html = html.replace(/^## (.*$)/gm, '<h2 class="markdown-h2">$1</h2>');
  html = html.replace(/^# (.*$)/gm, '<h1 class="markdown-h1">$1</h1>');
  
  // Séparateurs
  html = html.replace(/^---+$/gm, '<hr class="markdown-separator">');
  
  // Gras et italique (ordre important)
  html = html.replace(/\*\*\*(.*?)\*\*\*/g, '<strong class="markdown-bold"><em>$1</em></strong>');
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong class="markdown-bold">$1</strong>');
  html = html.replace(/\*(.*?)\*/g, '<em class="markdown-italic">$1</em>');
  
  // Code inline
  html = html.replace(/`([^`]+)`/g, '<code class="markdown-code">$1</code>');
  
  // Liens
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" class="markdown-link" target="_blank">$1</a>');
  
  // Citations
  html = html.replace(/^> (.*$)/gm, '<blockquote class="markdown-quote">$1</blockquote>');
  
  // Traitement des listes (complexe)
  const lines = html.split('\n');
  const processedLines = [];
  let inList = false;
  let inNumberedList = false;
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmedLine = line.trim();
    
    // Liste à puces
    if (trimmedLine.match(/^- .+/)) {
      if (!inList) {
        processedLines.push('<ul class="markdown-list">');
        inList = true;
      }
      processedLines.push(`<li class="markdown-list-item">${trimmedLine.substring(2).trim()}</li>`);
    }
    // Liste numérotée
    else if (trimmedLine.match(/^\d+\. .+/)) {
      if (!inNumberedList) {
        processedLines.push('<ol class="markdown-numbered-list">');
        inNumberedList = true;
      }
      const content = trimmedLine.replace(/^\d+\.\s*/, '');
      processedLines.push(`<li class="markdown-numbered-item">${content}</li>`);
    }
    // Ligne normale
    else {
      // Fermer les listes si nécessaire
      if (inList) {
        processedLines.push('</ul>');
        inList = false;
      }
      if (inNumberedList) {
        processedLines.push('</ol>');
        inNumberedList = false;
      }
      processedLines.push(line);
    }
  }
  
  // Fermer les listes ouvertes
  if (inList) processedLines.push('</ul>');
  if (inNumberedList) processedLines.push('</ol>');
  
  html = processedLines.join('\n');
  
  // Convertir en paragraphes (éviter les éléments de bloc)
  const paragraphs = html.split('\n\n').filter(p => p.trim());
  html = paragraphs.map(paragraph => {
    const trimmed = paragraph.trim();
    
    // Ne pas encapsuler dans <p> si c'est déjà un élément de bloc
    if (trimmed.match(/^<(h[1-6]|ul|ol|blockquote|hr|div)/)) {
      return trimmed;
    }
    
    // Ne pas encapsuler les lignes vides
    if (!trimmed) {
      return '';
    }
    
    // Encapsuler le reste dans des paragraphes
    return `<p class="markdown-paragraph">${trimmed.replace(/\n/g, '<br>')}</p>`;
  }).filter(p => p).join('\n');
  
  // Nettoyage final
  html = html.replace(/\n{3,}/g, '\n\n'); // Réduire les espaces multiples
  html = html.replace(/<p class="markdown-paragraph">\s*<\/p>/g, ''); // Supprimer paragraphes vides
  
  return html;
};

// Computed pour le rendu markdown
const renderedMarkdown = computed(() => {
  return parseMarkdown(props.text);
});
</script>

<style scoped>
.message-container {
  display: flex;
  align-items: flex-start;
  margin-bottom: 20px;
  animation: slideIn 0.3s ease-out;
}

.user-message {
  flex-direction: row-reverse;
}

.assistant-message {
  flex-direction: row;
}

.avatar-circle {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
  flex-shrink: 0;
}

.assistant-message .avatar-circle {
  background-color: #1a73e8;
  color: white;
  margin-right: 12px;
}

.user-message .avatar-circle {
  background-color: #34a853;
  color: white;
  margin-left: 12px;
}

.message-content {
  max-width: 80%;
  min-width: 200px;
}

.message-header {
  display: flex;
  align-items: center;
  margin-bottom: 6px;
  gap: 10px;
}

.sender-name {
  font-weight: 600;
  font-size: 14px;
  color: #202124;
}

.timestamp {
  font-size: 12px;
  color: #5f6368;
  background-color: #f1f3f4;
  padding: 2px 6px;
  border-radius: 8px;
}

.message-text {
  background-color: white;
  padding: 16px 20px;
  border-radius: 18px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  line-height: 1.5;
  word-wrap: break-word;
}

.user-message .message-text {
  background-color: #1a73e8;
  color: white;
  border-radius: 18px 18px 4px 18px;
}

.assistant-message .message-text {
  border-radius: 4px 18px 18px 18px;
}

.error-message {
  background-color: #fce8e6;
  border-left: 4px solid #ea4335;
  color: #d93025;
}

.user-text {
  font-size: 15px;
}

/* Styles pour le contenu Markdown */
.markdown-content {
  font-size: 15px;
  color: #202124;
}

/* Styles pour les sections numérotées spéciales */
:deep(.numbered-section) {
  margin: 20px 0;
  padding: 16px;
  border: 2px solid #e8f0fe;
  border-radius: 12px;
  background: linear-gradient(135deg, #fafbff 0%, #f8fbff 100%);
  box-shadow: 0 3px 6px rgba(26, 115, 232, 0.1);
  position: relative;
}

:deep(.section-number) {
  display: inline-block;
  background: linear-gradient(135deg, #1a73e8 0%, #1967d2 100%);
  color: white;
  font-weight: 700;
  font-size: 16px;
  padding: 8px 12px;
  border-radius: 50%;
  margin-right: 12px;
  min-width: 40px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(26, 115, 232, 0.3);
}

:deep(.section-title) {
  font-size: 18px;
  font-weight: 700;
  color: #1a73e8;
  margin-right: 8px;
}

:deep(.section-separator) {
  font-size: 18px;
  font-weight: 700;
  color: #34a853;
  margin-right: 12px;
}

:deep(.section-content) {
  margin-top: 12px;
  padding-left: 52px;
  line-height: 1.7;
  color: #333;
  font-size: 15px;
  text-align: justify;
}

/* Styles pour les titres */
:deep(.markdown-h1) {
  font-size: 28px;
  font-weight: 700;
  color: #1a73e8;
  margin: 32px 0 20px 0;
  padding: 12px 0;
  border-bottom: 3px solid #1a73e8;
  text-align: center;
  background: linear-gradient(135deg, #f8fbff 0%, #e8f0fe 100%);
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(26, 115, 232, 0.1);
}

:deep(.markdown-h2) {
  font-size: 22px;
  font-weight: 600;
  color: #1967d2;
  margin: 24px 0 16px 0;
  padding: 8px 12px;
  border-left: 4px solid #1967d2;
  background-color: #f8fbff;
  border-radius: 0 6px 6px 0;
}

:deep(.markdown-h3) {
  font-size: 19px;
  font-weight: 600;
  color: #1557b0;
  margin: 20px 0 12px 0;
  padding: 6px 0;
  border-bottom: 2px dotted #1557b0;
}

:deep(.markdown-h4) {
  font-size: 17px;
  font-weight: 500;
  color: #174ea6;
  margin: 16px 0 8px 0;
  font-style: italic;
}

/* Styles pour les paragraphes */
:deep(.markdown-paragraph) {
  margin: 14px 0;
  line-height: 1.7;
  text-align: justify;
  text-indent: 0;
  color: #333;
  font-size: 15px;
}

/* Styles pour le texte en gras et italique */
:deep(.markdown-bold) {
  font-weight: 700;
  color: #1a73e8;
  background: linear-gradient(120deg, transparent 0%, rgba(26, 115, 232, 0.1) 100%);
  padding: 1px 3px;
  border-radius: 3px;
}

:deep(.markdown-italic) {
  font-style: italic;
  color: #5f6368;
  font-weight: 500;
}

/* Styles pour les listes */
:deep(.markdown-list) {
  margin: 18px 0;
  padding-left: 0;
  background-color: #fafbfc;
  border-radius: 8px;
  padding: 12px;
  border-left: 3px solid #34a853;
}

:deep(.markdown-list-item) {
  margin: 10px 0;
  padding: 8px 0 8px 28px;
  position: relative;
  list-style: none;
  color: #333;
  line-height: 1.6;
  border-bottom: 1px dotted #e0e0e0;
}

:deep(.markdown-list-item:last-child) {
  border-bottom: none;
}

:deep(.markdown-list-item::before) {
  content: "▶";
  color: #34a853;
  font-weight: bold;
  position: absolute;
  left: 8px;
  top: 8px;
  font-size: 12px;
}

:deep(.markdown-numbered-list) {
  margin: 18px 0;
  padding: 12px 12px 12px 32px;
  background-color: #fff8e1;
  border-radius: 8px;
  border-left: 3px solid #fbbc04;
  counter-reset: list-counter;
}

:deep(.markdown-numbered-item) {
  margin: 10px 0;
  padding: 8px 0;
  color: #333;
  line-height: 1.6;
  counter-increment: list-counter;
  border-bottom: 1px dotted #e0e0e0;
  position: relative;
}

:deep(.markdown-numbered-item:last-child) {
  border-bottom: none;
}

:deep(.markdown-numbered-item::before) {
  content: counter(list-counter) ".";
  color: #fbbc04;
  font-weight: bold;
  position: absolute;
  left: -20px;
  top: 8px;
  background-color: #fff;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  border: 2px solid #fbbc04;
}

/* Styles pour les citations */
:deep(.markdown-quote) {
  border-left: 5px solid #ea4335;
  padding: 16px 20px;
  margin: 20px 0;
  background: linear-gradient(135deg, #fef7f0 0%, #fce8e6 100%);
  border-radius: 0 12px 12px 0;
  font-style: italic;
  color: #d93025;
  position: relative;
  box-shadow: 2px 2px 8px rgba(234, 67, 53, 0.1);
}

:deep(.markdown-quote::before) {
  content: '"';
  font-size: 48px;
  color: #ea4335;
  position: absolute;
  left: -10px;
  top: -10px;
  opacity: 0.3;
}

/* Styles pour le code */
:deep(.markdown-code) {
  background: linear-gradient(135deg, #f1f3f4 0%, #e8eaed 100%);
  padding: 4px 8px;
  border-radius: 6px;
  font-family: 'Courier New', Monaco, monospace;
  font-size: 13px;
  color: #d93025;
  border: 1px solid #dadce0;
  font-weight: 500;
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.1);
}

/* Styles pour les séparateurs */
:deep(.markdown-separator) {
  border: none;
  height: 3px;
  background: linear-gradient(90deg, transparent 0%, #1a73e8 20%, #34a853 50%, #fbbc04 80%, transparent 100%);
  margin: 32px 0;
  border-radius: 2px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Styles pour les liens */
:deep(.markdown-link) {
  color: #1a73e8;
  text-decoration: none;
  border-bottom: 2px dotted #1a73e8;
  transition: all 0.3s ease;
  padding: 2px 4px;
  border-radius: 4px;
  font-weight: 500;
}

:deep(.markdown-link:hover) {
  background: linear-gradient(135deg, #e8f0fe 0%, #cfe2ff 100%);
  border-bottom: 2px solid #1a73e8;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(26, 115, 232, 0.2);
}

/* Actions */
.message-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  flex-wrap: wrap;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background-color: #f1f3f4;
  border: none;
  border-radius: 16px;
  font-size: 12px;
  color: #5f6368;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background-color: #e8eaed;
  color: #202124;
}

.action-btn i {
  font-size: 12px;
}

/* Animation */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive */
@media (max-width: 768px) {
  .message-content {
    max-width: 85%;
    min-width: 150px;
  }
  
  .message-text {
    padding: 12px 16px;
  }
  
  :deep(.markdown-h1) {
    font-size: 20px;
  }
  
  :deep(.markdown-h2) {
    font-size: 18px;
  }
  
  :deep(.markdown-h3) {
    font-size: 16px;
  }
}
</style>