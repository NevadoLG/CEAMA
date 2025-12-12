// Patch para Vite en Django
// Asegurar que Vite cargue los assets desde la ruta correcta
(function() {
  const importMetaUrl = new URL(import.meta.url);
  const baseUrl = importMetaUrl.pathname.split('/').slice(0, -1).join('/') + '/';
  
  // Exportar la configuración
  window.__VITE_CONFIG__ = {
    base: '/static/landing/dist-assets/'
  };
  
  // Patch para __VITE_PRELOAD_HELPER__
  window.__VITE_PRELOAD_HELPER__ = {
    preload: function(modulePreload) {
      // No hacer nada, solo retornar la función original
      return modulePreload;
    }
  };
})();
