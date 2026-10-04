const VERSION_CACHE = 'inventario-v2';

self.addEventListener('install', (evento) => {
    self.skipWaiting();
});

self.addEventListener('activate', (evento) => {
    // Limpia cachés antiguas cuando se cambia el nombre de la versión
    evento.waitUntil(
        caches.keys().then(nombresCache => {
            return Promise.all(
                nombresCache.map(cache => {
                    if (cache !== VERSION_CACHE) {
                        return caches.delete(cache);
                    }
                })
            );
        }).then(() => clients.claim())
    );
});

self.addEventListener('fetch', (evento) => {
    evento.respondWith(
        fetch(evento.request).catch(() => {
            return new Response("Estás sin conexión o el archivo no se encuentra.");
        })
    );
});