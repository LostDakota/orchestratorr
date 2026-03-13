import adapterAuto from '@sveltejs/adapter-auto';
import adapterStatic from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	// Consult https://kit.svelte.dev/docs/integrations#preprocessors
	// for more information about preprocessors
	preprocess: vitePreprocess(),

	kit: {
		// Use adapter-static for Docker/production builds, adapter-auto for development
		// This can be controlled via VITE_ADAPTER environment variable
		adapter: process.env.VITE_ADAPTER === 'static' ? adapterStatic({
		   pages: 'build',
                   assets: 'build',
                   fallback: 'index.html',
                   precompress: false,
                   strict: true
                }) : adapterAuto()
	}
};

export default config;
