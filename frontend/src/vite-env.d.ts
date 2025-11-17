/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_BASE_PATH?: string
  readonly VITE_SENTRY_DSN?: string
  readonly VITE_ENABLE_ANALYTICS?: string
  readonly VITE_ANALYTICS_URL?: string
  readonly MODE: 'development' | 'production' | 'test'
  readonly DEV: boolean
  readonly PROD: boolean
  readonly SSR: boolean
}

interface ImportMeta {
  readonly env: ImportMetaEnv
  readonly hot?: {
    readonly data: Record<string, unknown>
    accept(): void
    accept(cb: (mod: unknown) => void): void
    accept(dep: string, cb: (mod: unknown) => void): void
    accept(deps: readonly string[], cb: (mods: unknown[]) => void): void
    dispose(cb: (data: Record<string, unknown>) => void): void
    decline(): void
    invalidate(): void
    on(event: string, cb: (...args: unknown[]) => void): void
  }
}

declare const __BUILD_TIME__: string
declare const __MODE__: string
