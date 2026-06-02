<script>
  import { auth } from './stores/auth.svelte.js';
  import { router, navigate } from './stores/router.svelte.js';
  import { toast } from './stores/toast.svelte.js';
  import { cartStore } from './stores/cart.svelte.js';
  import * as cartAPI from './services/cart.js';

  import Navbar from './components/Navbar.svelte';
  import Toast from './components/Toast.svelte';

  import Login from './pages/Login.svelte';
  import Register from './pages/Register.svelte';
  import Products from './pages/Products.svelte';
  import Profile from './pages/Profile.svelte';
  import Cart from './pages/Cart.svelte';
  import Orders from './pages/Orders.svelte';
  import AdminPanel from './pages/AdminPanel.svelte';

  let page = $derived.by(() => {
    const p = router.path;
    if (p === '/login') return 'login';
    if (p === '/register') return 'register';
    if (p === '/profile') return 'profile';
    if (p === '/cart') return 'cart';
    if (p === '/orders') return 'orders';
    if (p.startsWith('/admin')) return 'admin';
    return 'products';
  });

  let showNav = $derived(page !== 'login' && page !== 'register');

  // Redirect unauthenticated users away from private pages
  $effect(() => {
    if (!auth.isAuthenticated && page !== 'login' && page !== 'register') {
      navigate('/login');
    }
  });

  // Redirect non-admin users away from admin pages
  $effect(() => {
    if (auth.isAuthenticated && page === 'admin' && !auth.isAdmin) {
      navigate('/products');
      toast.error('Acceso solo para administradores');
    }
  });

  // Redirect authenticated users away from login/register
  $effect(() => {
    if (auth.isAuthenticated && (page === 'login' || page === 'register')) {
      navigate('/products');
    }
  });

  // Load cart when user authenticates
  $effect(() => {
    if (auth.isAuthenticated) {
      cartAPI.getCart()
        .then(cart => cartStore.set(cart))
        .catch(() => {});
    } else {
      cartStore.clear();
    }
  });
</script>

{#if showNav && auth.isAuthenticated}
  <Navbar />
{/if}

<main>
  {#if page === 'login'}
    <Login />
  {:else if page === 'register'}
    <Register />
  {:else if auth.isAuthenticated}
    {#if page === 'products'}
      <Products />
    {:else if page === 'profile'}
      <Profile />
    {:else if page === 'cart'}
      <Cart />
    {:else if page === 'orders'}
      <Orders />
    {:else if page === 'admin'}
      <AdminPanel />
    {/if}
  {/if}
</main>

<Toast />

<style>
  main {
    flex: 1;
    display: flex;
    flex-direction: column;
  }
</style>
