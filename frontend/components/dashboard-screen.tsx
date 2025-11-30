"use client";

import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import {
  TrendingUp,
  Users,
  Youtube,
  MessageSquare,
  FileText,
} from "lucide-react";
import { DashboardHeader } from "@/components/dashboard-header";
import { Mentions } from "./dashboard/mentions";
import { DashboardStats } from "./dashboard/stats";
import { OpportunityFloatingButton } from "@/components/opportunity-float-button";

const PlatformIcons = {
  youtube: Youtube,
  tiktok: MessageSquare,
  instagram: MessageSquare,
  x: MessageSquare,
  facebook: Users,
  article: FileText,
};

// Paleta de 3 colores: azul, púrpura, esmeralda
const platformColors = {
  youtube: "text-white bg-blue-500 border-blue-400 shadow-sm",
  tiktok: "text-white bg-purple-500 border-purple-400 shadow-sm",
  instagram: "text-white bg-purple-500 border-purple-400 shadow-sm",
  x: "text-white bg-blue-500 border-blue-400 shadow-sm",
  facebook: "text-white bg-blue-500 border-blue-400 shadow-sm",
  article: "text-white bg-emerald-500 border-emerald-400 shadow-sm",
};

export function DashboardScreen({ companyName }: { companyName?: string }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/20 to-purple-50/20">
      <div className="relative z-10">
        {/* Header */}
        <DashboardHeader
          companyName={companyName ?? ""}
          companyLogo="/rappi-logo.png"
          companyInitials="RA"
          subtitle="Perú · 20 de sept."
        />

        <div className="px-5 pt-5">
          <DashboardStats />

          {/* Trending Topics */}
          {/* <div className="mb-8">
            <div className="flex items-center gap-2 mb-3">
              <div className="p-2 rounded-lg bg-purple-500 shadow-sm">
                <TrendingUp className="w-4 h-4 text-white" />
              </div>
              <p className="text-sm text-slate-600 font-medium">
                Temas en tendencia
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              {[
                "calidad del pollo",
                "tiempos de entrega",
                "servicio al cliente",
                "rendimiento de la app",
              ].map((tag) => (
                <Badge
                  key={tag}
                  variant="outline"
                  className="px-4 py-2 text-sm font-medium rounded-full border-slate-200 bg-white text-slate-700 hover:bg-slate-50 cursor-pointer transition-colors shadow-sm"
                >
                  {tag}
                </Badge>
              ))}
            </div>
          </div> */}

          {/* Live Conversations */}
          {/* <div className="mb-8">
            <div className="flex items-center gap-2 mb-4">
              <div className="p-2 rounded-lg bg-emerald-500 shadow-sm">
                <Users className="w-4 h-4 text-white" />
              </div>
              <p className="text-base text-slate-800 font-semibold">
                Conversaciones en vivo
              </p>
            </div>
            <div className="flex flex-col gap-3">
              <Card className="border border-slate-200 bg-white/80 rounded-xl shadow-lg">
                <CardContent className="p-4 flex items-center justify-between">
                  <span className="text-sm font-medium text-slate-800">
                    Quejas sobre Pios Chicken
                  </span>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-slate-500">+200</span>
                    <div
                      className={cn(
                        "p-2 rounded-lg border shadow-sm",
                        platformColors.instagram
                      )}
                    >
                      <PlatformIcons.instagram className="w-4 h-4" />
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card className="border border-slate-200 bg-white/80 rounded-xl shadow-lg">
                <CardContent className="p-4 flex items-center justify-between">
                  <span className="text-sm font-medium text-slate-800">
                    Conversan sobre pollo en mal estado en Lima
                  </span>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-slate-500">+20</span>
                    <div
                      className={cn(
                        "p-2 rounded-lg border shadow-sm",
                        platformColors.tiktok
                      )}
                    >
                      <PlatformIcons.tiktok className="w-4 h-4" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
            <button className="w-full text-center text-sm text-blue-600 mt-3 hover:text-blue-700 transition-colors font-medium">
              Ver todas las conversaciones
            </button>
          </div> */}

          {/* Social Mentions */}
          <Mentions />
        </div>
      </div>

      {/* Floating Action Button */}
      <OpportunityFloatingButton />
    </div>
  );
}
