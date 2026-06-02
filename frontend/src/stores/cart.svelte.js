function createCartStore() {
  let items = $state([]);
  let total = $state(0);

  return {
    get items() { return items; },
    get total() { return total; },
    get count() { return items.reduce((sum, i) => sum + i.cantidad, 0); },

    set(cart) {
      items = cart.items || [];
      total = cart.total || 0;
    },

    clear() {
      items = [];
      total = 0;
    }
  };
}

export const cartStore = createCartStore();
