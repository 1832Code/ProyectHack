import GoogleProvider from "next-auth/providers/google";
import { NextAuthOptions } from "next-auth";
import { supabaseAdmin } from "@/lib/supabase-server";

export const authOptions: NextAuthOptions = {
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID ?? "",
      clientSecret: process.env.GOOGLE_CLIENT_SECRET ?? "",
    }),
  ],
  callbacks: {
    async signIn({ user, account }) {
      // Upsert user into Supabase (server-side). We use email as unique key.
      try {
        if (user?.email) {
          await supabaseAdmin.from("users").upsert(
            {
              email: user.email,
              name: user.name ?? undefined,
              image: user.image ?? undefined,
              provider: account?.provider ?? "google",
              provider_account_id: account?.providerAccountId ?? undefined,
            },
            { onConflict: "email" }
          );
        }
      } catch (e) {
        // don't block sign in for transient DB errors - log server-side
        console.error("Error upserting user into Supabase:", e);
      }

      return true;
    },
    async session({ session, token }) {
      // attach token data to session for client usage
      if (token) {
        // @ts-ignore
        session.user.id = token.sub;
      }
      return session;
    },
  },
  session: {
    strategy: "jwt",
  },
};

export default authOptions;

// Helpful developer-time warnings if required env vars are missing
if (process.env.NODE_ENV !== "production") {
  const missing: string[] = []
  if (!process.env.GOOGLE_CLIENT_ID) missing.push("GOOGLE_CLIENT_ID")
  if (!process.env.GOOGLE_CLIENT_SECRET) missing.push("GOOGLE_CLIENT_SECRET")
  if (!process.env.NEXTAUTH_SECRET) missing.push("NEXTAUTH_SECRET")

  if (missing.length > 0) {
    // warn devs with a hint to copy .env.local.example
    // We don't throw here because local dev can still run parts of the app without auth
    // but it's helpful to surface the missing variables early.
    // eslint-disable-next-line no-console
    console.warn(
      "Missing environment variables for NextAuth:",
      missing.join(", "),
      ". Copy frontend/.env.local.example to .env.local and set values to test authentication."
    )
  }
}
