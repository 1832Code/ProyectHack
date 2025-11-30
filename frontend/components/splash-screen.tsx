"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";
import Image from "next/image";

export function SplashScreen() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex flex-col items-center justify-center px-6 py-8 relative overflow-hidden">
      {/* Background decorative elements */}
      <div className="absolute top-20 left-10 w-32 h-32 bg-blue-500/10 rounded-full blur-3xl animate-pulse" />
      <div className="absolute bottom-40 right-10 w-40 h-40 bg-purple-500/10 rounded-full blur-3xl animate-pulse delay-700" />
      <div className="absolute top-1/2 left-1/4 w-24 h-24 bg-cyan-500/10 rounded-full blur-2xl animate-pulse delay-1000" />

      {/* Grid pattern overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:50px_50px] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_50%,black,transparent)]" />

      <main className="flex flex-col items-center justify-center relative z-10 gap-8 px-4 text-center">
        {/* Company Name */}
        <div className="space-y-2">
          <h1 className="text-4xl font-black bg-gradient-to-r from-cyan-400 via-purple-400 to-blue-400 bg-clip-text text-transparent leading-tight tracking-tight">
            Entropy
          </h1>
        </div>

        {/* Mission Statement */}
        <div className="max-w-md mx-auto">
          <p className="text-lg text-gray-200 font-medium leading-relaxed">
            Democratizar el acceso a las oportunidades que surgen del Internet
            para las PYMES
          </p>
        </div>

        {/* Logo + reflection */}
        <div className="my-4 flex flex-col items-center gap-2">
          <div className="w-32 h-32 relative bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-4 flex items-center justify-center">
            <Image
              src="/logo.png"
              alt="Entropy Logo"
              width={128}
              height={128}
              className="object-contain"
            />
          </div>

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
          <Link
            href="/buscar"
            className="flex items-center justify-center gap-2"
          >
            <span>Comenzar Análisis</span>
            <ArrowRight className="w-4 h-4 transition-transform duration-300 group-hover:translate-x-1" />
          </Link>
        </Button>

        {/* Analysis Time Notice */}
        <div className="text-center">
          <p className="text-sm text-gray-400 font-medium">
            El análisis tomará aproximadamente 30 segundos
          </p>
        </div>
      </footer>
    </div>
  );
}
