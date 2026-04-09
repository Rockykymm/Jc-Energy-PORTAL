self.addEventListener('install', () => {
  console.log('JC Energy Service Worker installed');
});

self.addEventListener('fetch', (event) => {
  // This allows the app to load normally while being "installable"
  event.respondWith(fetch(event.request));
});
