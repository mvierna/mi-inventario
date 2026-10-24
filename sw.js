const VERSION_CACHE = 'inventario-v6';

// Archivos estáticos principales para caché local
const ARCHIVOS_ESTATICOS = [
    './',
    './index.html',
    './movilec.html',
    './manifest.json',
    './manifest-android.json',
    './icono.png'
];

self.addEventListener('install', (evento) => {
    self.skipWaiting();
    evento.waitUntil(
        caches.open(VERSION_CACHE).then((cache) => {
            return cache.addAll(ARCHIVOS_ESTATICOS).catch((err) => {
                console.warn("Algunos archivos no se pudieron precachear:", err);
            });
        })
    );
});

self.addEventListener('activate', (evento) => {
    evento.waitUntil(
        caches.keys().then((nombresCache) => {
            return Promise.all(
                nombresCache.map((cache) => {
                    if (cache !== VERSION_CACHE) {
                        return caches.delete(cache);
                    }
                })
            );
        }).then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', (evento) => {
    const url = evento.request.url;

    // 1. Los CSV siempre van directo a RED para tener stock actualizado
    // (La persistencia offline del stock ya la gestiona IndexedDB en el HTML)
    if (url.includes('.csv')) {
        evento.respondWith(fetch(evento.request));
        return;
    }

    // 2. Para la interfaz y assets: Network First con fallback a Cache
    evento.respondWith(
        fetch(evento.request)
            .then((respuestaRed) => {
                // Si la red responde bien, actualizamos la copia en caché
                if (respuestaRed && respuestaRed.status === 200 && evento.request.method === 'GET') {
                    const respuestaClonada = respuestaRed.clone();
                    caches.open(VERSION_CACHE).then((cache) => {
                        cache.put(evento.request, respuestaClonada);
                    });
                }
                return respuestaRed;
            })
            .catch(() => {
                // Si no hay red, entrega la pantalla guardada en caché
                return caches.match(evento.request);
            })
    );
});