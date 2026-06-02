import { apiFetch } from './api.js';

export function getCart() {
  return apiFetch('/api/cart');
}

export function addToCart(productId, cantidad = 1) {
  return apiFetch('/api/cart/add', {
    method: 'POST',
    body: JSON.stringify({ productId, cantidad })
  });
}

export function updateCartItem(productId, cantidad) {
  return apiFetch('/api/cart/update', {
    method: 'PUT',
    body: JSON.stringify({ productId, cantidad })
  });
}

export function removeFromCart(productId) {
  return apiFetch(`/api/cart/remove/${productId}`, {
    method: 'DELETE'
  });
}

export function clearCart() {
  return apiFetch('/api/cart/clear', {
    method: 'DELETE'
  });
}
