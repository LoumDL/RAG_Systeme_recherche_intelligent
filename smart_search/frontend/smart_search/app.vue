
<template>
  <div class="app-container">
    <!-- Sidebar -->
    <div class="sidebar" :class="{ 'sidebar-open': isSidebarOpen }">
      <div class="sidebar-header">
        <div class="logo-container">
          <img src="/logo-ifad.png" alt="IFAD Logo" class="logo" />
          <span class="logo-text">IFAD</span>
        </div>
        <div class="logo-divider"></div>
        <div class="assistant-name">Halki</div>
        
        <!-- Bouton de fermeture pour mobile -->
        <button class="close-sidebar-btn" @click="toggleSidebar" v-if="isMobile">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <button class="new-document-btn" @click="startNewChat">
        <i class="fas fa-plus"></i> Nouvelle Discussion
      </button>

      <!-- Historique des conversations -->
      <ConversationHistory />

      <!-- Les entrées de menu ont été supprimées conformément à la demande -->
    </div>

    <!-- Mobile sidebar toggle -->
    <button class="mobile-menu-btn" @click="toggleSidebar" v-if="isMobile && !isSidebarOpen">
      <i class="fas fa-bars"></i>
    </button>

    <!-- Main Content -->
    <div class="main-content">
      <div class="chat-header">
        <div class="chat-title">
          <span>Assistant Halki</span>
          <div class="model-badge">IA</div>
        </div>
        <div class="user-info">
          <span></span>
          <img src="/user-avatar.png" alt="User Avatar" class="user-avatar" />
        </div>
      </div>

      <div class="chat-container" ref="chatContainer">
        <!-- Messages -->
        <div v-for="(message, index) in currentMessages" :key="index">
          <ChatMessage 
            :text="message.text" 
            :is-user="message.sender === 'user'" 
            :sender-name="message.senderName || 'Assistant Halki'" 
            :actions="message.actions || []"
            :is-error="message.isError || false"
            :processing-time="message.processingTime"
            @action-clicked="handleActionClick($event, message.id)"
            :class="{'slide-up': true, 'fade-in': true}"
          />
        </div>

        <!-- Message d'introduction si aucun message -->
        <div v-if="currentMessages.length === 0" class="empty-conversation">
          <div class="empty-icon">
            <i class="fas fa-comments"></i>
          </div>
          <h3>Bienvenue sur l'Assistant Halki</h3>
          <p>Posez vos questions ou partagez des fichiers pour commencer la conversation.</p>
        </div>

        <!-- Typing Indicator -->
        <div class="typing-indicator" v-if="isLoading">
          <div class="avatar-circle">H</div>
          <div class="typing-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>

      <div class="chat-input-container">
        <!-- Format Options -->
        <div class="format-options" v-if="showFormatOptions">
          <div class="format-options-header">
            <span>Options de formatage</span>
            <button class="close-format-btn" @click="showFormatOptions = false">
              <i class="fas fa-times"></i>
            </button>
          </div>
          <div class="format-buttons">
            <button @click="insertMarkdown('# ')" title="Titre principal">
              <i class="fas fa-heading"></i> H1
            </button>
            <button @click="insertMarkdown('## ')" title="Sous-titre">
              <i class="fas fa-heading"></i> H2
            </button>
            <button @click="insertMarkdown('### ')" title="Petit titre">
              <i class="fas fa-heading"></i> H3
            </button>
            <button @click="insertMarkdown('**', '**')" title="Gras">
              <i class="fas fa-bold"></i>
            </button>
            <button @click="insertMarkdown('*', '*')" title="Italique">
              <i class="fas fa-italic"></i>
            </button>
            <button @click="insertMarkdown('- ')" title="Liste à puces">
              <i class="fas fa-list-ul"></i>
            </button>
            <button @click="insertMarkdown('1. ')" title="Liste numérotée">
              <i class="fas fa-list-ol"></i>
            </button>
            <button @click="insertMarkdown('> ')" title="Citation">
              <i class="fas fa-quote-right"></i>
            </button>
            <button @click="insertMarkdown('`', '`')" title="Code">
              <i class="fas fa-code"></i>
            </button>
            <button @click="insertMarkdown('\n---\n')" title="Séparateur">
              <i class="fas fa-minus"></i>
            </button>
            <button @click="insertMarkdown('[', '](url)')" title="Lien">
              <i class="fas fa-link"></i>
            </button>
          </div>
        </div>
        
        <!-- File Upload UI -->
        <div class="file-upload-container" v-if="showFileUpload">
          <div class="file-upload-header">
            <span>Sélection de fichier</span>
            <button class="close-upload-btn" @click="cancelFileUpload">
              <i class="fas fa-times"></i>
            </button>
          </div>
          
          <div class="file-upload-area" 
               @dragover.prevent="highlightDropArea = true"
               @dragleave.prevent="highlightDropArea = false"
               @drop.prevent="onFileDrop"
               :class="{ 'highlight': highlightDropArea }">
            <div v-if="!selectedFile">
              <i class="fas fa-cloud-upload-alt"></i>
              <p>Glissez votre fichier ici ou</p>
              <label for="file-upload" class="file-upload-btn">
                Choisir un fichier
                <input id="file-upload" type="file" accept="image/jpeg,image/png,image/jpg,application/pdf" @change="onFileSelected" />
              </label>
              <p class="file-upload-info">Types supportés: JPG, PNG, PDF</p>
            </div>
            <div v-else class="selected-file">
              <div class="file-preview" v-if="isImage">
                <img :src="filePreviewUrl" alt="Aperçu de l'image" />
              </div>
              <div class="file-preview pdf" v-else-if="isPdf">
                <i class="fas fa-file-pdf"></i>
              </div>
              <div class="file-info">
                <span class="file-name">{{ selectedFile.name }}</span>
                <span class="file-size">{{ formatFileSize(selectedFile.size) }}</span>
              </div>
              <button class="remove-file-btn" @click="removeSelectedFile">
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </div>
          
          <div class="file-upload-actions">
            <button class="cancel-btn" @click="cancelFileUpload">Annuler</button>
            <button class="upload-btn" @click="sendWithFile" :disabled="!selectedFile || !newMessage.trim()">
              Envoyer avec fichier
            </button>
          </div>
        </div>
        
        <!-- Regular Chat Input -->
        <div class="chat-input-wrapper" v-if="!showFileUpload && !showFormatOptions">
          <button class="format-btn" @click="showFormatOptions = true" title="Options de formatage">
            <i class="fas fa-paragraph"></i>
          </button>

          <button class="attachment-btn" @click="showFileUpload = true">
            <i class="fas fa-paperclip"></i>
          </button>
          
          <textarea 
            v-model="newMessage" 
            class="chat-input" 
            placeholder="Écrivez votre message ici..."
            @keyup.enter.exact="sendMessage"
            @keydown.tab.prevent="handleTab"
            ref="messageInput"
            rows="1"
            @input="autoResizeTextarea"
          ></textarea>
          
          <button class="send-btn" @click="sendMessage" :disabled="!newMessage.trim() || isLoading">
            <i class="fas fa-paper-plane"></i>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>


