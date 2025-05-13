export class AlertSystem {
  constructor(containerId = 'alerts-container') {
    this.container = document.getElementById(containerId);
    if (!this.container) {
      console.error('Container de alertas não encontrado');
    }
  }

  show(message, type = 'info', timeout = 5000) {
    if (!this.container) return;

    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
      ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    this.container.prepend(alertDiv);

    setTimeout(() => {
      alertDiv.classList.remove('show');
      setTimeout(() => alertDiv.remove(), 150);
    }, timeout);
  }
}