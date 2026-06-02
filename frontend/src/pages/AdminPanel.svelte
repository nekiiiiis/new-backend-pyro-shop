<script>
  import { auth } from '../stores/auth.svelte.js';
  import { toast } from '../stores/toast.svelte.js';
  import * as usersAPI from '../services/users.js';
  import * as ordersAPI from '../services/orders.js';
  import * as productsAPI from '../services/products.js';
  import UserRow from '../components/UserRow.svelte';
  import ConfirmModal from '../components/ConfirmModal.svelte';
  import Spinner from '../components/Spinner.svelte';

  let activeTab = $state('dashboard');
  let loadingData = $state(true);

  let users = $state([]);
  let orders = $state([]);
  let products = $state([]);

  let deleteUserTarget = $state(null);
  let cancelOrderTarget = $state(null);
  let userSearch = $state('');
  let orderStatusFilter = $state('');

  // ── Derived: Metrics ──
  let totalRevenue = $derived(
    orders.filter(o => o.status === 'completed').reduce((sum, o) => sum + o.total, 0)
  );
  let pendingRevenue = $derived(
    orders.filter(o => o.status === 'pending').reduce((sum, o) => sum + o.total, 0)
  );
  let pendingCount = $derived(orders.filter(o => o.status === 'pending').length);
  let completedCount = $derived(orders.filter(o => o.status === 'completed').length);
  let adminCount = $derived(users.filter(u => u.role === 'admin').length);
  let userCount = $derived(users.filter(u => u.role === 'user').length);

  let categoryStats = $derived.by(() => {
    const map = {};
    for (const p of products) {
      const cat = p.categoria || 'otros';
      map[cat] = (map[cat] || 0) + 1;
    }
    return Object.entries(map)
      .map(([cat, count]) => ({ cat, count }))
      .sort((a, b) => b.count - a.count);
  });

  let recentOrders = $derived(
    [...orders].sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt)).slice(0, 8)
  );

  let avgOrderValue = $derived(
    orders.length > 0 ? orders.reduce((s, o) => s + o.total, 0) / orders.length : 0
  );

  // ── Derived: Filtered lists ──
  let filteredUsers = $derived(
    userSearch
      ? users.filter(u => u.username.toLowerCase().includes(userSearch.toLowerCase()))
      : users
  );

  let filteredOrders = $derived(
    orderStatusFilter ? orders.filter(o => o.status === orderStatusFilter) : orders
  );

  // ── Load all data ──
  $effect(() => { loadAll(); });

  async function loadAll() {
    loadingData = true;
    try {
      const [u, o, p] = await Promise.all([
        usersAPI.getUsers(),
        ordersAPI.getAllOrders(),
        productsAPI.getProducts()
      ]);
      users = u;
      orders = o;
      products = p;
    } catch (err) {
      toast.error('Error cargando datos: ' + err.message);
    } finally {
      loadingData = false;
    }
  }

  // ── User actions ──
  async function handleChangeRole(id, role) {
    try {
      await usersAPI.updateUserRole(id, role);
      toast.success('Rol actualizado');
      users = await usersAPI.getUsers();
    } catch (err) { toast.error(err.message); }
  }

  async function handleDeleteUser() {
    if (!deleteUserTarget) return;
    try {
      await usersAPI.deleteUser(deleteUserTarget._id);
      toast.success('Usuario eliminado');
      deleteUserTarget = null;
      users = await usersAPI.getUsers();
    } catch (err) { toast.error(err.message); }
  }

  // ── Order actions ──
  async function handleCompleteOrder(order) {
    try {
      await ordersAPI.updateOrderStatus(order._id, 'completed');
      toast.success('Pedido completado');
      orders = await ordersAPI.getAllOrders();
    } catch (err) { toast.error(err.message); }
  }

  async function handleCancelOrder() {
    if (!cancelOrderTarget) return;
    try {
      await ordersAPI.cancelOrder(cancelOrderTarget._id);
      toast.success('Pedido cancelado');
      cancelOrderTarget = null;
      orders = await ordersAPI.getAllOrders();
    } catch (err) { toast.error(err.message); }
  }

  // ── Helpers ──
  const catLabels = {
    'fuegos-artificiales': 'Fuegos Artificiales',
    'petardos': 'Petardos',
    'bengalas': 'Bengalas',
    'cohetes': 'Cohetes',
    'otros': 'Otros'
  };

  function statusLabel(s) {
    return s === 'pending' ? 'Pendiente' : s === 'completed' ? 'Completado' : s;
  }
  function statusClass(s) {
    return s === 'completed' ? 'badge-success' : 'badge-warning';
  }
  function fmtDate(d) {
    return new Date(d).toLocaleDateString('es-ES', {
      day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'
    });
  }
