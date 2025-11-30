import { createClient } from "@supabase/supabase-js";

if (!process.env.SUPABASE_URL || !process.env.SUPABASE_SERVICE_ROLE_KEY) {
  // Intentionally fail early for devs if env vars are missing
  // This file must only be used in server-side code
  // Provide a helpful hint pointing to the example env file
  throw new Error(
    "Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY environment variables.\n" +
      "Copy frontend/.env.local.example to frontend/.env.local and fill in your Supabase values for local testing.\n" +
      "IMPORTANT: SUPABASE_SERVICE_ROLE_KEY must only be set in server-side environment variables (do not expose it in the browser)."
  );
}

export const supabaseAdmin = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY,
  {
    // ensure server-only session behavior
    auth: {
      persistSession: false,
    },
  }
);

export default supabaseAdmin;
