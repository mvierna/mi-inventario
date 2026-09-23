self.addEventListener('install', (evento) => {
    self.skipWaiting();
});

self.addEventListener('fetch', (evento) => {
    // No bloqueamos las peticiones para asegurar la lectura del CSV actualizado
});
