// nuxt.config.ts - Configuration simplifiée pour API directe
export default defineNuxtConfig({
  app: {
    head: {
      title: 'ISFAD Assistant Hakili',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'Assistant virtuel IFAD Halki' }
      ],
      link: [
        {
          rel: 'stylesheet',
          href: 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css',
          integrity: 'sha512-1ycn6IcaQQ40/MKBW2W4Rhis/DbILU74C1vSrLJxCq57o941Ym01SwNsOMqvEBFlcgUa6xLiPY/NS5R+E6ztJQ==',
          crossorigin: 'anonymous'
        }
      ]
    },
  },
  
  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt',
  ],
  
  css: [
    './assets/css/main.css',
  ],
  
  postcss: {
    plugins: {
      tailwindcss: {},
      autoprefixer: {},
    },
  },
 
  // Configuration SSR
  ssr: true,
 
  // Variables d'environnement publiques
  runtimeConfig: {
    public: {
      environment: process.env.NODE_ENV || 'development',
      appVersion: '1.0.0',
      apiUrl: 'https://smartsearch.myfad.org' // Pour référence
    }
  },
  
  // Configuration Vercel simplifiée
  nitro: {
    preset: 'vercel'
  },

  // Configuration du build
  build: {
    extractCSS: true,
  },

  // Configuration expérimentale
  experimental: {
    payloadExtraction: false
  }
})