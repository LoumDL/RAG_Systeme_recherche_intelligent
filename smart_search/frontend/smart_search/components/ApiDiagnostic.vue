<!-- components/ApiDiagnostic.vue -->
<template>
  <div class="diagnostic-container" v-if="showDiagnostic">
    <div class="diagnostic-panel">
      <div class="diagnostic-header">
        <h3>🔧 Diagnostic API</h3>
        <button class="close-btn" @click="showDiagnostic = false">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <div class="diagnostic-content">
        <div class="status-overview">
          <div class="status-item" :class="{ 'success': overallStatus === 'success', 'error': overallStatus === 'error', 'warning': overallStatus === 'warning' }">
            <i class="fas" :class="statusIcon"></i>
            <span>{{ statusMessage }}</span>
          </div>
        </div>

        <div class="test-section">
          <button 
            class="test-btn" 
            @click="runDiagnostic" 
            :disabled="isRunning"
            :class="{ 'running': isRunning }"
          >
            <i class="fas" :class="isRunning ? 'fa-spinner fa-spin' : 'fa-play'"></i>
            {{ isRunning ? 'Test en cours...' : 'Lancer le diagnostic' }}
          </button>
        </div>

        <div class="results-section" v-if="testResults.length > 0">
          <h4>Résultats des tests</h4>
          <div class="test-results">
            <div 
              v-for="result in testResults" 
              :key="result.name"
              class="test-result"
              :class="{ 'success': result.success, 'error': !result.success }"
            >
              <div class="result-header">
                <i class="fas" :class="result.success ? 'fa-check-circle' : 'fa-times-circle'"></i>
                <span class="test-name">{{ result.name }}</span>
                <span class="test-duration">{{ result.duration }}ms</span>
              </div>
              <div class="result-details" v-if="result.error">
                <small>{{ result.error }}</small>
              </div>
              <div class="result-details" v-if="result.details">
                <small>{{ formatDetails(result.details) }}</small>
              </div>
            </div>
          </div>
        </div>

        <div class="info-section">
          <h4>Informations de configuration</h4>
          <div class="config-info">
            <div class="config-item">
              <strong>Environment:</strong> {{ environment }}
            </div>
            <div class="config-item">
              <strong>API Base URL:</strong> {{ apiBaseUrl }}
            </div>
            <div class="config-item">
              <strong>User Agent:</strong> {{ navigator.userAgent.substring(0, 50) }}...
            </div>
            <div class="config-item">
              <strong>Timestamp:</strong> {{ new Date().toISOString() }}
            </div>
          </div>
        </div>

        <div class="actions-section">
          <button class="action-btn" @click="copyReport">
            <i class="fas fa-copy"></i>
            Copier le rapport
          </button>
          <button class="action-btn" @click="downloadReport">
            <i class="fas fa-download"></i>
            Télécharger
          </button>
        </div>
      </div>
    </div>

    <!-- Backdrop -->
    <div class="diagnostic-backdrop" @click="showDiagnostic = false"></div>
  </div>

  <!-- Bouton de déclenchement -->
  <button 
    class="diagnostic-trigger" 
    @click="showDiagnostic = true"
    title="Diagnostic API"
    v-if="!showDiagnostic"
  >
    <i class="fas fa-cogs"></i>
  </button>
</template>

<script setup>
import { ref, computed } from 'vue';
import chatApi from '~/api/chat';

// Props (optionnel)
const props = defineProps({
  autoRun: {
    type: Boolean,
    default: false
  }
});

// État réactif
const showDiagnostic = ref(false);
const isRunning = ref(false);
const testResults = ref([]);
const environment = ref('Unknown');
const apiBaseUrl = ref('/api/smartsearch');

// Méthodes
const runTest = async (name, testFn) => {
  const startTime = Date.now();
  
  try {
    const result = await testFn();
    const duration = Date.now() - startTime;
    
    return {
      name,
      success: true,
      duration,
      details: result
    };
  } catch (error) {
    const duration = Date.now() - startTime;
    
    return {
      name,
      success: false,
      duration,
      error: error.message
    };
  }
};

const runDiagnostic = async () => {
  isRunning.value = true;
  testResults.value = [];
  
  try {
    // Test 1: Connectivité de base
    const connectivityTest = await runTest('Connectivité', async () => {
      const response = await chatApi.testConnection();
      return { connected: response };
    });
    testResults.value.push(connectivityTest);

    // Test 2: Endpoint text
    const textTest = await runTest('Endpoint Text', async () => {
      const response = await chatApi.sendTextMessage('Test diagnostic');
      return {
        hasResponse: !!response.reponse,
        processingTime: response.processing_time
      };
    });
    testResults.value.push(textTest);

    // Test 3: Endpoint multimodal (avec fichier test)
    const multimodalTest = await runTest('Endpoint Multimodal', async () => {
      const testFile = new File(['Test content'], 'test.txt', { type: 'text/plain' });
      const response = await chatApi.sendMultimodalMessage('Analyse ce fichier test', testFile);
      return {
        hasResponse: !!response.reponse,
        processingTime: response.processing_time
      };
    });
    testResults.value.push(multimodalTest);

    // Test 4: Performance
    const performanceTest = await runTest('Performance', async () => {
      const start = performance.now();
      await chatApi.sendTextMessage('Test performance');
      const end = performance.now();
      const totalTime = end - start;
      
      return {
        responseTime: Math.round(totalTime),
        acceptable: totalTime < 10000 // Moins de 10s
      };
    });
    testResults.value.push(performanceTest);

  } catch (error) {
    console.error('Erreur durante el diagnostic:', error);
  } finally {
    isRunning.value = false;
  }
};

