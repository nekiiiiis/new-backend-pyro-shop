function createToastStore() {
  let toasts = $state([]);
  let nextId = 0;

  return {
    get list() { return toasts; },

    add(message, type = 'info', duration = 3500) {
      const id = nextId++;
      toasts.push({ id, message, type });
      setTimeout(() => {
        const idx = toasts.findIndex(t => t.id === id);
        if (idx !== -1) toasts.splice(idx, 1);
      }, duration);
    },

    success(msg) { this.add(msg, 'success'); },
    error(msg) { this.add(msg, 'error', 5000); },
    info(msg) { this.add(msg, 'info'); },
    warning(msg) { this.add(msg, 'warning', 4000); },

    remove(id) {
      const idx = toasts.findIndex(t => t.id === id);
      if (idx !== -1) toasts.splice(idx, 1);
    }
  };
}

export const toast = createToastStore();
