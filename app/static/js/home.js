import { AlertSystem } from './home/alerts.js';
import { VideoUpload } from './home/upload.js';
import { VideoList } from './home/video-list.js';
import { TaskMonitor } from './home/tasks.js';

class HomeApp {
  constructor() {
    // Inicializa os módulos principais
    this.alertSystem = new AlertSystem();
    this.videoList = new VideoList('videos-container', this.alertSystem);
    this.taskMonitor = new TaskMonitor(this.alertSystem);
    this.videoUpload = new VideoUpload('upload-form', this.alertSystem);

    // Controle de estado
    this.refreshInterval = null;
    this.isInitialized = false;

    // Configura os listeners
    this.initEventListeners();
  }

  init() {
    if (this.isInitialized) return;

    try {
      // Inicializa os componentes
      this.videoUpload.init();
      this.loadInitialData();
      this.setupAutoRefresh();

      this.isInitialized = true;
      console.log('Aplicação inicializada com sucesso');
    } catch (error) {
      console.error('Falha na inicialização:', error);
      this.alertSystem.show('Erro ao iniciar a aplicação', 'danger');
    }
  }

  initEventListeners() {
    // Evento para atualização da lista de vídeos
    document.addEventListener('refreshVideos', () => {
      this.refreshVideoList();
    });

    // Evento para limpeza ao sair da página
    window.addEventListener('beforeunload', () => {
      this.cleanup();
    });

    // Listener alternativo para o seletor de tipo de upload
    document.addEventListener('change', (e) => {
      if (e.target.id === 'upload_type') {
        this.videoUpload.toggleUploadType(e.target.value);
      }
    });
  }

  async loadInitialData() {
    try {
      await this.videoList.loadVideos();

      // Verifica se há tarefas pendentes
      const pendingTask = localStorage.getItem('currentUploadTask');
      if (pendingTask) {
        this.taskMonitor.monitorTaskStatus(pendingTask);
      }
    } catch (error) {
      console.error('Erro ao carregar dados iniciais:', error);
      this.alertSystem.show('Erro ao carregar vídeos', 'danger');
    }
  }

  refreshVideoList() {
    this.videoList.loadVideos()
      .catch(error => {
        console.error('Erro ao atualizar lista:', error);
        this.alertSystem.show('Falha ao atualizar lista de vídeos', 'warning');
      });
  }

  setupAutoRefresh() {
    // Configura intervalo de atualização (30 segundos)
    this.refreshInterval = setInterval(() => {
      this.refreshVideoList();
    }, 30000);
  }

  cleanup() {
    // Limpa todos os recursos
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
      this.refreshInterval = null;
    }

    // Limpa listeners adicionais se necessário
    document.removeEventListener('refreshVideos', this.refreshVideoList);
    window.removeEventListener('beforeunload', this.cleanup);
  }
}

// Inicialização segura da aplicação
document.addEventListener('DOMContentLoaded', () => {
  try {
    const app = new HomeApp();
    app.init();

    // Exibe mensagem de carregamento para o usuário
    const loadingAlert = new AlertSystem();
    loadingAlert.show('Aplicação carregada com sucesso', 'success', 3000);
  } catch (error) {
    console.error('Falha crítica na inicialização:', error);
    const errorAlert = new AlertSystem();
    errorAlert.show('Erro crítico ao carregar a aplicação', 'danger');
  }
});