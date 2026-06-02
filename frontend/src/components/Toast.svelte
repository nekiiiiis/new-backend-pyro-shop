<script>
  import { toast } from '../stores/toast.svelte.js';
</script>

{#if toast.list.length > 0}
  <div class="toast-container">
    {#each toast.list as t (t.id)}
      <div class="toast toast-{t.type}">
        <span class="toast-icon">
          {#if t.type === 'success'}✓
          {:else if t.type === 'error'}✕
          {:else if t.type === 'warning'}!
          {:else}ℹ{/if}
        </span>
        <span class="toast-msg">{t.message}</span>
        <button class="toast-close" onclick={() => toast.remove(t.id)}>×</button>
      </div>
    {/each}
  </div>
{/if}

<style>
  .toast-container {
    position: fixed;
    top: 80px;
    right: 1rem;
    z-index: 200;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    max-width: 380px;
  }
  .toast {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.75rem 1rem;
    border-radius: var(--radius-sm);
    font-size: 0.9rem;
    animation: slideUp 0.2s ease;
    box-shadow: var(--shadow);
    border: 1px solid var(--border);
    background: var(--bg-secondary);
  }
  .toast-success { border-left: 3px solid var(--success); }
  .toast-error   { border-left: 3px solid var(--danger); }
  .toast-warning { border-left: 3px solid var(--warning); }
  .toast-info    { border-left: 3px solid var(--info); }

  .toast-icon {
    font-weight: 700;
    width: 22px;
    height: 22px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    flex-shrink: 0;
  }
  .toast-success .toast-icon { background: rgba(34,197,94,0.2); color: var(--success); }
  .toast-error .toast-icon   { background: rgba(239,68,68,0.2); color: var(--danger); }
  .toast-warning .toast-icon { background: rgba(245,158,11,0.2); color: var(--warning); }
  .toast-info .toast-icon    { background: rgba(59,130,246,0.2); color: var(--info); }

  .toast-msg { flex: 1; }
  .toast-close {
    background: none;
    border: none;
    color: var(--text-muted);
    cursor: pointer;
    font-size: 1.2rem;
    padding: 0 0.25rem;
    line-height: 1;
  }
  .toast-close:hover { color: var(--text-primary); }
</style>
