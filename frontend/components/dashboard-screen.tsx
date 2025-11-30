"use client";

import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { useEffect, useState, useCallback, useRef } from "react";
import {
  ArrowLeft,
  TrendingUp,
  Users,
  MessageCircle,
  Youtube,
  MessageSquare,
  FileText,
  ThumbsUp,
  ThumbsDown,
  Minus,
  Activity,
  BarChart3,
  Sparkles,
} from "lucide-react";

const PlatformIcons = {
  youtube: Youtube,
  tiktok: MessageSquare,
  instagram: MessageSquare,
  x: MessageSquare,
  facebook: Users,
  article: FileText,
};

const allMentions = [
  {
    id: 1,
    platform: "tiktok" as const,
    username: "@delivery_fails",
    avatar: "/placeholder.svg?height=40&width=40",
    content:
      "Cuando Rappi dice 10 minutos pero llevas esperando 45 minutos #rappi #delivery #perú",
    engagement: "245k vistas",
    time: "2h",
    sentiment: "negative" as const,
  },
  {
    id: 2,
    platform: "instagram" as const,
    username: "@foodie_lima",
    avatar: "/placeholder.svg?height=40&width=40",
    content:
      "Probé el nuevo RappiPrime y vale cada centavo. Envío ilimitado gratis y buenas promociones",
    engagement: "1.2k me gusta",
    time: "3h",
    sentiment: "positive" as const,
  },
  {
    id: 3,
    platform: "youtube" as const,
    username: "Tech Review Peru",
    avatar: "/placeholder.svg?height=40&width=40",
    content:
      "Comparativa completa: Rappi vs PedidosYa vs DiDi Food - ¿Cuál es mejor en 2024? | Reseña completa",
    engagement: "89k vistas",
    time: "5h",
    sentiment: "neutral" as const,
  },
  {
    id: 4,
    platform: "x" as const,
    username: "@carlosm_pe",
    avatar: "/placeholder.svg?height=40&width=40",
    content:
      "La app de Rappi cada día va más lenta. ¿Alguien más con problemas? No puedo ni ordenar correctamente.",
    engagement: "342 retuits",
    time: "6h",
    sentiment: "negative" as const,
  },
  {
    id: 5,
    platform: "article" as const,
    username: "El Comercio",
    avatar: "/placeholder.svg?height=40&width=40",
    content:
      "Rappi anuncia expansión a 5 nuevas ciudades en Perú y promete 2.000 nuevos empleos para repartidores",
    engagement: "Economía",
    time: "8h",
    sentiment: "positive" as const,
  },
  {
    id: 6,
    platform: "facebook" as const,
    username: "Lima Deals",
    avatar: "/placeholder.svg?height=40&width=40",
    content:
      "CÓDIGO DE DESCUENTO RAPPI: Usa 'SAVE30' para 30% de descuento en tu próximo pedido. ¡Válido hasta mañana!",
    engagement: "2.3k compartidos",
    time: "10h",
    sentiment: "positive" as const,
  },
  {
    id: 7,
    platform: "tiktok" as const,
    username: "@delivery_official",
    avatar: "/placeholder.svg?height=40&width=40",
    content:
      "Un día normal como repartidor de Rappi en Lima. Vida de repartidor #rappi #trabajo",
    engagement: "567k vistas",
    time: "12h",
    sentiment: "neutral" as const,
  },
  {
    id: 8,
    platform: "instagram" as const,
    username: "@peruvian_restaurant",
    avatar: "/placeholder.svg?height=40&width=40",
    content:
      "¡Ahora estamos en Rappi! Pide tu ceviche favorito con delivery gratis esta semana. Enlace en la bio",
    engagement: "856 me gusta",
    time: "14h",
    sentiment: "positive" as const,
  },
  {
    id: 9,
    platform: "x" as const,
    username: "@startup_latam",
    avatar: "/placeholder.svg?height=40&width=40",
    content:
      "Rappi reporta 40% de crecimiento en Perú durante el tercer trimestre. El mercado de delivery sigue expandiéndose en la región.",
    engagement: "189 me gusta",
    time: "16h",
    sentiment: "positive" as const,
  },
  {
    id: 10,
    platform: "youtube" as const,
    username: "3 Pepitos Podcast",
    avatar: "/placeholder.svg?height=40&width=40",
    content:
      "Ep. 234: Hablamos sobre la guerra de apps de delivery en Perú. Rappi, PedidosYa y nuevos actores",
    engagement: "12k vistas",
    time: "1d",
    sentiment: "neutral" as const,
  },
];

// Paleta de 3 colores: azul, púrpura, esmeralda
const platformColors = {
  youtube: "text-white bg-blue-500 border-blue-400 shadow-sm",
  tiktok: "text-white bg-purple-500 border-purple-400 shadow-sm",
  instagram: "text-white bg-purple-500 border-purple-400 shadow-sm",
  x: "text-white bg-blue-500 border-blue-400 shadow-sm",
  facebook: "text-white bg-blue-500 border-blue-400 shadow-sm",
  article: "text-white bg-emerald-500 border-emerald-400 shadow-sm",
};

