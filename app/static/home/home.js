import { AlertSystem } from './home/alerts.js';
import { VideoUpload } from './home/upload.js';
import { VideoList } from './home/video-list.js';
import { TaskMonitor } from './home/tasks.js';

class HomeApp {
  constructor() {
    this.alertSystem = new AlertSystem();
    this.videoList = new VideoList('videos-container', this.alertSystem);
    this.taskMonitor = new TaskMonitor(this.alertSystem);
    this.videoUpload = new VideoUpload('upload-form', this.alertSystem);

    this.refreshInterval = null;
    this.initEventListeners();
  }

  init() {
    this.videoUpload.init();
    this.loadInitialData();
    this.setupAutoRefresh();
  }

  initEventListeners() {
    // Evento personalizado para atualização da lista de vídeos
    document.addEventListener('refreshVideos', () => {
      this.videoList.loadVideos();
    });

    // Evento para limpar recursos ao sair da página
    window.addEventListener('beforeunload', () => {
      this.cleanup();
    });
  }

  loadInitialData() {
    this.videoList.loadVideos()
      .catch(error => {
        console.error('Failed to load initial videos:', error);
        this.alertSystem.show('Erro ao carregar vídeos iniciais', 'danger');
      });
  }

  setupAutoRefresh() {
    // Configura intervalo de atualização (30 segundos)
    this.refreshInterval = setInterval(() => {
      this.videoList.loadVideos();
    }, 30000);
  }

  cleanup() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
      this.refreshInterval = null;
    }
  }
}

// Inicializa a aplicação quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
  const app = new HomeApp();
  app.init();
});