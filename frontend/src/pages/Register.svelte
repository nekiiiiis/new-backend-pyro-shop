<script>
  import { auth } from '../stores/auth.svelte.js';
  import { navigate } from '../stores/router.svelte.js';
  import { toast } from '../stores/toast.svelte.js';
  import { register } from '../services/auth.js';
  import Spinner from '../components/Spinner.svelte';

  let username = $state('');
  let password = $state('');
  let confirmPassword = $state('');
  let loading = $state(false);
  let error = $state('');

  let passwordsMatch = $derived(password === confirmPassword);

  async function handleSubmit(e) {
    e.preventDefault();
    error = '';

    if (!username.trim() || !password || !confirmPassword) {
      error = 'Completa todos los campos';
      return;
    }
    if (username.trim().length < 3) {
      error = 'El nombre de usuario debe tener al menos 3 caracteres';
      return;
    }
    if (password.length < 6) {
      error = 'La contraseña debe tener al menos 6 caracteres';
      return;
    }
    if (!passwordsMatch) {
      error = 'Las contraseñas no coinciden';
      return;
    }

    loading = true;
    try {
      const data = await register(username.trim(), password);
      auth.login(data.token, data.user);
      toast.success('Cuenta creada correctamente');
      navigate('/products');
    } catch (err) {
      error = err.message;
    } finally {
      loading = false;
    }
  }
</script>

<div class="auth-page">
  <div class="auth-card">
    <h1>PyroShop</h1>
    <h2>Crear Cuenta</h2>

    <form onsubmit={handleSubmit}>
      {#if error}
        <div class="alert alert-error">{error}</div>
      {/if}

      <div class="form-group">
        <label for="reg-user">Usuario</label>
        <input
          id="reg-user"
          type="text"
          bind:value={username}
          placeholder="Mínimo 3 caracteres"
          autocomplete="username"
        />
      </div>

      <div class="form-group">
        <label for="reg-pass">Contraseña</label>
        <input
          id="reg-pass"
          type="password"
          bind:value={password}
          placeholder="Mínimo 6 caracteres"
          autocomplete="new-password"
        />
      </div>

      <div class="form-group">
        <label for="reg-pass2">Confirmar Contraseña</label>
        <input
          id="reg-pass2"
          type="password"
          bind:value={confirmPassword}
          placeholder="Repite la contraseña"
          autocomplete="new-password"
        />
        {#if confirmPassword && !passwordsMatch}
          <span class="field-err">Las contraseñas no coinciden</span>
        {/if}
      </div>

      <button type="submit" class="btn btn-primary btn-block" disabled={loading}>
        {#if loading}<Spinner small />{:else}Crear Cuenta{/if}
      </button>
    </form>

    <p class="auth-link">
      ¿Ya tienes cuenta? <a href="#/login">Inicia sesión</a>
    </p>
  </div>
</div>

<style>
  .field-err {
    color: var(--danger);
    font-size: 0.8rem;
    margin-top: 0.25rem;
    display: block;
  }
</style>
