"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { signIn, useSession } from "next-auth/react";
import Image from "next/image";
import Link from "next/link";

export default function SignInPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  const { data: session, status } = useSession();

  useEffect(() => {
    // If already signed in redirect to /buscar
    if (status === "authenticated") router.replace("/buscar");
  }, [status, router]);

  function signInWithGoogle() {
    setLoading(true);
    // NextAuth will open the OAuth flow and redirect back to our app
    signIn("google", { callbackUrl: "/buscar" });
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 px-4 py-8">
      <div className="w-full max-w-md rounded-3xl bg-white/5 border border-white/10 p-8 backdrop-blur-md shadow-xl">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-extrabold text-white">
              Iniciar sesión
            </h2>
            <p className="text-sm text-slate-300">
              Inicia sesión o regístrate con Google para continuar
            </p>
          </div>
          <div>
            <Link href="/" className="text-sm text-slate-400 hover:text-white">
              Volver
            </Link>
          </div>
        </div>

        <div className="flex flex-col gap-4">
          <div className="text-sm text-slate-300">
            Para continuar con la plataforma necesitas iniciar sesión o crear
            una cuenta con Google.
          </div>

          <button
            onClick={signInWithGoogle}
            disabled={loading}
            className="flex items-center gap-3 w-full justify-center rounded-xl px-4 py-3 bg-white/10 hover:bg-white/20 border border-white/10 text-white transition-all duration-200 shadow-sm"
          >
            <svg
              width="20"
              height="20"
              viewBox="0 0 48 48"
              className="inline-block"
              aria-hidden
            >
              <path
                fill="#EA4335"
                d="M24 9.5c3.8 0 6.8 1.6 8.9 2.9l6.5-6.3C35.8 3.1 30.3 1 24 1 14.9 1 7.2 5.8 3 12.3l7.6 5.9C12 14 17.6 9.5 24 9.5z"
              />
              <path
                fill="#34A853"
                d="M46.5 24c0-1.4-.1-2.7-.4-4H24v7.6h12.6c-.6 3-2.6 5.5-5.3 7.2l8 6.2C43.8 39.1 46.5 32.1 46.5 24z"
              />
              <path
                fill="#4A90E2"
                d="M10.6 29.9C9.3 27.8 8.7 25.6 8.7 23c0-2.6.7-4.9 1.9-6.9L3 10.3C1.1 13.6 0 17.6 0 23c0 5.4 1.4 9.3 3.8 12.9l6.8-6z"
              />
              <path
                fill="#FBBC05"
                d="M24 46c6.3 0 11.8-2.5 15.8-6.7l-7.6-5.9C29.9 34.9 27 36 24 36c-7 0-12.6-4.5-14.4-10.6L3 30.7C6.9 38.7 14.6 46 24 46z"
              />
            </svg>

            <span className="font-semibold">Continuar con Google</span>
            {loading && (
              <span className="ml-2 animate-pulse text-xs text-slate-300">
                Iniciando...
              </span>
            )}
          </button>

          <div className="text-xs text-slate-400 text-center mt-2">
            Si no tienes cuenta, se creará automáticamente con tu cuenta Google.
          </div>
        </div>
      </div>
    </div>
  );
}
