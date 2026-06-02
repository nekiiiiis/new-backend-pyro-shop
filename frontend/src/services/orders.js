import { apiFetch } from './api.js';

export function getAllOrders() {
  return apiFetch('/api/orders');
}

export function getMyOrders() {
  return apiFetch('/api/orders/my-orders');
}

export function createOrder() {
  return apiFetch('/api/orders', { method: 'POST' });
}

export function updateOrderStatus(id, status) {
  return apiFetch(`/api/orders/${id}/status`, {
    method: 'PUT',
    body: JSON.stringify({ status })
  });
}

export function cancelOrder(id) {
  return apiFetch(`/api/orders/${id}`, { method: 'DELETE' });
}
