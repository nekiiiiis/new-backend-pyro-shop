<script>
  import { cartStore } from '../stores/cart.svelte.js';
  import { toast } from '../stores/toast.svelte.js';
  import { navigate } from '../stores/router.svelte.js';
  import * as cartAPI from '../services/cart.js';
  import * as ordersAPI from '../services/orders.js';
  import CartItem from '../components/CartItem.svelte';
  import ConfirmModal from '../components/ConfirmModal.svelte';
  import Spinner from '../components/Spinner.svelte';

  let loading = $state(true);
  let ordering = $state(false);
  let showClearConfirm = $state(false);

  let isEmpty = $derived(cartStore.items.length === 0);

  $effect(() => {
    loadCart();
  });

  async function loadCart() {
    loading = true;
    try {
      const cart = await cartAPI.getCart();
      cartStore.set(cart);
    } catch (err) {
      toast.error('Error cargando el carrito: ' + err.message);
    } finally {
      loading = false;
    }
  }

  async function handleUpdateQty(productId, cantidad) {
    try {
      const result = await cartAPI.updateCartItem(productId, cantidad);
      cartStore.set(result.cart);
    } catch (err) {
      toast.error(err.message);
    }
  }

  async function handleRemove(productId) {
    try {
      const result = await cartAPI.removeFromCart(productId);
      cartStore.set(result.cart);
      toast.info('Producto eliminado del carrito');
    } catch (err) {
      toast.error(err.message);
    }
  }

  async function handleClear() {
    try {
      const result = await cartAPI.clearCart();
      cartStore.set(result.cart);
      showClearConfirm = false;
      toast.info('Carrito vaciado');
    } catch (err) {
      toast.error(err.message);
    }
  }

  async function handleCheckout() {
    ordering = true;
    try {
      await ordersAPI.createOrder();
      cartStore.clear();
      toast.success('Pedido creado correctamente');
      navigate('/orders');
    } catch (err) {
      toast.error(err.message);
    } finally {
      ordering = false;
    }
  }
</script>

<div class="page">
  <div class="page-header">
    <h1>Carrito</h1>
    {#if !isEmpty && !loading}
      <span class="badge badge-accent">{cartStore.count} artículo{cartStore.count !== 1 ? 's' : ''}</span>
    {/if}
  </div>

  {#if loading}
    <div class="empty-state"><Spinner /></div>
  {:else if isEmpty}
    <div class="empty-state">
      <p style="font-size:3rem">🛒</p>
      <p>Tu carrito está vacío</p>
      <button class="btn btn-primary" style="margin-top:1rem" onclick={() => navigate('/products')}>
        Ver productos
      </button>
    </div>
  {:else}
    <div class="cart-list">
      {#each cartStore.items as item (item.productId)}
        <CartItem {item} onUpdateQty={handleUpdateQty} onRemove={handleRemove} />
      {/each}
    </div>

    <div class="cart-summary">
      <div class="summary-row">
        <span>Total</span>
        <span class="summary-total">{cartStore.total.toFixed(2)} €</span>
      </div>
      <div class="summary-actions">
        <button class="btn btn-ghost" onclick={() => showClearConfirm = true}>Vaciar carrito</button>
        <button class="btn btn-primary" onclick={handleCheckout} disabled={ordering}>
          {#if ordering}<Spinner small />{:else}Realizar Pedido{/if}
        </button>
      </div>
    </div>
  {/if}
</div>

{#if showClearConfirm}
  <ConfirmModal
    title="Vaciar carrito"
    message="¿Estás seguro de que quieres vaciar todo el carrito?"
    confirmText="Vaciar"
    onConfirm={handleClear}
    onCancel={() => showClearConfirm = false}
  />
{/if}

<style>
  .cart-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    margin-bottom: 1.5rem;
  }
  .cart-summary {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem;
    max-width: 400px;
    margin-left: auto;
  }
  .summary-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    font-size: 1.1rem;
  }
  .summary-total {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--accent);
  }
  .summary-actions {
    display: flex;
    gap: 0.75rem;
    justify-content: flex-end;
  }
</style>
