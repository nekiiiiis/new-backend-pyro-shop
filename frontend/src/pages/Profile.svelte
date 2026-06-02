<script>
  import { auth } from '../stores/auth.svelte.js';
  import { toast } from '../stores/toast.svelte.js';
  import { changePassword } from '../services/auth.js';
  import Spinner from '../components/Spinner.svelte';

  let currentPassword = $state('');
  let newPassword = $state('');
  let confirmNew = $state('');
  let loading = $state(false);
  let error = $state('');
  let success = $state('');

  let passwordsMatch = $derived(newPassword === confirmNew);

  async function handleChangePassword(e) {
    e.preventDefault();
    error = '';
    success = '';

    if (!currentPassword || !newPassword || !confirmNew) {
      error = 'Completa todos los campos';
      return;
    }
    if (newPassword.length < 6) {
      error = 'La nueva contraseña debe tener al menos 6 caracteres';
      return;
    }
    if (!passwordsMatch) {
      error = 'Las contraseñas nuevas no coinciden';
      return;
    }

    loading = true;
    try {
      await changePassword(currentPassword, newPassword);
      success = 'Contraseña actualizada correctamente';
      toast.success('Contraseña actualizada');
      currentPassword = '';
      newPassword = '';
      confirmNew = '';
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }
</script>

<div class="page">
  <h1>Mi Perfil</h1>

  <div class="profile-grid">
    <div class="card profile-info">
      <h3>Información</h3>
      <div class="info-row">
        <span class="info-label">Usuario</span>
        <span class="info-value">{auth.username}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Rol</span>
        <span class="badge {auth.isAdmin ? 'badge-warning' : 'badge-info'}">
          {auth.isAdmin ? 'Administrador' : 'Usuario'}
        </span>
      </div>
      <div class="info-row">
        <span class="info-label">ID</span>
        <span class="info-value mono">{auth.userId}</span>
      </div>
    </div>

    <div class="card">
      <h3>Cambiar Contraseña</h3>

      <form onsubmit={handleChangePassword} style="margin-top:1rem">
        {#if error}
          <div class="alert alert-error">{error}</div>
        {/if}
        {#if success}
          <div class="alert alert-success">{success}</div>
        {/if}

        <div class="form-group">
          <label for="cp-current">Contraseña actual</label>
          <input id="cp-current" type="password" bind:value={currentPassword} autocomplete="current-password" />
        </div>
        <div class="form-group">
          <label for="cp-new">Nueva contraseña</label>
          <input id="cp-new" type="password" bind:value={newPassword} placeholder="Mínimo 6 caracteres" autocomplete="new-password" />
        </div>
        <div class="form-group">
          <label for="cp-confirm">Confirmar nueva contraseña</label>
          <input id="cp-confirm" type="password" bind:value={confirmNew} autocomplete="new-password" />
          {#if confirmNew && !passwordsMatch}
            <span class="field-err">Las contraseñas no coinciden</span>
          {/if}
        </div>

        <button type="submit" class="btn btn-primary" disabled={loading}>
          {#if loading}<Spinner small />{:else}Actualizar Contraseña{/if}
        </button>
      </form>
    </div>
  </div>
</div>

<style>
  .profile-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
    margin-top: 1.5rem;
  }
  .profile-info h3,
  .card h3 {
    margin-bottom: 1rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid var(--border);
  }
  .info-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.6rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
  }
  .info-row:last-child { border-bottom: none; }
  .info-label {
    font-size: 0.85rem;
    color: var(--text-secondary);
  }
  .info-value {
    font-weight: 600;
  }
  .mono {
    font-family: monospace;
    font-size: 0.8rem;
    color: var(--text-muted);
  }
  .field-err {
    color: var(--danger);
    font-size: 0.8rem;
    margin-top: 0.25rem;
    display: block;
  }
  @media (max-width: 768px) {
    .profile-grid { grid-template-columns: 1fr; }
  }
</style>