<script setup>
import { ref, onMounted, nextTick, computed, watch } from 'vue';
import ChatMessage from './components/ChatMessage.vue';
import ConversationHistory from './components/ConversationHistory.vue';
import chatApi from './api/chat';
import { useConversationStore } from './store/conversationStore';

// Store pour les conversations
const conversationStore = useConversationStore();

// Références
const chatContainer = ref(null);
const messageInput = ref(null);
const newMessage = ref('');
const isLoading = ref(false);
const isMobile = ref(false);
const isSidebarOpen = ref(false);
const showFileUpload = ref(false);
const showFormatOptions = ref(false);
const selectedFile = ref(null);
const filePreviewUrl = ref('');
const highlightDropArea = ref(false);

// Données de la conversation courante
const currentMessages = computed(() => {
  const currentConversation = conversationStore.currentConversation;
  return currentConversation ? currentConversation.messages : [];
});

// Détection écran mobile
const checkIfMobile = () => {
  isMobile.value = window.innerWidth < 768;
};

// Auto-resize du textarea
const autoResizeTextarea = () => {
  const textarea = messageInput.value;
  if (!textarea) return;
  
  // Reset height to auto to get the correct scrollHeight
  textarea.style.height = 'auto';
  
  // Set the height to match content + add some padding
  const newHeight = Math.min(textarea.scrollHeight, 150);
  textarea.style.height = `${newHeight}px`;
};

