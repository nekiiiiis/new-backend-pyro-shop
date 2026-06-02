import { apiFetch } from './api.js';

export function getProducts() {
  return apiFetch('/productos');
}

export function createProduct(product) {
  return apiFetch('/productos', {
    method: 'POST',
    body: JSON.stringify(product)
  });
}

export function updateProduct(id, product) {
  return apiFetch(`/productos/${id}`, {
    method: 'PUT',
    body: JSON.stringify(product)
  });
}

export function deleteProduct(id) {
  return apiFetch(`/productos/${id}`, {
    method: 'DELETE'
  });
}