</script>

<div class="page admin-page">
  <div class="page-header">
    <h1>Panel de Administración</h1>
  </div>

  {#if loadingData}
    <div class="empty-state"><Spinner /></div>
  {:else}

    <!-- ═══ Metric Cards ═══ -->
    <div class="metrics-grid">
      <div class="metric-card">
        <div class="metric-icon revenue-icon">€</div>
        <div class="metric-body">
          <span class="metric-value">{totalRevenue.toFixed(2)} €</span>
          <span class="metric-label">Ingresos Completados</span>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-icon orders-icon">📦</div>
        <div class="metric-body">
          <span class="metric-value">{orders.length}</span>
          <span class="metric-label">Pedidos Totales</span>
          <span class="metric-sub">{pendingCount} pendientes · {completedCount} completados</span>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-icon users-icon">👥</div>
        <div class="metric-body">
          <span class="metric-value">{users.length}</span>
          <span class="metric-label">Usuarios</span>
          <span class="metric-sub">{adminCount} admins · {userCount} usuarios</span>
        </div>
      </div>
      <div class="metric-card">
        <div class="metric-icon products-icon">🎆</div>
        <div class="metric-body">
          <span class="metric-value">{products.length}</span>
          <span class="metric-label">Productos</span>
          <span class="metric-sub">{categoryStats.length} categorías</span>
        </div>
      </div>
    </div>

    <!-- ═══ Tabs ═══ -->
    <div class="tabs">
      <button class="tab" class:active={activeTab === 'dashboard'} onclick={() => activeTab = 'dashboard'}>
        Resumen
      </button>
      <button class="tab" class:active={activeTab === 'orders'} onclick={() => activeTab = 'orders'}>
        Pedidos
        {#if pendingCount > 0}
          <span class="tab-badge">{pendingCount}</span>
        {/if}
      </button>
      <button class="tab" class:active={activeTab === 'users'} onclick={() => activeTab = 'users'}>
        Usuarios
      </button>
    </div>

    <!-- ═══ Tab: Dashboard ═══ -->
    {#if activeTab === 'dashboard'}
      <div class="dashboard-grid">
        <div class="dash-section">
          <h3>Pedidos Recientes</h3>
          {#if recentOrders.length === 0}
            <p class="dash-empty">No hay pedidos aún</p>
          {:else}
            <div class="recent-orders">
              {#each recentOrders as order (order._id)}
                <div class="recent-order-row">
                  <div class="ro-left">
                    <span class="ro-id">#{order._id.slice(-6).toUpperCase()}</span>
                    <span class="ro-user">{order.username || '—'}</span>
                  </div>
                  <div class="ro-right">
                    <span class="badge {statusClass(order.status)}">{statusLabel(order.status)}</span>
                    <span class="ro-total">{order.total.toFixed(2)} €</span>
                  </div>
                </div>
              {/each}
            </div>
          {/if}
        </div>

        <div class="dash-section">
          <h3>Estadísticas</h3>
          <div class="stat-rows">
            <div class="stat-row">
              <span>Valor medio por pedido</span>
              <span class="stat-val">{avgOrderValue.toFixed(2)} €</span>
            </div>
            <div class="stat-row">
              <span>Ingresos pendientes</span>
              <span class="stat-val pending-val">{pendingRevenue.toFixed(2)} €</span>
            </div>
            <div class="stat-row">
              <span>Tasa de completados</span>
              <span class="stat-val">{orders.length > 0 ? ((completedCount / orders.length) * 100).toFixed(0) : 0}%</span>
            </div>
          </div>

          <h3 style="margin-top:1.5rem">Productos por Categoría</h3>
          <div class="cat-bars">
            {#each categoryStats as { cat, count }}
              {@const pct = products.length > 0 ? (count / products.length) * 100 : 0}
              <div class="cat-bar-row">
                <span class="cat-bar-label">{catLabels[cat] || cat}</span>
                <div class="cat-bar-track">
                  <div class="cat-bar-fill" style="width:{pct}%"></div>
                </div>
                <span class="cat-bar-count">{count}</span>
              </div>
            {/each}
          </div>
        </div>
      </div>

    <!-- ═══ Tab: Orders ═══ -->
    {:else if activeTab === 'orders'}
      <div class="tab-header">
        <select bind:value={orderStatusFilter}>
          <option value="">Todos los estados</option>
          <option value="pending">Pendiente</option>
          <option value="completed">Completado</option>
        </select>
        <span class="badge badge-accent">{filteredOrders.length} pedido{filteredOrders.length !== 1 ? 's' : ''}</span>
      </div>

      {#if filteredOrders.length === 0}
        <div class="empty-state"><p>No hay pedidos con este filtro</p></div>
      {:else}
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Cliente</th>
                <th>Artículos</th>
                <th>Total</th>
                <th>Estado</th>
                <th>Fecha</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {#each filteredOrders as order (order._id)}
                <tr>
                  <td><span class="mono">#{order._id.slice(-6).toUpperCase()}</span></td>
                  <td>{order.username || '—'}</td>
                  <td>
                    <div class="order-items-cell">
                      {#each order.items.slice(0, 2) as item}
                        <span class="item-line">{item.nombre} ×{item.cantidad}</span>
                      {/each}
                      {#if order.items.length > 2}
                        <span class="item-more">+{order.items.length - 2} más</span>
                      {/if}
                    </div>
                  </td>
                  <td><span class="cell-total">{order.total.toFixed(2)} €</span></td>
                  <td><span class="badge {statusClass(order.status)}">{statusLabel(order.status)}</span></td>
                  <td class="cell-date">{fmtDate(order.createdAt)}</td>
                  <td>
                    <div class="row-actions">
                      {#if order.status === 'pending'}
                        <button class="btn btn-success btn-sm" onclick={() => handleCompleteOrder(order)}>Completar</button>
                        <button class="btn btn-danger btn-sm" onclick={() => cancelOrderTarget = order}>Cancelar</button>
                      {:else}
                        <span class="text-muted">—</span>
                      {/if}
                    </div>
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      {/if}

    <!-- ═══ Tab: Users ═══ -->
    {:else if activeTab === 'users'}
      <div class="tab-header">
        <input type="search" placeholder="Buscar usuario..." bind:value={userSearch} />
        <span class="badge badge-warning">{adminCount} admins</span>
        <span class="badge badge-info">{userCount} usuarios</span>
      </div>

      {#if filteredUsers.length === 0}
        <div class="empty-state"><p>No se encontraron usuarios</p></div>
      {:else}
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Usuario</th>
                <th>Rol</th>
                <th>Registro</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {#each filteredUsers as user (user._id)}
                <UserRow
                  {user}
                  currentUserId={auth.userId}
                  onChangeRole={handleChangeRole}
                  onDelete={(u) => deleteUserTarget = u}
                />
              {/each}
            </tbody>
          </table>
        </div>
      {/if}
    {/if}
  {/if}
</div>

<!-- Modals -->
{#if deleteUserTarget}
  <ConfirmModal
    title="Eliminar usuario"
    message={'¿Eliminar al usuario "' + deleteUserTarget.username + '"? Se borrará su cuenta y carrito.'}
    confirmText="Eliminar"
    onConfirm={handleDeleteUser}
    onCancel={() => deleteUserTarget = null}
  />
{/if}

{#if cancelOrderTarget}
  <ConfirmModal
    title="Cancelar pedido"
    message={'¿Cancelar el pedido #' + cancelOrderTarget._id.slice(-6).toUpperCase() + '?'}
    confirmText="Cancelar pedido"
    onConfirm={handleCancelOrder}
    onCancel={() => cancelOrderTarget = null}
  />
{/if}

<style>
  .admin-page { max-width: 1280px; }

  /* ── Metrics ── */
  .metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
  }
  .metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    transition: border-color var(--transition), transform var(--transition);
  }
  .metric-card:hover {
    border-color: rgba(255, 107, 53, 0.3);
    transform: translateY(-2px);
  }
  .metric-icon {
    width: 48px;
    height: 48px;
    border-radius: var(--radius);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.3rem;
    flex-shrink: 0;
  }
  .revenue-icon  { background: rgba(34, 197, 94, 0.15); color: var(--success); font-weight: 800; font-size: 1.4rem; }
  .orders-icon   { background: rgba(255, 107, 53, 0.15); }
  .users-icon    { background: rgba(59, 130, 246, 0.15); }
  .products-icon { background: rgba(245, 158, 11, 0.15); }
  .metric-body {
    display: flex;
    flex-direction: column;
    min-width: 0;
  }
  .metric-value {
    font-size: 1.5rem;
    font-weight: 700;
    line-height: 1.2;
  }
  .metric-label {
    font-size: 0.8rem;
    color: var(--text-secondary);
    margin-top: 0.1rem;
  }
  .metric-sub {
    font-size: 0.7rem;
    color: var(--text-muted);
    margin-top: 0.15rem;
  }

  /* ── Tabs ── */
  .tabs {
    display: flex;
    gap: 0.25rem;
    border-bottom: 2px solid var(--border);
    margin-bottom: 1.5rem;
  }
  .tab {
    background: none;
    border: none;
    color: var(--text-secondary);
    font-size: 0.95rem;
    font-weight: 600;
    padding: 0.75rem 1.25rem;
    cursor: pointer;
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
    transition: all var(--transition);
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-family: var(--font);
  }
  .tab:hover { color: var(--text-primary); }
  .tab.active {
    color: var(--accent);
    border-bottom-color: var(--accent);
  }
  .tab-badge {
    background: var(--accent);
    color: white;
    font-size: 0.65rem;
    font-weight: 700;
    padding: 0.1rem 0.4rem;
    border-radius: 999px;
    min-width: 18px;
    text-align: center;
    line-height: 1.3;
  }

  /* ── Tab header (filters) ── */
  .tab-header {
    display: flex;
    gap: 0.75rem;
    align-items: center;
    margin-bottom: 1rem;
    flex-wrap: wrap;
  }
  .tab-header input,
  .tab-header select {
    max-width: 300px;
  }

  /* ── Dashboard ── */
  .dashboard-grid {
    display: grid;
    grid-template-columns: 1.2fr 1fr;
    gap: 1.5rem;
  }
  .dash-section {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem;
  }
  .dash-section h3 {
    font-size: 0.95rem;
    margin-bottom: 1rem;
    color: var(--text-secondary);
  }
  .dash-empty {
    color: var(--text-muted);
    font-size: 0.9rem;
    padding: 1rem 0;
  }

  /* Recent orders */
  .recent-orders {
    display: flex;
    flex-direction: column;
  }
  .recent-order-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.6rem 0;
    border-bottom: 1px solid var(--border);
  }
  .recent-order-row:last-child { border-bottom: none; }
  .ro-left { display: flex; align-items: center; gap: 0.75rem; }
  .ro-id { font-weight: 700; font-size: 0.85rem; font-family: monospace; }
  .ro-user { color: var(--text-secondary); font-size: 0.85rem; }
  .ro-right { display: flex; align-items: center; gap: 0.75rem; }
  .ro-total { font-weight: 600; font-size: 0.9rem; }

  /* Stat rows */
  .stat-rows { display: flex; flex-direction: column; }
  .stat-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.55rem 0;
    border-bottom: 1px solid var(--border);
    font-size: 0.9rem;
    color: var(--text-secondary);
  }
  .stat-row:last-child { border-bottom: none; }
  .stat-val { font-weight: 700; color: var(--text-primary); }
  .pending-val { color: var(--warning); }

  /* Category bars */
  .cat-bars { display: flex; flex-direction: column; gap: 0.6rem; margin-top: 0.5rem; }
  .cat-bar-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 0.85rem;
  }
  .cat-bar-label {
    min-width: 130px;
    color: var(--text-secondary);
    white-space: nowrap;
  }
  .cat-bar-track {
    flex: 1;
    height: 8px;
    background: var(--bg-hover);
    border-radius: 4px;
    overflow: hidden;
  }
  .cat-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--accent), #ff4757);
    border-radius: 4px;
    transition: width 0.5s ease;
    min-width: 4px;
  }
  .cat-bar-count {
    min-width: 20px;
    text-align: right;
    font-weight: 600;
    font-size: 0.8rem;
    color: var(--text-muted);
  }

  /* ── Orders table cells ── */
  .mono { font-family: monospace; font-weight: 600; font-size: 0.85rem; }
  .order-items-cell { display: flex; flex-direction: column; gap: 0.15rem; }
  .item-line { font-size: 0.8rem; color: var(--text-secondary); }
  .item-more { font-size: 0.75rem; color: var(--text-muted); font-style: italic; }
  .cell-total { font-weight: 700; color: var(--accent); }
  .cell-date { font-size: 0.8rem; color: var(--text-muted); white-space: nowrap; }
  .row-actions { display: flex; gap: 0.5rem; }
  .text-muted { color: var(--text-muted); font-size: 0.85rem; }

  @media (max-width: 900px) {
    .dashboard-grid { grid-template-columns: 1fr; }
  }
  @media (max-width: 768px) {
    .metrics-grid { grid-template-columns: 1fr 1fr; }
    .tabs { overflow-x: auto; }
  }
  @media (max-width: 480px) {
    .metrics-grid { grid-template-columns: 1fr; }
  }
</style>
