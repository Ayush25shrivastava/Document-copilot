/**
 * Single source of truth for frontend environment variables.
 * Fails fast at startup if required variables are missing or empty.
 */

const getEnvVar = (key: string): string => {
  const value = import.meta.env[key]
  if (!value || typeof value !== 'string' || value.trim() === '') {
    throw new Error(`Missing required environment variable: ${key}`)
  }
  return value.trim()
}

export const env = {
  VITE_API_BASE_URL: getEnvVar('VITE_API_BASE_URL'),
  VITE_SUPABASE_URL: getEnvVar('VITE_SUPABASE_URL'),
  VITE_SUPABASE_ANON_KEY: getEnvVar('VITE_SUPABASE_ANON_KEY'),
} as const
