import { apiFetch } from './api.js';

export function login(username, password) {
  return apiFetch('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password })
  });
}

export function register(username, password) {
  return apiFetch('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ username, password })
  });
}

export function getMe() {
  return apiFetch('/auth/me');
}

export function changePassword(currentPassword, newPassword) {
  return apiFetch('/auth/change-password', {
    method: 'PUT',
    body: JSON.stringify({ currentPassword, newPassword })
  });
}
