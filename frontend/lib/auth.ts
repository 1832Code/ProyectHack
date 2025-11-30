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
  pages: {
    signIn: '/signin',
    error: '/signin',
  },
  callbacks: {
    async signIn({ user, account }) {
      // Upsert user into Supabase (server-side). We use email as unique key.
      try {
        if (user?.email && supabaseAdmin) {
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
  secret: process.env.NEXTAUTH_SECRET,
  debug: process.env.NODE_ENV === "development",
};

export default authOptions;

// Helpful developer-time warnings if required env vars are missing
const missing: string[] = []
if (!process.env.GOOGLE_CLIENT_ID) missing.push("GOOGLE_CLIENT_ID")
if (!process.env.GOOGLE_CLIENT_SECRET) missing.push("GOOGLE_CLIENT_SECRET")
if (!process.env.NEXTAUTH_SECRET) missing.push("NEXTAUTH_SECRET")
if (!process.env.NEXTAUTH_URL) missing.push("NEXTAUTH_URL")

if (missing.length > 0) {
  console.error(
    "Missing environment variables for NextAuth:",
    missing.join(", ")
  )
}
