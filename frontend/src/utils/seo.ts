/**
 * SEO and Meta Tags Utility
 * Comprehensive meta tag management for optimal SEO
 */

export interface MetaTagsConfig {
  title?: string
  description?: string
  keywords?: string[]
  image?: string
  url?: string
  type?: 'website' | 'article' | 'profile'
  author?: string
  publishedTime?: string
  modifiedTime?: string
  section?: string
  tags?: string[]
  locale?: string
  twitterCard?: 'summary' | 'summary_large_image' | 'app' | 'player'
  twitterCreator?: string
  canonicalUrl?: string
}

const DEFAULT_CONFIG: Required<Omit<MetaTagsConfig, 'publishedTime' | 'modifiedTime' | 'section' | 'tags' | 'canonicalUrl'>> = {
  title: 'Octopus Second Brain - AI-Powered Knowledge Management',
  description: 'Transform your knowledge into an intelligent neural network. Octopus Second Brain offers AI-powered semantic search, 3D visualization, and smart organization for your notes and ideas.',
  keywords: [
    'second brain',
    'knowledge management',
    'note-taking',
    'AI',
    'semantic search',
    'neural network',
    'visualization',
    '3D',
    'PKM',
    'personal knowledge management',
    'Zettelkasten',
    'digital garden'
  ],
  image: 'https://octopus-ai-secondbrain.github.io/og-image.png',
  url: 'https://octopus-ai-secondbrain.github.io/',
  type: 'website',
  author: 'Octopus Second Brain Team',
  locale: 'en_US',
  twitterCard: 'summary_large_image',
  twitterCreator: '@octopussecondbrain'
}

/**
 * Set document title with site name
 */
export const setDocumentTitle = (pageTitle?: string): void => {
  const siteName = 'Octopus Second Brain'
  document.title = pageTitle ? `${pageTitle} | ${siteName}` : siteName
}

/**
 * Update or create a meta tag
 */
const setMetaTag = (property: string, content: string, isName = false): void => {
  const attribute = isName ? 'name' : 'property'
  let element = document.querySelector(`meta[${attribute}="${property}"]`)
  
  if (!element) {
    element = document.createElement('meta')
    element.setAttribute(attribute, property)
    document.head.appendChild(element)
  }
  
  element.setAttribute('content', content)
}

/**
 * Set canonical URL
 */
const setCanonicalUrl = (url: string): void => {
  let link = document.querySelector('link[rel="canonical"]')
  
  if (!link) {
    link = document.createElement('link')
    link.setAttribute('rel', 'canonical')
    document.head.appendChild(link)
  }
  
  link.setAttribute('href', url)
}

/**
 * Set all meta tags for a page
 */
export const setMetaTags = (config: MetaTagsConfig = {}): void => {
  const merged = { ...DEFAULT_CONFIG, ...config }

  // Basic meta tags
  setMetaTag('description', merged.description, true)
  setMetaTag('keywords', merged.keywords.join(', '), true)
  setMetaTag('author', merged.author, true)

  // Open Graph
  setMetaTag('og:title', merged.title)
  setMetaTag('og:description', merged.description)
  setMetaTag('og:image', merged.image)
  setMetaTag('og:url', merged.url)
  setMetaTag('og:type', merged.type)
  setMetaTag('og:locale', merged.locale)
  setMetaTag('og:site_name', 'Octopus Second Brain')

  // Twitter Card
  setMetaTag('twitter:card', merged.twitterCard, true)
  setMetaTag('twitter:title', merged.title, true)
  setMetaTag('twitter:description', merged.description, true)
  setMetaTag('twitter:image', merged.image, true)
  setMetaTag('twitter:creator', merged.twitterCreator, true)

  // Article specific
  if (config.publishedTime) {
    setMetaTag('article:published_time', config.publishedTime)
  }
  if (config.modifiedTime) {
    setMetaTag('article:modified_time', config.modifiedTime)
  }
  if (config.section) {
    setMetaTag('article:section', config.section)
  }
  if (config.tags) {
    config.tags.forEach(tag => {
      setMetaTag('article:tag', tag)
    })
  }

  // Canonical URL
  const canonicalUrl = config.canonicalUrl || merged.url
  setCanonicalUrl(canonicalUrl)

  // Set document title
  setDocumentTitle(config.title || merged.title)
}

/**
 * Page-specific meta configurations
 */
