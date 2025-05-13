import { AlertSystem } from './alerts.js';

export class VideoUpload {
  constructor(formId = 'upload-form', alertSystem) {
    this.form = document.getElementById(formId);
    this.alertSystem = alertSystem || new AlertSystem();
    this.uploadState = {
      taskId: localStorage.getItem('currentUploadTask') || null,
      isProcessing: false
    };

    // Elementos do DOM
    this.uploadTypeSelect = document.getElementById('upload_type');
    this.fileUploadSection = document.querySelector('.upload-file');
    this.youtubeUploadSection = document.querySelector('.upload-youtube');
    this.fileInput = document.getElementById('file');
    this.youtubeInput = document.getElementById('youtube_link');

    // Elementos de UI
    this.submitBtn = this.form?.querySelector('button[type="submit"]');
    this.progressBar = document.getElementById('upload-progress');
  }

  init() {
    if (!this.form) {
      console.error('Formulário de upload não encontrado');
      return;
    }

    this.setupEventListeners();

    if (this.uploadState.taskId) {
      this.monitorPendingTask();
    }
  }

  setupEventListeners() {
    // Controle de tipo de upload
    if (this.uploadTypeSelect) {
      this.uploadTypeSelect.addEventListener('change', (e) => {
        this.toggleUploadType(e.target.value);
      });
      // Inicializa o estado
      this.toggleUploadType(this.uploadTypeSelect.value);
    }

    // Submissão do formulário
    this.form.addEventListener('submit', (e) => this.handleSubmit(e));
  }

  toggleUploadType(uploadType) {
    const isYoutube = uploadType === 'youtube';

    try {
      // Mostra/oculta seções
      if (this.fileUploadSection) {
        this.fileUploadSection.style.display = isYoutube ? 'none' : 'block';
      }
      if (this.youtubeUploadSection) {
        this.youtubeUploadSection.style.display = isYoutube ? 'block' : 'none';
      }

      // Atualiza campos obrigatórios
      if (this.fileInput) this.fileInput.required = !isYoutube;
      if (this.youtubeInput) this.youtubeInput.required = isYoutube;

      // Atualiza texto do botão
      if (this.submitBtn) {
        this.submitBtn.querySelector('span').textContent =
          isYoutube ? 'Processar Link' : 'Enviar Vídeo';
      }
    } catch (error) {
      console.error('Erro ao alternar tipo de upload:', error);
      this.alertSystem.show('Erro na configuração do formulário', 'danger');
    }
  }
/*
  async handleSubmit(e) {
    e.preventDefault();

    if (!this.validateForm()) return;

    this.setLoadingState(true);

    try {
      const formData = new FormData(this.form);
      const isYoutube = this.uploadTypeSelect.value === 'youtube';

      const response = await fetch(
        isYoutube ? '/video/process_link' : '/video/upload',
        {
          method: 'POST',
          body: formData
        }
      );

      if (!response.ok) throw new Error(await response.text());

      const result = await response.json();
      this.handleUploadSuccess(result);
    } catch (error) {
      this.handleUploadError(error);
    } finally {
      this.setLoadingState(false);
    }

  }
  */

  validateForm() {
    const isYoutube = this.uploadTypeSelect.value === 'youtube';
    const title = document.getElementById('title')?.value.trim();

    if (!title || title.length < 3) {
      this.alertSystem.show('O título deve ter pelo menos 3 caracteres', 'warning');
      return false;
    }

    if (isYoutube) {
      const youtubeLink = this.youtubeInput?.value.trim();
      if (!this.validateYoutubeUrl(youtubeLink)) {
        this.alertSystem.show('Por favor, insira um link válido do YouTube', 'warning');
        return false;
      }
    } else {
      if (!this.fileInput?.files[0]) {
        this.alertSystem.show('Por favor, selecione um arquivo de vídeo', 'warning');
        return false;
      }
      if (!this.validateFile(this.fileInput.files[0])) {
        this.alertSystem.show('Arquivo inválido (Formatos: MP4, AVI, MKV, MOV, até 500MB)', 'warning');
        return false;
      }
    }

    return true;
  }

  validateYoutubeUrl(url) {
    if (!url) return false;
    const pattern = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$/;
    return pattern.test(url);
  }

  validateFile(file) {
    const validTypes = ['video/mp4', 'video/avi', 'video/x-matroska', 'video/quicktime'];
    const maxSize = 500 * 1024 * 1024; // 500MB
    return file && validTypes.includes(file.type) && file.size <= maxSize;
  }

  setLoadingState(isLoading) {
    this.uploadState.isProcessing = isLoading;
    if (this.submitBtn) {
      this.submitBtn.disabled = isLoading;
      const icon = this.submitBtn.querySelector('i');
      if (icon) {
        icon.className = isLoading ? 'fas fa-spinner fa-spin' : 'fas fa-upload';
      }
    }
    if (this.progressBar) {
      this.progressBar.style.display = isLoading ? 'block' : 'none';
      this.progressBar.style.width = isLoading ? '0%' : '100%';
    }
  }

  handleUploadSuccess(result) {
    this.uploadState.taskId = result.task_id;
    localStorage.setItem('currentUploadTask', result.task_id);

    this.alertSystem.show(
      this.uploadTypeSelect.value === 'youtube'
        ? 'Link do YouTube recebido. Processando vídeo...'
        : 'Vídeo enviado com sucesso! Processando...',
      'info'
    );

    this.form.reset();
    this.monitorTaskStatus(result.task_id);
  }

  handleUploadError(error) {
    console.error('Upload error:', error);
    this.alertSystem.show(
      `Erro no envio: ${error.message || 'Erro desconhecido'}`,
      'danger'
    );
  }

  monitorPendingTask() {
    this.alertSystem.show('Continuando processamento pendente...', 'info');
    this.monitorTaskStatus(this.uploadState.taskId);
  }

  async monitorTaskStatus(taskId) {
    try {
      const response = await fetch(`/task/status/${taskId}`);
      if (!response.ok) throw new Error('Falha ao verificar status');

      const data = await response.json();

      if (data.status === 'SUCCESS') {
        this.handleTaskSuccess(data);
      } else if (data.status === 'FAILURE') {
        this.handleTaskFailure(data.error);
      } else if (data.status === 'PENDING') {
        setTimeout(() => this.monitorTaskStatus(taskId), 3000);
      }
    } catch (error) {
      console.error('Status check error:', error);
      setTimeout(() => this.monitorTaskStatus(taskId), 3000);
    }
  }

  handleTaskSuccess(data) {
    localStorage.removeItem('currentUploadTask');
    this.uploadState.taskId = null;

    this.alertSystem.show('Processamento concluído com sucesso!', 'success');
    document.dispatchEvent(new CustomEvent('refreshVideos'));
  }

  handleTaskFailure(error) {
    localStorage.removeItem('currentUploadTask');
    this.uploadState.taskId = null;

    this.alertSystem.show(
      `Falha no processamento: ${error || 'Erro desconhecido'}`,
      'danger'
    );
  }
}