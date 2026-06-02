<script>
  import { toast } from '../stores/toast.svelte.js';
  import * as ordersAPI from '../services/orders.js';
  import ConfirmModal from '../components/ConfirmModal.svelte';
  import Spinner from '../components/Spinner.svelte';

  let orders = $state([]);
  let loading = $state(true);
  let cancelTarget = $state(null);
  let statusFilter = $state('');

  let filteredOrders = $derived(
    statusFilter ? orders.filter(o => o.status === statusFilter) : orders
  );

  $effect(() => {
    loadOrders();
  });

  async function loadOrders() {
    loading = true;
    try {
      orders = await ordersAPI.getMyOrders();
    } catch (err) {
      toast.error('Error cargando pedidos: ' + err.message);
    } finally {
      loading = false;
    }
  }

  async function handleCancel() {
    if (!cancelTarget) return;
    try {
      await ordersAPI.cancelOrder(cancelTarget._id);
      toast.success('Pedido cancelado');
      cancelTarget = null;
      await loadOrders();
    } catch (err) {
      toast.error(err.message);
    }
  }

  function statusLabel(s) {
    return s === 'pending' ? 'Pendiente' : s === 'completed' ? 'Completado' : s;
  }

  function statusClass(s) {
    return s === 'completed' ? 'badge-success' : 'badge-warning';
  }
</script>

<div class="page">
  <div class="page-header">
    <h1>Mis Pedidos</h1>
    <span class="badge badge-accent">{filteredOrders.length}</span>
  </div>

  <div class="filters">
    <select bind:value={statusFilter}>
      <option value="">Todos los estados</option>
      <option value="pending">Pendiente</option>
      <option value="completed">Completado</option>
    </select>
  </div>

  {#if loading}
    <div class="empty-state"><Spinner /></div>
  {:else if filteredOrders.length === 0}
    <div class="empty-state">
      <p style="font-size:3rem">📦</p>
      <p>No hay pedidos</p>
    </div>
  {:else}
    <div class="orders-list">
      {#each filteredOrders as order (order._id)}
        <div class="order-card card">
          <div class="order-header">
            <span class="order-id">#{order._id.slice(-6).toUpperCase()}</span>
            <span class="badge {statusClass(order.status)}">
              {statusLabel(order.status)}
            </span>
          </div>

          <div class="order-items">
            {#each order.items as item}
              <div class="order-item">
                <span>{item.nombre} × {item.cantidad}</span>
                <span>{item.subtotal?.toFixed(2) || (item.precio * item.cantidad).toFixed(2)} €</span>
              </div>
            {/each}
          </div>

          <div class="order-footer">
            <span class="order-date">{new Date(order.createdAt).toLocaleDateString('es-ES', { day:'numeric', month:'short', year:'numeric', hour:'2-digit', minute:'2-digit' })}</span>
            <div class="order-right">
              <span class="order-total">{order.total.toFixed(2)} €</span>
              {#if order.status !== 'completed'}
                <button class="btn btn-danger btn-sm" onclick={() => cancelTarget = order}>
                  Cancelar
                </button>
              {/if}
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>

{#if cancelTarget}
  <ConfirmModal
    title="Cancelar pedido"
    message="¿Estás seguro de que quieres cancelar este pedido?"
    confirmText="Cancelar pedido"
    onConfirm={handleCancel}
    onCancel={() => cancelTarget = null}
  />
{/if}

<style>
  .orders-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  .order-card { padding: 0; overflow: hidden; }
  .order-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.25rem;
    border-bottom: 1px solid var(--border);
  }
  .order-id { font-weight: 700; font-size: 0.95rem; }
  .order-items { padding: 0.75rem 1.25rem; }
  .order-item {
    display: flex;
    justify-content: space-between;
    padding: 0.3rem 0;
    font-size: 0.9rem;
    color: var(--text-secondary);
  }
  .order-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 1.25rem;
    border-top: 1px solid var(--border);
    background: rgba(0,0,0,0.15);
    flex-wrap: wrap;
    gap: 0.75rem;
  }
  .order-date { font-size: 0.8rem; color: var(--text-muted); }
  .order-right { display: flex; align-items: center; gap: 1rem; }
  .order-total { font-size: 1.15rem; font-weight: 700; color: var(--accent); }
</style>