// Gestion de la touche Tab pour l'indentation
const handleTab = (e) => {
  const textarea = messageInput.value;
  const start = textarea.selectionStart;
  const end = textarea.selectionEnd;
  
  // Insert tab at cursor position
  newMessage.value = newMessage.value.substring(0, start) + '  ' + newMessage.value.substring(end);
  
  // Move cursor after the inserted tab
  nextTick(() => {
    textarea.selectionStart = textarea.selectionEnd = start + 2;
  });
};

// Insertion de balises Markdown
const insertMarkdown = (prefix, suffix = '') => {
  const textarea = messageInput.value;
  const start = textarea.selectionStart;
  const end = textarea.selectionEnd;
  const selectedText = newMessage.value.substring(start, end);
  
  if (selectedText) {
    // Si du texte est sélectionné, on l'entoure des balises
    newMessage.value = newMessage.value.substring(0, start) + prefix + selectedText + suffix + newMessage.value.substring(end);
    nextTick(() => {
      textarea.selectionStart = start + prefix.length;
      textarea.selectionEnd = start + prefix.length + selectedText.length;
      textarea.focus();
    });
  } else {
    // Si rien n'est sélectionné, on insère simplement les balises
    newMessage.value = newMessage.value.substring(0, start) + prefix + suffix + newMessage.value.substring(end);
    nextTick(() => {
      textarea.selectionStart = textarea.selectionEnd = start + prefix.length;
      textarea.focus();
    });
  }
  
  showFormatOptions.value = false;
};

// Propriétés calculées pour le type de fichier
const isImage = computed(() => {
  return selectedFile.value && 
         ['image/jpeg', 'image/png', 'image/jpg'].includes(selectedFile.value.type);
});

const isPdf = computed(() => {
  return selectedFile.value && selectedFile.value.type === 'application/pdf';
});

// Gestion du fichier sélectionné
const onFileSelected = (event) => {
  const file = event.target.files[0];
  if (file) {
    selectedFile.value = file;
    
    if (isImage.value) {
      filePreviewUrl.value = URL.createObjectURL(file);
    }
  }
};

const onFileDrop = (event) => {
  highlightDropArea.value = false;
  const file = event.dataTransfer.files[0];
  if (file && ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf'].includes(file.type)) {
    selectedFile.value = file;
    
    if (isImage.value) {
      filePreviewUrl.value = URL.createObjectURL(file);
    }
  }
};

const removeSelectedFile = () => {
  if (filePreviewUrl.value) {
    URL.revokeObjectURL(filePreviewUrl.value);
  }
  selectedFile.value = null;
  filePreviewUrl.value = '';
};

const cancelFileUpload = () => {
  removeSelectedFile();
  showFileUpload.value = false;
};

const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' bytes';
  else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
  else return (bytes / 1048576).toFixed(1) + ' MB';
};

// Fonction pour basculer la visibilité du sidebar sur mobile
const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value;
};

// Démarrer une nouvelle conversation
const startNewChat = () => {
  conversationStore.createConversation();
  
  // Fermer le sidebar sur mobile après avoir démarré un nouveau chat
  if (isMobile.value) {
    isSidebarOpen.value = false;
  }
  
  // Faire défiler vers le bas
  nextTick(() => {
    scrollToBottom();
  });
};

