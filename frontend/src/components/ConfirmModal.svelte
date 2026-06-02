<script>
  let {
    title = '¿Estás seguro?',
    message = '',
    confirmText = 'Confirmar',
    cancelText = 'Cancelar',
    danger = true,
    onConfirm,
    onCancel
  } = $props();

  let loading = $state(false);

  async function handleConfirm() {
    loading = true;
    try {
      await onConfirm?.();
    } finally {
      loading = false;
    }
  }

  function handleBackdrop(e) {
    if (e.target === e.currentTarget) onCancel?.();
  }

  function handleKeydown(e) {
    if (e.key === 'Escape') onCancel?.();
  }
</script>

<div class="modal-backdrop" onclick={handleBackdrop} onkeydown={handleKeydown} role="dialog" aria-modal="true" aria-label={title} tabindex="-1">
  <div class="modal">
    <div class="modal-header">
      <h2>{title}</h2>
    </div>
    <p style="color: var(--text-secondary); line-height: 1.5;">{message}</p>
    <div class="modal-actions">
      <button class="btn btn-ghost" onclick={onCancel} disabled={loading}>{cancelText}</button>
      <button
        class="btn {danger ? 'btn-danger' : 'btn-primary'}"
        onclick={handleConfirm}
        disabled={loading}
      >
        {#if loading}
          <span class="spinner-inline"></span>
        {:else}
          {confirmText}
        {/if}
      </button>
    </div>
  </div>
</div>

<style>
  .spinner-inline {
    display: inline-block;
    width: 16px;
    height: 16px;
    border: 2px solid rgba(255,255,255,0.3);
    border-top-color: white;
    border-radius: 50%;
    animation: spin 0.6s linear infinite;
  }
</style>
