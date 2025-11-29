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
  Zap,
  Crown,
  Target,
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
      "POV: When Rappi says 10 minutes but you've been waiting 45 #rappi #delivery #peru",
    engagement: "245k views",
    time: "2h",
    sentiment: "negative" as const,
  },
  {
    id: 2,
    platform: "instagram" as const,
    username: "@foodie_lima",
    avatar: "/placeholder.svg?height=40&width=40",
    content:
      "Tried the new RappiPrime and it's worth every penny. Unlimited free shipping and great deals",
    engagement: "1.2k likes",
    time: "3h",
    sentiment: "positive" as const,
  },
  {
    id: 3,
    platform: "youtube" as const,
    username: "Tech Review Peru",
    avatar: "/placeholder.svg?height=40&width=40",
    content:
      "Full comparison: Rappi vs PedidosYa vs DiDi Food - Which is better in 2024? | Complete Review",
    engagement: "89k views",
    time: "5h",
    sentiment: "neutral" as const,
  },
  {
    id: 4,
    platform: "x" as const,
    username: "@carlosm_pe",
    avatar: "/placeholder.svg?height=40&width=40",
    content:
      "The Rappi app is getting slower every day. Anyone else having issues? Can't even order properly.",
    engagement: "342 retweets",
    time: "6h",
    sentiment: "negative" as const,
  },
  {
    id: 5,
    platform: "article" as const,
    username: "El Comercio",
    avatar: "/placeholder.svg?height=40&width=40",
    content:
      "Rappi announces expansion to 5 new cities in Peru and promises 2,000 new jobs for delivery drivers",
    engagement: "Economy",
    time: "8h",
    sentiment: "positive" as const,
  },
  {
    id: 6,
    platform: "facebook" as const,
    username: "Lima Deals",
    avatar: "/placeholder.svg?height=40&width=40",
    content:
      "RAPPI DISCOUNT CODE: Use 'SAVE30' for 30% off your next order. Valid until tomorrow!",
    engagement: "2.3k shares",
    time: "10h",
    sentiment: "positive" as const,
  },
  {
    id: 7,
    platform: "tiktok" as const,
    username: "@delivery_official",
    avatar: "/placeholder.svg?height=40&width=40",
    content:
      "A normal day as a Rappi delivery driver in Lima. Life of a rappitendero #rappi #work",
    engagement: "567k views",
    time: "12h",
    sentiment: "neutral" as const,
  },
  {
    id: 8,
    platform: "instagram" as const,
    username: "@peruvian_restaurant",
    avatar: "/placeholder.svg?height=40&width=40",
    content:
      "We're now on Rappi! Order your favorite ceviche with free delivery this week. Link in bio",
    engagement: "856 likes",
    time: "14h",
    sentiment: "positive" as const,
  },
  {
    id: 9,
    platform: "x" as const,
    username: "@startup_latam",
    avatar: "/placeholder.svg?height=40&width=40",
    content:
      "Rappi reports 40% growth in Peru during Q3. The delivery market continues to expand in the region.",
    engagement: "189 likes",
    time: "16h",
    sentiment: "positive" as const,
  },
  {
    id: 10,
    platform: "youtube" as const,
    username: "3 Pepitos Podcast",
    avatar: "/placeholder.svg?height=40&width=40",
    content:
      "Ep. 234: We discuss the delivery app war in Peru. Rappi, PedidosYa and the new players",
    engagement: "12k views",
    time: "1d",
    sentiment: "neutral" as const,
  },
];

const platformColors = {
  youtube:
    "text-white bg-gradient-to-br from-red-500 to-red-600 border-red-300 shadow-sm",
  tiktok:
    "text-white bg-gradient-to-br from-purple-500 to-pink-500 border-purple-300 shadow-sm",
  instagram:
    "text-white bg-gradient-to-br from-pink-500 to-orange-500 border-pink-300 shadow-sm",
  x: "text-white bg-gradient-to-br from-blue-500 to-cyan-500 border-blue-300 shadow-sm",
  facebook:
    "text-white bg-gradient-to-br from-indigo-500 to-blue-600 border-indigo-300 shadow-sm",
  article:
    "text-white bg-gradient-to-br from-emerald-500 to-green-500 border-emerald-300 shadow-sm",
};

