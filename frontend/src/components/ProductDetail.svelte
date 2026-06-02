<script>
  let { product, isAdmin = false, onClose, onAddToCart, onEdit } = $props();

  const categoryLabels = {
    'fuegos-artificiales': 'Fuegos Artificiales',
    'petardos': 'Petardos',
    'bengalas': 'Bengalas',
    'cohetes': 'Cohetes',
    'otros': 'Otros'
  };

  let categoryLabel = $derived(categoryLabels[product.categoria] || product.categoria);

  function handleBackdrop(e) {
    if (e.target === e.currentTarget) onClose?.();
  }

  function handleKeydown(e) {
    if (e.key === 'Escape') onClose?.();
  }
</script>

<div class="modal-backdrop" onclick={handleBackdrop} onkeydown={handleKeydown} role="dialog" aria-modal="true" aria-label="Detalle del producto" tabindex="-1">
  <div class="modal modal-lg">
    <div class="modal-header">
      <h2>Detalle del Producto</h2>
      <button class="btn-icon" onclick={onClose}>✕</button>
    </div>

    <div class="detail-layout">
      {#if product.imagen}
        <img class="detail-img" src={product.imagen} alt={product.nombre} />
      {:else}
        <div class="detail-img detail-placeholder">🎆</div>
      {/if}

      <div class="detail-info">
        <span class="badge badge-accent">{categoryLabel}</span>
        <h2 class="detail-name">{product.nombre}</h2>
        <p class="detail-price">{product.precio.toFixed(2)} €</p>
        <p class="detail-desc">{product.descripcion}</p>

        {#if product.createdAt}
          <p class="detail-date">Añadido el {new Date(product.createdAt).toLocaleDateString('es-ES')}</p>
        {/if}

        <div class="detail-actions">
          {#if isAdmin}
            <button class="btn btn-primary" onclick={onEdit}>Editar producto</button>
          {:else}
            <button class="btn btn-primary" onclick={onAddToCart}>Añadir al carrito</button>
          {/if}
          <button class="btn btn-ghost" onclick={onClose}>Cerrar</button>
        </div>
      </div>
    </div>
  </div>
</div>

<style>
  .detail-layout {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
  }
  .detail-img {
    width: 100%;
    border-radius: var(--radius);
    object-fit: cover;
    max-height: 320px;
    background: var(--bg-hover);
  }
  .detail-placeholder {
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 4rem;
    height: 240px;
    opacity: 0.3;
    border-radius: var(--radius);
  }
  .detail-name {
    font-size: 1.4rem;
    margin: 0.75rem 0 0.5rem;
  }
  .detail-price {
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--accent);
    margin-bottom: 0.75rem;
  }
  .detail-desc {
    color: var(--text-secondary);
    line-height: 1.6;
    margin-bottom: 1rem;
  }
  .detail-date {
    font-size: 0.8rem;
    color: var(--text-muted);
    margin-bottom: 1.25rem;
  }
  .detail-actions {
    display: flex;
    gap: 0.75rem;
  }
  @media (max-width: 600px) {
    .detail-layout { grid-template-columns: 1fr; }
    .detail-img { max-height: 200px; }
  }
</style>
