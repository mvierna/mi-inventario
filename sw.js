// Service worker de MOVILEC: permite abrir la app sin conexión.
// Lo usan las dos versiones: index.html (iPhone) y movilec.html (Android).
// - Las páginas (HTML, manifest, icono): se piden a la red y, si no hay conexión, se usa la copia guardada.
// - Librerías de los CDN (versiones fijas): se usan desde la copia guardada.
// - Los CSV y Google Apps Script NO pasan por aquí: los CSV ya se guardan en IndexedDB desde la app.
// Si cambias las versiones de las librerías en movilec.html, cámbialas también aquí y sube VERSION.

const VERSION = 'movilec-v28';

const ARCHIVOS_APP = ['./', 'index.html', 'movilec.html', 'manifest.json', 'manifest-android.json', 'icono.png'];
const LIBRERIAS = [
    'https://cdnjs.cloudflare.com/ajax/libs/PapaParse/5.3.2/papaparse.min.js',
    'https://unpkg.com/@zxing/library@0.23.0/umd/index.min.js',
    'https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js',
    'https://cdn.jsdelivr.net/npm/jsbarcode@3.11.5/dist/JsBarcode.all.min.js',
    'https://cdn.jsdelivr.net/npm/zxing-wasm@3.1.5/dist/iife/reader/index.js',
    'https://fastly.jsdelivr.net/npm/zxing-wasm@3.1.5/dist/reader/zxing_reader.wasm',
    // OCR: el resto (motor y idioma) se guarda al usarlo la primera vez
    'https://cdn.jsdelivr.net/npm/tesseract.js@5.1.1/dist/tesseract.min.js'
];
const HOSTS_CDN = ['cdnjs.cloudflare.com', 'unpkg.com', 'cdn.jsdelivr.net', 'fastly.jsdelivr.net'];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(VERSION).then(cache =>
            // Cada archivo por separado: si falta uno (p. ej. el icono) no se cancela todo
            Promise.all([...ARCHIVOS_APP, ...LIBRERIAS].map(url => cache.add(url).catch(() => {})))
        ).then(() => self.skipWaiting())
    );
});

self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys()
            .then(nombres => Promise.all(nombres.filter(n => n !== VERSION).map(n => caches.delete(n))))
            .then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', event => {
    const req = event.request;
    if (req.method !== 'GET') return;
    const url = new URL(req.url);

    // Librerías: primero la copia guardada
    if (HOSTS_CDN.includes(url.hostname)) {
        event.respondWith(
            caches.match(req.url).then(guardada => guardada || fetch(req).then(resp => {
                const copia = resp.clone();
                caches.open(VERSION).then(cache => cache.put(req.url, copia));
                return resp;
            }))
        );
        return;
    }

    // Solo archivos de la propia app; los CSV los gestiona la app
    if (url.origin !== self.location.origin || url.pathname.toLowerCase().endsWith('.csv')) return;

    // Página y recursos propios: primero la red (para recibir actualizaciones), si falla la copia guardada.
    // cache 'no-cache': obliga a comprobar con el servidor y no usar la caché HTTP del navegador.
    event.respondWith(
        fetch(req, { cache: 'no-cache' }).then(resp => {
            if (resp.ok) { const copia = resp.clone(); caches.open(VERSION).then(cache => cache.put(req, copia)); }
            return resp;
        }).catch(() =>
            caches.match(req, { ignoreSearch: true }).then(guardada => guardada || Response.error())
        )
    );
});
