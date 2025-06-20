import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';

export default defineConfig({
  base: './',
  plugins: [vue()],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\//, '')
      }
    }
  },
  resolve: {
    dedupe: [
      '@codemirror/state',
      '@codemirror/view',
      '@codemirror/basic-setup',
      '@codemirror/lang-html',
      '@codemirror/lang-css',
      '@codemirror/lang-javascript',
      '@codemirror/theme-one-dark'
    ],
    alias: {
      '@': path.resolve(__dirname, 'src'),
      'codemirror/mode/htmlmixed/htmlmixed.js': path.resolve(__dirname, 'node_modules/codemirror/mode/htmlmixed/htmlmixed.js'),
      'codemirror/mode/css/css.js':          path.resolve(__dirname, 'node_modules/codemirror/mode/css/css.js'),
      'codemirror/mode/javascript/javascript.js': path.resolve(__dirname, 'node_modules/codemirror/mode/javascript/javascript.js'),
      'codemirror/lib/codemirror.css':       path.resolve(__dirname, 'node_modules/codemirror/lib/codemirror.css'),
    }
  },
  optimizeDeps: {
    include: [
      '@codemirror/basic-setup',
      '@codemirror/lang-html',
      '@codemirror/lang-css',
      '@codemirror/lang-javascript',
    ]
  }
});
