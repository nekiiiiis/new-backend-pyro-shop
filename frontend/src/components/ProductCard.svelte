<script>
  let { product, isAdmin = false, onView, onEdit, onDelete, onAddToCart } = $props();

  const categoryLabels = {
    'fuegos-artificiales': 'Fuegos Artificiales',
    'petardos': 'Petardos',
    'bengalas': 'Bengalas',
    'cohetes': 'Cohetes',
    'otros': 'Otros'
  };

  let categoryLabel = $derived(categoryLabels[product.categoria] || product.categoria);
</script>

<div class="product-card card">
  {#if product.imagen}
    <div class="card-img" style="background-image: url({product.imagen})"></div>
  {:else}
    <div class="card-img card-img-placeholder">
      <span>🎆</span>
    </div>
  {/if}

  <div class="card-body">
    <span class="category-tag">{categoryLabel}</span>
    <h3 class="card-title">{product.nombre}</h3>
    <p class="card-desc">{product.descripcion?.slice(0, 80)}{product.descripcion?.length > 80 ? '...' : ''}</p>
    <div class="card-price">{product.precio.toFixed(2)} €</div>
  </div>

  <div class="card-actions">
    <button class="btn btn-ghost btn-sm" onclick={onView}>Ver detalle</button>
    {#if isAdmin}
      <button class="btn btn-ghost btn-sm" onclick={onEdit}>Editar</button>
      <button class="btn btn-danger btn-sm" onclick={onDelete}>Eliminar</button>
    {:else}
      <button class="btn btn-primary btn-sm" onclick={onAddToCart}>Añadir al carrito</button>
    {/if}
  </div>
</div>

<style>
  .product-card {
    display: flex;
    flex-direction: column;
    overflow: hidden;
    padding: 0;
    transition: transform var(--transition), box-shadow var(--transition), border-color var(--transition);
  }
  .product-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 30px rgba(0,0,0,0.3);
  }
  .card-img {
    height: 180px;
    background-size: cover;
    background-position: center;
    background-color: var(--bg-hover);
  }
  .card-img-placeholder {
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 3rem;
    opacity: 0.3;
  }
  .card-body {
    padding: 1rem 1.25rem;
    flex: 1;
  }
  .category-tag {
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--accent);
    background: var(--accent-glow);
    padding: 0.15rem 0.5rem;
    border-radius: 4px;
    display: inline-block;
    margin-bottom: 0.5rem;
  }
  .card-title {
    font-size: 1.05rem;
    margin-bottom: 0.35rem;
    line-height: 1.3;
  }
  .card-desc {
    font-size: 0.85rem;
    color: var(--text-secondary);
    margin-bottom: 0.75rem;
    line-height: 1.4;
  }
  .card-price {
    font-size: 1.35rem;
    font-weight: 700;
    color: var(--accent);
  }
  .card-actions {
    padding: 0.75rem 1.25rem;
    border-top: 1px solid var(--border);
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
  }
</style>
