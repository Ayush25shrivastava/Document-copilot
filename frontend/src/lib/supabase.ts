import { createClient } from '@supabase/supabase-js'
import { env } from './env'

/**
 * Singleton Supabase client for browser authentication and public DB operations.
 */
export const supabase = createClient(env.VITE_SUPABASE_URL, env.VITE_SUPABASE_ANON_KEY)
