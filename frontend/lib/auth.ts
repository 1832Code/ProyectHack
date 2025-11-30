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
    async signIn({ user }) {
      return true;
    },
    async session({ session, token }) {
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
