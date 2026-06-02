<script>
  let { user, currentUserId, onChangeRole, onDelete } = $props();

  let isSelf = $derived(user._id === currentUserId);
  let changingRole = $state(false);

  async function toggleRole() {
    changingRole = true;
    try {
      const newRole = user.role === 'admin' ? 'user' : 'admin';
      await onChangeRole(user._id, newRole);
    } finally {
      changingRole = false;
    }
  }
</script>

<tr>
  <td>
    <div class="user-cell">
      <span class="avatar">{user.username.charAt(0).toUpperCase()}</span>
      <span>{user.username}</span>
    </div>
  </td>
  <td>
    <span class="badge {user.role === 'admin' ? 'badge-warning' : 'badge-info'}">
      {user.role}
    </span>
  </td>
  <td>{new Date(user.createdAt).toLocaleDateString('es-ES')}</td>
  <td>
    {#if !isSelf}
      <div class="row-actions">
        <button class="btn btn-ghost btn-sm" onclick={toggleRole} disabled={changingRole}>
          {changingRole ? '...' : user.role === 'admin' ? 'Quitar admin' : 'Hacer admin'}
        </button>
        <button class="btn btn-danger btn-sm" onclick={() => onDelete(user)}>Eliminar</button>
      </div>
    {:else}
      <span class="text-muted">Tú</span>
    {/if}
  </td>
</tr>

<style>
  .user-cell {
    display: flex;
    align-items: center;
    gap: 0.6rem;
  }
  .avatar {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background: var(--accent-glow);
    color: var(--accent);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.8rem;
    font-weight: 700;
    flex-shrink: 0;
  }
  .row-actions {
    display: flex;
    gap: 0.5rem;
  }
  .text-muted {
    color: var(--text-muted);
    font-size: 0.85rem;
  }
</style>
