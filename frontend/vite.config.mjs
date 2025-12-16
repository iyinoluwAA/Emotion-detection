import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tsconfigPaths from 'vite-tsconfig-paths';

export default defineConfig({
  plugins: [react(), tsconfigPaths()],
  server: {
    port: 7777, // Unique port for Emotion Detection to avoid conflicts with other projects
    strictPort: true, // Fail if port is already in use instead of trying another
    host: true, // Allow access from network
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './vitest.setup.mjs',
  },
});