const sentimentColors = {
  positive:
    "bg-gradient-to-r from-emerald-50 to-green-50 text-emerald-700 border-emerald-200/80 shadow-sm",
  negative:
    "bg-gradient-to-r from-red-50 to-rose-50 text-red-700 border-red-200/80 shadow-sm",
  neutral:
    "bg-gradient-to-r from-slate-50 to-gray-50 text-slate-700 border-slate-200/80 shadow-sm",
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
      {/* Enhanced background with subtle patterns */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-blue-100/20 via-transparent to-purple-100/20"></div>
      <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48Y2lyY2xlIGN4PSIzMCIgY3k9IjMwIiByPSIxIiBmaWxsPSIjOTliNmZmIiBmaWxsLW9wYWNpdHk9IjAuMSIvPjwvc3ZnPg==')] opacity-30"></div>

      <div className="relative z-10">
        {/* Header with enhanced sticky behavior */}
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
                ? "py-2 px-4 bg-white/90 backdrop-blur-xl rounded-2xl border border-white/20 shadow-lg w-fit"
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
                className="bg-white/80 hover:bg-white text-slate-700 hover:text-slate-900 rounded-full px-4 border border-slate-200/60 shadow-sm backdrop-blur-sm"
              >
                <Link href="/buscar">
                  <ArrowLeft className="w-4 h-4 mr-1" />
                  New search
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
                    "bg-white/80 hover:bg-white text-slate-700 hover:text-slate-900 transition-all duration-300 rounded-full border border-slate-200/60 shadow-sm backdrop-blur-sm",
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
                    "ring-2 ring-blue-100/50 transition-all duration-300 shadow-lg",
                    isSticky ? "h-8 w-8 rounded-xl" : "h-12 w-12 rounded-2xl"
                  )}
                >
                  <AvatarImage src="/rappi-logo.png" alt="Rappi" />
                  <AvatarFallback
                    className={cn(
                      "bg-gradient-to-br from-blue-500 to-purple-600 text-white font-semibold transition-all duration-300",
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
                  <div className="h-4 w-px bg-gradient-to-b from-slate-200 to-slate-100" />
                  <div className="flex items-center gap-3">
                    <div className="flex items-center gap-1.5">
                      <span className="text-sm font-bold text-slate-800">
                        32k
                      </span>
                      <span className="text-xs bg-gradient-to-r from-emerald-500 to-green-500 text-white px-1.5 py-0.5 rounded-full font-medium flex items-center gap-0.5">
                        <TrendingUp className="w-3 h-3" />
                        2%
                      </span>
                    </div>
                    <div className="h-3 w-px bg-gradient-to-b from-slate-200 to-slate-100" />
                    <div className="flex items-center gap-1.5">
                      <span className="text-sm font-bold text-slate-800">
                        89%
                      </span>
                      <span className="text-xs bg-gradient-to-r from-emerald-500 to-green-500 text-white px-1.5 py-0.5 rounded-full font-medium flex items-center gap-0.5">
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
                  <h1 className="text-2xl font-bold bg-gradient-to-br from-slate-800 to-slate-600 bg-clip-text text-transparent">
                    Rappi
                  </h1>
                  <p className="text-sm text-slate-500 flex items-center gap-1">
                    <Target className="w-3 h-3" />
                    Peru · Sep 20th
                  </p>
                </div>
              </div>
            </header>
          </div>
        </div>

        <div className="px-5 pt-5">
          {/* Enhanced Stats Cards */}
          <div className="grid grid-cols-2 gap-4 mb-8">
            <Card className="border border-white/20 bg-white/70 backdrop-blur-sm rounded-2xl shadow-lg overflow-hidden relative">
              <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 to-cyan-500"></div>
              <CardContent className="p-5">
                <div className="flex items-center gap-2 mb-2">
                  <div className="p-2 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500 shadow-sm">
                    <MessageCircle className="w-4 h-4 text-white" />
                  </div>
                  <p className="text-sm text-slate-600 font-medium">Mentions</p>
                </div>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-bold bg-gradient-to-br from-slate-800 to-slate-600 bg-clip-text text-transparent">
                    32k
                  </span>
                  <span className="text-sm bg-gradient-to-r from-emerald-500 to-green-500 text-white px-2 py-1 rounded-full font-medium flex items-center gap-0.5">
                    <TrendingUp className="w-3 h-3" />
                    2%
                  </span>
                </div>
              </CardContent>
            </Card>
            <Card className="border border-white/20 bg-white/70 backdrop-blur-sm rounded-2xl shadow-lg overflow-hidden relative">
              <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-purple-500 to-pink-500"></div>
              <CardContent className="p-5">
                <div className="flex items-center gap-2 mb-2">
                  <div className="p-2 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 shadow-sm">
                    <Activity className="w-4 h-4 text-white" />
                  </div>
                  <p className="text-sm text-slate-600 font-medium">Approval</p>
                </div>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-bold bg-gradient-to-br from-slate-800 to-slate-600 bg-clip-text text-transparent">
                    89%
                  </span>
                  <span className="text-sm bg-gradient-to-r from-emerald-500 to-green-500 text-white px-2 py-1 rounded-full font-medium flex items-center gap-0.5">
                    <TrendingUp className="w-3 h-3" />
                    12%
                  </span>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Enhanced Sentiment Chart */}
          <div className="mb-8">
            <div className="flex items-center gap-2 mb-3">
              <div className="p-2 rounded-lg bg-gradient-to-br from-orange-500 to-amber-500 shadow-sm">
                <BarChart3 className="w-4 h-4 text-white" />
              </div>
              <p className="text-sm text-slate-600 font-medium">
                Sentiment Trend
              </p>
            </div>
            <Card className="border border-white/20 bg-white/70 backdrop-blur-sm rounded-2xl shadow-lg overflow-hidden">
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
                      <stop offset="25%" stopColor="#8b5cf6" />
                      <stop offset="50%" stopColor="#ec4899" />
                      <stop offset="75%" stopColor="#f59e0b" />
                      <stop offset="100%" stopColor="#10b981" />
                    </linearGradient>
                    <linearGradient
                      id="areaGradient"
                      x1="0%"
                      y1="0%"
                      x2="0%"
                      y2="100%"
                    >
                      <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.2" />
                      <stop offset="100%" stopColor="#3b82f6" stopOpacity="0" />
                    </linearGradient>
                  </defs>
                  <path
                    d="M0,40 Q30,38 60,32 T120,28 T180,20 T240,16 T300,8 L300,48 L0,48 Z"
                    fill="url(#areaGradient)"
                  />
                  <path
                    d="M0,40 Q30,38 60,32 T120,28 T180,20 T240,16 T300,8"
                    fill="none"
                    stroke="url(#sentimentGradient)"
                    strokeWidth="3"
                    strokeLinecap="round"
                  />
                </svg>
                <div className="flex justify-between mt-2 text-xs text-slate-500">
                  <span>Mon</span>
                  <span>Tue</span>
                  <span>Wed</span>
                  <span>Thu</span>
                  <span>Fri</span>
                  <span>Sat</span>
                  <span>Sun</span>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Enhanced Trending Topics */}
          <div className="mb-8">
            <div className="flex items-center gap-2 mb-3">
              <div className="p-2 rounded-lg bg-gradient-to-br from-rose-500 to-pink-500 shadow-sm">
                <TrendingUp className="w-4 h-4 text-white" />
              </div>
              <p className="text-sm text-slate-600 font-medium">
                Trending Topics
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              {[
                "chicken quality",
                "delivery times",
                "customer service",
                "app performance",
              ].map((tag, index) => (
                <Badge
                  key={tag}
                  variant="outline"
                  className="px-4 py-2 text-sm font-medium rounded-full border-white/20 bg-white/50 backdrop-blur-sm text-slate-700 hover:bg-white/80 cursor-pointer transition-all duration-300 shadow-sm hover:shadow-md hover:scale-105"
                  style={{
                    background: `linear-gradient(135deg, ${
                      index % 4 === 0
                        ? "#f0f9ff"
                        : index % 4 === 1
                        ? "#faf5ff"
                        : index % 4 === 2
                        ? "#fef2f2"
                        : "#f0fdf4"
                    }, white)`,
                  }}
                >
                  {tag}
                </Badge>
              ))}
            </div>
          </div>

          {/* Enhanced Live Conversations */}
          <div className="mb-8">
            <div className="flex items-center gap-2 mb-4">
              <div className="p-2 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-500 shadow-sm">
                <Zap className="w-4 h-4 text-white" />
              </div>
              <p className="text-base font-semibold bg-gradient-to-br from-slate-800 to-slate-600 bg-clip-text text-transparent">
                Live Conversations
              </p>
            </div>
            <div className="flex flex-col gap-3">
              <Card className="border border-white/20 bg-white/70 backdrop-blur-sm rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-[1.02]">
                <CardContent className="p-4 flex items-center justify-between">
                  <span className="text-sm font-medium text-slate-800">
                    Complaints about Pios Chicken
                  </span>
                  <div className="flex items-center gap-2">
                    <span className="text-sm bg-gradient-to-r from-rose-500 to-pink-500 text-white px-2 py-1 rounded-full font-medium">
                      +200
                    </span>
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
              <Card className="border border-white/20 bg-white/70 backdrop-blur-sm rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-[1.02]">
                <CardContent className="p-4 flex items-center justify-between">
                  <span className="text-sm font-medium text-slate-800">
                    Talk about stale chicken in Lima
                  </span>
                  <div className="flex items-center gap-2">
                    <span className="text-sm bg-gradient-to-r from-rose-500 to-pink-500 text-white px-2 py-1 rounded-full font-medium">
                      +20
                    </span>
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
            <button className="w-full text-center text-sm bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent font-semibold mt-3 hover:from-blue-700 hover:to-purple-700 transition-all duration-300 py-2">
              See all conversations →
            </button>
          </div>

          {/* Enhanced Social Mentions */}
          <section className="pb-8">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <div className="p-2 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-500 shadow-sm">
                  <Crown className="w-4 h-4 text-white" />
                </div>
                <h2 className="text-base font-semibold bg-gradient-to-br from-slate-800 to-slate-600 bg-clip-text text-transparent">
                  Social Mentions
                </h2>
              </div>
              <span className="text-sm bg-gradient-to-r from-slate-600 to-slate-500 bg-clip-text text-transparent font-medium">
                {allMentions.length} total
              </span>
            </div>

            <div className="flex flex-col gap-4">
              {displayedMentions.map((mention) => {
                const PlatformIcon = PlatformIcons[mention.platform];
                const SentimentIcon = sentimentIcons[mention.sentiment];

                return (
                  <Card
                    key={mention.id}
                    className="border border-white/20 bg-white/70 backdrop-blur-sm rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-[1.01] overflow-hidden group"
                  >
                    <CardContent className="p-5">
                      <div className="flex items-start gap-4">
                        <div
                          className={cn(
                            "p-3 rounded-xl border shadow-sm group-hover:scale-110 transition-transform duration-300",
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
                            <span className="text-xs bg-gradient-to-r from-slate-500 to-slate-400 bg-clip-text text-transparent shrink-0">
                              {mention.time}
                            </span>
                          </div>
                          <p className="text-sm text-slate-600 leading-relaxed line-clamp-2 mb-3">
                            {mention.content}
                          </p>
                          <div className="flex items-center justify-between">
                            <span className="text-xs bg-gradient-to-r from-slate-500 to-slate-400 bg-clip-text text-transparent">
                              {mention.engagement}
                            </span>
                            <Badge
                              variant="secondary"
                              className={cn(
                                "text-xs font-medium px-3 py-1.5 rounded-full border flex items-center gap-1.5 shadow-sm",
                                sentimentColors[mention.sentiment]
                              )}
                            >
                              <SentimentIcon className="w-3 h-3" />
                              {mention.sentiment === "positive"
                                ? "Positive"
                                : mention.sentiment === "negative"
                                ? "Negative"
                                : "Neutral"}
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
                <div className="flex items-center gap-2 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600" />
                  <span className="text-sm font-medium">
                    Loading more mentions...
                  </span>
                </div>
              )}
              {!hasMore && displayedMentions.length > 0 && (
                <p className="text-sm bg-gradient-to-r from-slate-500 to-slate-400 bg-clip-text text-transparent font-medium">
                  No more mentions to load
                </p>
              )}
            </div>

            {/* Enhanced Generate Report Button */}
            <div className="mt-2">
              <Button className="w-full h-14 rounded-2xl bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 hover:from-blue-700 hover:via-purple-700 hover:to-pink-700 text-white text-base font-semibold shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:scale-[1.02] group">
                <div className="flex items-center gap-2">
                  <div className="p-1 rounded-lg bg-white/20 group-hover:scale-110 transition-transform duration-300">
                    <Sparkles className="w-5 h-5" />
                  </div>
                  Generate Report
                </div>
              </Button>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