export const PAGE_METAS = {
  home: {
    title: 'Octopus Second Brain - AI-Powered Knowledge Management',
    description: 'Transform your knowledge into an intelligent neural network with AI-powered semantic search and 3D visualization.',
    keywords: ['second brain', 'knowledge management', 'AI', 'semantic search'],
    url: 'https://octopus-ai-secondbrain.github.io/'
  },
  notes: {
    title: 'My Notes',
    description: 'Manage and organize your knowledge with rich text editing and smart tagging.',
    keywords: ['notes', 'writing', 'knowledge base'],
    url: 'https://octopus-ai-secondbrain.github.io/notes'
  },
  search: {
    title: 'Search',
    description: 'Find anything in your knowledge base with AI-powered semantic search.',
    keywords: ['search', 'semantic search', 'AI search', 'find notes'],
    url: 'https://octopus-ai-secondbrain.github.io/search'
  },
  map: {
    title: 'Neural Map',
    description: 'Visualize your knowledge network in stunning 2D and 3D interactive maps.',
    keywords: ['neural map', '3D visualization', 'knowledge graph', 'network'],
    url: 'https://octopus-ai-secondbrain.github.io/map'
  },
  dashboard: {
    title: 'Dashboard',
    description: 'View analytics and insights about your knowledge base.',
    keywords: ['analytics', 'statistics', 'dashboard', 'insights'],
    url: 'https://octopus-ai-secondbrain.github.io/dashboard'
  },
  settings: {
    title: 'Settings',
    description: 'Customize your Octopus Second Brain experience.',
    keywords: ['settings', 'preferences', 'configuration'],
    url: 'https://octopus-ai-secondbrain.github.io/settings'
  },
  login: {
    title: 'Login',
    description: 'Access your AI-powered second brain.',
    keywords: ['login', 'sign in', 'authentication'],
    url: 'https://octopus-ai-secondbrain.github.io/login'
  },
  signup: {
    title: 'Sign Up',
    description: 'Create your free Octopus Second Brain account.',
    keywords: ['sign up', 'register', 'create account'],
    url: 'https://octopus-ai-secondbrain.github.io/signup'
  }
} as const

/**
 * Generate structured data (JSON-LD) for rich snippets
 */
export const generateStructuredData = () => {
  const structuredData = {
    '@context': 'https://schema.org',
    '@type': 'WebApplication',
    name: 'Octopus Second Brain',
    description: 'AI-powered knowledge management system with semantic search and neural visualization',
    url: 'https://octopus-ai-secondbrain.github.io',
    applicationCategory: 'ProductivityApplication',
    operatingSystem: 'Any',
    offers: {
      '@type': 'Offer',
      price: '0',
      priceCurrency: 'USD'
    },
    author: {
      '@type': 'Organization',
      name: 'Octopus Second Brain Team',
      url: 'https://octopus-ai-secondbrain.github.io'
    },
    aggregateRating: {
      '@type': 'AggregateRating',
      ratingValue: '4.8',
      ratingCount: '156'
    },
    screenshot: 'https://octopus-ai-secondbrain.github.io/screenshots/desktop-1.png'
  }

  // Add or update structured data script tag
  let script = document.querySelector('script[type="application/ld+json"]')
  
  if (!script) {
    script = document.createElement('script')
    script.type = 'application/ld+json'
    document.head.appendChild(script)
  }
  
  script.textContent = JSON.stringify(structuredData)
}

/**
 * Initialize SEO for the application
 */
export const initializeSEO = (): void => {
  // Set default meta tags
  setMetaTags()
  
  // Add structured data
  generateStructuredData()
  
  // Add additional meta tags
  const additionalMetas = [
    { name: 'application-name', content: 'Octopus Second Brain' },
    { name: 'apple-mobile-web-app-capable', content: 'yes' },
    { name: 'apple-mobile-web-app-status-bar-style', content: 'black-translucent' },
    { name: 'apple-mobile-web-app-title', content: 'Octopus' },
    { name: 'mobile-web-app-capable', content: 'yes' },
    { name: 'msapplication-TileColor', content: '#F24D80' },
    { name: 'msapplication-config', content: '/browserconfig.xml' },
    { name: 'theme-color', content: '#F24D80' }
  ]

  additionalMetas.forEach(({ name, content }) => {
    setMetaTag(name, content, true)
  })
}
