import { createClient } from '@supabase/supabase-js';
// These variables pull from the Environment Variables you added to Vercel
const supabaseUrl = process.env.REACT_APP_SUPABASE_URL;
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY;

// This creates the connection bridge between your React app and JC Energy database
export const supabase = createClient(supabaseUrl, supabaseAnonKey);