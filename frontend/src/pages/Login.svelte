<script>
  import { auth } from '../stores/auth.svelte.js';
  import { navigate } from '../stores/router.svelte.js';
  import { toast } from '../stores/toast.svelte.js';
  import { login } from '../services/auth.js';
  import Spinner from '../components/Spinner.svelte';

  let username = $state('');
  let password = $state('');
  let loading = $state(false);
  let error = $state('');

  async function handleSubmit(e) {
    e.preventDefault();
    error = '';
    if (!username.trim() || !password) {
      error = 'Completa todos los campos';
      return;
    }
    loading = true;
    try {
      const data = await login(username.trim(), password);
      auth.login(data.token, data.user);
      toast.success(`Bienvenido, ${data.user.username}`);
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
    <h2>Iniciar Sesión</h2>

    <form onsubmit={handleSubmit}>
      {#if error}
        <div class="alert alert-error">{error}</div>
      {/if}

      <div class="form-group">
        <label for="login-user">Usuario</label>
        <input
          id="login-user"
          type="text"
          bind:value={username}
          placeholder="Tu nombre de usuario"
          autocomplete="username"
        />
      </div>

      <div class="form-group">
        <label for="login-pass">Contraseña</label>
        <input
          id="login-pass"
          type="password"
          bind:value={password}
          placeholder="Tu contraseña"
          autocomplete="current-password"
        />
      </div>

      <button type="submit" class="btn btn-primary btn-block" disabled={loading}>
        {#if loading}<Spinner small />{:else}Entrar{/if}
      </button>
    </form>

    <p class="auth-link">
      ¿No tienes cuenta? <a href="#/register">Regístrate</a>
    </p>
  </div>
</div>