// Envoi de message (texte seulement)
const sendMessage = async (event) => {
  // Si la touche entrée est pressée avec shift, on ajoute un saut de ligne
  if (event && event.type === 'keyup' && event.shiftKey) {
    return;
  }
  
  if (!newMessage.value.trim() || isLoading.value) return;
  
  // Récupérer le texte du message
  const userMessageText = newMessage.value;
  
  // Réinitialiser l'input
  newMessage.value = '';
  if (messageInput.value) {
    messageInput.value.style.height = 'auto';
  }
  
  // Créer une conversation si nécessaire
  if (!conversationStore.currentConversationId) {
    conversationStore.createConversation();
  }
  
  // Ajouter le message utilisateur à la conversation
  const userMessage = {
    id: `user-${Date.now()}`,
    sender: 'user',
    text: userMessageText,
    timestamp: new Date().toISOString()
  };
  
  conversationStore.addMessage(userMessage);
  
  // Faire défiler vers le bas
  await scrollToBottom();
  
  // Afficher l'indicateur de chargement
  isLoading.value = true;
  
  try {
    // Appel à l'API
    const response = await chatApi.sendTextMessage(userMessageText);
    
    // Format d'exemple SDN pour démonstration du formatage
    let formattedResponse = response.reponse;
    
    // Détecter si la réponse contient du texte sur SDN et appliquer un formatage structuré
    if (formattedResponse.includes('SDN') && formattedResponse.includes('contrôleur')) {
      // C'est juste une démonstration - en production, l'API retournera directement la réponse formatée
      formattedResponse = formatSDNResponse(formattedResponse);
    }
    
    // Ajouter la réponse de l'assistant
    const assistantMessage = {
      id: `assistant-${Date.now()}`,
      sender: 'assistant',
      senderName: 'Assistant Halki',
      text: formattedResponse,
      timestamp: new Date().toISOString(),
      actions: [
        { type: 'extract', label: 'Texte réimprimable (à extraire)', icon: 'fas fa-copy' },
        { type: 'bookmark', label: 'Marquer ce dialogue', icon: 'fas fa-bookmark' }
      ],
      processingTime: response.processing_time
    };
    
    conversationStore.addMessage(assistantMessage);
    
  } catch (error) {
    // Gérer l'erreur
    const errorMessage = {
      id: `error-${Date.now()}`,
      sender: 'assistant',
      senderName: 'Assistant Halki',
      text: `Désolé, une erreur s'est produite: ${error.message}`,
      timestamp: new Date().toISOString(),
      isError: true
    };
    
    conversationStore.addMessage(errorMessage);
    console.error('Erreur lors de l\'envoi du message:', error);
  } finally {
    isLoading.value = false;
    // Faire défiler vers le bas après la réponse
    await scrollToBottom();
  }
};

