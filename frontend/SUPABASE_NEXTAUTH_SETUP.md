# NextAuth + Supabase integration (Google sign-in)

This document shows how to finish configuring Google authentication with NextAuth and save users and user actions into Supabase.

Overview of what was implemented
- Server-side Supabase helper: `frontend/lib/supabase-server.ts`
- NextAuth sign-in callback updated: `frontend/lib/auth.ts` to upsert users into Supabase `users` table.
- API endpoint to record user events/actions: `app/api/user-actions/route.ts` (inserts into `user_actions`).
- UI: `confirm-company-button.tsx` now sends a `company_confirmation` action to the server before navigation.

Important environment variables you must set in `.env.local` (frontend root)
- You can copy the example file:

```bash
cp .env.local.example .env.local
```

- Edit `.env.local` and set the values:

- NEXTAUTH_URL=https://proyecthacks.onrender.com
- NEXTAUTH_SECRET=some-long-random-string
- GOOGLE_CLIENT_ID=your-google-client-id
- GOOGLE_CLIENT_SECRET=your-google-client-secret
- SUPABASE_URL=https://your-project.supabase.co
- SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

IMPORTANT: keep `SUPABASE_SERVICE_ROLE_KEY` secret and never expose it in the browser.

Install dependencies (run in `frontend`):

```powershell
pnpm install
# or npm install
```

If you prefer to add the Supabase client explicitly run:

```powershell
pnpm add @supabase/supabase-js
# or npm i @supabase/supabase-js
```

Database schema (run in Supabase SQL editor)
-- Create users table
CREATE TABLE IF NOT EXISTS public.users (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  email text UNIQUE NOT NULL,
  name text,
  image text,
  provider text,
  provider_account_id text,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Create user_actions table
CREATE TABLE IF NOT EXISTS public.user_actions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id text,
  type text NOT NULL,
  payload jsonb DEFAULT '{}',
  created_at timestamptz DEFAULT now()
);

How the flow works
1. User clicks Sign-in (Google) on the frontend (existing NextAuth flow).
2. On successful sign-in, NextAuth `signIn` callback (server-side) upserts the user into the `users` table in Supabase.
3. When the user performs an action (example: confirm company), the app calls the server API `/api/user-actions` which validates the session and inserts a record into `user_actions`.

How to test
1. Add required env vars into `.env.local`.
2. In `frontend`, run:
```powershell
pnpm install
pnpm dev
```
3. Visit the app and sign-in with a Google account.
4. Confirm a company (trigger ConfirmCompanyButton) and verify the action was written in the Supabase `user_actions` table.

Security notes
- Make sure `SUPABASE_SERVICE_ROLE_KEY` is only available to server runtime (you set it in Vercel/Netlify/your host environment variables, not in client side).

If you'd like, I can:
- add an admin-protected API route to query a user's actions
- add audit metadata (ip, ua)
- record extra application events (searches, claim requests) by wiring actions in other parts of the UI
