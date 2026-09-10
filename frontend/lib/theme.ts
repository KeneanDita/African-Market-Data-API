// Shared by the server layout (inline script) and the client ThemeProvider.
export const THEME_STORAGE_KEY = "africadata.theme";
export type Theme = "light" | "dark";

// Runs before hydration so the first paint already has the right class — no flash.
export const themeInitScript = `(function(){try{var k='${THEME_STORAGE_KEY}';var t=localStorage.getItem(k);if(t!=='light'&&t!=='dark'){t=window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light'}document.documentElement.classList.toggle('dark',t==='dark')}catch(e){}})();`;
