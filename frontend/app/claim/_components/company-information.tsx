import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { ConfirmCompanyButton } from "./confirm-company-button";
import Link from "next/link";
import BackButton from "@/components/back-button";
import { Button } from "@/components/ui/button";
import { Building2, Target, Users, Globe, CheckCircle } from "lucide-react";
import { lookupCompany } from "@/lib/api";
import { CompanyLookupResponse } from "@/types/company-lookup";

interface CompanyConfirmationProps {
  companyName: string;
  country: string;
}

export async function CompanyConfirmation({
  companyName,
  country,
}: CompanyConfirmationProps) {
  let company: CompanyLookupResponse | null = null;
  try {
    company = await lookupCompany({
      company: companyName,
      countryCode: country,
    });
  } catch (error) {
    console.error(error);
    throw new Error("Error loading company information", { cause: error });
  }

  return (
    <div className="flex items-center justify-center p-2 bg-gradient-to-br from-slate-50 via-blue-50/20 to-purple-50/20 h-screen">
      <Card className="relative w-full max-w-xl border-0 bg-white/80 backdrop-blur-sm shadow-2xl rounded-2xl overflow-hidden">
        <CardContent className="p-4">
          {/* Header Section - Más compacto */}
          {/* Top-left compact back button (icon-only) */}
          <div className="absolute top-4 left-4 z-20">
            <BackButton ariaLabel="Volver a búsqueda" />
          </div>

          <div className="flex flex-col items-center text-center mb-4">
            {/* Avatar - Reducir tamaño */}
            <div className="relative mb-3">
              <div className="absolute inset-0 bg-gradient-to-br from-blue-500 to-purple-500 rounded-xl blur-md opacity-20 transform scale-110"></div>
              <Avatar className="h-20 w-20 border-3 border-white shadow-lg relative z-10">
                <AvatarImage
                  src={company?.agent.logo_url || "/placeholder.svg"}
                  alt={company?.agent.company_name || "Company Logo"}
                  className="object-cover"
                />
                <AvatarFallback className="bg-gradient-to-br from-blue-500 to-purple-500 text-white text-xl">
                  <Building2 className="h-7 w-7" />
                </AvatarFallback>
              </Avatar>
            </div>

            {/* Company Name with Verification Badge - Fuente más pequeña y menos margen */}
            <div className="flex items-center gap-2 mb-2 ">
              <h1 className="text-2xl font-bold bg-gradient-to-br from-blue-600 to-purple-600 bg-clip-text text-transparent">
                {company?.agent.company_name}
              </h1>
            </div>

            {/* Location - Fuente más pequeña y menos margen */}
          </div>

          {/* Main Content Grid - Más compacto */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            {/* Sector Card - Más compacto */}
            <Card className="border border-slate-200 bg-white/60 backdrop-blur-sm rounded-xl shadow-sm">
              <CardContent className="p-3">
                <div className="flex items-center gap-3">
                  <div className="p-1.5 bg-blue-100 rounded-lg">
                    <Target className="h-4 w-4 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-xs text-slate-500 uppercase tracking-wide font-medium">
                      Sector
                    </p>
                    <p className="text-sm font-semibold text-slate-800">
                      {company?.agent.additional_data.sector}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Categories Section - Más compacto */}
          <div className="mb-5">
            <div className="flex items-center gap-2 mb-3">
              <div className="p-1 bg-gradient-to-br from-blue-500 to-purple-500 rounded-md">
                <Building2 className="h-3 w-3 text-white" />
              </div>
              <h3 className="text-sm font-semibold text-slate-800">
                Business Categories
              </h3>
            </div>

            <div className="flex flex-wrap gap-2 justify-center">
              {
                // Sort keywords alphabetically and show up to 6
                (() => {
                  const keywords = company?.agent.keywords ?? [];
                  const sorted = [...keywords].sort((a, b) =>
                    a.localeCompare(b)
                  );
                  const visible = sorted.slice(0, 4);
                  const moreCount = Math.max(0, sorted.length - 6);

                  return (
                    <>
                      {visible.map((category) => (
                        <Badge
                          key={category}
                          variant="secondary"
                          className="px-3 py-1.5 rounded-lg text-xs font-medium border-0 bg-cyan-500 text-white shadow-sm transition-transform duration-200 hover:scale-105"
                        >
                          {category}
                        </Badge>
                      ))}

                      {moreCount > 0 && (
                        <Badge
                          variant="outline"
                          className="px-3 py-1.5 rounded-lg text-xs font-medium border-slate-300 text-slate-600 bg-white/80"
                        >
                          +{moreCount} más
                        </Badge>
                      )}
                    </>
                  );
                })()
              }
            </div>
          </div>

          <div className="text-center">
            <div className="w-full max-w-xs mx-auto">
              <ConfirmCompanyButton
                categories={company?.agent.keywords}
                companyName={companyName}
                country={country}
              />
            </div>
            <div className="flex flex-col items-center gap-3 mt-2">
              <button className="w-full max-w-xs font-medium text-sm text-slate-600 hover:text-slate-800 hover:underline transition-colors">
                <Link href="/buscar">Volver a buscar otra empresa</Link>
              </button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
