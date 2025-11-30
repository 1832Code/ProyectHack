"use client";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";
import Image from "next/image";
import { useSession, signIn } from "next-auth/react";
import { useState } from "react";
import { useRouter } from "next/navigation";

export function SplashScreen() {
  const { data: session } = useSession();
  const [showAuthPanel, setShowAuthPanel] = useState(false);
  const router = useRouter();
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex flex-col items-center justify-center px-6 py-8 relative overflow-hidden">
      {/* Background decorative elements */}
      <div className="absolute top-20 left-10 w-32 h-32 bg-blue-500/10 rounded-full blur-3xl animate-pulse" />
      <div className="absolute bottom-40 right-10 w-40 h-40 bg-purple-500/10 rounded-full blur-3xl animate-pulse delay-700" />
      <div className="absolute top-1/2 left-1/4 w-24 h-24 bg-cyan-500/10 rounded-full blur-2xl animate-pulse delay-1000" />

      {/* Grid pattern overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:50px_50px] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_50%,black,transparent)]" />

      <main className="flex flex-col items-center justify-center relative z-10 gap-4 px-2 text-center">
        {/* Company Name */}
        <div className="flex flex-col items-center -mt-2.5  ">
          <Image
            src="/logo.png"
            alt="Entropy Logo"
            width={228}
            height={228}
            className="object-contain"
          />
        </div>
        <div className="-mt-10">
          <h1 className="text-6xl  bg-gradient-to-r from-cyan-400  via-purple-400 to-blue-400 bg-clip-text text-transparent leading-tight tracking-tight">
            entropy
          </h1>
        </div>

        {/* Logo + reflection */}
        <div className="my-4 flex flex-col items-center gap-2">
          {/* subtle reflected logo */}
          <div
            aria-hidden
            className="w-32 h-16 relative overflow-hidden pointer-events-none"
          >
            <div
              className="w-32 h-32 flex items-center justify-center"
              style={{
                transform: "scaleY(-1)",
                opacity: 0.42,
                filter: "blur(.4px) brightness(.75)",
                WebkitMaskImage:
                  "linear-gradient(to bottom, rgba(0,0,0,0.7), rgba(0,0,0,0))",
                maskImage:
                  "linear-gradient(to bottom, rgba(0,0,0,0.7), rgba(0,0,0,0))",
              }}
            >
              <Image
                src="/logo.png"
                alt="Entropy Logo (reflected)"
                width={128}
                height={128}
                className="object-contain"
              />
            </div>
          </div>
        </div>
      </main>

      <footer className="flex flex-col gap-4 relative z-10 mt-8 w-full max-w-sm">
        {/* Start Analysis Button */}
        <Button
          asChild
          size="lg"
          className="w-full h-14 rounded-xl text-base font-semibold bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-600 hover:to-purple-700 text-white shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40 transition-all duration-300 hover:scale-[1.02] active:scale-[0.98] border-0 group"
        >
          <div
            role="button"
            tabIndex={0}
            onClick={async () => {
              // if the user is not authenticated, show a small panel so user can confirm
              // they want to authenticate with Google (then the provider will show the
              // account chooser). If already authenticated, go to /buscar immediately.
              if (!session || !session.user) {
                setShowAuthPanel(true);
                return;
              }
              router.push("/buscar");
            }}
            onKeyDown={async (e) => {
              if (e.key === "Enter" || e.key === " ") {
                if (!session || !session.user) {
                  setShowAuthPanel(true);
                  return;
                }
                router.push("/buscar");
              }
            }}
            className="flex items-center justify-center gap-2 cursor-pointer"
          >
            <span>Comenzar</span>
            <ArrowRight className="w-4 h-4 transition-transform duration-300 group-hover:translate-x-1" />
          </div>
        </Button>

        {/* Auth confirmation panel (full-screen on mobile) */}
        {showAuthPanel && (
          <div className="fixed inset-0 z-50 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
            {/* Background decorative elements */}
            <div className="absolute top-20 left-10 w-32 h-32 bg-blue-500/10 rounded-full blur-3xl animate-pulse" />
            <div className="absolute bottom-40 right-10 w-40 h-40 bg-purple-500/10 rounded-full blur-3xl animate-pulse delay-700" />
            <div className="absolute top-1/2 left-1/4 w-24 h-24 bg-cyan-500/10 rounded-full blur-2xl animate-pulse delay-1000" />

            {/* Grid pattern overlay */}
            <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:50px_50px] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_50%,black,transparent)]" />

            <div className="relative z-10 flex flex-col items-center justify-center min-h-screen px-6 py-8">
              {/* Close button */}
              <button
                aria-label="Cerrar"
                onClick={() => setShowAuthPanel(false)}
                className="absolute top-6 right-6 w-10 h-10 rounded-full bg-white/10 border border-white/20 text-white hover:bg-white/20 transition-all duration-200 flex items-center justify-center backdrop-blur-sm"
              >
                ✕
              </button>

              {/* Logo */}
              <div className="mb-8">
                <Image
                  src="/logo.png"
                  alt="Entropy Logo"
                  width={96}
                  height={96}
                  className="object-contain"
                />
              </div>

              {/* Title */}
              <div className="text-center mb-8">
                <h1 className="text-3xl font-black bg-gradient-to-r from-cyan-400 via-purple-400 to-blue-400 bg-clip-text text-transparent mb-4">
                  Iniciar Sesión
                </h1>
                <p className="text-lg text-gray-200 max-w-md mx-auto leading-relaxed">
                  Para continuar con el análisis necesitas autenticarte con tu
                  cuenta de Google
                </p>
              </div>

              {/* Auth button */}
              <div className="w-full max-w-sm space-y-4">
                <button
                  onClick={() => signIn("google", { callbackUrl: "/buscar" })}
                  className="w-full h-14 rounded-xl bg-white hover:bg-gray-50 text-gray-900 font-semibold transition-all duration-200 shadow-lg hover:shadow-xl flex items-center justify-center gap-3 border-0 group hover:scale-[1.02] active:scale-[0.98]"
                >
                  <svg width="24" height="24" viewBox="0 0 48 48" aria-hidden>
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
                  <span>Continuar con Google</span>
                </button>

                <button
                  onClick={() => setShowAuthPanel(false)}
                  className="w-full h-12 rounded-xl border border-white/20 text-white hover:bg-white/10 transition-all duration-200 font-medium"
                >
                  Cancelar
                </button>
              </div>

              {/* Footer text */}
              <div className="text-center mt-8">
                <p className="text-sm text-gray-400">
                  Al continuar, aceptas nuestros términos de servicio
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Analysis Time Notice */}

        {/* <div className="text-center">
          <p className="text-sm text-gray-400 font-medium">
            El análisis tomará aproximadamente 30 segundos
          </p>
        </div> */}
      </footer>
    </div>
  );
}
