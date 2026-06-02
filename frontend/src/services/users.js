import { apiFetch } from './api.js';

export function getUsers() {
  return apiFetch('/api/users');
}

export function updateUserRole(id, role) {
  return apiFetch(`/api/users/${id}/role`, {
    method: 'PUT',
    body: JSON.stringify({ role })
  });
}

export function deleteUser(id) {
  return apiFetch(`/api/users/${id}`, {
    method: 'DELETE'
  });
}
