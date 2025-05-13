import { AlertSystem } from './alerts.js';

export class VideoList {
  constructor(containerId, alertSystem) {
    this.container = document.getElementById(containerId);
    this.alertSystem = alertSystem || new AlertSystem();
  }

  async loadVideos() {
    try {
      const response = await fetch('/videos/list');
      const html = await response.text();
      this.container.innerHTML = html;
    } catch (error) {
      console.error('Erro ao carregar vídeos:', error);
      this.alertSystem.show('Erro ao atualizar lista de vídeos', 'danger');
    }
  }

  highlightVideo(taskId) {
    if (!taskId) return;
    const videoElement = this.container.querySelector(`[data-task-id="${taskId}"]`);
    if (videoElement) {
      videoElement.classList.add('highlight');
      setTimeout(() => videoElement.classList.remove('highlight'), 5000);
    }
  }
}