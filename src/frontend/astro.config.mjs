// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

// GitHub Pages: https://nitnkalra.github.io/kc/
//  - site = https://<github-username>.github.io
//  - base = /<repo-name>
export default defineConfig({
  site: 'https://nitnkalra.github.io',
  base: '/kc',
  vite: { plugins: [tailwindcss()] },
});
