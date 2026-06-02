<script>
  import { auth } from '../stores/auth.svelte.js';
  import { toast } from '../stores/toast.svelte.js';
  import { cartStore } from '../stores/cart.svelte.js';
  import * as productsAPI from '../services/products.js';
  import * as cartAPI from '../services/cart.js';
  import ProductCard from '../components/ProductCard.svelte';
  import ProductForm from '../components/ProductForm.svelte';
  import ProductDetail from '../components/ProductDetail.svelte';
  import ConfirmModal from '../components/ConfirmModal.svelte';
  import Spinner from '../components/Spinner.svelte';

  let products = $state([]);
  let loading = $state(true);
  let search = $state('');
  let categoryFilter = $state('');
  let priceMin = $state('');
  let priceMax = $state('');
  let showForm = $state(false);
  let editingProduct = $state(null);
  let selectedProduct = $state(null);
  let deleteTarget = $state(null);

  const categoryLabels = {
    'fuegos-artificiales': 'Fuegos Artificiales',
    'petardos': 'Petardos',
    'bengalas': 'Bengalas',
    'cohetes': 'Cohetes',
    'otros': 'Otros'
  };

  let filteredProducts = $derived(
    products.filter(p => {
      const q = search.toLowerCase();
      const matchesSearch = !q ||
        p.nombre.toLowerCase().includes(q) ||
        (p.descripcion || '').toLowerCase().includes(q);
      const matchesCat = !categoryFilter || p.categoria === categoryFilter;
      const min = priceMin !== '' ? Number(priceMin) : 0;
      const max = priceMax !== '' ? Number(priceMax) : Infinity;
      const matchesPrice = p.precio >= min && p.precio <= max;
      return matchesSearch && matchesCat && matchesPrice;
    })
  );

  let productCount = $derived(filteredProducts.length);
  let totalCount = $derived(products.length);
  let categories = $derived([...new Set(products.map(p => p.categoria))].sort());

  $effect(() => {
    loadProducts();
  });

  async function loadProducts() {
    loading = true;
    try {
      products = await productsAPI.getProducts();
    } catch (err) {
      toast.error('Error cargando productos: ' + err.message);
    } finally {
      loading = false;
    }
  }

  async function handleAddToCart(product) {
    try {
      const result = await cartAPI.addToCart(product._id);
      cartStore.set(result.cart);
      toast.success(`${product.nombre} añadido al carrito`);
    } catch (err) {
      toast.error(err.message);
    }
  }

  async function handleSave(data) {
    try {
      if (editingProduct) {
        await productsAPI.updateProduct(editingProduct._id, data);
        toast.success('Producto actualizado');
      } else {
        await productsAPI.createProduct(data);
        toast.success('Producto creado');
      }
      showForm = false;
      editingProduct = null;
      await loadProducts();
    } catch (err) {
      toast.error(err.message);
    }
  }

  async function handleDelete() {
    if (!deleteTarget) return;
    try {
      await productsAPI.deleteProduct(deleteTarget._id);
      toast.success('Producto eliminado');
      deleteTarget = null;
      await loadProducts();
    } catch (err) {
      toast.error(err.message);
    }
  }

  function openCreate() { editingProduct = null; showForm = true; }

  function openEdit(product) { editingProduct = product; showForm = true; }

  function openEditFromDetail() {
    const p = selectedProduct;
    selectedProduct = null;
    openEdit(p);
  }
</script>

<div class="page">
  <div class="page-header">
    <h1>Productos</h1>
    <span class="badge badge-accent">{productCount} de {totalCount}</span>
    {#if auth.isAdmin}
      <button class="btn btn-primary" onclick={openCreate}>+ Nuevo Producto</button>
    {/if}
  </div>

  <div class="filters">
    <input
      type="search"
      class="search-input"
      placeholder="Buscar por nombre o descripción..."
      aria-label="Buscar productos"
      bind:value={search}
    />
    <select bind:value={categoryFilter} aria-label="Filtrar por categoría">
      <option value="">Todas las categorías</option>
      {#each categories as cat}
        <option value={cat}>{categoryLabels[cat] || cat}</option>
      {/each}
    </select>
    <input type="number" placeholder="Precio mín." aria-label="Precio mínimo" bind:value={priceMin} min="0" step="0.01" />
    <input type="number" placeholder="Precio máx." aria-label="Precio máximo" bind:value={priceMax} min="0" step="0.01" />
  </div>

  {#if loading}
    <div class="empty-state"><Spinner /></div>
  {:else if filteredProducts.length === 0}
    <div class="empty-state">
      <p>🎆</p>
      <p>No se encontraron productos</p>
      {#if search || categoryFilter || priceMin || priceMax}
        <button class="btn btn-ghost" style="margin-top:1rem" onclick={() => { search=''; categoryFilter=''; priceMin=''; priceMax=''; }}>
          Limpiar filtros
        </button>
      {/if}
    </div>
  {:else}
    <div class="grid grid-products">
      {#each filteredProducts as product (product._id)}
        <ProductCard
          {product}
          isAdmin={auth.isAdmin}
          onView={() => selectedProduct = product}
          onEdit={() => openEdit(product)}
          onDelete={() => deleteTarget = product}
          onAddToCart={() => handleAddToCart(product)}
        />
      {/each}
    </div>
  {/if}
</div>

{#if showForm}
  <ProductForm
    product={editingProduct}
    onSave={handleSave}
    onCancel={() => { showForm = false; editingProduct = null; }}
  />
{/if}

{#if selectedProduct}
  <ProductDetail
    product={selectedProduct}
    isAdmin={auth.isAdmin}
    onClose={() => selectedProduct = null}
    onAddToCart={() => { handleAddToCart(selectedProduct); selectedProduct = null; }}
    onEdit={openEditFromDetail}
  />
{/if}

{#if deleteTarget}
  <ConfirmModal
    title="Eliminar producto"
    message={'¿Estás seguro de que quieres eliminar "' + deleteTarget.nombre + '"? Esta acción no se puede deshacer.'}
    confirmText="Eliminar"
    onConfirm={handleDelete}
    onCancel={() => deleteTarget = null}
  />
{/if}
