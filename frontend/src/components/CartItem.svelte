<script>
  let { item, onUpdateQty, onRemove } = $props();

  let updating = $state(false);

  async function changeQty(delta) {
    const newQty = item.cantidad + delta;
    if (newQty < 1) return;
    updating = true;
    try {
      await onUpdateQty(item.productId, newQty);
    } finally {
      updating = false;
    }
  }
</script>

<div class="cart-item">
  {#if item.imagen}
    <img class="item-img" src={item.imagen} alt={item.nombre} />
  {:else}
    <div class="item-img item-img-placeholder">🎆</div>
  {/if}

  <div class="item-info">
    <h4>{item.nombre}</h4>
    <span class="item-price">{item.precio.toFixed(2)} €</span>
  </div>

  <div class="item-qty">
    <button class="qty-btn" onclick={() => changeQty(-1)} disabled={updating || item.cantidad <= 1}>−</button>
    <span class="qty-val">{item.cantidad}</span>
    <button class="qty-btn" onclick={() => changeQty(1)} disabled={updating}>+</button>
  </div>

  <div class="item-subtotal">
    {(item.precio * item.cantidad).toFixed(2)} €
  </div>

  <button class="btn-icon remove-btn" onclick={() => onRemove(item.productId)} title="Eliminar">✕</button>
</div>

<style>
  .cart-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    transition: border-color var(--transition);
  }
  .cart-item:hover { border-color: rgba(255,107,53,0.2); }
  .item-img {
    width: 64px;
    height: 64px;
    border-radius: var(--radius-sm);
    object-fit: cover;
    background: var(--bg-hover);
    flex-shrink: 0;
  }
  .item-img-placeholder {
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    opacity: 0.3;
  }
  .item-info {
    flex: 1;
    min-width: 0;
  }
  .item-info h4 {
    font-size: 0.95rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .item-price {
    font-size: 0.85rem;
    color: var(--text-secondary);
  }
  .item-qty {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  .qty-btn {
    width: 28px;
    height: 28px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border);
    background: var(--bg-input);
    color: var(--text-primary);
    cursor: pointer;
    font-size: 1rem;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all var(--transition);
  }
  .qty-btn:hover:not(:disabled) { border-color: var(--accent); color: var(--accent); }
  .qty-btn:disabled { opacity: 0.4; cursor: not-allowed; }
  .qty-val {
    min-width: 24px;
    text-align: center;
    font-weight: 600;
  }
  .item-subtotal {
    font-weight: 700;
    font-size: 1rem;
    color: var(--accent);
    min-width: 70px;
    text-align: right;
  }
  .remove-btn {
    color: var(--text-muted) !important;
    font-size: 0.9rem;
  }
  .remove-btn:hover { color: var(--danger) !important; background: rgba(239,68,68,0.1) !important; }

  @media (max-width: 600px) {
    .cart-item { flex-wrap: wrap; }
    .item-img { width: 48px; height: 48px; }
    .item-subtotal { min-width: auto; }
  }
</style>
