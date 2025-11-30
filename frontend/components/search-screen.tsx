"use client";

import type React from "react";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useSession, signOut } from "next-auth/react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { SearchCommand } from "@/components/search-command";
import { cn } from "@/lib/utils";
import { useServices } from "@/components/providers/services-providers";

const countries = [
  { id: "peru", label: "Perú" },
  { id: "chile", label: "Chile" },
  { id: "colombia", label: "Colombia" },
  { id: "mexico", label: "México" },
];

// sectors removed per request (UI simplified)

export function SearchScreen() {
  const { data: session } = useSession();
  const [showProfile, setShowProfile] = useState(false);
  const router = useRouter();
  const { resetAll } = useServices();

  // Reset all data when navigating to search page
  useEffect(() => {
    resetAll();
  }, [resetAll]);

  const [companyName, setCompanyName] = useState("");
  const [country, setCountry] = useState("peru");
  // sector removed — no longer required
  const [keywords, setKeywords] = useState("");
  const [errors, setErrors] = useState<{
    companyName?: string;
    country?: string;
  }>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validate = () => {
    const newErrors: {
      companyName?: string;
      country?: string;
    } = {};

    if (!companyName || companyName.length < 2) {
      newErrors.companyName = "El nombre debe tener al menos 2 caracteres";
    } else if (companyName.length > 100) {
      newErrors.companyName = "El nombre no puede exceder 100 caracteres";
    }

    if (!country) {
      newErrors.country = "Selecciona un país";
    }

    // sectors are removed; no sector validation

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const isValid = companyName.length >= 2 && country !== "";

  const handleSubmit = (e: React.MouseEvent) => {
    e.preventDefault();

    if (!validate()) return;

    setIsSubmitting(true);

    // Build query params for claim page
    const params = new URLSearchParams({
      companyName: companyName.trim(),
      country: country,
    });

    // Add keywords if provided
    if (keywords.trim()) {
      params.set("keywords", keywords.trim());
    }

    router.push(`/claim?${params.toString()}`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 px-6 py-6 flex flex-col relative overflow-hidden">
      {/* Elementos decorativos de fondo */}
      <div className="absolute top-20 left-10 w-32 h-32 bg-cyan-500/10 rounded-full blur-3xl animate-pulse" />
      <div className="absolute bottom-40 right-10 w-40 h-40 bg-purple-500/10 rounded-full blur-3xl animate-pulse" />

      {/* Grid pattern overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:50px_50px] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_50%,black,transparent)]" />

      <header className="mb-6 relative z-10 flex flex items-start justify-between">
        <div className="flex flex-col">
          <Button
            variant="ghost"
            size="sm"
            asChild
            className=" w-32  mb-4 -ml-2 text-gray-300 hover:text-white hover:bg-white/10 rounded-full px-3 backdrop-blur-sm border border-white/10"
          >
            <Link href="/">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="mr-1"
              >
                <path d="m12 19-7-7 7-7" />
                <path d="M19 12H5" />
              </svg>
              Volver
            </Link>
          </Button>

          {/*vista panel de busqueda*/}
          <div className="space-y-2 ">
            <div className="inline-block px-3 py-1 bg-cyan-500/10 border border-cyan-500/20 rounded-full backdrop-blur-sm">
              <span className="text-cyan-400 text-xs font-semibold tracking-wider">
                PASO 1 DE 1
              </span>
            </div>
            <h1 className="text-4xl font-bold text-white tracking-tight leading-tight">
              Cuéntanos sobre
              <br />
              <span className="bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                tu negocio
              </span>
            </h1>
          </div>
        </div>

        {/*vista de usuario perfil*/}
        <div className="ml-4 relative">
          {session?.user ? (
            <div className="flex items-center gap-2">
              <button
                aria-label="Perfil"
                onClick={() => setShowProfile((s) => !s)}
                className="rounded-full overflow-hidden border border-white/10 shadow-sm bg-white/5 p-0 w-10 h-10 flex items-center justify-center"
              >
                {session.user.image ? (
                  // small image
                  // eslint-disable-next-line @next/next/no-img-element
                  <img
                    src={session.user.image}
                    alt={session.user?.name ?? session.user?.email ?? "avatar"}
                    className="w-10 h-10 object-cover rounded-full"
                  />
                ) : (
                  <div className="w-10 h-10 flex items-center justify-center bg-slate-700 rounded-full text-sm font-semibold text-white">
                    {(
                      (session.user.name ?? session.user.email ?? "").match(
                        /(^|\s)([A-Za-z])/g
                      ) || []
                    )
                      .slice(0, 2)
                      .map((m) => m.trim().slice(0, 1).toUpperCase())
                      .join("")}
                  </div>
                )}
              </button>

              {showProfile && (
                <div className="absolute right-0 top-12 w-64 rounded-xl border border-white/10 bg-white/5 backdrop-blur-sm p-4 shadow-xl z-20">
                  <div className="flex items-center gap-3 mb-4">
                    {session.user.image ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img
                        src={session.user.image}
                        className="w-12 h-12 rounded-full object-cover"
                        alt="avatar"
                      />
                    ) : (
                      <div className="w-12 h-12 rounded-full bg-slate-700 flex items-center justify-center text-white font-semibold text-sm">
                        {(
                          (session.user.name ?? session.user.email ?? "").match(
                            /(^|\s)([A-Za-z])/g
                          ) || []
                        )
                          .slice(0, 2)
                          .map((m) => m.trim().slice(0, 1).toUpperCase())
                          .join("")}
                      </div>
                    )}

                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-semibold text-white truncate">
                        {session.user.name ?? session.user.email}
                      </div>
                      {session.user.email && (
                        <div className="text-xs text-slate-300 truncate">
                          {session.user.email}
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="border-t border-white/10 pt-3">
                    <button
                      onClick={() => {
                        setShowProfile(false);
                        signOut({ callbackUrl: "/" });
                      }}
                      className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-slate-300 hover:text-white hover:bg-white/10 transition-all duration-200"
                    >
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="16"
                        height="16"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      >
                        <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                        <polyline points="16,17 21,12 16,7" />
                        <line x1="21" x2="9" y1="12" y2="12" />
                      </svg>
                      Cerrar sesión
                    </button>
                  </div>
                </div>
              )}
            </div>
          ) : null}
        </div>
      </header>

      <div className="flex flex-col gap-6 flex-1 relative z-10">
        {/* Company Name Field - Con Autocompletado */}
        <div className="flex flex-col gap-2">
          <Label className="text-sm text-gray-300 font-medium">
            Nombre de la compañía
          </Label>
          <SearchCommand
            value={companyName}
            onChange={setCompanyName}
            onCompanySelect={(company) => {
              setCompanyName(company.name);
            }}
          />
          {errors.companyName && (
            <p className="text-xs text-red-400">{errors.companyName}</p>
          )}
          <p className="text-xs text-slate-400 mt-1">
            Escribe para buscar o selecciona de la lista de empresas conocidas.
          </p>
        </div>

        {/* Country Field - Mejorado */}
        <div className="flex flex-col gap-3">
          <div className="flex items-center justify-between">
            <Label className="text-sm text-gray-300 font-medium">
              País de operación
            </Label>
            <div className="text-xs text-slate-400">
              País seleccionado:{" "}
              <span className="font-semibold text-white ml-1">
                {countries.find((x) => x.id === country)?.label ?? "—"}
              </span>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            {countries.map((c) => (
              <button
                key={c.id}
                type="button"
                onClick={() => setCountry(c.id)}
                className={cn(
                  "h-16 rounded-2xl transition-all flex flex-col items-center justify-center gap-1 relative overflow-hidden group",
                  "border backdrop-blur-sm",
                  country === c.id
                    ? "bg-gradient-to-r from-cyan-500/30 to-purple-600/30 border-cyan-400 shadow-[0_8px_30px_rgba(99,102,241,0.12)] scale-105 ring-2 ring-cyan-400/30"
                    : "bg-white/6 border-white/10 hover:bg-white/12 hover:border-white/20"
                )}
              >
                {/* no top-right icon indicator */}
                {/* icons removed per request */}
                <span
                  className={cn(
                    "text-sm font-medium transition-all",
                    country === c.id ? "text-cyan-400" : "text-gray-300"
                  )}
                >
                  {c.label}
                </span>
              </button>
            ))}
          </div>
          {errors.country && (
            <p className="text-xs text-red-400">{errors.country}</p>
          )}
        </div>

        {/* sectors removed per request */}

        {/* Keywords Field - Mejorado */}
        <div className="flex flex-col gap-2">
          <Label className="text-sm text-gray-300 font-medium">
            Palabras clave (opcional)
          </Label>
          <div className="relative">
            <Textarea
              value={keywords}
              onChange={(e) => setKeywords(e.target.value)}
              placeholder="Ej: sostenibilidad, innovación, expansión..."
              rows={3}
              className="px-4 py-3 bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl text-base text-white placeholder:text-gray-500 resize-none focus-visible:ring-2 focus-visible:ring-cyan-500/50 focus-visible:border-cyan-500/50 transition-all hover:border-white/20"
            />
            {/* keyword quick-check removed */}
          </div>
          <p className="text-xs text-gray-500">
            Ayúdanos a personalizar el análisis con términos específicos
          </p>
        </div>

        {/* Spacer */}
        <div className="flex-1" />

        {/* Submit Button - Mejorado */}
        <div className="space-y-3 pb-2">
          <Button
            onClick={handleSubmit}
            disabled={!isValid || isSubmitting}
            className={cn(
              "w-full h-16 rounded-2xl text-lg font-bold transition-all relative overflow-hidden group",
              isValid
                ? "bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-600 hover:to-purple-700 text-white shadow-xl shadow-cyan-500/30 hover:shadow-cyan-500/50 hover:scale-[1.02]"
                : "bg-white/5 text-gray-500 border border-white/10",
              "disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100",
              isSubmitting && "animate-pulse"
            )}
          >
            {isSubmitting ? (
              <>
                <div className="absolute inset-0 bg-gradient-to-r from-cyan-500 to-purple-600 animate-pulse" />
                <span className="relative z-10 flex items-center gap-2">
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Generando...
                </span>
              </>
            ) : (
              <>
                <div className="absolute inset-0 bg-gradient-to-r from-cyan-500 to-purple-600 group-hover:from-cyan-600 group-hover:to-purple-700" />
                <span className="relative z-10 flex items-center gap-2">
                  Continuar
                </span>
              </>
            )}
          </Button>

          {isValid && (
            <p className="text-center text-xs text-gray-400">
              El análisis tomará aproximadamente 30 segundos
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
