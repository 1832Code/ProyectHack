"use client";

import type React from "react";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { cn } from "@/lib/utils";
import { ArrowLeft, Building, Globe, BarChart3, Search } from "lucide-react";

const countries = [
  { id: "peru", label: "Perú" },
  { id: "chile", label: "Chile" },
  { id: "colombia", label: "Colombia" },
  { id: "mexico", label: "México" },
];

const sectors = [
  { id: "tech", label: "Tecnología" },
  { id: "retail", label: "Retail" },
  { id: "finance", label: "Finanzas" },
  { id: "food", label: "Alimentos" },
  { id: "health", label: "Salud" },
  { id: "education", label: "Educación" },
  { id: "manufacturing", label: "Manufactura" },
  { id: "services", label: "Servicios" },
];

export function SearchScreen() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    companyName: "",
    country: "",
    sector: "",
    keywords: ""
  });
  const [errors, setErrors] = useState<{
    companyName?: string;
    country?: string;
    sector?: string;
  }>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field as keyof typeof errors]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  const validate = () => {
    const newErrors: {
      companyName?: string;
      country?: string;
      sector?: string;
    } = {};

    if (!formData.companyName || formData.companyName.length < 2) {
      newErrors.companyName = "El nombre debe tener al menos 2 caracteres";
    } else if (formData.companyName.length > 100) {
      newErrors.companyName = "El nombre no puede exceder 100 caracteres";
    }

    if (!formData.country) {
      newErrors.country = "Selecciona un país";
    }

    if (!formData.sector) {
      newErrors.sector = "Selecciona un sector";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const isValid = formData.companyName.length >= 2 && formData.country !== "" && formData.sector !== "";

  const handleSubmit = (e: React.MouseEvent) => {
    e.preventDefault();
    if (!validate()) return;

    setIsSubmitting(true);
    setTimeout(() => {
      router.push("/dashboard");
    }, 500);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 px-6 py-8 flex flex-col relative overflow-hidden">
      {/* Background Elements */}
      <div className="absolute top-20 left-10 w-32 h-32 bg-cyan-500/10 rounded-full blur-3xl animate-pulse" />
      <div className="absolute bottom-40 right-10 w-40 h-40 bg-purple-500/10 rounded-full blur-3xl animate-pulse" />
      
      {/* Grid Pattern */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:50px_50px] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_50%,black,transparent)]" />

      <header className="mb-8 relative z-10">
        <Button
          variant="ghost"
          size="sm"
          asChild
          className="mb-6 -ml-2 text-gray-300 hover:text-white hover:bg-white/10 rounded-full px-3 backdrop-blur-sm border border-white/10 transition-all duration-200"
        >
          <Link href="/">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Volver
          </Link>
        </Button>

        <div className="space-y-3">
          <div className="inline-flex items-center px-3 py-1 bg-cyan-500/10 border border-cyan-500/20 rounded-full backdrop-blur-sm">
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
          <p className="text-gray-400 text-lg">
            Analizaremos tu compañía en tiempo real
          </p>
        </div>
      </header>

      <div className="flex flex-col gap-8 flex-1 relative z-10 max-w-2xl">
        {/* Company Name Field */}
        <div className="space-y-3">
          <Label className="text-base text-gray-200 font-medium flex items-center gap-3">
            <Building className="w-5 h-5 text-cyan-400" />
            Nombre de la compañía
          </Label>
          <Input
            value={formData.companyName}
            onChange={(e) => handleInputChange("companyName", e.target.value)}
            placeholder="Ej: Mi Empresa S.A.C."
            className="h-14 px-4 bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl text-base text-white placeholder:text-gray-500 focus-visible:ring-2 focus-visible:ring-cyan-500/50 focus-visible:border-cyan-500/50 transition-all duration-200"
          />
          {errors.companyName && (
            <p className="text-sm text-red-400 flex items-center gap-2">
              {errors.companyName}
            </p>
          )}
        </div>

        {/* Country Field */}
        <div className="space-y-4">
          <Label className="text-base text-gray-200 font-medium flex items-center gap-3">
            <Globe className="w-5 h-5 text-cyan-400" />
            País de operación
          </Label>
          <ToggleGroup
            type="single"
            value={formData.country}
            onValueChange={(value) => value && handleInputChange("country", value)}
            className="grid grid-cols-2 gap-3"
          >
            {countries.map((country) => (
              <ToggleGroupItem
                key={country.id}
                value={country.id}
                className={cn(
                  "h-14 rounded-lg text-base font-medium transition-all duration-200",
                  "border backdrop-blur-sm",
                  "data-[state=off]:bg-white/5 data-[state=off]:text-gray-300 data-[state=off]:border-white/10",
                  "data-[state=off]:hover:bg-white/10 data-[state=off]:hover:border-white/20 data-[state=off]:hover:scale-[1.02]",
                  "data-[state=on]:bg-gradient-to-r data-[state=on]:from-cyan-500 data-[state=on]:to-purple-600",
                  "data-[state=on]:text-white data-[state=on]:border-transparent data-[state=on]:shadow-lg data-[state=on]:shadow-cyan-500/25"
                )}
              >
                {country.label}
              </ToggleGroupItem>
            ))}
          </ToggleGroup>
          {errors.country && (
            <p className="text-sm text-red-400 flex items-center gap-2">
              {errors.country}
            </p>
          )}
        </div>

        {/* Sector Field */}
        <div className="space-y-4">
          <Label className="text-base text-gray-200 font-medium flex items-center gap-3">
            <BarChart3 className="w-5 h-5 text-cyan-400" />
            Sector industrial
          </Label>
          <div className="grid grid-cols-2 gap-3">
            {sectors.map((sector) => (
              <button
                key={sector.id}
                type="button"
                onClick={() => handleInputChange("sector", sector.id)}
                className={cn(
                  "h-14 rounded-lg text-base font-medium transition-all duration-200 flex items-center justify-center",
                  "border backdrop-blur-sm",
                  formData.sector === sector.id
                    ? "bg-gradient-to-r from-cyan-500 to-purple-600 text-white border-transparent shadow-lg shadow-cyan-500/25 scale-[1.02]"
                    : "bg-white/5 text-gray-300 border-white/10 hover:bg-white/10 hover:border-white/20 hover:scale-[1.02]"
                )}
              >
                {sector.label}
              </button>
            ))}
          </div>
          {errors.sector && (
            <p className="text-sm text-red-400 flex items-center gap-2">
              {errors.sector}
            </p>
          )}
        </div>

        {/* Keywords Field */}
        <div className="space-y-3">
          <Label className="text-base text-gray-200 font-medium flex items-center gap-3">
            <Search className="w-5 h-5 text-cyan-400" />
            Palabras clave
            <span className="text-sm text-gray-500 font-normal">(opcional)</span>
          </Label>
          <Textarea
            value={formData.keywords}
            onChange={(e) => handleInputChange("keywords", e.target.value)}
            placeholder="Ej: sostenibilidad, innovación, expansión..."
            rows={3}
            className="px-4 py-3 bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl text-base text-white placeholder:text-gray-500 resize-none focus-visible:ring-2 focus-visible:ring-cyan-500/50 focus-visible:border-cyan-500/50 transition-all duration-200"
          />
          <p className="text-sm text-gray-500">
            Ayúdanos a personalizar el análisis con términos específicos
          </p>
        </div>

        {/* Spacer */}
        <div className="flex-1" />

        {/* Submit Button */}
        <div className="space-y-4 pb-4">
          <Button
            onClick={handleSubmit}
            disabled={!isValid || isSubmitting}
            size="lg"
            className={cn(
              "w-full h-16 rounded-xl text-lg font-semibold transition-all duration-200 relative overflow-hidden",
              isValid
                ? "bg-gradient-to-r from-cyan-500 to-purple-600 hover:from-cyan-600 hover:to-purple-700 text-white shadow-xl shadow-cyan-500/25 hover:shadow-cyan-500/40 hover:scale-[1.02]"
                : "bg-white/5 text-gray-400 border border-white/10",
              "disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
            )}
          >
            {isSubmitting ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-3" />
                Generando análisis...
              </>
            ) : (
              <>
                <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse mr-3" />
                Analizar mi negocio
              </>
            )}
          </Button>

          {isValid && (
            <p className="text-center text-sm text-gray-400">
              El análisis tomará aproximadamente 30 segundos
            </p>
          )}
        </div>
      </div>
    </div>
  );
}