import { createClient } from "@supabase/supabase-js";

let supabaseAdmin: any = null;

if (process.env.SUPABASE_URL && process.env.SUPABASE_SERVICE_ROLE_KEY) {
  supabaseAdmin = createClient(
    process.env.SUPABASE_URL,
    process.env.SUPABASE_SERVICE_ROLE_KEY,
    {
      // ensure server-only session behavior
      auth: {
        persistSession: false,
      },
    }
  );
} else {
  console.warn("Supabase not configured - user data will not be stored");
}

export { supabaseAdmin };

export default supabaseAdmin;
