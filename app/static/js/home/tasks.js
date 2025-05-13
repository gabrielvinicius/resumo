import { AlertSystem } from './alerts.js';

export class TaskMonitor {
  constructor(alertSystem) {
    this.alertSystem = alertSystem || new AlertSystem();
  }

  async checkStatus(taskId) {
    try {
      const response = await fetch(`/task/status/${taskId}`);
      if (!response.ok) throw new Error('Erro na requisição');

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Erro ao verificar status:', error);
      throw error;
    }
  }
}