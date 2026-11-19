// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

// GitHub Pages:
//  - Project site (https://<user>.github.io/<repo>/): set `base` to '/<repo>'
//  - User/org site or custom domain: set `base` to '/'
export default defineConfig({
  site: 'https://nitnkalra.github.io',
  base: '/kc',
  vite: { plugins: [tailwindcss()] },
});
