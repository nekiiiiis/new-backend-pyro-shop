function getHash() {
  const h = window.location.hash;
  return h.startsWith('#/') ? h.slice(1) : '/';
}

function createRouter() {
  let path = $state(getHash());

  window.addEventListener('hashchange', () => {
    path = getHash();
  });

  return {
    get path() { return path; },
    get segment() { return path.split('/')[1] || ''; },
    get param() { return path.split('/')[2] || null; }
  };
}

export const router = createRouter();

export function navigate(path) {
  window.location.hash = '#' + path;
}
