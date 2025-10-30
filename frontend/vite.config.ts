import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { componentTagger } from "lovable-tagger";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Load environment variables from the root directory
  const env = loadEnv(mode, path.resolve(__dirname, '../'), '');
  
  return {
    server: {
      host: "::",
      port: parseInt(env.VITE_PORT || '8080'),
    },
    plugins: [
      react(),
      mode === 'development' &&
      componentTagger(),
    ].filter(Boolean),
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
      },
    },
    define: {
      // Expose environment variables to the client
      __VITE_API_URL__: JSON.stringify(env.VITE_API_URL || 'http://127.0.0.1:8000'),
      __VITE_SUPABASE_PROJECT_ID__: JSON.stringify(env.VITE_SUPABASE_PROJECT_ID),
      __VITE_SUPABASE_ANON_KEY__: JSON.stringify(env.VITE_SUPABASE_ANON_KEY),
      __VITE_SUPABASE_URL__: JSON.stringify(env.VITE_SUPABASE_URL),
      __VITE_APP_ENV__: JSON.stringify(env.VITE_APP_ENV || 'development'),
    },
  };
});
