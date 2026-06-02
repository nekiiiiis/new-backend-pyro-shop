function createAuthStore() {
  let token = $state(localStorage.getItem('token') || '');
  let user = $state(JSON.parse(localStorage.getItem('user') || 'null'));

  return {
    get token() { return token; },
    get user() { return user; },
    get isAuthenticated() { return !!token; },
    get isAdmin() { return user?.role === 'admin'; },
    get username() { return user?.username || ''; },
    get userId() { return user?.id || ''; },

    login(newToken, newUser) {
      token = newToken;
      user = newUser;
      localStorage.setItem('token', newToken);
      localStorage.setItem('user', JSON.stringify(newUser));
    },

    logout() {
      token = '';
      user = null;
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    },

    updateUser(newUser) {
      user = newUser;
      localStorage.setItem('user', JSON.stringify(newUser));
    }
  };
}

export const auth = createAuthStore();
