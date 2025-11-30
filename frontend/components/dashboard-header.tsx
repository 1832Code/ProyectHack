"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { cn } from "@/lib/utils";
import { ArrowLeft, TrendingUp } from "lucide-react";
import { useEffect, useState } from "react";
import { useServices } from "@/components/providers/services-providers";

interface DashboardHeaderProps {
  companyName: string;
  companyLogo: string;
  companyInitials: string;
  subtitle: string;
  backHref?: string;
  backLabel?: string;
}

export function DashboardHeader({
  companyName,
  companyLogo,
  companyInitials,
  subtitle,
  backHref = "/buscar",
  backLabel = "Nueva búsqueda",
}: DashboardHeaderProps) {
  const [isSticky, setIsSticky] = useState(false);
  const { analytics, isLoadingAnalytics, fetchAnalytics } = useServices();

  useEffect(() => {
    fetchAnalytics({
      keyword: companyName ?? "",
      idCompany: 1,
      limit: 1000,
    });
  }, [companyName]);

  useEffect(() => {
    const handleScroll = () => {
      setIsSticky(window.scrollY > 120);
    };
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <div
      className={cn(
        "sticky top-0 z-50 transition-all duration-300 flex justify-center",
        isSticky ? "pt-4 px-4" : "px-5 pt-6 pb-0"
      )}
    >
      <div
        className={cn(
          "transition-all duration-300",
          isSticky
            ? "py-2 px-4 bg-white/90 backdrop-blur-xl rounded-2xl border border-slate-200 shadow-lg w-fit"
            : "w-full bg-transparent"
        )}
      >
        <div
          className={cn(
            "transition-all duration-300 overflow-hidden",
            isSticky ? "h-0 opacity-0 mb-0" : "h-auto opacity-100 mb-5"
          )}
        >
          <Button
            variant="secondary"
            size="sm"
            asChild
            className="bg-white/80 hover:bg-white text-slate-700 hover:text-slate-900 rounded-full px-4 border border-slate-200 shadow-sm backdrop-blur-sm"
          >
            <Link href={backHref}>
              <ArrowLeft className="w-4 h-4 mr-1" />
              {backLabel}
            </Link>
          </Button>
        </div>

        <header
          className={cn(
            "flex items-center transition-all duration-300",
            isSticky ? "justify-center gap-2" : "gap-3 mb-5"
          )}
        >
          <div className="flex items-center gap-2">
            <Button
              variant="secondary"
              size="icon"
              asChild
              className={cn(
                "bg-white/80 hover:bg-white text-slate-700 hover:text-slate-900 transition-all duration-300 rounded-full border border-slate-200 shadow-sm backdrop-blur-sm",
                isSticky
                  ? "w-8 h-8 opacity-100"
                  : "w-0 h-0 opacity-0 overflow-hidden"
              )}
            >
              <Link href={backHref}>
                <ArrowLeft className="w-4 h-4" />
              </Link>
            </Button>
            <Avatar
              className={cn(
                "ring-2 ring-blue-100 transition-all duration-300 shadow-lg",
                isSticky ? "h-8 w-8 rounded-xl" : "h-12 w-12 rounded-2xl"
              )}
            >
              <AvatarImage src={companyLogo} alt={companyName} />
              <AvatarFallback
                className={cn(
                  "bg-gradient-to-br from-blue-500 to-purple-500 text-white font-semibold transition-all duration-300",
                  isSticky ? "rounded-xl text-xs" : "rounded-2xl text-base"
                )}
              >
                {companyInitials}
              </AvatarFallback>
            </Avatar>
            <div
              className={cn(
                "flex items-center gap-3 transition-all duration-300",
                isSticky ? "opacity-100 ml-2" : "opacity-0 w-0 overflow-hidden"
              )}
            >
              <div className="h-4 w-px bg-slate-200" />
              {isLoadingAnalytics ? (
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-1.5">
                    <div className="h-4 w-10 bg-slate-200 rounded animate-pulse" />
                    <div className="h-5 w-12 bg-slate-200 rounded-full animate-pulse" />
                  </div>
                  <div className="h-3 w-px bg-slate-200" />
                  <div className="flex items-center gap-1.5">
                    <div className="h-4 w-10 bg-slate-200 rounded animate-pulse" />
                    <div className="h-5 w-12 bg-slate-200 rounded-full animate-pulse" />
                  </div>
                </div>
              ) : (
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-1.5">
                    <span className="text-sm font-bold text-slate-800">
                      {analytics?.count_mentions ?? 0}
                    </span>
                    <span className="text-xs bg-emerald-500 text-white px-1.5 py-0.5 rounded-full font-medium flex items-center gap-0.5">
                      <TrendingUp className="w-3 h-3" />
                      menciones
                    </span>
                  </div>
                  <div className="h-3 w-px bg-slate-200" />
                  <div className="flex items-center gap-1.5">
                    <span className="text-sm font-bold text-slate-800">
                      {analytics?.approval_score ?? 0}%
                    </span>
                    <span className="text-xs bg-emerald-500 text-white px-1.5 py-0.5 rounded-full font-medium flex items-center gap-0.5">
                      <TrendingUp className="w-3 h-3" />
                      aprobación
                    </span>
                  </div>
                </div>
              )}
            </div>
            <div
              className={cn(
                "transition-all duration-300",
                isSticky ? "hidden" : "block"
              )}
            >
              <h1 className="text-2xl font-bold text-slate-800">
                {companyName}
              </h1>
              <p className="text-sm text-slate-500">{subtitle}</p>
            </div>
          </div>
        </header>
      </div>
    </div>
  );
}