// Fonction pour formater la réponse SDN (à des fins de démonstration seulement)
const formatSDNResponse = (text) => {
  if (!text.includes('SDN')) return text;
  
  // Extraction du titre principal
  let formattedText = "# Le contrôleur SDN (Software-Defined Networking)\n\n";
  
  // Ajout d'une description initiale
  formattedText += "Un composant central d'un réseau SDN, chargé de gérer et de contrôler le plan de contrôle du réseau. Il permet une **gestion centralisée** et **programmable** des ressources réseau.\n\n";
  
  // Création des sections principales
  formattedText += "## 1. Caractéristiques principales\n\n";
  formattedText += "Le contrôleur SDN agit comme un **point de décision central** pour l'ensemble du réseau. Il communique avec les **commutateurs virtuels** (ou physiques) via des protocoles comme OpenFlow, permettant de programmer le comportement des appareils réseau.\n\n";
  
  formattedText += "## 2. API Nord\n\n";
  formattedText += "Il expose une **API Nord** (vers les applications) pour permettre à des logiciels externes (ex: outils de gestion, applications métier) d'interagir avec le réseau. Cela permet la création, la surveillance et la modification des réseaux virtuels.\n\n";
  
  formattedText += "## 3. Virtualisation des réseaux\n\n";
  formattedText += "Dans un contexte de **NFV** (Network Function Virtualization), le contrôleur SDN orchestre la virtualisation des réseaux. Il connecte des **hyperviseurs** aux commutateurs virtuels, en programmant l'encapsulation des paquets pour les transmettre à travers le réseau sous-jacent.\n\n";
  
  formattedText += "## 4. Gestion des QoS/QoE\n\n";
  formattedText += "Le contrôleur intègre des **paramètres de QoS** pour garantir des performances adaptées aux besoins des utilisateurs. Par exemple, il peut prioriser le trafic vidéo ou les appels en temps réel, en fonction des exigences de latence ou de bande passante.\n\n";
  
  formattedText += "## 5. Adoption dans l'industrie\n\n";
  formattedText += "### 5.1 Fournisseurs de cloud\n\n";
  formattedText += "**Fournisseurs de cloud** (Google, Facebook, Microsoft) utilisent des contrôleurs SDN pour optimiser leurs infrastructures, bien que leurs solutions restent souvent propriétaires.\n\n";
  
  formattedText += "### 5.2 Opérateurs télécoms\n\n";
  formattedText += "**Opérateurs télécoms** (AT&T, NTT, Comcast) adoptent des approches hybrides, combinant SDN et des technologies traditionnelles.\n\n";
  
  formattedText += "### 5.3 Entreprises\n\n";
  formattedText += "**Entreprises** intègrent le SDN via des solutions comme le **SD-WAN** (Software-Defined Wide Area Network), pour simplifier la gestion des réseaux distants.\n\n";
  
  formattedText += "---\n\n";
  formattedText += "En résumé, le contrôleur SDN est le **cerveau du réseau** modernisé, permettant une flexibilité, une scalabilité et une optimisation des performances grâce à sa programmabilité et son intégration avec des technologies comme la virtualisation et les réseaux hybrides.";
  
  return formattedText;
};

// Envoi de message avec fichier
const sendWithFile = async () => {
  if (!newMessage.value.trim() || !selectedFile.value || isLoading.value) return;
  
  // Récupérer le texte du message
  const userMessageText = newMessage.value;
  
  // Réinitialiser l'input et cacher l'interface d'upload
  newMessage.value = '';
  showFileUpload.value = false;
  
  // Créer une conversation si nécessaire
  if (!conversationStore.currentConversationId) {
    conversationStore.createConversation();
  }
  
  // Ajouter le message utilisateur à la conversation
  const userMessage = {
    id: `user-${Date.now()}`,
    sender: 'user',
    text: `${userMessageText} [Fichier: ${selectedFile.value.name}]`,
    timestamp: new Date().toISOString()
  };
  
  conversationStore.addMessage(userMessage);
  
  // Faire défiler vers le bas
  await scrollToBottom();
  
  // Afficher l'indicateur de chargement
  isLoading.value = true;
  
  try {
    // Appel à l'API multimodale
    const response = await chatApi.sendMultimodalMessage(userMessageText, selectedFile.value);
    
    // Formater la réponse avec Markdown pour une meilleure structure
    const formattedResponse = "# Analyse du document\n\n" + response.reponse;
    
    // Ajouter la réponse de l'assistant
    const assistantMessage = {
      id: `assistant-${Date.now()}`,
      sender: 'assistant',
      senderName: 'Assistant Halki',
      text: formattedResponse,
      timestamp: new Date().toISOString(),
      actions: [
        { type: 'extract', label: 'Texte réimprimable (à extraire)', icon: 'fas fa-copy' },
        { type: 'bookmark', label: 'Marquer ce dialogue', icon: 'fas fa-bookmark' }
      ],
      processingTime: response.processing_time
    };
    
    conversationStore.addMessage(assistantMessage);
    
  } catch (error) {
    // Gérer l'erreur
    const errorMessage = {
      id: `error-${Date.now()}`,
      sender: 'assistant',
      senderName: 'Assistant Halki',
      text: `Désolé, une erreur s'est produite lors du traitement du fichier: ${error.message}`,
      timestamp: new Date().toISOString(),
      isError: true
    };
    
    conversationStore.addMessage(errorMessage);
    console.error('Erreur lors de l\'envoi du message avec fichier:', error);
  } finally {
    isLoading.value = false;
    // Nettoyer les ressources du fichier
    removeSelectedFile();
    // Faire défiler vers le bas après la réponse
    await scrollToBottom();
  }
};