// Configuration avec gestion d'erreur
const initializeConfig = () => {
  try {
    const config = useRuntimeConfig();
    environment.value = config.public.environment || 'development';
    apiBaseUrl.value = config.public.apiBaseUrl || '/api/smartsearch';
  } catch (error) {
    console.warn('Configuration par défaut utilisée');
    environment.value = 'development';
    apiBaseUrl.value = '/api/smartsearch';
  }
};

// Initialiser la configuration
initializeConfig();

const formatDetails = (details) => {
  if (typeof details === 'object') {
    return Object.entries(details)
      .map(([key, value]) => `${key}: ${value}`)
      .join(', ');
  }
  return String(details);
};

const generateReport = () => {
  let report = `# Rapport de diagnostic API\n\n`;
  report += `**Date**: ${new Date().toISOString()}\n`;
  report += `**Environment**: ${environment.value}\n`;
  report += `**API URL**: ${apiBaseUrl.value}\n`;
  report += `**Statut général**: ${overallStatus.value}\n\n`;

  report += `## Résultats des tests\n\n`;
  
  testResults.value.forEach(result => {
    report += `### ${result.name}\n`;
    report += `- **Statut**: ${result.success ? '✅ Succès' : '❌ Échec'}\n`;
    report += `- **Durée**: ${result.duration}ms\n`;
    
    if (result.error) {
      report += `- **Erreur**: ${result.error}\n`;
    }
    
    if (result.details) {
      report += `- **Détails**: ${formatDetails(result.details)}\n`;
    }
    
    report += '\n';
  });

  return report;
};

const copyReport = async () => {
  try {
    const report = generateReport();
    await navigator.clipboard.writeText(report);
    alert('Rapport copié dans le presse-papier !');
  } catch (error) {
    console.error('Erreur lors de la copie:', error);
    alert('Erreur lors de la copie');
  }
};

const downloadReport = () => {
  const report = generateReport();
  const blob = new Blob([report], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  
  const a = document.createElement('a');
  a.href = url;
  a.download = `diagnostic-api-${new Date().toISOString().split('T')[0]}.md`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};

// Auto-run si demandé
if (props.autoRun) {
  runDiagnostic();
}
</script>

<style scoped>
.diagnostic-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.diagnostic-backdrop {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
}

.diagnostic-panel {
  position: relative;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  z-index: 1001;
}

.diagnostic-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.diagnostic-header h3 {
  margin: 0;
  color: #1a73e8;
}

.close-btn {
  background: none;
  border: none;
  color: #5f6368;
  cursor: pointer;
  font-size: 18px;
  padding: 8px;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.close-btn:hover {
  background-color: #f1f3f4;
}

.diagnostic-content {
  padding: 20px;
}

.status-overview {
  margin-bottom: 20px;
}

.status-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-radius: 8px;
  font-weight: 500;
}

.status-item.success {
  background-color: #e8f5e8;
  color: #1b5e20;
}

.status-item.error {
  background-color: #fdeded;
  color: #d32f2f;
}

.status-item.warning {
  background-color: #fff3e0;
  color: #f57c00;
}

.status-item i {
  margin-right: 8px;
}

.test-section {
  margin-bottom: 20px;
}

.test-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px 24px;
  background-color: #1a73e8;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
  width: 100%;
}

.test-btn:hover:not(:disabled) {
  background-color: #1967d2;
}

.test-btn:disabled {
  background-color: #c1d1f0;
  cursor: not-allowed;
}

.test-btn.running {
  background-color: #1967d2;
}

.test-btn i {
  margin-right: 8px;
}

.results-section {
  margin-bottom: 20px;
}

.results-section h4 {
  margin-bottom: 12px;
  color: #202124;
}

.test-results {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.test-result {
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #e0e0e0;
}

.test-result.success {
  background-color: #f8fff8;
  border-color: #4caf50;
}

.test-result.error {
  background-color: #fff8f8;
  border-color: #f44336;
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.test-name {
  flex: 1;
  margin-left: 8px;
  font-weight: 500;
}

.test-duration {
  font-size: 12px;
  color: #5f6368;
}

.result-details {
  margin-top: 8px;
  color: #5f6368;
  font-size: 12px;
}

.info-section, .config-info {
  margin-bottom: 20px;
}

.config-info {
  background-color: #f8f9fa;
  padding: 12px;
  border-radius: 6px;
  font-size: 12px;
}

.config-item {
  margin-bottom: 4px;
}

.config-item:last-child {
  margin-bottom: 0;
}

.actions-section {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.action-btn {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  background-color: #f1f3f4;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.action-btn:hover {
  background-color: #e8eaed;
}

.action-btn i {
  margin-right: 6px;
}

.diagnostic-trigger {
  position: fixed;
  bottom: 80px;
  right: 20px;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background-color: #f57c00;
  color: white;
  border: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  cursor: pointer;
  font-size: 18px;
  transition: background-color 0.2s, transform 0.2s;
  z-index: 100;
}

.diagnostic-trigger:hover {
  background-color: #ef6c00;
  transform: scale(1.1);
}

@media (max-width: 768px) {
  .diagnostic-panel {
    width: 95%;
    max-height: 90vh;
  }
  
  .diagnostic-content {
    padding: 16px;
  }
  
  .actions-section {
    flex-direction: column;
  }
  
  .diagnostic-trigger {
    bottom: 90px;
    right: 15px;
    width: 45px;
    height: 45px;
    font-size: 16px;
  }
}
</style>