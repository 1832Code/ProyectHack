"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import AnimatedMascot from "@/components/ui/animated-mascot";
import { ArrowRight, Zap, BarChart3, Target, Rocket } from "lucide-react";

export function SplashScreen() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex flex-col px-6 py-8 relative overflow-hidden">
      {/* Background decorative elements */}
      <div className="absolute top-20 left-10 w-32 h-32 bg-blue-500/10 rounded-full blur-3xl animate-pulse" />
      <div className="absolute bottom-40 right-10 w-40 h-40 bg-purple-500/10 rounded-full blur-3xl animate-pulse delay-700" />
      <div className="absolute top-1/2 left-1/4 w-24 h-24 bg-cyan-500/10 rounded-full blur-2xl animate-pulse delay-1000" />

      {/* Grid pattern overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:50px_50px] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_50%,black,transparent)]" />

      <main className="flex-1 flex flex-col items-center justify-center relative z-10 gap-8 px-4 mt-4">
        {/* Main logo/title */}
        <div className="text-center space-y-4">
          <div className="inline-flex items-center px-4 py-2 bg-cyan-500/10 border border-cyan-500/20 rounded-full">
            <span className="text-cyan-400 text-sm font-semibold tracking-wider">
              ANÁLISIS INTELIGENTE
            </span>
          </div>

          <div className="space-y-2">
            <h1 className="text-5xl font-black bg-gradient-to-r from-cyan-400 via-purple-400 to-blue-400 bg-clip-text text-transparent leading-tight tracking-tight">
              Entropy
            </h1>
            <p className="text-lg text-gray-300 font-medium max-w-md mx-auto leading-relaxed">
              Análisis empresarial en tiempo real con inteligencia artificial
            </p>
          </div>
        </div>

        {/* Feature highlights */}
        <div className="grid grid-cols-3 gap-4 max-w-md mx-auto">
          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-4 text-center group hover:bg-white/10 transition-all duration-300">
            <div className="flex justify-center mb-3">
              <div className="p-2 bg-cyan-500/10 rounded-lg group-hover:scale-110 transition-transform duration-300">
                <BarChart3 className="w-5 h-5 text-cyan-400" />
              </div>
            </div>
            <p className="text-xs text-gray-300 font-medium">Datos en vivo</p>
          </div>
          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-4 text-center group hover:bg-white/10 transition-all duration-300">
            <div className="flex justify-center mb-3">
              <div className="p-2 bg-purple-500/10 rounded-lg group-hover:scale-110 transition-transform duration-300">
                <Target className="w-5 h-5 text-purple-400" />
              </div>
            </div>
            <p className="text-xs text-gray-300 font-medium">
              Insights precisos
            </p>
          </div>
          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-4 text-center group hover:bg-white/10 transition-all duration-300">
            <div className="flex justify-center mb-3">
              <div className="p-2 bg-blue-500/10 rounded-lg group-hover:scale-110 transition-transform duration-300">
                <Zap className="w-5 h-5 text-blue-400" />
              </div>
            </div>
            <p className="text-xs text-gray-300 font-medium">
              Resultados rápidos
            </p>
          </div>
        </div>

        {/* Value proposition */}
        <div className="bg-gradient-to-r from-cyan-500/5 to-purple-500/5 border border-cyan-500/10 rounded-xl p-6 max-w-md backdrop-blur-sm group hover:border-cyan-500/20 transition-all duration-300">
          <p className="text-center text-gray-200 text-sm leading-relaxed">
            Ingresa el nombre de tu compañía y sector para obtener un{" "}
            <span className="text-cyan-400 font-semibold">
              análisis completo
            </span>{" "}
            y{" "}
            <span className="text-purple-400 font-semibold">
              recomendaciones personalizadas
            </span>{" "}
            en segundos
          </p>
        </div>
      </main>

      <footer className="flex flex-col gap-4 relative z-10 mt-8">
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

        <div className="flex items-center justify-center gap-2 text-gray-400">
          <Rocket className="w-3 h-3" />
          <p className="text-xs font-medium">
            Potenciado por IA • Resultados instantáneos
          </p>
        </div>
      </footer>

      {/* Custom animations */}
      <style jsx>{`
        @keyframes spin-slow {
          from {
            transform: rotate(0deg);
          }
          to {
            transform: rotate(360deg);
          }
        }
        .animate-spin-slow {
          animation: spin-slow 15s linear infinite;
        }
      `}</style>
    </div>
  );
}