// Gérer les clics sur les boutons d'action
const handleActionClick = (actionType, messageId) => {
  const conversation = conversationStore.currentConversation;
  if (!conversation) return;
  
  const message = conversation.messages.find(m => m.id === messageId);
  if (!message) return;
  
  switch (actionType) {
    case 'extract':
      // Copier le texte dans le presse-papier
      navigator.clipboard.writeText(message.text)
        .then(() => {
          alert('Texte copié dans le presse-papier!');
        })
        .catch(err => {
          console.error('Erreur lors de la copie: ', err);
        });
      break;
    case 'bookmark':
      // Logique pour marquer un message
      message.bookmarked = !message.bookmarked;
      conversationStore.saveToLocalStorage();
      alert(message.bookmarked ? 'Message marqué!' : 'Marque supprimée!');
      break;
    // Ajoutez d'autres cas selon les besoins
  }
};

// Fonction pour faire défiler vers le bas
const scrollToBottom = async () => {
  await nextTick();
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
  }
};

// Hook de cycle de vie
onMounted(() => {
  // Charger les conversations depuis le stockage local
  conversationStore.loadFromLocalStorage();
  
  // Créer une conversation si aucune n'existe
  if (conversationStore.conversations.length === 0) {
    conversationStore.createConversation();
  }
  
  // Vérifier si l'écran est mobile au chargement
  checkIfMobile();
  
  // Ajouter un écouteur pour détecter les changements de taille d'écran
  window.addEventListener('resize', checkIfMobile);
  
  // Faire défiler vers le bas au chargement initial
  nextTick(() => {
    scrollToBottom();
  });
});

// Nettoyage
watch(() => isMobile.value, (newValue) => {
  // Si on n'est plus sur mobile, fermer automatiquement le sidebar
  if (!newValue) {
    isSidebarOpen.value = false;
  }
});

// Observer les changements dans le texte pour auto-resize
watch(() => newMessage.value, () => {
  nextTick(() => {
    autoResizeTextarea();
  });
});
</script>

<style>
/* Base Styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

body {
  background-color: #f8f9fa;
}

.app-container {
  display: flex;
  height: 100vh;
  overflow: hidden;
  position: relative;
}

/* Sidebar Styles */
.sidebar {
  width: 250px;
  background-color: white;
  border-right: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  z-index: 100;
}

.sidebar-header {
  padding: 15px;
  display: flex;
  align-items: center;
  border-bottom: 1px solid #e0e0e0;
}

.logo-container {
  display: flex;
  align-items: center;
}

.logo {
  height: 24px;
  margin-right: 8px;
}

.logo-text {
  font-weight: bold;
  color: #4285f4;
}

.logo-divider {
  height: 20px;
  width: 1px;
  background-color: #e0e0e0;
  margin: 0 10px;
}

.assistant-name {
  font-weight: bold;
}

