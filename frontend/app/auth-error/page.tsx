"use client";

import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { Suspense } from "react";

function ErrorContent() {
  const searchParams = useSearchParams();
  const error = searchParams.get("error");

  return (
    <div className="text-center">
      <h1 className="text-2xl font-bold text-white mb-4">
        Error de Autenticación
      </h1>
      <p className="text-slate-300 mb-6">
        {error === "Configuration" 
          ? "Error de configuración del servidor"
          : error === "AccessDenied"
          ? "Acceso denegado"
          : "Ocurrió un error durante la autenticación"}
      </p>
      <Link
        href="/"
        className="inline-block px-6 py-3 bg-gradient-to-r from-cyan-500 to-purple-600 text-white rounded-xl font-semibold hover:from-cyan-600 hover:to-purple-700 transition-all"
      >
        Volver al Inicio
      </Link>
    </div>
  );
}

export default function AuthError() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 px-4">
      <div className="max-w-md w-full bg-white/5 border border-white/10 rounded-2xl p-8 backdrop-blur-sm">
        <Suspense fallback={
          <div className="text-center text-white">Cargando...</div>
        }>
          <ErrorContent />
        </Suspense>
      </div>
    </div>
  );
}