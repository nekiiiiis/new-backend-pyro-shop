<script>
  import { untrack } from 'svelte';
  import Spinner from './Spinner.svelte';

  let { product = null, onSave, onCancel } = $props();

  const initial = untrack(() => product);
  let nombre = $state(initial?.nombre || '');
  let precio = $state(initial?.precio ?? '');
  let descripcion = $state(initial?.descripcion || '');
  let imagen = $state(initial?.imagen || '');
  let categoria = $state(initial?.categoria || 'otros');
  let loading = $state(false);
  let errors = $state({});

  let isEditing = $derived(!!product);

  function validate() {
    const e = {};
    if (!nombre.trim()) e.nombre = 'El nombre es obligatorio';
    if (!precio || Number(precio) <= 0) e.precio = 'El precio debe ser mayor que 0';
    if (!descripcion.trim()) e.descripcion = 'La descripción es obligatoria';
    if (imagen && !imagen.startsWith('http')) e.imagen = 'Debe ser una URL válida';
    errors = e;
    return Object.keys(e).length === 0;
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!validate()) return;
    loading = true;
    try {
      await onSave({
        nombre: nombre.trim(),
        precio: Number(precio),
        descripcion: descripcion.trim(),
        imagen: imagen.trim() || null,
        categoria
      });
    } finally {
      loading = false;
    }
  }

  function handleBackdrop(e) {
    if (e.target === e.currentTarget) onCancel?.();
  }

  function handleKeydown(e) {
    if (e.key === 'Escape') onCancel?.();
  }
</script>

<div class="modal-backdrop" onclick={handleBackdrop} onkeydown={handleKeydown} role="dialog" aria-modal="true" aria-label={isEditing ? 'Editar producto' : 'Nuevo producto'} tabindex="-1">
  <div class="modal modal-lg">
    <div class="modal-header">
      <h2>{isEditing ? 'Editar Producto' : 'Nuevo Producto'}</h2>
      <button class="btn-icon" onclick={onCancel}>✕</button>
    </div>

    <form onsubmit={handleSubmit}>
      <div class="form-group">
        <label for="pf-nombre">Nombre *</label>
        <input id="pf-nombre" type="text" bind:value={nombre} placeholder="Nombre del producto" />
        {#if errors.nombre}<span class="field-error">{errors.nombre}</span>{/if}
      </div>

      <div class="form-row">
        <div class="form-group">
          <label for="pf-precio">Precio (€) *</label>
          <input id="pf-precio" type="number" step="0.01" min="0" bind:value={precio} placeholder="0.00" />
          {#if errors.precio}<span class="field-error">{errors.precio}</span>{/if}
        </div>
        <div class="form-group">
          <label for="pf-cat">Categoría</label>
          <select id="pf-cat" bind:value={categoria}>
            <option value="fuegos-artificiales">Fuegos Artificiales</option>
            <option value="petardos">Petardos</option>
            <option value="bengalas">Bengalas</option>
            <option value="cohetes">Cohetes</option>
            <option value="otros">Otros</option>
          </select>
        </div>
      </div>

      <div class="form-group">
        <label for="pf-desc">Descripción *</label>
        <textarea id="pf-desc" bind:value={descripcion} placeholder="Describe el producto..." rows="3"></textarea>
        {#if errors.descripcion}<span class="field-error">{errors.descripcion}</span>{/if}
      </div>

      <div class="form-group">
        <label for="pf-img">URL de imagen (opcional)</label>
        <input id="pf-img" type="url" bind:value={imagen} placeholder="https://..." />
        {#if errors.imagen}<span class="field-error">{errors.imagen}</span>{/if}
      </div>

      <div class="modal-actions">
        <button type="button" class="btn btn-ghost" onclick={onCancel} disabled={loading}>Cancelar</button>
        <button type="submit" class="btn btn-primary" disabled={loading}>
          {#if loading}<Spinner small />{:else}{isEditing ? 'Guardar Cambios' : 'Crear Producto'}{/if}
        </button>
      </div>
    </form>
  </div>
</div>

<style>
  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
  }
  .field-error {
    color: var(--danger);
    font-size: 0.8rem;
    margin-top: 0.25rem;
    display: block;
  }
  @media (max-width: 480px) {
    .form-row { grid-template-columns: 1fr; }
  }
</style>
