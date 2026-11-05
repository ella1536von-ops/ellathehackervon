/* Caches the app shell so CyberRange Academy opens offline. Paths are relative for GitHub Pages subpaths. */
var CACHE = "cyberrange-academy-v2";
var ASSETS = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./icon-192.png",
  "./icon-512.png"
];

function cacheAsset(cache, url) {
  return fetch(url).then(function (response) {
    if (!response || !response.ok) {
      throw new Error("failed to cache " + url);
    }
    if (!response.redirected) {
      return cache.put(url, response);
    }
    return response.blob().then(function (blob) {
      var headers = new Headers(response.headers);
      var copy = new Response(blob, {
        status: response.status,
        statusText: response.statusText,
        headers: headers
      });
      return cache.put(url, copy);
    });
  });
}

self.addEventListener("install", function (event) {
  event.waitUntil(
    caches.open(CACHE).then(function (cache) {
      return ASSETS.reduce(function (chain, url) {
        return chain.then(function () {
          return cacheAsset(cache, url);
        });
      }, Promise.resolve());
    }).then(function () {
      return self.skipWaiting();
    })
  );
});

self.addEventListener("activate", function (event) {
  event.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(keys.filter(function (key) {
        return key !== CACHE;
      }).map(function (key) {
        return caches.delete(key);
      }));
    }).then(function () {
      return self.clients.claim();
    })
  );
});

self.addEventListener("fetch", function (event) {
  if (event.request.method !== "GET") return;
  event.respondWith(
    caches.match(event.request).then(function (cached) {
      if (cached) return cached;
      return fetch(event.request).catch(function () {
        if (event.request.mode === "navigate") {
          return caches.match("./index.html").then(function (fallback) {
            return fallback || Response.error();
          });
        }
        return Response.error();
      });
    })
  );
});
