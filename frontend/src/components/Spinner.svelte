<script>
  let { small = false } = $props();
</script>

<span class="spinner" class:small></span>

<style>
  .spinner {
    display: inline-block;
    width: 32px;
    height: 32px;
    border: 3px solid var(--border);
    border-top-color: var(--accent);
    border-radius: 50%;
    animation: spin 0.6s linear infinite;
  }
  .small {
    width: 18px;
    height: 18px;
    border-width: 2px;
  }
</style>