.new-document-btn {
  margin: 15px;
  padding: 8px 12px;
  background-color: #f1f3f4;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}

.new-document-btn:hover {
  background-color: #e8eaed;
}

.new-document-btn i {
  margin-right: 8px;
}

.sidebar-menu {
  padding: 10px 0;
}

.menu-item {
  padding: 10px 15px;
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.menu-item i {
  margin-right: 10px;
  width: 16px;
  text-align: center;
}

.menu-item.active {
  background-color: #e8f0fe;
  color: #1a73e8;
  font-weight: 500;
}

.menu-item:hover:not(.active) {
  background-color: #f1f3f4;
}

/* Mobile Menu Button */
.mobile-menu-btn {
  position: fixed;
  bottom: 20px;
  left: 20px;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background-color: #1a73e8;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
  z-index: 50;
  cursor: pointer;
  font-size: 18px;
}

.close-sidebar-btn {
  margin-left: auto;
  background: none;
  border: none;
  color: #5f6368;
  cursor: pointer;
  font-size: 16px;
}

/* Main Content Styles */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #f8f9fa;
}

.chat-header {
  padding: 15px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: white;
}

.chat-title {
  font-weight: bold;
  font-size: 16px;
  display: flex;
  align-items: center;
}

.model-badge {
  margin-left: 8px;
  padding: 2px 6px;
  background-color: #e8f0fe;
  color: #1a73e8;
  border-radius: 4px;
  font-size: 12px;
  font-weight: normal;
}

.user-info {
  display: flex;
  align-items: center;
}

.user-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  margin-left: 10px;
}

.chat-container {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Empty conversation */
.empty-conversation {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #5f6368;
  text-align: center;
  padding: 20px;
}

.empty-icon {
  font-size: 48px;
  color: #dadce0;
  margin-bottom: 16px;
}

.empty-conversation h3 {
  font-size: 18px;
  font-weight: 500;
  margin-bottom: 8px;
  color: #202124;
}

.empty-conversation p {
  font-size: 14px;
  max-width: 320px;
}

/* Typing Indicator */
.typing-indicator {
  display: flex;
  align-items: flex-start;
  margin-bottom: 20px;
  animation: fadeIn 0.3s ease-in;
}

.typing-dots {
  background-color: white;
  padding: 12px 16px;
  border-radius: 18px 18px 18px 4px;
  margin-left: 12px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
}

.typing-dots span {
  height: 8px;
  width: 8px;
  margin: 0 2px;
  background-color: #5f6368;
  border-radius: 50%;
  display: inline-block;
  opacity: 0.4;
}

.typing-dots span:nth-child(1) {
  animation: bounce 1s infinite 0.1s;
}

.typing-dots span:nth-child(2) {
  animation: bounce 1s infinite 0.2s;
}

.typing-dots span:nth-child(3) {
  animation: bounce 1s infinite 0.3s;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); opacity: 0.4; }
  50% { transform: translateY(-4px); opacity: 1; }
}

/* Chat Input Styles */
.chat-input-container {
  padding: 15px;
  background-color: white;
  border-top: 1px solid #e0e0e0;
}

.chat-input-wrapper {
  display: flex;
  align-items: center;
}

.attachment-btn, .format-btn {
  background: none;
  border: none;
  color: #5f6368;
  font-size: 18px;
  cursor: pointer;
  padding: 8px;
  margin-right: 8px;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.attachment-btn:hover, .format-btn:hover {
  background-color: #f1f3f4;
}

.chat-input {
  flex: 1;
  padding: 10px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 24px;
  outline: none;
  font-size: 14px;
  resize: none;
  overflow-y: auto;
  max-height: 150px;
  line-height: 1.4;
}

.send-btn {
  margin-left: 10px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #1a73e8;
  border: none;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.2s;
}

.send-btn:hover {
  background-color: #1967d2;
}

.send-btn:disabled {
  background-color: #c1d1f0;
  cursor: not-allowed;
}

.send-btn i {
  font-size: 16px;
}

/* Format Options */
.format-options {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  animation: slideUp 0.3s ease-out;
  margin-bottom: 15px;
}

.format-options-header {
  padding: 12px 16px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
}

.close-format-btn {
  background: none;
  border: none;
  color: #5f6368;
  cursor: pointer;
  font-size: 16px;
}

.format-buttons {
  display: flex;
  flex-wrap: wrap;
  padding: 12px;
  gap: 8px;
}

.format-buttons button {
  padding: 6px 10px;
  background-color: #f1f3f4;
  border: none;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
}

.format-buttons button:hover {
  background-color: #e8eaed;
}

.format-buttons button i {
  margin-right: 6px;
}

/* File Upload Styles */
.file-upload-container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  animation: slideUp 0.3s ease-out;
  margin-bottom: 15px;
}