const sentimentColors = {
  positive: "bg-emerald-50 text-emerald-700 border-emerald-200 shadow-sm",
  negative: "bg-blue-50 text-blue-700 border-blue-200 shadow-sm",
  neutral: "bg-purple-50 text-purple-700 border-purple-200 shadow-sm",
};

const sentimentIcons = {
  positive: ThumbsUp,
  negative: ThumbsDown,
  neutral: Minus,
};

export function DashboardScreen() {
  const [isSticky, setIsSticky] = useState(false);
  const [displayedMentions, setDisplayedMentions] = useState(
    allMentions.slice(0, 5)
  );
  const [isLoading, setIsLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const loaderRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleScroll = () => {
      setIsSticky(window.scrollY > 120);
    };
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const loadMore = useCallback(() => {
    if (isLoading || !hasMore) return;

    setIsLoading(true);
    setTimeout(() => {
      const currentLength = displayedMentions.length;
      const nextItems = allMentions.slice(currentLength, currentLength + 5);
      if (nextItems.length === 0) {
        setHasMore(false);
      } else {
        setDisplayedMentions((prev) => [...prev, ...nextItems]);
      }
      setIsLoading(false);
    }, 800);
  }, [displayedMentions.length, isLoading, hasMore]);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasMore && !isLoading) {
          loadMore();
        }
      },
      { threshold: 0.1 }
    );

    if (loaderRef.current) {
      observer.observe(loaderRef.current);
    }

    return () => observer.disconnect();
  }, [loadMore, hasMore, isLoading]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/20 to-purple-50/20">
      <div className="relative z-10">
        {/* Header */}
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
                <Link href="/buscar">
                  <ArrowLeft className="w-4 h-4 mr-1" />
                  Nueva búsqueda
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
                  <Link href="/buscar">
                    <ArrowLeft className="w-4 h-4" />
                  </Link>
                </Button>
                <Avatar
                  className={cn(
                    "ring-2 ring-blue-100 transition-all duration-300 shadow-lg",
                    isSticky ? "h-8 w-8 rounded-xl" : "h-12 w-12 rounded-2xl"
                  )}
                >
                  <AvatarImage src="/rappi-logo.png" alt="Rappi" />
                  <AvatarFallback
                    className={cn(
                      "bg-gradient-to-br from-blue-500 to-purple-500 text-white font-semibold transition-all duration-300",
                      isSticky ? "rounded-xl text-xs" : "rounded-2xl text-base"
                    )}
                  >
                    RA
                  </AvatarFallback>
                </Avatar>
                <div
                  className={cn(
                    "flex items-center gap-3 transition-all duration-300",
                    isSticky
                      ? "opacity-100 ml-2"
                      : "opacity-0 w-0 overflow-hidden"
                  )}
                >
                  <div className="h-4 w-px bg-slate-200" />
                  <div className="flex items-center gap-3">
                    <div className="flex items-center gap-1.5">
                      <span className="text-sm font-bold text-slate-800">
                        32k
                      </span>
                      <span className="text-xs bg-emerald-500 text-white px-1.5 py-0.5 rounded-full font-medium flex items-center gap-0.5">
                        <TrendingUp className="w-3 h-3" />
                        2%
                      </span>
                    </div>
                    <div className="h-3 w-px bg-slate-200" />
                    <div className="flex items-center gap-1.5">
                      <span className="text-sm font-bold text-slate-800">
                        89%
                      </span>
                      <span className="text-xs bg-emerald-500 text-white px-1.5 py-0.5 rounded-full font-medium flex items-center gap-0.5">
                        <TrendingUp className="w-3 h-3" />
                        12%
                      </span>
                    </div>
                  </div>
                </div>
                <div
                  className={cn(
                    "transition-all duration-300",
                    isSticky ? "hidden" : "block"
                  )}
                >
                  <h1 className="text-2xl font-bold text-slate-800">Rappi</h1>
                  <p className="text-sm text-slate-500">Perú · 20 de sept.</p>
                </div>
              </div>
            </header>
          </div>
        </div>

        <div className="px-5 pt-5">
          {/* Stats Cards */}
          <div className="grid grid-cols-2 gap-4 mb-8">
            <Card className="border border-slate-200 bg-white/80 rounded-2xl shadow-lg overflow-hidden">
              <CardContent className="p-5">
                <div className="flex items-center gap-2 mb-2">
                  <div className="p-2 rounded-lg bg-blue-500 shadow-sm">
                    <MessageCircle className="w-4 h-4 text-white" />
                  </div>
                  <p className="text-sm text-slate-600 font-medium">
                    Menciones
                  </p>
                </div>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-bold text-slate-800">32k</span>
                  <span className="text-sm bg-emerald-500 text-white px-2 py-1 rounded-full font-medium flex items-center gap-0.5">
                    <TrendingUp className="w-3 h-3" />
                    2%
                  </span>
                </div>
              </CardContent>
            </Card>
            <Card className="border border-slate-200 bg-white/80 rounded-2xl shadow-lg overflow-hidden">
              <CardContent className="p-5">
                <div className="flex items-center gap-2 mb-2">
                  <div className="p-2 rounded-lg bg-purple-500 shadow-sm">
                    <Activity className="w-4 h-4 text-white" />
                  </div>
                  <p className="text-sm text-slate-600 font-medium">
                    Aprobación
                  </p>
                </div>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-bold text-slate-800">89%</span>
                  <span className="text-sm bg-emerald-500 text-white px-2 py-1 rounded-full font-medium flex items-center gap-0.5">
                    <TrendingUp className="w-3 h-3" />
                    12%
                  </span>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Sentiment Chart */}
          <div className="mb-8">
            <div className="flex items-center gap-2 mb-3">
              <div className="p-2 rounded-lg bg-blue-500 shadow-sm">
                <BarChart3 className="w-4 h-4 text-white" />
              </div>
              <p className="text-sm text-slate-600 font-medium">
                Tendencia de sentimiento
              </p>
            </div>
            <Card className="border border-slate-200 bg-white/80 rounded-2xl shadow-lg">
              <CardContent className="p-5">
                <svg viewBox="0 0 300 48" className="w-full h-12">
                  <defs>
                    <linearGradient
                      id="sentimentGradient"
                      x1="0%"
                      y1="0%"
                      x2="100%"
                      y2="0%"
                    >
                      <stop offset="0%" stopColor="#3b82f6" />
                      <stop offset="50%" stopColor="#8b5cf6" />
                      <stop offset="100%" stopColor="#10b981" />
                    </linearGradient>
                  </defs>
                  <path
                    d="M0,40 Q30,38 60,32 T120,28 T180,20 T240,16 T300,8"
                    fill="none"
                    stroke="url(#sentimentGradient)"
                    strokeWidth="3"
                    strokeLinecap="round"
                  />
                </svg>
              </CardContent>
            </Card>
          </div>

          {/* Trending Topics */}
          <div className="mb-8">
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
          </div>

          {/* Live Conversations */}
          <div className="mb-8">
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
          </div>

          {/* Social Mentions */}
          <section className="pb-8">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2"></div>
              <span className="text-sm text-slate-500">
                {allMentions.length} en total
              </span>
            </div>

            <div className="flex flex-col gap-4">
              {displayedMentions.map((mention) => {
                const PlatformIcon = PlatformIcons[mention.platform];
                const SentimentIcon = sentimentIcons[mention.sentiment];

                return (
                  <Card
                    key={mention.id}
                    className="border border-slate-200 bg-white/80 rounded-2xl shadow-lg overflow-hidden"
                  >
                    <CardContent className="p-5">
                      <div className="flex items-start gap-4">
                        <div
                          className={cn(
                            "p-3 rounded-xl border shadow-sm",
                            platformColors[mention.platform]
                          )}
                        >
                          <PlatformIcon className="w-5 h-5" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between gap-2 mb-2">
                            <span className="text-sm font-semibold text-slate-800 truncate">
                              {mention.username}
                            </span>
                            <span className="text-xs text-slate-500 shrink-0">
                              {mention.time}
                            </span>
                          </div>
                          <p className="text-sm text-slate-600 leading-relaxed line-clamp-2 mb-3">
                            {mention.content}
                          </p>
                          <div className="flex items-center justify-between">
                            <span className="text-xs text-slate-500">
                              {mention.engagement}
                            </span>
                            <Badge
                              variant="secondary"
                              className={cn(
                                "text-xs font-medium px-3 py-1.5 rounded-full border flex items-center gap-1.5",
                                sentimentColors[mention.sentiment]
                              )}
                            >
                              <SentimentIcon className="w-3 h-3" />
                              {mention.sentiment === "positive"
                                ? "Positivo"
                                : mention.sentiment === "negative"
                                ? "Negativo"
                                : "Neutro"}
                            </Badge>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>

            <div ref={loaderRef} className="flex justify-center py-6">
              {isLoading && (
                <div className="flex items-center gap-2 text-slate-500">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600" />
                  <span className="text-sm">Cargando más menciones...</span>
                </div>
              )}
              {!hasMore && displayedMentions.length > 0 && (
                <p className="text-sm text-slate-500">
                  No hay más menciones para cargar
                </p>
              )}
            </div>

            {/* Generate Report Button */}
            <div className="mt-2">
              <Button className="w-full h-14 rounded-2xl bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white text-base font-semibold shadow-lg hover:shadow-xl transition-all duration-300">
                <Sparkles className="w-5 h-5 mr-2" />
                Generar reporte
              </Button>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
