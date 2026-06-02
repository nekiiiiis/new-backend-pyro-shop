<script>
  import { auth } from '../stores/auth.svelte.js';
  import { router, navigate } from '../stores/router.svelte.js';
  import { cartStore } from '../stores/cart.svelte.js';

  let mobileOpen = $state(false);

  let currentSection = $derived(router.segment || 'products');

  function nav(path) {
    navigate(path);
    mobileOpen = false;
  }

  function handleLogout() {
    auth.logout();
    cartStore.clear();
    navigate('/login');
    mobileOpen = false;
  }
</script>

<nav class="navbar">
  <div class="nav-inner">
    <button class="nav-brand" onclick={() => nav('/products')}>
      <span class="brand-icon">🎆</span>
      <span class="brand-text">PyroShop</span>
    </button>

    <button class="hamburger" onclick={() => mobileOpen = !mobileOpen} aria-label="Menú">
      <span class="bar" class:open={mobileOpen}></span>
      <span class="bar" class:open={mobileOpen}></span>
      <span class="bar" class:open={mobileOpen}></span>
    </button>

    <div class="nav-links" class:open={mobileOpen}>
      <button
        class="nav-link" class:active={currentSection === 'products' || currentSection === ''}
        onclick={() => nav('/products')}
      >Productos</button>

      <button class="nav-link" class:active={currentSection === 'cart'} onclick={() => nav('/cart')}>
        Carrito
        {#if cartStore.count > 0}
          <span class="cart-badge">{cartStore.count}</span>
        {/if}
      </button>

      <button class="nav-link" class:active={currentSection === 'orders'} onclick={() => nav('/orders')}>
        Pedidos
      </button>

      {#if auth.isAdmin}
        <button class="nav-link" class:active={currentSection === 'admin'} onclick={() => nav('/admin')}>
          Panel Admin
        </button>
      {/if}

      <div class="nav-spacer"></div>

      <button class="nav-link" class:active={currentSection === 'profile'} onclick={() => nav('/profile')}>
        <span class="user-avatar">{auth.username.charAt(0).toUpperCase()}</span>
        <span class="username-text">{auth.username}</span>
        {#if auth.isAdmin}<span class="admin-tag">Admin</span>{/if}
      </button>

      <button class="nav-link logout-btn" onclick={handleLogout}>Salir</button>
    </div>
  </div>
</nav>

<style>
  .navbar {
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border);
    position: sticky;
    top: 0;
    z-index: 50;
    height: var(--nav-height);
  }
  .nav-inner {
    max-width: var(--max-width);
    margin: 0 auto;
    display: flex;
    align-items: center;
    height: 100%;
    padding: 0 1.5rem;
    gap: 0.5rem;
  }
  .nav-brand {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: none;
    border: none;
    cursor: pointer;
    color: var(--text-primary);
    font-size: 1.2rem;
    font-weight: 700;
    margin-right: 1.5rem;
    flex-shrink: 0;
  }
  .brand-icon { font-size: 1.4rem; }
  .brand-text {
    background: linear-gradient(135deg, var(--accent), #ff4757);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .nav-links {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    flex: 1;
  }
  .nav-link {
    background: none;
    border: none;
    color: var(--text-secondary);
    font-size: 0.9rem;
    font-weight: 500;
    padding: 0.5rem 0.85rem;
    border-radius: var(--radius-sm);
    cursor: pointer;
    transition: all var(--transition);
    display: flex;
    align-items: center;
    gap: 0.4rem;
    white-space: nowrap;
    font-family: var(--font);
  }
  .nav-link:hover { color: var(--text-primary); background: var(--bg-hover); }
  .nav-link.active { color: var(--accent); background: var(--accent-glow); }
  .nav-spacer { flex: 1; }
  .cart-badge {
    background: var(--accent);
    color: white;
    font-size: 0.7rem;
    font-weight: 700;
    padding: 0.1rem 0.45rem;
    border-radius: 999px;
    min-width: 18px;
    text-align: center;
    line-height: 1.3;
  }
  .user-avatar {
    width: 26px;
    height: 26px;
    border-radius: 50%;
    background: var(--accent-glow);
    color: var(--accent);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    font-weight: 700;
    flex-shrink: 0;
  }
  .admin-tag {
    font-size: 0.65rem;
    background: rgba(245,158,11,0.2);
    color: var(--warning);
    padding: 0.1rem 0.4rem;
    border-radius: 4px;
    font-weight: 600;
  }
  .logout-btn { color: var(--danger) !important; }
  .logout-btn:hover { background: rgba(239,68,68,0.1) !important; }

  .hamburger {
    display: none;
    flex-direction: column;
    gap: 5px;
    background: none;
    border: none;
    cursor: pointer;
    padding: 0.5rem;
    margin-left: auto;
  }
  .bar {
    display: block;
    width: 22px;
    height: 2px;
    background: var(--text-secondary);
    border-radius: 2px;
    transition: all 0.25s ease;
  }
  .bar.open:nth-child(1) { transform: translateY(7px) rotate(45deg); }
  .bar.open:nth-child(2) { opacity: 0; }
  .bar.open:nth-child(3) { transform: translateY(-7px) rotate(-45deg); }

  .username-text { display: inline; }

  @media (max-width: 768px) {
    .hamburger { display: flex; }
    .nav-links {
      display: none;
      position: absolute;
      top: var(--nav-height);
      left: 0;
      right: 0;
      background: var(--bg-secondary);
      border-bottom: 1px solid var(--border);
      flex-direction: column;
      padding: 0.75rem;
      gap: 0.25rem;
      box-shadow: var(--shadow);
    }
    .nav-links.open { display: flex; }
    .nav-spacer { display: none; }
    .nav-link { width: 100%; justify-content: flex-start; }
  }
</style>