.file-upload-header {
  padding: 12px 16px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
}

.close-upload-btn {
  background: none;
  border: none;
  color: #5f6368;
  cursor: pointer;
  font-size: 16px;
}

.file-upload-area {
  padding: 24px;
  text-align: center;
  border: 2px dashed #e0e0e0;
  margin: 16px;
  border-radius: 8px;
  transition: border-color 0.2s, background-color 0.2s;
}

.file-upload-area.highlight {
  border-color: #1a73e8;
  background-color: #f8fbff;
}

.file-upload-area i {
  font-size: 36px;
  color: #5f6368;
  margin-bottom: 12px;
}

.file-upload-area p {
  margin-bottom: 12px;
  color: #5f6368;
}

.file-upload-btn {
  display: inline-block;
  padding: 8px 16px;
  background-color: #1a73e8;
  color: white;
  border-radius: 4px;
  cursor: pointer;
  margin: 12px 0;
  transition: background-color 0.2s;
}

.file-upload-btn:hover {
  background-color: #1967d2;
}

.file-upload-btn input {
  display: none;
}

.file-upload-info {
  font-size: 12px;
  color: #5f6368;
}

.file-upload-actions {
  display: flex;
  justify-content: flex-end;
  padding: 12px 16px;
  border-top: 1px solid #e0e0e0;
}

.cancel-btn {
  padding: 8px 16px;
  background-color: #f1f3f4;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 8px;
  transition: background-color 0.2s;
}

.cancel-btn:hover {
  background-color: #e8eaed;
}

.upload-btn {
  padding: 8px 16px;
  background-color: #1a73e8;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.upload-btn:hover {
  background-color: #1967d2;
}

.upload-btn:disabled {
  background-color: #c1d1f0;
  cursor: not-allowed;
}

/* Selected File Display */
.selected-file {
  display: flex;
  align-items: center;
  padding: 8px;
  border-radius: 4px;
  background-color: #f8f9fa;
}

.file-preview {
  width: 80px;
  height: 80px;
  border-radius: 4px;
  overflow: hidden;
  margin-right: 12px;
  border: 1px solid #e0e0e0;
}

.file-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.file-preview.pdf {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f1f3f4;
}

.file-preview.pdf i {
  font-size: 36px;
  color: #ea4335;
}

.file-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.file-name {
  font-weight: 500;
  margin-bottom: 4px;
  word-break: break-all;
}

.file-size {
  font-size: 12px;
  color: #5f6368;
}

.remove-file-btn {
  background: none;
  border: none;
  color: #5f6368;
  cursor: pointer;
  font-size: 16px;
  padding: 8px;
}

.remove-file-btn:hover {
  color: #ea4335;
}

/* Animations */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.fade-in {
  animation: fadeIn 0.3s ease-in;
}

@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.slide-up {
  animation: slideUp 0.3s ease-out;
}

/* Styles adaptatifs pour mobile */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    height: 100%;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }
  
  .sidebar-open {
    transform: translateX(0);
  }
  
  .main-content {
    width: 100%;
  }
  
  .chat-container {
    padding: 12px;
  }
  
  .chat-input-container {
    padding: 10px;
  }
  
  .format-buttons {
    flex-wrap: wrap;
    padding: 8px;
    gap: 6px;
  }
  
  .format-buttons button {
    padding: 4px 8px;
    font-size: 12px;
  }
  
  .file-upload-area {
    padding: 16px;
    margin: 10px;
  }
  
  .file-preview {
    width: 60px;
    height: 60px;
  }
}
</style>
